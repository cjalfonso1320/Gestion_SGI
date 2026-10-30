document.addEventListener('DOMContentLoaded', function () {
    function getBaseUrl() { return (typeof BASE_URL !== 'undefined' && BASE_URL) ? BASE_URL : (window.BASE_URL || ''); }
    const searchInput = document.getElementById('searchInput');
    const docAccordion = document.querySelector('.doc-accordion');



    // ==========================================
    // 1. LÓGICA DE APERTURA/CIERRE (TOGGLE)
    // ==========================================
    docAccordion.addEventListener('click', function (e) {
        // Detectamos si se hizo clic en una sección, subsección o sub-subsección
        const header = e.target.closest('.doc-section, .doc-subsection, .doc-subsubsection');

        if (header) {
            e.preventDefault();

            // Alternamos la clase active para el estilo visual
            header.classList.toggle('active');

            // Buscamos el contenido que es el hermano siguiente
            const content = header.nextElementSibling;

            if (content) {
                // Si está oculto lo mostramos, si no lo ocultamos
                const isHidden = window.getComputedStyle(content).display === 'none';
                if (isHidden) {
                    content.style.display = 'block';
                    // Pequeña animación de entrada
                    content.style.opacity = '0';
                    setTimeout(function() {
                        content.style.opacity = '1';
                        content.style.transition = 'opacity 0.3s';
                    }, 10);
                } else {
                    content.style.display = 'none';
                }
            }

            // Cerrar hermanos del MISMO nivel (doc-section, doc-subsection, etc.)
            const parentContainer = header.parentElement;
            const miClase = header.classList[0];

            Array.from(parentContainer.children).forEach(function(child) {
                if (child !== header && child.classList.contains(miClase)) {
                    child.classList.remove('active');
                    const siblingContent = child.nextElementSibling;
                    if (siblingContent && (siblingContent.classList.contains('doc-content') || 
                        siblingContent.classList.contains('doc-subcontent') || 
                        siblingContent.classList.contains('doc-subsubcontent'))) {
                        siblingContent.style.display = 'none';
                    }
                }
            });
        }
    });

    // ==========================================
    // 2. LÓGICA DE BÚSQUEDA (FILTRADO)
    // ==========================================
    function filterDocuments() {
        const searchTerm = searchInput.value.toLowerCase().trim();
        const items = docAccordion.querySelectorAll('.filterable-item');

        items.forEach(item => {
            const itemText = item.textContent.toLowerCase();
            if (itemText.includes(searchTerm)) {
                item.style.display = '';
            } else {
                item.style.display = 'none';
            }
        });

        // Si hay búsqueda, actualizamos visibilidad de carpetas
        updateSectionVisibility(searchTerm !== "");
    }

    function updateSectionVisibility(isSearching) {
        const allSections = docAccordion.querySelectorAll('.doc-section, .doc-subsection, .doc-subsubsection');

        allSections.forEach(section => {
            const content = section.nextElementSibling;

            if (content) {
                const hasVisibleItems = content.querySelector('.filterable-item:not([style*="display: none"])');

                if (hasVisibleItems) {
                    section.style.display = ''; // Mostrar encabezado
                    // Si estamos buscando, abrimos automáticamente las secciones con resultados
                    if (isSearching) {
                        section.classList.add('active');
                        content.style.display = 'block';
                    }
                } else {
                    // Si no hay resultados y estamos buscando, ocultamos la sección
                    if (isSearching) {
                        section.style.display = 'none';
                    } else {
                        // Si no estamos buscando, volvemos al estado normal (visible)
                        section.style.display = '';
                    }
                }
            }
        });
    }

    if (searchInput) {
        searchInput.addEventListener('input', filterDocuments);
    }

    // ==========================================
    // 3. LÓGICA DEL MODAL DE CARGA
    // ==========================================
    const modal = document.getElementById('uploadModal');
    const uploadForm = document.getElementById('uploadForm');

    // Función para abrir el modal
    window.openUploadModal = function () {
        modal.classList.add('active');
    }

    // Función para cerrar el modal
    window.closeUploadModal = function () {
        modal.classList.remove('active');
        uploadForm.reset(); // Limpia el formulario al cerrar
    }

    // Abre el modal de subida con una carpeta preseleccionada
    window.openUploadModalWithCarpeta = function (carpeta) {
        document.getElementById('carpeta').value = carpeta;
        modal.classList.add('active');
    }

    // Stub para closeReplaceModal (el modal replaceModal queda como markup inactivo;
    // los reemplazos se manejan via enviarDocumento() con confirm() nativo)
    window.closeReplaceModal = function () {
        document.getElementById('replaceModal').classList.remove('active');
    }

    // Cerrar el modal si el usuario hace clic fuera de la caja blanca
    window.onclick = function (event) {
        if (event.target == modal) {
            closeUploadModal();
        }
    }

    function enviarDocumento(replace = false) {
        const formElement = document.getElementById('uploadForm');
        const formData = new FormData(formElement);

        if (replace) {
            formData.append('replace', 'true');
        }


        fetch(`${getBaseUrl()}/documentacion/subir`, {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    Swal.fire({
                        icon: 'succes',
                        title: 'Logrado',
                        text: data.message,
                        confirmButtonColor: '#3085d6'
                    }).then(() => {
                        closeUploadModal();
                    location.reload();
                    });                    
                } else {
                    if (data.exists) {
                        const confirmar = confirm("El archivo ya existe. ¿Deseas reemplazarlo?");
                        if (confirmar) {
                            enviarDocumento(true); // Llamada recursiva para reemplazar
                        }
                    } else {
                        alert("Error: " + data.message);
                    }
                }
            })
            .catch(error => { // <--- CORREGIDO AQUÍ (.catch en lugar de .cath)
                console.error('Error:', error);
                alert("Ocurrió un error al subir el documento");
            });
    }
    // Manejar el envío del formulario
    if (uploadForm) {
        uploadForm.addEventListener('submit', function (e) {
            e.preventDefault();
            enviarDocumento(false); // Iniciamos el envío normal
        });
    }
});

