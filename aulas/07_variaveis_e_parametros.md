# 🧪 Aula 07 — Variáveis e Parâmetros

**Disciplina:** Programação de *Scripts* — UFC Quixadá
**Material de apoio:** `slides/06_variaveis_e_parametros`
**Sessão:** Semana 4 — terça, 01/09
**Entrega desta aula:** 1,0 ponto (Nota 1)
**Duração estimada:** 100 minutos

---

## 🎯 Objetivos da Aula

Ao final desta aula você deve ser capaz de:

- Criar e usar variáveis, e explicar por que não pode haver espaço no `=`.
- Distinguir aspas simples, aspas duplas e ausência de aspas.
- Ler os parâmetros passados a um *script* com `$1`, `$2`, `$@` e `$#`.
- Usar `$0`, `$?` e variáveis de ambiente.
- Alimentar comandos com `xargs`.

## 🧰 Pré-requisitos

- Aulas 01 a 06 concluídas.

## 🗺️ Roteiro

| Etapa | Assunto | Tempo |
|---|---|---|
| 0 | Variáveis | 15 min |
| 1 | Aspas: o assunto que mais gera bug | 20 min |
| 2 | Parâmetros de linha de comando | 20 min |
| 3 | Variáveis especiais e de ambiente | 15 min |
| 4 | `xargs` | 10 min |
| 🏁 | Entrega | 20 min |

---

## 🧩 Etapa 0 — Variáveis

### Ação

```bash
ssh disciplina
mkdir -p ~/scripts/aula07
cd ~/scripts/aula07

NOME=João
echo $NOME
echo "Olá, $NOME"
echo "Olá, ${NOME}!"
```

Agora erre de propósito:

```bash
NOME = João
```

```
NOME: comando não encontrado
```

**Não pode haver espaço em volta do `=`.** Com espaços, o *shell* entende `NOME`
como um comando e `=` e `João` como argumentos dele.

Outro erro clássico:

```bash
NOME=João Marcelo
```

```
Marcelo: comando não encontrado
```

O espaço separa argumentos. Para valores com espaço, use aspas:

```bash
NOME="João Marcelo"
echo $NOME
```

As chaves em `${NOME}` são necessárias quando o nome da variável gruda em outro texto:

```bash
ARQ=relatorio
echo "$ARQ_final.txt"      # procura a variável ARQ_final, que não existe
echo "${ARQ}_final.txt"    # correto
```

### ✅ Checkpoint 0

✔ `echo "Olá, $NOME"` imprime `Olá, João Marcelo`.
✔ `echo "${ARQ}_final.txt"` imprime `relatorio_final.txt`.
✔ Você viu as duas mensagens de erro acima com seus próprios olhos.

### ❓ Pergunta

`echo "$ARQ_final.txt"` não deu erro — imprimiu apenas `.txt`. Por que uma variável
inexistente não gera erro no *shell*?

---

## 🧩 Etapa 1 — Aspas

Três formas de escrever um texto, três comportamentos diferentes.

### Ação

```bash
NOME="João Marcelo"

echo $NOME          # sem aspas
echo "$NOME"        # aspas duplas: expande variáveis
echo '$NOME'        # aspas simples: NÃO expande nada
```

A diferença entre as duas primeiras aparece quando há espaços múltiplos:

```bash
TEXTO="a     b"
echo $TEXTO         # a b
echo "$TEXTO"       # a     b
```

Sem aspas, o *shell* quebra o valor em palavras e o `echo` as reimprime separadas
por um espaço só.

O caso perigoso é com nomes de arquivo:

```bash
touch "arquivo com espaco.txt"
ARQUIVO="arquivo com espaco.txt"

ls $ARQUIVO         # erro: procura três arquivos
ls "$ARQUIVO"       # correto
```

E a substituição de comandos também respeita as aspas:

```bash
echo "Hoje: $(date)"
echo 'Hoje: $(date)'
```

> 💡 **Regra prática:** use aspas duplas em volta de **toda** expansão de variável,
> sempre. `"$VAR"`, nunca `$VAR`. As exceções são raras e você vai reconhecê-las
> quando aparecerem.

### ✅ Checkpoint 1

✔ `echo '$NOME'` imprime literalmente `$NOME`.
✔ `ls $ARQUIVO` falha e `ls "$ARQUIVO"` funciona.

