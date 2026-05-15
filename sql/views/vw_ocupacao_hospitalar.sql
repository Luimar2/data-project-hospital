CREATE OR REPLACE VIEW vw_ocupacao_hospitalar AS

SELECT
    dt.data_completa,
    dt.ano,
    dt.mes,
    dt.nome_mes,

    dl.tipo_leito,

    COUNT(fi.id_internacao)
        AS leitos_ocupados,

    total.total_leitos,

    (
        total.total_leitos
        - COUNT(fi.id_internacao)
    ) AS leitos_disponiveis,

    ROUND(
        (
            COUNT(fi.id_internacao)
            / total.total_leitos
        ) * 100,
        2
    ) AS taxa_ocupacao

FROM dim_tempo dt

JOIN fato_internacoes fi
    ON dt.id_tempo
    BETWEEN fi.id_tempo_entrada
    AND fi.id_tempo_alta

JOIN dim_leito dl
    ON fi.id_leito = dl.id_leito

JOIN (
    SELECT
        tipo_leito,
        COUNT(*) AS total_leitos
    FROM dim_leito
    GROUP BY tipo_leito
) total
ON dl.tipo_leito = total.tipo_leito

GROUP BY
    dt.data_completa,
    dt.ano,
    dt.mes,
    dt.nome_mes,
    dl.tipo_leito,
    total.total_leitos;