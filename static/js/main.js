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

// Toggle visibility of CSRF tokens for users who want to inspect them manually.
const initTokenToggles = () => {
  const toggleButtons = document.querySelectorAll("[data-token-toggle]");
  toggleButtons.forEach((button) => {
    const container = button.closest("[data-token-container]");
    const valueElement = container?.querySelector("[data-token-value]");
    if (!container || !valueElement) {
      return;
    }

    button.addEventListener("click", () => {
      const isHidden = valueElement.hasAttribute("hidden");
      if (isHidden) {
        valueElement.removeAttribute("hidden");
        button.textContent = "Hide CSRF token";
        return;
      }
      valueElement.setAttribute("hidden", "");
      button.textContent = "Show CSRF token";
    });
  });
};

document.addEventListener("DOMContentLoaded", () => {
  initConfirmDialogs();
  initTokenToggles();
});
