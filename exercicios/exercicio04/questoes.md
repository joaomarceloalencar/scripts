# Exercício 04 

Data: 22/12/2020

Coloque os arquivos na pasta _exercicios/exercicio04_.

## Questão 01

Nesta questão, você deve criar um _script_ chamado _agenda.sh_. Esse _script_ deve oferecer as funcionalidades de agenda de contatos, adicionando ou removendo informações em um arquivo auxiliar chamado _usuarios.db_. Por exemplo, ao executar o seguinte comando:

```
$ ./agenda.sh adicionar "João Marcelo" joao.marcelo@ufc.br
```

O _script_ deve criar o arquivo _usuarios.db_ com o seguinte conteúdo:

```
$ cat usuarios.db
João Marcelo:joao.marcelo@ufc.br
```

Portanto, uma nova execução:

```
$ ./agenda.sh adicionar "Jeando Bezerra" jeandro@ufc.br
```

O contéudo de _usuarios.db_ ficaria:

```
$ cat usuarios.db
João Marcelo:joao.marcelo@ufc.br
Jeandro Bezerra:jeandro@ufc.br
```

Espero que você tenha entendido que ao passar o primeiro parâmetro como _adicionar_, o segundo parâmetro (o nome) e o terceiro parâmetro (o _e-mail_) devem ser adicionados como nova linha no arquivo _usuarios.db_, separados por dois pontos (:).

## Questão 02

Agora, mais fácil. Você só precisa adicionar uma opção _listar_ ao mesmo _script_. Por exemplo:

```
$ ./agenda.sh listar 
João Marcelo:joao.marcelo@ufc.br
Jeandro Bezerra:jeandro@ufc.br
```

Quando receber um único parâmetro, _listar_, o conteúdo do arquivo _usuarios.db_ deve ser exibido na tela. Lembrando que se trata do mesmo _script_ da questão anterior, _agenda.sh_, que deve fazer duas ações diferentes de acordo com o valor do primeiro parâmetro. 


