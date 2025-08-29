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
            tablaBody.addEventListener('click', handleRowClick);
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
// ========================================================================
    // LÓGICA DE ENVÍO DE FORMULARIO Y ACTUALIZACIÓN DE UI
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
                    showMessage(data.message, true); // Llama a la función de alerta
                    if (successCallback) successCallback(data);
                    form.reset();
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

function updateUiRiesgos(data) {
    const tablaBody = document.getElementById('tabla_riesgos_body');
    if (!tablaBody) return;

    try {
        const newData = data.newData;
        const tempContainer = document.createElement('div');

        tempContainer.innerHTML = `
            <tr class="fila-principal" data-id="${newData.id}">
                <td><span class="toggle-icon">+</span></td>
                <td>${newData.nombre_riesgo || ''}</td>
                <td>${newData.nombre_activo || ''}</td>
                <td>${newData.criticidad_riesgo_inherente || ''}</td>
                <td>${newData.criticidad_riesgo_residual || ''}</td>
                <td>${newData.opciones_manejo || ''}</td>
            </tr>
            <tr class="fila-detalles">
                <td colspan="6">
                    <div class="detalles-contenido use-grid">
                        <div class="detalle-item"><strong>Proceso:</strong><span>${newData.proceso || ''}</span></div>
                        <div class="detalle-item"><strong>Tipo de Activo:</strong><span>${newData.tipo_activo || ''}</span></div>
                        <div class="detalle-item"><strong>Criticidad del Activo:</strong><span>${newData.criticidad_activo || ''}</span></div>
                        <div class="detalle-item"><strong>Amenaza:</strong><span>${newData.amenaza || ''}</span></div>
                        <div class="detalle-item"><strong>Vulnerabilidad:</strong><span>${newData.vulnerabilidad || ''}</span></div>
                        <div class="detalle-item"><strong>Descripción del Riesgo:</strong><span>${newData.descripcion_riesgo || ''}</span></div>
                        <div class="detalle-item"><strong>Tipo del Riesgo:</strong><span>${newData.tipo_riesgo || ''}</span></div>
                        <div class="detalle-item"><strong>Responsable del Riesgo:</strong><span>${newData.responsable_riesgo || ''}</span></div>
                        <div class="detalle-item"><strong>Norma:</strong><span>${newData.norma || ''}</span></div>
                        <div class="detalle-item"><strong>Probabilidad Inherente:</strong><span>${newData.probabilidad_inherente || ''}</span></div>
                        <div class="detalle-item"><strong>Impacto Inherente:</strong><span>${newData.impacto_inherente || ''}</span></div>
                        <div class="detalle-item"><strong>Total del Riesgo Inherente:</strong><span>${newData.total_riesgo_inherente || ''}</span></div>
                        <div class="detalle-item"><strong>Norma ISO:</strong><span>${newData.control_norma_iso || ''}</span></div>
                        <div class="detalle-item"><strong>Descripción del control:</strong><span>${newData.control_descripcion || ''}</span></div>
                        <div class="detalle-item"><strong>Seguimiento del control:</strong><span>${newData.control_seguimiento || ''}</span></div>
                        <div class="detalle-item"><strong>Fecha de Revisión del control:</strong><span>${newData.control_fecha_revision || ''}</span></div>
                        <div class="detalle-item"><strong>Probabilidad Residual:</strong><span>${newData.probabilidad_residual || ''}</span></div>
                        <div class="detalle-item"><strong>Impacto Residual:</strong><span>${newData.impacto_residual || ''}</span></div>
                        <div class="detalle-item"><strong>Riesgo Residual:</strong><span>${newData.total_riesgo_residual || ''}</span></div>
                        <div class="detalle-item"><strong>Plan de Acción:</strong><span>${newData.tratamiento_plan_accion || ''}</span></div>
                        <div class="detalle-item"><strong>Fecha de Implementación:</strong><span>${newData.tratamiento_fecha_implementacion || ''}</span></div>
                        <div class="detalle-item"><strong>Responsable del Tratamiento:</strong><span>${newData.tratamiento_responsable || ''}</span></div>
                        <div class="detalle-item"><strong>Descripción del Seguimiento:</strong><span>${newData.seguimiento_descripcion || ''}</span></div>
                        <div class="detalle-item"><strong>Fecha del Seguimiento:</strong><span>${newData.seguimiento_fecha || ''}</span></div>
                    </div>
                </td>
            </tr>
        `;
        
        tablaBody.prepend(tempContainer.children[1]); // Fila de detalles
        tablaBody.prepend(tempContainer.children[0]); // Fila principal
    } catch (error) {
        console.error("Error al actualizar la tabla:", error);
    }
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