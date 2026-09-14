/* The server owns the per-user answer. No cookies/storage flags or user IDs. */
(() => {
    const question = document.getElementById("report-feedback-question");
    const form = document.getElementById("report-feedback-form");
    const thanks = document.getElementById("report-feedback-thanks");
    const positionKey = "dmatrix-report-feedback-position:" + location.pathname;
    const storePosition = () => {
        try {
            sessionStorage.setItem(positionKey, JSON.stringify({
                path: location.pathname,
                x: scrollX,
                y: scrollY,
                at: Date.now(),
            }));
        } catch (_) { /* Position restoration is optional. */ }
    };
    const restorePosition = () => {
        if (!thanks) return;
        let saved = null;
        try {
            saved = JSON.parse(sessionStorage.getItem(positionKey));
            sessionStorage.removeItem(positionKey);
        } catch (_) { /* Ignore unavailable or invalid session storage. */ }
        if (!saved || saved.path !== location.pathname || Date.now() - saved.at > 600000) return;
        thanks.setAttribute("tabindex", "-1");
        requestAnimationFrame(() => requestAnimationFrame(() => {
            thanks.focus({preventScroll: true});
            scrollTo(saved.x, saved.y);
        }));
    };
    form?.addEventListener("submit", storePosition);
    restorePosition();
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
        if (thanks) channel.postMessage("answer-saved");
    } catch (_) { /* Optional optimisation. pageshow/visibility still work. */ }
})();
