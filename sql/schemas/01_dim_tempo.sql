CREATE TABLE dim_tempo (
    id_tempo INT PRIMARY KEY AUTO_INCREMENT,
    data_completa DATE NOT NULL,
    dia INT,
    mes INT,
    nome_mes VARCHAR(20),
    trimestre INT,
    ano INT,
    dia_semana VARCHAR(20),
    fim_semana BOOLEAN
);
