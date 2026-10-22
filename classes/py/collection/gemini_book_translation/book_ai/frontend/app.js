let appInfo = {};
let activeProjectId = null;
let sseSource = null;
let editingUnitId = null;

function showToast(msg, isError = false) {
    const box = document.getElementById("toast-box");
    box.textContent = msg;
    box.style.background = isError ? "var(--danger)" : "var(--primary)";
    box.classList.remove("hidden");
    setTimeout(() => box.classList.add("hidden"), 4000);
}

async function api(path, options = {}) {
    const res = await fetch(path, options);
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
        const err = new Error(data.message || data.detail || "שגיאה בביצוע הבקשה");
        err.status = res.status;
        err.data = data;
        throw err;
    }
    return data;
}

async function initApp() {
    const savedTheme = localStorage.getItem("bookai_theme") || "theme-dark";
    document.body.className = savedTheme;

    appInfo = await api("/api/info");
    populateSelects();
    await loadProjectsList();
    bindEvents();
}

function populateSelects() {
    const langEntries = Object.entries(appInfo.languages || {});
    for (const selId of ["new-src-lang", "new-tgt-lang", "set-src-lang", "set-tgt-lang"]) {
        const el = document.getElementById(selId);
        el.innerHTML = langEntries
            .filter(([code]) => !(selId.includes("tgt") && code === "auto"))
            .map(([code, info]) => `<option value="${code}">${info.name} (${code})</option>`)
            .join("");
    }
    document.getElementById("new-src-lang").value = "auto";
    document.getElementById("new-tgt-lang").value = "he";

    const goalEntries = Object.entries(appInfo.goals || {});
    for (const selId of ["new-goal", "set-goal"]) {
        document.getElementById(selId).innerHTML = goalEntries
            .map(([k, v]) => `<option value="${k}">${v}</option>`).join("");
    }

    const providers = Object.keys(appInfo.models || {});
    for (const selId of ["new-provider", "set-provider"]) {
        document.getElementById(selId).innerHTML = providers
            .map(p => `<option value="${p}">${p.toUpperCase()}</option>`).join("");
    }
    updateModelSuggestions("gemini");
}

function updateModelSuggestions(provider) {
    const list = (appInfo.models && appInfo.models[provider]) || [];
    const dl = document.getElementById("models-datalist");
    dl.innerHTML = list.map(m => `<option value="${m.id}">${m.name} - ${m.notes}</option>`).join("");
    if (list.length > 0) {
        document.getElementById("new-model").value = list[0].id;
    }
}

async function loadProjectsList() {
    const { projects } = await api("/api/projects");
    const tbody = document.getElementById("projects-tbody");
    if (!projects.length) {
        tbody.innerHTML = `<tr><td colspan="10" style="text-align:center;">אין פרויקטים עדיין. לחץ על "+ פרויקט חדש" כדי להתחיל.</td></tr>`;
        return;
    }
    tbody.innerHTML = projects.map(p => {
        const st = p.stats || {};
        const us = p.usage || {};
        return `
        <tr>
            <td><strong>${escapeHtml(p.name)}</strong></td>
            <td>${escapeHtml(p.original_filename)} <span class="badge">${p.source_format}</span></td>
            <td>${p.settings.src_lang} ⬅ ${p.settings.tgt_lang}</td>
            <td>${appInfo.goals[p.settings.goal] || p.settings.goal}</td>
            <td>${p.settings.provider} / ${p.settings.model}</td>
            <td><span class="badge ${p.status}">${p.status}</span></td>
            <td>${st.done || 0} / ${st.failed || 0} / ${st.total || 0}</td>
            <td>${st.progress_pct || 0}%</td>
            <td>$${(us.estimated_cost || 0).toFixed(4)}</td>
            <td>
                <button class="btn primary" onclick="openProject('${p.id}')">פתח</button>
                <button class="btn danger" onclick="deleteProject('${p.id}')">מחק</button>
            </td>
        </tr>`;
    }).join("");
}