// ==========================================
// 4. EDITOR DE EXCEL (SheetJS)
// ==========================================
let excelDataActual = null;      // Array de arrays (datos crudos)
let excelHeadersActual = [];     // Nombres de columnas
let excelRutaActual = '';      // URL del archivo en servidor (de url_for)
let excelNombreActual = '';      // Nombre del archivo
let excelNombreSheet = '';       // Nombre del sheet activo
let excelCarpetaActual = '';     // Carpeta para re-subir el archivo

function editarArchivo(rutaUrl, nombre, tipo, carpeta) {
    excelCarpetaActual = carpeta || '';
    if (tipo === '.xlsx' || tipo === '.xls') {
        editarExcel(rutaUrl, nombre);
    } else {
        editarPDF(rutaUrl, nombre);
    }
}

function editarPDF(rutaUrl, nombre) {
    // rutaUrl es la URL completa generada por url_for (endpoint /ver)
    Swal.fire({
        title: 'Editar PDF',
        html: `
            <p style="margin-bottom:16px;color:#475569;">
                <i class="fa-solid fa-download fs-icon icon-blue-500"></i>
                Para editar <strong>${nombre}</strong>:
            </p>
            <ol style="text-align:left;color:#334155;line-height:1.8;">
                <li>Descarga el archivo haciendo clic abajo</li>
                <li>Edítalo con tu editor de PDF local</li>
                <li>Vuelve a subirlo usando el botón <strong>Subir</strong> (⤴) para reemplazarlo</li>
            </ol>
        `,
        icon: 'info',
        confirmButtonText: '<i class="fa-solid fa-download"></i> Descargar PDF',
        confirmButtonColor: '#2563eb',
        showCancelButton: true,
        cancelButtonText: 'Cancelar',
        cancelButtonColor: '#64748b'
    }).then((result) => {
        if (result.isConfirmed) {
            window.open(rutaUrl, '_blank');
        }
    });
}

function editarExcel(rutaUrl, nombre) {
    excelRutaActual = rutaUrl;
    excelNombreActual = nombre;
    
    document.getElementById('excelEditorFileName').textContent = nombre;
    document.getElementById('excelEditorModal').classList.add('active');
    document.getElementById('excelEditorStatus').textContent = 'Descargando archivo...';
    
    // rutaUrl es la URL completa generada por url_for (endpoint /ver)
    fetch(rutaUrl)
        .then(res => {
            if (!res.ok) throw new Error('No se pudo descargar el archivo');
            return res.arrayBuffer();
        })
        .then(buffer => {
            const workbook = XLSX.read(buffer, { type: 'array' });
            excelNombreSheet = workbook.SheetNames[0];
            const sheet = workbook.Sheets[excelNombreSheet];
            const data = XLSX.utils.sheet_to_json(sheet, { header: 1 });
            
            if (data.length === 0) {
                // Hoja vacía: crear estructura por defecto
                excelHeadersActual = ['Columna 1'];
                excelDataActual = [['']];
            } else {
                excelHeadersActual = data[0];
                excelDataActual = data.slice(1);
            }
            
            renderizarTablaExcel();
            document.getElementById('excelEditorStatus').textContent = 
                `${excelDataActual.length} filas × ${excelHeadersActual.length} columnas`;
        })
        .catch(err => {
            console.error('Error al cargar Excel:', err);
            document.getElementById('excelEditorStatus').textContent = 'Error al cargar';
            Swal.fire('Error', 'No se pudo cargar el archivo Excel: ' + err.message, 'error');
        });
}

