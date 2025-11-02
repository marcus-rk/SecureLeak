// Bind optional confirmation dialogs to forms that declare a data-confirm message.
const initConfirmDialogs = () => {
  const confirmForms = document.querySelectorAll("form[data-confirm]");
  confirmForms.forEach((form) => {
    form.addEventListener("submit", (event) => {
      const message = form.getAttribute("data-confirm");
      if (message && !window.confirm(message)) {
        event.preventDefault();
      }
    });
  });
};

// Toggle visibility of CSRF tokens and optionally include/exclude them from submission.
const initTokenToggles = () => {
  const containers = document.querySelectorAll("[data-token-container]");
  containers.forEach((container) => {
    const valueElement = container.querySelector("[data-token-value]");
    const form = container.closest("form");
    const hiddenInput = form?.querySelector("input[name='csrf_token'][data-token-input]");
    if (!valueElement || !form || !hiddenInput) {
      return;
    }

    const visibilityToggle = container.querySelector("[data-token-visibility-toggle]");
    const includeToggle = container.querySelector("[data-token-include-toggle]");

    const applyVisibility = () => {
      if (visibilityToggle?.checked) {
        valueElement.removeAttribute("hidden");
      } else {
        valueElement.setAttribute("hidden", "");
      }
    };

    const applyInclusion = () => {
      if (includeToggle?.checked) {
        hiddenInput.removeAttribute("disabled");
      } else {
        hiddenInput.setAttribute("disabled", "");
      }
    };

    visibilityToggle?.addEventListener("change", applyVisibility);
    includeToggle?.addEventListener("change", applyInclusion);

    // Initialize state once
    applyVisibility();
    applyInclusion();
  });
};

document.addEventListener("DOMContentLoaded", () => {
  initConfirmDialogs();
  initTokenToggles();
});
