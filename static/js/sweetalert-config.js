/**
 * Configuración global de SweetAlert2
 * Puedes personalizar estos valores según tus necesidades
 */

// Configuración por defecto de Swal
Swal.mixin({
    allowOutsideClick: false,
    allowEscapeKey: false,
    confirmButtonColor: '#3085d6',
    cancelButtonColor: '#d33',
}).settings;

// Funciones helper para uso rápido
const SwalAlert = {
    // Éxito
    success: (titulo, mensaje) => {
        return Swal.fire(titulo, mensaje, 'success');
    },
    
    // Error
    error: (titulo, mensaje) => {
        return Swal.fire(titulo, mensaje, 'error');
    },
    
    // Advertencia
    warning: (titulo, mensaje) => {
        return Swal.fire(titulo, mensaje, 'warning');
    },
    
    // Información
    info: (titulo, mensaje) => {
        return Swal.fire(titulo, mensaje, 'info');
    },
    
    // Pregunta de confirmación
    confirm: (titulo, mensaje) => {
        return Swal.fire({
            title: titulo,
            text: mensaje,
            icon: 'question',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Sí, continuar',
            cancelButtonText: 'Cancelar'
        });
    },
    
    // Cargando
    loading: (titulo, mensaje) => {
        return Swal.fire({
            title: titulo,
            text: mensaje,
            icon: 'info',
            allowOutsideClick: false,
            allowEscapeKey: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });
    }
};
