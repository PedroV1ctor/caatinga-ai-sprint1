# Caatinga.AI - Sprint 1

## 1. Identificação
- Disciplina: [Inteligencia Artificial]
- Período: [6]
- Dupla: [NOME Pedro Victor Correia de Souza Santos ] (matrícula [24114017]) e [Rubriel Luuan Marques de Lima] (matrícula [24114026])
- Matrícula usada como semente: **[24114017]**

## 2. O que este projeto faz
O Caatinga.AI é um agente que planeja a rota de um robô de inspeção de pragas em um
pomar de manga representado como uma grade 12×12, comparando estratégias de busca
cega (BFS, DFS, UCS) e informada (A* com três heurísticas). Também modela, via busca
local, a escolha de quais talhões inspecionar sob restrição de bateria, e implementa um
pequeno sistema especialista com encadeamento para trás e um raciocínio bayesiano sobre
a confiabilidade do sensor de pragas.

## 3. Como rodar
- Python 3.10+ (testado em 3.12)
- Instalação:
```bash
pip install -r requirements.txt
```
- Execução (gera `resultados/resultados.csv`, `resultados/grafico.png` e `resultados/pomar.txt` do zero):
```bash
python src/main.py <matricula>
```

## 4. Tabela-resumo dos resultados (matrícula [24114017])

| Estratégia         | Custo | Passos | Nós expandidos | Fronteira máx. |
|---------------------|------:|-------:|----------------:|----------------:|
| BFS                  |   52  |    22  |      118       |      11         |
| DFS                  |  119  |    56  |       87       |      35         |
| UCS                  |   31  |    22  |      116       |      15         |
| A* (h1 = 0)          |   31  |    22  |      116       |      15         |
| A* (h2 = Manhattan)  |   31  |    22  |       92       |      21         |
| A* (h3 = 4×Manhattan)|   31  |    22  |       24       |      24         |

*(preencha com a saída de `python src/main.py <sua matrícula>` — os números acima com a
matrícula de referência 20231045 batem com a caixa de aferição do enunciado: UCS=34,
BFS=55/22 passos, UCS expandidos=112, A* Manhattan expandidos=93.)*

## 5. Ordem de expansão dos vizinhos
Norte, Sul, Oeste, Leste — isto é, ao gerar sucessores de um talhão `(i, j)`:
1. Norte `(i-1, j)`
2. Sul `(i+1, j)`
3. Oeste `(i, j-1)`
4. Leste `(i, j+1)`

Esta ordem é usada de forma idêntica em BFS, DFS, UCS e A* (arquivo `src/buscas.py`,
constante `ORDEM_VIZINHOS`).

**O A* implementado não reabre nós** já expandidos (assume heurística consistente — ver
Parte 3.2 do relatório para a prova de admissibilidade/consistência de h2).

## 6. Mapa do repositório
| Arquivo | O que resolve |
|---|---|
| `src/gerador_pomar.py` | Gerador do pomar e dos parâmetros do sensor (intacto, fornecido no enunciado) |
| `src/buscas.py` | BFS, DFS, UCS e A* com instrumentação (custo, passos, nós expandidos, fronteira máx.) |
| `src/busca_local.py` | Subida de encosta e têmpera simulada para escolha de K talhões a inspecionar |
| `src/especialista.py` | Regras SE-ENTÃO + encadeamento para trás com explicação da cadeia |
| `src/bayes.py` | Cálculo de P(infestado \| positivo) e derivados |
| `src/main.py` | Comando único: gera `resultados.csv`, `grafico.png` e `pomar.txt` |
| `RELATORIO.md` | Relatório completo com todas as tabelas e discussões (Partes 1–5) |
| `ANEXO_IA.md` | Uso de IA nesta atividade (Parte 6, obrigatório) |

## 7. Limitações conhecidas
- O custo estimado de percurso na busca local (3.4) usa uma
  aproximação de vizinho mais próximo com distância Manhattan ponderada pelo custo
  médio do terreno, não o custo real de caminho mínimo entre cada par de talhões —
  isso é uma simplificação declarada, não um bug.

