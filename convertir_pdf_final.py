import os
import pdfplumber
import re
from bs4 import BeautifulSoup, NavigableString

# Carpeta donde están tus PDFs
PDF_FOLDER = r"\\192.168.40.150\Confidencial_Sistema_de_Gestion_Integrado\DOCUMENTACION\Gestión Producción\Procedimientos"
# Carpeta donde se guardarán los HTMLs convertidos
HTML_FOLDER = r"C:\Users\cjalfonso\Desktop\codigos\GestionSGI\templates\procedimientos\HTML"

os.makedirs(HTML_FOLDER, exist_ok=True)

def convertir_pdf_a_html(pdf_path, html_path):
    base_name = os.path.basename(pdf_path)
    doc_name_no_ext = os.path.splitext(base_name)[0]
    html_doc_path = os.path.join('procedimientos', 'HTML', os.path.basename(html_path)).replace('\\', '/')

    # Estructura para almacenar el contenido
    sections = []
    current_section = None
    current_subsection = None
    current_subsubsection = None
    content_buffer = ""
    
    def escape_html(text):
        """Escapa caracteres HTML y limpia el texto"""
        if not text:
            return ""
        # Limpia puntos y espacios extra al final
        cleaned_text = re.sub(r'[\s.]+$', '', text).strip()
        # Remueve puntos suspensivos y números de página
        cleaned_text = re.sub(r'\s*\.{2,}.*$', '', cleaned_text).strip()
        cleaned_text = re.sub(r'^\d+\s*$', '', cleaned_text).strip()
        # Escapa caracteres HTML
        cleaned_text = cleaned_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        return cleaned_text

    def format_content(text):
        """Formatea el contenido como lista con iconos cuando detecta palabras clave"""
        if not text or not text.strip():
            return ""
        
        text = text.strip()
        
        # Palabras clave para detectar y formatear como lista
        keywords = ["Responsable:", "Registro:", "Descripción:", "Nota:", "RESPONSABLE:", "REGISTRO:", "DESCRIPCIÓN:", "NOTA:"]
        
        # Comprobar si el texto contiene alguna de las palabras clave
        if any(keyword in text for keyword in keywords):
            list_html = "<ul>\n"
            # Usar expresión regular para dividir por palabras clave, manteniéndolas
            pattern = r'(Responsable:|Registro:|Descripción:|Nota:|RESPONSABLE:|REGISTRO:|DESCRIPCIÓN:|NOTA:)'
            parts = re.split(pattern, text)
            
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
            # Si no hay palabras clave, lo tratamos como párrafos
            paragraphs = text.split('\n\n')
            html_content = ""
            for para in paragraphs:
                if para.strip():
                    html_content += f"                        <p>{escape_html(para.strip())}</p>\n"
            return html_content

    def detect_section_level(line):
        """Detecta el nivel de la sección basado en la numeración"""
        line = line.strip()
        
        # Sección principal: 1. OBJETIVO, 2. ALCANCE, etc.
        if re.match(r'^\d+\.\s+[A-ZÁÉÍÓÚÑ\s]+', line, re.IGNORECASE):
            return 'section', line
        # Subsección: 6.1. Recepción, 6.2. Captura, etc.
        elif re.match(r'^\d+\.\d+\.?\s+', line):
            return 'subsection', line
        # Sub-subsección: 6.1.1. Descargar, 6.1.2. Cargar, etc.
        elif re.match(r'^\d+\.\d+\.\d+\.?\s+', line):
            return 'subsubsection', line
        # Sub-sub-subsección: 6.1.1.1. Algo, 6.1.1.2. Otro, etc.
        elif re.match(r'^\d+\.\d+\.\d+\.\d+\.?\s+', line):
            return 'subsubsubsection', line
        
        return None, None

    def save_current_content():
        """Guarda el contenido actual en la estructura correcta"""
        nonlocal content_buffer, current_subsubsection, current_subsection, current_section
        
        if content_buffer.strip():
            if current_subsubsection:
                current_subsubsection['content'] = content_buffer.strip()
            elif current_subsection:
                current_subsection['content'] = content_buffer.strip()
            elif current_section:
                current_section['content'] = content_buffer.strip()
            content_buffer = ""

    def build_html_structure():
        """Construye la estructura HTML final"""
        html_content = '<div class="doc-accordion">\n\n'
        
        for section in sections:
            section_id = section['number']
            section_title = escape_html(section['title'])
            section_content = section['content']
            
            # Sección principal
            html_content += f'    <div class="doc-section" data-id="{section_id}">\n'
            html_content += f'        {section_title}\n'
            html_content += f'    </div>\n'
            html_content += f'    <div class="doc-content" data-id="{section_id}">\n'
            
            # Si tiene subsecciones, las procesamos
            if section['subsections']:
                for subsection in section['subsections']:
                    html_content += f'        <div class="doc-subsection">{escape_html(subsection["title"])}</div>\n'
                    html_content += f'        <div class="doc-subcontent">\n'
                    
                    # Si tiene sub-subsecciones
                    if subsection['subsubsections']:
                        for subsubsection in subsection['subsubsections']:
                            html_content += f'            <div class="doc-subsection">{escape_html(subsubsection["title"])}</div>\n'
                            html_content += f'            <div class="doc-subcontent">\n'
                            html_content += format_content(subsubsection['content'])
                            html_content += f'            </div>\n'
                    else:
                        # Solo contenido de subsección
                        html_content += format_content(subsection['content'])
                    
                    html_content += f'        </div>\n'
            else:
                # Solo contenido de sección principal
                html_content += format_content(section_content)
            
            html_content += f'    </div>\n\n'
        
        html_content += '</div>'
        return html_content

    # Procesar el PDF
    try:
        with pdfplumber.open(pdf_path) as pdf:
            all_text = ""
            
            # Extraer todo el texto primero
            for page in pdf.pages:
                text = page.extract_text(x_tolerance=1, y_tolerance=3)
                if text:
                    all_text += text + "\n"
            
            # Procesar el texto línea por línea
            lines = all_text.split('\n')
            i = 0
            
            while i < len(lines):
                line = lines[i].strip()
                
                # Ignorar líneas vacías
                if not line:
                    i += 1
                    continue
                
                # Ignorar cabeceras/pies de página
                if re.match(r"(C[OÓ]DIGO:|VERSI[OÓ]N:|P[ÁA]GINA|FECHA|USO INTERNO|COPIA CONTROLADA|CONFIDENCIAL|DIGICOM)", line, re.IGNORECASE):
                    i += 1
                    continue
                if re.match(r"^\d+\s+de\s+\d+$", line):
                    i += 1
                    continue
                
                # Detectar tipo de sección
                section_type, section_title = detect_section_level(line)
                
                if section_type == 'section':
                    # Guardar contenido anterior
                    save_current_content()
                    
                    # Guardar sección anterior si existe
                    if current_section:
                        sections.append(current_section)
                    
                    # Nueva sección principal
                    section_number = section_title.split('.')[0]
                    current_section = {
                        'number': section_number,
                        'title': section_title,
                        'content': '',
                        'subsections': []
                    }
                    current_subsection = None
                    current_subsubsection = None
                    
                elif section_type == 'subsection':
                    # Guardar contenido anterior
                    save_current_content()
                    
                    # Nueva subsección
                    if current_subsection and current_section:
                        current_section['subsections'].append(current_subsection)
                    
                    current_subsection = {
                        'title': section_title,
                        'content': '',
                        'subsubsections': []
                    }
                    current_subsubsection = None
                    
                elif section_type == 'subsubsection':
                    # Guardar contenido anterior
                    save_current_content()
                    
                    # Nueva sub-subsección
                    if current_subsubsection and current_subsection:
                        current_subsection['subsubsections'].append(current_subsubsection)
                    
                    current_subsubsection = {
                        'title': section_title,
                        'content': ''
                    }
                    
                elif section_type == 'subsubsubsection':
                    # Guardar contenido anterior
                    save_current_content()
                    
                    # Sub-sub-subsección (tratamos como sub-subsección)
                    if current_subsubsection and current_subsection:
                        current_subsection['subsubsections'].append(current_subsubsection)
                    
                    current_subsubsection = {
                        'title': section_title,
                        'content': ''
                    }
                    
                else:
                    # Es contenido, lo agregamos al buffer
                    content_buffer += line + " "
                
                i += 1
        
        # Guardar contenido final
        save_current_content()
        
        # Guardar las últimas secciones
        if current_subsubsection and current_subsection:
            current_subsection['subsubsections'].append(current_subsubsection)
        if current_subsection and current_section:
            current_section['subsections'].append(current_subsection)
        if current_section:
            sections.append(current_section)
    
    except Exception as e:
        print(f"    ❌ Error procesando PDF: {str(e)}")
        return False
    
    # Si no hay secciones, crear una por defecto
    if not sections:
        sections = [{
            'number': '1',
            'title': '1. CONTENIDO DEL DOCUMENTO',
            'content': 'Contenido del documento procesado automáticamente.',
            'subsections': []
        }]
    
    # Generar HTML final
    accordion_html = build_html_structure()
    
    # Limpiar el HTML generado con BeautifulSoup para un formato más legible
    try:
        soup = BeautifulSoup(accordion_html, 'html.parser')
        accordion_html_formatted = soup.prettify()
    except Exception as e:
        print(f"    ⚠️ Error formateando HTML: {str(e)}")
        accordion_html_formatted = accordion_html

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
<!-- Botón para abrir el modal -->
<button class="btn btn-outline-primary" id="openModalBtn" style="margin-top: 20px;">Editar Secciones</button>
<!-- El Modal -->
<div class="modal" id="sectionModal">
    <div class="modal-content">
        <span class="close-button">×</span>
        <h2>Selecciona y Edita una Sección</h2>
        <label for="sectionSelector">Sección:</label>
        <select id="sectionSelector">
            <option value="">-- Selecciona una sección --</option>
        </select>
        <label for="sectionContent">Contenido:</label>
        <textarea id="sectionContent" placeholder="El contenido de la sección aparecerá aquí..."></textarea>
        <label for="sectionCambio">Descripcion del Cambio:</label>
        <textarea id="sectionCambio" placeholder="Describe en palabras cortas el cambio realizado..."
            required></textarea>
        <button class="btn btn-outline-primary" id="saveChangesBtn" style="margin-top: 15px;">Guardar Cambios</button>
    </div>
