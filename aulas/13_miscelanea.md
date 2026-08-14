# 🧪 Aula 13 — Funções, `getopts` e `trap`

**Disciplina:** Programação de *Scripts* — UFC Quixadá
**Material de apoio:** `slides/12_miscelanea`
**Sessão:** Semana 7 — quarta, 23/09
**Entrega desta aula:** 1,25 pontos (Nota 2)
**Duração estimada:** 100 minutos

---

## 🎯 Objetivos da Aula

Ao final desta aula você deve ser capaz de:

- Escrever funções com parâmetros e devolver resultados.
- Tratar opções de linha de comando com `getopts`.
- Capturar sinais com `trap` e limpar arquivos temporários.
- Explicar o que o `eval` faz e por que ele é perigoso.
- Depurar um *script* passo a passo com `set -x`.

## 🧰 Pré-requisitos

- Aulas 10 a 12. Esta aula usa parâmetros, `case`, vetores e processos.

## 🗺️ Roteiro

| Etapa | Assunto | Tempo |
|---|---|---|
| 0 | Funções | 20 min |
| 1 | `getopts` | 25 min |
| 2 | `trap` | 20 min |
| 3 | `eval` e depuração | 10 min |
| 🏁 | Entrega | 25 min |

---

## 🧩 Etapa 0 — Funções

### Ação

```bash
ssh disciplina
mkdir -p ~/scripts/aula13
cd ~/scripts/aula13
```

Uma função recebe parâmetros do mesmo jeito que um *script*: `$1`, `$2`, `$#`.

```bash
cat > funcoes.sh
#!/bin/bash

saudacao() {
    echo "Olá, $1! Você passou $# parâmetro(s)."
}

soma() {
    echo $(( $1 + $2 ))
}

eh_par() {
    [ $(( $1 % 2 )) -eq 0 ]
}

saudacao "Ana"
RESULTADO=$(soma 3 4)
echo "3 + 4 = $RESULTADO"

if eh_par 10; then echo "10 é par"; fi
if eh_par 7;  then echo "7 é par"; else echo "7 é ímpar"; fi
```

Ctrl+D, e:

```bash
chmod +x funcoes.sh
./funcoes.sh
```

Há **duas** formas de uma função devolver algo, e elas servem a propósitos
diferentes:

| Forma | Como recuperar | Serve para |
|---|---|---|
| `echo` (imprime) | `VAR=$(funcao)` | devolver um **valor** |
| `return N` | `$?` | devolver um **status** (0 a 255) |

> ⚠️ O `return` só aceita números de 0 a 255, e a semântica é a do código de saída:
> `0` é sucesso. Não use `return` para devolver um resultado de cálculo.

Repare na função `eh_par`: ela não tem `return` nenhum. O valor de retorno é o do
**último comando executado** — o `[ ]`. Por isso ela funciona direto no `if`.

Variáveis dentro de funções são globais por padrão. Use `local`:

```bash
cat > escopo.sh
#!/bin/bash
X="global"

sem_local()  { X="alterado"; }
com_local()  { local X="alterado"; }

sem_local; echo "depois de sem_local: $X"
X="global"
com_local; echo "depois de com_local: $X"
```

Ctrl+D, `chmod +x escopo.sh`, e rode.

### ✅ Checkpoint 0

✔ `./funcoes.sh` imprime a saudação, `3 + 4 = 7`, `10 é par` e `7 é ímpar`.
✔ `./escopo.sh` mostra `alterado` no primeiro caso e `global` no segundo.

### ❓ Pergunta

A função `soma` devolve o resultado com `echo`. Isso significa que ela **não pode**
imprimir mensagens de depuração. Por quê? E como você resolveria isso?

---

## 🧩 Etapa 1 — `getopts`

Até agora seus *scripts* liam parâmetros pela posição: `$1`, `$2`. Isso quebra
assim que o usuário troca a ordem. O `getopts` trata **opções** de verdade.

