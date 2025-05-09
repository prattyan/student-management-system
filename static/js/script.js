// script.js

// Example: Show a confirmation dialog before deleting a student
function confirmDelete(studentName) {
    return confirm(`Are you sure you want to delete ${studentName}?`);
}

// Example: Auto-hide flash messages after 3 seconds
setTimeout(() => {
    let alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        alert.style.display = 'none';
    });
}, 3000);
const darkModeToggle = document.getElementById('darkModeToggle');

darkModeToggle.addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
    const darkMode = document.body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', darkMode ? 'enabled' : 'disabled');
});

// Set initial mode based on localStorage
if (localStorage.getItem('darkMode') === 'enabled') {
    document.body.classList.add('dark-mode');
}
document.getElementById('darkModeToggle').addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
    const darkMode = document.body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', darkMode ? 'enabled' : 'disabled');
});

if (localStorage.getItem('darkMode') === 'enabled') {
    document.body.classList.add('dark-mode');
}
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    const darkMode = document.body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', darkMode ? 'enabled' : 'disabled');
}
document.getElementById('darkModeToggle').addEventListener('click', toggleDarkMode);    