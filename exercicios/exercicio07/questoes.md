# Exercício 07

Data: 26/01/2021

Coloque os arquivos na pasta _exercicios/exercicio07_.

## Questão 01

Escreva um _script_ chamado _formataTexto.sh_ que receba quatro parâmetros:

1. **Primeiro Parâmetro**: um das três opções _sublinhado, negrito ou reverso_. 
2. **Segundo Parâmetro**: um número que representa a cor de acordo com o comando _tput_. 
3. **Terceiro Parâmetro**: dois números separados por vírgula. 
4. **Quarto Parâmetro**: um texto a ser impresso. 

Por exemplo:

```
$ ./formataTexto.sh negrito 1 20,20 "Scripts"
```

Imprime o texto na posição 20,20, na cor vermelha e em negrito.

## Questão 02

Façamos um _script_ chamado _contadorVetor.sh_:

1. O usuário deve informar, sem utilizar parâmetros, um número por vez.
2. O número deve ser armazenado em um vetor.
3. Quando o usuário informar o caractere _q_ o _script_ deve informar quantos números foram inseridos no vetor e terminar. 

É preciso usar vetores!
