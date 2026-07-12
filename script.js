const modules = {
  classical: {
    title: "Classical Mechanics",
    description: "Simulate motion, forces, energy, collisions, and gravity with intuitive visual tools.",
    url: "classical-mechanics.html",
  },
  quantum: {
    title: "Quantum Mechanics",
    description: "Explore probability clouds, energy levels, wave functions, and quantum states.",
    url: "quantum-mechanics.html",
  },
  relativistic: {
    title: "Relativistic Mechanics",
    description: "Visualize time dilation, length contraction, and motion near the speed of light.",
    url: "relativistic-mechanics.html",
  },
  statistical: {
    title: "Statistical Mechanics",
    description: "Study ensembles, entropy, temperature, and particle distributions.",
    url: "statistical-mechanics.html",
  },
};

const previewText = document.getElementById("previewText");
const launchButton = document.getElementById("launchButton");
let selectedModule = null;

function updatePreview(moduleKey) {
  selectedModule = modules[moduleKey];
  previewText.textContent = selectedModule.description;
  launchButton.disabled = false;
  launchButton.textContent = `Launch ${selectedModule.title}`;
}

function resetPreview() {
  selectedModule = null;
  previewText.textContent = "Select a module to see its description and launch it.";
  launchButton.disabled = true;
  launchButton.textContent = "Launch module";
}

const cards = document.querySelectorAll(".module-card");
cards.forEach((card) => {
  card.addEventListener("click", () => {
    const moduleKey = card.dataset.module;
    updatePreview(moduleKey);
    cards.forEach((other) => other.classList.remove("active"));
    card.classList.add("active");
  });
});

launchButton.addEventListener("click", () => {
  if (!selectedModule) {
    return;
  }
  window.location.href = selectedModule.url;
});

resetPreview();
