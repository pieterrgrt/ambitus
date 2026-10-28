// Small progressive enhancements; every page also works without this file.
document.addEventListener("DOMContentLoaded", () => {
  // AI requests take a while: show that something is happening and stop double submits.
  document.querySelectorAll("button[data-busy]").forEach((button) => {
    button.form?.addEventListener("submit", () => {
      button.disabled = true;
      button.classList.add("busy");
      button.textContent = button.dataset.busy;
    });
  });

  document.querySelectorAll("select[data-autosubmit]").forEach((select) => {
    select.addEventListener("change", () => select.form.submit());
  });

  document.querySelectorAll("[data-copy]").forEach((button) => {
    button.addEventListener("click", async () => {
      const source = document.querySelector(button.dataset.copy);
      const text = source.value ?? source.textContent;
      try {
        await navigator.clipboard.writeText(text);
        const label = button.textContent;
        button.textContent = button.dataset.copied;
        setTimeout(() => (button.textContent = label), 1800);
      } catch {
        if (source.select) source.select();
      }
    });
  });

  document.querySelectorAll("[data-share]").forEach((button) => {
    if (!navigator.share) return;
    button.hidden = false;
    button.addEventListener("click", () => navigator.share({ text: button.dataset.share }).catch(() => {}));
  });
});
