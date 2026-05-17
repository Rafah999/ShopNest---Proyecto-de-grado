// =========================
// VARIABLES GLOBALES
// =========================

const productoModal = document.getElementById("productoModal");
const productoForm = document.getElementById("productoForm");
const productoModalTitle = document.getElementById("productoModalTitle");
const openProductoModal = document.getElementById("openProductoModal");

let currentSlide = 0;
let imagenesParaEliminar = [];
let elementoPendienteEliminar = null;
let imagenesPreviewTemporales = [];

// =========================
// CSRF TOKEN
// =========================

function getCSRFToken() {
    const token = document.querySelector(
        '[name="csrfmiddlewaretoken"]'
    );

    return token ? token.value : "";
}

// =========================
// PREVIEW PRODUCTO
// =========================

function previewProducto(event) {
    const file = event.target.files[0];

    if (!file) return;

    const img = document.getElementById(
        "imgPreviewProducto"
    );

    const texto = document.getElementById(
        "textoPreviewProducto"
    );

    if (img) {
        img.src = URL.createObjectURL(file);
        img.style.display = "block";
    }

    if (texto) {
        texto.style.display = "none";
    }
}

// =========================
// TOGGLE STOCK
// =========================

function toggleStock() {
    const seleccionado = document.querySelector(
        'input[name="tipo_stock"]:checked'
    );

    const stockBox = document.getElementById(
        "stockBox"
    );

    if (!seleccionado || !stockBox) return;

    if (seleccionado.value === "indefinido") {
        stockBox.style.display = "none";
    } else {
        stockBox.style.display = "block";
    }
}

// =========================
// RESET MODAL PRODUCTO
// =========================

function resetProductoModal() {
    if (!productoForm) return;

    productoForm.reset();
    productoForm.action = "";

    const tipoInput = document.getElementById(
        "productoTipoInput"
    );

    if (tipoInput) {
        tipoInput.value = "producto";
    }

    if (productoModalTitle) {
        productoModalTitle.innerText =
            "Agregar un Producto";
    }

    const guardarBtn = document.getElementById(
        "guardarProductoBtn"
    );

    if (guardarBtn) {
        guardarBtn.innerText =
            "Guardar producto";
    }

    const img = document.getElementById(
        "imgPreviewProducto"
    );

    const texto = document.getElementById(
        "textoPreviewProducto"
    );

    if (img) {
        img.src = "";
        img.style.display = "none";
    }

    if (texto) {
        texto.style.display = "flex";
        texto.innerText = "Agregar Imagen";
    }

    const radioDefinido = document.querySelector(
        'input[name="tipo_stock"][value="definido"]'
    );

    if (radioDefinido) {
        radioDefinido.checked = true;
    }

    toggleStock();
}

// =========================
// EDITAR PRODUCTO
// =========================

function abrirEditarProducto(
    id,
    nombre,
    categoriaId,
    precio,
    descripcion,
    stockIndefinido,
    imagenUrl
) {
    if (!productoModal || !productoForm) return;

    resetProductoModal();

    productoForm.action =
        `/producto/editar/${id}/`;

    const tipoInput = document.getElementById(
        "productoTipoInput"
    );

    if (tipoInput) {
        tipoInput.value = "editar";
    }

    if (productoModalTitle) {
        productoModalTitle.innerText =
            "Editar Producto";
    }

    const guardarBtn = document.getElementById(
        "guardarProductoBtn"
    );

    if (guardarBtn) {
        guardarBtn.innerText =
            "Guardar cambios";
    }

    const nombreInput =
        document.getElementById("id_nombre");

    const categoriaInput =
        document.getElementById("id_categoria");

    const precioInput =
        document.getElementById("id_precio");

    const descripcionInput =
        document.getElementById(
            "id_descripcion"
        );

    if (nombreInput) {
        nombreInput.value = nombre;
    }

    if (categoriaInput) {
        categoriaInput.value = categoriaId;
    }

    if (precioInput) {
        precioInput.value = precio;
    }

    if (descripcionInput) {
        descripcionInput.value =
            descripcion;
    }

    const radioIndefinido =
        document.querySelector(
            'input[name="tipo_stock"][value="indefinido"]'
        );

    const radioDefinido =
        document.querySelector(
            'input[name="tipo_stock"][value="definido"]'
        );

    if (
        stockIndefinido &&
        radioIndefinido
    ) {
        radioIndefinido.checked = true;
    } else if (radioDefinido) {
        radioDefinido.checked = true;
    }

    toggleStock();

    const img = document.getElementById(
        "imgPreviewProducto"
    );

    const texto = document.getElementById(
        "textoPreviewProducto"
    );

    if (
        imagenUrl &&
        imagenUrl.trim() !== "" &&
        img
    ) {
        img.src = imagenUrl;
        img.style.display = "block";

        if (texto) {
            texto.style.display = "none";
        }
    }

    productoModal.classList.add("active");
    document.body.style.overflow = "hidden";
}

