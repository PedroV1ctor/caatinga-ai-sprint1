# Relatório - Caatinga.AI - Sprint 1

> Este relatório é um ESQUELETO guiado. As tabelas com números vocês preenchem
> rodando `python src/main.py <matrícula>`. As perguntas teóricas (marcadas com
> ✍️) são para vocês responderem com as próprias palavras — são justamente o
> que a arguição de 10 minutos vai cobrar, então não adianta copiar sem entender.

## Parte 1 — O agente antes do código (0,9 ponto)

### 1.1 Ficha PEAS
| Componente | Descrição |
|---|---|
| **P**erformance | ✍️ (precisa ser métrica mensurável, com unidade — ex. "custo total de deslocamento em unidades de terreno" + "nº de talhões infestados não detectados por semana". NÃO escreva algo como "inspecionar bem".) |
| **A**mbiente | O pomar 12×12, com talhões `.` `~` `#`, portão em (0,0), ponto de coleta em (11,11) |
| **A**tuadores | ✍️ (mover N/S/L/O, acionar sensor óptico, sinalizar talhão suspeito...) |
| **S**ensores | ✍️ (câmera/sensor óptico, posição atual, tipo do talhão adjacente...) |

### 1.2 Classificação do ambiente (seis dimensões)
| Dimensão | Classificação | Frase do cenário que sustenta |
|---|---|---|
| Observável | ✍️ | |
| Determinístico | ✍️ | |
| Episódico | ✍️ | |
| Estático | ✍️ | |
| Discreto | ✍️ | |
| Agente único | ✍️ | |

✍️ **Duas dimensões discutíveis:** identifique quais e qual informação faltante no
enunciado decidiria a questão (dica: pense se há outros agentes/pessoas no pomar
durante a inspeção, e se o estado do pomar pode mudar enquanto o agente se move).

### 1.3 Tipo de agente
✍️ Escolha entre: reativo simples, reativo baseado em modelo, baseado em objetivos,
baseado em utilidade, ou que aprende. Justifique com uma característica CONCRETA do
Caatinga.AI que exige aquele tipo (não "é o mais completo").

### 1.4 Métrica perversa
✍️ Proponha uma métrica de desempenho plausível que, otimizada sem cuidado, gera um
comportamento ruim específico. Descreva:
- a métrica proposta;
- o comportamento concreto que o agente aprenderia;
- em que ponto do pomar isso apareceria (pode usar coordenadas do seu pomar gerado);
- a correção da métrica.

---

## Parte 2 — Formulação e busca cega (1,2 ponto)

### 2.1 Componentes do problema de busca
| Componente | Definição para o Caatinga.AI |
|---|---|
| Estado inicial | (0, 0) |
| Ações | Mover para Norte, Sul, Oeste ou Leste, se o talhão destino existir na grade e não for `#` |
| Modelo de transição | ✍️ |
| Teste de objetivo | estado == (11, 11) |
| Custo do caminho | soma dos custos dos talhões em que entra (1 para `.`, 4 para `~`) |

**Quantos estados tem o espaço?** O pomar tem 12×12 = 144 talhões no total. Contando
a grade gerada pela matrícula 24114017, **26 talhões são bloqueados (`#`)**, restando
**118 talhões livres**. Como cada estado do problema é a posição do agente em um
talhão livre (não é possível estar sobre um talhão bloqueado), **o espaço de estados
tem 118 estados**.

### 2.2 BFS, DFS, UCS — tabela de resultados
Rode: `python src/main.py <matrícula>` (ou `python src/buscas.py <matrícula>` para ver
só esta parte) e preencha:

| Estratégia | Custo da rota | Nº de passos | Nós expandidos | Fronteira máx. | Rota é ótima em custo? |
|---|---:|---:|---:|---:|---|
| BFS | 52 | 22 | 118 | 11 | Não |
| DFS | 119 | 56 | 87 | 35 | Não |
| UCS | 31 | 22 | 116 | 15 | Sim |

### 2.3 ✍️ Por que a BFS devolveu rota mais cara com menos passos
Explique qual hipótese da Aula 03 foi violada (dica: BFS garante otimalidade apenas
quando todo passo tem o MESMO custo — isso é verdade no seu pomar?).

### 2.4 Teste de escala (n = 12 → 40 → 100 → ...)
| n | BFS | DFS | UCS |
|---|---|---|---|
| 12 | ok | ok | ok |
| 40 | | | |
| 100 | | | |
| ... | | | |

✍️ Registre em qual `n` cada estratégia falhou (estouro de memória, de pilha, ou
tempo > 60s) e relacione com a fórmula de complexidade de espaço/tempo da Aula 03
(ex.: `O(b^d)` para BFS/UCS em termos de nós na fronteira).

---

## Parte 3 — Busca informada (1,5 ponto)