### Ação

```bash
cat > opcoes.sh
#!/bin/bash

NOME=""
IDADE=""
VERBOSO=0

while getopts "n:i:v" opcao; do
    case "$opcao" in
        n) NOME="$OPTARG" ;;
        i) IDADE="$OPTARG" ;;
        v) VERBOSO=1 ;;
        \?) echo "Opção inválida: -$OPTARG" >&2; exit 1 ;;
        :)  echo "A opção -$OPTARG exige um argumento" >&2; exit 1 ;;
    esac
done

[ "$VERBOSO" -eq 1 ] && echo "(modo verboso)"
echo "Nome: $NOME"
echo "Idade: $IDADE"
```

Ctrl+D, `chmod +x opcoes.sh`, e teste:

```bash
./opcoes.sh -n Ana -i 25
./opcoes.sh -i 25 -n Ana        # ordem trocada, mesmo resultado
./opcoes.sh -v -n Ana
./opcoes.sh -x                  # opção inválida
./opcoes.sh -n                  # falta o argumento
```

A anatomia da cadeia `"n:i:v"`:

- Cada letra é uma opção aceita.
- Os **dois-pontos depois** da letra significam "esta opção exige um argumento".
- O `n:` exige argumento; o `v` não.

As variáveis que o `getopts` mantém:

| Variável | Conteúdo |
|---|---|
| `$opcao` | a letra da opção atual (o nome que você escolheu) |
| `$OPTARG` | o argumento da opção, quando há |
| `$OPTIND` | o índice do próximo parâmetro a processar |

Para pegar o que sobrou depois das opções:

```bash
cat >> opcoes.sh
shift $(( OPTIND - 1 ))
echo "Sobrou: $*"
```

Ctrl+D, e:

```bash
./opcoes.sh -n Ana arquivo1.txt arquivo2.txt
```

> 💡 Se você colocar um `:` no **começo** da cadeia (`":n:i:v"`), o `getopts` para
> de imprimir as próprias mensagens de erro e passa a acionar o ramo `:` do seu
> `case`. É o que permite escrever mensagens em português, como acima.

### ✅ Checkpoint 1

✔ `-n Ana -i 25` e `-i 25 -n Ana` produzem a mesma saída.
✔ `-x` cai no ramo `\?` e retorna 1.
✔ Depois do `shift`, `Sobrou:` mostra os nomes de arquivo.

### ❓ Pergunta

Por que o `shift $(( OPTIND - 1 ))` é necessário? O que aconteceria com `$1` sem ele?

---

## 🧩 Etapa 2 — `trap`

O `trap` executa um comando quando o *script* recebe um sinal — inclusive o Ctrl+C.

### Ação

```bash
cat > limpeza.sh
#!/bin/bash

TEMP="dados_$$.tmp"

limpar() {
    echo
    echo "Interrompido. Removendo $TEMP..."
    rm -f "$TEMP"
    exit 130
}

trap limpar INT TERM

echo "Criando $TEMP"
echo "dados importantes" > "$TEMP"
echo "Trabalhando por 30 segundos. Aperte Ctrl+C."
sleep 30
rm -f "$TEMP"
echo "Terminei normalmente."
```

Ctrl+D, `chmod +x limpeza.sh`. Rode e **deixe terminar**:

```bash
./limpeza.sh
ls dados_*.tmp 2>/dev/null || echo "nenhum temporário sobrou"
```

Agora rode e aperte **Ctrl+C** no meio:

```bash
./limpeza.sh
# aperte Ctrl+C
ls dados_*.tmp 2>/dev/null || echo "nenhum temporário sobrou"
```

Compare com um *script* sem `trap`:

```bash
cat > sem_trap.sh
#!/bin/bash
TEMP="lixo_$$.tmp"
echo "dados" > "$TEMP"
echo "Aperte Ctrl+C"
sleep 30
rm -f "$TEMP"
```

