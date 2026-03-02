function initTheme() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        document.body.classList.add('light-mode');
    }
}

function toggleTheme() {
    const isLight = document.body.classList.toggle('light-mode');
    localStorage.setItem('theme', isLight ? 'light' : 'dark');

    // Update all theme toggle buttons
    const btns = document.querySelectorAll('.theme-toggle');
    btns.forEach(btn => {
        btn.innerHTML = isLight ? '🌙' : '☀️';
        btn.title = isLight ? 'Passer au thème sombre' : 'Passer au thème clair';
    });
}

// Update icons on load
document.addEventListener('DOMContentLoaded', () => {
    const isLight = document.body.classList.contains('light-mode');
    const btns = document.querySelectorAll('.theme-toggle');
    btns.forEach(btn => {
        btn.innerHTML = isLight ? '🌙' : '☀️';
        btn.title = isLight ? 'Passer au thème sombre' : 'Passer au thème clair';
    });
});

// Execute immediately to prevent flash of unstyled content
initTheme();
