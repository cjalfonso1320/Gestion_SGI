#!/usr/bin/env python3
"""
Script para probar la conversión de un solo PDF
"""

import os
import sys
from convertir_pdf_final import convertir_pdf_a_html

def test_single_conversion():
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
    for i, pdf_file in enumerate(pdf_files[:5]):  # Mostrar solo los primeros 5
        print(f"  {i+1}. {pdf_file}")
    
    # Usar PRO-PR-012 si existe, sino el primero
    test_pdf = None
    for pdf_file in pdf_files:
        if "PRO-PR-012" in pdf_file:
            test_pdf = pdf_file
            break
    
    if not test_pdf:
        test_pdf = pdf_files[0]
    
    pdf_path = os.path.join(PDF_FOLDER, test_pdf)
    html_name = os.path.splitext(test_pdf)[0] + "_test.html"
    html_path = os.path.join(HTML_FOLDER, html_name)
    
    print(f"\n🔄 Probando conversión con: {test_pdf}")
    print(f"📂 Destino: {html_path}")
    
    try:
        success = convertir_pdf_a_html(pdf_path, html_path)
        
        if success and os.path.exists(html_path):
            file_size = os.path.getsize(html_path)
            print(f"✅ Conversión exitosa! Archivo creado: {file_size} bytes")
            
            # Leer y analizar el contenido
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Buscar patrones importantes
                section_count = content.count('doc-section')
                subsection_count = content.count('doc-subsection')
                list_count = content.count('<ul>')
                content_paragraphs = content.count('<p>')
                
                print(f"\n📊 Estadísticas del contenido generado:")
                print(f"  • Secciones principales: {section_count}")
                print(f"  • Subsecciones: {subsection_count}")
                print(f"  • Listas generadas: {list_count}")
                print(f"  • Párrafos generados: {content_paragraphs}")
                
                # Buscar contenido específico
                if "Responsable:" in content:
                    print(f"  ✅ Contenido con 'Responsable' encontrado")
                if "Descripción:" in content:
                    print(f"  ✅ Contenido con 'Descripción' encontrado")
                
                # Mostrar una muestra del contenido
                lines = content.split('\n')
                print(f"\n📄 Muestra del contenido generado (líneas 20-40):")
                print("-" * 60)
                for i in range(19, min(39, len(lines))):
                    if lines[i].strip():
                        print(f"{i+1:3d}: {lines[i]}")
                print("-" * 60)
                
                return True
        else:
            print("❌ Error: El archivo HTML no se creó o hubo un error")
            return False
            
    except Exception as e:
        print(f"❌ Error durante la conversión: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Iniciando prueba de conversión PDF a HTML")
    print("=" * 60)
    
    success = test_single_conversion()
    
    if success:
        print("\n🎉 ¡Prueba exitosa! El script corregido funciona correctamente.")
        print("💡 Ahora puedes usar 'convertir_pdf_final.py' para convertir todos tus PDFs.")
    else:
        print("\n💥 La prueba falló. Revisa los errores anteriores.")
        sys.exit(1)






