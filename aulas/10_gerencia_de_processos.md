# 🧪 Aula 10 — Gerência de Processos

**Disciplina:** Programação de *Scripts* — UFC Quixadá
**Material de apoio:** `slides/09_gerencia_de_processos`
**Sessão:** Semana 6 — terça, 15/09
**Entrega desta aula:** 1,25 pontos (Nota 2)
**Duração estimada:** 100 minutos

---

## 🎯 Objetivos da Aula

Ao final desta aula você deve ser capaz de:

- Listar e interpretar processos com `ps`.
- Executar comandos em segundo plano com `&` e recuperar o PID com `$!`.
- Encerrar processos com `kill` e entender a diferença entre os sinais.
- Manter um processo vivo depois do *logout* com `nohup`.
- Trabalhar com múltiplos painéis usando `tmux`.

## 🧰 Pré-requisitos

- Bloco 1 concluído. Esta aula usa laços, condicionais e redirecionamento.

## 🗺️ Roteiro

| Etapa | Assunto | Tempo |
|---|---|---|
| 0 | Vendo os processos | 15 min |
| 1 | Segundo plano com `&` | 20 min |
| 2 | Encerrando com `kill` | 15 min |
| 3 | Sobrevivendo ao *logout*: `nohup` | 10 min |
| 4 | `tmux` | 15 min |
| 🏁 | Entrega | 25 min |

---

## 🧩 Etapa 0 — Vendo os processos

### Ação

```bash
ssh disciplina
mkdir -p ~/scripts/aula10
cd ~/scripts/aula10

ps                  # só os processos do seu terminal
ps -f               # formato completo, com PPID e comando
ps aux | head -5    # todos os processos do sistema
ps aux | wc -l      # quantos processos existem agora
```

As colunas que mais importam:

| Coluna | Significado |
|---|---|
| `PID` | identificador do processo |
| `PPID` | identificador do processo **pai** |
| `TTY` | terminal ao qual está ligado |
| `STAT` | estado (`S` dormindo, `R` executando, `Z` zumbi) |
| `CMD` | o comando |

Encontre um processo pelo nome:

```bash
ps aux | grep sshd
pgrep -a sshd
```

Veja a relação pai/filho:

```bash
echo "meu shell é o PID $$"
ps -f
```

A variável `$$` guarda o PID do *shell* atual. Repare que o `ps` aparece como
filho dele.

### ✅ Checkpoint 0

✔ `echo $$` imprime um número que também aparece na coluna `PID` do `ps -f`.
✔ `ps aux | wc -l` responde algumas dezenas.

### ❓ Pergunta

Rode `ps aux | grep sshd`. Uma das linhas do resultado é o **próprio `grep`**. Por
que ele aparece na própria busca?

---

## 🧩 Etapa 1 — Segundo plano com `&`

### Ação

Crie um *script* que demora:

```bash
cat > contador.sh
#!/bin/bash
i=1
while true; do
    echo "$(date +%H:%M:%S) - volta $i"
    i=$(( i + 1 ))
    sleep 1
done
```

Ctrl+D, e:

```bash
chmod +x contador.sh
```

Execute normalmente — ele prende o terminal:

```bash
./contador.sh
```

Encerre com **Ctrl+C**. Agora execute em segundo plano:

```bash
./contador.sh > contador.log &
```

A saída mostra duas coisas:

```
[1] 4821
```

O `[1]` é o número do **job** e `4821` é o **PID**. O terminal voltou para você.

O PID do último processo em segundo plano fica na variável `$!`:

```bash
./contador.sh > outro.log &
PID_CONTADOR=$!
echo "O contador está no PID $PID_CONTADOR"
```

Acompanhe o arquivo crescendo:

```bash
tail -f contador.log
```

Saia do `tail` com **Ctrl+C** — isso encerra o `tail`, não o contador.

Gerencie os *jobs*:

```bash
jobs            # lista os jobs deste terminal
jobs -l         # com o PID
```

### ✅ Checkpoint 1

✔ `jobs` lista dois contadores rodando.
✔ `tail -f contador.log` mostra linhas novas aparecendo a cada segundo.
✔ `echo $PID_CONTADOR` imprime um número.

### ❓ Pergunta

Você rodou dois contadores. O `$!` guarda o PID de qual deles? E como você
recuperaria o PID do primeiro?

