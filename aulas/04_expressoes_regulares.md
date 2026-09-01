# 🧪 Aula 04 — Expressões Regulares

**Disciplina:** Programação de *Scripts* — UFC Quixadá
**Material de apoio:** `slides/03_expressoes_regulares`
**Sessão:** Semana 2 — quarta, 19/08
**Entrega desta aula:** 1,0 ponto (Nota 1)
**Duração estimada:** 100 minutos

---

## 🎯 Objetivos da Aula

Ao final desta aula você deve ser capaz de:

- Distinguir busca literal de busca por **padrão**.
- Usar âncoras (`^`, `$`), representantes (`.`, `[]`) e quantificadores (`*`, `+`, `?`, `{}`).
- Escolher entre `grep`, `grep -E` e `grep -F` conforme o caso.
- Escrever um `grep` que responda a uma pergunta concreta sobre um arquivo de *log*.

## 🧰 Pré-requisitos

- Aulas 01 a 03 concluídas. Acesso à sua máquina com `ssh disciplina`.

## 🗺️ Roteiro

| Etapa | Assunto | Tempo |
|---|---|---|
| 0 | Conhecendo os dados | 15 min |
| 1 | Âncoras | 15 min |
| 2 | Representantes e classes | 20 min |
| 3 | Quantificadores | 15 min |
| 4 | Básicas *vs.* estendidas | 10 min |
| 🏁 | Entrega | 25 min |

---

## 🧩 Etapa 0 — Conhecendo os dados

A sua máquina é nova, e o `/var/log/auth.log` dela tem pouca coisa — só os seus
próprios acessos. Confira:

```bash
ssh disciplina
sudo wc -l /var/log/auth.log
```

Vamos usar o *log* de autenticação de um servidor **real**, que ficou exposto na
internet por cinco dias. Baixe-o:

```bash
mkdir -p ~/scripts/aula04
cd ~/scripts/aula04
wget http://joao.marcelo.nom.br/disciplinas/20212/scripts/atividades/arquivos/auth.log
wc -l auth.log
```

> 🔧 Se o `wget` não estiver instalado: `sudo apt install -y wget`. O arquivo também
> está no repositório da disciplina, em `aulas/dados/auth.log` — nesse caso, copie-o
> com `scp`, como você fez na Aula 01.

Veja com o que estamos lidando:

```bash
head -5 auth.log
cut -c1-6 auth.log | sort | uniq -c
```

```
   1084 Oct 10
    537 Oct 11
    541 Oct 12
    772 Oct 13
    200 Oct 14
```

Cinco dias, 3.134 linhas. Cada linha tem a mesma estrutura:

```
Oct 10 00:15:06 scripts sshd[63884]: Invalid user user from 167.172.41.24 port 45876
└─ data ─┘ └hora┘ └máq┘ └programa┘   └────────────── mensagem ──────────────────┘
```

Quais programas escrevem nesse arquivo?

```bash
grep -c sshd auth.log
grep -c CRON auth.log
grep -c sudo auth.log
```

O `sshd` domina — e a maior parte não são acessos legítimos, mas **tentativas de
invasão**. Dê uma olhada:

```bash
grep "Invalid user" auth.log | head -5
grep -c "Invalid user" auth.log
```

### ✅ Checkpoint 0

✔ `wc -l auth.log` responde `3134`.
✔ `cut -c1-6 auth.log | sort | uniq -c` lista cinco dias, de `Oct 10` a `Oct 14`.
✔ `grep -c "Invalid user" auth.log` responde `417`.

### ❓ Pergunta

São 417 tentativas com usuário inválido em cinco dias, em uma máquina que era só um
servidor de aula. Quem está fazendo isso, e como descobriram o endereço?

---

## 🧩 Etapa 1 — Âncoras

Sem âncora, o `grep` acha o padrão **em qualquer posição** da linha.

### Ação

```bash
grep -c "sshd" auth.log        # em qualquer lugar da linha
grep -c "^sshd" auth.log       # apenas no início da linha
```

```
2708
0
```

Nenhuma linha **começa** com `sshd` — toda linha começa com a data. O `^` prende o
padrão ao início.

O `$` prende ao fim:

```bash
grep -c "root" auth.log        # em qualquer lugar
grep -c "root$" auth.log       # apenas no fim da linha
```

