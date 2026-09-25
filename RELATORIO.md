# Relatório - Caatinga.AI - Sprint 1

## Parte 1 — O agente antes do código (0,9 ponto)

### 1.1 Ficha PEAS
| Componente | Descrição |
|---|---|
| **P**erformance | Custo total do percurso, em unidades de terreno (Custo do caminho = soma dos custos dos talhões percorridos); número de talhões infestados não detectados por semana; tempo total gasto por rota, em minutos. |
| **A**mbiente | O pomar 12×12, com talhões `.` `~` `#`, portão em (0,0), ponto de coleta em (11,11) |
| **A**tuadores | Motor de deslocamento nas quatro direções ortogonais (Norte, Sul, Leste, Oeste); acionamento do sensor óptico de detecção de pragas; emissão de sinal/alerta apontando um talhão suspeito para inspeção humana. |
| **S**ensores | Câmera/sensor óptico de detecção de pragas; leitor de posição atual (coordenada no grid); leitor do tipo de terreno do talhão adjacente (necessário para saber o custo de entrada antes de se mover); medidor do nível de bateria restante. |

### 1.2 Classificação do ambiente (seis dimensões)
| Dimensão | Classificação | Frase do cenário que sustenta |
|---|---|---|
| Observável | Totalmente observável (discutível — ver abaixo) | O enunciado define o pomar inteiro como uma grade 12×12 conhecida, com todos os talhões e seus tipos definidos de antemão pelo gerador. |
| Determinístico | Determinístico | "Custo do caminho = soma do custo dos talhões em que ele entra" — o resultado de cada movimento (custo, novo estado) é sempre o mesmo, sem aleatoriedade na execução da ação. |
| Episódico | Sequencial | Cada movimento do agente depende da sequência de movimentos anteriores (a posição atual é resultado do histórico de ações) até alcançar o ponto de coleta — não são decisões independentes umas das outras. |
| Estático | Estático (discutível — ver abaixo) | O enunciado não menciona nenhuma mudança no pomar (chuva alterando encharcamento, outro trabalhador bloqueando um talhão) enquanto o agente se desloca. |
| Discreto | Discreto | O pomar é uma "grade de 12×12 talhões" com posições e ações ("quatro direções ortogonais") em número finito e bem definido. |
| Agente único | Agente único | O enunciado descreve apenas "o agente" no singular percorrendo o pomar, sem menção a outros agentes atuando simultaneamente. |

**Duas dimensões discutíveis:** *Observável* e *Estático*.
- **Observável:** o enunciado dá ao agente (e ao código) acesso ao mapa completo do pomar desde o início, o que sugere ambiente totalmente observável. Mas, em um cenário mais realista de robótica agrícola, o agente físico só enxergaria os talhões próximos via câmera, sem conhecer o pomar inteiro de antemão — o que tornaria o ambiente parcialmente observável. A informação que decidiria a questão é: **o agente recebe o mapa do pomar antes de começar a se mover, ou precisa descobri-lo talhão por talhão conforme avança?**
- **Estático:** o enunciado não menciona nada mudando durante o percurso, mas também não afirma explicitamente que nada muda (ex.: chuva podendo transformar um carreador `.` em solo encharcado `~` durante a inspeção, ou outro trabalhador temporariamente bloqueando um talhão). A informação que decidiria a questão é: **o estado do pomar pode se alterar enquanto o agente ainda está em rota, ou ele é fixo do início ao fim de cada execução?**

### 1.3 Tipo de agente
**Agente baseado em utilidade.** O Caatinga.AI não apenas precisa alcançar o ponto de
coleta (o que já bastaria para um agente baseado em objetivos) — ele precisa alcançá-lo
**minimizando uma medida contínua de custo** (a soma dos custos dos talhões percorridos).
Isso é exatamente a característica que distingue um agente baseado em utilidade de um
baseado em objetivos simples: existem várias rotas possíveis que atingem o objetivo
(chegar a (11,11)), mas elas têm qualidades diferentes, e o agente precisa comparar essas
rotas por uma função de utilidade (o custo do caminho) para escolher a melhor — é
justamente o que a UCS e o A* fazem ao comparar `g(n)` entre diferentes caminhos.

