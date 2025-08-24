const loader = document.getElementById("loader");
function showLoader() { loader.classList.remove("hidden"); }
function hideLoader() { loader.classList.add("hidden"); }
function celebrate() {
  if (window.confetti) {
    confetti({ spread: 60, origin: { y: 0.6 } });
  }
}

// Single ticket classification
document.getElementById("classifyBtn").addEventListener("click", async () => {
  const text = document.getElementById("ticketText").value.trim();
  if (!text) return;

  const resEl = document.getElementById("result");
  resEl.classList.add("hidden");
  showLoader();
  try {
    const response = await fetch("/classify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });
    if (!response.ok) throw new Error(await response.text());
    const data = await response.json();

    document.getElementById("category").textContent = data.category;
    document.getElementById("team").textContent = data.assigned_team;
    resEl.classList.remove("hidden");
    celebrate();
  } catch (err) {
    alert("Error: " + err.message);
  }
  hideLoader();
});

// Bulk CSV classification
document.getElementById("classifyFileBtn").addEventListener("click", async () => {
  const input = document.getElementById("fileInput");
  if (!input.files.length) {
    alert("Please select a CSV file containing tickets.");
    return;
  }
  const file = input.files[0];
  const formData = new FormData();
  formData.append("file", file);

  const fileResEl = document.getElementById("fileResult");
  fileResEl.classList.add("hidden");
  showLoader();
  try {
    const response = await fetch("/classify_file", {
      method: "POST",
      body: formData
    });
    if (!response.ok) throw new Error(await response.text());
    const data = await response.json();
    fileResEl.textContent = JSON.stringify(data, null, 2);
    fileResEl.classList.remove("hidden");
    celebrate();
  } catch (err) {
    alert("Error: " + err.message);
  }
  hideLoader();
});

// Added dark-mode toggle handling at top
const themeToggle = document.getElementById("themeToggle");
const root = document.documentElement;
const savedTheme = localStorage.getItem("theme");
if (savedTheme === "dark") root.setAttribute("data-theme", "dark");
updateToggleIcon();

themeToggle.addEventListener("click", () => {
  const isDark = root.getAttribute("data-theme") === "dark";
  root.setAttribute("data-theme", isDark ? "light" : "dark");
  localStorage.setItem("theme", isDark ? "light" : "dark");
  updateToggleIcon();
});
function updateToggleIcon(){
  themeToggle.textContent = root.getAttribute("data-theme") === "dark" ? "☀️" : "🌙";
}