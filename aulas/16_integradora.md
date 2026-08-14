# 🧪 Aula 16 — Integradora: Monitor de Servidor

**Disciplina:** Programação de *Scripts* — UFC Quixadá
**Material de apoio:** `slides/09` a `slides/13` (revisão do Bloco 2)
**Sessão:** Semana 9 — terça, 06/10
**Entrega desta aula:** 2,5 pontos (Nota 2) — *aula de fechamento do bloco*
**Duração estimada:** 100 minutos

---

## 🎯 Objetivos da Aula

Esta aula não traz assunto novo. Ela junta, em um projeto único, tudo que foi visto
no Bloco 2:

| Aula | O que entra no projeto |
|---|---|
| 10 — Processos | coleta em segundo plano, `$!`, `kill` |
| 11 — Leitura e escrita | menu interativo com `read` e `tput` |
| 12 — Vetores | acumulação de medições |
| 13 — Funções, `getopts`, `trap` | interface de linha de comando e limpeza |
| 14 e 15 — AWK | relatório estatístico |

O formato é diferente das aulas anteriores: **um terço guiado, dois terços de
projeto**. As etapas guiadas montam o esqueleto; a entrega é completar o sistema.

## 🧰 Pré-requisitos

- Aulas 10 a 15. Traga-as abertas — você vai consultar.

## 🗺️ Roteiro

| Etapa | Assunto | Tempo |
|---|---|---|
| 0 | A arquitetura do projeto | 10 min |
| 1 | O coletor | 15 min |
| 2 | O analisador AWK | 15 min |
| 🏁 | Entrega — o sistema completo | 60 min |

---

## 🧩 Etapa 0 — A arquitetura do projeto

Vamos construir um monitor de servidor com **três partes independentes**, que se
comunicam por um arquivo de dados.

```
        ┌──────────────┐
        │ coletor.sh   │  roda em segundo plano, escreve uma linha por medição
        └──────┬───────┘
               │
               ▼
        ┌──────────────┐
        │ medicoes.csv │  timestamp;carga;memoria_livre;processos
        └──────┬───────┘
               │
               ▼
        ┌──────────────┐
        │ analise.awk  │  lê o CSV e produz estatísticas
        └──────────────┘

        ┌──────────────┐
        │ monitor.sh   │  interface: getopts + menu, chama os outros dois
        └──────────────┘
```

Essa separação é deliberada: cada parte é testável sozinha, e a comunicação por
arquivo é o que permite que a coleta continue enquanto você analisa.

### Ação

```bash
ssh disciplina
mkdir -p ~/scripts/aula16
cd ~/scripts/aula16
```

Defina o formato do arquivo antes de escrever qualquer código:

```
timestamp;carga;memoria_livre_mb;processos
2026-10-06 09:15:01;0.42;1832;127
```

### ✅ Checkpoint 0

✔ Você entendeu por que as três partes não se chamam diretamente.

### ❓ Pergunta

O `coletor.sh` poderia calcular as médias ele mesmo, dispensando o `analise.awk`.
Que problema isso traria?

---

## 🧩 Etapa 1 — O coletor

### Ação

Descubra primeiro como obter cada número:

```bash
uptime | awk -F'load average:' '{ print $2 }' | cut -d, -f1 | tr -d ' '
free -m | awk '/^Mem:/ { print $7 }'
ps aux | wc -l
date '+%Y-%m-%d %H:%M:%S'
```

Rode cada um e confirme que devolve um valor limpo, sem rótulo.

Agora o coletor:

```bash
cat > coletor.sh
#!/bin/bash
# Coleta métricas do servidor a cada INTERVALO segundos.
# Uso: ./coletor.sh <arquivo_saida> <intervalo> <quantidade>

ARQUIVO="${1:?informe o arquivo de saida}"
INTERVALO="${2:-5}"
QUANTIDADE="${3:-10}"

trap 'echo "Coleta interrompida."; exit 130' INT TERM

if [ ! -f "$ARQUIVO" ]; then
    echo "timestamp;carga;memoria_livre_mb;processos" > "$ARQUIVO"
fi

for (( i = 1; i <= QUANTIDADE; i++ )); do
    TS=$(date '+%Y-%m-%d %H:%M:%S')
    CARGA=$(uptime | awk -F'load average:' '{ print $2 }' | cut -d, -f1 | tr -d ' ')
    MEM=$(free -m | awk '/^Mem:/ { print $7 }')
    PROC=$(ps aux | wc -l)
    echo "$TS;$CARGA;$MEM;$PROC" >> "$ARQUIVO"
    [ "$i" -lt "$QUANTIDADE" ] && sleep "$INTERVALO"
done
```

