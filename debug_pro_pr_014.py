#!/usr/bin/env python3
"""
Script para debuggear específicamente PRO-PR-014
"""

import os
import pdfplumber
import re
from convertir_pdf_estructura_fija import convertir_pdf_a_html

def debug_pro_pr_014():
    """Debug específico para PRO-PR-014"""
    
    # Configuración
    PDF_FOLDER = r"\\192.168.40.150\Confidencial_Sistema_de_Gestion_Integrado\DOCUMENTACION\Gestión Producción\Procedimientos"
    HTML_FOLDER = r"C:\Users\cjalfonso\Desktop\codigos\GestionSGI\templates\procedimientos\HTML"
    
    # Buscar PRO-PR-014 específicamente
    pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.lower().endswith(".pdf")]
    pro_pr_014_file = None
    
    for pdf_file in pdf_files:
        if "PRO-PR-014" in pdf_file:
            pro_pr_014_file = pdf_file
            break
    
    if not pro_pr_014_file:
        print("❌ No se encontró PRO-PR-014.pdf")
        return False
    
    pdf_path = os.path.join(PDF_FOLDER, pro_pr_014_file)
    html_name = os.path.splitext(pro_pr_014_file)[0] + "_debug.html"
    html_path = os.path.join(HTML_FOLDER, html_name)
    
    print(f"🔍 Debuggeando: {pro_pr_014_file}")
    print(f"📂 Destino: {html_path}")
    
    # Primero, analizar el PDF directamente
    print("\n📄 Analizando estructura del PDF...")
    try:
        with pdfplumber.open(pdf_path) as pdf:
            all_text = ""
            
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text(x_tolerance=1, y_tolerance=3)
                if text:
                    all_text += text + "\n"
                    if page_num < 3:  # Mostrar solo las primeras 3 páginas
                        print(f"\n--- PÁGINA {page_num + 1} ---")
                        lines = text.split('\n')[:20]  # Primeras 20 líneas
                        for i, line in enumerate(lines):
                            if line.strip():
                                print(f"{i+1:3d}: {line.strip()}")
            
            print(f"\n📊 Total de páginas: {len(pdf.pages)}")
            print(f"📊 Total de caracteres extraídos: {len(all_text)}")
            
            # Buscar patrones de secciones
            lines = all_text.split('\n')
            section_patterns = {
                'section': r'^\d+\.\s+[A-ZÁÉÍÓÚÑ\s]+',
                'subsection': r'^\d+\.\d+\.?\s+',
                'subsubsection': r'^\d+\.\d+\.\d+\.?\s+',
                'subsubsubsection': r'^\d+\.\d+\.\d+\.\d+\.?\s+'
            }
            
            print(f"\n🔍 Buscando patrones de secciones...")
            for pattern_name, pattern in section_patterns.items():
                matches = []
                for i, line in enumerate(lines):
                    if re.match(pattern, line.strip(), re.IGNORECASE):
                        matches.append((i+1, line.strip()))
                
                print(f"  {pattern_name}: {len(matches)} encontradas")
                for line_num, line_content in matches[:5]:  # Mostrar solo las primeras 5
                    print(f"    Línea {line_num}: {line_content}")
                if len(matches) > 5:
                    print(f"    ... y {len(matches) - 5} más")
            
            # Buscar contenido con palabras clave
            print(f"\n🔍 Buscando contenido con palabras clave...")
            keywords = ["Responsable:", "Registro:", "Descripción:", "Nota:"]
            for keyword in keywords:
                matches = []
                for i, line in enumerate(lines):
                    if keyword in line:
                        matches.append((i+1, line.strip()))
                
                print(f"  '{keyword}': {len(matches)} encontradas")
                for line_num, line_content in matches[:3]:  # Mostrar solo las primeras 3
                    print(f"    Línea {line_num}: {line_content[:100]}...")
                if len(matches) > 3:
                    print(f"    ... y {len(matches) - 3} más")
            
    except Exception as e:
        print(f"❌ Error analizando PDF: {str(e)}")
        return False
    
    # Ahora probar la conversión
    print(f"\n🔄 Probando conversión...")
    try:
        success = convertir_pdf_a_html(pdf_path, html_path)
        
        if success and os.path.exists(html_path):
            file_size = os.path.getsize(html_path)
            print(f"✅ Conversión exitosa! Archivo creado: {file_size} bytes")
            
            # Analizar el resultado
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Estadísticas
                section_count = content.count('doc-section')
                subsection_count = content.count('doc-subsection')
                list_count = content.count('<ul>')
                content_paragraphs = content.count('<p>')
                empty_content = content.count('<div class="doc-content" data-id="')
                non_empty_content = content.count('<div class="doc-content" data-id="') - content.count('<div class="doc-content" data-id="1">\n\n    </div>')
                
                print(f"\n📊 Estadísticas del HTML generado:")
                print(f"  • Secciones principales: {section_count}")
                print(f"  • Subsecciones: {subsection_count}")
                print(f"  • Listas generadas: {list_count}")
                print(f"  • Párrafos generados: {content_paragraphs}")
                print(f"  • Contenidos vacíos: {empty_content - non_empty_content}")
                print(f"  • Contenidos con datos: {non_empty_content}")
                
                # Buscar contenido específico
                if "Responsable:" in content:
                    print(f"  ✅ Contenido con 'Responsable' encontrado")
                if "Descripción:" in content:
                    print(f"  ✅ Contenido con 'Descripción' encontrado")
                
                # Mostrar muestra del contenido
                lines = content.split('\n')
                print(f"\n📄 Muestra del contenido generado (líneas 50-100):")
                print("-" * 60)
                for i in range(49, min(99, len(lines))):
                    if lines[i].strip():
                        print(f"{i+1:3d}: {lines[i]}")
                print("-" * 60)
                
                return True
        else:
            print("❌ Error: El archivo HTML no se creó")
            return False
            
    except Exception as e:
        print(f"❌ Error durante la conversión: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Iniciando debug de PRO-PR-014")
    print("=" * 60)
    
    success = debug_pro_pr_014()
    
    if success:
        print("\n🎉 Debug completado exitosamente!")
    else:
        print("\n💥 El debug falló. Revisa los errores anteriores.")