async function openProject(projectId) {
    activeProjectId = projectId;
    document.getElementById("screen-home").classList.add("hidden");
    document.getElementById("screen-workspace").classList.remove("hidden");
    document.getElementById("btn-back-home").classList.remove("hidden");

    const data = await api(`/api/projects/${projectId}`);
    const p = data.project;
    document.getElementById("ws-title").textContent = p.name;
    let sub = `קובץ מקור: ${p.original_filename} (${p.source_format}) | מחבר: ${p.metadata.author || "לא ידוע"}`;
    if (p.metadata.extraction_report) {
        sub += ` | ⚠️ ${p.metadata.extraction_report.limitations_notice}`;
    }
    document.getElementById("ws-subtitle").textContent = sub;

    const dlBtn = document.getElementById("btn-ws-download");
    if (p.output_path) {
        dlBtn.href = `/api/projects/${projectId}/download`;
        dlBtn.classList.remove("hidden");
    } else {
        dlBtn.classList.add("hidden");
    }

    const chOpts = `<option value="">כל הפרקים</option>` +
        data.chapters.map(c => `<option value="${c.id}">${c.ord}. ${escapeHtml(c.title)}</option>`).join("");
    document.getElementById("filter-chapter").innerHTML = chOpts;
    document.getElementById("preview-chapter-select").innerHTML =
        data.chapters.map(c => `<option value="${c.id}">${c.ord}. ${escapeHtml(c.title)}</option>`).join("");

    fillSettingsForm(p.settings);
    updateLiveMetrics(data.live);
    await loadUnits();
    startSSE(projectId);
}

function startSSE(projectId) {
    if (sseSource) sseSource.close();
    sseSource = new EventSource(`/api/projects/${projectId}/events`);
    sseSource.onmessage = (ev) => {
        const state = JSON.parse(ev.data);
        updateLiveMetrics(state);
    };
}

function updateLiveMetrics(state) {
    if (!state || !state.stats) return;
    const st = state.stats;
    const us = state.usage || {};
    const pct = st.progress_pct || 0;
    const fill = document.getElementById("ws-progress-fill");
    fill.style.width = `${pct}%`;
    fill.textContent = `${pct}%`;

    document.getElementById("m-status").textContent = state.status;
    document.getElementById("m-done").textContent = `${st.done} / ${st.total}`;
    document.getElementById("m-active").textContent = state.active_units || 0;
    document.getElementById("m-pending").textContent = st.pending || 0;
    document.getElementById("m-issues").textContent = `${st.failed || 0} / ${st.flagged || 0}`;
    document.getElementById("m-chapter").textContent = state.current_chapter || "-";
    const etaStr = state.eta_reliable ? `${state.eta_seconds} שניות` : "אין אומדן אמין כעת";
    document.getElementById("m-eta").textContent = `${state.elapsed_sec || 0}s / ${etaStr}`;
    document.getElementById("m-tokens").textContent = `${us.input_tokens || 0} / ${us.output_tokens || 0}`;
    document.getElementById("m-cost").textContent = `$${(us.estimated_cost || 0).toFixed(4)}`;
}

async function loadUnits() {
    if (!activeProjectId) return;
    const status = document.getElementById("filter-status").value;
    const chapter = document.getElementById("filter-chapter").value;
    const search = document.getElementById("filter-search").value;
    const q = new URLSearchParams({ status, chapter_id: chapter, search }).toString();
    const { units } = await api(`/api/projects/${activeProjectId}/units?${q}`);
    const tbody = document.getElementById("units-tbody");

    tbody.innerHTML = units.slice(0, 300).map(u => `
        <tr>
            <td><code>${u.id}</code></td>
            <td>${u.unit_type}</td>
            <td><span class="badge ${u.status}">${u.status}</span></td>
            <td dir="auto">${escapeHtml(u.source_text)}</td>
            <td dir="auto">
                ${u.result_text ? escapeHtml(u.result_text) : "<span class='muted'>-</span>"}
                ${u.error_msg ? `<div style="color:var(--danger);font-size:0.78rem;">⚠️ ${escapeHtml(u.error_msg)}</div>` : ""}
            </td>
            <td>${u.attempts}</td>
            <td>
                <button class="btn secondary" onclick="openEditModal('${u.id}')">✏️ ערוך</button>
                <button class="btn secondary" onclick="resendUnit('${u.id}', false)">🔄 שלח שוב</button>
            </td>
        </tr>
    `).join("");
}

async function openEditModal(unitId) {
    const { units } = await api(`/api/projects/${activeProjectId}/units?search=${unitId}`);
    const u = units.find(x => x.id === unitId);
    if (!u) return;
    editingUnitId = unitId;
    document.getElementById("edit-unit-id").textContent = unitId;
    document.getElementById("edit-src-text").value = u.source_text;
    document.getElementById("edit-tgt-text").value = u.result_text || u.source_text;
    document.getElementById("modal-edit").classList.remove("hidden");
}

