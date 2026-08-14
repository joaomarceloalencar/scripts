# 🧪 Aula 06 — Comandos Avançados de Texto

**Disciplina:** Programação de *Scripts* — UFC Quixadá
**Material de apoio:** `slides/05_comandos_avancados`
**Sessão:** Semana 3 — quarta, 26/08
**Entrega desta aula:** 1,0 ponto (Nota 1)
**Duração estimada:** 100 minutos

---

## 🎯 Objetivos da Aula

Ao final desta aula você deve ser capaz de:

- Recortar colunas de um arquivo com `cut`.
- Substituir e remover caracteres com `tr`.
- Substituir e apagar linhas com `sed`.
- Contar e eliminar repetições com `sort` e `uniq`.
- Fazer contas no *shell* com `$(( ))` e com `bc`.

## 🧰 Pré-requisitos

- Aulas 01 a 05 concluídas. O conceito de *pipe* precisa estar firme.

## 🗺️ Roteiro

| Etapa | Assunto | Tempo |
|---|---|---|
| 0 | Os dados da aula | 10 min |
| 1 | `cut` — recortando colunas | 15 min |
| 2 | `tr` — trocando caracteres | 15 min |
| 3 | `sed` — editando linhas | 20 min |
| 4 | `sort` e `uniq` — contando | 15 min |
| 5 | Aritmética | 10 min |
| 🏁 | Entrega | 25 min |

---

## 🧩 Etapa 0 — Os dados da aula

```bash
ssh disciplina
mkdir -p ~/scripts/aula06
cd ~/scripts/aula06
```

Crie o arquivo `compras.txt`:

```bash
cat > compras.txt
Produto, Valor, Loja
Playstation5, 4999, iByte
MacBook, 9799, iPlace
GalaxySamsung, 4654, FastShop
iPad, 3499, iPlace
SmartTV554k, 2799, FastShop
```

Encerre com **Ctrl+D** e confira:

```bash
cat compras.txt
wc -l compras.txt
```

### ✅ Checkpoint 0

✔ `wc -l compras.txt` responde `6` (o cabeçalho conta).

---

## 🧩 Etapa 1 — `cut`: recortando colunas

### Ação

O `cut` corta por **campo** (`-f`), usando um **delimitador** (`-d`):

```bash
cut -d, -f1 compras.txt      # só o produto
cut -d, -f2 compras.txt      # só o valor
cut -d, -f1,3 compras.txt    # produto e loja
cut -d, -f2- compras.txt     # do campo 2 até o fim
```

Também corta por **posição de caractere** (`-c`):

```bash
cut -c1-5 compras.txt
```

O cabeçalho atrapalha as contas. Para descartá-lo:

```bash
tail -n +2 compras.txt
tail -n +2 compras.txt | cut -d, -f2
```

O `tail -n +2` significa "a partir da linha 2".

### ✅ Checkpoint 1

✔ `cut -d, -f1 compras.txt` lista os produtos, com `Produto` na primeira linha.
✔ `tail -n +2 compras.txt | cut -d, -f2` lista só os cinco valores.

### ❓ Pergunta

Repare que os valores vêm com um espaço na frente (` 4999`). De onde ele veio, e
por que o `cut` não o removeu?

---

## 🧩 Etapa 2 — `tr`: trocando caracteres

O `tr` opera **caractere a caractere**, e lê apenas da entrada padrão.

### Ação

```bash
cat compras.txt | tr 'a-z' 'A-Z'          # tudo maiúsculo
cat compras.txt | tr ',' ';'              # troca vírgula por ponto e vírgula
cat compras.txt | tr -d ' '               # apaga todos os espaços
cat compras.txt | tr -s ' '               # espaços repetidos viram um só
```

A combinação que resolve o problema da etapa anterior:

```bash
tail -n +2 compras.txt | tr -d ' ' | cut -d, -f2
```

Agora os valores saem limpos.

Um uso muito comum é transformar uma linha em várias:

```bash
echo "a,b,c" | tr ',' '\n'
```

### ✅ Checkpoint 2

✔ `tail -n +2 compras.txt | tr -d ' ' | cut -d, -f2` imprime cinco números sem
espaço na frente.
✔ `echo "a,b,c" | tr ',' '\n'` imprime três linhas.

### ❓ Pergunta

O `tr` não aceita nome de arquivo como argumento — `tr 'a' 'b' arquivo.txt` dá
erro. Por que essa limitação praticamente não incomoda no dia a dia?

