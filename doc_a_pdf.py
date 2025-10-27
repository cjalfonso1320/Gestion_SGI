# NOMBRE SUGERIDO PARA EL ARCHIVO: convertir_docx.py

import os
import docx  # Para leer archivos .docx
import re
from bs4 import BeautifulSoup

# --- CONFIGURACIÓN ---
# Carpeta donde están tus archivos .docx
DOCX_FOLDER = r"C:\Users\cjalfonso\Desktop\proc"
# Carpeta donde se guardarán los HTMLs convertidos
HTML_FOLDER = r"C:\Users\cjalfonso\Desktop\codigos\GestionSGI\html"

# Se asegura de que la carpeta de destino exista
os.makedirs(HTML_FOLDER, exist_ok=True)


def convertir_docx_a_html(docx_path, html_path):
    """
    Función principal que toma una ruta a un .docx, extrae su texto,
    lo procesa para encontrar secciones y genera un archivo HTML.
    """
    base_name = os.path.basename(docx_path)
    doc_name_no_ext = os.path.splitext(base_name)[0]
    # Crea una ruta relativa para usar en la plantilla
    html_doc_path = os.path.join('procedimientos', 'HTML', os.path.basename(html_path)).replace('\\', '/')

    # 1. --- EXTRACCIÓN DE TEXTO DEL DOCUMENTO .DOCX ---
    try:
        doc = docx.Document(docx_path)
        all_text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        if not all_text:
            print("    ⚠️  El documento DOCX está vacío o no se pudo leer el texto.")
            return False
    except Exception as e:
        print(f"    ❌ Error al leer el archivo .docx: {e}")
        return False

    # 2. --- PROCESAMIENTO DEL TEXTO (Tu lógica original, sin cambios) ---
    sections = []
    current_section = None
    current_subsection = None
    current_subsubsection = None
    content_buffer = ""

    def escape_html(text):
        if not text:
            return ""
        cleaned_text = re.sub(r'[\s.]+$', '', text).strip()
        cleaned_text = re.sub(r'\s*\.{2,}.*$', '', cleaned_text).strip()
        cleaned_text = re.sub(r'^\d+\s*$', '', cleaned_text).strip()
        cleaned_text = cleaned_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        return cleaned_text

    def format_content(text):
        if not text or not text.strip():
            return ""
        text = text.strip()
        keywords = ["Responsable:", "Registro:", "Descripción:", "Nota:"]
        
        if any(keyword.lower() in text.lower() for keyword in keywords):
            list_html = "<ul>\n"
            pattern = r'(Responsable:|Registro:|Descripción:|Nota:)'
            parts = re.split(pattern, text, flags=re.IGNORECASE)
            for i in range(1, len(parts), 2):
                if i + 1 < len(parts):
                    keyword = parts[i]
                    content = parts[i + 1].strip()
                    if content:
                        list_html += f'                        <li>\n'
                        list_html += f'                            <i class="fa-regular fa-circle-check"></i>\n'
                        list_html += f'                            <b>{escape_html(keyword)}</b> {escape_html(content)}\n'
                        list_html += f'                        </li>\n'
            list_html += "                    </ul>"
            return list_html
        else:
            paragraphs = text.split('\n\n')
            html_content = ""
            for para in paragraphs:
                if para.strip():
                    html_content += f"                        <p>{escape_html(para.strip())}</p>\n"
            return html_content

    def detect_section_level(line):
        line = line.strip()
        if re.match(r'^\d+\.\s+[A-ZÁÉÍÓÚÑ\s]+', line, re.IGNORECASE):
            return 'section', line
        elif re.match(r'^\d+\.\d+\.?\s+', line):
            return 'subsection', line
        elif re.match(r'^\d+\.\d+\.\d+\.?\s+', line):
            return 'subsubsection', line
        elif re.match(r'^\d+\.\d+\.\d+\.\d+\.?\s+', line):
            return 'subsubsubsection', line
        return None, None

    def save_current_content():
        nonlocal content_buffer, current_subsubsection, current_subsection, current_section
        if content_buffer.strip():
            formatted = content_buffer.strip() # Ya formateado al agregar al buffer
            if current_subsubsection:
                current_subsubsection['content'] += formatted
            elif current_subsection:
                current_subsection['content'] += formatted
            elif current_section:
                current_section['content'] += formatted
            content_buffer = ""

    # Procesar el texto extraído línea por línea
    lines = all_text.split('\n')
    for line in lines:
        line = line.strip()
        if not line: continue
        
        if re.match(r"(C[OÓ]DIGO:|VERSI[OÓ]N:|P[ÁA]GINA|FECHA|USO INTERNO|COPIA CONTROLADA|CONFIDENCIAL|DIGICOM)", line, re.IGNORECASE) or \
           re.match(r"^\d+\s+de\s+\d+$", line):
            continue

        section_type, section_title = detect_section_level(line)

        if section_type:
            save_current_content()
            
            if section_type == 'section':
                if current_section: sections.append(current_section)
                current_section = {'number': section_title.split('.')[0], 'title': section_title, 'content': '', 'subsections': []}
                current_subsection = None
                current_subsubsection = None
            elif section_type == 'subsection' and current_section:
                if current_subsection: current_section['subsections'].append(current_subsection)
                current_subsection = {'title': section_title, 'content': '', 'subsubsections': []}
                current_subsubsection = None
            elif (section_type == 'subsubsection' or section_type == 'subsubsubsection') and current_subsection:
                if current_subsubsection: current_subsection['subsubsections'].append(current_subsubsection)
                current_subsubsection = {'title': section_title, 'content': ''}
        else:
            content_buffer += line + "\n"

    save_current_content()
    if current_subsubsection and current_subsection: current_subsection['subsubsections'].append(current_subsubsection)
    if current_subsection and current_section: current_section['subsections'].append(current_subsection)
    if current_section: sections.append(current_section)

    # 3. --- CONSTRUCCIÓN DEL HTML (Tu lógica original) ---
    def build_html_structure():
        # ... (Pega aquí tu función build_html_structure completa) ...
        # Por seguridad, la re-escribo aquí:
        html_content = '<div class="doc-accordion">\n\n'
        for section in sections:
            section_id = section['number']
            section_title = escape_html(section['title'])
            html_content += f'    <div class="doc-section" data-id="{section_id}">{section_title}</div>\n'
            html_content += f'    <div class="doc-content" data-id="{section_id}">\n'
            if section.get('subsections'):
                for subsection in section['subsections']:
                    html_content += f'        <div class="doc-subsection">{escape_html(subsection["title"])}</div>\n'
                    html_content += f'        <div class="doc-subcontent">\n'
                    if subsection.get('subsubsections'):
                        for subsubsection in subsection['subsubsections']:
                            html_content += f'            <div class="doc-subsubsection">{escape_html(subsubsection["title"])}</div>\n'
                            html_content += f'            <div class="doc-subsubcontent">\n'
                            html_content += format_content(subsubsection.get('content', ''))
                            html_content += f'            </div>\n'
                    else:
                        html_content += format_content(subsection.get('content', ''))
                    html_content += f'        </div>\n'
            else:
                html_content += format_content(section.get('content', ''))
            html_content += f'    </div>\n\n'
        html_content += '</div>'
        return html_content
        
    accordion_html = build_html_structure()
    
    # Limpiar el HTML generado
    try:
        soup = BeautifulSoup(accordion_html, 'html.parser')
        accordion_html_formatted = soup.prettify()
    except Exception as e:
        print(f"    ⚠️ Error formateando HTML: {str(e)}")
        accordion_html_formatted = accordion_html

    # Plantilla Jinja2 final
    html_template = f"""{{% extends 'home.html' %}}
{{% block title %}}Documentacion{{% endblock %}}
{{% block content %}}
<link href="{{{{ url_for('static', filename='css/acordeon_doc.css') }}}}" rel="stylesheet" />
<link href="{{{{ url_for('static', filename='css/procedimientos.css') }}}}" rel="stylesheet" />

<div id="documento" style="display:none;">{html_doc_path}</div>
<div id="nombre_documento" style="display: none;">{doc_name_no_ext}</div>
<h1>{doc_name_no_ext}</h1>
{{% for cambio in cambios %}}
{{% if loop.first %}}
<h3>Version: {{{{cambio[3]}}}}</h3>
{{% endif %}}
{{% endfor %}}
<br />
{accordion_html_formatted}
<!-- Botones y Modals para edición -->
<button class="btn btn-outline-primary" id="openModalBtn" style="margin-top: 20px;">Editar Secciones</button>
<div class="modal" id="sectionModal">
    <div class="modal-content">
        <span class="close-button">×</span>
        <h2>Selecciona y Edita una Sección</h2>
        <select id="sectionSelector"><option value="">-- Selecciona --</option></select>
        <textarea id="sectionContent" placeholder="Contenido..."></textarea>
        <textarea id="sectionCambio" placeholder="Descripción del cambio..." required></textarea>
        <button class="btn btn-outline-primary" id="saveChangesBtn" style="margin-top: 15px;">Guardar Cambios</button>
    </div>
</div>
<script src="{{{{ url_for('static', filename='js/jquery.min.js')}}}}"></script>
<script src="{{{{ url_for('static', filename='js/acordeon_doc.js')}}}}"></script>
<script src="{{{{ url_for('static', filename='js/edita_procedimiento.js')}}}}"></script>

{{% endblock %}}
"""
    # 4. --- GUARDADO DEL ARCHIVO HTML ---
    try:
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_template)
        return True
    except Exception as e:
        print(f"    ❌ Error escribiendo archivo HTML: {str(e)}")
        return False