### ❓ Pergunta

Se aspas duplas resolvem quase tudo, para que servem as aspas simples? Dê um
exemplo onde elas são obrigatórias. (Dica: lembre dos padrões da Aula 04.)

---

## 🧩 Etapa 2 — Parâmetros de linha de comando

### Ação

Crie o *script* `params.sh`:

```bash
cat > params.sh
#!/bin/bash
echo "Nome do script: $0"
echo "Primeiro parâmetro: $1"
echo "Segundo parâmetro: $2"
echo "Quantidade de parâmetros: $#"
echo "Todos: $@"
```

Ctrl+D, e então:

```bash
chmod +x params.sh
./params.sh
./params.sh um
./params.sh um dois tres
```

Repare no que acontece quando faltam parâmetros: `$1` e `$2` ficam vazios, sem
erro nenhum. O *script* continua rodando.

Agora teste com aspas:

```bash
./params.sh "João Marcelo" ufc
./params.sh João Marcelo ufc
```

No primeiro, `$1` é `João Marcelo`. No segundo, `$1` é `João` e `$2` é `Marcelo`.

### Ação — `$@` e `$*`

```bash
cat > lista.sh
#!/bin/bash
echo "--- com \$@"
for p in "$@"; do echo "[$p]"; done
echo "--- com \$*"
for p in "$*"; do echo "[$p]"; done
```

Ctrl+D, e:

```bash
chmod +x lista.sh
./lista.sh "João Marcelo" ufc quixada
```

O `"$@"` preserva cada parâmetro; o `"$*"` junta tudo em uma string só.

> 💡 O laço `for` só aparece formalmente na Aula 09. Aqui ele serve apenas para
> mostrar a diferença — não precisa entender a sintaxe ainda.

### ✅ Checkpoint 2

✔ `./params.sh um dois tres` imprime `Quantidade de parâmetros: 3`.
✔ `./params.sh` sem argumentos imprime `Quantidade de parâmetros: 0` e não dá erro.
✔ `./lista.sh "João Marcelo" ufc` mostra `[João Marcelo]` com `$@` e tudo junto com `$*`.

### ❓ Pergunta

Um *script* que espera dois parâmetros foi chamado sem nenhum. Ele não deu erro e
seguiu executando com variáveis vazias. Isso é um recurso ou um problema? Como
você trataria isso? (Guarde a resposta para a Aula 08.)

---

## 🧩 Etapa 3 — Variáveis especiais e de ambiente

### Ação — o código de retorno

Todo comando devolve um número ao terminar: `0` significa sucesso, qualquer outro
significa erro. Ele fica em `$?`:

```bash
ls /etc > /dev/null
echo $?

ls /naoexiste 2> /dev/null
echo $?

grep "root" /etc/passwd > /dev/null
echo $?

grep "naoexisteusuario" /etc/passwd > /dev/null
echo $?
```

> ⚠️ O `$?` guarda o retorno do **último** comando executado. Se você rodar
> qualquer outra coisa no meio — inclusive um `echo` —, o valor é sobrescrito.

### Ação — variáveis de ambiente

```bash
echo $HOME
echo $USER
echo $PWD
echo $PATH
env | head -10
```

A diferença entre uma variável comum e uma de ambiente é a exportação:

```bash
MINHA=valor
bash -c 'echo "[$MINHA]"'       # vazio: o subprocesso não enxerga

export MINHA=valor
bash -c 'echo "[$MINHA]"'       # agora enxerga
```

### ✅ Checkpoint 3

✔ `$?` responde `0` depois de um comando que deu certo e diferente de `0` depois
de um que falhou.
✔ Sem `export`, o `bash -c` imprime `[]`; com `export`, imprime `[valor]`.

### ❓ Pergunta

O `PATH` é uma lista de diretórios separados por `:`. Rode `echo $PATH | tr ':' '\n'`.
Agora explique por que, na Aula 01, foi preciso escrever `./usuarios.sh` em vez de
só `usuarios.sh`.

---

## 🧩 Etapa 4 — `xargs`

Alguns comandos não leem da entrada padrão — eles só aceitam argumentos. O `xargs`
faz a ponte: lê o fluxo e o transforma em argumentos.

### Ação

