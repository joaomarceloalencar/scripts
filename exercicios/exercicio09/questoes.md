# Exercício 09

Data: 09/02/2021

Coloque os arquivos na pasta _exercicios/exercicio09_.

## Questão 01
Coloque os padrões e ações _awk_ no arquivo _questao01.awk_, da mesma forma que foi demonstrado em vídeo aula.

Considerando o arquivo _/home/compartilhado/emailsordenados.txt_, faça com que:

```
$ awk -f questao01.awk /home/compartilhado/emailsordenados.txt
```

retorne os alunos que tem _e-mail_ no domínio _@alu.ufc.br_.

## Questão 02
Coloque os padrões e ações _awk_ no arquivo _questao02.awk_, da mesma forma que foi demonstrado em vídeo aula.

Considerando o arquivo _/home/compartilhado/emailsordenados.txt_, faça com que:

```
$ awk -f questao02.awk /home/compartilhado/emailsordenados.txt
```

retorne apenas a **quantidade** de alunos com _e-mail_ no domínio _@gmail.com_

## Questão 03
Coloque os padrões e ações _awk_ no arquivo _questao03.awk_, da mesma forma que foi demonstrado em vídeo aula.

Considerando o arquivo _/home/compartilhado/emailsordenados.txt_, faça com que:

```
$ awk -f questao03.awk /home/compartilhado/emailsordenados.txt
```
imprima na tela todos os _e-mails_, porém se um _e-mail_ não for do domínio _@alu.ufc.br_, deve ser substituído por ele

Exemplo: _estudante@gmail.com_ deve virar _estudante@alu.ufc.br_.

## Questão 04
Coloque os padrões e ações _awk_ no arquivo _questao04.awk_, da mesma forma que foi demonstrado em vídeo aula.

Considere um arquivo com o seguinte conteúdo:

```
### Produtos Valor ###
    PS5      5000
    MACBOOK  12000
    GALAXY   6000
    MIBAND   300
```

Faça um comando:

```
$ awk -f questao04.awk compras.txt
```

que retorne a soma dos produtos com valor acima de 5000. 

