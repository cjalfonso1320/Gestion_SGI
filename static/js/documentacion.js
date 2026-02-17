document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const docAccordion = document.querySelector('.doc-accordion');

    // ==========================================
    // 1. LÓGICA DE APERTURA/CIERRE (TOGGLE)
    // ==========================================
    docAccordion.addEventListener('click', function(e) {
        // Detectamos si se hizo clic en una sección, subsección o sub-subsección
        const header = e.target.closest('.doc-section, .doc-subsection, .doc-subsubsection');
        
        if (header) {
            e.preventDefault();
            
            // Alternamos la clase active para el estilo CSS
            header.classList.toggle('active');
            
            // Buscamos el contenido que es el hermano siguiente
            const content = header.nextElementSibling;
            
            if (content) {
                // Si está oculto lo mostramos, si no lo ocultamos
                const isHidden = window.getComputedStyle(content).display === 'none';
                content.style.display = isHidden ? 'block' : 'none';
            }
            console.log("Sección de documentación conmutada");
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
});