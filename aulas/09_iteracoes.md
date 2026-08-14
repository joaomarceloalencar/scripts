# 🧪 Aula 09 — Iterações

**Disciplina:** Programação de *Scripts* — UFC Quixadá
**Material de apoio:** `slides/08_iteracoes`
**Sessão:** Semana 5 — terça, 08/09
**Entrega desta aula:** 2,0 pontos (Nota 1) — *aula de fechamento do bloco*
**Duração estimada:** 100 minutos

---

## 🎯 Objetivos da Aula

Ao final desta aula você deve ser capaz de:

- Escrever laços `for` sobre listas, faixas e resultados de comandos.
- Escrever laços `while` e `until`, e saber quando cada um cabe.
- Ler um arquivo linha a linha sem perder espaços nem barras invertidas.
- Explicar o papel do `IFS` na quebra de uma linha em campos.
- Combinar laços com tudo que foi visto no bloco.

## 🧰 Pré-requisitos

- Aulas 01 a 08. Esta aula usa condicionais, variáveis, parâmetros e *pipes*.

## 🗺️ Roteiro

| Etapa | Assunto | Tempo |
|---|---|---|
| 0 | `for` sobre listas | 15 min |
| 1 | `for` sobre saída de comando | 15 min |
| 2 | `while` e `until` | 15 min |
| 3 | Lendo arquivo linha a linha | 15 min |
| 4 | O `IFS` | 10 min |
| 🏁 | Entrega | 30 min |

---

## 🧩 Etapa 0 — `for` sobre listas

### Ação

```bash
ssh disciplina
mkdir -p ~/scripts/aula09
cd ~/scripts/aula09
```

A forma mais simples percorre uma lista literal:

```bash
for cor in vermelho verde azul; do
    echo "Cor: $cor"
done
```

A lista pode vir de uma expansão de chaves ou de um padrão de arquivo:

```bash
for n in {1..5}; do
    echo "Número $n"
done

for arq in /etc/*.conf; do
    echo "$arq"
done
```

E existe a forma estilo C, útil quando você precisa de um contador:

```bash
for (( i=0; i<5; i++ )); do
    echo "i vale $i"
done
```

Laços aninhados criam estruturas rapidamente:

```bash
for d in {1..3}; do
    mkdir -p "estrutura/dir$d"
    for a in {1..2}; do
        touch "estrutura/dir$d/arq$a.txt"
    done
done
ls -R estrutura
```

### ✅ Checkpoint 0

✔ `ls -R estrutura` mostra `dir1` a `dir3`, cada um com `arq1.txt` e `arq2.txt`.
✔ Você criou 3 diretórios e 6 arquivos com **um** bloco de código.

### ❓ Pergunta

`for arq in /etc/*.conf` funcionou. Mas se o diretório não tivesse nenhum `.conf`,
o que a variável `arq` conteria na primeira volta? Teste com um padrão que não casa
com nada.

---

## 🧩 Etapa 1 — `for` sobre saída de comando

### Ação

```bash
for u in $(cut -d: -f1 /etc/passwd | head -5); do
    echo "Usuário: $u"
done
```

Isso funciona — mas tem um defeito grave que você precisa ver agora:

```bash
mkdir -p nomes
touch "nomes/arquivo com espaco.txt"
touch "nomes/simples.txt"

for arq in $(ls nomes); do
    echo "[$arq]"
done
```

Saída:

```
[arquivo]
[com]
[espaco.txt]
[simples.txt]
```

O `$(ls)` devolveu um texto, e o *shell* o quebrou em **palavras**, não em nomes de
arquivo. A forma correta usa o próprio *glob*:

```bash
for arq in nomes/*; do
    echo "[$arq]"
done
```

```
[nomes/arquivo com espaco.txt]
[nomes/simples.txt]
```

> ⚠️ **Nunca escreva `for arq in $(ls ...)`.** Use `for arq in diretorio/*`. Esse é
> um dos erros mais comuns em *scripts* de produção.

### ✅ Checkpoint 1

✔ A versão com `$(ls)` quebrou o nome com espaço em três pedaços.
✔ A versão com `nomes/*` manteve o nome inteiro.

### ❓ Pergunta

O `for` sobre `$(comando)` quebra em espaços, tabulações e quebras de linha. Onde
o *shell* guarda essa lista de separadores? (Você vai descobrir na Etapa 4.)

---

## 🧩 Etapa 2 — `while` e `until`

O `for` percorre uma lista conhecida. O `while` repete **enquanto** uma condição for
verdadeira — útil quando você não sabe quantas voltas serão.

### Ação

```bash
contador=1
while [ "$contador" -le 5 ]; do
    echo "Volta $contador"
    contador=$(( contador + 1 ))
done
```

