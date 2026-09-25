# Anexo de uso de IA — Caatinga.AI Sprint 1

## A.1 Ferramentas usadas e em quais partes
Usamos o Claude (Anthropic) para gerar o esqueleto de todos os arquivos `.py`
(`gerador_pomar.py` copiado exatamente do enunciado, `buscas.py`, `busca_local.py`,
`especialista.py`, `bayes.py`, `main.py`), para rodar os testes com a nossa matrícula
(24114017) e preencher as tabelas numéricas do `RELATORIO.md`, para nos ajudar a
redigir um rascunho das respostas dissertativas (PEAS, classificação do ambiente,
provas de admissibilidade, auditoria do laudo) e para nos explicar como funciona sua estrutuura detalhada.

## A.2 Dois prompts na íntegra, com a resposta recebida

### Prompt 1
[tenho que fazer essa atividade, leve em consideracao as regras impostas nele pois vale nota]

[A IA leu o enunciado em PDF que enviamos e propôs montar o repositório completo
(BFS/DFS/UCS/A*, busca local, sistema especialista, cálculo de Bayes, main.py),
destacando que seguiria as regras do enunciado (matrícula intocável, mínimo de 8
commits distribuídos, ANEXO_IA.md obrigatório), e perguntou por onde queríamos
começar.]

### Prompt 2
[Explique como funciona sua estrutura]

[A IA explicou de forma detalhada como cada parte funcionava]


## A.3 Um erro, imprecisão ou invenção real do assistente

- **O que o assistente afirmou:** ao implementar a busca local (item 3.4), a IA
  definiu os parâmetros `PENALIDADE = 0.08` e `T_UNIDADE_MINUTOS = 3` como "premissas
  declaradas" da modelagem, dando a entender nos comentários do código que
  `PENALIDADE` era o parâmetro relevante para controlar o trade-off entre risco de
  praga e estouro de bateria.

- **Evidência do nosso experimento que desmentiu isso:** rodamos o código com a nossa
  matrícula (24114017) e multiplicamos `PENALIDADE` por ~6× (de 0,08 para 0,5) — o
  resultado da têmpera simulada praticamente não mudou (média de 13,939 para 13,941,
  uma variação irrelevante). Já ao mudar `T_UNIDADE_MINUTOS` de 3 para 10 minutos (a
  premissa de quanto tempo cada unidade de custo de deslocamento consome da bateria),
  o resultado caiu de forma real: média de 13,939 para 11,642. Ou seja, o parâmetro
  que a IA tratou como "declarado mas coadjuvante" na verdade tem pouquíssimo efeito
  prático nesta instância, enquanto outro parâmetro mencionado só de passagem é que
  domina o resultado.

## A.4 O que você sabia depois de rodar o código que não sabia lendo a resposta do assistente
Só entendemos de fato por que a heurística h3 (4×Manhattan) não é admissível depois de
vermos, no nosso pomar real, o número concreto do talhão (1,1) — h3 estimando 80
contra um custo real de apenas 29 — porque só o texto da fórmula, sem números, não
deixava claro o tamanho do erro nem em qual tipo de talhão isso realmente acontece.