---

## 🧩 Etapa 2 — Encerrando com `kill`

### Ação

```bash
jobs -l
kill "$PID_CONTADOR"
jobs
```

O `kill` não "mata" — ele **envia um sinal**. O padrão é o `TERM` (15), que pede
educadamente que o processo encerre.

```bash
kill -l | head -5          # lista os sinais disponíveis
```

Os três que mais importam:

| Sinal | Número | O que faz |
|---|---|---|
| `SIGTERM` | 15 | pede para encerrar; o processo pode tratar |
| `SIGINT` | 2 | o mesmo que Ctrl+C |
| `SIGKILL` | 9 | encerra à força; **não** pode ser tratado |

Encerre o outro contador com o sinal explícito:

```bash
jobs -l
kill -TERM %1        # pelo número do job
jobs
```

Se um processo ignora o `TERM`, resta o `KILL`:

```bash
./contador.sh > /dev/null &
PID2=$!
kill -9 "$PID2"
jobs
```

> ⚠️ O `kill -9` não dá ao processo nenhuma chance de fechar arquivos ou limpar
> temporários. Use-o só quando o `TERM` não resolver.

Encerrar pelo nome:

```bash
./contador.sh > /dev/null &
pkill -f contador.sh
jobs
```

### ✅ Checkpoint 2

✔ Depois dos `kill`, o `jobs` não lista mais nada.
✔ `ps aux | grep contador.sh` só mostra a linha do próprio `grep`.

### ❓ Pergunta

Por que o `SIGKILL` não pode ser tratado pelo processo? Que problema existiria se
pudesse?

---

## 🧩 Etapa 3 — Sobrevivendo ao *logout*: `nohup`

### Ação

Um processo em segundo plano ainda pertence ao seu terminal. Quando você desconecta,
ele recebe um `SIGHUP` e morre. Teste:

```bash
./contador.sh > teste_hup.log &
exit
```

Reconecte e verifique:

```bash
ssh disciplina
cd ~/scripts/aula10
ps aux | grep contador.sh
tail -2 teste_hup.log
```

O horário da última linha é o do momento em que você desconectou.

O `nohup` desliga o processo do terminal:

```bash
nohup ./contador.sh > nohup_teste.log 2>&1 &
echo $!
exit
```

Reconecte:

```bash
ssh disciplina
cd ~/scripts/aula10
ps aux | grep contador.sh
tail -2 nohup_teste.log
```

Dessa vez ele continuou. Encerre:

```bash
pkill -f contador.sh
```

### ✅ Checkpoint 3

✔ Sem `nohup`, o *log* para de crescer depois do `exit`.
✔ Com `nohup`, o *log* continua crescendo.

### ❓ Pergunta

O nome `SIGHUP` vem de *hang up*, o gesto de desligar o telefone. O que isso conta
sobre a época em que o Unix foi projetado?

---

## 🧩 Etapa 4 — `tmux`

O `nohup` resolve a persistência, mas você perde a interatividade. O `tmux` mantém
uma **sessão inteira** viva no servidor.

### Ação

```bash
tmux new -s aula10
```

Você entra em uma sessão. Note a barra de status embaixo. Todos os atalhos começam
com o **prefixo Ctrl+B**, solto, seguido da tecla:

| Atalho | Ação |
|---|---|
| `Ctrl+B` depois `%` | divide o painel na **vertical** |
| `Ctrl+B` depois `"` | divide na **horizontal** |
| `Ctrl+B` depois seta | move entre painéis |
| `Ctrl+B` depois `d` | *detach* — sai deixando a sessão viva |
| `Ctrl+B` depois `x` | fecha o painel atual |

Experimente:

1. `Ctrl+B` `%` para dividir na vertical.
2. No painel da esquerda, rode `./contador.sh`.
3. `Ctrl+B` seta-direita para ir ao painel da direita.
4. Rode `tail -f contador.log` — não, melhor: rode `watch -n 1 date`.
5. `Ctrl+B` `d` para sair.

De volta ao *shell* normal:

```bash
tmux ls                 # lista as sessões vivas
exit                    # desconecta do servidor
```

Reconecte e recupere a sessão:

```bash
ssh disciplina
tmux ls
tmux attach -t aula10
```