### 1.4 Métrica perversa
**Métrica proposta:** "minimizar o custo total do percurso do portão até o ponto de
coleta" — parece razoável, já que é literalmente o que otimizamos nas Partes 2 e 3.

**Comportamento ruim que o agente aprenderia:** se essa fosse a ÚNICA métrica de
desempenho (sem nenhuma recompensa por inspecionar talhões suspeitos), o agente
aprenderia a seguir sempre a rota mais barata possível (a rota ótima da UCS) e **jamais
se desviaria dela para inspecionar um talhão suspeito fora do caminho** — mesmo que o
sensor óptico apontasse uma alta probabilidade de praga ali. O sensor viraria peça de
decoração: o agente teria o dado de talhões suspeitos, mas nenhum incentivo para agir
sobre ele.

**Onde isso apareceria no pomar:** na nossa rota ótima (matrícula 24114017, custo 31),
o caminho passa por `(0,0) → (0,1) → (0,2) → (1,2) → ... → (11,11)`. Qualquer talhão
fora dessa lista — por exemplo `(5,0)` ou `(9,3)` — jamais seria visitado, mesmo que
fosse ali que a armadilha do sensor apontasse a maior suspeita de infestação da semana.

**Correção da métrica:** combinar o custo do percurso com uma recompensa por talhões
suspeitos efetivamente inspecionados e uma penalidade por infestações confirmadas e não
detectadas — de forma parecida com o que fizemos na função objetivo da busca local
(Parte 3.4), que já pondera risco contra custo de deslocamento, em vez de só minimizar
uma das duas coisas isoladamente.

---

## Parte 2 — Formulação e busca cega (1,2 ponto)

### 2.1 Componentes do problema de busca
| Componente | Definição para o Caatinga.AI |
|---|---|
| Estado inicial | (0, 0) |
| Ações | Mover para Norte, Sul, Oeste ou Leste, se o talhão destino existir na grade e não for `#` |
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

### 2.3 Por que a BFS devolveu rota mais cara com menos passos
Isso não é um bug: a BFS garante otimalidade apenas quando **todos os passos têm o
mesmo custo** (custo uniforme) — hipótese conhecida como "custo de passo uniforme",
usada na prova de otimalidade da BFS (Aula 03). No nosso pomar, os passos custam **1**
(carreador `.`) ou **4** (solo encharcado `~`) — logo essa hipótese é **violada**. A
BFS encontra a rota com o **menor número de passos** (22, igual ao da UCS), mas entre
todas as rotas de 22 passos ela para na primeira que encontra (por ser busca em
largura, expandindo por "camadas" de distância em número de arestas, não por custo
acumulado) — e essa rota específica passou por mais talhões `~` de custo 4, resultando
em custo 52 contra os 31 da UCS.

### 2.4 Teste de escala (n = 12 → 40 → 100 → ...)
| n | BFS | DFS | UCS |
|---|---|---|---|
| 12 | ok (0,2 ms) | ok (0,2 ms) | ok (0,2 ms) |
| 40 | ok (1,7 ms) | ok (1,3 ms) | ok (3,0 ms) |
| 100 | ok (12,3 ms) | ok (8,7 ms) | ok (16,1 ms) |
| 300 | ok (110,8 ms) | ok (76,3 ms) | ok (182,7 ms) |
| 600 | ok (527,5 ms) | ok (397,1 ms) | ok (912,7 ms) |
| 1000 | ok (1,63 s) | ok (1,04 s) | ok (2,82 s) |
| 2000 | ok (7,27 s) | ok (4,97 s) | ok (12,61 s) |
| 3000 | ok (17,21 s) | ok (12,51 s) | ok (32,16 s) |
| 3500 | — | — | ok (42,20 s, ~2,46 GB de memória) |
| **4000** | **FALHOU** | **FALHOU** | **FALHOU (estouro de memória)** |

