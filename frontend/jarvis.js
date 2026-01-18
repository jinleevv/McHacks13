document.addEventListener("DOMContentLoaded", () => {
  const { ipcRenderer } = require("electron");

  // Only the lower-right UI should capture clicks; elsewhere clicks pass through.
  const interactiveEls = [
    document.getElementById("slide-container"),
    document.getElementById("mainBtn"),
    document.getElementById("actionBtns"),
  ];

  function setIgnore(ignore) {
    ipcRenderer.send("set-ignore-mouse-events", ignore);
  }

  function bindHover(el) {
    if (!el) return;
    el.addEventListener("pointerenter", () => setIgnore(false));
    el.addEventListener("pointerleave", () => setIgnore(true));
  }

  interactiveEls.forEach(bindHover);

  // Start with background-clickable by default
  setIgnore(true);

  // Re-enforce alwaysOnTop after any click outside UI
  document.addEventListener(
    "click",
    (e) => {
      const isUIElement = interactiveEls.some(
        (el) => el && el.contains(e.target),
      );
      if (!isUIElement) {
        ipcRenderer.send("restore-on-top");
      }
    },
    true,
  );

  const slides = document.querySelectorAll(".slide");
  const nextBtn = document.getElementById("nextBtn");
  const skipBtn = document.getElementById("skipBtn");

  let currentSlide = 0;

  function showSlide(index) {
    slides.forEach((slide, i) => {
      slide.classList.remove("active", "exit-left");

      if (i < index) {
        slide.classList.add("exit-left");
      } else if (i === index) {
        slide.classList.add("active");
      }
    });
  }

  function nextSlide() {
    currentSlide++;
    if (currentSlide >= slides.length) {
      currentSlide = slides.length - 1;
      updateButtonForLastSlide();
      return;
    }
    updateButtonForLastSlide();
    showSlide(currentSlide);
  }

  function updateButtonForLastSlide() {
    if (currentSlide === slides.length - 1) {
      nextBtn.textContent = "Start";
    } else {
      nextBtn.textContent = "Next";
    }
  }

  function closeIntro() {
    const introContainer = document.getElementById("slide-container");
    if (introContainer) {
      introContainer.style.display = "none";

      console.log("Intro closed, Jarvis remains active.");
    }
  }

  function openIntro() {
    currentSlide = 0;
    updateButtonForLastSlide();
    showSlide(currentSlide);
    const introContainer = document.getElementById("slide-container");
    if (introContainer) {
      introContainer.style.display = "flex";
    }
  }

  nextBtn?.addEventListener("click", () => {
    if (currentSlide === slides.length - 1) {
      closeIntro();
    } else {
      nextSlide();
    }
  });
  skipBtn?.addEventListener("click", closeIntro);

  const mainBtn = document.getElementById("mainBtn");
  const actionBtns = document.getElementById("actionBtns");

  let menuOpen = false;

  function toggleMenu() {
    menuOpen = !menuOpen;

    if (menuOpen) {
      actionBtns.classList.add("show");
      mainBtn.textContent = "×";
    } else {
      actionBtns.classList.remove("show");
      mainBtn.textContent = "+";
    }
  }

  mainBtn?.addEventListener("click", toggleMenu);

  const actions = {
    create: () => {
      console.log("Add mode activated");
      openIntro();
    },

    manage: () => {
      console.log("Manage mode activated");
      openIntro();
    },

    info: () => {
      console.log("Info panel opened");
      openIntro();
    },
  };

  const customBtn = document.getElementById("customBtn");
  const mngBtn = document.getElementById("mngBtn");
  const infoBtn = document.getElementById("infoBtn");
  const exitBtn = document.getElementById("exitBtn");

  customBtn?.addEventListener("click", () => {
    actions.create();
    toggleMenu();
  });

  mngBtn?.addEventListener("click", () => {
    actions.manage();
    toggleMenu();
  });

  infoBtn?.addEventListener("click", () => {
    actions.info();
    toggleMenu();
  });

  exitBtn?.addEventListener("click", () => {
    window.close();
  });

  document.addEventListener("keydown", (e) => {
    switch (e.key) {
      case "ArrowRight":
        nextSlide();
        break;

      case "Escape":
        closeIntro();
        break;

      case "c":
        actions.create();
        break;

      case "m":
        actions.manage();
        break;

      case "i":
        actions.info();
        break;
    }
  });

  console.log("UI Controller Loaded");
});