Ctrl+D, `chmod +x sem_trap.sh`, rode e interrompa:

```bash
./sem_trap.sh
# Ctrl+C
ls lixo_*.tmp
```

O temporário ficou lá.

Os sinais mais usados no `trap`:

| Sinal | Quando dispara |
|---|---|
| `INT` | Ctrl+C |
| `TERM` | `kill` sem opção |
| `EXIT` | **sempre** que o *script* termina, por qualquer motivo |
| `ERR` | quando um comando falha |

O `EXIT` é o mais robusto para limpeza — cobre saída normal e interrupção:

```bash
trap 'rm -f "$TEMP"' EXIT
```

> ⚠️ Não existe `trap` para o `SIGKILL` (`kill -9`). Ele não pode ser capturado —
> é justamente essa a garantia que ele oferece.

### ✅ Checkpoint 2

✔ Com `trap`, o `.tmp` some tanto na saída normal quanto no Ctrl+C.
✔ Sem `trap`, o `.tmp` sobrevive ao Ctrl+C.

Limpe antes de seguir: `rm -f lixo_*.tmp dados_*.tmp`

### ❓ Pergunta

O `trap ... EXIT` cobre mais casos que o `trap ... INT`. Por que alguém escolheria
o `INT`?

---

## 🧩 Etapa 3 — `eval` e depuração

### Ação — `eval`

O `eval` monta uma linha de comando a partir de texto e a executa:

```bash
COMANDO="ls -l /etc"
$COMANDO                 # funciona por acaso
eval "$COMANDO"          # funciona por construção
```

A diferença aparece quando há aspas ou redirecionamento no texto:

```bash
CMD='echo "um   dois" > saida.txt'
$CMD                     # imprime tudo literalmente, não redireciona
cat saida.txt 2>/dev/null || echo "não criou arquivo"

eval "$CMD"
cat saida.txt
```

Agora o `eval "$(ssh-agent -s)"` da Aula 01 faz sentido: o `ssh-agent -s` imprime
**texto que é código de *shell***, e só o `eval` o executa como tal.

```bash
ssh-agent -s | head -2
```

> ⚠️ **O `eval` executa qualquer coisa.** Se o texto vier do usuário, ele pode
> executar o que quiser na sua conta. Nunca use `eval` com entrada não controlada.
> Teste mentalmente: o que aconteceria se `COMANDO` valesse `rm -rf ~`?

### Ação — depuração

```bash
bash -x ./funcoes.sh
```

Cada linha executada aparece precedida de `+`. Para ligar e desligar dentro do
*script*:

```bash
cat > debug.sh
#!/bin/bash
echo "parte normal"
set -x
X=10
Y=$(( X * 2 ))
set +x
echo "resultado: $Y"
```

Ctrl+D, `chmod +x debug.sh`, e rode.

Três opções que valem a pena conhecer:

| Opção | Efeito |
|---|---|
| `set -x` | mostra cada comando antes de executar |
| `set -e` | encerra o *script* no primeiro comando que falhar |
| `set -u` | trata variável não definida como erro |

```bash
cat > estrito.sh
#!/bin/bash
set -u
echo "[$NAO_EXISTE]"
echo "esta linha não roda"
```

Ctrl+D, `chmod +x estrito.sh`, rode e veja a mensagem.

### ✅ Checkpoint 3

✔ `$CMD` imprime as aspas literalmente; `eval "$CMD"` cria o `saida.txt`.
✔ `bash -x` mostra as linhas com `+`.
✔ `set -u` interrompe o *script* na variável inexistente.

### ❓ Pergunta

O `set -u` teria evitado algum bug que você produziu nas aulas anteriores? Lembre
do `${ARQ}_final.txt` da Aula 07.

---

## 🏁 Entrega da Aula — 1,25 pontos (Nota 2)

Individualmente, nos últimos 25 minutos.

Crie o *script* `~/scripts/aula13/hosts.sh`, que gerencia um mapeamento de nomes de
máquinas e endereços IP.

