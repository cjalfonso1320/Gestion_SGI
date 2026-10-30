-- ============================================================
-- AGREGAR COLUMNA fecha_confirmacion_datos A LA TABLA users_rrhh
-- Permite rastrear la última vez que un empleado confirmó sus
-- datos personales (correo y celular). Se usa para mostrar un
-- modal obligatorio cada 3 meses.
--
-- Ejecutar en MySQL:
--   mysql -u usuario -p < sql/agregar_fecha_confirmacion_datos.sql
-- ============================================================

-- 1. Agregar la columna (nullable para no romper filas existentes)
ALTER TABLE users_rrhh
    ADD COLUMN fecha_confirmacion_datos DATETIME NULL AFTER primer_ingreso;

-- 2. Backfill: inicializar con la fecha actual para empleados existentes.
--    Esto evita que TODOS se les muestre el modal inmediatamente al
--    implementar la funcionalidad. Los que nunca confirmaron tendrán NULL,
--    lo que se interpreta como "nunca ha confirmado" → se muestra el modal.
UPDATE users_rrhh
SET fecha_confirmacion_datos = NOW()
WHERE activo = 1;
