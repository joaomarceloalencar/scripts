# 🧪 Aula 15 — AWK (parte 2): Laços, Vetores e Formatação

**Disciplina:** Programação de *Scripts* — UFC Quixadá
**Material de apoio:** `slides/13_awk`
**Sessão:** Semana 8 — quarta, 30/09
**Entrega desta aula:** 1,25 pontos (Nota 2)
**Duração estimada:** 100 minutos

---

## 🎯 Objetivos da Aula

Ao final desta aula você deve ser capaz de:

- Usar `if`, `while` e `for` dentro de um programa AWK.
- Acumular dados em vetores associativos e percorrê-los no `END`.
- Formatar saída com `printf` e funções de texto.
- Redirecionar a saída do AWK para arquivos e para comandos externos.
- Passar valores do *shell* para o AWK com `-v`.

## 🧰 Pré-requisitos

- Aula 14 concluída: campos, `NR`, `NF`, `BEGIN` e `END`.

## 🗺️ Roteiro

| Etapa | Assunto | Tempo |
|---|---|---|
| 0 | Operadores e funções | 15 min |
| 1 | `if`, `while` e `for` | 20 min |
| 2 | Vetores | 20 min |
| 3 | `printf` e funções de texto | 15 min |
| 4 | Redirecionando a saída | 10 min |
| 🏁 | Entrega | 20 min |

---

## 🧩 Etapa 0 — Operadores e funções

### Ação

```bash
ssh disciplina
mkdir -p ~/scripts/aula15
cd ~/scripts/aula15
```

Crie o arquivo de trabalho:

```bash
cat > notas.txt
Aluno:Nota1:Nota2:Nota3
João Marcelo:10.0:10.0:10.0
Alisson Barbosa:1.0:2.0:3.0
Jeandro Bezerra:7.0:8.0:9.0
Marcos Dantas:5.0:4.0:6.0
Michel Sales:3.0:4.0:2.0
```

Ctrl+D. Aritmética funciona direto:

```bash
awk -F: 'NR > 1 { print $1, ($2 + $3 + $4) / 3 }' notas.txt
```

Repare no `NR > 1`: ele pula o cabeçalho.

As funções matemáticas mais usadas:

```bash
awk 'BEGIN { print int(7.9), sqrt(16), 2^10 }'
awk 'BEGIN { srand(); print int(rand() * 100) }'
```

E os operadores de atribuição, iguais aos de C:

```bash
awk -F: 'NR > 1 { soma += $2 } END { print "Soma da Nota1:", soma }' notas.txt
awk -F: 'NR > 1 { n++ } END { print "Alunos:", n }' notas.txt
```

### ✅ Checkpoint 0

✔ A média de João Marcelo sai como `10`.
✔ `END { print "Alunos:", n }` responde `5`.

### ❓ Pergunta

`awk 'BEGIN { print int(7.9) }'` responde `7`, não `8`. O `int()` arredonda ou
trunca? Teste com `-7.9`.

---

## 🧩 Etapa 1 — `if`, `while` e `for`

### Ação — `if`

```bash
awk -F: '
NR > 1 {
    media = ($2 + $3 + $4) / 3
    if (media >= 7)
        situacao = "Aprovado"
    else if (media >= 5)
        situacao = "Final"
    else
        situacao = "Reprovado"
    print $1 ":" situacao ":" media
}
' notas.txt
```

Repare: `print a ":" b` concatena sem espaço — a **ausência** de vírgula é que
gruda os valores.

### Ação — `for` clássico

Percorrendo os campos de uma linha:

```bash
awk -F: 'NR > 1 {
    soma = 0
    for (i = 2; i <= NF; i++)
        soma += $i
    print $1, soma / (NF - 1)
}' notas.txt
```

Essa versão não depende de saber que são exatamente três notas.

### Ação — `while`

```bash
awk -F: 'NR > 1 {
    i = 2
    maior = $2
    while (i <= NF) {
        if ($i > maior) maior = $i
        i++
    }
    print $1, "maior nota:", maior
}' notas.txt
```

Os comandos `break`, `continue` e `next` também existem:

```bash
awk -F: 'NR == 1 { next } { print $1 }' notas.txt
```

O `next` pula para a próxima linha, sem executar os blocos seguintes — é a forma
idiomática de descartar o cabeçalho.

### ✅ Checkpoint 1

✔ O `if` classifica João como `Aprovado` e Michel como `Reprovado`.
✔ A versão com `for (i = 2; i <= NF; i++)` dá as mesmas médias.
✔ `NR == 1 { next }` remove o cabeçalho.

### ❓ Pergunta

Qual a diferença entre `next` e `continue` no AWK?

---

## 🧩 Etapa 2 — Vetores

Vetores no AWK são **sempre** associativos — o índice é texto, mesmo quando parece
número.

### Ação

