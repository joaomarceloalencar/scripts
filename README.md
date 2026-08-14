
# Programação de Scripts

## Material Disciplina de Programação de Scripts

Professor João Marcelo Uchôa de Alencar

Campus da UFC em Quixadá

Semestre letivo 2026.2 — 10/08/2026 a 11/12/2026 — Aulas às **terças e
quartas-feiras**.

## Conteúdo

### src/ - código de exemplo

São vários exemplos, explorando vários aspectos de Shell Script.

### slides/ - pasta com os _slides_ das aulas

Os slides são escritos em LaTeX/Beamer e usam o pacote `minted` (realce de
sintaxe via Pygments), portanto a compilação exige a flag `-shell-escape`.

Considerando uma máquina com Ubuntu 18.04, é preciso instalar os seguintes
pacotes:

```bash
$ sudo apt install texlive-latex-base texlive-lang-portuguese texlive-latex-extra python-pygments
```

Em seguida, para cada capítulo, construa o pdf. Por exemplo, para o capítulo 01:

```bash
$ cd slides/01_introducao
$ pdflatex -shell-escape introducao.tex
```

### aulas/ - roteiros das aulas *hands-on*

**A fonte principal do curso.** Um arquivo por sessão do cronograma, com o roteiro
prático da aula: etapas guiadas com *checkpoints*, perguntas de discussão e a
entrega que vale nota. Veja o índice em [`aulas/README.md`](aulas/README.md).

### atividades/ - índice de avaliação e questões de reserva

Não há mais atividades para casa: os enunciados foram absorvidos pelas aulas, como
entregas feitas em sala. A pasta mantém o índice que mapeia cada nota às aulas que a
compõem e um banco de questões de reserva, para prova e segunda chamada.

## Avaliação

- A nota final é composta por **3 notas**, cada uma associada a um bloco de aulas.
- Nenhuma das 3 notas pode ser entregue vazia (zerada).
- As entregas são **individuais** — cópia é proibida.
- A nota final é a **média aritmética** das 3 notas.
- A disciplina é presencial; a frequência é registrada pelo comparecimento
  às aulas.

### Como a nota é composta

Não há atividades para casa. Toda aula prática termina com uma **entrega**, feita
em sala nos últimos 20 a 30 minutos, individualmente e sem passo a passo. A
entrega é sempre uma *variação* do exercício guiado da própria aula.

Cada nota vale **10,0 pontos**, distribuídos entre as aulas do bloco:

| Nota | Conteúdo | Aulas | Pontos por aula | Total |
|---|---|---|---|---|
| **Nota 1** | Caps. 01–08 — terminal, regex, redirecionamento, variáveis, condicionais, iterações | 01–09 | 1,0 (a Aula 09 vale 2,0) | 10,0 |
| **Nota 2** | Caps. 09–13 — processos, leitura/escrita, vetores, miscelânea, AWK | 10–16 | 1,25 (a Aula 16 vale 2,5) | 10,0 |
| **Nota 3** | Caps. 14–21 — inicialização, cron, rede, Dialog, AWS, Terraform, Ansible | 17–30 | 0,7 (a Aula 30 vale 0,9) | 10,0 |

Ao fechar cada nota, as **duas piores entregas do bloco são descartadas**. Isso
absorve falta, atraso e dia ruim sem necessidade de segunda chamada.

## Cronograma 2026.2

Período letivo: **10/08/2026 a 11/12/2026**, com aulas às terças e
quartas-feiras.

**Feriados nacionais no período** (nenhum cai em terça ou quarta-feira, logo
não há aulas canceladas por feriado neste calendário):

| Data | Dia da semana | Feriado |
|---|---|---|
| 07/09/2026 | segunda-feira | Independência do Brasil |
| 12/10/2026 | segunda-feira | Nossa Senhora Aparecida |
| 02/11/2026 | segunda-feira | Finados |
| 15/11/2026 | domingo | Proclamação da República |
| 20/11/2026 | sexta-feira | Consciência Negra |

> **Atenção:** este cronograma foi construído considerando apenas os
> feriados nacionais. Confirme no calendário acadêmico oficial da UFC se há
> emendas, recessos ou outros ajustes de calendário (ex.: eleições, greves)
> que possam alterar as datas de aula.

### Distribuição das aulas (18 semanas, 36 aulas)

Os blocos seguem a sequência dos capítulos em `slides/`, e cada bloco fecha uma
das 3 notas.

#### Bloco 1 — Nota 1 (Aulas 01–09)

| Semana | Terça | Quarta | Conteúdo |
|---|---|---|---|
| 1 | 11/08 | 12/08 | **Aula 01** 01. Introdução (+ SSH/SCP) / **Aula 02** 02. Comandos básicos (parte 1) |
| 2 | 18/08 | 19/08 | **Aula 03** 02. Comandos básicos (parte 2) / **Aula 04** 03. Expressões regulares |
| 3 | 25/08 | 26/08 | **Aula 05** 04. Redirecionamento de saída / **Aula 06** 05. Comandos avançados |
| 4 | 01/09 | 02/09 | **Aula 07** 06. Variáveis e parâmetros / **Aula 08** 07. Condicionais |
| 5 | 08/09 | 09/09 | **Aula 09** 08. Iterações / Correção das entregas (fechamento Nota 1) |

#### Bloco 2 — Nota 2 (Aulas 10–16)

| Semana | Terça | Quarta | Conteúdo |
|---|---|---|---|
| 6 | 15/09 | 16/09 | **Aula 10** 09. Gerência de processos / **Aula 11** 10. Leitura e escrita |
| 7 | 22/09 | 23/09 | **Aula 12** 11. Variáveis e vetores / **Aula 13** 12. Miscelânea |
| 8 | 29/09 | 30/09 | **Aula 14** 13. AWK (parte 1) / **Aula 15** 13. AWK (parte 2) |
| 9 | 06/10 | 07/10 | **Aula 16** Integradora / Correção das entregas (fechamento Nota 2) |

#### Bloco 3 — Nota 3 (Aulas 17–30)

| Semana | Terça | Quarta | Conteúdo |
|---|---|---|---|
| 10 | 13/10 | 14/10 | **Aula 17** 14. Scripts de inicialização / **Aula 18** 15. Execução programada (cron) |
| 11 | 20/10 | 21/10 | **Aula 19** 16. Compilação e configuração / **Aula 20** 17. Ferramentas de rede |
| 12 | 27/10 | 28/10 | **Aula 21** 18. Dialog (parte 1) / **Aula 22** 18. Dialog (parte 2) |
| 13 | 03/11 | 04/11 | **Aula 23** 19. AWS (parte 1) / **Aula 24** 19. AWS (parte 2) |
| 14 | 10/11 | 11/11 | **Aula 25** 20. Terraform (parte 1) / **Aula 26** 20. Terraform (parte 2) |
| 15 | 17/11 | 18/11 | **Aula 27** 21. Ansible (parte 1) / **Aula 28** 21. Ansible (parte 2) |
| 16 | 24/11 | 25/11 | **Aula 29** Projeto integrador (parte 1) / **Aula 30** Projeto integrador (parte 2) |
| 17 | 01/12 | 02/12 | Preparação de seminários / Apresentação de seminários (parte 1) |
| 18 | 08/12 | 09/12 | Apresentação de seminários (parte 2) / Correção das entregas (fechamento Nota 3) |

Total: **36 aulas** distribuídas em 18 semanas, cobrindo os 21 capítulos de
`slides/` e os três blocos de atividades avaliativas descritos acima.
