// ==========================================
// ISLDetect — Frontend App Logic
// ==========================================
// This file handles:
//  1. Image upload / drag-drop / preview
//  2. Simulated prediction (replace with real model call)
//  3. Result rendering + bar chart
//  4. Classes grid rendering
// ==========================================

// ── CONFIG ────────────────────────────────
// These are your ISL class labels (A–Z + digits or custom).
// UPDATE this list to match your actual model's class_indices.
const CLASS_LABELS = [
  "0","1","2","3","4","5","6","7","8","9",
  "A","B","C","D","E","F","G","H","I","J",
  "K","L","M","N","O","P","Q","R","S","T",
  "U","V","W","X","Y","Z"
];

// ── DOM REFS ──────────────────────────────
const dropZone    = document.getElementById("dropZone");
const fileInput   = document.getElementById("fileInput");
const browseBtn   = document.getElementById("browseBtn");
const uploadInner = document.getElementById("uploadInner");
const previewImg  = document.getElementById("previewImg");
const predictBtn  = document.getElementById("predictBtn");
const resetBtn    = document.getElementById("resetBtn");
const btnText     = document.getElementById("btnText");
const resultDisplay = document.getElementById("resultDisplay");
const resultMeta  = document.getElementById("resultMeta");
const barSection  = document.getElementById("barSection");
const barChart    = document.getElementById("barChart");
const predClass   = document.getElementById("predClass");
const predConf    = document.getElementById("predConf");
const predStatus  = document.getElementById("predStatus");
const statusDot   = document.getElementById("statusDot");
const classesGrid = document.getElementById("classesGrid");

let currentFile = null;

// ── CLASSES GRID ──────────────────────────
function renderClasses() {
  classesGrid.innerHTML = CLASS_LABELS.map(c =>
    `<div class="class-chip">${c}</div>`
  ).join("");
}
renderClasses();

// ── DRAG & DROP ───────────────────────────
dropZone.addEventListener("dragover", e => {
  e.preventDefault();
  dropZone.classList.add("dragover");
});
dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));
dropZone.addEventListener("drop", e => {
  e.preventDefault();
  dropZone.classList.remove("dragover");
  const file = e.dataTransfer.files[0];
  if (file) handleFile(file);
});

dropZone.addEventListener("click", () => {
  if (!previewImg.hidden) return;
  fileInput.click();
});
browseBtn.addEventListener("click", e => {
  e.stopPropagation();
  fileInput.click();
});
fileInput.addEventListener("change", () => {
  if (fileInput.files[0]) handleFile(fileInput.files[0]);
});

// ── FILE HANDLER ──────────────────────────
function handleFile(file) {
  if (!file.type.startsWith("image/")) {
    alert("Please upload a valid image file.");
    return;
  }
  currentFile = file;

  const reader = new FileReader();
  reader.onload = e => {
    previewImg.src = e.target.result;
    previewImg.hidden = false;
    uploadInner.style.display = "none";
    predictBtn.disabled = false;
    resetResult();
  };
  reader.readAsDataURL(file);
}

// ── RESET ─────────────────────────────────
function resetResult() {
  resultDisplay.innerHTML = `
    <div class="result-placeholder">
      <div class="placeholder-ring"></div>
      <p>Awaiting prediction…</p>
    </div>`;
  resultMeta.style.display = "none";
  barSection.style.display = "none";
  statusDot.className = "status-dot";
}

resetBtn.addEventListener("click", () => {
  previewImg.hidden = true;
  previewImg.src = "";
  uploadInner.style.display = "";
  predictBtn.disabled = true;
  currentFile = null;
  fileInput.value = "";
  resetBtn.style.display = "none";
  resetResult();
  resultDisplay.innerHTML = `
    <div class="result-placeholder">
      <div class="placeholder-ring"></div>
      <p>Awaiting image…</p>
    </div>`;
  statusDot.className = "status-dot";
});

// ── PREDICT ───────────────────────────────
predictBtn.addEventListener("click", async () => {
  if (!currentFile) return;

  // UI: loading state
  predictBtn.disabled = true;
  btnText.textContent = "Analysing…";
  statusDot.className = "status-dot loading";
  resultDisplay.innerHTML = `<p class="loading-text">Running inference…</p>`;
  resultMeta.style.display = "none";
  barSection.style.display = "none";

  try {
    const result = await callBackendAPI(currentFile);
    renderResult(result);

  } catch (err) {
    resultDisplay.innerHTML = `<p style="color:#ef4444;font-size:0.85rem;">Error: ${err.message}</p>`;
    statusDot.className = "status-dot";
  } finally {
    predictBtn.disabled = false;
    btnText.textContent = "Predict Sign";
    resetBtn.style.display = "";
  }
});

// ── SIMULATION (replace with real model call) ──
async function simulatePrediction(file) {
  // Fake delay to mimic inference time
  await new Promise(r => setTimeout(r, 1400));

  // Pick a random class as the "winner"
  const topIdx  = Math.floor(Math.random() * CLASS_LABELS.length);
  const topConf = 0.65 + Math.random() * 0.30;

  // Generate fake distribution for top-5
  const others = CLASS_LABELS
    .map((label, i) => ({ label, score: i === topIdx ? topConf : Math.random() * (1 - topConf) / CLASS_LABELS.length }))
    .sort((a, b) => b.score - a.score)
    .slice(0, 5);

  // Normalise to sum ≈ 1
  const total = others.reduce((s, o) => s + o.score, 0);
  others.forEach(o => o.score /= total);

  return {
    predicted: CLASS_LABELS[topIdx],
    confidence: topConf,
    top5: others
  };
}

// ── RENDER RESULT ─────────────────────────
function renderResult(result) {
  const confPct = (result.confidence * 100).toFixed(1);
  const quality = result.confidence > 0.85 ? "High" : result.confidence > 0.65 ? "Medium" : "Low";

  // Big letter display
  resultDisplay.innerHTML = `
    <div class="result-big">
      <div class="big-letter">${result.predicted}</div>
      <div class="big-label">PREDICTED CLASS</div>
    </div>`;

  // Meta row
  predClass.textContent = result.predicted;
  predConf.textContent  = `${confPct}%`;
  predStatus.textContent = quality;
  resultMeta.style.display = "grid";

  // Bar chart (top 5)
  barChart.innerHTML = result.top5.map(item => `
    <div class="bar-row">
      <span class="bar-name">${item.label}</span>
      <div class="bar-track">
        <div class="bar-fill" style="width:0%" data-width="${(item.score*100).toFixed(1)}%"></div>
      </div>
      <span class="bar-pct">${(item.score*100).toFixed(1)}%</span>
    </div>
  `).join("");
  barSection.style.display = "";

  // Animate bars
  requestAnimationFrame(() => {
    document.querySelectorAll(".bar-fill").forEach(bar => {
      bar.style.width = bar.dataset.width;
    });
  });

  statusDot.className = "status-dot active";
}

// ── REAL BACKEND INTEGRATION ──
async function callBackendAPI(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch("http://localhost:5000/predict", {
    method: "POST",
    body: formData
  });

  if (!response.ok) throw new Error(`Server error: ${response.status}`);
  const data = await response.json();
  return data;
}

// ── SCROLL ANIMATIONS ─────────────────────
const observer = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.style.animation = "fadeUp 0.6s ease both";
      observer.unobserve(e.target);
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll(".step-card, .card-section, .about-section, .classes-section")
  .forEach(el => observer.observe(el));