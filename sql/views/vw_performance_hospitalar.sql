CREATE OR REPLACE VIEW vw_performance_hospitalar AS

SELECT

    a.ano,
    a.mes,
    a.nome_mes,

    a.total_atendimentos,

    i.total_internacoes,

    a.faturamento_total,

    a.tempo_medio_espera,

    i.media_permanencia,

    i.taxa_mortalidade

FROM vw_kpi_atendimentos a

JOIN vw_kpi_internacoes i
    ON a.ano = i.ano
    AND a.mes = i.mes;