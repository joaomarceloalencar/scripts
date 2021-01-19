# Exercício 06

Data: 19/01/2021

Coloque os arquivos na pasta _exercicios/exercicio06_.

## Questão Única

Vamos fazer um _script_ chamado _IPsAtivos.sh_ que receba como parâmetros os três primeiros octetos de uma sub-rede /24 e verifique quais IPs da rede estão ativos. Exemplo de execução:

```
$ ./IPsAtivos.sh 192.168.0.
```

O problema da execução desse _script_ de forma iterativa é que demora bastante para verificar cada endereço da rede. Portanto, você deve usar algumas das técnicas apresentadas na aula para guardar o resultado 
em algum lugar e depois verificá-lo. Então a execução final do _script_ ficaria assim:

```
$ ./IPsAtivos.sh 192.168.0.
Iniciando análise da rede 192.168.0.0/24.
O resultado estará em 192.168.0.txt
$
```

O $ ao final indica que o terminal deve ser retornado ao usuário. Após algum tempo, o _script_ deverá produzir no arquivo  192.168.0.txt o seguinte conteúdo:

```
INICIO
192.168.0.1   on
192.168.0.54  on 
...
192.168.0.101 on
FIM 
```

Detalhe para os marcadores INICIO e FIM. Através dele é que o usuário poderá consultar o andamento da varredura através do terminal no qual iniciou a execução ou de outro.
    

