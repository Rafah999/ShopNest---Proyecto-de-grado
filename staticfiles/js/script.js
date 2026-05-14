document.addEventListener("DOMContentLoaded", function () {

    console.log("JS funcionando");

    // =========================
    // DRAWER USUARIO
    // =========================
    const openBtn = document.getElementById("openDrawer");
    const drawer = document.getElementById("drawer");
    const closeBtn = document.getElementById("closeDrawer");
    const overlay = document.getElementById("drawerOverlay");

    if (openBtn && drawer && overlay) {
        openBtn.addEventListener("click", () => {
            drawer.classList.add("active");
            overlay.classList.add("active");
        });
    }

    if (closeBtn && drawer && overlay) {
        closeBtn.addEventListener("click", () => {
            drawer.classList.remove("active");
            overlay.classList.remove("active");
        });
    }

    if (overlay && drawer) {
        overlay.addEventListener("click", () => {
            drawer.classList.remove("active");
            overlay.classList.remove("active");
        });
    }

    // =========================
    // CARRUSEL LOGIN / REGISTRO
    // =========================
    const slides = document.querySelectorAll(".slide");

    if (slides.length > 0) {

        let index = 0;

        slides[0].classList.add("active");

        setInterval(() => {

            slides[index].classList.remove("active");

            index = (index + 1) % slides.length;

            slides[index].classList.add("active");

        }, 4000);
    }

    // =========================
    // NOTIFICACIONES
    // =========================
    const openDrawerNoti = document.getElementById("openNotiDrawer");
    const modal = document.getElementById("notiModal");
    const closeNoti = document.getElementById("closeNoti");
    const notiList = document.getElementById("notiList");
    const notiCount = document.getElementById("notiCount");

    function cargarNotificaciones() {

        fetch("/api/notificaciones/")
            .then(response => response.json())
            .then(data => {

                if (notiCount) {

                    const noLeidas = data.filter(
                        n => n.estado === "no_leido"
                    ).length;

                    notiCount.innerText = noLeidas;

                    if (noLeidas === 0) {
                        notiCount.style.display = "none";
                    } else {
                        notiCount.style.display = "flex";
                    }
                }

                if (notiList) {

                    if (data.length === 0) {

                        notiList.innerHTML =
                            "<p>No tienes notificaciones.</p>";

                    } else {

                        notiList.innerHTML = "";

                        data.forEach(n => {

                            notiList.innerHTML += `
                                <div class="noti-item ${n.estado}">
                                    <p>${n.mensaje}</p>
                                    <small>${n.fecha}</small>
                                </div>
                            `;
                        });
                    }
                }
            })
            .catch(error => {
                console.error(
                    "Error cargando notificaciones:",
                    error
                );
            });
    }

    function abrirModalNoti() {

        if (modal) {

            modal.classList.add("active");

            fetch("/api/notificaciones/marcar/")
                .then(() => {
                    cargarNotificaciones();
                });
        }
    }

    if (openDrawerNoti) {
        openDrawerNoti.addEventListener(
            "click",
            abrirModalNoti
        );
    }

    if (closeNoti && modal) {

        closeNoti.addEventListener("click", () => {
            modal.classList.remove("active");
        });
    }

    if (modal) {

        modal.addEventListener("click", function (e) {

            if (e.target === modal) {
                modal.classList.remove("active");
            }
        });
    }

    if (openDrawerNoti) {

        cargarNotificaciones();

        setInterval(cargarNotificaciones, 5000);
    }

    // =========================
    // AYUDA EMPRENDIMIENTO
    // =========================
    const openAyuda = document.getElementById("openAyuda");
    const ayudaModal = document.getElementById("ayudaModal");
    const closeAyuda = document.getElementById("closeAyuda");

    if (openAyuda && ayudaModal) {

        openAyuda.addEventListener("click", () => {
            ayudaModal.classList.add("active");
        });
    }

    if (closeAyuda && ayudaModal) {

        closeAyuda.addEventListener("click", () => {
            ayudaModal.classList.remove("active");
        });
    }

    if (ayudaModal) {

        ayudaModal.addEventListener("click", function (e) {

            if (e.target === ayudaModal) {
                ayudaModal.classList.remove("active");
            }
        });
    }

    // =========================
    // TUTORIAL GUIADO
    // =========================

    const tutorialOverlay =
        document.getElementById("tutorialOverlay");

    const tutorialTooltip =
        document.getElementById("tutorialTooltip");

    const tutorialText =
        document.getElementById("tutorialText");

    const nextTutorial =
        document.getElementById("nextTutorial");

    const openTutorialManual =
        document.getElementById("openTutorialManual");

    const pasos = [
        {
            element: document.getElementById("stepInfo"),
            texto:
                "Primero revisa la información base de tu emprendimiento."
        },
        {
            element: document.getElementById("stepLogo"),
            texto:
                "Aquí debes subir o cambiar el logo principal de tu negocio."
        },
        {
            element: document.getElementById("stepCarrusel"),
            texto:
                "En esta sección debes agregar hasta 5 imágenes para tu carrusel."
        },
        {
            element: document.getElementById("stepProductos"),
            texto:
                "Aquí registra mínimo 3 productos para que tu tienda pueda publicarse."
        },
        {
            element: document.getElementById("stepPublicar"),
            texto:
                "Cuando completes todo, desde aquí podrás publicar tu emprendimiento."
        }
    ];

    let pasoActual = 0;

    // =========================
    // LIMPIAR
    // =========================
    function limpiarTutorial() {

        document
            .querySelectorAll(".tutorial-step")
            .forEach(el => {
                el.classList.remove(
                    "tutorial-highlight"
                );
            });
    }

    // =========================
    // POSICIONAR TOOLTIP
    // =========================
    function posicionarTooltip(elemento) {

        if (!tutorialTooltip || !elemento) return;

        const rect = elemento.getBoundingClientRect();

        const tooltipHeight =
            tutorialTooltip.offsetHeight;

        const tooltipWidth =
            tutorialTooltip.offsetWidth;

        // POSICIÓN ARRIBA DEL ELEMENTO
        let top =
            rect.top - tooltipHeight - 20;

        let left =
            rect.left + (
                rect.width / 2
            ) - (
                tooltipWidth / 2
            );

        // si no cabe arriba -> abajo
        if (top < 20) {

            top = rect.bottom + 20;
        }

        // limitar izquierda
        if (left < 20) {
            left = 20;
        }

        // limitar derecha
        if (
            left + tooltipWidth >
            window.innerWidth - 20
        ) {

            left =
                window.innerWidth -
                tooltipWidth -
                20;
        }

        tutorialTooltip.style.top =
            `${top}px`;

        tutorialTooltip.style.left =
            `${left}px`;
    }

    // =========================
    // MOSTRAR PASO
    // =========================
    function mostrarPaso(index) {

        const paso = pasos[index];

        if (!paso || !paso.element) return;

        limpiarTutorial();

        paso.element.classList.add(
            "tutorial-highlight"
        );

        tutorialText.innerText =
            paso.texto;

        // HACER SCROLL HASTA EL ELEMENTO
        paso.element.scrollIntoView({
            behavior: "smooth",
            block: "center"
        });

        // ESPERAR QUE TERMINE EL SCROLL
        setTimeout(() => {

            posicionarTooltip(
                paso.element
            );

        }, 600);
    }

    // =========================
    // INICIAR TUTORIAL
    // =========================
    function iniciarTutorial() {

        if (
            !tutorialOverlay ||
            !tutorialTooltip ||
            !tutorialText ||
            !nextTutorial
        ) {
            return;
        }

        pasoActual = 0;

        tutorialOverlay.classList.add(
            "active"
        );

        setTimeout(() => {

            mostrarPaso(0);

        }, 300);
    }

    // =========================
    // BOTÓN VER TUTORIAL
    // =========================
    if (openTutorialManual) {

        openTutorialManual.addEventListener(
            "click",
            () => {

                if (ayudaModal) {

                    ayudaModal.classList.remove(
                        "active"
                    );
                }

                iniciarTutorial();
            }
        );
    }

    // =========================
    // AUTO INICIO
    // =========================
    if (
        tutorialOverlay &&
        tutorialTooltip &&
        tutorialText &&
        nextTutorial
    ) {

        if (
            tutorialOverlay.classList.contains(
                "active"
            )
        ) {

            setTimeout(() => {

                iniciarTutorial();

            }, 300);
        }

        // SIGUIENTE
        nextTutorial.addEventListener(
            "click",
            () => {

                pasoActual++;

                if (
                    pasoActual <
                    pasos.length
                ) {

                    mostrarPaso(
                        pasoActual
                    );

                } else {

                    tutorialOverlay.classList.remove(
                        "active"
                    );

                    limpiarTutorial();
                }
            }
        );

        // REPOSICIONAR EN RESIZE
        window.addEventListener(
            "resize",
            () => {

                if (
                    tutorialOverlay.classList.contains(
                        "active"
                    )
                ) {

                    posicionarTooltip(
                        pasos[pasoActual].element
                    );
                }
            }
        );
    }

});