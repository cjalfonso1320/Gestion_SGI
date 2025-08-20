document.addEventListener('DOMContentLoaded', function() {
    
    // =================================================================================
    // 1. FUNCIONES AUXILIARES (Tus funciones de alertas y estilos, sin cambios)
    // =================================================================================

    // Función para mostrar mensajes de éxito/error (Tu código, está perfecto)
    function showMessage(message, isSuccess = true) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `alert ${isSuccess ? 'alert-success' : 'alert-danger'}`;
        messageDiv.style.cssText = `
            position: fixed; top: 20px; right: 20px; z-index: 9999;
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
            setTimeout(() => {
                if (messageDiv.parentNode) {
                    messageDiv.parentNode.removeChild(messageDiv);
                }
            }, 300);
        }, 5000);
    }

    // Estilos CSS para las animaciones (Tu código, está perfecto)
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
        @keyframes slideOutRight { from { transform: translateX(0); opacity: 1; } to { transform: translateX(100%); opacity: 0; } }
    `;
    document.head.appendChild(style);


    // =================================================================================
    // 2. MANEJADOR DE FORMULARIOS GENÉRICO Y ACTUALIZADORES DE UI
    // =================================================================================

    /**
     * Función genérica para manejar el envío de formularios con AJAX.
     * @param {HTMLFormElement} form - El formulario a manejar.
     * @param {string} endpoint - La URL a la que se enviarán los datos.
     * @param {function} successCallback - La función que se ejecutará en caso de éxito para actualizar la UI.
     */
    function handleFormSubmit(form, endpoint, successCallback) {
        if (form.dataset.listenerAttached) return;
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Guardando...';
            submitBtn.disabled = true;
            
            const formData = new FormData(form);
            
            fetch(endpoint, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showMessage(data.message, true);
                    // Llama a la función específica para actualizar la tabla y la gráfica
                    if (successCallback) {
                        successCallback(data, form);
                    }
                    form.reset();
                    // Limpia campos 'readonly' que .reset() no afecta
                    form.querySelectorAll('input[readonly]').forEach(input => input.value = '');
                } else {
                    showMessage(data.message, false);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showMessage('Error de comunicación al guardar el indicador.', false);
            })
            .finally(() => {
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            });
        });
    }

    /**
     * Actualizador de UI específico para los indicadores de "Entrega Físicos".
     * @param {object} data - Los datos recibidos del servidor.
     */
    const updateUiEntregaFisicos = (data) => {
    try {
        const newData = data.newData;
        // Obtenemos el 'proceso' de los datos devueltos para encontrar el elemento correcto
        const proceso = newData.proceso;

        // 1. Actualizar la tabla
        // El ID de la tabla es dinámico, por eso necesitamos la variable 'proceso'
        const tablaBody = document.getElementById(`tabla_entrega_fisicos_body_${proceso}`);
        if (tablaBody) {
            const newRow = tablaBody.insertRow(0); // Añadir la fila al principio
            newRow.innerHTML = `
                <td>${newData.mes}</td>
                <td>${newData.documentos_entregados}</td>
                <td>${newData.documentos_extemporaneos}</td>
                <td>${newData.resultado}</td>
                <td>${newData.meta}</td>
                <td>${newData.analisis}</td>
            `;
        } else {
            console.error(`Error: No se encontró el body de la tabla con id 'tabla_entrega_fisicos_body_${proceso}'`);
        }
        
        // 2. Actualizar la gráfica
        // El nombre de la variable de la gráfica también es dinámico
        const chart = window[`grafica_entregaFisicos_${proceso}`];
        if (chart) {
            chart.data.labels.push(newData.mes);
            chart.data.datasets[0].data.push(parseFloat(newData.resultado));
            chart.update();
        } else {
            console.error(`Error: No se encontró la variable global de la gráfica 'window.grafica_entrega_fisicos_${proceso}'`);
        }

    } catch (error) {
        console.error("¡Error dentro de updateUiEntregaFisicos!:", error);
        throw error;
    }
};

    /**
     * Actualizador de UI específico para los indicadores de "Sanciones MAgneticas".
     * @param {object} data - Los datos recibidos del servidor.
     */
    const updateUiSancionesMagneticas = (data) => {
    try {
        const newData = data.newData;
        const tablaBody = document.getElementById('tabla_sancionesMagneticas_body');
        if (tablaBody) {
            const newRow = tablaBody.insertRow(0);
            // Leemos las claves específicas para Magnéticas
            newRow.innerHTML = `
                <td>${newData.mes}</td>
                <td>${newData.R_extemporaneos}</td>
                <td>${newData.r_digicom}</td>
                <td>${newData.meta}</td>
                <td>$ ${newData.multa}</td>
                <td>${newData.analisis}</td>
            `;
        } else {
            console.error("Error: No se encontró el body de la tabla con id 'tabla_sancionesMagneticas_body'");
        }
        
        const chart = window.grafica_sancionesMagneticas;
        if (chart) {
            const valorMultaNumerico = parseFloat(String(newData.multa).replace(/[^0-9.-]+/g,""));
            
            chart.data.labels.push(newData.mes);
            chart.data.datasets[0].data.push(valorMultaNumerico);
            chart.update();
        } else {
            console.error("Error: No se encontró la gráfica 'window.grafica_sancionesMagneticas'");
        }

    } catch (error) {
        console.error("¡Error dentro de updateUiSancionesMagneticas!:", error);
        throw error;
    }
};
    /**
     * Actualizador de UI específico para los indicadores de "Sanciones Fisicas".
      * @param {object} data - Los datos recibidos del servidor.
 */
