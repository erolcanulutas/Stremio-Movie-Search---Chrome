document.addEventListener("DOMContentLoaded", () => {
  const checkbox = document.getElementById("useStremioApp");
  const saveButton = document.getElementById("save");

  chrome.storage.local.get("useStremioApp", (result) => {
    checkbox.checked = result.useStremioApp || false;
  });

  saveButton.addEventListener("click", () => {
    const useApp = checkbox.checked;
    chrome.storage.local.set({ useStremioApp: useApp }, () => {
      alert("Preferences saved!");
    });
  });
});