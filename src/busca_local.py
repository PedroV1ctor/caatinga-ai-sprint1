"""
busca_local.py - Parte 3.4: escolher quais K talhoes inspecionar com bateria
limitada, modelado como busca local.

MODELAGEM
---------
Estado:      um subconjunto de tamanho K de talhoes livres (nao bloqueados)
             do pomar. Representado como uma tupla ordenada de coordenadas.
Vizinhanca:  trocar (swap) UM talhao do estado por UM talhao livre que esta
             fora do estado. Cada estado tem ate K * (L - K) vizinhos, onde L
             e o numero total de talhoes livres.
Funcao objetivo (a maximizar):
    objetivo(estado) = soma_risco(estado) - PENALIDADE * excesso_bateria(estado)

    - soma_risco(estado): soma de um escore de risco de praga por talhao
      (determinístico, derivado da matricula e da posicao - simula a saida
      do sensor optico de deteccao de pragas).
    - excesso_bateria(estado) = max(0, custo_estimado_percurso(estado) - LIMITE)
      custo_estimado_percurso: tour guloso do vizinho mais proximo (nearest
      neighbor), partindo do portao (0,0), visitando os K talhoes do estado,
      em unidades de custo de deslocamento (mesma unidade da Parte 2).
      LIMITE: quantas unidades de custo cabem nas 6 horas de bateria, dado
      que assumimos T_UNIDADE minutos de deslocamento por unidade de custo
      (premissa declarada abaixo - ajuste se o enunciado da sua dupla
      especificar outro valor).

Isso cria uma paisagem de busca real: aumentar o risco total tende a exigir
talhoes mais espalhados, o que aumenta o custo do percurso e pode estourar a
bateria (penalidade). O objetivo tem vales e picos -> boa demonstracao de por
que a tempera simulada aceita piora de proposito (Aula 04): ela escapa de
otimos locais em que a subida de encosta greedy fica presa.
"""

import math
import random
import statistics
from gerador_pomar import gerar_pomar, CUSTO, BLOQUEADO

# ---- premissas declaradas (documentar no relatorio) ----
T_UNIDADE_MINUTOS = 3          # minutos gastos por unidade de custo de deslocamento
BATERIA_MINUTOS = 6 * 60       # 6 horas de bateria
LIMITE_UNIDADES = BATERIA_MINUTOS / T_UNIDADE_MINUTOS  # 120 unidades de custo
PENALIDADE = 0.08              # perda de "valor" por unidade de custo excedente
K = 15


def talhoes_livres(grid):
    n = len(grid)
    return [(i, j) for i in range(n) for j in range(n) if grid[i][j] != BLOQUEADO]


def risco_por_talhao(grid, matricula):
    """Escore de risco deterministico por talhao, derivado da matricula.
    Representa a saida do sensor optico (quanto maior, mais suspeito)."""
    risco = {}
    for i in range(len(grid)):
        for j in range(len(grid)):
            if grid[i][j] != BLOQUEADO:
                seed = (matricula % 1_000_000) * 10_000 + i * 100 + j
                risco[(i, j)] = random.Random(seed).uniform(0.0, 1.0)
    return risco


def custo_tour_vizinho_mais_proximo(grid, estado, origem=(0, 0)):
    """Estimativa (heuristica) do custo do percurso: tour guloso do vizinho
    mais proximo, usando distancia Manhattan ponderada pelo custo medio do
    terreno como proxy do custo real de deslocamento entre talhoes."""
    custo_medio_terreno = 1.85  # entre 1 (carreador) e 4 (encharcado), aprox.
    restantes = list(estado)
    atual = origem
    total = 0.0
    while restantes:
        prox = min(restantes, key=lambda t: abs(t[0] - atual[0]) + abs(t[1] - atual[1]))
        dist = abs(prox[0] - atual[0]) + abs(prox[1] - atual[1])
        total += dist * custo_medio_terreno
        atual = prox
        restantes.remove(prox)
    return total


def objetivo(grid, estado, risco):
    soma_risco = sum(risco[t] for t in estado)
    custo = custo_tour_vizinho_mais_proximo(grid, estado)
    excesso = max(0.0, custo - LIMITE_UNIDADES)
    return soma_risco - PENALIDADE * excesso


def estado_inicial(livres, k, rng):
    return tuple(rng.sample(livres, k))


