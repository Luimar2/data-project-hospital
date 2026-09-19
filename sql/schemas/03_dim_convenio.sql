CREATE TABLE dim_convenio (
    id_convenio INT PRIMARY KEY AUTO_INCREMENT,
    nome_convenio VARCHAR(100),
    tipo VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