---

## 🧩 Etapa 3 — `sed`: editando linhas

O `sed` (*stream editor*) aplica comandos de edição a cada linha que passa.

### Ação — substituição

A forma mais usada é `s/padrão/substituto/`:

```bash
sed 's/iPlace/Apple/' compras.txt
sed 's/,/;/' compras.txt          # troca só a PRIMEIRA vírgula de cada linha
sed 's/,/;/g' compras.txt         # o g troca TODAS
```

O `sed` não altera o arquivo — ele imprime o resultado. Para gravar:

```bash
sed 's/,/;/g' compras.txt > compras_pv.txt
head -2 compras_pv.txt
```

Para alterar o arquivo no lugar, existe o `-i` — use com cuidado:

```bash
cp compras.txt teste_sed.txt
sed -i 's/iByte/Magalu/' teste_sed.txt
head -2 teste_sed.txt
```

### Ação — apagando e selecionando linhas

```bash
sed '1d' compras.txt              # apaga a linha 1
sed '/FastShop/d' compras.txt     # apaga as linhas que casam com FastShop
sed -n '2,4p' compras.txt         # imprime só as linhas 2 a 4
```

O `-n` desliga a impressão automática, e o `p` imprime só o que foi selecionado.

O `sed` também aceita expressões regulares — as mesmas da Aula 04:

```bash
sed -n '/^i/p' compras.txt        # linhas começando com i
sed 's/[0-9]\{4\}/XXXX/' compras.txt
```

### ✅ Checkpoint 3

✔ `sed '1d' compras.txt` imprime cinco linhas, sem o cabeçalho.
✔ `sed 's/,/;/g'` troca todas as vírgulas; sem o `g`, só a primeira.
✔ O `compras.txt` original continua intacto — confira com `head -1 compras.txt`.

### ❓ Pergunta

`sed '1d' arquivo` e `tail -n +2 arquivo` produzem a mesma saída. Existe alguma
situação em que você preferiria um ao outro?

---

## 🧩 Etapa 4 — `sort` e `uniq`: contando

### Ação

```bash
tail -n +2 compras.txt | tr -d ' ' | cut -d, -f3          # as lojas
tail -n +2 compras.txt | tr -d ' ' | cut -d, -f3 | sort   # ordenadas
tail -n +2 compras.txt | tr -d ' ' | cut -d, -f3 | sort | uniq
tail -n +2 compras.txt | tr -d ' ' | cut -d, -f3 | sort | uniq -c
```

> ⚠️ **O `uniq` só elimina repetições adjacentes.** Sem o `sort` antes, ele não
> funciona. Teste: rode o `uniq` sem o `sort` e compare.

Ordenando por número, e não por texto:

```bash
tail -n +2 compras.txt | tr -d ' ' | sort -t, -k2 -n      # crescente
tail -n +2 compras.txt | tr -d ' ' | sort -t, -k2 -rn     # decrescente
```

- `-t,` define a vírgula como separador.
- `-k2` ordena pelo campo 2.
- `-n` trata como número; sem ele, `9799` viria antes de `999`.
- `-r` inverte.

O produto mais caro, e a loja dele:

```bash
tail -n +2 compras.txt | tr -d ' ' | sort -t, -k2 -rn | head -1
tail -n +2 compras.txt | tr -d ' ' | sort -t, -k2 -rn | head -1 | cut -d, -f3
```

### ✅ Checkpoint 4

✔ `uniq -c` mostra a contagem por loja: `2 FastShop`, `1 iByte`, `2 iPlace`.
✔ A loja do produto mais caro é `iPlace`.
✔ Você conferiu que o `uniq` sem `sort` dá resultado errado.

### ❓ Pergunta

Sem o `-n`, o `sort` colocaria `9799` antes de `999`. Por quê?

---

## 🧩 Etapa 5 — Aritmética

### Ação

O *shell* faz contas com inteiros usando `$(( ))`:

```bash
echo $(( 2 + 3 ))
echo $(( 10 / 3 ))        # divisão inteira: 3
echo $(( 10 % 3 ))        # resto: 1
echo $(( 2 ** 10 ))
```

Para somar uma coluna inteira, o `paste` ajuda a montar a expressão:

```bash
tail -n +2 compras.txt | tr -d ' ' | cut -d, -f2 | paste -sd+
tail -n +2 compras.txt | tr -d ' ' | cut -d, -f2 | paste -sd+ | bc
```

