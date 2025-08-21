document.addEventListener('DOMContentLoaded', function() {

    // ========================================================================
    // SECCIÓN 1: EDICIÓN EN LÍNEA DE LA TABLA
    // ========================================================================
    const tablaBody = document.getElementById('tabla_MatrizActivos_body');

    if (tablaBody) {
        tablaBody.addEventListener('dblclick', function(event) {
            const cell = event.target;
            if (cell.tagName === 'TD' && cell.dataset.column) {
                makeCellEditable(cell);
            }
        });
    }

    function makeCellEditable(cell) {
        if (cell.querySelector('input') || cell.dataset.column === 'total') {
            return; // No editar celdas ya en edición o la celda del total
        }

        const originalValue = cell.textContent;
        cell.innerHTML = `<input type="text" value="${originalValue}" class="edit-input" style="width: 100%; box-sizing: border-box;">`;
        const input = cell.querySelector('input');
        input.focus();
        input.select();

        const save = () => {
            saveCellValue(cell, input.value, originalValue);
        };

        input.addEventListener('blur', save);
        input.addEventListener('keyup', (event) => {
            if (event.key === 'Enter') input.blur();
            if (event.key === 'Escape') cell.textContent = originalValue;
        });
    }

    function saveCellValue(cell, newValue, originalValue) {
        const row = cell.closest('tr');
        if (!row) return;

        const id = row.dataset.id;
        const columna = cell.dataset.column;
        
        // Si no hay cambios, no hacemos nada
        if (newValue === originalValue) {
            cell.textContent = originalValue;
            return;
        }

        cell.textContent = 'Guardando...';

        fetch('/actualizar_activo', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id, columna, valor: newValue })
        })
        .then(response => {
            if (!response.ok) throw new Error('Error del servidor');
            return response.json();
        })
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

    // ========================================================================
    // SECCIÓN 2: MANEJO DEL FORMULARIO DE NUEVO ACTIVO
    // ========================================================================
    const formNuevoActivo = document.getElementById('form_MatrizActivos');
    if (formNuevoActivo) {
        handleFormSubmit(formNuevoActivo, '/guardarMatriz', updateUiMatrizActivos);
    }

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
                    showMessage(data.message, false);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showMessage('Error de comunicación al guardar.', false);
            })
            .finally(() => {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            });
        });
    }

    function updateUiMatrizActivos(data) {
    const tablaBody = document.getElementById('tabla_MatrizActivos_body');
    if (!tablaBody) return;

    try {
        const newData = data.newData;
        const newRow = tablaBody.insertRow(0);
        newRow.dataset.id = newData.id;

        // --- INNERHTML CORREGIDO ---
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
            <td><button class="btn-editar">Editar</button></td> <!-- CELDA DE ACCIONES AÑADIDA -->
        `;
    } catch (error) {
        console.error("Error dentro de updateUiMatrizActivos:", error);
    }
}

// =================================================================================
    // 3. INICIALIZACIÓN (Conectar los formularios con sus manejadores y actualizadores)
    // =================================================================================

    // Usamos selectores de atributos para encontrar todos los formularios de un tipo.
    
    // Indicador: Matriz de Activos
    document.querySelectorAll('form[id^="form_MatrizActivos"]').forEach(form => {
        const endpoint = '/guardarMatriz'; // O podrías leerlo de form.getAttribute('action')
        handleFormSubmit(form, endpoint, updateUiMatrizActivos);
    });
})