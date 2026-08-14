# 🧪 Aula 14 — AWK (parte 1): Padrões e Campos

**Disciplina:** Programação de *Scripts* — UFC Quixadá
**Material de apoio:** `slides/13_awk`
**Sessão:** Semana 8 — terça, 29/09
**Entrega desta aula:** 1,25 pontos (Nota 2)
**Duração estimada:** 100 minutos

---

## 🎯 Objetivos da Aula

Ao final desta aula você deve ser capaz de:

- Explicar o modelo `padrão { ação }` do AWK.
- Acessar campos com `$1`, `$2`, `$NF` e alterar o separador com `FS`.
- Usar as variáveis internas `NR`, `NF` e `FILENAME`.
- Filtrar linhas com expressões relacionais e regulares.
- Usar os blocos `BEGIN` e `END`.

## 🧰 Pré-requisitos

- Bloco 2 até a Aula 13. Expressões regulares da Aula 04.

## 🗺️ Roteiro

| Etapa | Assunto | Tempo |
|---|---|---|
| 0 | O modelo do AWK | 15 min |
| 1 | Campos e separadores | 20 min |
| 2 | Variáveis internas | 15 min |
| 3 | Padrões: relacionais e regulares | 20 min |
| 4 | `BEGIN` e `END` | 10 min |
| 🏁 | Entrega | 20 min |

---

## 🧩 Etapa 0 — O modelo do AWK

O AWK lê a entrada **linha a linha**. Para cada linha, testa um padrão; se casar,
executa a ação.

```
padrão { ação }
```

- Sem padrão → a ação roda para **toda** linha.
- Sem ação → a linha é **impressa**.

### Ação

```bash
ssh disciplina
mkdir -p ~/scripts/aula14
cd ~/scripts/aula14
cp /etc/passwd dados.txt
```

Compare as três formas:

```bash
awk '{ print }' dados.txt | head -3          # ação sem padrão
awk '/root/' dados.txt                       # padrão sem ação
awk '/root/ { print "achei:", $0 }' dados.txt
```

O `$0` é a **linha inteira**.

> ⚠️ Use sempre **aspas simples** em volta do programa AWK. Com aspas duplas, o
> *shell* expandiria `$1` como parâmetro do *script* antes de o AWK vê-lo. Teste:
>
> ```bash
> awk "{ print \$1 }" dados.txt | head -2    # funciona, mas exige escapar tudo
> awk '{ print $1 }' dados.txt | head -2     # limpo
> ```

### ✅ Checkpoint 0

✔ `awk '{ print }'` imprime o arquivo inteiro.
✔ `awk '/root/'` imprime só as linhas com `root`.
✔ Você entendeu que `$0` é a linha completa.

### ❓ Pergunta

`awk '/root/' arquivo` e `grep root arquivo` fazem a mesma coisa. Qual é a
vantagem do AWK, então?

---

## 🧩 Etapa 1 — Campos e separadores

### Ação

O AWK quebra cada linha em **campos**, acessíveis por `$1`, `$2`, e assim por diante.
O padrão é separar por espaços em branco:

```bash
echo "João Marcelo Alencar" | awk '{ print $2 }'
echo "João Marcelo Alencar" | awk '{ print $3, $1 }'
```

A vírgula no `print` insere um espaço. Sem ela, os campos ficam colados:

```bash
echo "a b c" | awk '{ print $1, $2 }'      # a b
echo "a b c" | awk '{ print $1 $2 }'       # ab
```

O `/etc/passwd` usa `:` como separador. Há três formas de informar isso:

```bash
awk -F: '{ print $1 }' dados.txt | head -3
awk -F':' '{ print $1 }' dados.txt | head -3
awk 'BEGIN { FS=":" } { print $1 }' dados.txt | head -3
```

O `$NF` é o **último** campo, sem você precisar saber quantos são:

```bash
awk -F: '{ print $NF }' dados.txt | head -3       # o shell de cada usuário
awk -F: '{ print $(NF-1) }' dados.txt | head -3   # o penúltimo
```

Campos podem ser **alterados**:

```bash
awk -F: 'BEGIN { OFS=" | " } { $1 = toupper($1); print $1, $NF }' dados.txt | head -3
```

O `OFS` é o separador de **saída**.

### ✅ Checkpoint 1

✔ `awk -F: '{ print $1 }'` lista os nomes de usuário.
✔ `awk -F: '{ print $NF }'` lista os *shells*.
✔ A versão com `OFS=" | "` sai com o separador escolhido.

### ❓ Pergunta

Na Aula 06 você fez `cut -d: -f1 /etc/passwd`. O AWK faz o mesmo com
`awk -F: '{print $1}'`. Além do `$NF`, que outra coisa o AWK faz que o `cut` não faz?

