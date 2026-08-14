# 🧪 Aula 12 — Variáveis e Vetores

**Disciplina:** Programação de *Scripts* — UFC Quixadá
**Material de apoio:** `slides/11_variaveis_e_vetores`
**Sessão:** Semana 7 — terça, 22/09
**Entrega desta aula:** 1,25 pontos (Nota 2)
**Duração estimada:** 100 minutos

---

## 🎯 Objetivos da Aula

Ao final desta aula você deve ser capaz de:

- Explicar o que é um *subshell* e por que variáveis "somem" dentro dele.
- Usar `source` para executar um *script* no *shell* atual.
- Criar, ler e percorrer vetores indexados.
- Usar vetores associativos (dicionários) para contagem.
- Aplicar expansões de `${ }` para valor padrão, tamanho e substituição.

## 🧰 Pré-requisitos

- Aulas 10 e 11. Esta aula usa laços, `read` e funções.

## 🗺️ Roteiro

| Etapa | Assunto | Tempo |
|---|---|---|
| 0 | O *subshell* | 20 min |
| 1 | `source` | 10 min |
| 2 | Vetores indexados | 20 min |
| 3 | Vetores associativos | 20 min |
| 4 | Expansões de `${ }` | 10 min |
| 🏁 | Entrega | 20 min |

---

## 🧩 Etapa 0 — O *subshell*

Na Aula 09 você viu um `while read` perder o valor de uma variável. Agora vamos
entender por quê.

### Ação

```bash
ssh disciplina
mkdir -p ~/scripts/aula12
cd ~/scripts/aula12
```

Um *subshell* é um *shell* filho. Ele **herda** as variáveis do pai, mas o que ele
altera não volta:

```bash
X=10
( X=20; echo "dentro: $X" )
echo "fora: $X"
```

```
dentro: 20
fora: 10
```

Os parênteses criam o *subshell* explicitamente. Mas há vários lugares onde ele
aparece **sem** você pedir:

```bash
# 1. O lado direito de um pipe
total=0
echo -e "a\nb\nc" | while read -r l; do total=$(( total + 1 )); done
echo "com pipe: $total"

# 2. A substituição de comandos
Y=1
Z=$( Y=99; echo "ok" )
echo "depois de \$( ): $Y"

# 3. Um script executado com ./
```

Compare o PID em cada caso:

```bash
echo "shell atual: $$"
( echo "subshell: $$" )
( echo "subshell real: $BASHPID" )
```

> 💡 O `$$` **não** muda em um *subshell* — ele guarda o PID do *shell* original.
> Para ver o PID real do *subshell*, use `$BASHPID`.

A solução para o caso do *pipe* é redirecionar em vez de encanar:

```bash
total=0
while read -r l; do total=$(( total + 1 )); done <<< $'a\nb\nc'
echo "com redirecionamento: $total"
```

### ✅ Checkpoint 0

✔ O bloco entre parênteses imprime `dentro: 20` e `fora: 10`.
✔ A versão com *pipe* imprime `com pipe: 0`.
✔ A versão com `<<<` imprime `com redirecionamento: 3`.

### ❓ Pergunta

Se o *subshell* herda as variáveis mas não devolve as alterações, como um *script*
consegue passar um resultado de volta para quem o chamou?

---

## 🧩 Etapa 1 — `source`

### Ação

```bash
cat > config.sh
#!/bin/bash
PROJETO="Programação de Scripts"
AUTOR="$USER"
echo "Configuração carregada."
```

Ctrl+D, e:

```bash
chmod +x config.sh

./config.sh
echo "[$PROJETO]"        # vazio: rodou em um processo separado

source config.sh
echo "[$PROJETO]"        # agora tem valor
```

O `.` é sinônimo de `source`:

```bash
unset PROJETO
. config.sh
echo "[$PROJETO]"
```

É exatamente assim que funciona o `~/.bashrc`: o *shell* dá `source` nele ao
iniciar, e por isso os `alias` e variáveis definidos lá valem na sua sessão.

```bash
grep -c . ~/.bashrc
```

> ⚠️ Um *script* executado com `source` roda **no seu *shell***. Um `exit` dentro
> dele fecha o seu terminal. Teste com cuidado.

### ✅ Checkpoint 1

✔ Depois de `./config.sh`, a variável `PROJETO` está vazia.
✔ Depois de `source config.sh`, ela tem valor.

### ❓ Pergunta

Quando você instala uma ferramenta e ela pede para rodar `source ~/.bashrc`, por
que não bastaria executar `./.bashrc`?

---

## 🧩 Etapa 2 — Vetores indexados

### Ação

```bash
FRUTAS=(maçã banana laranja)

echo "${FRUTAS[0]}"          # primeiro elemento
echo "${FRUTAS[2]}"          # terceiro
echo "${FRUTAS[@]}"          # todos
echo "${#FRUTAS[@]}"         # quantidade
echo "${!FRUTAS[@]}"         # os índices
```

