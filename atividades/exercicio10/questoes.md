# Exercício 10 

Data: 16/02/2021

Coloque os arquivos na pasta _exercicios/exercicio10_.

## Questão 01

Considere o seguinte conteúdo em um arquivo de texto:

```
Roberta Evans de Jesus     5.0   5.0   4.0   3.0
Jusicreudo Lineu da Rocha  7.0   6.0   8.0   6.0
Ananias Silva              10.0  5.0   1.0   6.0
Ludivania Amarelo Pinto    5.0   5.0   3.0   7.0
Jonas Tadeu Emanuel        7.0   3.0   9.0   4.0
Roberto Silva Sauro        3.0   7.0   9.0   9.0
Tarcisio Anapalpega        4.0   4.0   10.0  5.0
Gratenildo Hulmide da Paz  2.0   1.0   6.0   4.0
```

Escreva um _script_ chamado _disciplina.awk_ que faça a média das três maiores notas. Deve ser impresso um relatório mostrando o nome e a média dos alunos:

* Aprovados (média >= 7)
* Final (5 <= média < 7)
* Reprovados (média < 5)

## Questão 02

Faça um _script_ chamado _marajas.awk_ que dado um arquivo de salários no formato abaixo imprima os professores que mais ganham por curso.

```
NOME        CURSO       SALARIO
Jeandro     Redes       10000
Elvis       Engenharia  11000
Hélder      Engenharia  15000
João        Redes       1000
Michel      Redes       800
Jefferson   Sistemas    5000
Márcio      Sistemas    6000
Marcos      Redes       11000
```

A saída deve ser no formato:

```
$ awk -f marajas.awk professores.txt
Engenharia: Elvis,   11000
Redes:      Marcos,  11000
Sistemas:   Márcio,  6000
```
