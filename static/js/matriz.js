document.addEventListener('DOMContentLoaded', function() {

    // Referencias a los elementos principales de la página
     const contentWrapper = document.getElementById('matriz-content-wrapper');
    const procesoSelect = document.getElementById('proceso-select');

    // ========================================================================
    // INICIALIZACIÓN PRINCIPAL
    // ========================================================================

    // 1. Configura el listener para el menú desplegable de procesos
    if (procesoSelect) {
        procesoSelect.addEventListener('change', function() {
            loadProcesoContent(this.value);
        });
    }

    initializeMatrizListeners();

    // ========================================================================
    // FUNCIONES DE LÓGICA
    // ========================================================================

    /**
     * Carga el contenido de un proceso (tabla y formulario) de forma dinámica.
     * @param {string} proceso - El nombre del proceso a cargar.
     */
    function loadProcesoContent(proceso) {
        contentWrapper.innerHTML = '<p style="text-align: center; padding: 20px;">Cargando datos del proceso...</p>';
        fetch(`/cargar_matriz_proceso?proceso=${proceso}`)
            .then(response => response.text())
            .then(html => {
                contentWrapper.innerHTML = html;
                // Después de cargar el nuevo contenido, volvemos a aplicar TODOS los listeners
                initializeMatrizListeners();
            })
            .catch(error => {
                console.error('Error al cargar el proceso:', error);
                contentWrapper.innerHTML = '<p style="color: red; text-align: center; padding: 20px;">Error al cargar los datos.</p>';
            });
    }
    /**
     * Función central que busca y aplica todos los listeners de eventos
     * necesarios para que la matriz sea interactiva. Se debe llamar cada vez
     * que el contenido de la tabla/formulario se actualiza.
     */
    function initializeMatrizListeners() {
        const formNuevoActivo = document.getElementById('form_MatrizActivos');
        const tablaBody = document.getElementById('tabla_MatrizActivos_body');

        // 1. Listener para el formulario de NUEVO ACTIVO
        if (formNuevoActivo) {
            handleFormSubmit(formNuevoActivo, '/guardarMatriz', updateUiMatrizActivos);
            // --- LÓGICA DE CÁLCULO AÑADIDA AQUÍ ---
            initializeFormCalculations(formNuevoActivo);
        }

        // 2. Listener para la EDICIÓN EN LÍNEA
        if (tablaBody) {
            tablaBody.addEventListener('dblclick', function(event) {
                const cell = event.target;
                if (cell.tagName === 'TD' && cell.dataset.column) {
                    makeCellEditable(cell);
                }
            });
        }
    }

/**
     * Añade los listeners para el cálculo automático del total en el formulario.
     * @param {HTMLFormElement} form - El formulario al que se le añadirán los listeners.
     */
    function initializeFormCalculations(form) {
        const confidencialidadInput = form.querySelector('#ConfidencialidadActivo');
        const integridadInput = form.querySelector('#IntegridadActivo');
        const disponibilidadInput = form.querySelector('#DisponibilidadActivo');
        const totalInput = form.querySelector('#TotalActivo');

        // Si alguno de los campos no existe, no hacemos nada.
        if (!confidencialidadInput || !integridadInput || !disponibilidadInput || !totalInput) {
            return;
        }

        function calcularTotal() {
            const confidencialidad = parseInt(confidencialidadInput.value) || 0;
            const integridad = parseInt(integridadInput.value) || 0;
            const disponibilidad = parseInt(disponibilidadInput.value) || 0;
            totalInput.value = confidencialidad + integridad + disponibilidad;
        }

        confidencialidadInput.addEventListener('input', calcularTotal);
        integridadInput.addEventListener('input', calcularTotal);
        disponibilidadInput.addEventListener('input', calcularTotal);
    }


    // ========================================================================
    // FUNCIONES AUXILIARES (Las que ya tenías)
    // ========================================================================

    /**
     * Maneja el envío de un formulario de forma asíncrona.
     */
    function handleFormSubmit(form, endpoint, successCallback) {
        // Previene que se añada el listener múltiples veces
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
                    showMessage(data.message, false);
                }
            })
            .catch(error => {
                console.error('Error al enviar el formulario:', error);
                showMessage('Error de comunicación al guardar.', false);
            })
            .finally(() => {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            });
        });
    }

    /**
     * Actualiza la tabla después de guardar un nuevo activo.
     */
    function updateUiMatrizActivos(data) {
        const tablaBody = document.getElementById('tabla_MatrizActivos_body');
        if (!tablaBody) return;
        try {
            const newData = data.newData;
            const newRow = tablaBody.insertRow(0);
            newRow.dataset.id = newData.id;

            newRow.innerHTML = `
                <td data-column="tipoActivo">${newData.tipoActivo}</td>
                <td data-column="nombre_activo">${newData.nombre_activo}</td>
                <td data-column="cant_activo">${newData.cant_activo}</td>
                <td data-column="responsable_activo">${newData.responsable_activo}</td>
                <td data-column="clasificacionActivo">${newData.clasificacionActivo}</td>
                <td data-column="ConfidencialidadActivo">${newData.ConfidencialidadActivo}</td>
                <td data-column="IntegridadActivo">${newData.IntegridadActivo}</td>
                <td data-column="DisponibilidadActivo">${newData.DisponibilidadActivo}</td>
                <td data-column="total">${newData.TotalActivo}</td>
                
            `;
        } catch (error) {
            console.error("Error al actualizar la tabla:", error);
        }
    }

    /**
     * Convierte una celda <td> en un <input> editable.
     */
    function makeCellEditable(cell) {
        if (cell.querySelector('input') || cell.dataset.column === 'total') {
            return;
        }

        const originalValue = cell.textContent;
        cell.innerHTML = `<input type="text" value="${originalValue}" class="edit-input" style="width: 100%; box-sizing: border-box;">`;
        const input = cell.querySelector('input');
        input.focus();
        input.select();

        const save = () => saveCellValue(cell, input.value, originalValue);

        input.addEventListener('blur', save);
        input.addEventListener('keyup', (event) => {
            if (event.key === 'Enter') input.blur();
            if (event.key === 'Escape') cell.textContent = originalValue;
        });
    }

    /**
     * Guarda el valor de una celda editada en la base de datos.
     */
    function saveCellValue(cell, newValue, originalValue) {
        const row = cell.closest('tr');
        if (!row || newValue === originalValue) {
            cell.textContent = originalValue;
            return;
        }

        const id = row.dataset.id;
        const columna = cell.dataset.column;
        cell.textContent = 'Guardando...';

        fetch('/actualizar_activo', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id, columna, valor: newValue })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                cell.textContent = newValue;
                const totalCell = row.querySelector('td[data-column="total"]');
                if (totalCell && data.nuevo_total !== undefined) {
                    totalCell.textContent = data.nuevo_total;
                }
            } else {
                cell.textContent = originalValue;
                alert('Error al actualizar: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error de red:', error);
            cell.textContent = originalValue;
            alert('Error de red al intentar actualizar.');
        });
    }

    /**
     * Muestra una notificación emergente de éxito o error.
     */
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

    // Añade los estilos para las animaciones de las alertas
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
        @keyframes slideOutRight { from { transform: translateX(0); opacity: 1; } to { transform: translateX(100%); opacity: 0; } }
    `;
    document.head.appendChild(style);
});