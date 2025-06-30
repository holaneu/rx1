const hamburger = document.getElementById('hamburger');
const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('overlay');
const mainContent = document.querySelector('.main-content');

function adjustSidebar() {
    const windowWidth = window.innerWidth;
    const contentMax = 800;
    const sidebarWidth = 230;
    if (windowWidth >= contentMax + sidebarWidth + 20) {
    sidebar.classList.add('active');
    overlay.classList.remove('active');
    mainContent.style.transform = "translateX(115px)";
    } else {
    sidebar.classList.remove('active');
    overlay.classList.remove('active');
    mainContent.style.transform = "translateX(0)";
    }
}



hamburger.addEventListener('click', () => {
    const windowWidth = window.innerWidth;
    const isActive = sidebar.classList.contains('active');
    if (!isActive) {
    sidebar.classList.add('active');
    if (windowWidth < 1024) {
        overlay.classList.add('active');
    } else {
        mainContent.style.transform = "translateX(115px)";
    }
    } else {
    sidebar.classList.remove('active');
    overlay.classList.remove('active');
    mainContent.style.transform = "translateX(0)";
    }
});

overlay.addEventListener('click', () => {
    sidebar.classList.remove('active');
    overlay.classList.remove('active');
});

window.addEventListener('resize', adjustSidebar);
window.addEventListener('DOMContentLoaded', adjustSidebar);