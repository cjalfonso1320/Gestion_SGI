/**
 * acordeon_doc.js — Acordeones de Documentación
 * 
 * NOTA: jQuery se carga DESDE home.html (CDN), que se ejecuta después
 * del contenido del bloque. Por eso usamos DOMContentLoaded + un
 * intervalo corto para esperar a que jQuery esté disponible.
 */
document.addEventListener('DOMContentLoaded', function() {
  // Esperar a que jQuery esté disponible (viene de home.html, después del bloque)
  var checkJQ = setInterval(function() {
    if (typeof jQuery === 'undefined') return;
    clearInterval(checkJQ);
    initAcordeones();
  }, 5);
});

function initAcordeones() {
  // ---- Acordeón DOC (principal) ----
  // Primer nivel
  $(".doc-accordion .doc-section").click(function() {
    var content = $(this).next(".doc-content");
    $(".doc-accordion .doc-content").not(content).slideUp();
    $(".doc-accordion .doc-subcontent").slideUp();
    content.slideToggle();
  });

  // Segundo nivel
  $(".doc-accordion .doc-subsection").click(function() {
    var subcontent = $(this).next(".doc-subcontent");
    $(this).siblings(".doc-subcontent").not(subcontent).slideUp();
    subcontent.slideToggle();
  });

  // Tercer nivel
  $(".doc-accordion .doc-subsubsection").click(function() {
    var subsub = $(this).next(".doc-subsubcontent");
    $(this).siblings(".doc-subsubcontent").not(subsub).slideUp();
    subsub.slideToggle();
  });

  // ---- Acordeón SST ----
  // Primer nivel
  $(".sst-accordion .sst-section").click(function() {
    var content = $(this).next(".sst-content");
    $(".sst-accordion .sst-content").not(content).slideUp();
    $(".sst-accordion .sst-subcontent").slideUp();
    content.slideToggle();
  });

  // Segundo nivel
  $(".sst-accordion .sst-subsection").click(function() {
    var subcontent = $(this).next(".sst-subcontent");
    $(this).siblings(".sst-subcontent").not(subcontent).slideUp();
    subcontent.slideToggle();
  });
}

// ============================================================
// FUNCIONES GLOBALES (modales de subida / reemplazo)
// Se mantienen tal cual porque no dependen de jQuery.
// ============================================================

var currentFile = null;
var currentCarpeta = null;
var shouldReplace = false;

function openUploadModal() {
  document.getElementById('uploadModal').classList.add('active');
  document.body.style.overflow = 'hidden';
}

function openUploadModalWithCarpeta(carpeta) {
  document.getElementById('carpeta').value = carpeta;
  document.getElementById('uploadModal').classList.add('active');
  document.body.style.overflow = 'hidden';
}

function closeUploadModal() {
  document.getElementById('uploadModal').classList.remove('active');
  document.body.style.overflow = 'auto';
  document.getElementById('uploadForm').reset();
  currentFile = null;
  currentCarpeta = null;
  shouldReplace = false;
}

function closeReplaceModal() {
  document.getElementById('replaceModal').classList.remove('active');
  document.body.style.overflow = 'auto';
}

function confirmReplace() {
  shouldReplace = true;
  closeReplaceModal();
  uploadFile();
}

function uploadFile() {
  if (!currentFile || !currentCarpeta) {
    Swal.fire('Advertencia', 'Por favor seleccione un archivo y una carpeta', 'warning');
    return;
  }

  var formData = new FormData();
  formData.append('documento', currentFile);
  formData.append('carpeta', currentCarpeta);
  formData.append('replace', shouldReplace);

  var submitBtn = document.querySelector('#uploadForm button[type="submit"]');
  var originalText = submitBtn.textContent;
  submitBtn.textContent = 'Subiendo...';
  submitBtn.disabled = true;

  fetch((window.BASE_URL || '') + '/documentacion/subir', {
    method: 'POST',
    body: formData
  })
    .then(function(response) { return response.json(); })
    .then(function(data) {
      if (data.success) {
        Swal.fire('Éxito', 'Documento subido exitosamente', 'success');
        closeUploadModal();
        location.reload();
      } else {
        if (data.exists) {
          document.getElementById('existingFileName').textContent = currentFile.name;
          document.getElementById('replaceModal').classList.add('active');
          document.body.style.overflow = 'hidden';
        } else {
          Swal.fire('Error', 'Error: ' + data.message, 'error');
        }
      }
    })
    .catch(function(error) {
      console.error('Error:', error);
      Swal.fire('Error', 'Error al subir el documento', 'error');
    })
    .finally(function() {
      submitBtn.textContent = originalText;
      submitBtn.disabled = false;
    });
}

// Event listeners para modales
document.addEventListener('DOMContentLoaded', function() {
  var uploadForm = document.getElementById('uploadForm');
  if (uploadForm) {
    uploadForm.addEventListener('submit', function(e) {
      e.preventDefault();
      var carpeta = document.getElementById('carpeta').value;
      var fileInput = document.getElementById('documento');

      if (!carpeta) {
        Swal.fire('Advertencia', 'Por favor seleccione una carpeta', 'warning');
        return;
      }
      if (!fileInput.files[0]) {
        Swal.fire('Advertencia', 'Por favor seleccione un archivo', 'warning');
        return;
      }

      currentFile = fileInput.files[0];
      currentCarpeta = carpeta;
      shouldReplace = false;
      uploadFile();
    });
  }

  window.addEventListener('click', function(e) {
    var uploadModal = document.getElementById('uploadModal');
    var replaceModal = document.getElementById('replaceModal');
    if (e.target === uploadModal) closeUploadModal();
    if (e.target === replaceModal) closeReplaceModal();
  });

  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      closeUploadModal();
      closeReplaceModal();
    }
  });
});
