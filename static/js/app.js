/* app.js
   Plain JS single-page UI to drive your LangGraph pipeline.
   Works with your existing style.css classes:
   - .auth-container / .dashboard / .report-container
   - .card / .auth-card
   - .spinner, .error, .download-btn

   Assumes there is an existing index.html with these root containers:
     <div id="app"></div>
   Or you can change mountEl below.

   Backend API assumed (matches the flows we discussed):
     POST   {API_BASE}/report/start      { topic, max_analysts, thread_id, human_analyst_feedback }
     POST   {API_BASE}/report/feedback   { thread_id, feedback }
     GET    {API_BASE}/report/state/:id
     POST   {API_BASE}/report/export     { thread_id, topic, format } -> { path } or { download_url }
*/

(() => {
  // -------------------------
  // Config
  // -------------------------
  const DEFAULTS = {
    apiBase: "http://localhost:8000",
    threadId: "ui-thread-1",
    maxAnalysts: 3,
    topic: "Impact of LLMs over the Future of Marketing?",
  };

  // -------------------------
  // State
  // -------------------------
  const state = {
    apiBase: load("apiBase", DEFAULTS.apiBase),
    threadId: load("threadId", DEFAULTS.threadId),
    maxAnalysts: Number(load("maxAnalysts", DEFAULTS.maxAnalysts)),
    topic: load("topic", DEFAULTS.topic),

    busy: false,
    error: null,

    run: null, // { thread_id, status, values }
    feedback: "",
    // pseudo-auth (optional)
    loggedIn: load("loggedIn", "false") === "true",
    userEmail: load("userEmail", ""),
  };

  // -------------------------
  // Mount
  // -------------------------
  const mountEl = document.getElementById("app") || document.body;

  // -------------------------
  // Utilities
  // -------------------------
  function save(k, v) {
    try {
      localStorage.setItem(k, String(v));
    } catch {}
  }
  function load(k, fallback) {
    try {
      const v = localStorage.getItem(k);
      return v == null ? fallback : v;
    } catch {
      return fallback;
    }
  }

  function setBusy(v) {
    state.busy = v;
    render();
  }
  function setError(msg) {
    state.error = msg;
    render();
  }

  function escapeHtml(s) {
    return (s ?? "")
      .toString()
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function persona(a) {
    if (!a) return "";
    return `Name: ${a.name}\nRole: ${a.role}\nAffiliation: ${a.affiliation}\nDescription: ${a.description}\n`;
  }

  async function postJSON(url, body) {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }

  async function getJSON(url) {
    const res = await fetch(url);
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }

  function downloadFromResponse(exportRes) {
    // Flexible: backend can return {download_url} or {path}
    if (!exportRes) return;
    const downloadUrl = exportRes.download_url || exportRes.url || null;

    if (downloadUrl) {
      // open in new tab
      window.open(downloadUrl, "_blank", "noopener,noreferrer");
      return;
    }

    // If only a server path is returned, just show it (UI will display it).
  }

  // -------------------------
  // Actions
  // -------------------------
  async function startRun() {
    setBusy(true);
    setError(null);
    try {
      save("apiBase", state.apiBase);
      save("threadId", state.threadId);
      save("maxAnalysts", state.maxAnalysts);
      save("topic", state.topic);

      const run = await postJSON(`${state.apiBase}/report/start`, {
        topic: state.topic,
        max_analysts: Number(state.maxAnalysts),
        thread_id: state.threadId,
        human_analyst_feedback: "",
      });
      state.run = run;
    } catch (e) {
      setError(String(e?.message || e));
    } finally {
      setBusy(false);
    }
  }

  async function submitFeedback() {
    setBusy(true);
    setError(null);
    try {
      const run = await postJSON(`${state.apiBase}/report/feedback`, {
        thread_id: state.threadId,
        feedback: state.feedback || "",
      });
      state.run = run;
    } catch (e) {
      setError(String(e?.message || e));
    } finally {
      setBusy(false);
    }
  }

  async function refreshState() {
    setBusy(true);
    setError(null);
    try {
      const run = await getJSON(`${state.apiBase}/report/state/${encodeURIComponent(state.threadId)}`);
      state.run = run;
    } catch (e) {
      setError(String(e?.message || e));
    } finally {
      setBusy(false);
    }
  }

  async function exportReport(format) {
    setBusy(true);
    setError(null);
    try {
      const res = await postJSON(`${state.apiBase}/report/export`, {
        thread_id: state.threadId,
        topic: state.topic,
        format,
      });
      // show result
      state.run = state.run || { thread_id: state.threadId, status: "running", values: {} };
      state.run._lastExport = res;
      downloadFromResponse(res);
    } catch (e) {
      setError(String(e?.message || e));
    } finally {
      setBusy(false);
    }
  }

  // Optional pseudo-auth: purely client side (no security). Remove if not needed.
  function login(email) {
    state.loggedIn = true;
    state.userEmail = email || "";
    save("loggedIn", "true");
    save("userEmail", state.userEmail);
    render();
  }
  function logout() {
    state.loggedIn = false;
    save("loggedIn", "false");
    render();
  }

  // -------------------------
  // Rendering
  // -------------------------
  function render() {
    // Choose view
    if (!state.loggedIn) {
      mountEl.innerHTML = authView();
      bindAuthHandlers();
      return;
    }

    mountEl.innerHTML = dashboardView();
    bindDashboardHandlers();
  }

  function authView() {
    return `
      <div class="auth-container">
        <div class="auth-card">
          <h2>Research Analyst Studio</h2>
          <p class="subtitle">Login to run the Interview + Report generation flow</p>

          ${state.error ? `<div class="error">${escapeHtml(state.error)}</div>` : ""}

          <input id="email" type="email" placeholder="Email (any value)" value="${escapeHtml(state.userEmail)}" />
          <input id="password" type="password" placeholder="Password (not checked)" />

          <button id="loginBtn">${state.busy ? "Please wait..." : "Login"}</button>
          <div class="switch">
            <span>Tip:</span> this is a demo login (client-side only).
          </div>
        </div>
      </div>
    `;
  }

  function dashboardView() {
    const run = state.run;
    const values = (run && run.values) || {};
    const status = (run && run.status) || "idle";

    const analysts = Array.isArray(values.analysts) ? values.analysts : [];
    const sections = Array.isArray(values.sections) ? values.sections : [];
    const intro = values.introduction || "";
    const content = values.content || "";
    const conclusion = values.conclusion || "";
    const finalReport = values.final_report || "";

    const lastExport = run && run._lastExport ? JSON.stringify(run._lastExport, null, 2) : "";

    return `
      <div class="dashboard">
        <div class="card" style="width: min(980px, 95vw); text-align:left;">
          <div style="display:flex; align-items:flex-start; justify-content:space-between; gap:12px;">
            <div>
              <h2 style="margin-top:0;">Autonomous Report Generator</h2>
              <div class="subtitle" style="margin-bottom:0;">
                Status: <b>${escapeHtml(status)}</b>
              </div>
            </div>
            <div style="display:flex; gap:10px; align-items:center;">
              <button id="refreshBtn" ${state.busy ? "disabled" : ""}>Refresh</button>
              <button id="logoutBtn" ${state.busy ? "disabled" : ""} style="background:#0f172a;">Logout</button>
            </div>
          </div>

          ${state.error ? `<div class="error" style="margin-top:10px;">${escapeHtml(state.error)}</div>` : ""}

          <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:12px; margin-top:14px;">
            ${textField("API Base", "apiBase", state.apiBase, "http://localhost:8000")}
            ${textField("Thread ID", "threadId", state.threadId, "ui-thread-1")}
            ${numberField("Max Analysts", "maxAnalysts", state.maxAnalysts, 1)}
          </div>

          <div style="margin-top:12px;">
            <div style="font-weight:600; color:#1e3a8a;">Topic</div>
            <textarea id="topic" rows="3" placeholder="Enter research topic...">${escapeHtml(state.topic)}</textarea>
          </div>

          <div style="display:flex; gap:10px; align-items:center; margin-top:12px;">
            <button id="startBtn" ${state.busy ? "disabled" : ""}>
              ${state.busy ? "Running..." : "Start / Run Until Feedback"}
            </button>
            <div style="display:flex; align-items:center; gap:10px;">
              ${state.busy ? `<div class="spinner" style="width:34px;height:34px;border-width:4px;"></div>` : ""}
            </div>
          </div>

          ${status === "awaiting_feedback" ? feedbackPanel() : ""}

          ${analystsPanel(analysts)}

          ${sectionsPanel(sections)}

          ${reportBranchPanel(intro, content, conclusion)}

          ${finalReportPanel(finalReport, lastExport)}
        </div>
      </div>
    `;
  }

  function textField(label, id, value, placeholder) {
    return `
      <label style="display:block;">
        <div style="font-weight:600; color:#1e3a8a;">${escapeHtml(label)}</div>
        <input id="${escapeHtml(id)}" type="text" value="${escapeHtml(value)}" placeholder="${escapeHtml(placeholder || "")}" />
      </label>
    `;
  }

  function numberField(label, id, value, min) {
    return `
      <label style="display:block;">
        <div style="font-weight:600; color:#1e3a8a;">${escapeHtml(label)}</div>
        <input id="${escapeHtml(id)}" type="number" min="${min ?? 1}" value="${escapeHtml(value)}" />
      </label>
    `;
  }

  function feedbackPanel() {
    return `
      <div style="margin-top:18px; padding:12px; border:1px solid #e2e8f0; border-radius:14px; background:#f8fafc;">
        <div style="font-weight:800; color:#0f172a;">Human Feedback (paused)</div>
        <div style="color:#475569; font-size:0.95rem; margin-top:4px;">
          The graph is interrupted before <code>human_feedback</code>. Add feedback (optional) and resume.
        </div>

        <textarea id="feedback" rows="3" placeholder="Enter feedback or leave blank to continue...">${escapeHtml(
          state.feedback
        )}</textarea>

        <div style="display:flex; gap:10px; margin-top:10px;">
          <button id="submitFeedbackBtn" ${state.busy ? "disabled" : ""}>Submit Feedback & Resume</button>
          <button id="clearFeedbackBtn" ${state.busy ? "disabled" : ""} style="background:#64748b;">Clear</button>
        </div>
      </div>
    `;
  }

  function analystsPanel(analysts) {
    const body =
      analysts.length === 0
        ? `<div class="subtitle">No analysts yet.</div>`
        : `<div style="display:grid; grid-template-columns: 1fr 1fr; gap:12px; margin-top:12px;">
            ${analysts
              .map((a, i) => {
                const p = persona(a);
                return `
                  <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:14px; padding:12px;">
                    <div style="font-weight:800; color:#0f172a;">${escapeHtml(a.name || `Analyst #${i + 1}`)}</div>
                    <div style="color:#475569; margin-top:2px;">${escapeHtml(
                      (a.role || "") + (a.affiliation ? " — " + a.affiliation : "")
                    )}</div>
                    <div style="margin-top:8px;">${escapeHtml(a.description || "")}</div>
                    <details style="margin-top:10px;">
                      <summary style="cursor:pointer;">Persona string</summary>
                      <pre style="${inlinePreStyle()}">${escapeHtml(p)}</pre>
                    </details>
                  </div>
                `;
              })
              .join("")}
          </div>`;

    return `
      <div style="margin-top:18px;">
        <div style="font-weight:800; color:#0f172a; font-size:1.05rem;">Analysts</div>
        ${body}
      </div>
    `;
  }

  function sectionsPanel(sections) {
    const body =
      sections.length === 0
        ? `<div class="subtitle">No interview sections yet.</div>`
        : `<div style="display:grid; gap:12px; margin-top:12px;">
            ${sections
              .map(
                (s, i) => `
              <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:14px; padding:12px;">
                <div style="font-weight:800; color:#0f172a;">Section #${i + 1}</div>
                <pre style="${inlinePreStyle({ maxH: 220 })}">${escapeHtml(String(s))}</pre>
              </div>
            `
              )
              .join("")}
          </div>`;

    return `
      <div style="margin-top:18px;">
        <div style="font-weight:800; color:#0f172a; font-size:1.05rem;">Interview-generated Sections</div>
        <div class="subtitle" style="margin-bottom:0;">
          Aggregated from each <code>conduct_interview</code> run into <code>ResearchGraphState.sections</code>.
        </div>
        ${body}
      </div>
    `;
  }

  function reportBranchPanel(intro, content, conclusion) {
    return `
      <div style="margin-top:18px;">
        <div style="font-weight:800; color:#0f172a; font-size:1.05rem;">Report Branch Outputs</div>
        <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:12px; margin-top:12px;">
          ${branchBox("Introduction", intro)}
          ${branchBox("Content", content)}
          ${branchBox("Conclusion", conclusion)}
        </div>
      </div>
    `;
  }

  function branchBox(title, text) {
    const body = text
      ? `<pre style="${inlinePreStyle({ maxH: 220 })}">${escapeHtml(String(text))}</pre>`
      : `<div class="subtitle" style="margin-top:10px;">—</div>`;
    return `
      <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:14px; padding:12px;">
        <div style="font-weight:800; color:#0f172a;">${escapeHtml(title)}</div>
        ${body}
      </div>
    `;
  }

  function finalReportPanel(finalReport, lastExport) {
    const hasReport = !!(finalReport && String(finalReport).trim());

    return `
      <div style="margin-top:18px;">
        <div style="display:flex; justify-content:space-between; align-items:center; gap:10px;">
          <div style="font-weight:800; color:#0f172a; font-size:1.05rem;">Final Report</div>
          <div style="display:flex; gap:10px;">
            <button id="exportDocxBtn" ${!hasReport || state.busy ? "disabled" : ""}>Export DOCX</button>
            <button id="exportPdfBtn" ${!hasReport || state.busy ? "disabled" : ""} style="background:#0ea5e9;">
              Export PDF
            </button>
          </div>
        </div>

        ${
          hasReport
            ? `<pre style="${inlinePreStyle({ maxH: 420 })}">${escapeHtml(String(finalReport))}</pre>`
            : `<div class="subtitle" style="margin-top:10px;">Not finalized yet.</div>`
        }

        ${
          lastExport
            ? `
              <details style="margin-top:10px;">
                <summary style="cursor:pointer;">Last export response</summary>
                <pre style="${inlinePreStyle({ maxH: 160 })}">${escapeHtml(lastExport)}</pre>
              </details>
            `
            : ""
        }
      </div>
    `;
  }

  function inlinePreStyle(opts = {}) {
    const maxH = opts.maxH ?? 200;
    return `
      margin-top:10px;
      white-space:pre-wrap;
      border:1px solid #e2e8f0;
      border-radius:12px;
      padding:12px;
      background:#f8fafc;
      font-size:13px;
      line-height:1.45;
      max-height:${maxH}px;
      overflow:auto;
    `;
  }

  // -------------------------
  // Bind handlers (event delegation)
  // -------------------------
  function bindAuthHandlers() {
    const email = mountEl.querySelector("#email");
    const loginBtn = mountEl.querySelector("#loginBtn");

    loginBtn?.addEventListener("click", () => {
      state.error = null;
      const em = email?.value?.trim() || "";
      if (!em) {
        setError("Please enter an email.");
        return;
      }
      login(em);
    });
  }

  function bindDashboardHandlers() {
    // Inputs
    const apiBase = mountEl.querySelector("#apiBase");
    const threadId = mountEl.querySelector("#threadId");
    const maxAnalysts = mountEl.querySelector("#maxAnalysts");
    const topic = mountEl.querySelector("#topic");

    apiBase?.addEventListener("input", (e) => {
      state.apiBase = e.target.value;
      save("apiBase", state.apiBase);
    });
    threadId?.addEventListener("input", (e) => {
      state.threadId = e.target.value;
      save("threadId", state.threadId);
    });
    maxAnalysts?.addEventListener("input", (e) => {
      state.maxAnalysts = Number(e.target.value || 1);
      save("maxAnalysts", state.maxAnalysts);
    });
    topic?.addEventListener("input", (e) => {
      state.topic = e.target.value;
      save("topic", state.topic);
    });

    // Buttons
    mountEl.querySelector("#startBtn")?.addEventListener("click", startRun);
    mountEl.querySelector("#refreshBtn")?.addEventListener("click", refreshState);
    mountEl.querySelector("#logoutBtn")?.addEventListener("click", logout);

    // Feedback panel (conditional)
    mountEl.querySelector("#feedback")?.addEventListener("input", (e) => {
      state.feedback = e.target.value;
    });
    mountEl.querySelector("#submitFeedbackBtn")?.addEventListener("click", submitFeedback);
    mountEl.querySelector("#clearFeedbackBtn")?.addEventListener("click", () => {
      state.feedback = "";
      render();
    });

    // Exports
    mountEl.querySelector("#exportDocxBtn")?.addEventListener("click", () => exportReport("docx"));
    mountEl.querySelector("#exportPdfBtn")?.addEventListener("click", () => exportReport("pdf"));
  }

  // -------------------------
  // Start
  // -------------------------
  render();
})();