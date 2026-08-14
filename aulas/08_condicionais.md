# 🧪 Aula 08 — Condicionais

**Disciplina:** Programação de *Scripts* — UFC Quixadá
**Material de apoio:** `slides/07_condicionais`
**Sessão:** Semana 4 — quarta, 02/09
**Entrega desta aula:** 1,0 ponto (Nota 1)
**Duração estimada:** 100 minutos

---

## 🎯 Objetivos da Aula

Ao final desta aula você deve ser capaz de:

- Escrever `if`/`then`/`else`/`elif` com a sintaxe correta.
- Testar arquivos, cadeias de caracteres e números com `[ ]`.
- Usar `&&` e `||` como alternativa curta ao `if`.
- Escolher entre `if` e `case` conforme o problema.
- Validar os parâmetros recebidos por um *script*.

## 🧰 Pré-requisitos

- Aula 07 concluída: parâmetros (`$1`, `$#`) e código de retorno (`$?`).

## 🗺️ Roteiro

| Etapa | Assunto | Tempo |
|---|---|---|
| 0 | O `if` e o código de retorno | 15 min |
| 1 | O comando `test` e os colchetes | 20 min |
| 2 | Testando arquivos, textos e números | 20 min |
| 3 | `&&` e `||` | 10 min |
| 4 | `case` | 10 min |
| 🏁 | Entrega | 25 min |

---

## 🧩 Etapa 0 — O `if` e o código de retorno

O `if` do *shell* não avalia uma expressão booleana. Ele executa um **comando** e
olha o código de retorno: `0` é verdadeiro, qualquer outro é falso.

### Ação

```bash
ssh disciplina
mkdir -p ~/scripts/aula08
cd ~/scripts/aula08
```

Veja o `if` usando um comando qualquer:

```bash
if grep -q "root" /etc/passwd; then
    echo "O usuário root existe"
else
    echo "Não achei o root"
fi
```

O `grep -q` não imprime nada — só devolve `0` se achou. É isso que o `if` usa.

Teste com um comando que falha:

```bash
if ls /naoexiste 2> /dev/null; then
    echo "existe"
else
    echo "não existe"
fi
```

> ⚠️ O `;` antes do `then` é **obrigatório** se eles estiverem na mesma linha. A
> alternativa é quebrar a linha:
>
> ```bash
> if comando
> then
>     ...
> fi
> ```

### ✅ Checkpoint 0

✔ O primeiro `if` imprime `O usuário root existe`.
✔ O segundo imprime `não existe`.

### ❓ Pergunta

`0` é verdadeiro e o resto é falso — o contrário da maioria das linguagens, onde
zero é falso. Por que o *shell* faz assim? (Dica: quantas formas diferentes um
comando tem de dar errado?)

---

## 🧩 Etapa 1 — O comando `test` e os colchetes

### Ação

O `test` é um **comando de verdade**, não sintaxe:

```bash
type test
test -f /etc/passwd
echo $?
test -f /naoexiste
echo $?
```

E `[` é outro nome para o mesmo comando:

```bash
type [
[ -f /etc/passwd ]
echo $?
```

Por isso a sintaxe é tão exigente:

```bash
[ -f /etc/passwd ]      # correto
[-f /etc/passwd ]       # erro: comando "[-f" não existe
[ -f /etc/passwd]       # erro: falta o argumento de fechamento
```

Rode os três e leia as mensagens de erro.

**Os espaços em volta dos colchetes são obrigatórios** porque `[` é o nome de um
programa e `]` é o último argumento dele.

Juntando com o `if`:

```bash
if [ -f /etc/passwd ]; then
    echo "É um arquivo comum"
fi
```

### ✅ Checkpoint 1

✔ `type [` responde que é um *builtin* do *shell*.
✔ Você viu os erros de `[-f` e de `]` colado.

### ❓ Pergunta

Se `[` é um comando, o que exatamente o `]` significa para ele? Rode
`help test | head -5` e confirme.

---

## 🧩 Etapa 2 — Testando arquivos, textos e números

### Ação — arquivos

| Teste | Verdadeiro se |
|---|---|
| `-e caminho` | existe (arquivo ou diretório) |
| `-f caminho` | existe e é arquivo comum |
| `-d caminho` | existe e é diretório |
| `-r` / `-w` / `-x` | tem permissão de leitura / escrita / execução |
| `-s caminho` | existe e não está vazio |

