async function translate(text, targetLang = "he", sourceLang = "auto") {
  const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=${sourceLang}&tl=${targetLang}&dt=t&q=${encodeURIComponent(text)}`;
  const response = await fetch(url);
  const data = await response.json();
  
  return await data[0].map(item => item[0]).join("")
}

export {translate}