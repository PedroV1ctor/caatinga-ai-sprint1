"""
main.py - comando unico exigido pelo enunciado (Secao 9.1, regra 4):
    python src/main.py <matricula>

Gera, do zero:
    resultados/resultados.csv
    resultados/grafico.png
    resultados/pomar.txt
"""

import sys
import os
import time
import csv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from gerador_pomar import gerar_pomar, parametros_sensor
import buscas
import busca_local
import especialista
import bayes


def main(matricula):
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pasta_resultados = os.path.join(raiz, "resultados")
    os.makedirs(pasta_resultados, exist_ok=True)

    grid = gerar_pomar(matricula)
    n = len(grid)
    inicio, objetivo = (0, 0), (n - 1, n - 1)

    # ---- pomar.txt ----
    with open(os.path.join(pasta_resultados, "pomar.txt"), "w") as f:
        f.write(f"{matricula}\n")
        for linha in grid:
            f.write(" ".join(linha) + "\n")

    # ---- Parte 2: BFS, DFS, UCS ----
    linhas_csv = []

    def roda(nome_estrategia, nome_heuristica, funcao, *args):
        t0 = time.perf_counter()
        r = funcao(*args)
        tempo_ms = (time.perf_counter() - t0) * 1000
        linhas_csv.append({
            "estrategia": nome_estrategia,
            "heuristica": nome_heuristica,
            "custo": r["custo"],
            "passos": r["passos"],
            "nos_expandidos": r["expandidos"],
            "fronteira_max": r["fronteira_max"],
            "tempo_ms": round(tempo_ms, 3),
        })
        return r

    r_bfs = roda("BFS", "", buscas.bfs, grid, inicio, objetivo)
    r_dfs = roda("DFS", "", buscas.dfs, grid, inicio, objetivo)
    r_ucs = roda("UCS", "", buscas.ucs, grid, inicio, objetivo)

    # ---- Parte 3: A* com h1, h2, h3 ----
    r_h1 = roda("A*", "h1=0", buscas.astar, grid, inicio, objetivo, lambda s, o: 0)
    r_h2 = roda("A*", "h2=Manhattan", buscas.astar, grid, inicio, objetivo, buscas.manhattan)
    r_h3 = roda("A*", "h3=4xManhattan", buscas.astar, grid, inicio, objetivo,
                lambda s, o: 4 * buscas.manhattan(s, o))

    # ---- resultados.csv ----
    caminho_csv = os.path.join(pasta_resultados, "resultados.csv")
    with open(caminho_csv, "w", newline="") as f:
        campos = ["estrategia", "heuristica", "custo", "passos",
                  "nos_expandidos", "fronteira_max", "tempo_ms"]
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        for linha in linhas_csv:
            w.writerow(linha)

    # ---- grafico.png: nos expandidos x estrategia ----
    rotulos = [f"{l['estrategia']}\n{l['heuristica']}".strip() for l in linhas_csv]
    valores = [l["nos_expandidos"] for l in linhas_csv]

    fig, ax = plt.subplots(figsize=(9, 5))
    barras = ax.bar(rotulos, valores, color="#4a7c59")
    ax.set_xlabel("Estrategia de busca")
    ax.set_ylabel("Numero de nos expandidos")
    ax.set_title(f"Nos expandidos por estrategia - Caatinga.AI (matricula {matricula})")
    ax.bar_label(barras, padding=3)
    fig.tight_layout()
    fig.savefig(os.path.join(pasta_resultados, "grafico.png"), dpi=150)
    plt.close(fig)

    # ---- resumo no terminal ----
    print(f"\n=== Caatinga.AI - matricula {matricula} (pomar {n}x{n}) ===\n")
    print(f"{'Estrategia':<16}{'Custo':>8}{'Passos':>8}{'Expandidos':>12}{'Fronteira max':>16}")
    for l in linhas_csv:
        nome = f"{l['estrategia']} {l['heuristica']}".strip()
        print(f"{nome:<16}{l['custo']:>8}{l['passos']:>8}{l['nos_expandidos']:>12}{l['fronteira_max']:>16}")

    print(f"\nArquivos gerados em {pasta_resultados}/:")
    print("  - pomar.txt")
    print("  - resultados.csv")
    print("  - grafico.png")

    # ---- Parte 3.4: busca local ----
    print("\n=== Parte 3.4 - Busca local (K=15, 30 execucoes) ===")
    rl = busca_local.rodar_experimento(matricula)
    print(f"Limite de bateria: {rl['limite_unidades_bateria']:.1f} unidades de custo")
    print(f"Subida de encosta : media={rl['hill_climbing']['media']:.3f}  "
          f"desvio={rl['hill_climbing']['desvio']:.3f}  melhor={rl['hill_climbing']['melhor']:.3f}")
    print(f"Tempera simulada  : media={rl['tempera_simulada']['media']:.3f}  "
          f"desvio={rl['tempera_simulada']['desvio']:.3f}  melhor={rl['tempera_simulada']['melhor']:.3f}")

    # ---- Parte 4.1/4.2: sistema especialista (demonstracao) ----
    print("\n=== Parte 4.1/4.2 - Sistema especialista (ver especialista.py para o traco completo) ===")
    fatos = {"armadilha_positiva", "umidade_alta", "dias_desde_pulverizacao_maior_14"}
    especialista.explicar("inspecionar_prioridade_alta", fatos)

    # ---- Parte 4.3: Bayes ----
    print("\n=== Parte 4.3 - Bayes ===")
    rb = bayes.relatorio_bayes(matricula)
    print(f"P(infestado|positivo) = {rb['ppv_original']:.4f}")
    print(f"A cada 100 alertas, ~{rb['falsos_em_100_alertas']} sao falsos")
    print(f"Horas/semana perseguindo falsos: {rb['horas_por_semana_em_falsos']:.1f}")
    print(f"Com sensibilidade 99.9%: novo VPP = {rb['ppv_com_sensibilidade_99_9']:.4f} "
          f"(melhora de {rb['melhora_no_ppv']:.4f})")

    print("\nOK - execucao completa.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("uso: python src/main.py <matricula>")
        sys.exit(1)
    main(int(sys.argv[1]))
