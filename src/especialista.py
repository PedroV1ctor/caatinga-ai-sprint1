"""
especialista.py - Parte 4.1 e 4.2: mini sistema especialista para manejo de
talhao, com encadeamento para tras (backward chaining) e explicacao da
cadeia de regras que sustentou a conclusao.

Representacao: cada regra e (nome, [premissas], conclusao).
Uma premissa ou conclusao e uma string "fato" (ex.: "armadilha_positiva").
Fatos podem ser: conhecidos diretamente (fornecidos pelo usuario/sensor) ou
derivados por OUTRA regra (sub-objetivo), recursivamente.
"""

REGRAS = [
    ("R1", ["armadilha_positiva", "umidade_alta", "dias_desde_pulverizacao_maior_14"],
     "inspecionar_prioridade_alta"),

    ("R2", ["terreno_encharcado", "chuva_recente"],
     "risco_fungo_alto"),

    ("R3", ["risco_fungo_alto", "sem_pulverizacao_recente"],
     "inspecionar_prioridade_alta"),

    ("R4", ["armadilha_positiva", "umidade_baixa"],
     "monitorar_proxima_semana"),

    ("R5", ["talhao_bloqueado"],
     "nao_inspecionar"),

    ("R6", ["inspecionar_prioridade_alta", "historico_infestacao_no_talhao"],
     "acionar_equipe_campo_imediato"),

    ("R7", ["vizinho_com_infestacao_confirmada", "distancia_menor_que_2_talhoes"],
     "risco_contagio_alto"),

    ("R8", ["risco_contagio_alto", "sem_barreira_fisica"],
     "inspecionar_prioridade_alta"),
]


def encadeamento_para_tras(objetivo, fatos_conhecidos, regras=REGRAS, _profundidade=0):
    """Tenta provar `objetivo`.
    Retorna (True/False, cadeia) onde cadeia e a lista de passos usados
    (para imprimir 'por que voce concluiu isso?')."""
    if objetivo in fatos_conhecidos:
        return True, [f"FATO conhecido: {objetivo}"]

    for nome, premissas, conclusao in regras:
        if conclusao != objetivo:
            continue
        cadeia_regra = [f"Tentando {nome}: SE {' E '.join(premissas)} ENTAO {conclusao}"]
        todas_provadas = True
        for premissa in premissas:
            ok, sub_cadeia = encadeamento_para_tras(premissa, fatos_conhecidos, regras, _profundidade + 1)
            cadeia_regra.extend(["    " + linha for linha in sub_cadeia])
            if not ok:
                todas_provadas = False
                cadeia_regra.append(f"    FALHOU: premissa '{premissa}' nao provada")
                break
        if todas_provadas:
            cadeia_regra.append(f"=> {nome} disparada: {conclusao} PROVADO")
            return True, cadeia_regra
        # tenta a proxima regra que conclui o mesmo objetivo

    return False, [f"Nenhuma regra prova '{objetivo}' com os fatos disponiveis"]


def explicar(objetivo, fatos_conhecidos, regras=REGRAS):
    ok, cadeia = encadeamento_para_tras(objetivo, fatos_conhecidos, regras)
    print(f"\nObjetivo: {objetivo}  ->  {'PROVADO' if ok else 'NAO PROVADO'}")
    print("Cadeia de raciocinio:")
    for linha in cadeia:
        print("  " + linha)
    return ok


if __name__ == "__main__":
    # ---- Caso 1: cenario normal, cobre pelas regras existentes ----
    fatos_1 = {"armadilha_positiva", "umidade_alta", "dias_desde_pulverizacao_maior_14"}
    explicar("inspecionar_prioridade_alta", fatos_1)

    # ---- Parte 4.2: caso legitimo que a base classifica ERRADO ----
    # Talhao com fungo por encharcamento + chuva, MAS sem pulverizacao
    # recente e SEM passar por armadilha (a base so teria R1/R3 pra isso).
    # Se a regra R3 nao existisse, este caso passaria batido: alto risco de
    # fungo (terreno encharcado + chuva recente) mas sem pulverizacao nao
    # gera prioridade alta, so seria pego por acaso.
    print("\n--- Traco ANTES da correcao (sem R3, simulando a base quebrada) ---")
    regras_sem_r3 = [r for r in REGRAS if r[0] != "R3"]
    fatos_2 = {"terreno_encharcado", "chuva_recente", "sem_pulverizacao_recente"}
    explicar("inspecionar_prioridade_alta", fatos_2, regras_sem_r3)

    print("\n--- Traco DEPOIS da correcao (com R2 + R3 na base) ---")
    explicar("inspecionar_prioridade_alta", fatos_2, REGRAS)
