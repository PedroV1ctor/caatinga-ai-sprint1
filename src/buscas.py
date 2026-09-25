"""
buscas.py - BFS, DFS, UCS e A* para o Caatinga.AI (Sprint 1)

Ordem de expansao dos vizinhos declarada: Norte, Sul, Oeste, Leste
    Norte = (i-1, j)
    Sul   = (i+1, j)
    Oeste = (i, j-1)
    Leste = (i, j+1)

Todas as estratégias usam BUSCA EM GRAFO (mantêm um conjunto de estados já
visitados/expandidos). Isso é obrigatório: como o mesmo talhão (estado) pode
ser alcançado por caminhos diferentes (nós diferentes), uma busca em ÁRVORE
pura entraria em laço infinito na grade (ida e volta entre dois talhões).

Convenções de instrumentação (mesmas para as quatro estratégias):
    - "nós expandidos": incrementado quando um nó é RETIRADO da fronteira e
      efetivamente processado (vizinhos gerados). Nós descartados por já
      estarem no conjunto de expandidos (custo pior) não contam.
    - "fronteira máxima": maior tamanho que a estrutura de fronteira atingiu
      em QUALQUER momento da execução (não o tamanho final).
    - teste de objetivo é feito na EXPANSÃO do nó (ao retirá-lo da fronteira),
      não na geração. Isso é importante para BFS/UCS/A* ficarem corretos.
"""

from collections import deque
import heapq
import itertools
from gerador_pomar import CUSTO, BLOQUEADO

ORDEM_VIZINHOS = [(-1, 0, "N"), (1, 0, "S"), (0, -1, "O"), (0, 1, "L")]


def vizinhos(grid, estado):
    n = len(grid)
    i, j = estado
    for di, dj, _ in ORDEM_VIZINHOS:
        ni, nj = i + di, j + dj
        if 0 <= ni < n and 0 <= nj < n and grid[ni][nj] != BLOQUEADO:
            custo = CUSTO[grid[ni][nj]]
            yield (ni, nj), custo


def reconstruir_caminho(veio_de, estado):
    caminho = [estado]
    while estado in veio_de:
        estado = veio_de[estado]
        caminho.append(estado)
    caminho.reverse()
    return caminho


def bfs(grid, inicio, objetivo):
    """Busca em largura. Otima em NUMERO DE PASSOS, nao em custo."""
    fronteira = deque([inicio])
    veio_de = {}
    visitados = {inicio}
    expandidos = 0
    fronteira_max = 1

    while fronteira:
        fronteira_max = max(fronteira_max, len(fronteira))
        estado = fronteira.popleft()
        expandidos += 1

        if estado == objetivo:
            caminho = reconstruir_caminho(veio_de, estado)
            custo = sum(CUSTO[grid[i][j]] for (i, j) in caminho[1:])
            return {
                "caminho": caminho, "custo": custo, "passos": len(caminho) - 1,
                "expandidos": expandidos, "fronteira_max": fronteira_max,
            }

        for prox, _ in vizinhos(grid, estado):
            if prox not in visitados:
                visitados.add(prox)
                veio_de[prox] = estado
                fronteira.append(prox)

    return None


def dfs(grid, inicio, objetivo):
    """Busca em profundidade (em GRAFO, com conjunto de visitados)."""
    fronteira = [inicio]
    veio_de = {}
    visitados = {inicio}
    expandidos = 0
    fronteira_max = 1

    while fronteira:
        fronteira_max = max(fronteira_max, len(fronteira))
        estado = fronteira.pop()
        expandidos += 1

        if estado == objetivo:
            caminho = reconstruir_caminho(veio_de, estado)
            custo = sum(CUSTO[grid[i][j]] for (i, j) in caminho[1:])
            return {
                "caminho": caminho, "custo": custo, "passos": len(caminho) - 1,
                "expandidos": expandidos, "fronteira_max": fronteira_max,
            }

        # empilha em ordem REVERSA para que N seja o topo da pilha
        # (ou seja, o primeiro a ser desempilhado / explorado)
        vizs = list(vizinhos(grid, estado))
        for prox, _ in reversed(vizs):
            if prox not in visitados:
                visitados.add(prox)
                veio_de[prox] = estado
                fronteira.append(prox)

    return None