> ⚠️ As chaves são **obrigatórias** em vetores. `$FRUTAS[0]` não funciona — o
> *shell* entende como a variável `$FRUTAS` seguida do texto `[0]`.

Adicionando e alterando:

```bash
FRUTAS+=(uva)
echo "${FRUTAS[@]}"

FRUTAS[1]="banana prata"
echo "${FRUTAS[1]}"
echo "${#FRUTAS[@]}"
```

Percorrendo — e a diferença que as aspas fazem:

```bash
for f in "${FRUTAS[@]}"; do echo "[$f]"; done     # correto
for f in ${FRUTAS[@]};   do echo "[$f]"; done     # quebra "banana prata"
```

Preenchendo a partir de um comando:

```bash
mapfile -t USUARIOS < <(cut -d: -f1 /etc/passwd | head -5)
echo "${#USUARIOS[@]}"
echo "${USUARIOS[0]}"
for u in "${USUARIOS[@]}"; do echo "- $u"; done
```

E a partir do `read`:

```bash
read -ra PALAVRAS <<< "um dois tres quatro"
echo "${#PALAVRAS[@]}"
echo "${PALAVRAS[3]}"
```

### ✅ Checkpoint 2

✔ `${#FRUTAS[@]}` responde `4` depois do `+=`.
✔ Com aspas, `banana prata` sai em uma linha; sem aspas, em duas.
✔ `mapfile` preencheu o vetor com 5 usuários.

### ❓ Pergunta

`${FRUTAS[@]}` e `${#FRUTAS[@]}` diferem por um `#`, e `${!FRUTAS[@]}` por um `!`.
Qual a lógica por trás desses símbolos? (Dica: você já viu `${#VAR}` na Aula 11.)

---

## 🧩 Etapa 3 — Vetores associativos

Um vetor associativo usa **texto** como índice, não número. É a estrutura certa
para contar coisas.

### Ação

A declaração com `-A` é **obrigatória**:

```bash
declare -A IDADE
IDADE[ana]=25
IDADE[bruno]=31
IDADE[carla]=28

echo "${IDADE[ana]}"
echo "${!IDADE[@]}"          # as chaves
echo "${IDADE[@]}"           # os valores
echo "${#IDADE[@]}"          # quantos pares
```

Percorrendo:

```bash
for nome in "${!IDADE[@]}"; do
    printf "%-10s %3d\n" "$nome" "${IDADE[$nome]}"
done
```

> ⚠️ Sem o `declare -A`, o *bash* trata os índices como aritmética e todos os
> nomes viram `0`. Teste: rode sem declarar e veja o resultado.

O uso clássico é contar ocorrências:

```bash
cat > conta.sh
#!/bin/bash
declare -A CONTAGEM
for palavra in a casa que vivo é boa boa casa é; do
    CONTAGEM[$palavra]=$(( ${CONTAGEM[$palavra]:-0} + 1 ))
done
for p in "${!CONTAGEM[@]}"; do
    printf "%-6s %d\n" "$p" "${CONTAGEM[$p]}"
done
```

Ctrl+D, e:

```bash
chmod +x conta.sh
./conta.sh
./conta.sh | sort -k2 -rn
```

Repare no `${CONTAGEM[$palavra]:-0}`: se a chave ainda não existe, o valor `0` é
usado. Sem isso, a primeira soma daria erro.

### ✅ Checkpoint 3

✔ `${#IDADE[@]}` responde `3`.
✔ `./conta.sh | sort -k2 -rn` mostra `casa 2`, `boa 2`, `é 2` no topo.
✔ Você testou o que acontece sem o `declare -A`.

### ❓ Pergunta

Na Aula 06 você contou ocorrências com `sort | uniq -c`, sem nenhum vetor. Quando
o vetor associativo compensa o trabalho extra?

---

## 🧩 Etapa 4 — Expansões de `${ }`

### Ação

Valor padrão e obrigatoriedade:

```bash
unset NOME
echo "[${NOME:-visitante}]"      # usa o padrão, mas não atribui
echo "[$NOME]"

echo "[${NOME:=visitante}]"      # usa o padrão E atribui
echo "[$NOME]"

unset OBRIGATORIA
echo "${OBRIGATORIA:?variável não definida}"
```

Tamanho e fatiamento:

```bash
TEXTO="Programação de Scripts"
echo "${#TEXTO}"                 # tamanho
echo "${TEXTO:0:11}"             # a partir do 0, 11 caracteres
echo "${TEXTO: -7}"              # os 7 últimos (repare no espaço)
```

Remoção de prefixo e sufixo:

```bash
ARQ="/home/aluno/relatorio.tar.gz"
echo "${ARQ##*/}"                # só o nome: relatorio.tar.gz
echo "${ARQ%/*}"                 # só o diretório: /home/aluno
echo "${ARQ%.gz}"                # tira o .gz
echo "${ARQ%%.*}"                # tira tudo a partir do primeiro ponto
```

