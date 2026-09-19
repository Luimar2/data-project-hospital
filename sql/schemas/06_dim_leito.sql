CREATE TABLE dim_leito (
    id_leito INT PRIMARY KEY AUTO_INCREMENT,

    codigo_leito VARCHAR(20),

    tipo_leito VARCHAR(50),

    setor VARCHAR(100),

    ativo BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;