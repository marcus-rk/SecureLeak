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
    const button = container.querySelector("[data-token-toggle]");
    const valueElement = container.querySelector("[data-token-value]");
    const includeCheckbox = container.querySelector("[data-token-include]");
    const form = container.closest("form");
    const hiddenInput = form?.querySelector("input[name='csrf_token'][data-token-input]");
    if (!button || !valueElement || !form || !hiddenInput) {
      return;
    }

    // Show/hide the token value only (for learning/inspection)
    button.addEventListener("click", () => {
      const isHidden = valueElement.hasAttribute("hidden");
      if (isHidden) {
        valueElement.removeAttribute("hidden");
        button.textContent = "Hide CSRF token";
      } else {
        valueElement.setAttribute("hidden", "");
        button.textContent = "Show CSRF token";
      }
    });

    // Include/exclude the CSRF token in the form submission by toggling disabled
    if (includeCheckbox) {
      includeCheckbox.addEventListener("change", () => {
        const include = includeCheckbox.checked;
        if (include) {
          hiddenInput.removeAttribute("disabled");
        } else {
          hiddenInput.setAttribute("disabled", "");
        }
      });
    }
  });
};

document.addEventListener("DOMContentLoaded", () => {
  initConfirmDialogs();
  initTokenToggles();
});