Nas nossas três implementações (busca em GRAFO, com conjunto de visitados/expandidos),
nenhuma delas sofre estouro de **pilha** — são implementações **iterativas** (com
`deque`/lista/heap explícitos), não recursivas, então não existe risco de
`RecursionError`. O que de fato limita a escala é a **memória**: cada estratégia
mantém estruturas (`visitados`, `veio_de`, `custo_g`) de tamanho proporcional ao número
de estados já visitados, que cresce em **O(n²)** (o número de talhões livres do
pomar). Em n=3500, o pomar já tem ~12,25 milhões de talhões, e cada estrutura guarda
tuplas de coordenadas e referências para boa parte deles — no nosso teste, isso já
consumia ~2,46 GB de RAM. Em **n=4000** (16 milhões de talhões), o processo foi
finalizado pelo sistema operacional por estouro de memória (memória disponível do
ambiente de teste excedida) antes de qualquer uma das três estratégias terminar. Isso
bate com a fórmula de complexidade espacial da Aula 03 para BFS/UCS: `O(b^d)` em
termos de nós armazenados na fronteira e no conjunto de expandidos — aqui, como o
fator de ramificação `b` é fixo (até 4 vizinhos) mas a profundidade `d` cresce
linearmente com `n`, o número total de estados cresce quadraticamente com `n`, e é
essa curva quadrática que eventualmente estoura a memória disponível.

---

## Parte 3 — Busca informada (1,5 ponto)

### 3.1 A* com três heurísticas
| Heurística | Custo da rota | Nós expandidos | Admissível? (prove) |
|---|---:|---:|---|
| h1 = 0 | 31 | 116 | Sim, trivialmente (h(n) = 0 nunca supera nada; a busca se comporta como UCS) |
| h2 = Manhattan | 31 | 92 |  (ver prova na seção 3.2 abaixo) |
| h3 = 4×Manhattan | 31 | 24 |  Não (ver contraexemplo na seção 3.2 abaixo) |

### 3.2 Prova de admissibilidade / contraexemplo
**h2 (prova de admissibilidade):** h2(n) é a distância de Manhattan entre o talhão `n`
e o objetivo — ou seja, o **número mínimo de movimentos ortogonais** necessários para
alcançar o objetivo, ignorando obstáculos e tipos de terreno. O **menor custo possível
de entrada em qualquer talhão** do problema é 1 (o custo do carreador `.`). Logo, o
custo real de **qualquer** caminho de `n` até o objetivo é, no mínimo,
`distância_Manhattan(n, objetivo) × 1 = h2(n)` — porque o agente precisa dar pelo menos
esse número de passos, e cada passo custa pelo menos 1. Como o custo real nunca pode
ser menor que h2(n), h2 **nunca superestima** o custo real restante — por definição,
h2 é **admissível**.

**h3:** no pomar da matrícula 24114017, tome o talhão **(1, 1)** e o ponto de coleta
**(11, 11)**:
- h3 estimado = 4 × distância de Manhattan((1,1), (11,11)) = 4 × 20 = **80**
- Custo real mínimo restante de (1,1) até (11,11) (via UCS a partir desse talhão) = **29**

Como 80 > 29, **h3 superestima o custo real em 51 unidades** nesse talhão — logo **h3
não é admissível**. Isso acontece porque a maior parte do pomar é carreador `.` (custo
1), mas h3 assume implicitamente que cada passo custaria 4 (o custo do solo
encharcado), inflando a estimativa sempre que o caminho real usa poucos talhões `~`.

### 3.3 A pergunta que separa quem rodou de quem entendeu
No nosso pomar (matrícula 24114017), o custo devolvido pelo A* com h3 foi **31**,
exatamente igual ao custo da UCS (também 31).

**Isso prova que h3 é admissível? Não.** O fato de h3 ter "acertado" o custo ótimo
**nesta instância específica** não prova admissibilidade — admissibilidade é uma
propriedade que precisa valer para **todos os estados possíveis** do problema, e nós já
provamos formalmente o contrário na Parte 3.2: existe pelo menos um talhão (o (1,1))
onde h3 superestima o custo real em 51 unidades. O que aconteceu aqui é que, mesmo com
uma heurística inadmissível guiando a busca "na direção errada" em alguns pontos, o
caminho que o A* acabou encontrando com h3 ainda coincidiu com o caminho ótimo — isso
pode acontecer dependendo da estrutura do grafo, mas é sorte da instância, não garantia
do algoritmo. Um único contraexemplo formal (Parte 3.2) já é suficiente para refutar a
admissibilidade, independentemente do resultado prático em qualquer pomar específico.

