CREATE OR REPLACE VIEW vw_performance_hospitalar AS

SELECT
    STR_TO_DATE(
        CONCAT(a.ano, '-', LPAD(a.mes, 2, '0'), '-01'),
        '%Y-%m-%d'
    ) AS data_mes,

    a.ano,
    a.mes,
    a.nome_mes,

    a.total_atendimentos,
    i.total_internacoes,

    a.faturamento_total,
    a.ticket_medio,
    a.tempo_medio_espera,

    i.media_permanencia,
    i.custo_medio_internacao,
    i.custo_medio_diario,
    i.taxa_mortalidade

FROM vw_kpi_atendimentos a

JOIN vw_kpi_internacoes i
    ON a.ano = i.ano
    AND a.mes = i.mes;