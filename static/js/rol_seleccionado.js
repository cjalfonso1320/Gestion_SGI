function getAppBasePath() {
    const firstSegment = window.location.pathname.split('/').filter(Boolean)[0] || '';
    const appRoutes = new Set([
        'control',
        'documentacion',
        'indicadores',
        'Matriz_Activos',
        'Matriz_Riesgos'
    ]);

    return firstSegment && !appRoutes.has(firstSegment) ? `/${firstSegment}` : '';
}

function limpiarRolSeleccionado() {
    // 1. Confirmación con SweetAlert
    Swal.fire({
        title: '¿Estás seguro?',
        text: "Se limpiará el rol seleccionado y volverás a tu rol por defecto.",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#2563eb', // Azul acorde a tu tema
        cancelButtonColor: '#64748b',
        confirmButtonText: 'Sí, volver al inicio',
        cancelButtonText: 'Cancelar',
        reverseButtons: true
    }).then((result) => {
        if (result.isConfirmed) {
            
            // Mostrar un loading mientras se procesa
            Swal.fire({
                title: 'Procesando...',
                allowOutsideClick: false,
                didOpen: () => {
                    Swal.showLoading();
                }
            });

            // 2. Ejecutar el Fetch
            fetch(`${getAppBasePath()}/limpiar_rol_seleccionado`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Éxito: Notificar brevemente y recargar
                    Swal.fire({
                        icon: 'success',
                        title: 'Rol restablecido',
                        text: 'Redirigiendo...',
                        timer: 1500,
                        showConfirmButton: false
                    }).then(() => {
                        window.location.reload();
                    });
                } else {
                    // Error desde el servidor
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: data.message || data.error || 'Error al limpiar el rol seleccionado'
                    });
                }
            })
            .catch(error => {
                console.error('Error:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Error de conexión',
                    text: 'No se pudo comunicar con el servidor.'
                });
            });
        }
    });
}