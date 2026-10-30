var activosData = Array.isArray(window.__activosData) ? window.__activosData : [];

document.addEventListener('DOMContentLoaded', function(){

    initializeAllListeners();
        //FUNCION CENTRAL QUE INICIALIZA LOS LISTENER
    function initializeAllListeners() {
        const form = document.getElementById('form_MatrizRiesgos');
        const tablaBody = document.getElementById('tabla_riesgos_body');

        if (form) {
            // Se añaden los listeners para el cálculo y el autocompletado
            form.addEventListener('input', calcularRiesgos);
            initializeActivoSelect(form);
            // Se añade el listener para el envío del formulario
            handleFormSubmit(form, '/guardar_riesgo', updateUiRiesgos);
        }

        if (tablaBody) {
            // Se añade el listener para expandir/colapsar filas
            tablaBody.addEventListener('click', function(event) {
                // Si el click fue en el botón editar, no expandir/colapsar
                if (event.target.closest('.btn-editar-riesgo')) return;
                handleRowClick(event);
            });

            // Listener para el botón editar
            tablaBody.addEventListener('click', function(event) {
                const editBtn = event.target.closest('.btn-editar-riesgo');
                if (editBtn) {
                    const riesgoId = editBtn.dataset.id;
                    cargarRiesgoEnFormulario(riesgoId);
                }
            });
        }
    }

    // ========================================================================
    // CARGA RIESGO EN FORMULARIO (EDITAR)
    // ========================================================================
    function cargarRiesgoEnFormulario(riesgoId) {
        const form = document.getElementById('form_MatrizRiesgos');
        if (!form) return;

        const baseUrl = window.BASE_URL || '';
        fetch(`${baseUrl}/get_riesgo/${riesgoId}`)
            .then(res => res.json())
            .then(data => {
                if (!data.success) {
                    showMessage('Error al cargar riesgo: ' + data.message, false);
                    return;
                }
                const r = data.riesgo;

                // Guardar ID en hidden
                document.getElementById('edit_id').value = r.id;

                // 1. Identificación del Activo
                setSelectValue('nombre_activo', r.nombre_activo);
                setFieldValue('tipoActivo', r.tipo_activo);
                setFieldValue('criticidadActivo', r.criticidad_activo);

                // 2. Identificación del Riesgo
                setFieldValue('amenaza', r.amenaza);
                setFieldValue('vulnerabilidad', r.vulnerabilidad);
                setFieldValue('nombre_riesgo', r.nombre_riesgo);
                setFieldValue('descripcion_riesgo', r.descripcion_riesgo);
                setSelectValue('tipoRiesgo', r.tipo_riesgo);
                setFieldValue('responsable_riesgo', r.responsable_riesgo);
                setSelectValue('norma', r.norma);

                // 3. Análisis y Controles
                setFieldValue('probabilidadInherente', r.probabilidad_inherente);
                setFieldValue('impactoInherente', r.impacto_inherente);
                setFieldValue('total_riesgoInherente', r.total_riesgo_inherente);
                setFieldValue('criticidadRiesgoInherente', r.criticidad_riesgo_inherente);
                setFieldValue('NormaISO', r.control_norma_iso);
                setFieldValue('descripcionControl', r.control_descripcion);
                setFieldValue('seguimientoControl', r.control_seguimiento);
                setFieldValue('fechaRevision', r.control_fecha_revision);
                setFieldValue('probabilidadResidual', r.probabilidad_residual);
                setFieldValue('impactoResidual', r.impacto_residual);
                setFieldValue('total_riesgoResidual', r.total_riesgo_residual);
                setFieldValue('criticidadRiesgoResidual', r.criticidad_riesgo_residual);
                setSelectValue('opcionesManejo', r.opciones_manejo);

                // 4. Tratamiento y Seguimiento
                setFieldValue('actividades_planAccion', r.tratamiento_plan_accion);
                setFieldValue('fechaImplementacion', r.tratamiento_fecha_implementacion);
                setFieldValue('responsable_implementacion', r.tratamiento_responsable);
                setFieldValue('descripcion_seguimiento', r.seguimiento_descripcion);
                setFieldValue('fechaSeguimiento', r.seguimiento_fecha);

                // Aplicar colores de criticidad
                aplicarColorCriticidad('criticidadRiesgoInherente', r.criticidad_riesgo_inherente);
                aplicarColorCriticidad('criticidadRiesgoResidual', r.criticidad_riesgo_residual);

                // Cambiar el botón submit a modo edición
                const submitBtn = form.querySelector('button[type="submit"]');
                submitBtn.innerHTML = '<i class="fa-solid fa-pen-to-square"></i> Actualizar';
                submitBtn.style.background = 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)';

                // Mostrar botón Cancelar
                const cancelBtn = document.getElementById('btnCancelarEdicion');
                if (cancelBtn) cancelBtn.style.display = 'inline-flex';

                // Abrir el acordeón si está cerrado
                const accordion = document.getElementById('acordeonTabla');
                if (accordion) accordion.classList.add('active');

                // Scroll suave al formulario
                form.scrollIntoView({ behavior: 'smooth', block: 'start' });

                showMessage('Riesgo cargado para edición. Al guardar se actualizarán los datos.', true);
            })
            .catch(err => {
                console.error('Error al cargar riesgo:', err);
                if (err instanceof TypeError && err.message.includes('JSON')) {
                    showMessage('El servidor no devolvió JSON. Revisa consola (F12) para más detalles.', false);
                } else {
                    showMessage('Error de conexión: ' + err.message, false);
                }
            });
    }

    function setFieldValue(id, value) {
        const el = document.getElementById(id);
        if (el) el.value = value || '';
    }

    function setSelectValue(id, value) {
        const el = document.getElementById(id);
        if (!el) return;
        // Buscar la opción que coincida (case-insensitive)
        for (let opt of el.options) {
            if (opt.value.toLowerCase() === (value || '').toLowerCase()) {
                el.value = opt.value;
                return;
            }
        }
        el.value = '';
    }

    function aplicarColorCriticidad(id, criticidad) {
        const el = document.getElementById(id);
        if (!el) return;
        let color = '';
        const c = (criticidad || '').toLowerCase();
        if (c === 'extrema') color = '#E7180B';
        else if (c === 'alta') color = '#FF8904';
        else if (c === 'moderada') color = '#FFDF20';
        else if (c === 'baja') color = '#2795F5';
        if (color) {
            el.style.backgroundColor = color;
            el.style.color = (color === '#FFDF20') ? 'black' : 'white';
        }
    }

    window.limpiarFormularioRiesgo = function () {
        const form = document.getElementById('form_MatrizRiesgos');
        if (form) {
            form.reset();
            document.getElementById('edit_id').value = '';
            const submitBtn = form.querySelector('button[type="submit"]');
            submitBtn.innerHTML = '<i class="fa-solid fa-floppy-disk"></i> Guardar';
            submitBtn.style.background = '';
            
            const cancelBtn = document.getElementById('btnCancelarEdicion');
            if (cancelBtn) cancelBtn.style.display = 'none';
        }
    }

    //funciones auxiliares
    function initializeActivoSelect(form) {
        const nombreActivoSelect = form.querySelector('#nombre_activo');
        const tipoActivoInput = form.querySelector('#tipoActivo');
        const criticidadActivoInput = form.querySelector('#criticidadActivo');

        if (!nombreActivoSelect || !tipoActivoInput || !criticidadActivoInput) return;

        function getCriticidadFromTotal(total) {
            const valor = parseInt(total);
            if (valor > 12) return "Extrema";
            if (valor >= 9) return "Alta";
            if (valor >= 5) return "Moderada";
            return "Baja";
        }

        nombreActivoSelect.addEventListener('change', function() {
            const selectedName = this.value;

            if (!selectedName) {
                tipoActivoInput.value = '';
                criticidadActivoInput.value = '';
                return;
            }
            
            // Ahora 'activosData' es accesible porque está en el ámbito global
            if (!Array.isArray(activosData) || activosData.length === 0) {
                tipoActivoInput.value = '';
                criticidadActivoInput.value = '';
                return;
            }
            const selectedActivo = activosData.find(activo => activo.nombre === selectedName);
            if (selectedActivo) {
                tipoActivoInput.value = selectedActivo.tipo_activo;
                criticidadActivoInput.value = getCriticidadFromTotal(selectedActivo.total);
            } else {
                tipoActivoInput.value = '';
                criticidadActivoInput.value = '';
            }
        });
    }

    function calcularRiesgos() {
        // RIESGO INHERENTE
        const probInhEl = document.getElementById('probabilidadInherente');
        const impInhEl = document.getElementById('impactoInherente');
        const critInhEl = document.getElementById('criticidadRiesgoInherente');
        const totalInhEl = document.getElementById('total_riesgoInherente');
        if (!probInhEl || !impInhEl || !critInhEl || !totalInhEl) return;
        const probInherente = parseInt(probInhEl.value) || 0;
        const impInherente = parseInt(impInhEl.value) || 0;
        const totalInherente = probInherente * impInherente;
        
        totalInhEl.value = totalInherente;
        
        let criticidad = "N/A";
        let color = "";
        if (totalInherente > 12) { criticidad = "Extrema"; color = "#E7180B"; }
        else if (totalInherente >= 9) { criticidad = "Alta"; color = "#FF8904"; }
        else if (totalInherente >= 5) { criticidad = "Moderada"; color = "#FFDF20"; }
        else if (totalInherente >= 1) { criticidad = "Baja"; color = "#2795F5"; }
        
        critInhEl.value = criticidad;
        critInhEl.style.backgroundColor = color;
        critInhEl.style.color = (color === "#FFDF20" || color === "") ? "black" : "white";

        // RIESGO RESIDUAL
        const probResEl = document.getElementById('probabilidadResidual');
        const impResEl = document.getElementById('impactoResidual');
        const critResEl = document.getElementById('criticidadRiesgoResidual');
        const totalResEl = document.getElementById('total_riesgoResidual');
        if (!probResEl || !impResEl || !critResEl || !totalResEl) return;
        const probResidual = parseInt(probResEl.value) || 0;
        const impResidual = parseInt(impResEl.value) || 0;
        const totalResidual = probResidual * impResidual;
        
        totalResEl.value = totalResidual;
        
        let criticidadRes = "N/A";
        let colorRes = "";
        if (totalResidual > 12) { criticidadRes = "Extrema"; colorRes = "#E7180B"; }
        else if (totalResidual >= 9) { criticidadRes = "Alta"; colorRes = "#FF8904"; }
        else if (totalResidual >= 5) { criticidadRes = "Moderada"; colorRes = "#FFDF20"; }
        else if (totalResidual >= 1) { criticidadRes = "Baja"; colorRes = "#2795F5"; }

        critResEl.value = criticidadRes;
        critResEl.style.backgroundColor = colorRes;
        critResEl.style.color = (colorRes === "#FFDF20" || colorRes === "") ? "black" : "white";
    }
    function handleRowClick(event) {
        const clickedRow = event.target.closest('.fila-principal');
        if (!clickedRow) return;
        const detailsRow = clickedRow.nextElementSibling;
        if (detailsRow && detailsRow.classList.contains('fila-detalles')) {
            // Corregido: 'toggle'
            detailsRow.classList.toggle('show');
            clickedRow.classList.toggle('expanded');
        }
    }

    /**
     * Convierte una celda <td> en un <input> editable.
     */
    function makeCellEditable(cell) {
        // Evita que se pueda editar si ya hay un input o es una celda no editable
        if (cell.querySelector('input')) {
            return;
        }

        const originalValue = cell.textContent.trim();
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

        fetch(`${BASE_URL}/actualizar_riesgo`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id, columna, valor: newValue })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                cell.textContent = newValue;
                showMessage(data.message, true);
            } else {
                cell.textContent = originalValue;
                showMessage('Error al actualizar: ' + data.message, false);
            }
        })
        .catch(error => console.error('Error de red:', error));
    }
