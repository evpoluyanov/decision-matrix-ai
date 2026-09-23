(function () {
    "use strict";

    function initialise() {
        const question = document.getElementById("decision-question");
        const templateKey = document.getElementById("template-key");
        const cards = Array.from(document.querySelectorAll("[data-template-key]"));
        if (!question || !templateKey || cards.length === 0) {
            return;
        }

        function selectCard(card, fillExample) {
            cards.forEach((item) => {
                const selected = item === card;
                item.setAttribute("aria-pressed", selected ? "true" : "false");
                item.classList.toggle("border-primary", selected);
                item.classList.toggle("border", selected);
            });
            templateKey.value = card.dataset.templateKey || "custom";
            if (fillExample && (!question.value.trim() || question.dataset.templateFilled === "true")) {
                question.value = card.dataset.templateExample || "";
                question.dataset.templateFilled = "true";
            }
            question.focus();
            question.select();
        }

        cards.forEach((card) => {
            card.addEventListener("click", () => selectCard(card, true));
            if (card.getAttribute("aria-pressed") === "true") {
                selectCard(card, false);
            }
        });

        question.addEventListener("input", () => {
            question.dataset.templateFilled = "false";
        });
    }

    document.addEventListener("DOMContentLoaded", initialise);
}());
