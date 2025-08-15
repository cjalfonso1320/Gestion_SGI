$(function () {
  // Primer nivel
  $(".doc-accordion .doc-section").click(function () {
    const content = $(this).next(".doc-content");
    $(".doc-accordion .doc-content").not(content).slideUp();
    $(".doc-accordion .doc-subcontent").slideUp();
    content.slideToggle();
  });

  // Segundo nivel
  $(".doc-accordion .doc-subsection").click(function () {
    const subcontent = $(this).next(".doc-subcontent");
    $(this).siblings(".doc-subcontent").not(subcontent).slideUp();
    subcontent.slideToggle();
  });

  // Tercer nivel
  $(".doc-accordion .doc-subsubsection").click(function () {
    const subsub = $(this).next(".doc-subsubcontent");

    // Cierra otros del mismo nivel
    $(this).siblings(".doc-subsubcontent").not(subsub).slideUp();
    subsub.slideToggle();
  });

    $(function () {
    // Primer nivel
    $(".sst-accordion .sst-section").click(function () {
      const content = $(this).next(".sst-content");
      $(".sst-accordion .sst-content").not(content).slideUp();
      $(".sst-accordion .sst-subcontent").slideUp();
      content.slideToggle();
    });

    // Segundo nivel
    $(".sst-accordion .sst-subsection").click(function () {
      const subcontent = $(this).next(".sst-subcontent");
      $(this).siblings(".sst-subcontent").not(subcontent).slideUp();
      subcontent.slideToggle();
    });
  });
});

// Variables globales para el manejo de archivos
let currentFile = null;
let currentCarpeta = null;
let shouldReplace = false;

// Funciones para el modal de subida
function openUploadModal() {
    document.getElementById('uploadModal').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function openUploadModalWithCarpeta(carpeta) {
    document.getElementById('carpeta').value = carpeta;
    document.getElementById('uploadModal').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function closeUploadModal() {
    document.getElementById('uploadModal').style.display = 'none';
    document.body.style.overflow = 'auto';
    // Limpiar formulario
    document.getElementById('uploadForm').reset();
    currentFile = null;
    currentCarpeta = null;
    shouldReplace = false;
}

function closeReplaceModal() {
    document.getElementById('replaceModal').style.display = 'none';
    document.body.style.overflow = 'auto';
}

function confirmReplace() {
    shouldReplace = true;
    closeReplaceModal();
    uploadFile();
}

// Función para subir archivo
function uploadFile() {
    if (!currentFile || !currentCarpeta) {
        alert('Por favor seleccione un archivo y una carpeta');
        return;
    }

    const formData = new FormData();
    formData.append('documento', currentFile);
    formData.append('carpeta', currentCarpeta);
    formData.append('replace', shouldReplace);

    // Mostrar indicador de carga
    const submitBtn = document.querySelector('#uploadForm button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Subiendo...';
    submitBtn.disabled = true;

    fetch('/documentacion/subir', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Documento subido exitosamente');
            closeUploadModal();
            // Recargar la página para mostrar el nuevo documento
            location.reload();
        } else {
            if (data.exists) {
                // Mostrar modal de confirmación para reemplazar
                document.getElementById('existingFileName').textContent = currentFile.name;
                document.getElementById('replaceModal').style.display = 'block';
                document.body.style.overflow = 'hidden';
            } else {
                alert('Error: ' + data.message);
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al subir el documento');
    })
    .finally(() => {
        // Restaurar botón
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    });
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Formulario de subida
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const carpeta = document.getElementById('carpeta').value;
            const fileInput = document.getElementById('documento');
            
            if (!carpeta) {
                alert('Por favor seleccione una carpeta');
                return;
            }
            
            if (!fileInput.files[0]) {
                alert('Por favor seleccione un archivo');
                return;
            }
            
            currentFile = fileInput.files[0];
            currentCarpeta = carpeta;
            shouldReplace = false;
            
            uploadFile();
        });
    }

    // Cerrar modales al hacer clic fuera de ellos
    window.addEventListener('click', function(e) {
        const uploadModal = document.getElementById('uploadModal');
        const replaceModal = document.getElementById('replaceModal');
        
        if (e.target === uploadModal) {
            closeUploadModal();
        }
        
        if (e.target === replaceModal) {
            closeReplaceModal();
        }
    });

    // Cerrar modales con ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeUploadModal();
            closeReplaceModal();
        }
    });
});


