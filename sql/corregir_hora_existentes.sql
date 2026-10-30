-- ============================================================
-- CORREGIR HORA DE EVALUACIONES EXISTENTES
-- ============================================================
-- Los registros existentes en intentos_evaluacion se guardaron
-- con la hora UTC (5 horas adelantadas a Colombia).
-- Este script resta 5 horas a todas las fechas para corregirlas.
--
-- Ejecutar SOLO UNA VEZ en tu base de datos MySQL.
-- ============================================================

-- Ver cuántos registros se van a afectar (opcional)
SELECT COUNT(*) AS registros_afectados,
       MIN(fecha_presentacion) AS fecha_minima,
       MAX(fecha_presentacion) AS fecha_maxima
FROM intentos_evaluacion;

-- Corregir: restar 5 horas a todas las fechas existentes
UPDATE intentos_evaluacion
SET fecha_presentacion = DATE_SUB(fecha_presentacion, INTERVAL 5 HOUR)
WHERE fecha_presentacion IS NOT NULL;

-- Verificar la corrección (opcional)
SELECT COUNT(*) AS registros_corregidos,
       MIN(fecha_presentacion) AS nueva_fecha_minima,
       MAX(fecha_presentacion) AS nueva_fecha_maxima
FROM intentos_evaluacion;