O `until` é o inverso: repete **até que** a condição fique verdadeira.

```bash
contador=1
until [ "$contador" -gt 5 ]; do
    echo "Volta $contador"
    contador=$(( contador + 1 ))
done
```

Os dois blocos acima imprimem exatamente a mesma coisa.

Controlando o laço por dentro:

```bash
for n in {1..10}; do
    [ "$n" -eq 3 ] && continue     # pula esta volta
    [ "$n" -eq 6 ] && break        # encerra o laço
    echo "n = $n"
done
```

> ⚠️ Um `while` cuja condição nunca muda é um laço infinito. Se travar, **Ctrl+C**
> encerra. Antes de rodar um `while`, confirme que algo dentro dele altera a
> condição.

### ✅ Checkpoint 2

✔ Os blocos de `while` e `until` imprimem `Volta 1` a `Volta 5`.
✔ O laço com `continue`/`break` imprime `1`, `2`, `4`, `5` e para.

### ❓ Pergunta

Se `while` e `until` fazem a mesma coisa com a condição invertida, por que a
linguagem oferece os dois?

---

## 🧩 Etapa 3 — Lendo arquivo linha a linha

### Ação

Prepare um arquivo:

```bash
cat > pessoas.txt
João Marcelo:joao@ufc.br:professor
Ana Paula:ana@alu.ufc.br:aluno
Carlos Silva:carlos@alu.ufc.br:aluno
```

Ctrl+D. Agora a forma **correta** de percorrer as linhas:

```bash
while read -r linha; do
    echo "[$linha]"
done < pessoas.txt
```

Repare no `< pessoas.txt` **depois** do `done`: a entrada é redirecionada para o
laço inteiro.

O `read` também divide a linha em campos, se você der mais de uma variável:

```bash
while IFS=: read -r nome email tipo; do
    echo "$tipo: $nome <$email>"
done < pessoas.txt
```

Saída:

```
professor: João Marcelo <joao@ufc.br>
aluno: Ana Paula <ana@alu.ufc.br>
aluno: Carlos Silva <carlos@alu.ufc.br>
```

> 💡 **Por que `-r`?** Sem ele, o `read` interpreta a contrabarra como escape e
> come caracteres do seu texto. Use `read -r` sempre.

Também dá para ler da saída de um *pipe*:

```bash
cut -d: -f1 pessoas.txt | while read -r nome; do
    echo "Nome: $nome"
done
```

> ⚠️ Cuidado com essa forma: o lado direito do *pipe* roda em um **subprocesso**.
> Variáveis alteradas lá dentro **não** sobrevivem ao fim do laço. Teste:
>
> ```bash
> total=0
> cut -d: -f1 pessoas.txt | while read -r n; do total=$(( total + 1 )); done
> echo "total=$total"
> ```
>
> Imprime `total=0`. Com `done < arquivo` em vez do *pipe*, imprime `3`.

### ✅ Checkpoint 3

✔ O laço com `IFS=:` imprime as três linhas formatadas.
✔ Você reproduziu o `total=0` com *pipe* e o `total=3` com redirecionamento.

### ❓ Pergunta

O `while read` com *pipe* perde o valor da variável. Que outra construção do
*shell* você conhece que também roda em subprocesso?

---

## 🧩 Etapa 4 — O `IFS`

O `IFS` (*Internal Field Separator*) é a variável que guarda os caracteres usados
para quebrar texto em campos.

### Ação

```bash
echo "[$IFS]" | cat -A
```

O padrão é espaço, tabulação e quebra de linha.

Veja o efeito de alterá-lo:

```bash
LINHA="a:b:c"

for campo in $LINHA; do echo "[$campo]"; done      # um campo só

IFS=:
for campo in $LINHA; do echo "[$campo]"; done      # três campos
```

Restaure antes de continuar — um `IFS` alterado quebra comandos seguintes:

```bash
unset IFS
for campo in $LINHA; do echo "[$campo]"; done
```

A forma segura é alterar o `IFS` **só para um comando**, como fizemos na etapa
anterior com `IFS=: read -r ...`. Assim ele volta ao normal automaticamente.

### ✅ Checkpoint 4

✔ Com o `IFS` padrão, `a:b:c` é um campo só.
✔ Com `IFS=:`, viram três.
✔ Depois do `unset IFS`, volta a ser um.

### ❓ Pergunta

Agora responda a pergunta da Etapa 1: por que `for arq in $(ls nomes)` quebrou o
nome `arquivo com espaco.txt` em três pedaços?

---

## 🏁 Entrega da Aula — 2,0 pontos (Nota 1)

Individualmente, nos últimos 30 minutos. São **duas** questões, 1,0 ponto cada.

Esta é a última entrega da Nota 1 e vale o dobro: ela combina laços com o que você
viu nas aulas anteriores do bloco.

