(function () {
    "use strict";

    function initialise() {
        const question = document.getElementById("decision-question");
        const templateKey = document.getElementById("template-key");
        const cards = Array.from(document.querySelectorAll("[data-template-key]"));
        if (!question || !templateKey || cards.length === 0) {
            return;
        }

        function selectExample(card, fillExample) {
            cards.forEach((item) => {
                const selected = item === card;
                item.setAttribute("aria-pressed", selected ? "true" : "false");
                item.classList.toggle("active", selected);
            });
            templateKey.value = card.dataset.templateKey || "custom";
            if (fillExample) {
                question.value = card.dataset.templateExample || "";
                question.dataset.templateFilled = "true";
            }
            question.focus();
            question.select();
        }

        cards.forEach((card) => {
            card.addEventListener("click", () => selectExample(card, true));
            if (card.getAttribute("aria-pressed") === "true") {
                selectExample(card, false);
            }
        });

        question.addEventListener("input", () => {
            question.dataset.templateFilled = "false";
        });
    }

    document.addEventListener("DOMContentLoaded", initialise);
}());
