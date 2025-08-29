// ========================================================================
// SCRIPT DE INTERACTIVIDAD PARA LA PÁGINA DE LISTA MAESTRA
// Maneja:
// 1. Carga dinámica de procesos sin recargar la página.
// 2. Guardado de nuevos documentos vía AJAX.
// 3. Expansión y colapso de filas para ver detalles.
// 4. Edición en línea (doble clic) de los datos de la tabla.
// ========================================================================

document.addEventListener('DOMContentLoaded', function() {

    // Referencias a los elementos principales que se actualizan
    const contentWrapper = document.getElementById('lista-maestra-content-wrapper');
    const procesoSelect = document.getElementById('proceso-select-lm');

    // ========================================================================
    // INICIALIZACIÓN
    // ========================================================================

    // 1. Listener para el menú desplegable de procesos
    if (procesoSelect) {
        procesoSelect.addEventListener('change', () => {
            const selectedProceso = procesoSelect.value;
            if (selectedProceso) {
                loadProcesoContent(selectedProceso);
            }
        });
    }

    // 2. Ejecuta todos los listeners por primera vez para el contenido inicial
    initializeAllListeners();

    // ========================================================================
    // LÓGICA PRINCIPAL Y DE CARGA
    // ========================================================================

    /**
     * Carga el contenido de un proceso (tabla y formulario) de forma dinámica.
     * @param {string} proceso - El nombre del proceso a cargar.
     */
    function loadProcesoContent(proceso) {
        if (!contentWrapper) return;
        contentWrapper.innerHTML = '<p style="text-align: center; padding: 20px;">Cargando...</p>';
        
        fetch(`/cargar_lista_proceso?proceso=${proceso}`)
            .then(response => {
                if (!response.ok) throw new Error('Error de red al cargar el proceso.');
                return response.text();
            })
            .then(html => {
                contentWrapper.innerHTML = html;
                // Después de inyectar el nuevo HTML, volvemos a aplicar todos los listeners.
                initializeAllListeners();
            })
            .catch(error => {
                console.error('Error al cargar la lista maestra:', error);
                contentWrapper.innerHTML = '<p style="color: red; text-align: center;">Error al cargar el contenido. Por favor, intente de nuevo.</p>';
            });
    }

    /**
     * Función central que busca y aplica todos los listeners de eventos
     * necesarios para que la página sea interactiva.
     */
    function initializeAllListeners() {
        const formNuevoDocumento = document.getElementById('form_ListaMaestra');
        const tablaBody = document.getElementById('tabla_lista_maestra_body');

        // Listener para el formulario de NUEVO DOCUMENTO
        if (formNuevoDocumento) {
            handleFormSubmit(formNuevoDocumento, '/guardaListaMaestra', updateUiListaMaestra);
        }

        // Listeners para la TABLA
        if (tablaBody) {
            tablaBody.addEventListener('click', handleRowClick);
            tablaBody.addEventListener('dblclick', handleRowDblClick);
        }
    }

    // ========================================================================
    // MANEJADORES DE EVENTOS
    // ========================================================================

    function handleRowClick(event) {
        const clickedRow = event.target.closest('.fila-principal');
        if (!clickedRow || event.target.tagName === 'INPUT') return;

        const detailsRow = clickedRow.nextElementSibling;
        if (detailsRow && detailsRow.classList.contains('fila-detalles')) {
            clickedRow.classList.toggle('expanded');
            detailsRow.classList.toggle('show');
        }
    }

    function handleRowDblClick(event) {
        const cell = event.target;
        if ((cell.tagName === 'TD' || cell.tagName === 'SPAN') && cell.dataset.column) {
            makeCellEditable(cell);
        }
    }

    // ========================================================================
    // LÓGICA DE EDICIÓN EN LÍNEA
    // ========================================================================

    function makeCellEditable(cell) {
        if (cell.querySelector('input')) return;
        const originalValue = cell.textContent.trim();
        
        const inputType = cell.dataset.column.includes('fecha') ? 'date' : 'text';
        cell.innerHTML = `<input type="${inputType}" value="${originalValue}" class="edit-input" style="width: 100%; box-sizing: border-box;">`;
        
        const input = cell.querySelector('input');
        input.focus();
        input.select();

        const save = () => saveCellValue(cell, input.value, originalValue);
        
        input.addEventListener('blur', save);
        input.addEventListener('keyup', (e) => {
            if (e.key === 'Enter') input.blur();
            if (e.key === 'Escape') cell.textContent = originalValue;
        });
    }

   function saveCellValue(cell, newValue, originalValue) {
    // --- LÓGICA DE BÚSQUEDA CORREGIDA Y SIMPLIFICADA ---
    let mainRow;
    const parentRow = cell.closest('tr'); // Encuentra la fila <tr> padre del elemento clickeado

    if (parentRow.classList.contains('fila-principal')) {
        mainRow = parentRow; // Si ya estamos en la fila principal, la usamos.
    } else if (parentRow.classList.contains('fila-detalles')) {
        mainRow = parentRow.previousElementSibling; // Si estamos en los detalles, buscamos la fila de arriba.
    }
    
    // Si no encontramos una fila principal o no hay cambios, no hacemos nada.
    if (!mainRow || newValue.trim() === originalValue) {
        cell.textContent = originalValue;
        return;
    }

    const id = mainRow.dataset.id;
    const columna = cell.dataset.column;
    
    // Si no tenemos todos los datos necesarios, detenemos para evitar errores.
    if (!id || !columna) {
        console.error("No se pudo encontrar el ID o la columna para guardar.");
        cell.textContent = originalValue;
        return;
    }

    cell.textContent = 'Guardando...';

    fetch('/actualizar_documento_maestro', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, columna, valor: newValue })
    })
    .then(response => {
        if (!response.ok) {
            // Si el servidor devuelve un error, lo leemos como texto para verlo.
            return response.text().then(text => { throw new Error(text) });
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            cell.textContent = newValue;
            // Opcional: mostrar un mensaje de éxito
            // showMessage('¡Actualizado!'); 
        } else {
            cell.textContent = originalValue;
            showMessage(data.message || 'Error al actualizar.', false);
        }
    })
    .catch(error => {
        console.error('Error en saveCellValue:', error);
        cell.textContent = originalValue;
        showMessage('Error de red al intentar actualizar.', false);
    });
}
    // ========================================================================
    // LÓGICA DE GUARDADO DE FORMULARIO
    // ========================================================================

    function handleFormSubmit(form, endpoint, successCallback) {
        if (form.dataset.listenerAttached) return;
        form.dataset.listenerAttached = 'true';

        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.disabled = true;
            submitBtn.textContent = 'Guardando...';

            fetch(endpoint, {
                method: 'POST',
                body: new FormData(form)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showMessage(data.message, true);
                    if (successCallback) successCallback(data);
                    form.reset();
                } else {
                    showMessage(data.message || 'Ocurrió un error.', false);
                }
            })
            .catch(error => {
                console.error('Error al enviar formulario:', error);
                showMessage('Error de comunicación al guardar.', false);
            })
            .finally(() => {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            });
        });
    }

    function updateUiListaMaestra(data) {
        const tablaBody = document.getElementById('tabla_lista_maestra_body');
        if (!tablaBody) return;
        try {
            const newData = data.newData;
            const newMainRow = document.createElement('tr');
            newMainRow.className = 'fila-principal';
            newMainRow.dataset.id = newData.id;
            
            newMainRow.innerHTML = `
                <td><span class="toggle-icon">+</span></td>
                <td data-column="tipo_documento">${newData.tipo_documento}</td>
                <td data-column="consecutivo">${newData.consecutivo}</td>
                <td data-column="nombre_documento">${newData.nombre_documento}</td>
                <td data-column="version">${newData.version}</td>
                <td data-column="estado">${newData.estado}</td>
                <td><button>Ver</button></td>
            `;

            const newDetailsRow = document.createElement('tr');
            newDetailsRow.className = 'fila-detalles';
            newDetailsRow.innerHTML = `
                <td colspan="7">
                    <div class="detalles-contenido">
                        <div class="detalle-item"><strong>Área:</strong> <span data-column="area">${newData.area}</span></div>
                        <div class="detalle-item"><strong>Int/Ext:</strong> <span data-column="int_ext">${newData.int_ext}</span></div>
                        <div class="detalle-item"><strong>Medio:</strong> <span data-column="medio">${newData.medio}</span></div>
                        <div class="detalle-item"><strong>Procedimiento:</strong> <span data-column="procedimiento">${newData.procedimiento}</span></div>
                        <div class="detalle-item"><strong>Fecha Aprobación:</strong> <span data-column="fecha_aprobacion">${newData.fecha_aprobacion}</span></div>
                        <div class="detalle-item"><strong>Responsable:</strong> <span data-column="responsable_aprobacion">${newData.responsable_aprobacion}</span></div>
                        <div class="detalle-item"><strong>Última Revisión:</strong> <span data-column="fecha_ultima_revision">${newData.fecha_ultima_revision}</span></div>
                        <div class="detalle-item"><strong>Almacenamiento:</strong> <span data-column="almacenamiento_donde">${newData.almacenamiento_donde}</span> (<span data-column="almacenamiento_como">${newData.almacenamiento_como}</span>)</div>
                        <div class="detalle-item"><strong>Clasificación:</strong> <span data-column="clasificacion">${newData.clasificacion}</span></div>
                        <div class="detalle-item"><strong>Disponible Para:</strong> <span data-column="disponible_para">${newData.disponible_para}</span></div>
                        <div class="detalle-item"><strong>Protección:</strong> <span data-column="proteccion">${newData.proteccion}</span></div>
                        <div class="detalle-item"><strong>Tiempo Archivo:</strong> <span data-column="tiempo_activo">Activo: ${newData.tiempo_activo}</span>, <span data-column="tiempo_inactivo">Inactivo: ${newData.tiempo_inactivo}</span></div>
                        <div class="detalle-item"><strong>Disposición:</strong> <span data-column="disposicion">${newData.disposicion}</span></div>
                    </div>
                </td>
            `;
            
            tablaBody.prepend(newDetailsRow);
            tablaBody.prepend(newMainRow);

        } catch (error) {
            console.error("Error al actualizar la tabla:", error);
        }
    }

    // ========================================================================
    // LÓGICA DE ALERTAS Y ESTILOS
    // ========================================================================
    
    function showMessage(message, isSuccess = true) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `alert ${isSuccess ? 'alert-success' : 'alert-danger'}`;
        messageDiv.style.cssText = `
            position: fixed; top: 20px; right: 20px; z-index: 10000;
            padding: 15px 20px; border-radius: 8px; color: white;
            font-weight: 600; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            animation: slideInRight 0.3s ease; max-width: 400px; word-wrap: break-word;
        `;
        if (isSuccess) {
            messageDiv.style.background = 'linear-gradient(135deg, #28a745 0%, #20c997 100%)';
        } else {
            messageDiv.style.background = 'linear-gradient(135deg, #dc3545 0%, #c82333 100%)';
        }
        messageDiv.textContent = message;
        document.body.appendChild(messageDiv);
        setTimeout(() => {
            messageDiv.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => messageDiv.remove(), 300);
        }, 5000);
    }

    if (!document.getElementById('alert-animation-styles')) {
        const style = document.createElement('style');
        style.id = 'alert-animation-styles';
        style.textContent = `
            @keyframes slideInRight { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
            @keyframes slideOutRight { from { transform: translateX(0); opacity: 1; } to { transform: translateX(100%); opacity: 0; } }
        `;
        document.head.appendChild(style);
    }
});