**Dados:** um arquivo `hosts.db`, com um par `hostname,IP` por linha.

**Obrigatório:** processar as opções com `getopts` em um laço `while`, e criar uma
**função separada** para cada operação.

| Operação | Chamada | Ação |
|---|---|---|
| Adicionar | `./hosts.sh -a <hostname> -i <IP>` | acrescenta o par ao `hosts.db` |
| Remover | `./hosts.sh -d <hostname>` | remove a linha do `hostname` (use `sed`) |
| Listar | `./hosts.sh -l` | exibe todo o conteúdo, alinhado com `printf` |
| Procurar | `./hosts.sh -s <hostname>` | imprime **apenas** o IP correspondente |
| Procurar reversa | `./hosts.sh -r <IP>` | imprime **apenas** o `hostname` |

Exemplo:

```
$ ./hosts.sh -a routerlab -i 192.168.0.1
$ ./hosts.sh -a lab01 -i 192.168.0.100
$ ./hosts.sh -l
routerlab  192.168.0.1
lab01      192.168.0.100
$ ./hosts.sh -d routerlab
$ ./hosts.sh -s lab01
192.168.0.100
$ ./hosts.sh -r 192.168.0.100
lab01
$ ./hosts.sh -x
Opção inválida: -x
```

Requisitos adicionais:

1. Uma opção inválida deve produzir mensagem de erro **no `stderr`** e retorno `1`.
2. Procurar por um `hostname` que não existe deve retornar `1` sem imprimir nada
   no `stdout`.
3. Use um `trap` para garantir que qualquer arquivo temporário criado pela remoção
   seja apagado, mesmo se o *script* for interrompido.

### Critérios de correção

| # | Critério | Valor |
|---|---|---|
| 1 | Usa `getopts` em `while` e uma função por operação | 0,30 |
| 2 | Adicionar e listar funcionam, com saída alinhada | 0,25 |
| 3 | Remover funciona e usa `sed` | 0,20 |
| 4 | As duas buscas imprimem só o campo pedido | 0,25 |
| 5 | Opção inválida vai para o `stderr` e retorna 1 | 0,15 |
| 6 | Há `trap` para limpar temporário | 0,10 |

Correção:

```bash
cd ~/scripts/aula13 && rm -f hosts.db
./hosts.sh -a routerlab -i 192.168.0.1
./hosts.sh -a lab01 -i 192.168.0.100
./hosts.sh -l
./hosts.sh -d routerlab && ./hosts.sh -l
./hosts.sh -s lab01
./hosts.sh -r 192.168.0.100
./hosts.sh -s naoexiste; echo "retorno=$?"
./hosts.sh -x 2>/dev/null; echo "retorno=$?"
grep -c "getopts" hosts.sh
```

---

## ✅ Checklist de Encerramento

| # | Verificação | Comando |
|---|---|---|
| 1 | O *script* é executável | `ls -l ~/scripts/aula13/hosts.sh` |
| 2 | Usa `getopts` | `grep -c getopts hosts.sh` |
| 3 | Tem pelo menos 4 funções | `grep -c "^[a-z_]*() {" hosts.sh` |
| 4 | Tem `trap` | `grep -c trap hosts.sh` |
| 5 | Erros vão para o `stderr` | `./hosts.sh -x 2>/dev/null` não imprime nada |

---

## 💬 Para Discutir em Sala

- Comparado com ler `$1` e `$2`, o `getopts` é bem mais trabalhoso. A partir de
  quantas opções ele começa a compensar?
- O `eval` é chamado de "a função mais perigosa do *shell*". Depois desta aula,
  você consegue justificar o apelido?

## 📌 Para a Próxima Aula

Na **Aula 14** começa o AWK (`slides/13_awk`), a última ferramenta do Bloco 2. Ele
resolve em três linhas o que o `contaPalavras.sh` da Aula 12 levou quinze.