// ========================================================================
    // LÓGICA DE ENVÍO DE FORMULARIO Y ACTUALIZACIÓN DE UI
    // ========================================================================
    
    function handleFormSubmit(form, endpoint, successCallback) {
        if (form.dataset.listenerAttached) return;
        form.dataset.listenerAttached = 'true';

        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const submitBtn = form.querySelector('button[type="submit"]');
            const editId = document.getElementById('edit_id').value;
            const isEditing = editId && editId !== '';
            const originalText = submitBtn.textContent;
            submitBtn.disabled = true;
            submitBtn.textContent = 'Guardando...';

            // Elegir endpoint según si estamos creando o actualizando
            const baseUrl = window.BASE_URL || '';
            const url = isEditing ? `${baseUrl}/actualizar_riesgo_completo` : endpoint;

            fetch(url, {
                method: 'POST',
                body: new FormData(form)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showMessage(data.message, true);
                    if (successCallback) successCallback(data, isEditing);
                    limpiarFormularioRiesgo();
                } else {
                    showMessage(data.message || 'Ocurrió un error al guardar.', false);
                }
            })
            .catch(error => {
                console.error('Error en fetch:', error);
                showMessage('Error de comunicación al guardar.', false);
            })
            .finally(() => {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            });
        });
    }

function updateUiRiesgos(data, isEditing) {
    const tablaBody = document.getElementById('tabla_riesgos_body');
    if (!tablaBody) return;

    try {
        const newData = data.newData;
        const newRowHtml = crearFilaRiesgoHtml(newData);
        const tempContainer = document.createElement('div');
        tempContainer.innerHTML = newRowHtml;

        if (isEditing) {
            // Reemplazar la fila existente en lugar de añadir al inicio
            const existingRow = tablaBody.querySelector(`tr.fila-principal[data-id="${newData.id}"]`);
            if (existingRow) {
                const existingDetails = existingRow.nextElementSibling;
                existingRow.replaceWith(tempContainer.children[0]); // nueva fila principal
                if (existingDetails && existingDetails.classList.contains('fila-detalles')) {
                    existingDetails.replaceWith(tempContainer.children[1]); // nueva fila detalles
                }
            } else {
                tablaBody.prepend(tempContainer.children[1]);
                tablaBody.prepend(tempContainer.children[0]);
            }
        } else {
            tablaBody.prepend(tempContainer.children[1]); // Fila de detalles
            tablaBody.prepend(tempContainer.children[0]); // Fila principal
        }
    } catch (error) {
        console.error('Error al actualizar la tabla:', error);
    }
}

