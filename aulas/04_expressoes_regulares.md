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

- Aulas 01 a 03 concluídas. Acesso ao servidor com `ssh disciplina`.

## 🗺️ Roteiro

| Etapa | Assunto | Tempo |
|---|---|---|
| 0 | Preparando os dados | 10 min |
| 1 | Âncoras | 15 min |
| 2 | Representantes e classes | 20 min |
| 3 | Quantificadores | 20 min |
| 4 | Básicas *vs.* estendidas | 10 min |
| 🏁 | Entrega | 25 min |

---

## 🧩 Etapa 0 — Preparando os dados

A sua máquina é nova e o `/var/log/auth.log` dela tem pouca coisa — só os seus
próprios acessos. Confira:

```bash
ssh disciplina
sudo wc -l /var/log/auth.log
exit
```

Para ter material de verdade, vamos usar o *log* de um servidor com movimento, que
está no repositório da disciplina em `aulas/dados/auth.log`.

Da **sua máquina local**, no diretório do repositório:

```bash
ssh disciplina 'mkdir -p ~/scripts/aula04'
scp aulas/dados/auth.log disciplina:~/scripts/aula04/
```

> 👀 Você acabou de usar o `scp` e o apelido `disciplina` da Aula 01 para uma tarefa
> real. É assim que eles se pagam.

Agora conecte e confira:

```bash
ssh disciplina
cd ~/scripts/aula04
wc -l auth.log
head -5 auth.log
cut -c1-6 auth.log | sort -u
```

Uma linha típica:

```
Sep 26 07:21:44 servidor-aula sshd[2211]: Accepted publickey for bruno from 10.0.1.15 port 51322 ssh2: RSA SHA256:9Kd0AkJT7haicaMxQ
```

### ✅ Checkpoint 0

✔ `wc -l auth.log` responde `338`.
✔ `cut -c1-6 auth.log | sort -u` lista seis dias, de `Sep 26` a `Oct  1`.
✔ `head -5 auth.log` mostra linhas começando com um mês abreviado.

> 💡 O arquivo é sintético, mas o formato é o do `sshd` real: acessos aceitos por
> chave e por senha, tentativas de invasão em usuários como `root` e `admin`, e
> linhas de `sudo`, `CRON` e `systemd-logind` que **não** são do `sshd`. Você vai
> precisar dessa variedade na entrega.

---

## 🧩 Etapa 1 — Âncoras

Sem âncora, o `grep` acha o padrão **em qualquer posição** da linha.

### Ação

```bash
grep "sshd" auth.log | head -3          # em qualquer lugar da linha
grep "^Aug" auth.log | head -3          # apenas no início da linha
grep "ssh2$" auth.log | head -3         # apenas no fim da linha
```

Veja a diferença que a âncora faz:

```bash
grep -c "Aug" auth.log
grep -c "^Aug" auth.log
```

O segundo número é menor ou igual ao primeiro: linhas que mencionam `Aug` no meio
do texto contam no primeiro, mas não no segundo.

Duas opções que ajudam muito a enxergar o resultado:

```bash
grep -n "^Aug" auth.log | head -3       # mostra o número da linha
grep --color=auto "sshd" auth.log | head -3   # destaca o que casou
```

### ✅ Checkpoint 1

✔ `grep -c "Aug"` e `grep -c "^Aug"` devolvem números, e o segundo não é maior.
✔ `grep "ssh2$"` só traz linhas terminadas em `ssh2`.

### ❓ Pergunta

O que `grep "^$" arquivo` procura? E por que `grep -c "^"` sempre devolve o mesmo
número que `wc -l`?

---

## 🧩 Etapa 2 — Representantes e classes

### Ação — o ponto

O `.` representa **um caractere qualquer**, exatamente um:

```bash
grep "r..t" auth.log | head -3          # r, dois quaisquer, t
```

Para procurar um ponto literal, é preciso escapá-lo com `\`:

```bash
grep "10.0.0.7"  auth.log | head -3     # o ponto é curinga aqui
grep "10\.0\.0\.7" auth.log | head -3   # agora é ponto de verdade
```

### Ação — as classes

Colchetes definem um **conjunto** de caracteres aceitos naquela posição:

```bash
grep "sshd\[[0-9]" auth.log | head -3   # sshd[ seguido de um dígito
grep "port [0-9]" auth.log | head -3
grep "[aeiou]ccepted" auth.log | head -3
```

O `^` dentro dos colchetes **nega** o conjunto:

```bash
grep "^[^A]" auth.log | head -3         # linhas que NÃO começam com A
```

> ⚠️ Cuidado: `^` fora dos colchetes é âncora de início de linha; dentro deles é
> negação. São dois significados diferentes do mesmo símbolo.

As classes POSIX dão nomes aos conjuntos comuns:

```bash
grep "[[:digit:]]" auth.log | head -3
grep "[[:upper:]][[:lower:]]*" auth.log | head -3
grep "[[:space:]]$" auth.log            # linhas terminadas em espaço
```

### ✅ Checkpoint 2

✔ `grep "10.0.0.7"` traz um número de linhas **maior ou igual** ao de
`grep "10\.0\.0\.7"`.
✔ `grep "^[^A]"` não traz nenhuma linha começando com `A`.

### ❓ Pergunta

O padrão `[0-9]` e a classe `[[:digit:]]` fazem a mesma coisa em português e em
inglês. Em que situação usar `[[:alpha:]]` é mais seguro do que escrever `[a-zA-Z]`?

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
grep "sshd\[[0-9]*\]" auth.log | head -3
grep "port [0-9]\{4,5\}" auth.log | head -3
grep "[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}" auth.log | head -3
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

✔ `grep "port [0-9]\{4,5\}"` traz linhas com portas de 4 ou 5 dígitos.
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
grep    "[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}" auth.log | head -2
grep -E "[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}"         auth.log | head -2
```

