-- ============================================================
-- AGREGAR COLUMNA tipo_contrato_id A LA TABLA contratos
-- Permite que cada contrato guarde su propio tipo de contrato,
-- en lugar de heredar siempre el tipo actual del empleado
-- (users_rrhh.tipo_contrato_id).
--
-- Ejecutar en MySQL:
--   mysql -u usuario -p < sql/agregar_tipo_contrato_contratos.sql
-- ============================================================

-- 1. Agregar la columna (nullable para no romper filas existentes)
ALTER TABLE contratos
    ADD COLUMN tipo_contrato_id INT NULL AFTER factor_no_salarial;

-- 2. Backfill: los contratos históricos no guardaban su tipo, por lo que
--    se hereda el tipo ACTUAL del empleado. Los contratos nuevos ya
--    guardarán su propio tipo desde la creación.
UPDATE contratos c
    INNER JOIN users_rrhh u ON c.empleado_id = u.id
SET c.tipo_contrato_id = u.tipo_contrato_id
WHERE c.tipo_contrato_id IS NULL;

-- 3. (Opcional) Índice para agilizar las consultas por tipo
CREATE INDEX idx_contratos_tipo ON contratos (tipo_contrato_id);