Ctrl+D, e teste em primeiro plano com poucas medições:

```bash
chmod +x coletor.sh
./coletor.sh medicoes.csv 1 3
cat medicoes.csv
```

Agora em segundo plano, do jeito que ele vai ser usado:

```bash
./coletor.sh medicoes.csv 2 20 &
COLETOR_PID=$!
echo "coletando no PID $COLETOR_PID"
sleep 6
wc -l medicoes.csv
kill "$COLETOR_PID"
```

### ✅ Checkpoint 1

✔ `medicoes.csv` tem o cabeçalho e uma linha por medição.
✔ Os quatro campos estão preenchidos, sem rótulos e sem espaços sobrando.
✔ Rodando em segundo plano, o terminal volta na hora e o arquivo cresce.

### ❓ Pergunta

O `${1:?informe o arquivo de saida}` substitui um `if` de validação. Ele foi visto
na Aula 12. O que exatamente acontece se você chamar `./coletor.sh` sem argumentos?

---

## 🧩 Etapa 2 — O analisador AWK

### Ação

```bash
cat > analise.awk
BEGIN {
    FS = ";"
    print "=== Análise de medições ==="
}

NR == 1 { next }

{
    n++
    carga_total += $2
    mem_total   += $3
    if (n == 1 || $2 > carga_max) { carga_max = $2; pico_ts = $1 }
    if (n == 1 || $3 < mem_min)   { mem_min   = $3 }
}

END {
    if (n == 0) {
        print "Nenhuma medição encontrada."
        exit 1
    }
    printf "Medições:        %d\n", n
    printf "Carga média:     %.2f\n", carga_total / n
    printf "Carga máxima:    %.2f (em %s)\n", carga_max, pico_ts
    printf "Memória média:   %.0f MB\n", mem_total / n
    printf "Memória mínima:  %d MB\n", mem_min
}
```

Ctrl+D, e:

```bash
awk -f analise.awk medicoes.csv
```

Teste o caminho de erro:

```bash
printf 'timestamp;carga;memoria_livre_mb;processos\n' > vazio.csv
awk -f analise.awk vazio.csv; echo "retorno=$?"
```

### ✅ Checkpoint 2

✔ A análise imprime as cinco linhas com números coerentes.
✔ Com o arquivo vazio, imprime a mensagem e retorna `1`.

### ❓ Pergunta

O bloco `NR == 1 { next }` descarta o cabeçalho. O que aconteceria com a
`carga_média` sem essa linha?

---

## 🏁 Entrega da Aula — 2,5 pontos (Nota 2)

Você tem **60 minutos**. Individual.

Escreva o `~/scripts/aula16/monitor.sh`, a interface que amarra o sistema. Ele deve
funcionar de **dois modos**.

### Modo 1 — linha de comando, com `getopts` (1,25 ponto)

| Opção | Argumento | Ação |
|---|---|---|
| `-c` | quantidade | inicia a coleta **em segundo plano** e imprime o PID |
| `-i` | segundos | define o intervalo entre medições (padrão: 5) |
| `-a` | — | roda o `analise.awk` sobre o arquivo de medições |
| `-k` | — | encerra a coleta em andamento |
| `-h` | — | imprime a ajuda e sai com retorno 0 |

```
$ ./monitor.sh -c 20 -i 2
Coleta iniciada em segundo plano (PID 5312, 20 medições a cada 2s).
$ ./monitor.sh -a
=== Análise de medições ===
Medições:        6
...
$ ./monitor.sh -k
Coleta encerrada (PID 5312).
$ ./monitor.sh -x
Opção inválida: -x
```

Requisitos:

1. O PID do coletor deve ser gravado em um arquivo `monitor.pid`, para que o `-k`
   funcione em uma **execução posterior** do `monitor.sh`.
2. O `-k` deve avisar se não há coleta em andamento, e retornar `1`.
3. Opção inválida: mensagem no `stderr` e retorno `1`.
4. Use um `trap` para remover o `monitor.pid` quando o *script* for interrompido
   durante o início da coleta.

### Modo 2 — menu interativo (1,25 ponto)

