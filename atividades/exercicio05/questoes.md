# Exercício 05

Data: 12/01/2021

Coloque os arquivos na pasta _exercicios/exercicio05_.

## Questão 01
Faça um _script_ chamados _ipsValidos.sh_ que receba um arquivo texto chamado _ips.txt_ contendo uma lista de endereços IP e gere um outro arquivo chamados _ips_classificados.txt_, contendo um relatório dos endereços IP válidos e inválidos. Por IP válido, entenda um IP no qual cada campo está entre 0 e 255. O arquivo de entrada possui o seguinte formato:

```
200.135.80.9
192.168.1.1
8.35.67.74
257.32.4.5
85.345.1.2
1.2.3.4
9.8.234.5
192.168.0.256
```

O arquivo de saída possui o seguinte formato:

```
Endereços válidos:
200.135.80.9
192.168.1.1
8.35.67.74
1.2.3.4
9.8.234.5

Endereços inválidos:
257.32.4.5
85.345.1.2
192.168.0.256
```

A execução seria:
```
$ ./ipsValidos.sh ips.txt
```

## Questão 02

 Crie um script chamado _backupIncremental.sh_, que receba como parâmetro dois diretórios, chamados de _dir1_ e _dir2_. Ao ser executado, o _script_ deve copiar todos os arquivos de _dir1_ que não tenham o mesmo nome de um arquivo em _dir2_.  Por exemplo, considere a estrutura de diretórios abaixo. 

```
├── backupIncremental.sh
├── dir1
│   ├── arq1.txt
│   ├── arq2.txt
│   └── arq3.txt
│   
└── dir2
    └── arq1.txt
```

Quando o comando: 
```
$./backupIncremental.sh dir1/ dir2/ 
```
for executado, somente os arquivos _arq2.txt_ e _arq3.txt_ devem ser copiados de _dir1_ para _dir2_. O arquivo _arq1.txt_ não deve ser copiado novamente! Este é apenas um exemplo, seu _script_ deve funcionar para um número arbitrário de arquivos. 