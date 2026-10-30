-- ============================================================
-- ELIMINAR RESTRICCIÓN UNIQUE EN intentos_evaluacion
-- ============================================================
-- 
-- La tabla intentos_evaluacion tiene un UNIQUE KEY en 
-- (evaluacion_id, estudiante_id) que impide que un estudiante
-- tenga más de un intento por evaluación.
-- 
-- Para permitir hasta 3 intentos, debemos eliminar este UNIQUE KEY.
-- 
-- IMPORTANTE: La FOREIGN KEY en evaluacion_id requiere un índice,
-- por lo que primero creamos un índice normal y luego eliminamos
-- el UNIQUE KEY.
-- ============================================================

-- 1. Crear un índice normal (no único) en evaluacion_id para la FK
ALTER TABLE intentos_evaluacion ADD INDEX idx_evaluacion_id (evaluacion_id);

-- 2. Eliminar el UNIQUE KEY (ya no es necesario)
ALTER TABLE intentos_evaluacion DROP INDEX evaluacion_id;

-- ============================================================
-- Verificar que se eliminó correctamente:
-- SHOW CREATE TABLE intentos_evaluacion;
-- ============================================================
