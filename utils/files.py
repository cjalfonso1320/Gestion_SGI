import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONES = {'pdf', 'jpg', 'jpeg', 'png', 'tiff'}

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONES
        
def guardar_archivo(file, carpeta, nombre_base):
    """
    Docstring for guardar_archivo
    
    file: -> request.files['cedula'] o ['foto']
    carpeta: -> ruta base del empleado
    nombre_base: -> cedula|foto
    """
    if not file or file.filename == '':
        return None
    
    if not allowed_file(file.filename):
        raise ValueError('Extension de archivo no permitida')
    
    os.makedirs(carpeta, exist_ok=True)
    
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = secure_filename(f"{nombre_base}.{ext}")
    
    ruta_relativa = os.path.join(carpeta, filename)
    file.save(ruta_relativa)
    
    return ruta_relativa

def guardar_archivos_multiples(files, carpeta, prefijo):
    rutas = []
    
    if not files:
        return rutas
    
    os.makedirs(carpeta, exist_ok=True)
    
    for i, file in enumerate(files, start=1):
        if file and file.filename and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = secure_filename(f"{prefijo}_{i}.{ext}")
            ruta = os.path.join(carpeta, filename)
            file.save(ruta)
            
            rutas.append(ruta.replace('\\', '/'))
    return rutas