```bash
awk -F: '
NR > 1 {
    media = ($2 + $3 + $4) / 3
    if (media >= 7)      situacao["Aprovado"]++
    else if (media >= 5) situacao["Final"]++
    else                 situacao["Reprovado"]++
}
END {
    for (s in situacao)
        print s ":", situacao[s]
}
' notas.txt
```

> ⚠️ O `for (chave in vetor)` **não garante ordem**. Se a ordem importa, ordene a
> saída — veja a Etapa 4.

Testando se uma chave existe:

```bash
awk 'BEGIN {
    v["a"] = 1
    if ("a" in v) print "a existe"
    if ("b" in v) print "b existe"; else print "b não existe"
    print length(v)
}'
```

> ⚠️ Escrever `if (v["b"] == "")` **cria** a chave `b` no vetor. Use sempre o
> operador `in` para testar existência.

Removendo:

```bash
awk 'BEGIN { v["a"]=1; v["b"]=2; delete v["a"]; print length(v) }'
```

Acumulando por chave — o padrão mais comum de todos:

```bash
awk -F: 'NR > 1 {
    for (i = 2; i <= NF; i++) {
        soma[i] += $i
        n[i]++
    }
}
END {
    printf "Média das provas:"
    for (i = 2; i <= NF; i++)
        printf " %.1f", soma[i] / n[i]
    printf "\n"
}' notas.txt
```

### ✅ Checkpoint 2

✔ O primeiro bloco imprime `Aprovado: 2`, `Final: 1`, `Reprovado: 2`.
✔ `length(v)` responde `2` e depois `1`.
✔ A média das provas sai como `5.2 5.6 6.0`.

### ❓ Pergunta

Um vetor AWK indexado por `1`, `2`, `3` parece um vetor comum. Rode
`awk 'BEGIN { v[1]=10; v["1"]=20; print length(v) }'`. O que o resultado revela?

---

## 🧩 Etapa 3 — `printf` e funções de texto

### Ação

O `printf` do AWK é praticamente o mesmo do *shell* (Aula 11):

```bash
awk -F: 'NR > 1 {
    media = ($2 + $3 + $4) / 3
    printf "%-20s %5.1f\n", $1, media
}' notas.txt
```

As funções de texto mais úteis:

| Função | O que faz |
|---|---|
| `length(s)` | tamanho |
| `toupper(s)` / `tolower(s)` | troca a caixa |
| `substr(s, i, n)` | recorta `n` caracteres a partir de `i` |
| `index(s, t)` | posição de `t` em `s`, ou 0 |
| `split(s, v, sep)` | quebra `s` em `v`, devolve a quantidade |
| `sub(re, novo)` | substitui a **primeira** ocorrência |
| `gsub(re, novo)` | substitui **todas** |
| `sprintf(fmt, ...)` | formata e devolve como texto |

```bash
awk -F: 'NR > 1 { print toupper(substr($1, 1, 1)) substr($1, 2) }' notas.txt

awk -F: 'NR > 1 {
    n = split($1, partes, " ")
    print "Sobrenome:", partes[n]
}' notas.txt

echo "a-b-c" | awk '{ gsub(/-/, "+"); print }'
```

> 💡 O `split` conta a partir de `1`, não de `0` — diferente dos vetores do *bash*.

### ✅ Checkpoint 3

✔ A tabela com `%-20s %5.1f` sai alinhada.
✔ O `split` extrai `Marcelo` como sobrenome de `João Marcelo`.
✔ `gsub` troca os dois hífens.

### ❓ Pergunta

`sub()` e `gsub()` alteram `$0` por padrão. O que acontece com `NF` se o seu `gsub`
trocar espaços por vírgulas?

---

## 🧩 Etapa 4 — Redirecionando a saída

O AWK escreve em arquivos e em comandos externos, direto do `print`.

### Ação

```bash
awk -F: 'NR > 1 {
    media = ($2 + $3 + $4) / 3
    if (media >= 7) print $1 > "aprovados.txt"
    else            print $1 > "reprovados.txt"
}' notas.txt

cat aprovados.txt
cat reprovados.txt
```

> ⚠️ Dentro do AWK, o `>` **não** trunca a cada `print` — ele abre o arquivo uma vez
> e vai acrescentando. É diferente do `>` do *shell*.

E o mais útil: mandar para um comando com `|`.

```bash
awk -F: '
NR > 1 {
    media = ($2 + $3 + $4) / 3
    printf "%-20s %5.1f\n", $1, media | "sort -k2 -rn"
}' notas.txt
```

O AWK entrega cada linha ao `sort`, que ordena tudo ao final. Isso resolve a falta
de ordem do `for (k in v)`:

```bash
awk -F: 'NR > 1 {
    if (($2+$3+$4)/3 >= 7) s["Aprovado"]++; else s["Reprovado"]++
}
END {
    for (k in s) print k, s[k] | "sort"
    close("sort")
}' notas.txt
```

