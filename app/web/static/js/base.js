
// Sidebar
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

// Mobile navigation toggle (right hamburger menu)
document.addEventListener('DOMContentLoaded', function() {
    const hamburger = document.getElementById('hamburger');
    const navMain = document.querySelector('.nav-main');
    const overlay = document.getElementById('mobile-nav-overlay');

    hamburger.addEventListener('click', function() {
        navMain.classList.toggle('active');
        overlay.classList.toggle('active');
    });

    overlay.addEventListener('click', function() {
        navMain.classList.remove('active');
        overlay.classList.remove('active');
    });
});
