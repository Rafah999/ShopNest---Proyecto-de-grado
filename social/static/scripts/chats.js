document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("chatForm");

    if (!form) return;

    form.addEventListener("submit", async function (e) {
        e.preventDefault();

        const chatId = document.getElementById("chatId").value;
        const tipo = document.getElementById("chatTipo").value;
        const mensaje = document.getElementById("chatMensaje").value.trim();
        const csrfToken = document.querySelector(
            "[name=csrfmiddlewaretoken]"
        ).value;

        if (!tipo) {
            alert("Debes seleccionar una opción.");
            return;
        }

        const submitBtn = form.querySelector("button[type='submit']");
        submitBtn.disabled = true;
        submitBtn.textContent = "Enviando...";

        const formData = new FormData();
        formData.append("chat_id", chatId);
        formData.append("tipo", tipo);
        formData.append("mensaje", mensaje);

        try {
            const response = await fetch("/social/chats/enviar/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken,
                    "X-Requested-With": "XMLHttpRequest"
                },
                body: formData
            });

            const data = await response.json();

            if (!data.success) {
                alert(data.error || "Ocurrió un error.");
                submitBtn.disabled = false;
                submitBtn.textContent = "Enviar mensaje";
                return;
            }

            // Recargar para mostrar mensajes guardados y el nuevo producto
            window.location.href = `?chat=${chatId}`;

        } catch (error) {
            console.error(error);
            alert("Ocurrió un error al enviar el mensaje.");
            submitBtn.disabled = false;
            submitBtn.textContent = "Enviar mensaje";
        }
    });
});