> 💡 O `close()` fecha o canal e força o comando a terminar. Sem ele, a saída pode
> aparecer fora de ordem em relação ao resto do programa.

### Ação — passando valores do *shell*

```bash
LIMITE=7
awk -F: -v corte="$LIMITE" 'NR > 1 && ($2+$3+$4)/3 >= corte { print $1 }' notas.txt
```

O `-v` é a forma correta. **Não** interpole variáveis do *shell* dentro das aspas
simples — isso quebra assim que o valor tiver um espaço ou uma aspa.

### ✅ Checkpoint 4

✔ `aprovados.txt` e `reprovados.txt` foram criados com os nomes certos.
✔ O `| "sort -k2 -rn"` imprime as médias da maior para a menor.
✔ `-v corte=7` filtra os aprovados.

### ❓ Pergunta

Por que o `>` dentro do AWK não trunca o arquivo a cada `print`, se no *shell* ele
trunca?

---

## 🏁 Entrega da Aula — 1,25 pontos (Nota 2)

Individualmente, nos últimos 20 minutos. São **dois** programas AWK.

### A) `~/scripts/aula15/disciplina.awk` — 0,75 ponto

Gera um relatório completo a partir do `notas.txt` desta aula.

1. Deve ser invocado com `awk -F: -f disciplina.awk notas.txt`.
2. No `BEGIN`, imprima o cabeçalho `Aluno:Situação:Média`.
3. Para cada aluno, calcule a média das três notas e determine a situação:
   - média ≥ 7,0 → **Aprovado**
   - 5,0 ≤ média < 7,0 → **Final**
   - média < 5,0 → **Reprovado**
4. No `END`, imprima a média de **cada prova** considerando todos os alunos.
5. O cabeçalho do arquivo (linha 1) não pode entrar nos cálculos.

Saída esperada:

```
$ awk -F: -f disciplina.awk notas.txt
Aluno:Situação:Média
João Marcelo:Aprovado:10.0
Alisson Barbosa:Reprovado:2.0
Jeandro Bezerra:Aprovado:8.0
Marcos Dantas:Final:5.0
Michel Sales:Reprovado:3.0
Média das Provas: 5.2 5.6 6.0
```

### B) `~/scripts/aula15/marajas.awk` — 0,50 ponto

Dado um arquivo de salários, imprime **quem mais ganha em cada curso**.

Crie o `professores.txt`:

```
NOME        CURSO       SALARIO
Jeandro     Redes       10000
Elvis       Engenharia  11000
Hélder      Engenharia  15000
João        Redes       1000
Michel      Redes       800
Jefferson   Sistemas    5000
Márcio      Sistemas    6000
Marcos      Redes       11000
```

Saída esperada, alinhada e ordenada por curso:

```
$ awk -f marajas.awk professores.txt
Engenharia: Hélder,  15000
Redes:      Marcos,  11000
Sistemas:   Márcio,  6000
```

> 💡 Você vai precisar de **dois** vetores indexados pelo curso: um para o maior
> salário e outro para o nome de quem o recebe. A ordenação por curso sai com um
> *pipe* para `sort` no `END`.

### Critérios de correção

| # | Critério | Valor |
|---|---|---|
| 1 | `disciplina.awk` imprime cabeçalho no `BEGIN` e ignora a linha 1 | 0,20 |
| 2 | Classifica as três situações corretamente | 0,25 |
| 3 | Calcula a média de cada prova no `END` | 0,30 |
| 4 | `marajas.awk` acerta o maior salário de cada curso | 0,35 |
| 5 | A saída de `marajas.awk` sai ordenada e alinhada | 0,15 |

Correção:

```bash
cd ~/scripts/aula15
awk -F: -f disciplina.awk notas.txt
awk -f marajas.awk professores.txt
```

---

## ✅ Checklist de Encerramento

| # | Verificação | Comando |
|---|---|---|
| 1 | Os dois `.awk` existem | `ls ~/scripts/aula15/*.awk` |
| 2 | `disciplina.awk` usa `BEGIN` e `END` | `grep -c -E "BEGIN\|END" disciplina.awk` |
| 3 | `marajas.awk` usa vetores | `grep -c "\[" marajas.awk` |
| 4 | A saída de `marajas.awk` tem 3 linhas | `awk -f marajas.awk professores.txt \| wc -l` |

---

## 💬 Para Discutir em Sala

- O `disciplina.awk` faz em 20 linhas o que um *script* em *bash* puro faria em 60.
  O que o AWK tem que o *shell* não tem?
- E o contrário: o que o *shell* faz que o AWK não faz? Por que os dois continuam
  existindo lado a lado depois de 50 anos?

## 📌 Para a Próxima Aula

A **Aula 16** fecha a Nota 2. É uma **aula integradora**: um projeto único que
combina processos, menu interativo, vetores, `getopts`, `trap` e AWK. Ela vale
**2,5 pontos** — o dobro das demais.

Revise as Aulas 10 a 15 antes de vir.
