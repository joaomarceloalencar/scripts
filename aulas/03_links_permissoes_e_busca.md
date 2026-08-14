# 🧪 Aula 03 — Ligações, Permissões e Busca

**Disciplina:** Programação de *Scripts* — UFC Quixadá
**Material de apoio:** `slides/02_comandos_basicos` (parte 2)
**Sessão:** Semana 2 — terça, 18/08
**Entrega desta aula:** 1,0 ponto (Nota 1)
**Duração estimada:** 100 minutos

---

## 🎯 Objetivos da Aula

Ao final desta aula você deve ser capaz de:

- Criar ligações simbólicas com `ln -s` e explicar por que o caminho usado importa.
- Ler e alterar permissões de arquivos com `chmod`, nas formas simbólica e octal.
- Localizar arquivos por nome com `find`.
- Localizar arquivos por **conteúdo** com `grep`.
- Extrair partes de um caminho com `basename` e `dirname`.

## 🧰 Pré-requisitos

- A [Aula 02](02_navegacao_e_arquivos.md) concluída, com o diretório
  `~/scripts/aula02/meucurso` montado.

## 🗺️ Roteiro

| Etapa | Assunto | Tempo |
|---|---|---|
| 0 | Preparando o terreno | 5 min |
| 1 | Ligações simbólicas | 20 min |
| 2 | O caminho relativo dentro do link | 15 min |
| 3 | Permissões | 20 min |
| 4 | Procurando por nome e por conteúdo | 15 min |
| 🏁 | Entrega | 25 min |

---

## 🧩 Etapa 0 — Preparando o terreno

Trabalhe sobre uma **cópia** do que você montou na aula passada, para não perder o
original se algo der errado:

```bash
ssh disciplina
mkdir -p ~/scripts/aula03
cp -r ~/scripts/aula02/meucurso ~/scripts/aula03/
cd ~/scripts/aula03/meucurso
ls
```

### ✅ Checkpoint 0

✔ `ls` mostra `disciplinas`, `professores` e `historico`.

---

## 🧩 Etapa 1 — Ligações simbólicas

Uma ligação simbólica (*soft link*) é um arquivo que **aponta** para outro. É o
equivalente de um atalho.

### Ação

```bash
cd ~/scripts/aula03/meucurso
ln -s disciplinas/fundamentos_de_programacao.txt atalho.txt
ls -l
```

Repare na saída:

```
lrwxrwxrwx 1 aluno aluno   42 ago 18 08:22 atalho.txt -> disciplinas/fundamentos_de_programacao.txt
```

O `l` no início indica *link*. A seta mostra para onde ele aponta.

Escreva através do *link* e veja o efeito no original:

```bash
echo "QXD0001" > atalho.txt
cat disciplinas/fundamentos_de_programacao.txt
```

O conteúdo aparece no arquivo original — o *link* é só um caminho, não uma cópia.

Agora quebre o *link* de propósito:

```bash
mv disciplinas/fundamentos_de_programacao.txt disciplinas/fp.txt
ls -l atalho.txt
cat atalho.txt
```

```
cat: atalho.txt: Arquivo ou diretório inexistente
```

O *link* continua existindo, mas aponta para um caminho que não existe mais. Desfaça:

```bash
mv disciplinas/fp.txt disciplinas/fundamentos_de_programacao.txt
cat atalho.txt
```

### ✅ Checkpoint 1

✔ `ls -l atalho.txt` começa com `l` e mostra a seta `->`.
✔ `cat atalho.txt` imprime `QXD0001`.

### ❓ Pergunta

Se o *link* fosse uma cópia do arquivo, o que teria acontecido quando você
renomeou o original? E o que aconteceu de fato?

---

## 🧩 Etapa 2 — O caminho relativo dentro do *link*

Aqui está a parte que costuma dar errado. O caminho guardado no *link* é
interpretado **a partir do diretório onde o link está**, não de onde você o criou.

### Ação

Crie um diretório e, de dentro dele, um *link* usando um caminho relativo errado:

```bash
cd ~/scripts/aula03/meucurso
mkdir -p historico/fundamentos_de_programacao
cd historico/fundamentos_de_programacao
ln -s disciplinas/fundamentos_de_programacao.txt programa
ls -l
cat programa
```