# --- FUNCIÓN PARA EJECUTAR LA CONVERSIÓN EN LOTE ---
def convertir_todos_los_docx():
    try:
        # Ahora solo busca archivos .docx
        docx_files = [f for f in os.listdir(DOCX_FOLDER) if f.lower().endswith(".docx")]
        
        if not docx_files:
            print("❌ No se encontraron archivos DOCX en la carpeta.")
            return
        
        print(f"📁 Encontrados {len(docx_files)} archivos DOCX")
        print(f"📂 Carpeta origen: {DOCX_FOLDER}")
        print(f"📂 Carpeta destino: {HTML_FOLDER}")
        print("-" * 50)
        
        success_count = 0
        error_count = 0
        
        for file in docx_files:
            try:
                docx_path = os.path.join(DOCX_FOLDER, file)
                html_name = os.path.splitext(file)[0] + ".html"
                html_path = os.path.join(HTML_FOLDER, html_name)
                
                print(f"🔄 Procesando: {file}")
                if convertir_docx_a_html(docx_path, html_path):
                    success_count += 1
                    print(f"    ✅ Convertido exitosamente")
                else:
                    error_count += 1
            except Exception as e:
                error_count += 1
                print(f"❌ Error grave procesando {file}: {str(e)}")
        
        print("-" * 50)
        print(f"📊 Resumen: {success_count} exitosos, {error_count} errores")
        print("✅ Proceso finalizado")
        
    except Exception as e:
        print(f"❌ Error general: {str(e)}")

if __name__ == "__main__":
    convertir_todos_los_docx()