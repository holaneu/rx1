function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('open');
}

// Header background change on scroll ---
window.addEventListener('scroll', () => {
  // Check if user has scrolled down more than a small threshold (e.g., 50px)
  if (window.scrollY > 50) {
      header.classList.add('scrolled');
  } else {
      header.classList.remove('scrolled');
  }
});