// =========================
// NUEVO PRODUCTO
// =========================

if (openProductoModal) {
    openProductoModal.addEventListener(
        "click",
        function () {
            if (!productoModal) return;

            resetProductoModal();

            productoModal.classList.add(
                "active"
            );

            document.body.style.overflow =
                "hidden";
        }
    );
}

// =========================
// CERRAR MODAL PRODUCTO
// =========================

if (productoModal) {
    productoModal.addEventListener(
        "click",
        function (e) {
            if (e.target === productoModal) {
                productoModal.classList.remove(
                    "active"
                );

                document.body.style.overflow =
                    "auto";
            }
        }
    );
}

// =========================
// CARRUSEL PRINCIPAL
// =========================

function moveSlide(direction) {
    const slides = document.querySelectorAll(
        ".carousel-slide"
    );

    if (!slides.length) return;

    currentSlide += direction;

    if (currentSlide < 0) {
        currentSlide = slides.length - 1;
    }

    if (currentSlide >= slides.length) {
        currentSlide = 0;
    }

    updateCarousel();
}

function updateCarousel() {
    const slides = document.querySelectorAll(
        ".carousel-slide"
    );

    if (!slides.length) return;

    slides.forEach((slide, index) => {
        slide.classList.remove(
            "active",
            "left",
            "right"
        );

        if (index === currentSlide) {
            slide.classList.add("active");
        } else if (
            index ===
            (
                currentSlide -
                1 +
                slides.length
            ) % slides.length
        ) {
            slide.classList.add("left");
        } else if (
            index ===
            (
                currentSlide + 1
            ) % slides.length
        ) {
            slide.classList.add("right");
        }
    });
}

// =========================
// STOCK
// =========================

function increaseStock(button) {
    const input =
        button.parentElement.querySelector(
            ".stock-input"
        );

    if (!input) return;

    input.value =
        parseInt(input.value || 0) + 1;
}

function decreaseStock(button) {
    const input =
        button.parentElement.querySelector(
            ".stock-input"
        );

    if (!input) return;

    const current =
        parseInt(input.value || 0);

    if (current > 0) {
        input.value = current - 1;
    }
}

// =========================
// GUARDAR STOCK
// =========================

async function saveStock(
    productoId,
    btn
) {
    const card = btn.closest(
        ".producto-card"
    );

    if (!card) return;

    const input =
        card.querySelector(
            ".stock-input"
        );

    if (!input) return;

    const formData = new FormData();

    formData.append(
        "producto_id",
        productoId
    );

    formData.append(
        "stock",
        input.value
    );

    const response = await fetch(
        "/actualizar-stock/",
        {
            method: "POST",
            headers: {
                "X-CSRFToken":
                    getCSRFToken(),
            },
            body: formData,
        }
    );

    const data =
        await response.json();

    if (data.success) {
        location.reload();
    }
}

// =========================
// VISIBILIDAD
// =========================

async function toggleVisibility(
    productoId
) {
    const formData = new FormData();

    formData.append(
        "producto_id",
        productoId
    );

    const response = await fetch(
        "/toggle-visibility/",
        {
            method: "POST",
            headers: {
                "X-CSRFToken":
                    getCSRFToken(),
            },
            body: formData,
        }
    );

    const data =
        await response.json();

    if (data.success) {
        location.reload();
    }
}

// =========================
// MODAL CARRUSEL
// =========================

function abrirModalCarrusel() {
    const modal = document.getElementById(
        "modalCarrusel"
    );

    if (!modal) return;

    imagenesParaEliminar = [];
    elementoPendienteEliminar = [];
    imagenesPreviewTemporales = [];

    const hidden =
        document.getElementById(
            "imagenesEliminarInput"
        );

    if (hidden) {
        hidden.value = "";
    }

    modal.classList.add("active");
    document.body.style.overflow =
        "hidden";
}

function cerrarModalCarrusel() {
    const modal = document.getElementById(
        "modalCarrusel"
    );

    if (!modal) return;

    modal.classList.remove("active");
    document.body.style.overflow =
        "auto";

    location.reload();
}

// =========================
// CONFIRMAR ELIMINACIÓN
// =========================

function confirmarEliminarCarrusel(
    btn
) {
    elementoPendienteEliminar =
        btn.closest(
            ".carrusel-editor-item"
        );

    const modal = document.getElementById(
        "confirmDeleteCarruselModal"
    );

    if (modal) {
        modal.classList.add("active");
    }
}