O `paste -sd+` junta as linhas com `+` no meio, e o `bc` calcula.

O `bc` também faz contas com casas decimais, coisa que o `$(( ))` não faz:

```bash
echo "10 / 3" | bc          # 3
echo "scale=2; 10 / 3" | bc # 3.33
```

### ✅ Checkpoint 5

✔ `paste -sd+` produz algo como `4999+9799+4654+3499+2799`.
✔ Passando isso pelo `bc`, o total é `25750`.
✔ `echo "scale=2; 10/3" | bc` responde `3.33`.

### ❓ Pergunta

`echo $(( 10 / 3 ))` responde `3` e descarta o resto sem avisar. Que tipo de bug
isso pode causar em um *script* de cálculo?

---

## 🏁 Entrega da Aula — 1,0 ponto (Nota 1)

Individualmente, nos últimos 25 minutos.

Crie o arquivo `~/scripts/aula06/acessos.log` com o conteúdo abaixo, simulando o
*log* de acessos de um servidor:

```
192.168.1.10, user_a, /home, 10:01:35
192.168.1.5, user_b, /etc, 10:02:10
192.168.1.10, user_a, /var/log, 10:03:00
192.168.1.20, user_c, /tmp, 10:04:45
192.168.1.5, user_b, /home, 10:05:20
192.168.1.10, user_a, /etc, 10:06:15
192.168.1.20, user_c, /var/log, 10:07:00
192.168.1.5, user_b, /tmp, 10:08:30
192.168.1.10, user_d, /usr, 10:09:10
```

Escreva **três *scripts*** no mesmo diretório. Em nenhum deles é permitido usar
laços (`for`, `while`) — apenas *pipes* e os comandos desta aula.

### A) `usuarios_unicos.sh`

Imprime a lista de usuários únicos que acessaram o servidor, em ordem alfabética.

```
user_a
user_b
user_c
user_d
```

### B) `ip_mais_frequente.sh`

Imprime **apenas** o endereço IP que mais acessou o servidor.

```
192.168.1.10
```

### C) `acessos_por_usuario.sh`

Imprime a quantidade de acessos por usuário, do mais ativo para o menos ativo, no
formato `<quantidade> <usuário>`.

```
3 user_a
3 user_b
2 user_c
1 user_d
```

> ⚠️ Repare que `user_a` e `user_b` **empatam** com 3 acessos cada. A ordem entre
> os dois pode variar conforme o `sort`. Qualquer uma das duas ordens é aceita na
> correção — mas pense em como você garantiria uma ordem previsível.

### Critérios de correção

| # | Critério | Valor |
|---|---|---|
| 1 | O `acessos.log` existe com as 9 linhas | 0,1 |
| 2 | `usuarios_unicos.sh` produz a saída exata | 0,3 |
| 3 | `ip_mais_frequente.sh` imprime só o IP, sem contagem | 0,3 |
| 4 | `acessos_por_usuario.sh` produz a saída ordenada | 0,2 |
| 5 | Nenhum *script* usa `for` ou `while` | 0,1 |

Correção:

```bash
cd ~/scripts/aula06 && for s in usuarios_unicos ip_mais_frequente acessos_por_usuario; do echo "--- $s"; ./$s.sh; done
```

> 💡 O item B é o C com mais um passo. Resolva o C primeiro e depois pense em como
> ficar só com o IP.

---

## ✅ Checklist de Encerramento

| # | Verificação | Comando |
|---|---|---|
| 1 | Os três *scripts* são executáveis | `ls -l ~/scripts/aula06/*.sh` |
| 2 | Nenhum usa laço | `grep -l -E "for \|while " ~/scripts/aula06/*.sh` |
| 3 | Todos têm *shebang* | `head -1 ~/scripts/aula06/*.sh` |

O item 2 não deve listar nenhum arquivo.

---

## 💬 Para Discutir em Sala

- O encadeamento `tr -d ' ' | cut -d, -f2 | sort -rn | head -1` é poderoso, mas
  quebra se o formato do arquivo mudar um pouco. Quão frágil é essa abordagem?
- Você usou `cut`, `tr` e `sed`, e os três sabem fazer substituição. Como escolher?

## 📌 Para a Próxima Aula

Na **Aula 07** paramos de digitar comandos soltos e começamos a escrever *scripts*
de verdade: variáveis, parâmetros e leitura de argumentos
(`slides/06_variaveis_e_parametros`).
