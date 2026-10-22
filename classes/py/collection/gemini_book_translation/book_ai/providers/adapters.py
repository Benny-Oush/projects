import json
import re
import time
import httpx
from typing import Dict, Any, List, Optional
from book_ai.security.secrets import secret_manager

MODEL_CATALOG: Dict[str, List[Dict[str, Any]]] = {
    "gemini": [
        {
            "id": "gemini-2.5-flash", "name": "Gemini 2.5 Flash", "provider": "gemini",
            "context_tokens": 1000000, "max_output_tokens": 8192, "supports_json": True,
            "supports_temperature": True, "price_in": 0.15, "price_out": 0.60, "notes": "מהיר ומומלץ לתרגום ספרים"
        },
        {
            "id": "gemini-2.5-pro", "name": "Gemini 2.5 Pro", "provider": "gemini",
            "context_tokens": 2000000, "max_output_tokens": 8192, "supports_json": True,
            "supports_temperature": True, "price_in": 1.25, "price_out": 5.00, "notes": "איכות ספרותית גבוהה במיוחד"
        }
    ],
    "openai": [
        {
            "id": "gpt-4o-mini", "name": "GPT-4o Mini", "provider": "openai",
            "context_tokens": 128000, "max_output_tokens": 16384, "supports_json": True,
            "supports_temperature": True, "price_in": 0.15, "price_out": 0.60, "notes": "חסכוני ומהיר"
        },
        {
            "id": "gpt-4o", "name": "GPT-4o", "provider": "openai",
            "context_tokens": 128000, "max_output_tokens": 16384, "supports_json": True,
            "supports_temperature": True, "price_in": 2.50, "price_out": 10.00, "notes": "מודל דגל לעריכה מורכבת"
        }
    ],
    "anthropic": [
        {
            "id": "claude-3-5-sonnet-latest", "name": "Claude 3.5 Sonnet", "provider": "anthropic",
            "context_tokens": 200000, "max_output_tokens": 8192, "supports_json": False,
            "supports_temperature": True, "price_in": 3.00, "price_out": 15.00, "notes": "מצוין לעריכה ספרותית ועברית"
        }
    ],
    "openrouter": [
        {
            "id": "google/gemini-2.5-flash", "name": "OpenRouter: Gemini 2.5 Flash", "provider": "openrouter",
            "context_tokens": 1000000, "max_output_tokens": 8192, "supports_json": True,
            "supports_temperature": True, "price_in": 0.15, "price_out": 0.60, "notes": "גישה מאוחדת"
        }
    ],
    "ollama": [
        {
            "id": "llama3.1:8b", "name": "Llama 3.1 8B (Local)", "provider": "ollama",
            "context_tokens": 32768, "max_output_tokens": 4096, "supports_json": True,
            "supports_temperature": True, "price_in": 0.0, "price_out": 0.0, "notes": "ריצה מקומית ללא עלות"
        }
    ],
    "custom": [
        {
            "id": "custom-model", "name": "Custom OpenAI-Compatible", "provider": "custom",
            "context_tokens": 32768, "max_output_tokens": 4096, "supports_json": True,
            "supports_temperature": True, "price_in": 0.0, "price_out": 0.0, "notes": "שרת מותאם אישית"
        }
    ],
    "mock": [
        {
            "id": "mock-deterministic", "name": "Mock Provider (בדיקות בלבד)", "provider": "mock",
            "context_tokens": 128000, "max_output_tokens": 8192, "supports_json": True,
            "supports_temperature": True, "price_in": 0.0, "price_out": 0.0, "notes": "לבדיקות אוטומטיות דטרמיניסטיות"
        }
    ]
}

class ProviderError(Exception):
    def __init__(self, message: str, retryable: bool = False, status_code: int = 0, retry_after: float = 0.0):
        super().__init__(secret_manager.redact(message))
        self.retryable = retryable
        self.status_code = status_code
        self.retry_after = retry_after

def extract_json_payload(raw_text: str) -> Dict[str, Any]:
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        cleaned = cleaned[start:end + 1]
    return json.loads(cleaned)

