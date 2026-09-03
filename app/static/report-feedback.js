/* The server owns the per-user answer. No cookies/storage flags or user IDs. */
(() => {
    const question = document.getElementById("report-feedback-question");
    let generation = 0;
    async function refresh() {
        if (!question) return;
        const ticket = ++generation;
        question.hidden = true;
        try {
            const response = await fetch("/feedback/report-question/state", {cache: "no-store"});
            const state = response.ok ? await response.json() : null;
            if (ticket === generation) question.hidden = state?.answered !== false;
        } catch (_) { /* Keep a cached question hidden until the server is reachable. */ }
    }
    // A cached report opened via Back must not restore an already answered form.
    window.addEventListener("pagehide", () => { generation++; if (question) question.hidden = true; });
    window.addEventListener("pageshow", event => { if (event.persisted) refresh(); });
    document.addEventListener("visibilitychange", () => { if (!document.hidden) refresh(); });
    // Other visible tabs recheck their own authenticated state, not a shared flag.
    try {
        const channel = new BroadcastChannel("dmatrix-report-question");
        channel.onmessage = event => { if (event.data === "answer-saved") refresh(); };
        if (document.getElementById("report-feedback-thanks")) channel.postMessage("answer-saved");
    } catch (_) { /* Optional optimisation. pageshow/visibility still work. */ }
})();
