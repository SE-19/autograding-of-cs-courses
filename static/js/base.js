// Getting the hamburger icon toggle button
const hamburger = document.getElementsByClassName("hamburger")[0];
// Getting the navbar-links
const navLinks = document.getElementsByClassName("Navbar-links")[0];
// Setting on click action which opens the navbar
// And runs the animation on hamburger icon
hamburger.addEventListener("click", () => {
  // If the class is not included this includes it and if it is this function removes it
  navLinks.classList.toggle("open");

  hamburger.classList.toggle("toggle");
});