| Operador | Remove |
|---|---|
| `#` | menor prefixo que casa |
| `##` | maior prefixo |
| `%` | menor sufixo |
| `%%` | maior sufixo |

Substituição:

```bash
FRASE="um dois um dois"
echo "${FRASE/um/UM}"            # a primeira ocorrência
echo "${FRASE//um/UM}"           # todas
```

### ✅ Checkpoint 4

✔ `${ARQ##*/}` responde `relatorio.tar.gz`.
✔ `${ARQ%%.*}` responde `/home/aluno/relatorio`.
✔ `${FRASE//um/UM}` troca as duas ocorrências.

### ❓ Pergunta

`${ARQ##*/}` faz o mesmo que `basename "$ARQ"`, e `${ARQ%/*}` o mesmo que
`dirname "$ARQ"`. Por que preferir a expansão?

---

## 🏁 Entrega da Aula — 1,25 pontos (Nota 2)

Individualmente, nos últimos 20 minutos. São **duas** questões.

### A) `~/scripts/aula12/contaPalavras.sh` — 0,75 ponto

Pergunta ao usuário o nome de um arquivo de texto e, para cada palavra do arquivo,
diz quantas vezes ela aparece — da mais frequente para a menos frequente.

**Restrição:** é obrigatório usar um **vetor associativo**. Não pode usar `awk`,
nem resolver tudo com `sort | uniq -c`.

```
$ cat arquivo.txt
a casa que vivo é boa.
boa casa é.
$ ./contaPalavras.sh
Informe o arquivo: arquivo.txt
casa: 2
boa:  2
é:    2
a:    1
que:  1
vivo: 1
```

Requisitos:

1. O nome do arquivo vem do `read`, não de parâmetro.
2. Se o arquivo não existir, imprima `Arquivo não encontrado.` e retorne `1`.
3. A pontuação (`.` e `,`) não deve contar como parte da palavra.
4. A saída deve estar alinhada, usando `printf`.

### B) `~/scripts/aula12/contadorVetor.sh` — 0,50 ponto

1. Lê números do usuário, **um por vez**, sem usar parâmetros.
2. Cada número é armazenado em um **vetor indexado**.
3. Quando o usuário digitar `q`, o *script* informa quantos números foram inseridos,
   qual o **maior** e qual o **menor**, e encerra.

```
$ ./contadorVetor.sh
Número (q para sair): 10
Número (q para sair): 3
Número (q para sair): 47
Número (q para sair): q
Foram inseridos 3 números.
Maior: 47
Menor: 3
```

### Critérios de correção

| # | Critério | Valor |
|---|---|---|
| 1 | `contaPalavras.sh` usa `declare -A` e conta certo | 0,35 |
| 2 | Trata arquivo inexistente com retorno 1 | 0,10 |
| 3 | Remove pontuação e alinha a saída com `printf` | 0,30 |
| 4 | `contadorVetor.sh` usa vetor indexado e conta certo | 0,30 |
| 5 | Informa maior e menor corretamente | 0,20 |

Correção:

```bash
cd ~/scripts/aula12
printf 'a casa que vivo é boa.\nboa casa é.\n' > arquivo.txt
echo arquivo.txt | ./contaPalavras.sh
echo naoexiste | ./contaPalavras.sh; echo "retorno=$?"
printf '10\n3\n47\nq\n' | ./contadorVetor.sh
grep -c "declare -A" contaPalavras.sh
```

> 💡 Para separar as palavras de uma linha, lembre do `tr`: ele troca e apaga
> caracteres, e aceita `-s` para colapsar repetições.

---

## ✅ Checklist de Encerramento

| # | Verificação | Comando |
|---|---|---|
| 1 | Os dois *scripts* são executáveis | `ls -l ~/scripts/aula12/*.sh` |
| 2 | O contador de palavras usa vetor associativo | `grep -c "declare -A" contaPalavras.sh` |
| 3 | Nenhum usa `awk` | `grep -c awk *.sh` |
| 4 | Ambos funcionam via *pipe* na entrada | veja os comandos de correção |

---

## 💬 Para Discutir em Sala

- O `sort | uniq -c` da Aula 06 resolve a contagem em uma linha. Seu
  `contaPalavras.sh` tem umas quinze. O que você ganhou em troca?
- O *subshell* é a causa de bugs que "não fazem sentido": o código está certo, mas
  a variável está vazia. Que regra prática evita cair nisso?

## 📌 Para a Próxima Aula

Na **Aula 13** vamos à miscelânea (`slides/12_miscelanea`): funções com retorno,
`getopts` para tratar opções de linha de comando, `trap` para capturar sinais e
`eval` — aquele da Aula 01, finalmente explicado.
