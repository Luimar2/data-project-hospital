CREATE OR REPLACE VIEW vw_kpi_atendimentos AS

SELECT

    STR_TO_DATE(
        CONCAT(
            dt.ano,
            '-',
            LPAD(dt.mes,2,'0'),
            '-01'
        ),
        '%Y-%m-%d'
    ) AS data_mes,

    dt.ano,
    dt.mes,
    dt.nome_mes,

    COUNT(fa.id_atendimento)
        AS total_atendimentos,

    ROUND(
        AVG(fa.tempo_espera_min),
        2
    ) AS tempo_medio_espera,

    ROUND(
        SUM(fa.valor_atendimento),
        2
    ) AS faturamento_total,

    ROUND(
        AVG(fa.valor_atendimento),
        2
    ) AS ticket_medio,

    SUM(
        CASE
            WHEN dc.nome_convenio = 'SUS'
            THEN 1
            ELSE 0
        END
    ) AS atendimentos_sus,

    SUM(
        CASE
            WHEN dc.nome_convenio <> 'SUS'
            THEN 1
            ELSE 0
        END
    ) AS atendimentos_convenio

FROM fato_atendimentos fa

JOIN dim_tempo dt
    ON fa.id_tempo = dt.id_tempo

JOIN dim_convenio dc
    ON fa.id_convenio = dc.id_convenio

GROUP BY
    dt.ano,
    dt.mes,
    dt.nome_mes;