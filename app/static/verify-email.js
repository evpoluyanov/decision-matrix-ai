(function () {
    "use strict";
    document.addEventListener("DOMContentLoaded", function () {
        const form = document.getElementById("verify-email-form");
        if (!form || form.dataset.submitted === "true") {
            return;
        }
        form.dataset.submitted = "true";
        window.setTimeout(function () {
            form.requestSubmit();
        }, 50);
    });
}());
