CREATE TABLE fato_internacoes (
    id_internacao BIGINT PRIMARY KEY AUTO_INCREMENT,

    id_paciente INT NOT NULL,
    id_convenio INT NOT NULL,
    id_leito INT NOT NULL,

    id_tempo_entrada INT NOT NULL,
    id_tempo_alta INT NOT NULL,

    tipo_internacao VARCHAR(50),

    dias_internado INT,

    custo_total DECIMAL(12,2),

    desfecho VARCHAR(50),

    FOREIGN KEY (id_paciente)
        REFERENCES dim_paciente(id_paciente),

    FOREIGN KEY (id_convenio)
        REFERENCES dim_convenio(id_convenio),

    FOREIGN KEY (id_leito)
        REFERENCES dim_leito(id_leito),

    FOREIGN KEY (id_tempo_entrada)
        REFERENCES dim_tempo(id_tempo),

    FOREIGN KEY (id_tempo_alta)
        REFERENCES dim_tempo(id_tempo)
);