---

## 🧩 Etapa 2 — Variáveis internas

| Variável | Conteúdo |
|---|---|
| `NR` | número do registro (linha) atual, acumulado |
| `NF` | número de campos da linha atual |
| `FNR` | número da linha **dentro do arquivo atual** |
| `FILENAME` | nome do arquivo sendo lido |
| `FS` / `OFS` | separador de entrada / de saída |

### Ação

```bash
awk '{ print NR, $0 }' dados.txt | head -3        # numera as linhas
awk -F: '{ print NR, NF, $1 }' dados.txt | head -3
awk 'END { print NR }' dados.txt                  # conta linhas, como wc -l
```

O `NR` também permite selecionar faixas:

```bash
awk 'NR == 1' dados.txt
awk 'NR >= 3 && NR <= 5' dados.txt
awk 'NR % 2 == 0' dados.txt | head -3             # só as linhas pares
```

A diferença entre `NR` e `FNR` aparece com vários arquivos:

```bash
head -3 dados.txt > a.txt
head -2 dados.txt > b.txt
awk '{ print FILENAME, FNR, NR }' a.txt b.txt
```

### ✅ Checkpoint 2

✔ `awk 'END { print NR }' dados.txt` responde o mesmo que `wc -l < dados.txt`.
✔ No teste com dois arquivos, o `FNR` reinicia e o `NR` continua.

### ❓ Pergunta

`awk 'END { print NR }'` e `wc -l` deram o mesmo número. Se o arquivo **não**
terminar com quebra de linha, eles ainda concordam? Teste com
`printf 'a\nb' > sem_quebra.txt`.

---

## 🧩 Etapa 3 — Padrões: relacionais e regulares

### Ação — expressões relacionais

```bash
awk -F: '$3 >= 1000' dados.txt                    # UID a partir de 1000
awk -F: '$3 >= 1000 { print $1, $3 }' dados.txt
awk -F: 'NF != 7' dados.txt                       # linhas malformadas
awk -F: '$7 == "/bin/bash" { print $1 }' dados.txt
```

Operadores disponíveis: `==`, `!=`, `<`, `<=`, `>`, `>=`, e os lógicos `&&`, `||`, `!`.

> ⚠️ O AWK decide sozinho se compara como número ou como texto. `$3 >= 1000`
> compara números; `$7 == "/bin/bash"` compara texto. Se der resultado estranho,
> force com `$3+0` (número) ou `$3""` (texto).

### Ação — expressões regulares

```bash
awk '/bash/' dados.txt                            # a regex vale para a linha toda
awk -F: '$1 ~ /^r/' dados.txt                     # só o campo 1 começa com r
awk -F: '$1 !~ /^r/ { print $1 }' dados.txt | head -3
awk -F: '$7 ~ /(bash|sh)$/ { print $1, $7 }' dados.txt | head -5
```

O `~` significa "casa com" e o `!~`, "não casa com". As expressões regulares são as
**estendidas** — as mesmas do `grep -E` da Aula 04, sem precisar de contrabarra.

Combinando os dois tipos de padrão:

```bash
awk -F: '$3 >= 1000 && $7 ~ /bash$/ { print $1 }' dados.txt
```

Faixas de linhas delimitadas por padrão:

```bash
awk '/^root/,/^daemon/' dados.txt
```

### ✅ Checkpoint 3

✔ `awk -F: '$3 >= 1000'` traz menos linhas que o arquivo inteiro.
✔ `$1 ~ /^r/` e `$1 !~ /^r/` são complementares — as contagens somam o total.
✔ Você usou `&&` combinando um teste numérico e uma regex.

### ❓ Pergunta

Qual a diferença entre `awk '/bash/'` e `awk -F: '$7 ~ /bash/'`? Rode os dois e
compare as contagens.

---

## 🧩 Etapa 4 — `BEGIN` e `END`

O `BEGIN` roda **antes** da primeira linha; o `END`, **depois** da última.

### Ação

```bash
awk -F: 'BEGIN { print "USUÁRIO" } { print $1 }' dados.txt | head -4

awk -F: '
BEGIN { print "=== Usuários com UID >= 1000 ===" }
$3 >= 1000 { print $1; total++ }
END { print "Total:", total }
' dados.txt
```

Repare que `total` não foi declarado nem inicializado — no AWK, uma variável não
inicializada vale `0` em contexto numérico e `""` em contexto de texto.

O `BEGIN` é o lugar de configurar separadores e cabeçalhos:

```bash
awk '
BEGIN { FS=":"; OFS=" | "; print "LOGIN", "SHELL" }
$3 >= 1000 { print $1, $7 }
' dados.txt
```