async function resendUnit(unitId, forceOverride = false) {
    try {
        await api(`/api/projects/${activeProjectId}/control`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ action: "resend_unit", unit_id: unitId, force_manual_override: forceOverride })
        });
        showToast(`יחידה ${unitId} נשלחה לעיבוד מחדש.`);
        setTimeout(loadUnits, 1200);
    } catch (e) {
        if (e.status === 409 && e.data.error === "MANUAL_EDIT_PROTECTED") {
            if (confirm(`${e.data.message}\n\nטקסט נוכחי:\n${e.data.current_text}`)) {
                await resendUnit(unitId, true);
            }
        } else {
            showToast(e.message, true);
        }
    }
}

function fillSettingsForm(s) {
    document.getElementById("set-goal").value = s.goal;
    document.getElementById("set-src-lang").value = s.src_lang;
    document.getElementById("set-tgt-lang").value = s.tgt_lang;
    document.getElementById("set-provider").value = s.provider;
    document.getElementById("set-model").value = s.model;
    document.getElementById("set-base-url").value = s.base_url || "";
    document.getElementById("set-temp").value = s.temperature ?? 0.3;
    document.getElementById("set-chunk-chars").value = s.chunk_chars;
    document.getElementById("set-overlap").value = s.overlap;
    document.getElementById("set-concurrency").value = s.concurrency;
    document.getElementById("set-rpm").value = s.rpm;
    document.getElementById("set-attempts").value = s.attempts;
    document.getElementById("set-api-retries").value = s.api_retries;
    document.getElementById("set-timeout").value = s.timeout;
    document.getElementById("set-price-in").value = s.price_in;
    document.getElementById("set-price-out").value = s.price_out;
    document.getElementById("set-format-failure").value = s.on_format_failure;
    document.getElementById("set-extra").value = s.extra || "";
    document.getElementById("set-preserve-layout").checked = s.layout?.preserve_original ?? true;
    document.getElementById("set-font-family").value = s.layout?.font_family || "";
    document.getElementById("set-font-size").value = s.layout?.font_size || "";
    document.getElementById("set-line-height").value = s.layout?.line_height || "";
    document.getElementById("set-force-dir").value = s.layout?.force_direction || "auto";
    document.getElementById("set-rtl-isolate").checked = s.rtl_isolate ?? true;
    document.getElementById("set-mock").checked = s.mock ?? false;
}

async function deleteProject(projectId) {
    if (!confirm("האם למחוק את הפרויקט ונתוני העבודה שלו?")) return;
    await api(`/api/projects/${projectId}`, { method: "DELETE" });
    showToast("הפרויקט נמחק.");
    await loadProjectsList();
}