function cerrarConfirmDeleteCarrusel() {
    const modal = document.getElementById(
        "confirmDeleteCarruselModal"
    );

    if (modal) {
        modal.classList.remove(
            "active"
        );
    }

    elementoPendienteEliminar =
        null;
}

function eliminarImagenSeleccionada() {
    if (!elementoPendienteEliminar)
        return;

    const imagenId =
        elementoPendienteEliminar.dataset.id;

    if (
        imagenId &&
        !imagenesParaEliminar.includes(
            imagenId
        )
    ) {
        imagenesParaEliminar.push(
            imagenId
        );

        const hidden =
            document.getElementById(
                "imagenesEliminarInput"
            );

        if (hidden) {
            hidden.value =
                imagenesParaEliminar.join(
                    ","
                );
        }
    }

    elementoPendienteEliminar.remove();

    cerrarConfirmDeleteCarrusel();
}

// =========================
// PREVIEW NUEVAS IMÁGENES
// =========================

function previewNuevasImagenesCarrusel(input) {
    const grid = document.getElementById("carruselEditorGrid");

    if (!grid) return;

    const empty = grid.querySelector(".empty-products");
    if (empty) {
        empty.remove();
    }

    // Eliminar previews anteriores
    imagenesPreviewTemporales.forEach(item => item.remove());
    imagenesPreviewTemporales = [];

    Array.from(input.files).forEach((file, index) => {
        const reader = new FileReader();

        reader.onload = function (e) {
            const item = document.createElement("div");
            item.className = "carrusel-editor-item preview-temporal";
            item.dataset.previewIndex = index;

            item.innerHTML = `
                <img src="${e.target.result}">
                <button
                    type="button"
                    class="delete-carrusel-btn"
                    onclick="eliminarPreviewTemporal(this)"
                >
                    ×
                </button>
            `;

            grid.appendChild(item);
            imagenesPreviewTemporales.push(item);
        };

        reader.readAsDataURL(file);
    });
}

function eliminarPreviewTemporal(btn) {
    const item = btn.closest(".preview-temporal");

    if (!item) return;

    item.remove();
}

// =========================
// CERRAR MODALES
// =========================

document.addEventListener(
    "click",
    function (e) {
        const modalCarrusel =
            document.getElementById(
                "modalCarrusel"
            );

        const confirmModal =
            document.getElementById(
                "confirmDeleteCarruselModal"
            );

        if (
            modalCarrusel &&
            e.target === modalCarrusel
        ) {
            cerrarModalCarrusel();
        }

        if (
            confirmModal &&
            e.target === confirmModal
        ) {
            cerrarConfirmDeleteCarrusel();
        }
    }
);

// =========================
// INICIALIZACIÓN
// =========================

document.addEventListener(
    "DOMContentLoaded",
    function () {
        document
            .querySelectorAll(
                'input[name="tipo_stock"]'
            )
            .forEach((radio) => {
                radio.addEventListener(
                    "change",
                    toggleStock
                );
            });

        toggleStock();
        updateCarousel();
    }
);

// =========================
// MODAL LOGO
// =========================

function abrirModalLogo() {
    const modal = document.getElementById("modalLogo");

    if (!modal) return;

    const eliminarInput = document.getElementById(
        "eliminarLogoInput"
    );

    if (eliminarInput) {
        eliminarInput.value = "0";
    }

    modal.classList.add("active");
    document.body.style.overflow = "hidden";
}

function cerrarModalLogo() {
    const modal = document.getElementById("modalLogo");

    if (!modal) return;

    modal.classList.remove("active");
    document.body.style.overflow = "auto";

    // Restaurar estado original
    location.reload();
}

function previewNuevoLogo(event) {
    const file = event.target.files[0];

    if (!file) return;

    const reader = new FileReader();

    reader.onload = function (e) {
        const img = document.getElementById("logoPreview");
        const placeholder = document.getElementById(
            "logoPlaceholder"
        );

        if (img) {
            img.src = e.target.result;
            img.style.display = "block";
        }

        if (placeholder) {
            placeholder.style.display = "none";
        }

        const eliminarInput = document.getElementById(
            "eliminarLogoInput"
        );

        if (eliminarInput) {
            eliminarInput.value = "0";
        }
    };

    reader.readAsDataURL(file);
}

function eliminarLogo() {
    const img = document.getElementById("logoPreview");
    const placeholder = document.getElementById(
        "logoPlaceholder"
    );
    const eliminarInput = document.getElementById(
        "eliminarLogoInput"
    );

    if (img) {
        img.src = "";
        img.style.display = "none";
    }

    if (placeholder) {
        placeholder.style.display = "flex";
    }

    if (eliminarInput) {
        eliminarInput.value = "1";
    }
}