</div>
<script src="{{{{ url_for('static', filename='js/jquery.min.js')}}}}"></script>
<script src="{{{{ url_for('static', filename='js/acordeon_doc.js')}}}}"></script>
<script src="{{{{ url_for('static', filename='js/edita_procedimiento.js')}}}}"></script>

{{% endblock %}}
"""

    try:
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_template)
        return True
    except Exception as e:
        print(f"    ❌ Error escribiendo archivo: {str(e)}")
        return False

# 🔄 Recorrer todos los PDFs de la carpeta
def convertir_todos_los_pdfs():
    try:
        pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.lower().endswith(".pdf")]
        
        if not pdf_files:
            print("❌ No se encontraron archivos PDF en la carpeta")
            return
        
        print(f"📁 Encontrados {len(pdf_files)} archivos PDF")
        print(f"📂 Carpeta origen: {PDF_FOLDER}")
        print(f"📂 Carpeta destino: {HTML_FOLDER}")
        print("-" * 50)
        
        success_count = 0
        error_count = 0
        
        for file in pdf_files:
            try:
                pdf_path = os.path.join(PDF_FOLDER, file)
                html_name = os.path.splitext(file)[0] + ".html"
                html_path = os.path.join(HTML_FOLDER, html_name)
                
                print(f"🔄 Procesando: {file}")
                if convertir_pdf_a_html(pdf_path, html_path):
                    success_count += 1
                    print(f"    ✅ Convertido exitosamente")
                else:
                    error_count += 1
                    print(f"    ❌ Error en la conversión")
                
            except Exception as e:
                error_count += 1
                print(f"❌ Error procesando {file}: {str(e)}")
        
        print("-" * 50)
        print(f"📊 Resumen: {success_count} exitosos, {error_count} errores")
        print("✅ Proceso finalizado")
        
    except Exception as e:
        print(f"❌ Error general: {str(e)}")

if __name__ == "__main__":
    convertir_todos_los_pdfs()