**Em que situação de negócio valeria a pena trocar otimalidade por velocidade?**
Note que h3, mesmo não sendo admissível, expandiu muito menos nós que h2 (24 contra 92
— quase **74% menos nós expandidos**) neste pomar. Uma condição verificável para
justificar essa troca seria: **se o sistema embarcado no agente precisar recalcular a
rota em tempo real, com um orçamento fixo de latência (por exemplo, no máximo 50 ms por
replanejamento, porque o agente precisa decidir a cada poucos segundos de deslocamento)
e a versão com h2 ultrapassar esse limite em pomares maiores, enquanto h3 consistentemente
o respeitar** — aí a cooperativa estaria trocando uma garantia teórica de otimalidade por
uma restrição operacional real e mensurável, desde que o custo extra esperado da rota
(medido empiricamente ao longo de várias execuções) fique dentro de uma margem aceitável
pré-definida (por exemplo, no máximo 5% acima do custo ótimo, em média).

### 3.4 Busca local — escolher K=15 talhões para inspecionar

**Modelagem do problema:**

- **Estado:** um subconjunto de tamanho K=15 de talhões livres (não bloqueados) do
  pomar, representado como uma tupla ordenada de coordenadas.

- **Vizinhança:** trocar (swap) UM talhão do estado por UM talhão livre que está fora
  do estado. Cada estado tem até K × (L − K) vizinhos, onde L é o número total de
  talhões livres do pomar (118, no caso da matrícula 24114017).

- **Função objetivo (a maximizar):**
  ```
  objetivo(estado) = soma_risco(estado) - PENALIDADE × excesso_bateria(estado)
  ```
  - `soma_risco(estado)`: soma de um escore de risco de praga por talhão
    (determinístico, derivado da matrícula e da posição — simula a saída do sensor
    óptico de detecção de pragas).
  - `excesso_bateria(estado) = max(0, custo_estimado_percurso(estado) - LIMITE)`:
    `custo_estimado_percurso` é um tour guloso do vizinho mais próximo (nearest
    neighbor), partindo do portão (0,0) e visitando os K talhões do estado, em
    unidades de custo de deslocamento (mesma unidade da Parte 2). `LIMITE` é quantas
    unidades de custo cabem nas 6 horas de bateria, assumindo `T_UNIDADE` minutos de
    deslocamento por unidade de custo (premissa declarada no código — 3 minutos por
    unidade, resultando em um limite de 120 unidades de custo).

**Por que essa modelagem cria uma paisagem de busca real:** aumentar o risco total
tende a exigir talhões mais espalhados pelo pomar, o que aumenta o custo do percurso e
pode estourar a bateria (ativando a penalidade). O objetivo resultante tem vales e
picos — boa demonstração de por que a têmpera simulada aceita piora de propósito
(Aula 04): ela escapa de ótimos locais em que a subida de encosta greedy fica presa.

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

Nas 30 execuções, o script contou entre 109 e 148 pioras aceitas por execução (nos
primeiros 10 valores: [128, 129, 126, 124, 113, 121, 121, 128, 109, 127]) — ou seja, a
maior parte das trocas feitas no começo da execução pioram o valor da função objetivo
de propósito, e é justamente isso que evita que o algoritmo fique preso em um máximo
local abaixo do ótimo, como aconteceu com a subida de encosta.

**Bônus - Liga de IA (+0,3, opcional):** construa à mão um pomar ≤ 8×8 em que sua
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
  ponto percentual). O problema **não melhorou de forma relevante**: mesmo levando a
  sensibilidade a praticamente 100%, o VPP continua baixíssimo (~15%), porque a
  prevalência é muito baixa (0,87%) e é a **taxa de falso positivo (5%)** que domina o
  número de alertas falsos, não a sensibilidade. O parâmetro que a cooperativa deveria
  mexer de fato é a **taxa de falso positivo**, não a sensibilidade — reduzi-la teria
  impacto muito maior no VPP e nas horas semanais desperdiçadas.

### 4.4 A regra que salva o modelo
**Decisão que deve ficar em regra explícita:** nunca tentar entrar em um talhão marcado
como bloqueado (`#`) — galpões, reservatórios, mata — independentemente do que qualquer
modelo aprendido "ache" sobre aquele talhão.

