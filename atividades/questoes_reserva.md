# Banco de Questões de Reserva

Enunciados que **não** foram usados como entrega de nenhuma aula. Servem para prova,
segunda chamada, substituição de entrega ou exercício extra.

Cada questão indica a aula cujo conteúdo ela cobra.

---

## R01 — `ipsValidos.sh` *(Aula 09 — iterações)*

Faça um *script* chamado `ipsValidos.sh` que receba um arquivo texto chamado
`ips.txt` contendo uma lista de endereços IP e gere outro arquivo,
`ips_classificados.txt`, com um relatório dos endereços válidos e inválidos. Por IP
válido, entenda um IP no qual cada campo está entre 0 e 255.

Entrada:

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

Saída:

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

Execução: `./ipsValidos.sh ips.txt`

---

## R02 — `backupIncremental.sh` *(Aula 09 — iterações)*

Crie um *script* `backupIncremental.sh` que receba como parâmetro dois diretórios,
`dir1` e `dir2`. Ao ser executado, deve copiar todos os arquivos de `dir1` que **não**
tenham o mesmo nome de um arquivo em `dir2`.

```
├── backupIncremental.sh
├── dir1
│   ├── arq1.txt
│   ├── arq2.txt
│   └── arq3.txt
└── dir2
    └── arq1.txt
```

Ao executar `./backupIncremental.sh dir1/ dir2/`, apenas `arq2.txt` e `arq3.txt`
devem ser copiados. O *script* deve funcionar para um número arbitrário de arquivos,
inclusive com espaços no nome.

---

## R03 — `latencia.sh` *(Aula 09 — iterações, sem AWK)*

Desenvolva o *script* `latencia.sh`, que recebe como parâmetro o nome de um arquivo
de texto contendo um endereço IP por linha.

O *script* deve usar o `ping` para enviar dez pacotes ICMP a cada endereço,
calculando o tempo médio de resposta. Ao final, deve imprimir a lista ordenada do
menor para o maior tempo médio, informando o endereço e o tempo.

**Restrição:** não pode usar `awk`.

```
$ cat enderecos_ip.txt
8.8.8.8
192.168.1.1
208.67.222.222
104.26.4.156
$ ./latencia.sh enderecos_ip.txt
192.168.1.1 11.1ms
104.26.4.156 23.7ms
208.67.222.222 55.4ms
8.8.8.8 94.0ms
```

---

## R04 — `alertaDiretorio.sh` *(Aula 10 — processos)*

Escreva um *script* `alertaDiretorio.sh` que recebe como parâmetros um valor inteiro
(intervalo em segundos) e o caminho de um diretório.

A cada intervalo, a quantidade de arquivos no diretório é analisada. Caso ela mude
entre duas verificações, o *script* deve acrescentar ao arquivo `dirSensors.log`:

1. A data em que a alteração foi percebida.
2. Quantos arquivos existiam.
3. Quantos existem agora.
4. Quais foram adicionados ou removidos.

```
$ ./alertaDiretorio.sh 5 diretorioMonitorado
[25-01-2026 12:59:51] Alteração! 3->2. Removidos: notas.txt
[25-01-2026 13:04:51] Alteração! 2->4. Adicionados: a.txt, b.txt
[25-01-2026 13:09:51] Alteração! 4->3. Removidos: a.txt
```

**Correção:** usando `tmux`, divida a tela em dois painéis. No painel 1, deixe o
*script* rodando; no painel 2, entre no diretório monitorado. Ao criar ou remover
arquivos no painel 2, as mensagens devem aparecer no painel 1.

---

## R05 — `task_manager.sh` *(Aula 13 — `getopts` e `trap`)*

Crie um *script* `task_manager.sh` que simula um gerenciador de tarefas simples,
usando `getopts` para processar opções e `trap` para garantir a limpeza de arquivos
temporários.

| Opção | Argumento | Ação |
|---|---|---|
| `-n` | obrigatório | nome da tarefa (e do arquivo temporário) |
| `-t` | obrigatório | tempo de execução em segundos (máximo 15) |

Requisitos:

1. **`trap`** — configure um `trap` para `SIGINT` (Ctrl+C). Ao receber o sinal, exiba
   `Tarefa interrompida. Limpando...` e **remova** o arquivo temporário antes de sair.