class UnifiedAIProvider:
    @staticmethod
    async def complete(
        provider: str,
        model: str,
        messages: List[Dict[str, str]],
        settings: Dict[str, Any],
        temp_api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        t0 = time.perf_counter()
        prov = provider.lower()

        if prov == "mock" or settings.get("mock"):
            return UnifiedAIProvider._run_mock(messages, model, t0)

        api_key = secret_manager.get_key(prov, temp_api_key)
        if prov not in ("ollama",) and not api_key:
            raise ProviderError(f"חסר מפתח API עבור הספק '{prov}'. הזן מפתח בהגדרות הספק.", retryable=False)

        timeout = float(settings.get("timeout", 120))
        temperature = settings.get("temperature")
        max_tokens = int(settings.get("max_output_tokens", 8192))

        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                if prov == "gemini":
                    return await UnifiedAIProvider._call_gemini(client, model, messages, api_key, temperature, max_tokens, settings, t0)
                elif prov == "anthropic":
                    return await UnifiedAIProvider._call_anthropic(client, model, messages, api_key, temperature, max_tokens, t0)
                elif prov == "ollama":
                    return await UnifiedAIProvider._call_ollama(client, model, messages, temperature, max_tokens, settings, t0)
                else:
                    return await UnifiedAIProvider._call_openai_compat(client, prov, model, messages, api_key, temperature, max_tokens, settings, t0)
            except httpx.TimeoutException:
                raise ProviderError(f"חריגה מזמן ההמתנה ({timeout}s) מול הספק {prov}.", retryable=True)
            except httpx.RequestError as e:
                raise ProviderError(f"שגיאת רשת מול הספק {prov}: {e}", retryable=True)

    @staticmethod
    def _run_mock(messages: List[Dict[str, str]], model: str, t0: float) -> Dict[str, Any]:
        user_msg = messages[-1]["content"]
        idx = user_msg.find("INPUT DATA PAYLOAD:\n")
        payload_str = user_msg[idx + len("INPUT DATA PAYLOAD:\n"):] if idx != -1 else "{}"
        data = json.loads(payload_str)
        target_units = data.get("target_units_to_process", [])
        out_units = []
        for u in target_units:
            out_units.append({
                "id": u["id"],
                "unit_type": u["unit_type"],
                "text": f"[מתורגם] {u['text']}"
            })
        raw_json = json.dumps({"units": out_units}, ensure_ascii=False)
        in_tok = max(1, len(user_msg) // 4)
        out_tok = max(1, len(raw_json) // 4)
        return {
            "parsed": {"units": out_units},
            "raw_text": raw_json,
            "input_tokens": in_tok,
            "output_tokens": out_tok,
            "is_estimated_usage": True,
            "elapsed": time.perf_counter() - t0,
            "model": model
        }

    @staticmethod
    async def _call_openai_compat(client: httpx.AsyncClient, prov: str, model: str, messages: List[Dict[str, str]],
                                  api_key: str, temperature: Optional[float], max_tokens: int,
                                  settings: Dict[str, Any], t0: float) -> Dict[str, Any]:
        base_urls = {
            "openai": "[https://api.openai.com/v1](https://api.openai.com/v1)",
            "openrouter": "[https://openrouter.ai/api/v1](https://openrouter.ai/api/v1)",
            "custom": settings.get("base_url") or "[http://127.0.0.1:8080/v1](http://127.0.0.1:8080/v1)"
        }
        base_url = (settings.get("base_url") or base_urls.get(prov, "[https://api.openai.com/v1](https://api.openai.com/v1)")).rstrip("/")
        url = f"{base_url}/chat/completions"

        body: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
        }
        if temperature is not None:
            body["temperature"] = temperature
        if settings.get("format", "auto") in ("auto", "json"):
            body["response_format"] = {"type": "json_object"}

        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        resp = await client.post(url, json=body, headers=headers)
        UnifiedAIProvider._check_http_status(resp, prov)
        res_data = resp.json()
        content = res_data["choices"][0]["message"]["content"]
        usage = res_data.get("usage", {})
        return {
            "parsed": extract_json_payload(content),
            "raw_text": content,
            "input_tokens": usage.get("prompt_tokens", len(str(messages)) // 4),
            "output_tokens": usage.get("completion_tokens", len(content) // 4),
            "is_estimated_usage": "usage" not in res_data,
            "elapsed": time.perf_counter() - t0,
            "model": model
        }

    @staticmethod
    async def _call_gemini(client: httpx.AsyncClient, model: str, messages: List[Dict[str, str]],
                           api_key: str, temperature: Optional[float], max_tokens: int,
                           settings: Dict[str, Any], t0: float) -> Dict[str, Any]:
        base = (settings.get("base_url") or "[https://generativelanguage.googleapis.com/v1beta](https://generativelanguage.googleapis.com/v1beta)").rstrip("/")
        url = f"{base}/models/{model}:generateContent"
        sys_instruction = next((m["content"] for m in messages if m["role"] == "system"), "")
        user_content = next((m["content"] for m in messages if m["role"] == "user"), "")

        gen_config: Dict[str, Any] = {
            "maxOutputTokens": max_tokens,
            "responseMimeType": "application/json"
        }
        if temperature is not None:
            gen_config["temperature"] = temperature

        payload = {
            "systemInstruction": {"parts": [{"text": sys_instruction}]},
            "contents": [{"role": "user", "parts": [{"text": user_content}]}],
            "generationConfig": gen_config
        }
        resp = await client.post(url, json=payload, headers={"x-goog-api-key": api_key})
        UnifiedAIProvider._check_http_status(resp, "gemini")
        data = resp.json()
        candidates = data.get("candidates", [])
        if not candidates:
            raise ProviderError("המודל החזיר תשובה ריקה ללא מועמדים (Candidates).", retryable=True)
        content = candidates[0]["content"]["parts"][0]["text"]
        usage = data.get("usageMetadata", {})
        return {
            "parsed": extract_json_payload(content),
            "raw_text": content,
            "input_tokens": usage.get("promptTokenCount", len(user_content) // 4),
            "output_tokens": usage.get("candidatesTokenCount", len(content) // 4),
            "is_estimated_usage": "usageMetadata" not in data,
            "elapsed": time.perf_counter() - t0,
            "model": model
        }

    @staticmethod
    async def _call_anthropic(client: httpx.AsyncClient, model: str, messages: List[Dict[str, str]],
                              api_key: str, temperature: Optional[float], max_tokens: int, t0: float) -> Dict[str, Any]:
        url = "[https://api.anthropic.com/v1/messages](https://api.anthropic.com/v1/messages)"
        sys_instruction = next((m["content"] for m in messages if m["role"] == "system"), "")
        user_content = next((m["content"] for m in messages if m["role"] == "user"), "")
        body: Dict[str, Any] = {
            "model": model,
            "max_tokens": max_tokens,
            "system": sys_instruction,
            "messages": [{"role": "user", "content": user_content}]
        }
        if temperature is not None:
            body["temperature"] = temperature
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        resp = await client.post(url, json=body, headers=headers)
        UnifiedAIProvider._check_http_status(resp, "anthropic")
        data = resp.json()
        content = data["content"][0]["text"]
        usage = data.get("usage", {})
        return {
            "parsed": extract_json_payload(content),
            "raw_text": content,
            "input_tokens": usage.get("input_tokens", len(user_content) // 4),
            "output_tokens": usage.get("output_tokens", len(content) // 4),
            "is_estimated_usage": "usage" not in data,
            "elapsed": time.perf_counter() - t0,
            "model": model
        }

    @staticmethod
    async def _call_ollama(client: httpx.AsyncClient, model: str, messages: List[Dict[str, str]],
                           temperature: Optional[float], max_tokens: int, settings: Dict[str, Any], t0: float) -> Dict[str, Any]:
        base = (settings.get("base_url") or "[http://127.0.0.1:11434](http://127.0.0.1:11434)").rstrip("/")
        url = f"{base}/api/chat"
        body = {
            "model": model,
            "messages": messages,
            "stream": False,
            "format": "json",
            "options": {"num_predict": max_tokens}
        }
        if temperature is not None:
            body["options"]["temperature"] = temperature
        resp = await client.post(url, json=body)
        UnifiedAIProvider._check_http_status(resp, "ollama")
        data = resp.json()
        content = data["message"]["content"]
        return {
            "parsed": extract_json_payload(content),
            "raw_text": content,
            "input_tokens": data.get("prompt_eval_count", len(str(messages)) // 4),
            "output_tokens": data.get("eval_count", len(content) // 4),
            "is_estimated_usage": "eval_count" not in data,
            "elapsed": time.perf_counter() - t0,
            "model": model
        }

    @staticmethod
    def _check_http_status(resp: httpx.Response, provider: str) -> None:
        if resp.status_code < 400:
            return
        sc = resp.status_code
        retry_after = float(resp.headers.get("Retry-After", 0) or 0)
        detail = resp.text[:300]
        if sc in (401, 403):
            raise ProviderError(f"שגיאת אימות מול {provider} (HTTP {sc}): בדוק את מפתח ה-API.", retryable=False, status_code=sc)
        if sc == 404:
            raise ProviderError(f"המודל המבוקש או הנתיב לא נמצאו אצל {provider} (HTTP 404).", retryable=False, status_code=sc)
        if sc == 429:
            raise ProviderError(f"חריגה ממגבלת קצב הבקשות (Rate Limit 429) מול {provider}.", retryable=True, status_code=sc, retry_after=retry_after)
        if sc >= 500:
            raise ProviderError(f"שגיאת שרת זמנית אצל {provider} (HTTP {sc}).", retryable=True, status_code=sc)
        raise ProviderError(f"שגיאת בקשה מול {provider} (HTTP {sc}): {detail}", retryable=False, status_code=sc)
