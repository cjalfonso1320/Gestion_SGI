-- Tabla para el Buzón de Mensajes (Mensajería RRHH)
-- Almacena los mensajes enviados a cada empleado para que puedan
-- consultarlos desde los módulos SGI, RRHH y Aula Virtual.

USE gestion_sgi;

CREATE TABLE IF NOT EXISTS buzon_mensajes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    empleado_id INT NOT NULL,
    asunto VARCHAR(200) NOT NULL,
    mensaje_html TEXT,
    leido TINYINT(1) DEFAULT 0,
    fecha_envio DATETIME DEFAULT CURRENT_TIMESTAMP,
    enviado_por_id INT DEFAULT NULL,
    enviado_por_nombre VARCHAR(200) DEFAULT NULL,
    INDEX idx_empleado (empleado_id),
    INDEX idx_leido (empleado_id, leido),
    FOREIGN KEY (empleado_id) REFERENCES users_rrhh(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