```
531
122
```

Dessas 122, praticamente todas são do `CRON`. Confira — e ache a exceção:

```bash
grep "root$" auth.log | head -2
grep "root$" auth.log | grep -v CRON
```

A exceção é uma linha do `sudo`. Repare como uma pergunta simples ("quais linhas
terminam em `root`?") já exige um segundo filtro para ser respondida com precisão.

Agora a âncora que você mais vai usar — filtrar por data:

```bash
grep -c "^Oct 13" auth.log
grep "^Oct 13 09" auth.log | head -3
```

Duas opções que ajudam muito a enxergar o resultado:

```bash
grep -n "^Oct 14" auth.log | head -3       # mostra o número da linha
grep --color=auto "Invalid" auth.log | head -3   # destaca o que casou
```

### ✅ Checkpoint 1

✔ `grep -c "sshd"` responde `2708` e `grep -c "^sshd"` responde `0`.
✔ `grep -c "root"` responde `531` e `grep -c "root$"` responde `122`.
✔ `grep -c "^Oct 13"` responde `772`.

### ❓ Pergunta

O que `grep "^$" arquivo` procura? E por que `grep -c "^"` sempre devolve o mesmo
número que `wc -l`?

---

## 🧩 Etapa 2 — Representantes e classes

### Ação — o ponto

O `.` representa **um caractere qualquer**, exatamente um. Cuidado com ele:

```bash
grep -c "r..t" auth.log
```

```
3134
```

Todas as linhas do arquivo? Você queria `root`. Descubra o que de fato casou:

```bash
grep -o "r..t" auth.log | sort | uniq -c | sort -rn
```

```
3134 ript
 531 root
  14 rant
   9 ract
```

O `ript` vem de `scripts`, o nome da máquina, presente em toda linha. **O padrão fez
exatamente o que você pediu — não o que você queria.**

> 💡 **Guarde este encadeamento** — você vai usá-lo na entrega:
>
> ```bash
> grep -o "<padrão>" arquivo | sort | uniq -c | sort -rn
> ```
>
> O `-o` imprime **só o trecho que casou**, um por linha, em vez da linha inteira. O
> `sort | uniq -c` agrupa e conta, e o `sort -rn` ordena do mais frequente para o
> menos. Os comandos `sort` e `uniq` são o assunto da Aula 06; por hoje, use-os como
> receita.
>
> Para contar **quantos valores distintos** existem, sem a contagem de cada um:
>
> ```bash
> grep -o "<padrão>" arquivo | sort -u | wc -l
> ```

O mesmo vale para o ponto em endereços IP. Neste arquivo os dois dão o mesmo
resultado, mas o risco é real:

```bash
grep -c "115.87.76.161"   auth.log     # o ponto é curinga
grep -c "115\.87\.76\.161" auth.log    # agora é ponto de verdade
```

Veja a diferença com um caso construído:

```bash
echo "115x87x76x161" | grep "115.87.76.161"      # casa!
echo "115x87x76x161" | grep "115\.87\.76\.161"   # não casa
```

### Ação — as classes

Colchetes definem um **conjunto** de caracteres aceitos naquela posição:

```bash
grep -c "sshd\[[0-9]" auth.log
grep -c "port [0-9]" auth.log
grep "Oct 1[01] " auth.log | head -3        # dias 10 e 11
```

O `^` dentro dos colchetes **nega** o conjunto:

```bash
grep -c "Oct 1[^0]" auth.log      # todos os dias menos o 10
```

> ⚠️ Cuidado: `^` fora dos colchetes é âncora de início de linha; dentro deles é
> negação. São dois significados diferentes do mesmo símbolo.

A caixa importa:

```bash
grep -c "Accepted" auth.log       # 57
grep -c "accepted" auth.log       # 0
grep -ci "accepted" auth.log      # 57, ignorando a caixa
```

As classes POSIX dão nomes aos conjuntos comuns:

```bash
grep -c "[[:digit:]]" auth.log
grep "[[:upper:]][[:lower:]]*" auth.log | head -3
```

### ✅ Checkpoint 2

✔ Você descobriu, com `grep -o`, por que `r..t` casou com todas as linhas.
✔ `grep -c "Accepted"` responde `57` e `grep -c "accepted"` responde `0`.
✔ O teste com `echo "115x87x76x161"` mostrou a diferença entre `.` e `\.`.

### ❓ Pergunta

O `grep -o` foi o que revelou o problema do `r..t`. Ele imprime **só a parte que
casou**, em vez da linha inteira. Por que essa é a primeira ferramenta a usar quando
um padrão traz resultado demais?

---

## 🧩 Etapa 3 — Quantificadores

Um quantificador diz **quantas vezes** o item anterior pode se repetir.

| Quantificador | Significado |
|---|---|
| `*` | zero ou mais |
| `\+` (ou `+` no `-E`) | uma ou mais |
| `\?` (ou `?` no `-E`) | zero ou uma |
| `\{n\}` (ou `{n}` no `-E`) | exatamente `n` |
| `\{n,m\}` (ou `{n,m}` no `-E`) | de `n` a `m` |

### Ação

```bash
grep -c "sshd\[[0-9]*\]" auth.log
grep -c "port [0-9]\{4,5\}" auth.log
grep -c "[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}" auth.log
```

Aquela última linha é um padrão de endereço IP. Repare em quanta contrabarra ela
exige — é exatamente esse incômodo que a próxima etapa resolve.

Um detalhe importante do `*`:

```bash
echo "abc" | grep "x*abc"
```

Isso **casa**, e a linha é impressa. O `x*` aceita **zero** ocorrências de `x`, ou
seja, ele não exige nada.

### ✅ Checkpoint 3

✔ `grep -c "port [0-9]\{4,5\}"` responde `2353`.
✔ `echo "abc" | grep "x*abc"` imprime `abc`.

### ❓ Pergunta

Se `x*` aceita zero ocorrências, o que o padrão `^.*$` casa? Quantas linhas do
`auth.log` ele traz?

---

## 🧩 Etapa 4 — Básicas *vs.* estendidas

O `grep` sem opção usa **expressões regulares básicas** (ERB), onde `+`, `?`, `{`,
`(` e `|` precisam de contrabarra. Com `-E`, ele usa **estendidas** (ERE), onde
esses símbolos já são especiais.

### Ação

Compare as duas escritas do mesmo padrão de IP:

```bash
grep -c    "[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}" auth.log
grep -c -E "[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}"         auth.log
```

Mesmo resultado, metade das contrabarras.

O `-E` também habilita alternativa e grupos:

```bash
grep -cE "Accepted|Invalid" auth.log
grep -E "Accepted|Invalid" auth.log | head -5
```

Os parênteses agrupam, e alternativas podem ser aninhadas. As tentativas contra o
`root` aparecem com três verbos e duas preposições diferentes:

```bash
grep -cE "(Disconnected|Connection closed|Connection reset) (from|by) authenticating user root" auth.log
```

```
281
```

Escrever isso sem `-E`, com `\(`, `\|` e `\)`, seria quase ilegível.

E há o `-F`, que desliga tudo e trata o padrão como **texto literal**:

```bash
grep -cF "115.87.76.161" auth.log     # o ponto é ponto mesmo, sem escapar
```

Resumo prático:

| Quando | Use |
|---|---|
| Texto fixo, sem padrão | `grep -F` |
| Padrão simples | `grep` |
| Padrão com `+`, `?`, `{}`, `\|`, `()` | `grep -E` |

### ✅ Checkpoint 4

✔ As duas formas do padrão de IP trazem o mesmo número de linhas.
✔ `grep -cE "Accepted|Invalid"` responde `474` — a soma de `57` e `417`.
✔ A alternativa aninhada das tentativas contra o `root` responde `281`.

### ❓ Pergunta

O comando `grep "Accepted|Invalid" auth.log` (sem o `-E`) não traz nada. O que ele
estava procurando literalmente?

---

## 🏁 Entrega da Aula — 1,0 ponto (Nota 1)

Individualmente, nos últimos 25 minutos.

Você foi chamado para investigar o servidor invadido. Vai entregar uma **ferramenta**,
não uma lista de comandos: um *script* de relatório que qualquer pessoa possa rodar.

Crie em `~/scripts/aula04/investigacao.sh` um *script* **executável**, com *shebang*,
que imprima na tela o relatório abaixo.

```
=== RELATÓRIO DE SEGURANÇA — auth.log ===

Período analisado:
Oct 10
Oct 11
Oct 12
Oct 13
Oct 14

1. Linhas que não são do sshd: 426
2. Acessos aceitos: 57
3. Tentativas contra o root via sshd: 285
4. Usuário inválido com exatamente 4 letras minúsculas: 139
5. Usuário inválido contendo dígito: 63
6. IPs distintos que tentaram invadir: 31

7. Os 5 IPs mais insistentes:
    272 115.87.76.161
     35 199.19.225.248
     28 201.249.146.101
     11 167.172.41.24
      8 64.227.65.76

8. Primeiro e último acesso legítimo:
Oct 10 00:59:32
Oct 14 09:06:30
```

O *script* fica no mesmo diretório do `auth.log` e é executado de lá, com
`./investigacao.sh`.

**Restrições:**

- O bloco "Período analisado" deve ser **gerado**, não digitado à mão: extraia as
  datas do próprio arquivo com um padrão.
- Cada número dos itens 1 a 6 vem de **um único `grep`**, opcionalmente encanado
  para `wc -l`.
- Os itens 7 e 8 podem usar o encadeamento da Etapa 2 e os comandos `head` e `tail`
  da Aula 02.
- A saída dos itens 7 e 8 deve trazer **apenas** o que está no exemplo: no item 7, a
  contagem e o IP — sem a palavra `from`; no item 8, só data e hora.
- O alinhamento dos números no item 7 é o que o `uniq -c` produzir — não precisa
  ajustar espaços à mão.

> ⚠️ **O item 6 tem uma armadilha.** A resposta ingênua — extrair todo endereço IP
> precedido de `from` — devolve **66**. Mas nem todo `from` do arquivo é tentativa de
> invasão: há acessos legítimos e outras mensagens do `sshd` no meio. A resposta certa
> é **31**. Filtre antes de extrair.

> 💡 O item 4 pede **exatamente** quatro letras minúsculas. Um padrão que aceite
> "quatro ou mais" devolve um número maior. Pense em qual caractere vem logo depois do
> nome do usuário na linha, e ancore o padrão nele.

### Critérios de correção

| # | Critério | Valor |
|---|---|---|
| 1 | Tem *shebang* correto e permissão de execução | 0,10 |
| 2 | O "Período analisado" é gerado por um padrão, não digitado | 0,15 |
| 3 | Itens 1, 2 e 3 corretos (426, 57, 285) | 0,15 |
| 4 | Item 4 correto (**139**, e não "quatro ou mais") | 0,15 |
| 5 | Item 5 correto (63) | 0,10 |
| 6 | Item 6 correto (**31**, e não 66) | 0,20 |
| 7 | Item 7 traz contagem e IP limpo; item 8, só data e hora | 0,15 |

Correção:

```bash
cd ~/scripts/aula04
head -1 investigacao.sh && ls -l investigacao.sh
./investigacao.sh
```

---

## ✅ Checklist de Encerramento

| # | Verificação | Comando |
|---|---|---|
| 1 | Executável e com *shebang* | `ls -l investigacao.sh && head -1 investigacao.sh` |
| 2 | O relatório sai completo | `./investigacao.sh` |
| 3 | Os números batem com a tabela do enunciado | `./investigacao.sh \| head -20` |
| 4 | O período não está digitado à mão | `grep -c "Oct 1" investigacao.sh` — deve ser `0` |

---

## 💬 Para Discutir em Sala

- Este é o *log* de um servidor real que ficou cinco dias na internet. Foram 417
  tentativas de invasão e **nenhum** *login* por senha bem-sucedido — todos os 57
  acessos legítimos foram por chave. O que isso diz sobre a decisão de desabilitar
  autenticação por senha no SSH?
- Expressões regulares são difíceis de escrever e ainda mais difíceis de **ler**.
  Que hábito de escrita ajuda a manter um padrão compreensível daqui a um mês?
- O `r..t` da Etapa 2 casou com 3.134 linhas em vez de 531, e o item 6 da entrega
  devolve 66 em vez de 31 se você não filtrar antes. Os dois erros têm a mesma
  natureza. Como você se protege dele antes de confiar em um número?

## 📌 Para a Próxima Aula

Na **Aula 05** vamos ver redirecionamento (`slides/04_redirecionamento_de_saida`) e
aí sim vamos poder **guardar** o resultado dos nossos `grep` em arquivos, em vez de
só olhar na tela.