### 3.1 A* com três heurísticas
| Heurística | Custo da rota | Nós expandidos | Admissível? (prove) |
|---|---:|---:|---|
| h1 = 0 | 31 | 116 | Sim, trivialmente (h(n) = 0 nunca supera nada; a busca se comporta como UCS) |
| h2 = Manhattan | 31 | 92 | ✍️ (ver prova na seção 3.2 abaixo) |
| h3 = 4×Manhattan | 31 | 24 | ✍️ Não (ver contraexemplo na seção 3.2 abaixo) |

### 3.2 Prova de admissibilidade / contraexemplo
✍️ **h2:** demonstre usando o custo MÍNIMO de entrada em um talhão (1, do carreador)
que h2 nunca superestima o custo real restante.

**h3:** no pomar da matrícula 24114017, tome o talhão **(1, 1)** e o ponto de coleta
**(11, 11)**:
- h3 estimado = 4 × distância de Manhattan((1,1), (11,11)) = 4 × 20 = **80**
- Custo real mínimo restante de (1,1) até (11,11) (via UCS a partir desse talhão) = **29**

Como 80 > 29, **h3 superestima o custo real em 51 unidades** nesse talhão — logo **h3
não é admissível**. Isso acontece porque a maior parte do pomar é carreador `.` (custo
1), mas h3 assume implicitamente que cada passo custaria 4 (o custo do solo
encharcado), inflando a estimativa sempre que o caminho real usa poucos talhões `~`.

### 3.3 A pergunta que separa quem rodou de quem entendeu
Compare o custo devolvido por h3 com o do UCS:
- ✍️ Se ficou igual: isso prova que h3 é admissível? (sim/não + justificativa formal)
- ✍️ Se ficou maior: calcule a perda percentual e quantos nós de expansão "comprou".

✍️ Em ambos os casos: em que situação de negócio da cooperativa valeria a pena trocar
garantia de otimalidade por velocidade? Dê uma condição VERIFICÁVEL (não uma opinião).

### 3.4 Busca local — escolher K=15 talhões para inspecionar
Modelagem usada (ver `src/busca_local.py` para os detalhes e as premissas declaradas):
- **Estado:** subconjunto de 15 talhões livres do pomar
- **Vizinhança:** troca de um talhão do estado por outro talhão livre fora dele
- **Função objetivo:** soma do risco dos talhões escolhidos, penalizada pelo excesso
  de custo de percurso acima do limite de bateria (6h)

Rode `python src/busca_local.py <matrícula>` e preencha:

| Algoritmo | Média (30 execuções) | Desvio padrão | Melhor valor |
|---|---:|---:|---:|
| Subida de encosta | 12,789 | 0,575 | 13,749 |
| Têmpera simulada | 13,939 | 0,036 | 13,975 |

A têmpera simulada obteve uma média **maior** e um desvio padrão **muito menor** que a
subida de encosta (12,79 vs. 13,94 de média; 0,575 vs. 0,036 de desvio). Isso é o
esperado: a subida de encosta greedy fica presa no primeiro ótimo local que encontra
(por isso o resultado varia bastante entre as 30 execuções, dependendo do estado
inicial sorteado), enquanto a têmpera simulada escapa de ótimos locais aceitando
piora de propósito no início (quando a "temperatura" ainda é alta), o que permite
explorar mais do espaço de estados antes de convergir.

✍️ Nas 30 execuções, o script contou entre 109 e 148 pioras aceitas por execução (nos
primeiros 10 valores: [128, 129, 126, 124, 113, 121, 121, 128, 109, 127]) — ou seja, a
maior parte das trocas feitas no começo da execução pioram o valor da função objetivo
de propósito, e é justamente isso que evita que o algoritmo fique preso em um máximo
local abaixo do ótimo, como aconteceu com a subida de encosta.

**Bônus - Liga de IA (+0,3, opcional):** ✍️ construa à mão um pomar ≤ 8×8 em que sua
DFS devolve rota > 2× o ótimo. Anexe a grade, as duas rotas e os dois custos.

---

## Parte 4 — Regras e incerteza (1,5 ponto)

Parâmetros do sensor para a matrícula 24114017 (via `python src/bayes.py 24114017`):
- prevalência = 0,0087
- sensibilidade = 0,95
- taxa de falso positivo = 0,05
- talhões/semana = 2000

### 4.1 Mini sistema especialista
Regras usadas: ver `src/especialista.py` (8 regras, R1–R8). Saída de
`python src/especialista.py` para o caso 1 (fatos: armadilha positiva, umidade alta,
mais de 14 dias sem pulverização):

```
Objetivo: inspecionar_prioridade_alta  ->  PROVADO
Cadeia de raciocinio:
  Tentando R1: SE armadilha_positiva E umidade_alta E dias_desde_pulverizacao_maior_14 ENTAO inspecionar_prioridade_alta
      FATO conhecido: armadilha_positiva
      FATO conhecido: umidade_alta
      FATO conhecido: dias_desde_pulverizacao_maior_14
  => R1 disparada: inspecionar_prioridade_alta PROVADO
```

