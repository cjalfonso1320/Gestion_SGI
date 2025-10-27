
document.addEventListener('DOMContentLoaded', function () {
    const modal = document.getElementById('sectionModal');
    const btn = document.getElementById('openModalBtn');
    const span = document.querySelector('.close-button');
    const selector = document.getElementById('sectionSelector');
    const contentArea = document.getElementById('sectionContent');
    const saveBtn = document.getElementById('saveChangesBtn');
    const sections = document.querySelectorAll('.doc-section');

    // Llenar el select con las secciones del documento
    sections.forEach((section, index) => {
        // Usamos el data-id como valor para identificar la sección
        let option = new Option(section.textContent.trim(), section.dataset.id);
        selector.add(option);
    });

    // Mostrar contenido cuando se selecciona una opción
    selector.addEventListener('change', function () {
        if (this.value !== "") {
            // Buscamos el contenido por su data-id correspondiente
            const contentElement = document.querySelector(`.doc-content[data-id="${this.value}"]`);
            if (contentElement) {
                // Usamos innerHTML para preservar el formato HTML si existe
                contentArea.value = contentElement.innerHTML.trim();
            } else {
                contentArea.value = 'No se encontró contenido para esta sección.';
            }
        } else {
            contentArea.value = '';
        }
    });

    // Lógica para guardar los cambios
    saveBtn.addEventListener('click', function () {
        const sectionId = selector.value;
        const newContent = contentArea.value;
        const cambioDescripcion = document.getElementById('sectionCambio').value.trim();
        const documento = document.getElementById('documento').textContent.trim();
        const nombreDocumento = document.getElementById('nombre_documento').textContent.trim();

        if (!sectionId) {
            showMessage('Por favor, selecciona una sección para editar.', false);
            return;
        }

        fetch('/procedimientos/actualizar_seccion', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                documento: documento, // <-- ¡NUEVO! Enviamos el nombre del archivo
                id: sectionId,
                contenido: newContent,
                descripcion: cambioDescripcion, // <-- ¡NUEVO! Enviamos la descripción del cambio
                nombre_documento: nombreDocumento // <-- ¡NUEVO! Enviamos el nombre del documento
            })
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showMessage(data.message, true);
                    // Actualizar el contenido en la página sin recargar
                    const contentElement = document.querySelector(`.doc-content[data-id="${sectionId}"]`);
                    if (contentElement) {
                        contentElement.innerHTML = newContent;
                    }
                    modal.style.display = 'none'; // Cerrar modal
                } else {
                    showMessage(data.message || 'Error al guardar los cambios.', false);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showMessage('Error de red al intentar guardar.', false);
            });
    });

    function showMessage(message, isSuccess = true) {
        const alert = document.createElement('div');
        alert.className = `alert ${isSuccess ? 'alert-success' : 'alert-danger'}`;
        alert.textContent = message;
        document.body.appendChild(alert);
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 3000);
    }

    // Lógica para abrir y cerrar el modal
    btn.onclick = () => modal.style.display = 'block';
    span.onclick = () => modal.style.display = 'none';
    window.onclick = (event) => {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    };

    // Manejar el formulario de aprobación/rechazo


});
