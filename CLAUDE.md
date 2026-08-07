# CLAUDE.md

Guia para trabalhar neste repositório com o Claude Code / OpenCode.

## Sobre o repositório

Material didático da disciplina **Programação de Scripts**, do curso de Ciência
da Computação da UFC — Campus Quixadá, ministrada pelo professor João Marcelo
Uchôa de Alencar.

O conteúdo é organizado por **semestre em branches**: cada oferta da disciplina
vive em um branch próprio, nomeado com ano + semestre (ex.: `20252` = 2º
semestre de 2025, `20261` = 1º semestre de 2026). Branches novos normalmente
são criados a partir do branch do semestre anterior (`git checkout -b <novo>
<anterior>`), preservando o histórico e permitindo ajustes pontuais de
conteúdo a cada oferta.

`master` existe como branch de referência, mas o trabalho corrente acontece
nos branches de semestre.

## Estrutura de diretórios

- **`slides/`** — Slides de aula em LaTeX/Beamer, um subdiretório por capítulo
  (`01_introducao`, `02_comandos_basicos`, ..., `21_Ansible`, além de
  `atividades` e `seminarios`). Cada pasta contém o `.tex` principal, uma
  pasta `figuras/` com imagens e (após compilar) artefatos gerados como
  `.pdf`, `.aux`, `.log`, `_minted/` etc.
- **`atividades/`** — Enunciados de atividades e exercícios avaliativos em
  Markdown (`questoes.md`), um subdiretório por atividade/exercício
  (`atividade01`, `atividade02`, `exercicio04` a `exercicio11`).
- **`src/`** — Código de exemplo usado nas aulas (scripts shell, exemplos de
  `awk` em `src/awk/`, exemplos de JSON/shell em `src/json/`).
- **`tutoriais/`** — Tutoriais avulsos em Markdown (ex.: `wordpress.md`).

## Compilação dos slides (LaTeX/Beamer)

Os slides usam `documentclass{beamer}`, pacote `minted` (realce de sintaxe via
Pygments) e babel em português. A compilação **exige `-shell-escape`** porque
o `minted` invoca o `pygmentize` externamente.

### Pré-requisitos

- Distribuição LaTeX com `pdflatex` (TeX Live).
- Pacote `minted` (`kpsewhich minted.sty` deve resolver).
- `pygmentize` (Pygments) instalado e no `PATH`.
- Pacotes de idioma português para o `babel`.

No Ubuntu (conforme o `README.md`):

```bash
sudo apt install texlive-latex-base texlive-lang-portuguese texlive-latex-extra python-pygments
```

No macOS, uma distribuição TeX Live/MacTeX completa com Pygments instalado via
Homebrew (`brew install pygments` ou dentro de um virtualenv Python) atende os
requisitos.

### Como compilar um capítulo

```bash
cd slides/<capitulo>
pdflatex -shell-escape <arquivo>.tex
```

Pode ser necessário rodar duas vezes para resolver referências cruzadas
(sumário, contadores de frame etc.).

### Status de compilação nesta máquina

✅ **Confirmado**: a máquina atual compila os slides com sucesso.

Verificado compilando `slides/01_introducao/introducao.tex`:
- `pdflatex`, `latex`, `xelatex`, `lualatex` disponíveis em
  `/Library/TeX/texbin` (TeX Live 2026).
- `pygmentize` disponível via Homebrew (`/opt/homebrew/bin/pygmentize`).
- `minted.sty` resolvido em
  `/usr/local/texlive/2026/texmf-dist/tex/latex/minted/minted.sty`.
- `pdflatex -shell-escape -interaction=nonstopmode introducao.tex` gerou
  `introducao.pdf` (24 páginas) sem erros — apenas warnings inofensivos de
  substituição de fonte (`OMS/cmss/m/n`).

Artefatos de compilação (`.pdf`, `.aux`, `.log`, `_minted*` etc.) já estão
cobertos pelo `.gitignore` e não devem ser versionados.

## Atividades (Markdown)

Cada `atividades/<pasta>/questoes.md` segue um padrão simples:
- Título (`# Atividade NN` ou `# Exercício NN`).
- Metadados como valor da nota, data limite/data de publicação.
- Enunciado das questões, frequentemente pedindo scripts shell com exemplos de
  uso em blocos de código (ex.: manipulação de arquivos, AWS CLI, agenda de
  contatos, etc.).

Ao editar ou criar novas atividades, manter esse mesmo formato e o padrão de
nomenclatura de pastas (`atividadeNN` para atividades, `exercicioNN` para
exercícios de menor peso).

## Convenções gerais

- Conteúdo majoritariamente em português (idioma da disciplina).
- Nomes de arquivos e pastas em minúsculo sem acentos, exceto exceções ligadas
  a nomes de tecnologias (`19_AWS`, `20_Terraform`, `21_Ansible`).
- Preferir editar arquivos `.tex`/`.md` existentes a criar novos, seguindo a
  estrutura de capítulos/pastas já estabelecida.
