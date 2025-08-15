# Funcionalidad de Subida de Documentos

## Descripción
Se ha implementado una funcionalidad completa para subir documentos al sistema de gestión integrado. Esta funcionalidad incluye:

- Botón flotante para subir documentos desde cualquier página
- Botones específicos en cada sección de documentos
- Modal de selección de carpeta y archivo
- Modal de confirmación para reemplazar archivos existentes
- Validación de archivos y carpetas
- Interfaz moderna y responsiva

## Características

### 1. Botón Flotante
- Ubicado en la esquina inferior derecha de la pantalla
- Accesible desde cualquier página de documentación
- Diseño moderno con gradiente y efectos hover

### 2. Botones de Sección
- Botones específicos en cada sección de documentos
- Pre-seleccionan automáticamente la carpeta correspondiente
- Texto descriptivo según el tipo de documento

### 3. Modal de Subida
- Selección de carpeta desde un dropdown
- Selección de archivo con validación de tipos
- Interfaz intuitiva y fácil de usar

### 4. Modal de Confirmación
- Se muestra cuando un archivo ya existe
- Permite al usuario decidir si reemplazar o cancelar
- Muestra el nombre del archivo existente

## Tipos de Archivos Soportados
- PDF (.pdf)
- Documentos de Word (.doc, .docx)
- Hojas de cálculo (.xls, .xlsx)
- Presentaciones (.ppt, .pptx)
- Archivos de texto (.txt)

## Carpetas Disponibles
- Procedimientos
- Formatos Digitales
- Formatos Físicos
- Formatos Externos Digital
- Formatos Externos Físico
- Plan de Calidad
- Requisitos del Cliente
- Actas de Restauración
- Instructivos
- Manuales
- Auditorías (IFX, Integrum, Inter Servicios)
- Políticas ISEC
- Comité de Seguridad
- Vulnerabilidades (2024, 2025, Anteriores)
- Revisión de Seguridad (2021-2024)
- Encuestas (2019-2021)

## Uso

### Subir un Documento Nuevo
1. Hacer clic en el botón flotante o en el botón de la sección específica
2. Seleccionar la carpeta destino desde el dropdown
3. Seleccionar el archivo a subir
4. Hacer clic en "Subir"

### Reemplazar un Documento Existente
1. Si el archivo ya existe, se mostrará un modal de confirmación
2. Hacer clic en "Reemplazar" para sobrescribir el archivo
3. Hacer clic en "Cancelar" para abortar la operación

## Archivos Modificados

### Templates
- `templates/users/documentacion.html` - Modal principal y botón flotante
- `templates/users/procedimientos.html` - Botón de sección
- `templates/users/formatosDigitales.html` - Botón de sección

### Estilos
- `static/css/acordeon_doc.css` - Estilos para modales y botones

### JavaScript
- `static/js/acordeon_doc.js` - Funcionalidad de modales y subida

### Backend
- `routes/doc_routes.py` - Nueva ruta `/documentacion/subir`

## Seguridad
- Validación de tipos de archivo
- Nombres de archivo seguros con `secure_filename`
- Verificación de permisos de carpeta
- Validación de rol de usuario

## Responsive Design
- Modales adaptables a dispositivos móviles
- Botones con tamaño optimizado para touch
- Layout flexible para diferentes tamaños de pantalla

## Notas Técnicas
- Los archivos se guardan en las rutas configuradas en la base de datos
- Se verifica la existencia de la carpeta antes de subir
- Se manejan errores de forma elegante con mensajes informativos
- La página se recarga automáticamente después de una subida exitosa