Um programa AWK pode ficar em **arquivo**, o que é bem mais legível:

```bash
cat > relatorio.awk
BEGIN {
    FS = ":"
    print "=== Relatório de usuários ==="
}

$3 >= 1000 {
    print $1, "(UID " $3 ")"
    normais++
}

$3 < 1000 {
    sistema++
}

END {
    print "---"
    print "Usuários normais:", normais
    print "Usuários de sistema:", sistema
    print "Total de linhas:", NR
}
```

Ctrl+D, e execute com `-f`:

```bash
awk -f relatorio.awk dados.txt
```

### ✅ Checkpoint 4

✔ `awk -f relatorio.awk dados.txt` imprime o cabeçalho, a lista e o resumo.
✔ A soma de `normais` e `sistema` é igual ao `NR`.

### ❓ Pergunta

O `BEGIN` roda antes de qualquer linha ser lida. O que acontece se você tentar usar
`$1` dentro dele?

---

## 🏁 Entrega da Aula — 1,25 pontos (Nota 2)

Individualmente, nos últimos 20 minutos.

Crie o arquivo `~/scripts/aula14/emails.txt`:

```
Ana Souza:ana.souza@alu.ufc.br:2021
Bruno Lima:brunolima@gmail.com:2020
Carla Dias:carla.dias@alu.ufc.br:2022
Diego Rocha:diego.rocha@gmail.com:2021
Elisa Prado:elisa@alu.ufc.br:2023
Fabio Nunes:fabionunes@gmail.com:2022
Gabriel Reis:gabriel.reis@alu.ufc.br:2020
```

Escreva **quatro** programas AWK, cada um em seu próprio arquivo `.awk`, executados
com `awk -f`. Todos devem definir o separador no `BEGIN`, não na linha de comando.

### A) `questao01.awk`

Imprime o **nome** dos alunos com *e-mail* no domínio `@alu.ufc.br`.

### B) `questao02.awk`

Imprime **apenas a quantidade** de alunos com *e-mail* `@gmail.com`.

```
3
```

### C) `questao03.awk`

Imprime todos os *e-mails*, mas se o domínio **não** for `@alu.ufc.br`, ele deve ser
substituído por esse. Exemplo: `brunolima@gmail.com` vira `brunolima@alu.ufc.br`.

### D) `questao04.awk`

Imprime um relatório com a quantidade de alunos por **ano de ingresso** (o campo 3),
com cabeçalho no `BEGIN` e total no `END`:

```
=== Alunos por ano ===
2020: 2
2021: 2
2022: 2
2023: 1
---
Total: 7
```

> 💡 Para o item D você vai precisar acumular contagens por chave. O AWK tem vetores
> associativos nativos — `contagem[$3]++` já funciona. Percorra no `END` com
> `for (k in contagem)`. A ordenação você resolve com um *pipe* para `sort`.

### Critérios de correção

| # | Critério | Valor |
|---|---|---|
| 1 | `questao01.awk` filtra pelo domínio e imprime só o nome | 0,25 |
| 2 | `questao02.awk` imprime só o número, usando `END` | 0,25 |
| 3 | `questao03.awk` substitui o domínio corretamente | 0,35 |
| 4 | `questao04.awk` agrupa por ano com `BEGIN` e `END` | 0,30 |
| 5 | Todos definem `FS` no `BEGIN` | 0,10 |

Correção:

```bash
cd ~/scripts/aula14
for q in questao01 questao02 questao03 questao04; do
    echo "--- $q"; awk -f $q.awk emails.txt
done
grep -L "FS" *.awk
```

O último comando não deve listar nenhum arquivo.

---

## ✅ Checklist de Encerramento

| # | Verificação | Comando |
|---|---|---|
| 1 | Os quatro `.awk` existem | `ls ~/scripts/aula14/questao*.awk` |
| 2 | Todos definem `FS` no `BEGIN` | `grep -c "FS" questao*.awk` |
| 3 | O item B imprime um número só | `awk -f questao02.awk emails.txt \| wc -l` |
| 4 | Nenhum usa `-F` na linha de comando | conferido na correção |

O item 3 deve responder `1`.

---

## 💬 Para Discutir em Sala

- O item C substitui o domínio. Dá para fazer isso com `sed`. Qual das duas soluções
  fica mais legível?
- O AWK inicializa variáveis sozinho, com `0` ou `""`. Isso é conveniente ou
  perigoso? Compare com o `set -u` da Aula 13.

## 📌 Para a Próxima Aula

A **Aula 15** completa o AWK: laços, funções, `printf` e redirecionamento da saída
para comandos externos. É onde ele deixa de ser "um `grep` melhor" e vira linguagem.