function crearFilaRiesgoHtml(d) {
    return `
        <tr class="fila-principal" data-id="${d.id}">
            <td><span class="toggle-icon">+</span></td>
            <td><button type="button" class="btn-editar-riesgo" data-id="${d.id}" title="Editar riesgo"><i class="fa-regular fa-pen-to-square"></i></button></td>
            <td data-column="nombre_riesgo">${d.nombre_riesgo || ''}</td>
            <td data-column="nombre_activo">${d.nombre_activo || ''}</td>
            <td><span class="badge-criticidad ${(d.criticidad_riesgo_inherente||'na').toLowerCase()}">${d.criticidad_riesgo_inherente || ''}</span></td>
            <td><span class="badge-criticidad ${(d.criticidad_riesgo_residual||'na').toLowerCase()}">${d.criticidad_riesgo_residual || ''}</span></td>
            <td><span class="badge-manejo ${(d.opciones_manejo||'').toLowerCase()}">${d.opciones_manejo || ''}</span></td>
        </tr>
        <tr class="fila-detalles">
            <td colspan="7">
                <div class="detalles-contenido use-grid">
                    <div class="detalle-item"><strong>Proceso:</strong><span>${d.proceso || ''}</span></div>
                    <div class="detalle-item"><strong>Tipo de Activo:</strong><span>${d.tipo_activo || ''}</span></div>
                    <div class="detalle-item"><strong>Criticidad del Activo:</strong><span>${d.criticidad_activo || ''}</span></div>
                    <div class="detalle-item"><strong>Amenaza:</strong><span>${d.amenaza || ''}</span></div>
                    <div class="detalle-item"><strong>Vulnerabilidad:</strong><span>${d.vulnerabilidad || ''}</span></div>
                    <div class="detalle-item"><strong>Descripción del Riesgo:</strong><span>${d.descripcion_riesgo || ''}</span></div>
                    <div class="detalle-item"><strong>Tipo del Riesgo:</strong><span>${d.tipo_riesgo || ''}</span></div>
                    <div class="detalle-item"><strong>Responsable del Riesgo:</strong><span>${d.responsable_riesgo || ''}</span></div>
                    <div class="detalle-item"><strong>Norma:</strong><span>${d.norma || ''}</span></div>
                    <div class="detalle-item"><strong>Probabilidad Inherente:</strong><span>${d.probabilidad_inherente || ''}</span></div>
                    <div class="detalle-item"><strong>Impacto Inherente:</strong><span>${d.impacto_inherente || ''}</span></div>
                    <div class="detalle-item"><strong>Total del Riesgo Inherente:</strong><span>${d.total_riesgo_inherente || ''}</span></div>
                    <div class="detalle-item"><strong>Norma ISO:</strong><span>${d.control_norma_iso || ''}</span></div>
                    <div class="detalle-item"><strong>Descripción del control:</strong><span>${d.control_descripcion || ''}</span></div>
                    <div class="detalle-item"><strong>Seguimiento del control:</strong><span>${d.control_seguimiento || ''}</span></div>
                    <div class="detalle-item"><strong>Fecha de Revisión del control:</strong><span>${d.control_fecha_revision || ''}</span></div>
                    <div class="detalle-item"><strong>Probabilidad Residual:</strong><span>${d.probabilidad_residual || ''}</span></div>
                    <div class="detalle-item"><strong>Impacto Residual:</strong><span>${d.impacto_residual || ''}</span></div>
                    <div class="detalle-item"><strong>Riesgo Residual:</strong><span>${d.total_riesgo_residual || ''}</span></div>
                    <div class="detalle-item"><strong>Plan de Acción:</strong><span>${d.tratamiento_plan_accion || ''}</span></div>
                    <div class="detalle-item"><strong>Fecha de Implementación:</strong><span>${d.tratamiento_fecha_implementacion || ''}</span></div>
                    <div class="detalle-item"><strong>Responsable del Tratamiento:</strong><span>${d.tratamiento_responsable || ''}</span></div>
                    <div class="detalle-item"><strong>Descripción del Seguimiento:</strong><span>${d.seguimiento_descripcion || ''}</span></div>
                    <div class="detalle-item"><strong>Fecha del Seguimiento:</strong><span>${d.seguimiento_fecha || ''}</span></div>
                </div>
            </td>
        </tr>
    `;
}
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
    // Estilos globales en CSS; solo aseguramos el toggle del ícono
    if (!document.getElementById('riesgos-toggle-style')) {
        const style = document.createElement('style');
        style.id = 'riesgos-toggle-style';
        style.textContent = `.toggle-icon { display: inline-block; transition: transform .2s ease; } .fila-principal.expanded .toggle-icon { transform: rotate(45deg); }`;
        document.head.appendChild(style);
    }
    
})