A regra R1 dispara diretamente porque os três fatos que ela exige já são conhecidos
(fornecidos como entrada), sem precisar provar nenhum sub-objetivo por outras regras.

### 4.2 Quebre a sua própria base
**Caso legítimo:** um talhão com terreno encharcado e chuva recente (logo, alto risco
de fungo) e sem pulverização recente — mas **sem** ter passado por armadilha (por
exemplo, uma área nova que ainda não tem armadilha instalada). Esse caso é legítimo
porque terreno encharcado + chuva por si só já é um indício forte de risco, mesmo sem
o dado da armadilha.

**Traço ANTES da correção** (base só com R1, sem R2/R3 — a base "quebrada"):
```
Objetivo: inspecionar_prioridade_alta  ->  NAO PROVADO
Cadeia de raciocinio:
  Nenhuma regra prova 'inspecionar_prioridade_alta' com os fatos disponiveis
```
A base original classificava esse talhão errado: **não** inspecionava, mesmo com risco
real de fungo, só porque faltava o dado de armadilha exigido por R1.

**Traço DEPOIS da correção** (com R2 e R3 adicionadas):
```
Objetivo: inspecionar_prioridade_alta  ->  PROVADO
Cadeia de raciocinio:
  Tentando R3: SE risco_fungo_alto E sem_pulverizacao_recente ENTAO inspecionar_prioridade_alta
      Tentando R2: SE terreno_encharcado E chuva_recente ENTAO risco_fungo_alto
          FATO conhecido: terreno_encharcado
          FATO conhecido: chuva_recente
      => R2 disparada: risco_fungo_alto PROVADO
      FATO conhecido: sem_pulverizacao_recente
  => R3 disparada: inspecionar_prioridade_alta PROVADO
```
A correção **não contradiz** as regras existentes porque R2/R3 formam um caminho
alternativo, independente, para chegar à mesma conclusão (`inspecionar_prioridade_alta`)
— elas não alteram nem invalidam a lógica de R1 (armadilha + umidade + dias sem
pulverização continua funcionando exatamente como antes), apenas cobrem um cenário que
R1 sozinha não alcançava.

### 4.3 Bayes com os seus números
Saída de `python src/bayes.py 24114017`:
- (a) P(infestado | positivo) = **0,1429**
- (b) a cada 100 alertas, cerca de **85,7** serão falsos
- (c) alertas totais/semana = 115,7; alertas falsos/semana = **99,1**; horas/semana
  perseguindo falsos = **19,8 horas** (quase 2,5 dias úteis de trabalho por semana!)
- (d) novo VPP com sensibilidade 99,9% = **0,1492** (melhora de apenas 0,0063, ou 0,63
  ponto percentual). ✍️ O problema **não melhorou de forma relevante**: mesmo levando a
  sensibilidade a praticamente 100%, o VPP continua baixíssimo (~15%), porque a
  prevalência é muito baixa (0,87%) e é a **taxa de falso positivo (5%)** que domina o
  número de alertas falsos, não a sensibilidade. O parâmetro que a cooperativa deveria
  mexer de fato é a **taxa de falso positivo**, não a sensibilidade — reduzi-la teria
  impacto muito maior no VPP e nas horas semanais desperdiçadas.

### 4.4 ✍️ A regra que salva o modelo
Proponha uma decisão do Caatinga.AI que deve ficar em regra explícita, não em modelo
aprendido. Justifique por auditabilidade/responsabilidade, não por acurácia.

---

## Parte 5 — Auditoria do laudo do fornecedor (0,9 ponto)

| # | Afirmação | Veredito | Justificativa (teoria + número medido por vocês) |
|---|---|---|---|
| 1 | A* com h3 é ótimo porque A* é "comprovadamente ótimo" | ✍️ | (dica: A* só é ótimo com heurística ADMISSÍVEL — vocês já provaram em 3.2 que h3 não é) |
| 2 | BFS→A* caiu 38% de custo, "prova" que a heurística melhora a solução | ✍️ | (dica: BFS não otimiza custo, é injusto comparar custo de BFS com A*; o ganho é de troca de ALGORITMO, não da heurística em si) |
| 3 | Sensibilidade 99% ⇒ 99% dos apontados estão infestados | ✍️ | (dica: isso confunde sensibilidade com VPP — usem o número da Parte 4.3a) |
| 4 | Dois testes positivos seguidos ⇒ confiança > 99% | ✍️ | ✍️ (pensem em independência dos testes e façam a conta de Bayes com o segundo teste) |
| 5 | DFS "é suficiente" porque o pomar é estático e observável | ✍️ | (dica: estático/observável não tem relação com otimalidade de custo — o que garante isso é custo uniforme, Parte 2.3) |

✍️ **Parágrafo de recomendação (máx. 8 linhas):** contratar / contratar com ressalvas
/ recusar — com a condição técnica que mudaria a resposta.
