CREATE TABLE dim_leito (
    id_leito INT PRIMARY KEY AUTO_INCREMENT,

    codigo_leito VARCHAR(20),

    tipo_leito VARCHAR(50),

    setor VARCHAR(100),

    ativo BOOLEAN DEFAULT TRUE
);