function renderizarTablaExcel() {
    const head = document.getElementById('excelEditorHead');
    const body = document.getElementById('excelEditorBody');
    
    // Renderizar headers
    head.innerHTML = '<tr>' + excelHeadersActual.map((h, ci) => 
        `<th style="border:1px solid #cbd5e1;padding:6px 10px;background:#f1f5f9;color:#334155;font-weight:600;text-align:left;min-width:100px;">
            <input value="${escapeHtml(h)}" 
                   onchange="cambiarHeaderExcel(${ci}, this.value)"
                   class="fs-sm" style="width:100%;border:none;background:transparent;font-weight:600;outline:none;">
        </th>`
    ).join('') + '</tr>';
    
    // Renderizar filas
    body.innerHTML = excelDataActual.map((row, ri) => 
        '<tr>' + excelHeadersActual.map((_, ci) => 
            `<td style="border:1px solid #e2e8f0;padding:4px 8px;">
                <input value="${escapeHtml(row[ci] !== undefined && row[ci] !== null ? String(row[ci]) : '')}"
                       onchange="cambiarCeldaExcel(${ri}, ${ci}, this.value)"
                       class="fs-sm" style="width:100%;border:none;background:transparent;outline:none;
                              ${ci === 0 ? 'font-weight:500;' : ''}">
            </td>`
        ).join('') + 
        `<td style="border:1px solid #e2e8f0;padding:4px 8px;width:32px;text-align:center;">
            <button onclick="eliminarFilaExcel(${ri})" style="border:none;background:none;color:#ef4444;cursor:pointer;" title="Eliminar fila">
                <i class="fa-solid fa-xmark"></i>
            </button>
        </td>`
    ).join('') + '</tr>';
}

function escapeHtml(text) {
    return String(text ?? '')
        .replace(/&/g, '&amp;')
        .replace(/"/g, '&quot;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
}

function cambiarHeaderExcel(index, value) {
    excelHeadersActual[index] = value;
}

function cambiarCeldaExcel(ri, ci, value) {
    if (!excelDataActual[ri]) excelDataActual[ri] = [];
    excelDataActual[ri][ci] = value;
}

function agregarFilaExcel() {
    excelDataActual.push(excelHeadersActual.map(() => ''));
    renderizarTablaExcel();
    actualizarEstadoExcel();
}

function agregarColumnaExcel() {
    excelHeadersActual.push('Columna ' + (excelHeadersActual.length + 1));
    excelDataActual.forEach(row => row.push(''));
    renderizarTablaExcel();
    actualizarEstadoExcel();
}

function eliminarFilaExcel(index) {
    excelDataActual.splice(index, 1);
    renderizarTablaExcel();
    actualizarEstadoExcel();
}

function actualizarEstadoExcel() {
    document.getElementById('excelEditorStatus').textContent = 
        `${excelDataActual.length} filas × ${excelHeadersActual.length} columnas`;
}

function cerrarEditorExcel() {
    document.getElementById('excelEditorModal').classList.remove('active');
    excelDataActual = null;
    excelHeadersActual = [];
    excelRutaActual = '';
    excelNombreActual = '';
}

function guardarExcelEditado() {
    if (!excelDataActual || !excelHeadersActual.length) {
        Swal.fire('Sin datos', 'No hay datos para guardar', 'warning');
        return;
    }
    
    Swal.fire({
        title: 'Guardando...',
        text: 'Generando archivo Excel...',
        allowOutsideClick: false,
        didOpen: () => Swal.showLoading()
    });
    
    try {
        // Construir la hoja de datos
        const datosCompletos = [excelHeadersActual, ...excelDataActual];
        const ws = XLSX.utils.aoa_to_sheet(datosCompletos);
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, excelNombreSheet || 'Datos');
        
        // Generar el archivo como blob
        const wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });
        const blob = new Blob([wbout], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
        
        // Enviar al servidor
        const formData = new FormData();
        formData.append('documento', blob, excelNombreActual);
        formData.append('carpeta', excelCarpetaActual);
        formData.append('replace', 'true');
        
        const baseUrl = (typeof BASE_URL !== 'undefined' && BASE_URL) ? BASE_URL : (window.BASE_URL || '');
        
        fetch(baseUrl + '/documentacion/subir', {
            method: 'POST',
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                Swal.fire({
                    icon: 'success',
                    title: 'Guardado',
                    text: 'Archivo Excel actualizado correctamente',
                    confirmButtonColor: '#3085d6'
                }).then(() => {
                    cerrarEditorExcel();
                    location.reload();
                });
            } else {
                throw new Error(data.message || 'Error al guardar');
            }
        })
        .catch(err => {
            Swal.fire('Error', 'No se pudo guardar: ' + err.message, 'error');
        });
        
    } catch (err) {
        Swal.fire('Error', 'Error al generar el Excel: ' + err.message, 'error');
    }
}

// ==========================================
// 5. CERRAR MODAL EDITOR EXCEL CON CLICK FUERA
// ==========================================
window.addEventListener('click', function(event) {
    const modal = document.getElementById('excelEditorModal');
    if (event.target === modal) {
        cerrarEditorExcel();
    }
});