### A) `~/scripts/aula09/cinco_diretorios.sh` — 1,0 ponto

Ao ser executado, o *script* deve:

1. Criar um diretório chamado `cinco`.
2. Criar cinco subdiretórios, de `cinco/dir1` a `cinco/dir5`.
3. Em **cada** subdiretório, criar quatro arquivos, de `arq1.txt` a `arq4.txt`, onde:
   - `arq1.txt` tem 1 linha, contendo apenas o dígito `1`.
   - `arq2.txt` tem 2 linhas, cada uma com o dígito `2`.
   - `arq3.txt` tem 3 linhas, cada uma com o dígito `3`.
   - `arq4.txt` tem 4 linhas, cada uma com o dígito `4`.

**Restrição:** você **não pode** repetir `mkdir` seis vezes nem escrever vinte
comandos em sequência. Use laços aninhados.

Verificação:

```
$ ./cinco_diretorios.sh
$ wc -l cinco/dir3/*
 1 cinco/dir3/arq1.txt
 2 cinco/dir3/arq2.txt
 3 cinco/dir3/arq3.txt
 4 cinco/dir3/arq4.txt
10 total
```

### B) `~/scripts/aula09/ordenar_linhas.sh` — 1,0 ponto

Recebe como parâmetro o caminho de um diretório que contém arquivos de texto.
Imprime a lista dos arquivos **em ordem crescente de quantidade de linhas**,
mostrando a contagem e o nome.

1. Valide que foi passado exatamente um parâmetro e que ele é um diretório
   existente. Se não for, imprima `Uso: ./ordenar_linhas.sh <diretorio>` e
   encerre com retorno `1`.
2. Considere apenas arquivos comuns — ignore subdiretórios.
3. O *script* deve funcionar com nomes de arquivo que contenham **espaços**.

> 💡 O arquivo com mais linhas não é necessariamente o maior em *bytes*.

Ambiente de teste — monte com os comandos abaixo:

```bash
mkdir -p testes_linhas
printf 'Linha 1\nLinha 2\nLinha 3\n' > testes_linhas/a.txt
printf 'A\nB\nC\nD\nE\n'             > testes_linhas/b.txt
seq 1 7                              > "testes_linhas/c com espaco.txt"
```

Saída esperada:

```
$ ./ordenar_linhas.sh testes_linhas
3 a.txt
5 b.txt
7 c com espaco.txt
```

### Critérios de correção

| # | Critério | Valor |
|---|---|---|
| 1 | `cinco_diretorios.sh` cria a árvore completa | 0,4 |
| 2 | O conteúdo dos arquivos tem a contagem de linhas certa | 0,3 |
| 3 | Usa laços aninhados, sem repetir comandos | 0,3 |
| 4 | `ordenar_linhas.sh` valida o parâmetro e retorna 1 | 0,2 |
| 5 | Ordena corretamente por número de linhas | 0,5 |
| 6 | Funciona com nome de arquivo contendo espaço | 0,3 |

Correção:

```bash
cd ~/scripts/aula09
rm -rf cinco && ./cinco_diretorios.sh && wc -l cinco/dir3/*
./ordenar_linhas.sh; echo "retorno=$?"
./ordenar_linhas.sh testes_linhas
```

---

## ✅ Checklist de Encerramento

| # | Verificação | Comando |
|---|---|---|
| 1 | A árvore `cinco` está completa | `find cinco -type f \| wc -l` |
| 2 | As contagens de linha estão certas | `wc -l cinco/dir1/*` |
| 3 | O ordenador valida parâmetro | `./ordenar_linhas.sh; echo $?` |
| 4 | O ordenador aguenta espaço no nome | `./ordenar_linhas.sh testes_linhas` |
| 5 | Nenhum laço usa `$(ls)` | `grep -c 'in \$(ls' *.sh` |

O item 1 deve responder `20`. O item 5 deve responder `0` para todos os arquivos.

---

## 💬 Para Discutir em Sala

- A restrição "não repita `mkdir` seis vezes" parece arbitrária. Qual é o argumento
  real a favor do laço, se o resultado é idêntico?
- O `for arq in $(ls)` é um erro tão comum que tem nome próprio na comunidade.
  Depois desta aula, você consegue explicar o problema para um colega em uma frase?

## 📌 Fechamento da Nota 1

A próxima sessão (quarta, 09/09) é de **entrega e correção**. Traga resolvidas as
entregas das Aulas 01 a 09 — as **duas piores serão descartadas** no cálculo da nota.

Confira antes de vir:

```bash
ls -d ~/scripts/aula0*
```

Na **Aula 10** começa o Bloco 2, com gerência de processos
(`slides/09_gerencia_de_processos`).