Mesmo resultado, metade das contrabarras.

O `-E` também habilita alternativa e grupos:

```bash
grep -E "Accepted|Failed" auth.log | head -5
grep -E "(Accepted|Failed) (password|publickey)" auth.log | head -5
```

E há o `-F`, que desliga tudo e trata o padrão como **texto literal**:

```bash
grep -F "10.0.0.7" auth.log | head -3     # o ponto é ponto mesmo, sem escapar
```

Resumo prático:

| Quando | Use |
|---|---|
| Texto fixo, sem padrão | `grep -F` |
| Padrão simples | `grep` |
| Padrão com `+`, `?`, `{}`, `|`, `()` | `grep -E` |

### ✅ Checkpoint 4

✔ As duas formas do padrão de IP trazem o mesmo número de linhas — confirme com `-c`.
✔ `grep -E "Accepted|Failed"` traz linhas dos dois tipos.

### ❓ Pergunta

O comando `grep "Accepted|Failed" auth.log` (sem o `-E`) provavelmente não trouxe
nada. O que ele estava procurando literalmente?

---

## 🏁 Entrega da Aula — 1,0 ponto (Nota 1)

Individualmente, nos últimos 25 minutos.

Crie o arquivo `~/scripts/aula04/logins.sh` contendo **quatro comandos `grep`**,
um por linha, que respondam às perguntas abaixo sobre o `auth.log`.

1. Todas as linhas com mensagens que **não** são do `sshd`. *(53 linhas)*
2. Todas as linhas que indicam um *login* de **sucesso** via `sshd` cujo nome de
   usuário começa com a letra **a**. *(18 linhas)*
3. Todas as vezes que alguém tentou fazer *login* como **root** via `sshd`.
4. Todas as linhas do dia **29 de setembro**. *(65 linhas)*

**Regras:**

- Um **único** comando `grep` por item. Sem *pipe*, sem `;`, sem redirecionamento.
- O arquivo é uma lista de comandos para leitura, não precisa ser executável.
- Comente cada linha com `#` dizendo a que item ela responde.

Formato esperado:

```bash
# 1. Linhas que não são do sshd
grep ... auth.log
# 2. Login de sucesso de usuário começando com "a"
grep ... auth.log
```

### Critérios de correção

| # | Critério | Valor |
|---|---|---|
| 1 | O item 1 usa negação e funciona | 0,25 |
| 2 | O item 2 combina sucesso + inicial do usuário | 0,25 |
| 3 | O item 3 encontra tentativas com `root` | 0,25 |
| 4 | O item 4 filtra por data | 0,15 |
| 5 | Nenhum item usa *pipe* ou mais de um `grep` | 0,10 |

Correção: o professor executa cada linha do seu arquivo e confere a saída.

```bash
cd ~/scripts/aula04 && cat logins.sh
```

> 💡 O item 1 tem uma opção do `grep` que resolve sozinha. Procure em `man grep`
> por *invert*.

---

## ✅ Checklist de Encerramento

| # | Verificação | Comando |
|---|---|---|
| 1 | O arquivo existe | `ls -l ~/scripts/aula04/logins.sh` |
| 2 | Tem quatro linhas de comando | `grep -c "^grep" ~/scripts/aula04/logins.sh` |
| 3 | Nenhuma linha tem *pipe* | `grep -c "|" ~/scripts/aula04/logins.sh` |

O item 3 deve responder `0`.

---

## 💬 Para Discutir em Sala

- Expressões regulares são difíceis de escrever e ainda mais difíceis de **ler**.
  Que hábito de escrita ajuda a manter um padrão compreensível daqui a um mês?
- O `grep -F` é mais rápido que o `grep -E`. Por quê?

## 📌 Para a Próxima Aula

Na **Aula 05** vamos ver redirecionamento (`slides/04_redirecionamento_de_saida`) e
aí sim vamos poder **guardar** o resultado dos nossos `grep` em arquivos, em vez de
só olhar na tela.