def ucs(grid, inicio, objetivo):
    """Busca de custo uniforme (Dijkstra)."""
    contador = itertools.count()
    fronteira = [(0, next(contador), inicio)]
    veio_de = {}
    custo_g = {inicio: 0}
    expandidos_set = set()
    expandidos = 0
    fronteira_max = 1

    while fronteira:
        fronteira_max = max(fronteira_max, len(fronteira))
        g, _, estado = heapq.heappop(fronteira)

        if estado in expandidos_set:
            continue  # entrada obsoleta na fila (custo pior), nao conta
        expandidos_set.add(estado)
        expandidos += 1

        if estado == objetivo:
            caminho = reconstruir_caminho(veio_de, estado)
            return {
                "caminho": caminho, "custo": g, "passos": len(caminho) - 1,
                "expandidos": expandidos, "fronteira_max": fronteira_max,
            }

        for prox, custo in vizinhos(grid, estado):
            novo_g = g + custo
            if prox not in custo_g or novo_g < custo_g[prox]:
                custo_g[prox] = novo_g
                veio_de[prox] = estado
                heapq.heappush(fronteira, (novo_g, next(contador), prox))

    return None


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(grid, inicio, objetivo, heuristica):
    """A* generico. heuristica(estado, objetivo) -> float.
    NAO reabre nos ja expandidos (assume heuristica consistente)."""
    contador = itertools.count()
    h0 = heuristica(inicio, objetivo)
    fronteira = [(h0, 0, next(contador), inicio)]
    veio_de = {}
    custo_g = {inicio: 0}
    expandidos_set = set()
    expandidos = 0
    fronteira_max = 1

    while fronteira:
        fronteira_max = max(fronteira_max, len(fronteira))
        f, g, _, estado = heapq.heappop(fronteira)

        if estado in expandidos_set:
            continue
        expandidos_set.add(estado)
        expandidos += 1

        if estado == objetivo:
            caminho = reconstruir_caminho(veio_de, estado)
            return {
                "caminho": caminho, "custo": g, "passos": len(caminho) - 1,
                "expandidos": expandidos, "fronteira_max": fronteira_max,
            }

        for prox, custo in vizinhos(grid, estado):
            novo_g = g + custo
            if prox not in custo_g or novo_g < custo_g[prox]:
                custo_g[prox] = novo_g
                veio_de[prox] = estado
                novo_f = novo_g + heuristica(prox, objetivo)
                heapq.heappush(fronteira, (novo_f, novo_g, next(contador), prox))

    return None


if __name__ == "__main__":
    import sys
    from gerador_pomar import gerar_pomar

    m = int(sys.argv[1]) if len(sys.argv) > 1 else 20231045
    grid = gerar_pomar(m)
    n = len(grid)
    inicio, objetivo = (0, 0), (n - 1, n - 1)

    r_bfs = bfs(grid, inicio, objetivo)
    r_dfs = dfs(grid, inicio, objetivo)
    r_ucs = ucs(grid, inicio, objetivo)
    r_h0 = astar(grid, inicio, objetivo, lambda s, o: 0)
    r_h2 = astar(grid, inicio, objetivo, manhattan)
    r_h3 = astar(grid, inicio, objetivo, lambda s, o: 4 * manhattan(s, o))

    print(f"matricula = {m}")
    print(f"BFS : custo={r_bfs['custo']:>4} passos={r_bfs['passos']:>3} "
          f"expandidos={r_bfs['expandidos']:>4} fronteira_max={r_bfs['fronteira_max']:>4}")
    print(f"DFS : custo={r_dfs['custo']:>4} passos={r_dfs['passos']:>3} "
          f"expandidos={r_dfs['expandidos']:>4} fronteira_max={r_dfs['fronteira_max']:>4}")
    print(f"UCS : custo={r_ucs['custo']:>4} passos={r_ucs['passos']:>3} "
          f"expandidos={r_ucs['expandidos']:>4} fronteira_max={r_ucs['fronteira_max']:>4}")
    print(f"A* h1=0        : custo={r_h0['custo']:>4} expandidos={r_h0['expandidos']:>4}")
    print(f"A* h2=Manhattan: custo={r_h2['custo']:>4} expandidos={r_h2['expandidos']:>4}")
    print(f"A* h3=4xManhat.: custo={r_h3['custo']:>4} expandidos={r_h3['expandidos']:>4}")