```bash
echo "/etc/passwd /etc/hostname" | wc -l        # conta 1: contou a própria linha
echo "/etc/passwd /etc/hostname" | xargs wc -l  # conta os dois arquivos
```

Combinando com o `find`:

```bash
cd ~/scripts
find . -name "*.sh" | xargs wc -l
find . -name "*.sh" | xargs grep -l "bash"
```

Controlando quantos argumentos por chamada:

```bash
echo "a b c d" | xargs -n 1 echo "Item:"
```

> ⚠️ Nomes de arquivo com espaço quebram o `xargs`. A solução é combinar
> `find -print0` com `xargs -0`:
>
> ```bash
> find . -name "*.txt" -print0 | xargs -0 wc -l
> ```

### ✅ Checkpoint 4

✔ `echo "/etc/passwd" | wc -l` responde `1`, mas com `xargs` responde o número de
linhas do arquivo.
✔ `echo "a b c d" | xargs -n 1 echo "Item:"` imprime quatro linhas.

### ❓ Pergunta

Qual a diferença entre `find . -name "*.sh" | xargs grep "bash"` e
`grep -r "bash" .`? Os dois resolvem o mesmo problema?

---

## 🏁 Entrega da Aula — 1,0 ponto (Nota 1)

Individualmente, nos últimos 20 minutos.

Crie o *script* `~/scripts/aula07/saudacao.sh` que:

1. Receba **um** parâmetro: o nome de uma pessoa.
2. Imprima na tela exatamente:

   ```
   Olá <nome>,
   Hoje é dia <dia>, do mês <mês> do ano de <ano>.
   Você é o usuário <usuário do sistema> na máquina <hostname>.
   ```

3. Funcione com nomes que tenham espaço: `./saudacao.sh "João Marcelo"` deve
   imprimir `Olá João Marcelo,` em uma linha só.
4. Se **nenhum** parâmetro for passado, use o nome do usuário do sistema no lugar.
5. Além de imprimir na tela, **acrescente** a saudação ao arquivo `saudacao.log`,
   sem apagar as saudações anteriores.

Exemplo:

```
$ ./saudacao.sh "João Marcelo"
Olá João Marcelo,
Hoje é dia 01, do mês 09 do ano de 2026.
Você é o usuário aluno na máquina servidor.
$ ./saudacao.sh
Olá aluno,
...
$ wc -l saudacao.log
6 saudacao.log
```

### Critérios de correção

| # | Critério | Valor |
|---|---|---|
| 1 | Usa `$1` e imprime as três linhas no formato pedido | 0,3 |
| 2 | A data vem do `date`, com dia, mês e ano separados | 0,2 |
| 3 | Funciona com nome entre aspas, sem quebrar em duas linhas | 0,2 |
| 4 | Sem parâmetro, cai no usuário do sistema | 0,15 |
| 5 | O `saudacao.log` acumula em vez de sobrescrever | 0,15 |

Correção:

```bash
cd ~/scripts/aula07 && rm -f saudacao.log && ./saudacao.sh "Maria Silva" && ./saudacao.sh && wc -l saudacao.log
```

> 💡 Para o item 4 você ainda não tem `if`. Existe uma expansão do *shell* que
> resolve em uma linha: `${1:-valor_padrão}`. Investigue.

---

## ✅ Checklist de Encerramento

| # | Verificação | Comando |
|---|---|---|
| 1 | O *script* é executável e tem *shebang* | `ls -l saudacao.sh && head -1 saudacao.sh` |
| 2 | Funciona com nome composto | `./saudacao.sh "Ana Paula"` |
| 3 | Funciona sem parâmetro | `./saudacao.sh` |
| 4 | O *log* acumulou | `wc -l saudacao.log` |

---

## 💬 Para Discutir em Sala

- A regra "sempre use `"$VAR"`" parece exagerada. Quantos bugs dela você já
  produziu só nesta aula?
- O *shell* não avisa quando uma variável não existe — ele a trata como vazia.
  Compare com uma linguagem compilada. Qual abordagem você prefere, e por quê?

## 📌 Para a Próxima Aula

Na **Aula 08** vamos aprender a **decidir**: `if`, `test`, `case` e os operadores
`&&` e `||` (`slides/07_condicionais`). Aí sim o `saudacao.sh` vai poder verificar
se recebeu parâmetro em vez de torcer para que sim.
