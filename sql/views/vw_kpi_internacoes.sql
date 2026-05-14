CREATE OR REPLACE VIEW vw_kpi_internacoes AS

SELECT

    dt.ano,
    dt.mes,
    dt.nome_mes,

    COUNT(fi.id_internacao)
        AS total_internacoes,

    ROUND(
        AVG(fi.dias_internado),
        2
    ) AS media_permanencia,

    ROUND(
        AVG(fi.custo_total),
        2
    ) AS custo_medio_internacao,

    ROUND(
        SUM(fi.custo_total),
        2
    ) AS custo_total_hospitalar,

    SUM(
        CASE
            WHEN fi.desfecho = 'Óbito'
            THEN 1
            ELSE 0
        END
    ) AS total_obitos,

    ROUND(
        (
            SUM(
                CASE
                    WHEN fi.desfecho = 'Óbito'
                    THEN 1
                    ELSE 0
                END
            )
            /
            COUNT(fi.id_internacao)
        ) * 100,
        2
    ) AS taxa_mortalidade,

    SUM(
        CASE
            WHEN dc.nome_convenio = 'SUS'
            THEN 1
            ELSE 0
        END
    ) AS internacoes_sus,

    SUM(
        CASE
            WHEN dc.nome_convenio <> 'SUS'
            THEN 1
            ELSE 0
        END
    ) AS internacoes_convenio

FROM fato_internacoes fi

JOIN dim_tempo dt
    ON fi.id_tempo_entrada = dt.id_tempo

JOIN dim_convenio dc
    ON fi.id_convenio = dc.id_convenio

GROUP BY
    dt.ano,
    dt.mes,
    dt.nome_mes;