2. **Função `executar_tarefa`** — recebe o nome (`$1`) e o tempo (`$2`). Cria um
   arquivo temporário com o nome da tarefa (ex.: `backup.tmp`), imprime a mensagem de
   início, aguarda com `sleep` e imprime a conclusão.
3. **`getopts`** — laço `while getopts` processando `-n` e `-t`, chamando a função
   com os valores capturados.

```
$ ./task_manager.sh -n backup -t 5
Iniciando tarefa: backup (PID: 4821)
Tarefa 'backup' concluída com sucesso.

$ ./task_manager.sh -n teste_curto -t 10
Iniciando tarefa: teste_curto (PID: 4830)
^C
Tarefa interrompida. Limpando...
```

**Correção:** executar `./task_manager.sh -n lixo -t 15`, apertar Ctrl+C e verificar
que `lixo.tmp` **não** existe.

---

## R06 — `faturamento.awk` *(Aula 15 — AWK)*

Você recebeu um arquivo de vendas `vendas.txt`, com campos separados por ponto e
vírgula, no formato `Produto;PrecoUnitario;Quantidade`:

```
Teclado;50;10
Mouse;20;5
Monitor;800;2
Cabo HDMI;15;3
Webcam;150;4
```

Desenvolva `faturamento.awk` que:

1. Para cada produto, calcule o **valor total** (preço × quantidade).
2. Imprima o nome e o valor total **apenas** dos produtos cujo total seja **maior ou
   igual a 200**.
3. Use o formato `Produto: ValorTotal`.

```
$ awk -F\; -f faturamento.awk vendas.txt
Teclado: 500
Monitor: 1600
Webcam: 600
```

---

## R07 — `latencia.awk` *(Aula 15 — AWK com redirecionamento)*

O objetivo é processar dados de IP e latência, ordenando o resultado final com um
*pipe* para comando externo.

Considere `ips_latencia.txt`, separado por espaço:

```
192.168.0.1 11.1
54.230.57.207 55.4
8.8.8.8 94.0
```

Crie `latencia.awk` que:

1. **Vetor** — para cada linha, armazene o IP (`$1`) e a latência (`$2`) em um vetor,
   usando o IP como chave.
2. **`END`** — itere sobre o vetor com `for (chave in vetor)`.
3. **Ordenação com *pipe*** — redirecione a saída de cada `print` para o comando
   externo `sort`, ordenando pela latência, do menor para o maior.
   *Dica: `| "sort -k2n"`.*
4. **Formatação** — use `printf` para acrescentar `ms` ao valor.

```
$ awk -f latencia.awk ips_latencia.txt
192.168.0.1 11.1ms
54.230.57.207 55.4ms
8.8.8.8 94.0ms
```

---

## R08 — `agenda.sh` *(Aula 13 — funções e parâmetros)*

Desenvolva uma agenda em um *script* `agenda.sh` que gerencie nomes e *e-mails* em um
arquivo `agenda.db`, no formato:

```
João Marcelo:joao.marcelo@ufc.br
Jeandro Bezerra:jeandro@ufc.br
```

O *script* deve suportar três operações, passadas por parâmetro, e avisar quando o
arquivo for criado pela primeira vez:

```
$ ./agenda.sh listar
Arquivo vazio!!!
$ ./agenda.sh adicionar "João Marcelo" "joao.marcelo@ufc.br"
Arquivo criado!!!
Usuário João Marcelo adicionado.
$ ./agenda.sh adicionar "Jeandro Bezerra" "jeandro@ufc.br"
Usuário Jeandro Bezerra adicionado.
$ ./agenda.sh listar
João Marcelo:joao.marcelo@ufc.br
Jeandro Bezerra:jeandro@ufc.br
$ ./agenda.sh remover joao.marcelo@ufc.br
Usuário João Marcelo removido.
```

1. **Adicionar** — parâmetro `adicionar` mais nome e *e-mail*.
2. **Listar** — apenas o parâmetro `listar`.
3. **Remover** — parâmetro `remover` mais o *e-mail*. Remover alguém que não existe
   deve apenas avisar, sem alterar o arquivo.
