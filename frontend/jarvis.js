document.addEventListener("DOMContentLoaded", () => {
  const { ipcRenderer } = require("electron");

  const slides = document.querySelectorAll(".slide");
  const nextBtn = document.getElementById("nextBtn");
  const prevBtn = document.getElementById("prevBtn");
  // const voiceBtn = document.getElementById("voice");
  // const voiceIcon = document.querySelector(".voice img");

  // let listening = false;

  // voiceBtn?.addEventListener("click", () => {
  //   listening = !listening;

  //   if (listening) {
  //     voiceBtn.classList.add("active");
  //     voiceIcon.src = "./icons/pause.png";
  //   } else {
  //     voiceBtn.classList.remove("active");
  //     voiceIcon.src = "./icons/mic.png";
  //   }
  // });

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
    if (currentSlide < slides.length - 1) {
      currentSlide++;
      updateButtonForLastSlide();
      showSlide(currentSlide);
    }
  }

  function previousSlide() {
    if (currentSlide > 0) {
      currentSlide--;
      updateButtonForLastSlide();
      showSlide(currentSlide);
    }
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
      // Reset button text when intro closes
      nextBtn.textContent = "Next";
      currentSlide = 0;
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
    // Close action buttons when opening intro
    if (menuOpen) {
      menuOpen = false;
      actionBtns.classList.remove("show");
      mainBtn.textContent = "+";
    }
  }

  nextBtn?.addEventListener("click", () => {
    if (currentSlide === slides.length - 1) {
      closeIntro();
    } else {
      nextSlide();
    }
  });
  prevBtn?.addEventListener("click", previousSlide);

  const mainBtn = document.getElementById("mainBtn");
  const actionBtns = document.getElementById("actionBtns");

  let menuOpen = false;

  function toggleMenu() {
    menuOpen = !menuOpen;

    if (menuOpen) {
      actionBtns.classList.add("show");
      mainBtn.textContent = "×";
      // Close intro when opening action buttons
      closeIntro();
    } else {
      actionBtns.classList.remove("show");
      mainBtn.textContent = "+";
    }
  }

  mainBtn?.addEventListener("click", toggleMenu);

  const actions = {
    // manage: () => {
    //   console.log("Manage mode activated");
    //   openIntro();
    // },

    info: () => {
      console.log("Info panel opened");
      openIntro();
    },
  };

  // const mngBtn = document.getElementById("mngBtn");
  const infoBtn = document.getElementById("infoBtn");
  const exitBtn = document.getElementById("exitBtn");

  // mngBtn?.addEventListener("click", () => {
  //   actions.manage();
  //   toggleMenu();
  // });

  infoBtn?.addEventListener("click", () => {
    actions.info();
  });

  exitBtn?.addEventListener("click", () => {
    const { ipcRenderer } = require("electron");
    ipcRenderer.send("quit-app");
  });

  document.addEventListener("keydown", (e) => {
    switch (e.key) {
      case "ArrowRight":
        nextSlide();
        break;

      case "Escape":
        closeIntro();
        break;

      // case "c":
      //   actions.create();
      //   break;

      // case "m":
      //   actions.manage();
      //   break;

      case "i":
        actions.info();
        break;
    }
  });

  console.log("UI Controller Loaded");
});
