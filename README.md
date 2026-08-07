
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

### atividades/ - enunciados de atividades e exercícios

Cada pasta contém um `questoes.md` com o enunciado da atividade/exercício
correspondente.

## Avaliação

Conforme apresentado no slide de introdução (`slides/01_introducao`):

- A nota final é composta por **3 notas**, cada uma associada a um grupo de
  atividades.
- Nenhuma das 3 notas pode ser entregue vazia (zerada).
- As atividades são **individuais** — cópia é proibida.
- A nota final é a **média aritmética** das 3 notas.
- A disciplina é presencial; a frequência é registrada pelo comparecimento
  às aulas.

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

As 3 notas correspondem a blocos de aproximadamente 12 aulas cada, seguindo a
sequência dos capítulos em `slides/`.

#### Bloco 1 — Nota 1

| Semana | Terça | Quarta | Conteúdo |
|---|---|---|---|
| 1 | 11/08 | 12/08 | 01. Introdução (+ SSH/SCP) / 02. Comandos básicos (parte 1) |
| 2 | 18/08 | 19/08 | 02. Comandos básicos (parte 2) / 03. Expressões regulares |
| 3 | 25/08 | 26/08 | 04. Redirecionamento de saída / 05. Comandos avançados |
| 4 | 01/09 | 02/09 | 06. Variáveis e parâmetros / 07. Condicionais |
| 5 | 08/09 | 09/09 | 08. Iterações / Orientação Atividade 01 |
| 6 | 15/09 | 16/09 | 09. Gerência de processos / 10. Leitura e escrita |
| 7 | 22/09 | 23/09 | 11. Variáveis e vetores / 12. Miscelânea |
| 8 | 29/09 | 30/09 | 13. AWK (parte 1) / 13. AWK (parte 2) |
| 9 | 06/10 | 07/10 | Revisão / Entrega e correção da Atividade 01 (fechamento Nota 1) |

#### Bloco 2 — Nota 2

| Semana | Terça | Quarta | Conteúdo |
|---|---|---|---|
| 10 | 13/10 | 14/10 | 14. Scripts de inicialização / 15. Execução programada (cron) |
| 11 | 20/10 | 21/10 | 16. Compilação e configuração de programas / 17. Ferramentas de rede |
| 12 | 27/10 | 28/10 | 18. Dialog / Orientação exercícios (04–07) |
| 13 | 03/11 | 04/11 | Correção exercícios (08–11) / Entrega e correção (fechamento Nota 2) |

#### Bloco 3 — Nota 3

| Semana | Terça | Quarta | Conteúdo |
|---|---|---|---|
| 14 | 10/11 | 11/11 | 19. AWS (parte 1) / 19. AWS (parte 2) |
| 15 | 17/11 | 18/11 | 20. Terraform (parte 1) / 20. Terraform (parte 2) |
| 16 | 24/11 | 25/11 | 21. Ansible (parte 1) / 21. Ansible (parte 2) |
| 17 | 01/12 | 02/12 | Preparação de seminários / Apresentação de seminários (parte 1) |
| 18 | 08/12 | 09/12 | Apresentação de seminários (parte 2) / Encerramento (fechamento Nota 3) |

Total: **36 aulas** distribuídas em 18 semanas, cobrindo os 21 capítulos de
`slides/` e os três blocos de atividades avaliativas descritos acima.