Tudo continua rodando, exatamente como você deixou. Para encerrar de vez, feche os
painéis com `Ctrl+B` `x` ou rode `tmux kill-session -t aula10`.

### ✅ Checkpoint 4

✔ `tmux ls` lista a sessão `aula10` mesmo depois de você sair do servidor.
✔ Ao dar *attach*, os dois painéis estão como você deixou.

### ❓ Pergunta

Qual a diferença prática entre rodar um comando com `nohup ... &` e rodá-lo dentro
de uma sessão `tmux`?

---

## 🏁 Entrega da Aula — 1,25 pontos (Nota 2)

Individualmente, nos últimos 25 minutos.

Crie o *script* `~/scripts/aula10/varredura.sh`, que verifica quais endereços de
uma sub-rede /24 estão ativos.

1. Recebe como parâmetro os **três primeiros octetos** da rede, com o ponto final.
   Exemplo: `./varredura.sh 192.168.0.`
2. Valide o parâmetro: se não foi passado, imprima
   `Uso: ./varredura.sh <tres.primeiros.octetos.>` e encerre com retorno `1`.
3. Ao ser executado, imprime **duas linhas** e **devolve o terminal imediatamente**:

   ```
   $ ./varredura.sh 192.168.0.
   Iniciando análise da rede 192.168.0.0/24.
   O resultado estará em 192.168.0.txt
   $
   ```

4. A varredura roda em **segundo plano** e grava o resultado no arquivo
   `<rede>txt` — no exemplo, `192.168.0.txt` — com este formato:

   ```
   INICIO
   192.168.0.1 on
   192.168.0.54 on
   192.168.0.101 on
   FIM
   ```

5. Os marcadores `INICIO` e `FIM` são obrigatórios: é por eles que o usuário
   acompanha o andamento com `tail -f` enquanto a varredura ainda roda.
6. Apenas os endereços que **responderam** aparecem no arquivo.

> 💡 Use `ping -c 1 -W 1 <ip>` para testar um endereço. O código de retorno diz se
> respondeu. Redirecione a saída do `ping` para `/dev/null` — o que interessa é o `$?`.
>
> 💡 Testar 254 endereços em sequência demora. Não tente paralelizar hoje; o que
> importa é o terminal voltar na hora e o arquivo ir sendo preenchido.

### Critérios de correção

| # | Critério | Valor |
|---|---|---|
| 1 | Valida o parâmetro e retorna 1 quando ausente | 0,15 |
| 2 | Imprime as duas linhas e **devolve o terminal na hora** | 0,35 |
| 3 | O arquivo é criado com o nome derivado do parâmetro | 0,20 |
| 4 | Contém `INICIO` no começo e `FIM` no fim | 0,25 |
| 5 | Lista apenas endereços que responderam, um por linha | 0,30 |

Correção:

```bash
cd ~/scripts/aula10
./varredura.sh; echo "retorno=$?"
time ./varredura.sh 127.0.0.       # deve voltar em menos de 1 segundo
head -3 127.0.0.txt
sleep 20 && tail -2 127.0.0.txt
```

O `time` é o critério 2: se o *script* travar o terminal, ele falha.

---

## ✅ Checklist de Encerramento

| # | Verificação | Comando |
|---|---|---|
| 1 | O *script* devolve o terminal na hora | `time ./varredura.sh 127.0.0.` |
| 2 | O arquivo começa com `INICIO` | `head -1 127.0.0.txt` |
| 3 | O arquivo termina com `FIM` | `tail -1 127.0.0.txt` |
| 4 | Não sobrou processo rodando | `ps aux \| grep varredura` |
| 5 | Nenhuma sessão `tmux` esquecida | `tmux ls` |

---

## 💬 Para Discutir em Sala

- Seu *script* devolve o terminal na hora, mas o resultado demora. Como o usuário
  sabe se ele terminou ou se travou? Foi para isso que serviram o `INICIO` e o `FIM`.
- Você deixou processos rodando no servidor durante a aula. Se toda a turma fizer
  isso e ninguém encerrar, o que acontece com a máquina?

## 📌 Para a Próxima Aula

Na **Aula 11** vamos ver leitura e escrita (`slides/10_leitura_e_escrita`): `read`,
`printf` e `tput`. É a aula que transforma *scripts* mudos em programas interativos.
