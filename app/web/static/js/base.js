const hamburger = document.getElementById('hamburger');
const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('overlay');
const mainContent = document.querySelector('.main-content');

const sidebarLsKey = 'sidebarActivated';
const isSidebarAllowed = function(){
    return (localStorage.getItem(sidebarLsKey) || 'true') === 'true';
}



function openSidebar() {
  sidebar.classList.add('active');  
  if (window.innerWidth < 1024) {    
    overlay.classList.add('active');
    mainContent.style.transform = "translateX(0)";
  } else {
    overlay.classList.remove('active');
    mainContent.style.transform = "translateX(115px)";
  }
}

function closeSidebar() {  
  sidebar.classList.remove('active');
  overlay.classList.remove('active');
  mainContent.style.transform = "translateX(0)";
}

function setInitialSidebarState() {
  const windowWidth = window.innerWidth;
  const contentMax = 800;
  const sidebarWidth = 230;
  if (windowWidth >= contentMax + sidebarWidth + 20 && isSidebarAllowed() ) {
    openSidebar(); // no transition yet
  } else {
    closeSidebar(); // no transition yet
  }
}

window.addEventListener('DOMContentLoaded', () => {
  setInitialSidebarState();
  requestAnimationFrame(() => {
    document.body.classList.add('transition-enabled');
  });
});

window.addEventListener('resize', () => {
  const windowWidth = window.innerWidth;
  console.log('Window resized to:', windowWidth, '\nSidebar allowed:', isSidebarAllowed() );
  if (isSidebarAllowed() ) {
    if (windowWidth >= 1024) {
        openSidebar();
    } else {
        closeSidebar();
    }
 }
});

hamburger.addEventListener('click', () => {
  const windowWidth = window.innerWidth;
  if (sidebar.classList.contains('active')) {
    closeSidebar();
    if (windowWidth >= 1024) {
        localStorage.setItem(sidebarLsKey, 'false');
    }
  } else {
    openSidebar();
    if (windowWidth >= 1024) {
        localStorage.setItem(sidebarLsKey, 'true');
    }
  }
});

overlay.addEventListener('click', () => {
  closeSidebar();
});
