
# Programação de Scripts 

Material Disciplina de Programação de Scripts

Professor João Marcelo Uchôa de Alencar

Campus da UFC em Quixadá

## Conteúdo

### src/ - código de exemplo
São vários exemplos, explorando vários aspectos de Shell Script.

### slides/ - pasta com os _slides_ das aulas. 
Considerando uma máquina com Ubuntu 18.04, é preciso instalar os seguintes pacotes:

```bash
$ sudo apt install texlive-latex-base texlive-lang-portuguese texlive-latex-extra python-pygments
```

Em seguida, para cada capítulo, construa o pdf. Por exemplo, para o capítulo 01:

```bash
$ cd scr/slides/01_Introdução
$ pdflatex -shell-escape introducao.tex
```
