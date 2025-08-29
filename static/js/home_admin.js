//! Navbar and Content Navigation

const navItems = document.querySelectorAll(".nav-item");
const navLinks = document.querySelectorAll(".nav-link");
const initialPresentation = document.getElementById("initial-presentation");
const dynamicContent = document.getElementById("dynamic-content");

// Handle navigation clicks
navLinks.forEach((navLink) => {
  navLink.addEventListener("click", (e) => {
    // Remove active class from all nav items
    navItems.forEach((item) => {
      item.className = "nav-item";
    });
    
    // Add active class to clicked nav item
    const navItem = navLink.closest(".nav-item");
    navItem.className = "nav-item active";
    
    // Hide initial presentation and show dynamic content
    if (initialPresentation && dynamicContent) {
      initialPresentation.style.display = "none";
      dynamicContent.style.display = "block";
      
      // Add fade animation
      initialPresentation.style.animation = "fadeOut 0.3s ease-in-out";
      dynamicContent.style.animation = "fadeIn 0.5s ease-in-out";
    }
    
    // Get the section data attribute
    const section = navLink.getAttribute("data-section");
    
    // Allow normal navigation to proceed
    // The page will reload and show the actual content
    console.log("Navigating to section:", section);
  });
});

// Handle feature card clicks (optional - for better UX)
const featureCards = document.querySelectorAll(".feature-card");
featureCards.forEach((card) => {
  card.addEventListener("click", () => {
    // Find corresponding nav link and trigger click
    const cardTitle = card.querySelector("h3").textContent.toLowerCase();
    const correspondingLink = Array.from(navLinks).find(link => {
      const linkText = link.querySelector(".nav-text").textContent.toLowerCase();
      return linkText.includes(cardTitle) || cardTitle.includes(linkText);
    });
    
    if (correspondingLink) {
      correspondingLink.click();
    }
  });
});

//! Light/Dark Mode

const moonIcon = document.querySelector(".moon");
const sunIcon = document.querySelector(".sun");
const nightImage = document.querySelector(".night-img");
const morningImage = document.querySelector(".morning-img");
const toggle = document.querySelector(".toggle");

function switchTheme() {
  document.body.classList.toggle("darkmode");
  if (document.body.classList.contains("darkmode")) {
    sunIcon.classList.remove("hidden");
    moonIcon.classList.add("hidden");
    morningImage.classList.add("hidden");
    nightImage.classList.remove("hidden");
  } else {
    sunIcon.classList.add("hidden");
    moonIcon.classList.remove("hidden");
    morningImage.classList.remove("hidden");
    nightImage.classList.add("hidden");
  }
}

//! Share Button Popup

const sharebtns = document.querySelectorAll(".share-btn");

sharebtns.forEach((btn) => {
  btn.addEventListener("click", (event) => {
    const popup = btn.closest(".event-footer").querySelector(".popup");

    btn.classList.toggle("active");
    popup.classList.toggle("active");

    event.stopPropagation();
  });
});

document.addEventListener("click", (event) => {
  const popups = document.querySelectorAll(".popup");

  popups.forEach((popup) => {
    if (popup.classList.contains("active") && !popup.contains(event.target)) {
      popup.classList.remove("active");

      const shareBtn = popup
        .closest(".event-footer")
        .querySelector(".share-btn");
      shareBtn.classList.remove("active");
    }
  });
});

//! Like Buttons

const likeBtns = document.querySelectorAll(".like-btn");

likeBtns.forEach((likeBtn) => {
  likeBtn.addEventListener("click", () => {
    if (likeBtn.classList.contains("bxs-heart")) {
      likeBtn.classList.remove("bxs-heart");
      likeBtn.classList.add("bx-heart");
      likeBtn.classList.remove("bounce-in");
    } else {
      likeBtn.classList.add("bxs-heart");
      likeBtn.classList.remove("bx-heart");
      likeBtn.classList.add("bounce-in");
    }
  });
});

//! Chart JS

const chartData = {
  labels: ["Workshop", "Theater", "Concert", "Sport"],
  data: [40, 15, 25, 20],
};

const chart = document.getElementById("doughnut");
const eventList = document.querySelector(".chart ul");

new Chart(chart, {
  type: "doughnut",
  data: {
    labels: ["Workshop", "Theater", "Concert", "Sport"],
    datasets: [
      {
        label: "# of Events",
        data: [8, 3, 5, 4],
        backgroundColor: ["#582bac", "#b31a4d", "#e48e2c", "#4a920f"],
        offset: 10,
        hoverOffset: 8,
        hoverBorderColor: "#9a999b",
        borderWidth: 1,
      },
    ],
  },
  options: {
    responsive: true,
    plugins: {
      legend: {
        display: true,
        labels: {
          color: "#8b8a96",
          font: {
            size: 12,
            weight: 600,
          },
        },
      },
    },
    layout: {
      padding: {
        bottom: 10,
      },
    },
  },
});

function population() {
  chartData.labels.forEach((label, i) => {
    let eachEvent = document.createElement("li");
    eachEvent.innerHTML = `${label}: <span class="percentage">${chartData.data[i]}%</span> `;
    eventList.appendChild(eachEvent);
  });
}

population();