Quebrado. O *link* está em `historico/fundamentos_de_programacao/`, e a partir
dali não existe nenhum `disciplinas/`. Corrija subindo dois níveis:

```bash
rm programa
ln -s ../../disciplinas/fundamentos_de_programacao.txt programa
ls -l
cat programa
```

Agora funciona. Faça o mesmo para o professor:

```bash
ln -s ../../professores/joao_marcelo_uchoa_de_alencar.txt professor
ls -l
```

Teste a propriedade que realmente importa — o *link* precisa sobreviver a uma
mudança de lugar da árvore inteira:

```bash
cd ~/scripts/aula03
cp -r meucurso /tmp/teste_links
cat /tmp/teste_links/historico/fundamentos_de_programacao/programa
```

### ✅ Checkpoint 2

✔ `cat programa` imprime `QXD0001` dentro de `~/scripts/aula03/meucurso`.
✔ `cat /tmp/teste_links/historico/fundamentos_de_programacao/programa` **também**
imprime `QXD0001`.

Se o segundo falhou, seu *link* usa caminho absoluto. Refaça com `../../`.

### ❓ Pergunta

Um *link* com caminho absoluto (`/home/aluno/scripts/...`) funciona perfeitamente
na sua conta. Por que ele quebra quando o professor copia a sua pasta para
corrigir?

---

## 🧩 Etapa 3 — Permissões

### Ação

Toda entrada do `ls -l` começa com dez caracteres:

```
-rw-rw-r-- 1 aluno aluno 8 ago 18 08:30 atalho.txt
```

- Posição 1: tipo (`-` arquivo, `d` diretório, `l` *link*).
- Posições 2–4: permissões do **dono** (*user*).
- Posições 5–7: permissões do **grupo** (*group*).
- Posições 8–10: permissões dos **outros** (*others*).

Cada trio é `r` (ler), `w` (escrever), `x` (executar).

Experimente a forma simbólica:

```bash
cd ~/scripts/aula03/meucurso
touch teste.txt
ls -l teste.txt

chmod u+x teste.txt      # adiciona execução para o dono
ls -l teste.txt

chmod go-r teste.txt     # remove leitura de grupo e outros
ls -l teste.txt

chmod a+r teste.txt      # devolve leitura para todos
ls -l teste.txt
```

E a forma octal, onde `r=4`, `w=2`, `x=1`:

```bash
chmod 644 teste.txt      # dono rw-, grupo r--, outros r--
ls -l teste.txt

chmod 700 teste.txt      # só o dono, e com tudo
ls -l teste.txt

chmod 755 teste.txt      # o padrão de um script executável
ls -l teste.txt
```

Veja na prática o que a falta de permissão faz:

```bash
chmod 000 teste.txt
cat teste.txt
chmod 644 teste.txt
cat teste.txt
```

### ✅ Checkpoint 3

✔ `chmod 000` faz o `cat` responder `Permissão negada`.
✔ Depois do `chmod 644`, o `ls -l` mostra `-rw-r--r--`.

### ❓ Pergunta

Na Aula 01 usamos `chmod 600` na chave SSH e `chmod 700` no diretório `~/.ssh`.
Traduza esses dois números para `rwx` e explique por que o `ssh` exige justamente
esses valores.

---

## 🧩 Etapa 4 — Procurando por nome e por conteúdo

### Ação — `find` procura por **nome**

```bash
cd ~/scripts/aula03/meucurso

find . -name "*.txt"                 # todos os .txt, em qualquer profundidade
find . -name "fundamentos*"          # começando com "fundamentos"
find . -type d                       # só diretórios
find . -type l                       # só links simbólicos
find . -type f -name "*.txt" | wc -l # quantos arquivos .txt existem
```

> ⚠️ As aspas em `"*.txt"` são obrigatórias. Sem elas, o *shell* expande o `*`
> antes de o `find` receber o argumento, e o resultado muda.

### Ação — `grep` procura por **conteúdo**

