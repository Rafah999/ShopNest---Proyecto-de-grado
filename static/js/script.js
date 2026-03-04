document.addEventListener("DOMContentLoaded", function() {
    const userCircle = document.getElementById("userCircle");
    const userDropdown = document.getElementById("userDropdown");

    userCircle.addEventListener("click", function(event) {
        event.stopPropagation(); // Evita que se cierre inmediatamente
        userDropdown.classList.toggle("active");
    });

    // Cerrar si hago click fuera
    document.addEventListener("click", function() {
        userDropdown.classList.remove("active");
    });
});
