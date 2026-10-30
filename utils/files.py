"""Utilidades para la gestión y validación de archivos subidos.

Proporciona funciones para validar extensiones, verificar magic bytes
(MIME real), guardar archivos en disco y manejar subidas múltiples.

Validaciones de seguridad:
    - Extensión permitida (ALLOWED_EXTENSIONES).
    - Magic bytes (firma real del archivo) post-grabado.
    - Rechazo y logging de archivos sospechosos.
"""

import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONES = {'pdf', 'jpg', 'jpeg', 'png', 'tiff'}

# ── Magic bytes / firmas de archivo ────────────────────────────────────────
# Cada entrada: (extensión, offset, bytes mágicos)
_FILE_SIGNATURES = [
    ('pdf', 0, b'%PDF'),
    ('jpg',  0, b'\xff\xd8\xff'),
    ('jpeg', 0, b'\xff\xd8\xff'),
    ('png',  0, b'\x89PNG\r\n\x1a\n'),
    ('tiff', 0, b'II\x2a\x00'),   # Little-endian TIFF
    ('tiff', 0, b'MM\x00\x2a'),   # Big-endian TIFF
]


def _check_magic_bytes(filepath, expected_ext):
    """Verifica que los primeros bytes del archivo coincidan con la firma esperada.

    Lee los primeros 32 bytes del archivo y los compara con las firmas
    conocidas para la extensión indicada.

    Args:
        filepath: Ruta absoluta o relativa al archivo en disco.
        expected_ext: Extensión esperada (ej: 'pdf', 'jpg').

    Returns:
        bool: True si la firma coincide, False en caso contrario.
    """
    if not os.path.exists(filepath):
        return False

    try:
        with open(filepath, 'rb') as f:
            header = f.read(32)
    except (IOError, OSError):
        return False

    expected_ext = expected_ext.lower().lstrip('.')

    for ext, offset, magic in _FILE_SIGNATURES:
        if ext != expected_ext:
            continue
        if offset + len(magic) > len(header):
            continue
        if header[offset:offset + len(magic)] == magic:
            return True

    # Si no hay firma definida para esta extensión, confiar en la extensión
    return expected_ext in ALLOWED_EXTENSIONES


def allowed_file(filename, filepath=None):
    """Valida que un archivo tenga extensión permitida y, opcionalmente, magic bytes.

    Si se proporciona filepath, también verifica los magic bytes para
    confirmar que el contenido coincide con la extensión declarada.

    Args:
        filename: Nombre del archivo (para validar extensión).
        filepath: Ruta al archivo en disco (para validar magic bytes, opcional).

    Returns:
        bool: True si el archivo es válido, False en caso contrario.
    """
    if '.' not in filename:
        return False

    ext = filename.rsplit('.', 1)[1].lower()
    if ext not in ALLOWED_EXTENSIONES:
        return False

    # Si se proporciono filepath, validar magic bytes
    if filepath is not None:
        return _check_magic_bytes(filepath, ext)

    return True


def guardar_archivo(file, carpeta, nombre_base):
    """Guarda un archivo en disco y valida su contenido mediante magic bytes.

    Si los magic bytes no coinciden con la extensión, elimina el archivo
    y lanza una excepción con la descripción del error.

    Args:
        file: Objeto FileStorage de Flask (request.files['campo']).
        carpeta: Ruta base del directorio donde guardar.
        nombre_base: Nombre base del archivo (ej: 'cedula', 'foto').

    Returns:
        str: Ruta relativa normalizada del archivo guardado, o None si no se recibió archivo.

    Raises:
        ValueError: Si la extensión no está permitida o los magic bytes no coinciden.
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

    # Validar magic bytes post-grabado
    if not _check_magic_bytes(ruta_relativa, ext):
        os.remove(ruta_relativa)
        from utils.security_logger import file_upload_rejected
        file_upload_rejected(
            user_id='N/A',
            username='N/A',
            filename=filename,
            reason=f'Magic bytes no coinciden para extension .{ext}',
        )
        raise ValueError(
            f'El archivo tiene extension .{ext} pero su contenido '
            f'no corresponde a ese formato.'
        )

    # Normalizar a forward slashes para compatibilidad web
    return ruta_relativa.replace('\\', '/')


def guardar_archivos_multiples(files, carpeta, prefijo):
    """Guarda múltiples archivos en disco validando cada uno con magic bytes.

    Cada archivo se guarda de forma independiente. Si un archivo falla
    la validación de magic bytes, se omite y se continúa con el siguiente.

    Args:
        files: Lista de objetos FileStorage de Flask.
        carpeta: Ruta base del directorio donde guardar.
        prefijo: Prefijo para nombrar los archivos (ej: 'estudio').

    Returns:
        list: Lista de rutas normalizadas de los archivos guardados exitosamente.
    """
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

            # Validar magic bytes post-grabado
            if not _check_magic_bytes(ruta, ext):
                os.remove(ruta)
                from utils.security_logger import file_upload_rejected
                file_upload_rejected(
                    user_id='N/A',
                    username='N/A',
                    filename=filename,
                    reason=f'Magic bytes no coinciden para extension .{ext}',
                )
                continue  # Saltar este archivo, continuar con el siguiente

            # Normalizar a forward slashes para compatibilidad web
            rutas.append(ruta.replace('\\', '/'))

    return rutas