const updateUiSancionesFisicas = (data) => {
    try {
       const newData = data.newData;

        // Para depurar: Muestra en la consola exactamente lo que el servidor envió.
        console.log("Datos recibidos para actualizar la tabla de Físicos:", newData);

        const tablaBody = document.getElementById('tabla_sancionesFisicos_body');
        if (tablaBody) {
            const newRow = tablaBody.insertRow(0); // Añade la fila al principio
            
            // VERSIÓN FINAL Y CORREGIDA: Usa las claves EXACTAS del diccionario de Python
            newRow.innerHTML = `
                <td>${newData.mes}</td>
                <td>${newData.D_extemporaneos2}</td>
                <td>${newData.dr_digicom}</td>
                <td>${newData.meta_sancionesFisicos}</td>
                <td>$ ${newData.multa_sancionesFisicos}</td>
                <td>${newData.analisis_sancionesFisicos}</td>
            `;
        } else {
            console.error("Error: No se encontró el body de la tabla con id 'tabla_sancionesFisicas_body'");
        }
        
        const chart = window.grafica_sancionesFisicos;
        if (chart) {
            const valorMultaNumerico = parseFloat(String(newData.multa_sancionesFisicos).replace(/[^0-9.-]+/g,""));
            
            chart.data.labels.push(newData.mes);
            chart.data.datasets[0].data.push(valorMultaNumerico);
            chart.update();
        } else {
            console.error("Error: No se encontró la gráfica 'window.grafica_sancionesFisicos'");
        }

    } catch (error) {
        console.error("¡Error dentro de updateUiSancionesFisicas!:", error);
        throw error;
    }
};
    
 /**
     * Actualizador de UI específico para los indicadores de "Entrega Físicos".
     * @param {object} data - Los datos recibidos del servidor.
     */
    const updateUiPasivo = (data) => {
    try {
        const newData = data.newData;
        // Obtenemos el 'proceso' de los datos devueltos para encontrar el elemento correcto
        const proceso = newData.proceso;

        // 1. Actualizar la tabla
        // El ID de la tabla es dinámico, por eso necesitamos la variable 'proceso'
        const tablaBody = document.getElementById(`tabla_inconsistencia_body_${proceso}`);
        if (tablaBody) {
            const newRow = tablaBody.insertRow(0); // Añadir la fila al principio
            newRow.innerHTML = `
                <td>${newData.mes}</td>
                <td>${newData.t_casos}</td>
                <td>${newData.e_grabacion_analisis}</td>
                <td>${newData.resultado}</td>
                <td>${newData.meta}</td>
                <td>${newData.analisis}</td>
            `;
        } else {
            console.error(`Error: No se encontró el body de la tabla con id 'tabla_inconsistencia_body_${proceso}'`);
        }
        
        // 2. Actualizar la gráfica
        // El nombre de la variable de la gráfica también es dinámico
        const chart = window[`grafica_inconsistenciasPasivo_${proceso}`];
        if (chart) {
            chart.data.labels.push(newData.mes);
            chart.data.datasets[0].data.push(parseFloat(newData.resultado));
            chart.update();
        } else {
            console.error(`Error: No se encontró la variable global de la gráfica 'window.grafica_inconsistenciasPasivo_${proceso}'`);
        }

    } catch (error) {
        console.error("¡Error dentro de updateUiPasivo!:", error);
        throw error;
    }
};

 /**
     * Actualizador de UI específico para los indicadores de "Entrega Físicos".
     * @param {object} data - Los datos recibidos del servidor.
     */
    const updateUiRespuestaCredito = (data) => {
    try {
        const newData = data.newData;
        // Obtenemos el 'proceso' de los datos devueltos para encontrar el elemento correcto
        const proceso = newData.proceso;

        // 1. Actualizar la tabla
        // El ID de la tabla es dinámico, por eso necesitamos la variable 'proceso'
        const tablaBody = document.getElementById(`tabla_RespuestaCredito_body_${proceso}`);
        if (tablaBody) {
            const newRow = tablaBody.insertRow(0); // Añadir la fila al principio
            newRow.innerHTML = `
                <td>${newData.mes}</td>
                <td>${newData.t_creditos}</td>
                <td>${newData.t_respuesta}</td>
                <td>${newData.resultado}</td>
                <td>${newData.analisis}</td>
            `;
        } else {
            console.error(`Error: No se encontró el body de la tabla con id 'tabla_RespuestaCredito_body_${proceso}'`);
        }
        
        // 2. Actualizar la gráfica
        // El nombre de la variable de la gráfica también es dinámico
        const chart = window[`grafica_TRespuesta_${proceso}`];
        if (chart) {
            chart.data.labels.push(newData.mes);
            chart.data.datasets[0].data.push(parseFloat(newData.resultado));
            chart.update();
        } else {
            console.error(`Error: No se encontró la variable global de la gráfica 'window.grafica_TRespuesta_${proceso}'`);
        }

    } catch (error) {
        console.error("¡Error dentro de updateUiRespuestaCredito!:", error);
        throw error;
    }
};

    // --- ¡AQUÍ PUEDES AÑADIR MÁS FUNCIONES "updateUi..." PARA OTROS INDICADORES! ---
    // Ejemplo:
    // const updateUiCalidadInformacion = (data) => { ... lógica para actualizar tabla y gráfica de calidad ... }


    // =================================================================================
    // 3. INICIALIZACIÓN (Conectar los formularios con sus manejadores y actualizadores)
    // =================================================================================

    // Usamos selectores de atributos para encontrar todos los formularios de un tipo.
    
    // Indicador: Entrega Físicos
    document.querySelectorAll('form[id^="form_entrega_fisicos_"]').forEach(form => {
        const endpoint = '/guardar_entrega_fisicos'; // O podrías leerlo de form.getAttribute('action')
        handleFormSubmit(form, endpoint, updateUiEntregaFisicos);
    });

    // Indicador: Sanciones Magneticas
    document.querySelectorAll('form[id^="form_sanciones"]').forEach(form => {
    let endpoint = '';
    let updateCallback = null;

    // Decidimos qué hacer basándonos en el ID del propio formulario.
    // Esto es más robusto que depender del valor de un input oculto.
    if (form.id.includes('Fisicos')) {
        endpoint = '/guardar_sanciones_fisicos';
        updateCallback = updateUiSancionesFisicas;
    } else if (form.id.includes('Magneticas')) {
        endpoint = '/guardar_sanciones_magneticas';
        updateCallback = updateUiSancionesMagneticas;
    }

    // Solo añadimos el manejador si encontramos un endpoint válido
    if (endpoint) {
        handleFormSubmit(form, endpoint, updateCallback);
    }
});
// Indicador: Inconsistencias Pasivo y Activo Complementacion Avvillñas
    document.querySelectorAll('form[id^="form_incon_"]').forEach(form => {
        const endpoint = '/guardar_inconsistencias_pasivo'; // O podrías leerlo de form.getAttribute('action')
        handleFormSubmit(form, endpoint, updateUiPasivo);
    });
    
    // Indicador: Tiempo de respuesta credito Complementacion Avvillñas
    document.querySelectorAll('form[id^="form_tiempoCredito_"]').forEach(form => {
        const endpoint = '/guardar_TRespuesta_Credito'; // O podrías leerlo de form.getAttribute('action')
        handleFormSubmit(form, endpoint, updateUiRespuestaCredito);
    });
    

});