CREATE TABLE fato_atendimentos (
    id_atendimento BIGINT PRIMARY KEY AUTO_INCREMENT,

    id_tempo INT,
    id_setor INT,
    id_convenio INT,

    tipo_atendimento VARCHAR(50),
    tempo_espera_min INT,
    valor_atendimento DECIMAL(10,2),

    FOREIGN KEY (id_tempo)
        REFERENCES dim_tempo(id_tempo),

    FOREIGN KEY (id_setor)
        REFERENCES dim_setor(id_setor),

    FOREIGN KEY (id_convenio)
        REFERENCES dim_convenio(id_convenio)
);
