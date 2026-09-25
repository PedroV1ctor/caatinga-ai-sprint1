"""
bayes.py - Parte 4.3: P(infestado | sensor positivo) e derivados,
usando os parametros do sensor gerados por parametros_sensor(matricula).

Notacao:
    I  = infestado, ~I = nao infestado
    +  = sensor deu positivo
    prevalencia            P(I)
    sensibilidade           P(+ | I)      "taxa de verdadeiro positivo"
    taxa_falso_positivo     P(+ | ~I)
"""

from gerador_pomar import parametros_sensor


def bayes_ppv(prevalencia, sensibilidade, taxa_falso_positivo):
    """Teorema de Bayes / VPP (valor preditivo positivo):
    P(I|+) = P(+|I)P(I) / [P(+|I)P(I) + P(+|~I)P(~I)]"""
    p_i = prevalencia
    p_nao_i = 1 - prevalencia
    numerador = sensibilidade * p_i
    denominador = numerador + taxa_falso_positivo * p_nao_i
    return numerador / denominador


def relatorio_bayes(matricula):
    params = parametros_sensor(matricula)
    prevalencia = params["prevalencia"]
    sensibilidade = params["sensibilidade"]
    fpr = params["taxa_falso_positivo"]
    talhoes_semana = params["talhoes_por_semana"]

    # (a) P(infestado | positivo)
    ppv = bayes_ppv(prevalencia, sensibilidade, fpr)

    # (b) a cada 100 alertas, quantos sao falsos
    falsos_em_100 = round((1 - ppv) * 100, 1)

    # (c) alertas falsos por semana e horas perseguindo alertas falsos
    p_positivo = sensibilidade * prevalencia + fpr * (1 - prevalencia)
    alertas_totais_semana = p_positivo * talhoes_semana
    alertas_falsos_semana = alertas_totais_semana * (1 - ppv)
    minutos_por_inspecao = 12
    horas_gastas_falsos = (alertas_falsos_semana * minutos_por_inspecao) / 60

    # (d) aumentar sensibilidade para 99,9%, mesma taxa de falso positivo
    nova_sensibilidade = 0.999
    novo_ppv = bayes_ppv(prevalencia, nova_sensibilidade, fpr)

    return {
        "parametros": params,
        "ppv_original": ppv,
        "falsos_em_100_alertas": falsos_em_100,
        "alertas_totais_por_semana": alertas_totais_semana,
        "alertas_falsos_por_semana": alertas_falsos_semana,
        "horas_por_semana_em_falsos": horas_gastas_falsos,
        "ppv_com_sensibilidade_99_9": novo_ppv,
        "melhora_no_ppv": novo_ppv - ppv,
    }


if __name__ == "__main__":
    import sys
    m = int(sys.argv[1]) if len(sys.argv) > 1 else 20231045
    r = relatorio_bayes(m)
    p = r["parametros"]
    print(f"matricula = {m}")
    print(f"prevalencia={p['prevalencia']}  sensibilidade={p['sensibilidade']}  "
          f"fpr={p['taxa_falso_positivo']}  talhoes/semana={p['talhoes_por_semana']}")
    print(f"(a) P(infestado|positivo) = {r['ppv_original']:.4f}")
    print(f"(b) a cada 100 alertas, ~{r['falsos_em_100_alertas']} sao falsos")
    print(f"(c) alertas totais/semana={r['alertas_totais_por_semana']:.1f}  "
          f"alertas falsos/semana={r['alertas_falsos_por_semana']:.1f}  "
          f"horas/semana perseguindo falsos={r['horas_por_semana_em_falsos']:.1f}")
    print(f"(d) com sensibilidade=99.9%: novo PPV = {r['ppv_com_sensibilidade_99_9']:.4f} "
          f"(melhora de {r['melhora_no_ppv']:.4f})")