function escapeHtml(str) {
    return String(str || "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
}

function bindEvents() {
    document.getElementById("btn-theme-toggle").onclick = () => {
        const next = document.body.classList.contains("theme-dark") ? "theme-light" : "theme-dark";
        document.body.className = next;
        localStorage.setItem("bookai_theme", next);
    };

    document.getElementById("btn-back-home").onclick = () => {
        if (sseSource) sseSource.close();
        activeProjectId = null;
        document.getElementById("screen-workspace").classList.add("hidden");
        document.getElementById("btn-back-home").classList.add("hidden");
        document.getElementById("screen-home").classList.remove("hidden");
        loadProjectsList();
    };

    document.getElementById("btn-new-project-toggle").onclick = () => {
        document.getElementById("panel-create-project").classList.toggle("hidden");
    };
    document.getElementById("btn-cancel-create").onclick = () => {
        document.getElementById("panel-create-project").classList.add("hidden");
    };

    document.getElementById("new-provider").onchange = (e) => updateModelSuggestions(e.target.value);

    document.getElementById("form-create-project").onsubmit = async (e) => {
        e.preventDefault();
        const fileInput = document.getElementById("input-book-file");
        if (!fileInput.files.length) return showToast("בחר קובץ ספר תחילה", true);

        const fd = new FormData();
        fd.append("file", fileInput.files[0]);
        fd.append("name", document.getElementById("new-proj-name").value);
        fd.append("settings_json", JSON.stringify({
            src_lang: document.getElementById("new-src-lang").value,
            tgt_lang: document.getElementById("new-tgt-lang").value,
            goal: document.getElementById("new-goal").value,
            provider: document.getElementById("new-provider").value,
            model: document.getElementById("new-model").value,
            mock: document.getElementById("new-mock-mode").checked
        }));

        try {
            showToast("מנתח מבנה ספר ויוצר פרויקט...");
            const proj = await api("/api/projects", { method: "POST", body: fd });
            document.getElementById("panel-create-project").classList.add("hidden");
            await openProject(proj.id);
        } catch (err) {
            showToast(err.message, true);
        }
    };

    document.querySelectorAll("[data-ctrl]").forEach(btn => {
        btn.onclick = async () => {
            try {
                await api(`/api/projects/${activeProjectId}/control`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ action: btn.dataset.ctrl })
                });
                showToast(`פעולה בוצעה: ${btn.dataset.ctrl}`);
                setTimeout(loadUnits, 1000);
            } catch (err) {
                showToast(err.message, true);
            }
        };
    });

    document.querySelectorAll(".tab-btn").forEach(btn => {
        btn.onclick = async () => {
            document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
            document.querySelectorAll(".tab-content").forEach(c => c.classList.add("hidden"));
            btn.classList.add("active");
            const target = btn.dataset.tab;
            document.getElementById(target).classList.remove("hidden");

            if (target === "tab-units") await loadUnits();
            if (target === "tab-preview") await loadPreview();
            if (target === "tab-glossary") await loadGlossaryAndTM();
            if (target === "tab-logs") await loadLogs();
        };
    });

    document.getElementById("btn-filter-apply").onclick = loadUnits;
    document.getElementById("preview-chapter-select").onchange = loadPreview;

    document.getElementById("btn-ws-build").onclick = async () => {
        try {
            showToast("מרכיב ומאמת קובץ EPUB סופי...");
            const res = await api(`/api/projects/${activeProjectId}/build`, { method: "POST" });
            const rep = res.report;
            const box = document.getElementById("build-report-box");
            box.classList.remove("hidden");
            if (rep.valid) {
                box.textContent = `✅ הפקת ה-EPUB עברה את כל בדיקות השלמות (${rep.replaced_units}/${rep.expected_units} יחידות).`;
                const dl = document.getElementById("btn-ws-download");
                dl.href = `/api/projects/${activeProjectId}/download`;
                dl.classList.remove("hidden");
                showToast("הספר הופק ואומת בהצלחה! לחץ על 'הורד EPUB'.");
            } else {
                box.textContent = `❌ שגיאות באימות הפלט: ${rep.errors.join(" | ")}`;
                showToast("אימות הפלט נכשל. ראה פירוט בלשונית היומן.", true);
            }
        } catch (err) {
            showToast(err.message, true);
        }
    };

    document.getElementById("form-ws-settings").onsubmit = async (e) => {
        e.preventDefault();
        const payload = {
            goal: document.getElementById("set-goal").value,
            src_lang: document.getElementById("set-src-lang").value,
            tgt_lang: document.getElementById("set-tgt-lang").value,
            provider: document.getElementById("set-provider").value,
            model: document.getElementById("set-model").value,
            base_url: document.getElementById("set-base-url").value,
            temperature: parseFloat(document.getElementById("set-temp").value),
            chunk_chars: parseInt(document.getElementById("set-chunk-chars").value, 10),
            overlap: parseInt(document.getElementById("set-overlap").value, 10),
            concurrency: parseInt(document.getElementById("set-concurrency").value, 10),
            rpm: parseInt(document.getElementById("set-rpm").value, 10),
            attempts: parseInt(document.getElementById("set-attempts").value, 10),
            api_retries: parseInt(document.getElementById("set-api-retries").value, 10),
            timeout: parseInt(document.getElementById("set-timeout").value, 10),
            price_in: parseFloat(document.getElementById("set-price-in").value),
            price_out: parseFloat(document.getElementById("set-price-out").value),
            on_format_failure: document.getElementById("set-format-failure").value,
            extra: document.getElementById("set-extra").value,
            rtl_isolate: document.getElementById("set-rtl-isolate").checked,
            mock: document.getElementById("set-mock").checked,
            layout: {
                preserve_original: document.getElementById("set-preserve-layout").checked,
                font_family: document.getElementById("set-font-family").value,
                font_size: document.getElementById("set-font-size").value,
                line_height: document.getElementById("set-line-height").value,
                force_direction: document.getElementById("set-force-dir").value
            }
        };
        await api(`/api/projects/${activeProjectId}/settings`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        showToast("הגדרות הפרויקט נשמרו.");
    };

    document.getElementById("btn-save-edit").onclick = async () => {
        const text = document.getElementById("edit-tgt-text").value;
        await api(`/api/units/${editingUnitId}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ result_text: text })
        });
        document.getElementById("modal-edit").classList.add("hidden");
        showToast("העריכה הידנית נשמרה ומוגנת מפני דריסה.");
        await loadUnits();
    };
    document.getElementById("btn-revert-edit").onclick = async () => {
        const u = await api(`/api/units/${editingUnitId}/revert`, { method: "POST" });
        document.getElementById("edit-tgt-text").value = u.result_text || "";
        showToast("שוחזר לגרסה הקודמת בהיסטוריה.");
        await loadUnits();
    };
    document.getElementById("btn-close-edit").onclick = () => {
        document.getElementById("modal-edit").classList.add("hidden");
    };

    document.getElementById("form-glossary").onsubmit = async (e) => {
        e.preventDefault();
        await api(`/api/projects/${activeProjectId}/glossary`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                source_term: document.getElementById("gl-src").value,
                target_term: document.getElementById("gl-tgt").value,
                term_type: document.getElementById("gl-type").value
            })
        });
        document.getElementById("gl-src").value = "";
        document.getElementById("gl-tgt").value = "";
        await loadGlossaryAndTM();
    };

    document.getElementById("btn-secrets-modal").onclick = () => {
        renderSecretsStatus();
        document.getElementById("modal-secrets").classList.remove("hidden");
    };
    document.getElementById("btn-close-secrets").onclick = () => {
        document.getElementById("modal-secrets").classList.add("hidden");
    };
    document.getElementById("form-secret").onsubmit = async (e) => {
        e.preventDefault();
        const res = await api("/api/secrets", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                provider: document.getElementById("sec-provider").value,
                api_key: document.getElementById("sec-key").value
            })
        });
        appInfo.secrets_status = res.secrets_status;
        document.getElementById("sec-key").value = "";
        renderSecretsStatus();
        showToast("המפתח הוצפן ונשמר בהצלחה.");
    };
    document.getElementById("btn-test-conn").onclick = async () => {
        const prov = document.getElementById("sec-provider").value;
        const model = (appInfo.models[prov] && appInfo.models[prov][0]?.id) || "gemini-2.5-flash";
        try {
            showToast(`בודק חיבור מול ${prov}...`);
            const res = await api("/api/providers/test", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    provider: prov,
                    model: model,
                    temp_api_key: document.getElementById("sec-key").value || null
                })
            });
            showToast(`החיבור תקין! (${res.model} הגיב תוך ${res.elapsed_sec}s)`);
        } catch (err) {
            showToast(err.message, true);
        }
    };

    document.getElementById("btn-clear-logs").onclick = async () => {
        await api(`/api/projects/${activeProjectId}/logs`, { method: "DELETE" });
        await loadLogs();
    };
}

async function loadPreview() {
    const chId = document.getElementById("preview-chapter-select").value;
    const res = await api(`/api/projects/${activeProjectId}/preview?chapter_id=${chId}`);
    document.getElementById("preview-container").innerHTML = res.html;
}

async function loadGlossaryAndTM() {
    const gl = await api(`/api/projects/${activeProjectId}/glossary`);
    document.getElementById("glossary-tbody").innerHTML = gl.entries.map(g => `
        <tr>
            <td>${escapeHtml(g.source_term)}</td>
            <td>${escapeHtml(g.target_term)}</td>
            <td>${g.term_type}</td>
            <td><button class="btn danger" onclick="deleteGlossary('${g.id}')">מחק</button></td>
        </tr>
    `).join("");

    const tm = await api(`/api/projects/${activeProjectId}/tm`);
    document.getElementById("tm-tbody").innerHTML = tm.entries.slice(0, 100).map(t => `
        <tr>
            <td dir="auto">${escapeHtml(t.source_text)}</td>
            <td dir="auto">${escapeHtml(t.target_text)}</td>
            <td>${escapeHtml(t.context)}</td>
        </tr>
    `).join("");
}

async function deleteGlossary(id) {
    await api(`/api/projects/${activeProjectId}/glossary/${id}`, { method: "DELETE" });
    await loadGlossaryAndTM();
}

async function loadLogs() {
    const { logs } = await api(`/api/projects/${activeProjectId}/logs`);
    document.getElementById("logs-tbody").innerHTML = logs.map(l => `
        <tr>
            <td><small>${l.timestamp}</small></td>
            <td><span class="badge ${l.level === 'ERROR' ? 'failed' : ''}">${l.level}</span></td>
            <td>${l.stage}</td>
            <td><code>${l.unit_id || "-"}</code></td>
            <td>${escapeHtml(l.message)}</td>
        </tr>
    `).join("");
}

function renderSecretsStatus() {
    const st = appInfo.secrets_status || {};
    document.getElementById("secrets-status-list").innerHTML = Object.entries(st).map(([p, info]) => `
        <div style="padding:0.35rem 0;border-bottom:1px solid var(--border);">
            <strong>${p.toUpperCase()}:</strong>
            ${info.configured ? "✅ מוגדר ומוכן" : "❌ לא מוגדר"}
            ${info.saved ? "(שמור מוצפן)" : ""} ${info.env ? "(משתנה סביבה)" : ""}
        </div>
    `).join("");
}

window.addEventListener("DOMContentLoaded", initApp);