```bash
[ -e /etc ] && echo "existe"
[ -f /etc ] && echo "é arquivo" || echo "não é arquivo comum"
[ -d /etc ] && echo "é diretório"
[ -w /etc ] && echo "posso escrever" || echo "não posso escrever"
```

### Ação — cadeias de caracteres

| Teste | Verdadeiro se |
|---|---|
| `-z "$VAR"` | está **vazia** |
| `-n "$VAR"` | **não** está vazia |
| `"$A" = "$B"` | são iguais |
| `"$A" != "$B"` | são diferentes |

```bash
VAZIA=""
CHEIA="texto"

[ -z "$VAZIA" ] && echo "vazia"
[ -n "$CHEIA" ] && echo "cheia"
[ "$CHEIA" = "texto" ] && echo "igual"
```

> ⚠️ **As aspas aqui não são opcionais.** Teste o que acontece sem elas:
>
> ```bash
> [ -z $VAZIA ] && echo ok
> ```
>
> Sem aspas, a variável vazia some antes de o `[` recebê-la, e o teste fica
> malformado.

### Ação — números

Números usam operadores **diferentes** dos de texto:

| Números | Texto | Significado |
|---|---|---|
| `-eq` | `=` | igual |
| `-ne` | `!=` | diferente |
| `-lt` | | menor |
| `-le` | | menor ou igual |
| `-gt` | | maior |
| `-ge` | | maior ou igual |

```bash
N=10
[ "$N" -gt 5 ] && echo "maior que 5"
[ "$N" -eq 10 ] && echo "igual a 10"
```

Veja por que a distinção importa:

```bash
[ "10" = "10.0" ] && echo "iguais como texto" || echo "diferentes como texto"
[ 10 -eq 10 ] && echo "iguais como número"
```

### ✅ Checkpoint 2

✔ `[ -f /etc ]` é falso e `[ -d /etc ]` é verdadeiro.
✔ `[ -z $VAZIA ]` sem aspas dá erro ou resultado inesperado; com aspas funciona.
✔ Você usou `-gt` para números e `=` para texto.

### ❓ Pergunta

O que acontece em `[ "$N" -gt 5 ]` se `N` contiver a palavra `abc`? Teste e leia a
mensagem.

---

## 🧩 Etapa 3 — `&&` e `||`

### Ação

O `&&` executa o segundo comando **só se** o primeiro deu certo. O `||`, só se deu
errado.

```bash
mkdir -p testes && echo "diretório pronto"
ls /naoexiste 2> /dev/null || echo "não encontrei"
```

Combinando os dois, você tem um `if`/`else` de uma linha:

```bash
[ -d testes ] && echo "existe" || echo "não existe"
```

> ⚠️ **Essa construção tem uma armadilha.** Se o comando do `&&` falhar, o `||`
> dispara também. Compare:
>
> ```bash
> [ -d testes ] && ls /naoexiste || echo "caiu no else"
> ```
>
> O teste deu certo, mas a mensagem do `else` apareceu mesmo assim. Para lógica
> com mais de um comando, use `if` de verdade.

Encadeando testes dentro do mesmo `[ ]`:

```bash
N=15
[ "$N" -gt 10 ] && [ "$N" -lt 20 ] && echo "entre 10 e 20"
[ "$N" -gt 10 -a "$N" -lt 20 ] && echo "entre 10 e 20 (forma antiga)"
```

A primeira forma é a recomendada; a segunda (`-a`, `-o`) está obsoleta.

### ✅ Checkpoint 3

✔ `[ -d testes ] && echo existe || echo "não existe"` imprime `existe`.
✔ Você reproduziu a armadilha do `&&` seguido de `||`.

### ❓ Pergunta

Por que a forma `teste && A || B` **não** é equivalente a `if teste; then A; else B; fi`?

---

## 🧩 Etapa 4 — `case`

Quando você compara **a mesma variável** com vários valores, o `case` fica mais
legível que uma cadeia de `elif`.

### Ação

```bash
cat > classifica.sh
#!/bin/bash
case "$1" in
    0)
        echo "O valor é nulo."
        ;;
    10|20)
        echo "Valor especial."
        ;;
    [0-9]|1[0-9]|20)
        echo "Valor é $1 e não é especial."
        ;;
    *)
        echo "Fora da faixa aceita (0 a 20)."
        ;;
esac
```

Ctrl+D, e teste:

```bash
chmod +x classifica.sh
./classifica.sh 0
./classifica.sh 10
./classifica.sh 7
./classifica.sh 99
./classifica.sh abc
```