Se o `monitor.sh` for chamado **sem nenhuma opção**, ele entra em modo interativo.

1. Um menu **dentro de uma função**, com título colorido e em negrito (`tput`), e
   opções alinhadas com `printf`.
2. Opções: `1` iniciar coleta, `2` ver análise, `3` ver as últimas 5 medições,
   `4` encerrar coleta, `5` sair.
3. Cada opção limpa a tela, executa, mostra o resultado e espera uma tecla.
4. O laço só termina na opção 5, que deve **encerrar a coleta se ela estiver
   rodando** e restaurar o terminal.
5. Opção inválida não pode quebrar o laço.
6. O menu deve mostrar, no cabeçalho, se há coleta em andamento:

   ```
   === MONITOR DO SERVIDOR ===   [coletando: PID 5312]
   ```

   ou

   ```
   === MONITOR DO SERVIDOR ===   [parado]
   ```

### Critérios de correção

**Modo 1 — 1,25 ponto**

| # | Critério | Valor |
|---|---|---|
| 1 | `getopts` trata as cinco opções e a inválida | 0,30 |
| 2 | `-c` inicia em segundo plano e devolve o terminal na hora | 0,25 |
| 3 | O `monitor.pid` persiste entre execuções e o `-k` funciona | 0,30 |
| 4 | `-a` chama o `analise.awk` e mostra o relatório | 0,25 |
| 5 | Há `trap` para limpar o `monitor.pid` | 0,15 |

**Modo 2 — 1,25 ponto**

| # | Critério | Valor |
|---|---|---|
| 6 | Sem opções, entra no menu interativo | 0,25 |
| 7 | O menu usa função, `tput` e `printf` alinhado | 0,35 |
| 8 | O cabeçalho reflete o estado da coleta | 0,35 |
| 9 | A opção 5 encerra a coleta e restaura o terminal | 0,30 |

Correção:

```bash
cd ~/scripts/aula16
./monitor.sh -h; echo "retorno=$?"
time ./monitor.sh -c 30 -i 1        # deve voltar em menos de 1 segundo
cat monitor.pid
sleep 5
./monitor.sh -a
./monitor.sh -k
./monitor.sh -k; echo "retorno=$?"  # já encerrada: deve ser 1
./monitor.sh -x 2>/dev/null; echo "retorno=$?"
./monitor.sh                        # menu interativo
```

> 💡 **Ordem de ataque sugerida.** Faça o `-h` e o `getopts` primeiro (é o
> esqueleto), depois `-c` e `-k` (a parte de processos), depois `-a` (é só chamar o
> AWK), e por último o menu — que reaproveita tudo em funções.
>
> 💡 Se o tempo apertar, um modo bem-feito vale mais que dois pela metade.

---

## ✅ Checklist de Encerramento

| # | Verificação | Comando |
|---|---|---|
| 1 | Os quatro arquivos existem | `ls ~/scripts/aula16` |
| 2 | O `monitor.sh` usa `getopts` | `grep -c getopts monitor.sh` |
| 3 | Tem `trap` | `grep -c trap monitor.sh` |
| 4 | O menu está em função | `grep -c "^menu()" monitor.sh` |
| 5 | Nenhum coletor ficou rodando | `ps aux \| grep coletor` |
| 6 | Nenhum `.pid` órfão | `ls *.pid 2>/dev/null` |

> ⚠️ Os itens 5 e 6 são obrigatórios: **não deixe processos rodando no servidor** ao
> sair da sala.

---

## 💬 Para Discutir em Sala

- O projeto tem quatro arquivos que se comunicam por um CSV. Poderia ser um único
  *script* de 200 linhas. O que a separação lhe deu, na prática, durante esta aula?
- Você guardou o PID em arquivo para sobreviver entre execuções. É a mesma técnica
  que o `systemd` usa. Que problema aparece se o processo morrer sem apagar o `.pid`?

## 📌 Fechamento da Nota 2

A próxima sessão (quarta, 07/10) é de **entrega e correção**. Traga resolvidas as
entregas das Aulas 10 a 16 — as **duas piores serão descartadas**.

Confira antes de vir:

```bash
ls -d ~/scripts/aula1[0-6]
```

Na **Aula 17** começa o Bloco 3, com *scripts* de inicialização
(`slides/14_scripts_de_inicializacao`). O foco muda: sai o processamento de texto,
entra a administração de sistemas e a nuvem.
