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
    # Asumimos que el HTML se guardará en una subcarpeta de 'procedimientos'
    # Esto puede necesitar ajuste dependiendo de tu estructura final.
    html_doc_path = os.path.join('procedimientos', 'HTML', os.path.basename(html_path)).replace('\\', '/')

    accordion_html = '<div class="doc-accordion">\n'

    with pdfplumber.open(pdf_path) as pdf:
        seccion_actual = None
        subseccion_actual = None
        buffer = ""
        in_subsection_block = False

        def escape_html(text):
            # Limpia puntos y espacios extra al final, luego escapa.
            cleaned_text = re.sub(r'[\s.]+$', '', text).strip()
            cleaned_text = re.sub(r'\s+\.{2,}.*$', '', cleaned_text).strip()
            return cleaned_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

        def format_buffer(text):
            text = text.strip()
            if not text:
                return ""

            # Palabras clave para detectar y formatear como lista
            keywords = ["Responsable:", "Registro:", "Descripción:", "Nota:"]
            
            # Comprobar si el texto contiene alguna de las palabras clave
            if any(keyword in text for keyword in keywords):
                list_html = "<ul>\n"
                # Usamos una expresión regular para dividir el texto por las palabras clave, manteniéndolas.
                # (Responsable:|Registro:|Descripción:|Nota:)
                parts = re.split(r'(Responsable:|Registro:|Descripción:|Nota:)', text)
                
                for i in range(1, len(parts), 2):
                    keyword = parts[i]
                    content = parts[i+1].strip()
                    list_html += f'                    <li><i class="fa-regular fa-circle-check"></i><b>{escape_html(keyword)}</b> {escape_html(content)}</li>\n'
                list_html += "                </ul>"
                return list_html
            else:
                # Si no hay palabras clave, lo tratamos como párrafos normales.
                return f"<p>{escape_html(text)}</p>"

        def close_section():
            nonlocal buffer, seccion_actual, subseccion_actual, accordion_html, in_subsection_block
            
            if subseccion_actual:
                accordion_html += f'        <div class="doc-subsection">{escape_html(subseccion_actual)}</div>\n'
                accordion_html += f'        <div class="doc-subcontent">\n{format_buffer(buffer)}        </div>\n'
                subseccion_actual = None
            elif seccion_actual:
                if in_subsection_block:
                    accordion_html += '        </div>\n' # Cierra el doc-content que contiene subsecciones
                    in_subsection_block = False
                
                # Verificación para evitar el error 'NoneType'
                data_id = seccion_actual.split('.')[0] if seccion_actual else '0'
                escaped_seccion = escape_html(seccion_actual) if seccion_actual else ''

                accordion_html += f'    <div class="doc-section" data-id="{data_id}">{escaped_seccion}</div>\n'
                accordion_html += f'    <div class="doc-content" data-id="{data_id}">\n{format_buffer(buffer)}    </div>\n'

                seccion_actual = None
            buffer = ""

        for page in pdf.pages:
            text = page.extract_text(x_tolerance=1, y_tolerance=3)
            if not text:
                continue

            for line in text.split('\n'):
                line = line.strip()
                if not line:
                    continue

                # Detecta secciones principales (e.g., "1. OBJETIVO")
                if re.match(r"^\d+\.\s+[\w\s]+", line) and not re.match(r"^\d+\.\d+", line):
                    close_section()
                    seccion_actual = line.upper() # Convertir a mayúsculas para consistencia
                # Detecta subsecciones (e.g., "6.1. Creación" o "6.1.1. Algo")
                elif re.match(r"^\d+\.\d+", line):
                    if subseccion_actual: # Cierra la subsección anterior
                        accordion_html += f'        <div class="doc-subsection">{escape_html(subseccion_actual)}</div>\n'
                        accordion_html += f'        <div class="doc-subcontent">\n{format_buffer(buffer)}        </div>\n'
                        buffer = ""
                    
                    if not in_subsection_block:
                        # Verificación para evitar el error 'NoneType'
                        if seccion_actual:
                            data_id = seccion_actual.split('.')[0]
                            escaped_seccion = escape_html(seccion_actual)
                            accordion_html += f'    <div class="doc-section" data-id="{data_id}">{escaped_seccion}</div>\n'
                            accordion_html += f'    <div class="doc-content" data-id="{data_id}">\n'
                            if buffer.strip():
                                accordion_html += format_buffer(buffer)
                            in_subsection_block = True
                            buffer = ""
                        # Cierra el buffer de la sección principal si existe

                    subseccion_actual = line
                else:
                    # Ignorar cabeceras/pies de página comunes
                    if re.match(r"(C[OÓ]DIGO:|VERSI[OÓ]N:|P[ÁA]GINA|FECHA|USO INTERNO|COPIA CONTROLADA|CONFIDENCIAL)", line, re.IGNORECASE) or re.match(r"^\d+\s+de\s+\d+$", line):
                        continue
                    buffer += line + " "

        close_section()

    accordion_html += '</div>'

    # Limpiar el HTML generado con BeautifulSoup para un formato más legible
    soup = BeautifulSoup(accordion_html, 'html.parser')
    accordion_html_formatted = soup.prettify()

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

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_template)

# 🔄 Recorrer todos los PDFs de la carpeta
for file in os.listdir(PDF_FOLDER):
    if file.lower().endswith(".pdf"):
        pdf_path = os.path.join(PDF_FOLDER, file)
        html_name = os.path.splitext(file)[0] + ".html"
        html_path = os.path.join(HTML_FOLDER, html_name)

        print(f"Convirtiendo {file} → {html_name}")
        convertir_pdf_a_html(pdf_path, html_path)

print("✅ Conversión finalizada")