**Justificativa (auditabilidade/responsabilidade, não acurácia):** um modelo aprendido
(por exemplo, um classificador probabilístico de terreno a partir de imagens) sempre tem
uma taxa de erro, por menor que seja — e um falso negativo aqui (o modelo "achar" que um
reservatório de água é atravessável) coloca em risco físico o próprio equipamento e,
dependendo do tipo de área bloqueada (mata com pessoas trabalhando, por exemplo),
também pessoas. Isso não é uma questão de "qual modelo tem mais acurácia": é uma decisão
de segurança que precisa ser **auditável e determinística** — qualquer pessoa (inclusive
um fiscal ou um juiz, em caso de acidente) precisa conseguir verificar exatamente por que
o agente nunca deveria ter entrado ali, sem depender da interpretação de uma rede neural
que pode mudar de comportamento a cada retreinamento.

---

## Parte 5 — Auditoria do laudo do fornecedor (0,9 ponto)

| # | Afirmação | Veredito | Justificativa (teoria + número medido por vocês) |
|---|---|---|---|
| 1 | A* com h3 é ótimo porque A* é "comprovadamente ótimo" | **Incorreta** | A* só é garantidamente ótimo com heurística **admissível**. Provamos na Parte 3.2 que h3 = 4×Manhattan **não é admissível** (no talhão (1,1), h3 estima 80 contra um custo real de 29 — superestimativa de 51 unidades). O fato de o custo ter batido com o UCS no nosso pomar (Parte 3.3, ambos = 31) é coincidência de instância, não garantia do algoritmo. |
| 2 | BFS→A* caiu 38% de custo, "prova" que a heurística melhora a solução | **Incorreta** | BFS não otimiza custo (otimiza nº de passos), então comparar seu custo com o de A* é injusto. No nosso pomar, BFS = 52 e A* com **h1 = 0 (sem heurística nenhuma, equivalente a UCS)** já obtém custo 31 — a mesma queda (~40%) que h2 e h3 obtêm. Isso mostra que a queda de custo vem de **trocar de algoritmo** (de BFS para uma busca que otimiza custo), não da heurística em si. |
| 3 | Sensibilidade 99% ⇒ 99% dos apontados estão infestados | **Incorreta** | Isso confunde sensibilidade (P(+\|infestado)) com VPP (P(infestado\|+)). Com nossos parâmetros reais (Parte 4.3a: sensibilidade 95%, prevalência 0,87%), o VPP calculado é de apenas **14,29%** — muitíssimo abaixo dos 99% alegados. A prevalência baixa faz a taxa de falso positivo dominar o resultado. |
| 4 | Dois testes positivos seguidos ⇒ confiança > 99% | **Incorreta** | Aplicando Bayes duas vezes com nossos parâmetros (usando o VPP do 1º teste como nova prevalência do 2º, assumindo testes independentes): após 1 teste, VPP = 14,29%; após 2 testes, VPP = **76,01%** — bem abaixo de 99%. Seriam necessários **4 testes positivos independentes seguidos** para ultrapassar 99% (chegando a 99,91%), não 2. Além disso, a suposição de independência entre dois testes do mesmo sensor, nas mesmas condições, é otimista — testes correlacionados aumentariam a confiança ainda mais devagar que isso. |
| 5 | DFS "é suficiente" porque o pomar é estático e observável | **Incorreta** | Estático e observável não têm relação com otimalidade de custo — quem garante rota ótima é o algoritmo (UCS/A*) aliado a custo uniforme dos passos (Parte 2.3), não essas duas dimensões do ambiente. Na prática, a DFS no nosso pomar devolveu uma rota de custo **119**, quase **4× pior** que o custo ótimo de 31 — o oposto de "suficiente" se o objetivo é economizar deslocamento. |

**Parágrafo de recomendação:** recomendamos **contratar com ressalvas**. A solução
técnica da AgroVision pode ser funcional na prática, mas o laudo superestima
sistematicamente suas garantias formais (otimalidade, confiabilidade estatística),
o que pode levar a decisões operacionais equivocadas da cooperativa (confiar cegamente
em alertas do sensor, por exemplo). A condição técnica que mudaria nossa resposta para
"contratar sem ressalvas" seria a AgroVision reescrever o laudo comunicando os números
reais (VPP em vez de sensibilidade, custo real do A* com heurística não-admissível
divulgado como aproximado) e comprovando empiricamente a independência estatística
alegada no item 4 antes de prometer ganhos específicos de confiança.