def vizinho_swap(estado, livres, rng):
    estado = list(estado)
    fora = [t for t in livres if t not in estado]
    if not fora:
        return tuple(estado)
    idx_sai = rng.randrange(len(estado))
    entra = rng.choice(fora)
    estado[idx_sai] = entra
    return tuple(estado)


def subida_de_encosta(grid, livres, risco, rng, k=K, max_iter=300, vizinhos_por_iter=20):
    estado = estado_inicial(livres, k, rng)
    valor = objetivo(grid, estado, risco)
    for _ in range(max_iter):
        melhor_vizinho, melhor_valor = None, valor
        for _ in range(vizinhos_por_iter):
            cand = vizinho_swap(estado, livres, rng)
            v = objetivo(grid, cand, risco)
            if v > melhor_valor:
                melhor_vizinho, melhor_valor = cand, v
        if melhor_vizinho is None:
            break  # otimo local: nenhum vizinho amostrado melhora
        estado, valor = melhor_vizinho, melhor_valor
    return estado, valor


def tempera_simulada(grid, livres, risco, rng, k=K, max_iter=1500,
                      t0=1.0, alpha=0.995):
    estado = estado_inicial(livres, k, rng)
    valor = objetivo(grid, estado, risco)
    melhor_estado, melhor_valor = estado, valor
    t = t0
    for _ in range(max_iter):
        cand = vizinho_swap(estado, livres, rng)
        v = objetivo(grid, cand, risco)
        delta = v - valor
        if delta > 0 or rng.random() < math.exp(delta / max(t, 1e-9)):
            # aceita, inclusive quando delta < 0 (piora de proposito)
            estado, valor = cand, v
            if valor > melhor_valor:
                melhor_estado, melhor_valor = estado, valor
        t *= alpha
    return melhor_estado, melhor_valor


def rodar_experimento(matricula, n_execucoes=30, k=K, seed_base=0):
    grid = gerar_pomar(matricula)
    livres = talhoes_livres(grid)
    risco = risco_por_talhao(grid, matricula)

    resultados_hc, resultados_sa = [], []
    aceitou_piora_exemplos = []

    for exec_i in range(n_execucoes):
        rng = random.Random((matricula % 1_000_000) + seed_base + exec_i)
        _, v_hc = subida_de_encosta(grid, livres, risco, rng, k=k)
        resultados_hc.append(v_hc)

        rng2 = random.Random((matricula % 1_000_000) + seed_base + 500 + exec_i)
        # instrumenta uma execucao para mostrar aceite de piora
        estado = estado_inicial(livres, k, rng2)
        valor = objetivo(grid, estado, risco)
        melhor_estado, melhor_valor = estado, valor
        t, t0, alpha = 1.0, 1.0, 0.995
        pioras_aceitas = 0
        for _ in range(1500):
            cand = vizinho_swap(estado, livres, rng2)
            v = objetivo(grid, cand, risco)
            delta = v - valor
            if delta > 0:
                estado, valor = cand, v
            elif rng2.random() < math.exp(delta / max(t, 1e-9)):
                pioras_aceitas += 1
                estado, valor = cand, v
            if valor > melhor_valor:
                melhor_estado, melhor_valor = estado, valor
            t *= alpha
        resultados_sa.append(melhor_valor)
        aceitou_piora_exemplos.append(pioras_aceitas)

    def resumo(vals):
        return {
            "media": statistics.mean(vals),
            "desvio": statistics.pstdev(vals),
            "melhor": max(vals),
        }

    return {
        "hill_climbing": resumo(resultados_hc),
        "tempera_simulada": resumo(resultados_sa),
        "pioras_aceitas_por_execucao_sa": aceitou_piora_exemplos,
        "limite_unidades_bateria": LIMITE_UNIDADES,
    }


if __name__ == "__main__":
    import sys
    m = int(sys.argv[1]) if len(sys.argv) > 1 else 20231045
    r = rodar_experimento(m)
    print(f"matricula = {m}, K = {K}, limite de bateria = {r['limite_unidades_bateria']:.1f} unidades de custo")
    print("Subida de encosta (30 execucoes):", r["hill_climbing"])
    print("Tempera simulada  (30 execucoes):", r["tempera_simulada"])
    print("Nº de pioras aceitas por execucao (SA), primeiras 10:",
          r["pioras_aceitas_por_execucao_sa"][:10])
