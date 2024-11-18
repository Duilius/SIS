// static/js/app.js
// Solo funciones esenciales que no se pueden manejar con HTMX/Hyperscript

// Persistencia de usuario
document.addEventListener('htmx:afterRequest', function(evt) {
    if (evt.detail.path === '/api/login' && evt.detail.successful) {
        const response = JSON.parse(evt.detail.xhr.response);
        localStorage.setItem('user', JSON.stringify(response.user));
    }
});

// Cerrar modal al hacer clic fuera
document.addEventListener('click', function(evt) {
    if (evt.target.matches('.modal')) {
        evt.target.remove();
    }
});

// Formateo de números
function formatNumber(num) {
    return new Intl.NumberFormat('es-PE').format(num);
}

function toggleTheme() {
    document.body.classList.toggle('dark-mode');
    const isDark = document.body.classList.contains('dark-mode');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
}

// Al cargar la página
document.addEventListener('DOMContentLoaded', () => {
    if (localStorage.getItem('theme') === 'dark') {
        document.body.classList.add('dark-mode');
    }
});

// Intercept