#!/usr/bin/env python3
"""
Script de prueba para validar la conversión de PDF a HTML
"""

import os
import sys
from convertir_pdf_mejorado import convertir_pdf_a_html

def test_conversion():
    """Prueba la conversión con un PDF específico"""
    
    # Configuración de prueba
    PDF_FOLDER = r"\\192.168.40.150\Confidencial_Sistema_de_Gestion_Integrado\DOCUMENTACION\Gestión Producción\Procedimientos"
    HTML_FOLDER = r"C:\Users\cjalfonso\Desktop\codigos\GestionSGI\templates\procedimientos\HTML"
    
    # Verificar que la carpeta de PDFs existe
    if not os.path.exists(PDF_FOLDER):
        print(f"❌ Error: No se puede acceder a la carpeta de PDFs: {PDF_FOLDER}")
        return False
    
    # Listar PDFs disponibles
    pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.lower().endswith(".pdf")]
    
    if not pdf_files:
        print("❌ No se encontraron archivos PDF")
        return False
    
    print(f"📁 Archivos PDF encontrados ({len(pdf_files)}):")
    for i, pdf_file in enumerate(pdf_files[:10]):  # Mostrar solo los primeros 10
        print(f"  {i+1}. {pdf_file}")
    
    if len(pdf_files) > 10:
        print(f"  ... y {len(pdf_files) - 10} más")
    
    # Probar con el primer PDF
    test_pdf = pdf_files[0]
    pdf_path = os.path.join(PDF_FOLDER, test_pdf)
    html_name = os.path.splitext(test_pdf)[0] + "_test.html"
    html_path = os.path.join(HTML_FOLDER, html_name)
    
    print(f"\n🔄 Probando conversión con: {test_pdf}")
    print(f"📂 Destino: {html_path}")
    
    try:
        convertir_pdf_a_html(pdf_path, html_path)
        
        # Verificar que el archivo se creó
        if os.path.exists(html_path):
            file_size = os.path.getsize(html_path)
            print(f"✅ Conversión exitosa! Archivo creado: {file_size} bytes")
            
            # Leer y mostrar una muestra del contenido
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                print(f"\n📄 Muestra del contenido generado (primeras 20 líneas):")
                print("-" * 50)
                for i, line in enumerate(lines[:20]):
                    print(f"{i+1:2d}: {line}")
                print("-" * 50)
                
                # Buscar patrones importantes
                section_count = content.count('doc-section')
                subsection_count = content.count('doc-subsection')
                list_count = content.count('<ul>')
                
                print(f"\n📊 Estadísticas:")
                print(f"  • Secciones principales: {section_count}")
                print(f"  • Subsecciones: {subsection_count}")
                print(f"  • Listas generadas: {list_count}")
                
                return True
        else:
            print("❌ Error: El archivo HTML no se creó")
            return False
            
    except Exception as e:
        print(f"❌ Error durante la conversión: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def validate_html_structure(html_path):
    """Valida que la estructura HTML sea correcta"""
    try:
        from bs4 import BeautifulSoup
        
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Verificar elementos principales
        accordion = soup.find('div', class_='doc-accordion')
        if not accordion:
            print("❌ No se encontró el elemento doc-accordion")
            return False
        
        sections = accordion.find_all('div', class_='doc-section')
        contents = accordion.find_all('div', class_='doc-content')
        
        if len(sections) != len(contents):
            print(f"❌ Número inconsistente de secciones ({len(sections)}) y contenidos ({len(contents)})")
            return False
        
        print(f"✅ Estructura HTML válida: {len(sections)} secciones principales")
        return True
        
    except Exception as e:
        print(f"❌ Error validando HTML: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Iniciando pruebas de conversión PDF a HTML")
    print("=" * 60)
    
    success = test_conversion()
    
    if success:
        print("\n🎉 ¡Prueba exitosa! El script mejorado funciona correctamente.")
        print("💡 Puedes usar 'convertir_pdf_mejorado.py' para convertir todos tus PDFs.")
    else:
        print("\n💥 La prueba falló. Revisa los errores anteriores.")
        sys.exit(1)