```bash
grep "QXD0001" disciplinas/fundamentos_de_programacao.txt
grep -r "QXD0001" .                  # recursivo, em toda a árvore
grep -r -l "QXD0001" .               # só o nome dos arquivos que casam
grep -i "qxd0001" disciplinas/*      # ignorando maiúsculas e minúsculas
grep -c "QXD" disciplinas/*          # contando as ocorrências
```

### Ação — `basename` e `dirname`

```bash
CAMINHO=/home/aluno/scripts/aula03/meucurso/disciplinas/fundamentos_de_programacao.txt
basename $CAMINHO
dirname  $CAMINHO
basename $CAMINHO .txt
```

Saída:

```
fundamentos_de_programacao.txt
/home/aluno/scripts/aula03/meucurso/disciplinas
fundamentos_de_programacao
```

### ✅ Checkpoint 4

✔ `find . -type l` lista os dois *links* que você criou na Etapa 2.
✔ `grep -r -l "QXD0001" .` lista pelo menos o arquivo da disciplina.

### ❓ Pergunta

O `grep -r "QXD0001" .` encontrou o texto também através do *link* `programa`?
Rode e confira. O que isso diz sobre como o `grep` trata ligações simbólicas?

---

## 🏁 Entrega da Aula — 1,0 ponto (Nota 1)

Individualmente, nos últimos 25 minutos.

Complete o `historico/` do seu `~/scripts/aula03/meucurso`:

1. Para **cada disciplina que você já foi aprovado**, crie um diretório dentro de
   `historico/` com o mesmo nome do arquivo da disciplina, **sem** a extensão
   `.txt`. Mínimo de **4 disciplinas**.
2. Dentro de cada um desses diretórios, crie dois *links* simbólicos:
   - `programa` → o arquivo correspondente em `disciplinas/`
   - `professor` → o arquivo do professor que ministrou, em `professores/`
3. Os *links* devem usar **caminho relativo** e continuar válidos se a pasta
   `meucurso` for copiada para outro lugar.

Estrutura esperada:

```
meucurso/
├── disciplinas/
│   └── fundamentos_de_programacao.txt
├── professores/
│   └── joao_marcelo_uchoa_de_alencar.txt
└── historico/
    └── fundamentos_de_programacao/
        ├── professor -> ../../professores/joao_marcelo_uchoa_de_alencar.txt
        └── programa  -> ../../disciplinas/fundamentos_de_programacao.txt
```

### Critérios de correção

| # | Critério | Valor |
|---|---|---|
| 1 | Existem pelo menos 4 diretórios em `historico/` | 0,2 |
| 2 | Cada um tem os *links* `programa` e `professor` | 0,3 |
| 3 | Os *links* apontam para arquivos que existem | 0,2 |
| 4 | Os *links* continuam válidos depois de copiar a árvore | 0,3 |

O professor corrige copiando a sua árvore para outro lugar e lendo os *links* de lá:

```bash
cp -r ~/scripts/aula03/meucurso /tmp/correcao_$USER
find /tmp/correcao_$USER/historico -type l -exec cat {} \;
```

Se algum *link* estiver quebrado, o `cat` acusa `Arquivo ou diretório inexistente`
e o critério 4 é perdido.

---

## ✅ Checklist de Encerramento

| # | Verificação | Comando |
|---|---|---|
| 1 | Os *links* existem | `find ~/scripts/aula03/meucurso -type l` |
| 2 | Nenhum *link* está quebrado | `find ~/scripts/aula03/meucurso -type l ! -exec test -e {} \; -print` |
| 3 | A árvore sobrevive a uma cópia | `cp -r ~/scripts/aula03/meucurso /tmp/t && cat /tmp/t/historico/*/programa` |

O comando 2 imprime **apenas os links quebrados**. Se não imprimir nada, está tudo certo.

---

## 💬 Para Discutir em Sala

- Por que o Linux permite que um *link* aponte para um arquivo que não existe, em
  vez de recusar a criação?
- O `find` procura por nome e o `grep` por conteúdo. Como você faria para procurar
  arquivos que tenham *ao mesmo tempo* um nome específico e um conteúdo específico?

## 📌 Para a Próxima Aula

Na **Aula 04** entramos em expressões regulares (`slides/03_expressoes_regulares`)
e o `grep` deixa de procurar texto literal para procurar **padrões**.
