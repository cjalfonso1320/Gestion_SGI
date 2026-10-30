// Funciones para manejar formularios de indicadores
document.addEventListener('DOMContentLoaded', function() {
    // Función para mostrar mensajes de éxito/error
    function showMessage(message, isSuccess = true) {
        // Crear elemento de mensaje
        const messageDiv = document.createElement('div');
        messageDiv.className = `alert ${isSuccess ? 'alert-success' : 'alert-danger'}`;
        messageDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            padding: 15px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 600;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            animation: slideInRight 0.3s ease;
            max-width: 400px;
            word-wrap: break-word;
        `;
        
        if (isSuccess) {
            messageDiv.style.background = 'linear-gradient(135deg, #28a745 0%, #20c997 100%)';
        } else {
            messageDiv.style.background = 'linear-gradient(135deg, #dc3545 0%, #c82333 100%)';
        }
        
        messageDiv.textContent = message;
        
        // Agregar al DOM
        document.body.appendChild(messageDiv);
        
        // Remover después de 5 segundos
        setTimeout(() => {
            messageDiv.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                if (messageDiv.parentNode) {
                    messageDiv.parentNode.removeChild(messageDiv);
                }
            }, 300);
        }, 5000);
    }
    
    // Función para manejar envío de formularios
    function handleFormSubmit(form, endpoint) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Mostrar indicador de carga
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Guardando...';
            submitBtn.disabled = true;
            
            // Crear FormData
            const formData = new FormData(form);
            
            // Enviar petición
            fetch(endpoint, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showMessage(data.message, true);
                    // Limpiar formulario si es exitoso
                    form.reset();
                    // Recargar la página después de un breve delay
                    setTimeout(() => {
                        location.reload();
                    }, 2000);
                } else {
                    showMessage(data.message, false);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showMessage('Error al guardar el indicador', false);
            })
            .finally(() => {
                // Restaurar botón
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            });
        });
    }
    
    // Aplicar a todos los formularios de indicadores
    const forms = document.querySelectorAll('form[action*="guardar"]');
    forms.forEach(form => {
        const action = form.getAttribute('action');
        if (action) {
            handleFormSubmit(form, action);
        }
    });
    
    // También manejar formularios que no tienen action pero sí un id específico
    const calidadInfoForm = document.getElementById('form-calidad-informacion');
    if (calidadInfoForm) {
        handleFormSubmit(calidadInfoForm, '/guardar_calidad_informacion');
    }
    
    const registrosMagneticosForm = document.getElementById('form-registros-magneticos');
    if (registrosMagneticosForm) {
        handleFormSubmit(registrosMagneticosForm, '/guardar_registros_magneticos');
    }
    
    const sancionesMagneticasForm = document.getElementById('form-sanciones-magneticas');
    if (sancionesMagneticasForm) {
        handleFormSubmit(sancionesMagneticasForm, '/guardar_sanciones_magneticas');
    }
    
    const sancionesFisicosForm = document.getElementById('form-sanciones-fisicos');
    if (sancionesFisicosForm) {
        handleFormSubmit(sancionesFisicosForm, '/guardar_sanciones_fisicos');
    }
    
    const entregaFisicosForm = document.getElementById('form-entrega-fisicos');
    if (entregaFisicosForm) {
        handleFormSubmit(entregaFisicosForm, '/guardar_entrega_fisicos');
    }
    
    const cintasMagneticasForm = document.getElementById('form-cintas-magneticas');
    if (cintasMagneticasForm) {
        handleFormSubmit(cintasMagneticasForm, '/guardar_cintas_magneticas');
    }
    
    const informesEntregadosForm = document.getElementById('form-informes-entregados');
    if (informesEntregadosForm) {
        handleFormSubmit(informesEntregadosForm, '/guardar_informes_entregados');
    }
    
    const sitioWebForm = document.getElementById('form-sitio-web');
    if (sitioWebForm) {
        handleFormSubmit(sitioWebForm, '/guardar_sitioWeb');
    }
    
    const calidadInformesForm = document.getElementById('form-calidad-informes');
    if (calidadInformesForm) {
        handleFormSubmit(calidadInformesForm, '/guardar_calidad_informes');
    }
    
    const entregaImagenesForm = document.getElementById('form-entrega-imagenes');
    if (entregaImagenesForm) {
        handleFormSubmit(entregaImagenesForm, '/guardar_entrega_imagenes');
    }
    
    const solucionInconsistenciasForm = document.getElementById('form-solucion-inconsistencias');
    if (solucionInconsistenciasForm) {
        handleFormSubmit(solucionInconsistenciasForm, '/guardar_solucion_inconsistencias');
    }
    
    const trasladosForm = document.getElementById('form-traslados');
    if (trasladosForm) {
        handleFormSubmit(trasladosForm, '/guardar_traslados');
    }
    
    const inconsistenciasPasivoForm = document.getElementById('form-inconsistencias-pasivo');
    if (inconsistenciasPasivoForm) {
        handleFormSubmit(inconsistenciasPasivoForm, '/guardar_inconsistencias_pasivo');
    }
    
    const tRespuestaCreditoForm = document.getElementById('form-trespuesta-credito');
    if (tRespuestaCreditoForm) {
        handleFormSubmit(tRespuestaCreditoForm, '/guardar_TRespuesta_Credito');
    }
    
    const transmisionAduanasForm = document.getElementById('form-transmision-aduanas');
    if (transmisionAduanasForm) {
        handleFormSubmit(transmisionAduanasForm, '/guardar_transmision_aduanas');
    }
    
    const administrativoForm = document.getElementById('form-administrativo');
    if (administrativoForm) {
        handleFormSubmit(administrativoForm, '/guardar_administrativo');
    }
});

// Estilos CSS para las animaciones
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