Repare em três coisas:

- Cada ramo termina com `;;`.
- O `|` separa alternativas no mesmo ramo.
- Os padrões são os do *shell* (`*`, `?`, `[]`), **não** expressões regulares — um
  `*` aqui é "qualquer coisa", não "zero ou mais do anterior".
- O primeiro padrão que casa vence; a **ordem importa**.

### ✅ Checkpoint 4

✔ `./classifica.sh 10` responde `Valor especial.`
✔ `./classifica.sh 99` e `./classifica.sh abc` caem no `*`.

### ❓ Pergunta

Se você mover o ramo `*)` para o topo do `case`, o que acontece? Teste.

---

## 🏁 Entrega da Aula — 1,0 ponto (Nota 1)

Individualmente, nos últimos 25 minutos. São **dois** *scripts*.

### A) `~/scripts/aula08/valida_dir.sh` — 0,5 ponto

Recebe um nome de diretório como parâmetro.

1. Verifique se foi passado **exatamente um** parâmetro. Se não, imprima
   `Uso: ./valida_dir.sh <diretorio>` e encerre com código de retorno `1`.
2. Usando `[ ]`, verifique se o diretório **existe** e se tem **permissão de escrita**.
3. Se existir **e** for gravável, imprima `Diretório ok. Listando:` e em seguida
   liste o conteúdo.
4. Caso contrário, imprima `Erro: o diretório não existe ou não pode ser modificado.`

```
$ ./valida_dir.sh
Uso: ./valida_dir.sh <diretorio>
$ ./valida_dir.sh /tmp
Diretório ok. Listando:
...
$ ./valida_dir.sh /etc
Erro: o diretório não existe ou não pode ser modificado.
```

### B) `~/scripts/aula08/classifica_num.sh` — 0,5 ponto

Recebe um número inteiro como primeiro parâmetro e o classifica **usando `case`**:

- Exatamente `0` → `O valor é nulo.`
- Exatamente `10` ou `20` → `Valor especial.`
- Qualquer outro número **de 0 a 20** → `Valor é <n> e não é especial.`
- Qualquer outra coisa → `Entrada inválida: informe um número de 0 a 20.`

**Restrição:** a validação da faixa 0–20 deve ser feita **apenas com `case`**. Não
use `if` neste *script*.

### Critérios de correção

| # | Critério | Valor |
|---|---|---|
| 1 | `valida_dir.sh` trata a ausência de parâmetro e retorna 1 | 0,15 |
| 2 | `valida_dir.sh` testa existência **e** escrita | 0,20 |
| 3 | `valida_dir.sh` lista o conteúdo no caso de sucesso | 0,15 |
| 4 | `classifica_num.sh` acerta os quatro casos | 0,30 |
| 5 | `classifica_num.sh` não usa `if` | 0,20 |

Correção:

```bash
cd ~/scripts/aula08
./valida_dir.sh; echo "retorno=$?"
./valida_dir.sh /tmp | head -2
./valida_dir.sh /etc
for n in 0 10 20 7 99 abc; do printf '%s -> ' "$n"; ./classifica_num.sh "$n"; done
grep -c "if " classifica_num.sh
```

O último comando deve responder `0`.

---

## ✅ Checklist de Encerramento

| # | Verificação | Comando |
|---|---|---|
| 1 | Os dois *scripts* são executáveis | `ls -l ~/scripts/aula08/*.sh` |
| 2 | O `valida_dir.sh` retorna 1 sem parâmetro | `./valida_dir.sh; echo $?` |
| 3 | O `classifica_num.sh` não tem `if` | `grep -c "if " classifica_num.sh` |
| 4 | Todos os testes usam aspas nas variáveis | `grep '\[ \$' *.sh` |

O item 4 **não** deve listar nada: toda variável dentro de `[ ]` deve estar entre aspas.

---

## 💬 Para Discutir em Sala

- O `[` ser um comando, e não sintaxe, explica quase todos os erros bobos desta
  aula. Que outros "detalhes de sintaxe" do *shell* na verdade são comandos?
- O `case` do *shell* usa padrões de arquivo, e o `grep` usa expressões regulares.
  Os dois usam `*` com significados diferentes. Como você evita confundir?

## 📌 Para a Próxima Aula

A **Aula 09** fecha a Nota 1 com laços (`slides/08_iteracoes`): `for`, `while`,
`until` e o `IFS`. Ela vale **2,0 pontos** — o dobro das demais — porque a entrega
combina tudo que vimos no bloco.
