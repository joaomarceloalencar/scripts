# 🧪 Aula 02 — Navegação e Manipulação de Arquivos

**Disciplina:** Programação de *Scripts* — UFC Quixadá
**Material de apoio:** `slides/02_comandos_basicos` (parte 1)
**Sessão:** Semana 1 — quarta, 12/08
**Entrega desta aula:** 1,0 ponto (Nota 1)
**Duração estimada:** 100 minutos

---

## 🎯 Objetivos da Aula

Ao final desta aula você deve ser capaz de:

- Localizar-se na árvore de diretórios com `pwd`, `cd` e `ls`.
- Distinguir **caminho absoluto** de **caminho relativo**.
- Criar, copiar, mover e remover arquivos e diretórios.
- Criar vários arquivos ou diretórios de uma vez, sem repetir comandos.
- Inspecionar arquivos com `file`, `cat`, `head`, `tail` e `wc`.

## 🧰 Pré-requisitos

- A [Aula 01](01_primeiro_script.md) concluída: `ssh disciplina` funcionando.

## 🗺️ Roteiro

| Etapa | Assunto | Tempo |
|---|---|---|
| 0 | Onde eu estou | 10 min |
| 1 | Caminhos absolutos e relativos | 15 min |
| 2 | Criando estrutura sem repetir comandos | 20 min |
| 3 | Copiar, mover, renomear | 15 min |
| 4 | Olhando dentro dos arquivos | 15 min |
| 🏁 | Entrega | 25 min |

Toda a aula acontece **no servidor**. Comece por:

```bash
ssh disciplina
mkdir -p ~/scripts/aula02
cd ~/scripts/aula02
```

---

## 🧩 Etapa 0 — Onde eu estou

### Ação

```bash
pwd                 # caminho completo do diretório atual
ls                  # o que tem aqui
ls -l               # com detalhes: permissões, dono, tamanho, data
ls -la              # inclui os arquivos ocultos (começam com .)
ls -lh              # tamanhos legíveis: 4,0K em vez de 4096
```

Repare na saída do `ls -la`:

```
drwxrwxr-x  2 aluno aluno 4096 ago 12 08:15 .
drwxrwxr-x  4 aluno aluno 4096 ago 12 08:15 ..
```

O `.` é o diretório atual e o `..` é o diretório acima. Eles existem em **todo**
diretório do sistema.

### ✅ Checkpoint 0

✔ `pwd` mostra um caminho terminando em `/scripts/aula02`.
✔ `ls -la` mostra as entradas `.` e `..`.

### ❓ Pergunta

O `ls` sozinho não mostrou nada, mas o `ls -la` mostrou duas entradas. O diretório
está vazio ou não está?

---

## 🧩 Etapa 1 — Caminhos absolutos e relativos

### Ação

Um caminho que começa com `/` é **absoluto**: parte da raiz do sistema e funciona
de qualquer lugar. Qualquer outro é **relativo**: parte de onde você está.

```bash
cd /etc              # absoluto
pwd
ls | head -5

cd /                 # a raiz do sistema
ls

cd ~                 # atalho para o seu diretório pessoal
pwd

cd scripts/aula02    # relativo: a partir de onde estou
pwd
```

Agora os atalhos de navegação:

```bash
cd ..                # sobe um nível
pwd
cd ..                # sobe mais um
pwd
cd -                 # volta para o diretório anterior
pwd
```

### ✅ Checkpoint 1

Partindo de `~/scripts/aula02`, chegue em `/etc` usando **apenas caminhos
relativos** (só `..` e nomes de diretório, sem `/` no início e sem `~`).

✔ `pwd` deve responder `/etc`.

### ❓ Pergunta

O comando `cd ../../..` a partir de `/home/aluno/scripts` leva a qual diretório?
E se você repetir `cd ..` mais cinco vezes depois disso, o que acontece?

---

## 🧩 Etapa 2 — Criando estrutura sem repetir comandos

Vamos montar uma estrutura de diretórios. Volte para a área da aula:

```bash
cd ~/scripts/aula02
```

### Ação — um de cada vez

```bash
mkdir universidade
cd universidade
mkdir professores
mkdir disciplinas
ls
cd ..
```

Funciona, mas é trabalhoso. O `mkdir` aceita vários nomes de uma vez:

```bash
mkdir universidade/historico universidade/notas
ls universidade
```

E a opção `-p` cria a árvore inteira, incluindo os diretórios intermediários que
ainda não existem:

```bash
mkdir -p campus/quixada/computacao/2026
ls -R campus
```

> 💡 O `-p` também serve para **não dar erro** se o diretório já existir. Por isso
> usamos `mkdir -p ~/scripts/aulaNN` no começo de toda aula.

### Ação — expansão de chaves

O *shell* consegue gerar listas de nomes antes de executar o comando. Veja primeiro
o que ele produz, sem criar nada:

```bash
echo dir{1,2,3}
echo dir{1..5}
echo arq{1..3}.txt
```

Saída:

```
dir1 dir2 dir3
dir1 dir2 dir3 dir4 dir5
arq1.txt arq2.txt arq3.txt
```

O *shell* expandiu as chaves **antes** de chamar o `echo`. Isso vale para qualquer
comando:

```bash
mkdir -p universidade/dir{1..5}
ls universidade
touch universidade/dir1/arq{1..4}.txt
ls universidade/dir1
```

### ✅ Checkpoint 2

✔ `ls universidade` mostra `dir1` até `dir5`, além de `professores`, `disciplinas`,
`historico` e `notas`.
✔ `ls universidade/dir1` mostra `arq1.txt` até `arq4.txt`.
✔ Você criou os 4 arquivos com **um** comando `touch`, não quatro.

### ❓ Pergunta

Compare `mkdir dir{1..3}` com `mkdir -p dir1/dir2/dir3`. Os dois criam três
diretórios — qual a diferença no resultado?

---

## 🧩 Etapa 3 — Copiar, mover, renomear

### Ação

```bash
cd ~/scripts/aula02
touch original.txt
cp original.txt copia.txt
ls
```

Para diretórios, é preciso `-r` (*recursive*):

```bash
cp universidade backup          # dá erro
cp -r universidade backup       # funciona
ls backup
```

O `mv` faz duas coisas com o mesmo comando — mover e renomear:

```bash
mv copia.txt renomeado.txt      # renomeia (mesmo diretório)
ls

mv renomeado.txt universidade/  # move (outro diretório)
ls
ls universidade
```

Remover:

```bash
rm original.txt
rmdir campus                    # dá erro: não está vazio
rmdir campus/quixada/computacao/2026
rm -r campus                    # remove a árvore inteira
ls
```

> ⚠️ **Não existe lixeira no terminal.** O `rm -r` apaga em silêncio e de vez.
> Antes de rodar um `rm -r`, rode o mesmo caminho com `ls -R` e confirme que é
> aquilo mesmo que você quer perder.

### ✅ Checkpoint 3

✔ `ls` no diretório da aula mostra `universidade` e `backup`, e **não** mostra
`campus`, `original.txt` nem `copia.txt`.
✔ `ls universidade` inclui `renomeado.txt`.

### ❓ Pergunta

O `cp` precisou de `-r` para diretórios, mas o `mv` não precisou. Por quê? (Dica:
pense no que cada um faz com os arquivos que estão dentro.)

---

## 🧩 Etapa 4 — Olhando dentro dos arquivos

### Ação

Precisamos de um arquivo com conteúdo de verdade:

```bash
cd ~/scripts/aula02
cp /etc/passwd usuarios.txt
```

Agora inspecione:

```bash
file usuarios.txt      # que tipo de arquivo é
wc -l usuarios.txt     # quantas linhas
wc -c usuarios.txt     # quantos bytes
wc usuarios.txt        # linhas, palavras e bytes
```

Ver o conteúdo:

```bash
cat usuarios.txt       # tudo de uma vez
head usuarios.txt      # as 10 primeiras linhas
head -3 usuarios.txt   # as 3 primeiras
tail -3 usuarios.txt   # as 3 últimas
```

Para arquivos grandes, o `cat` rola a tela toda. Use o paginador:

```bash
less usuarios.txt      # navegue com as setas, saia com q
```

Compare os tipos:

```bash
file usuarios.txt
file universidade
file /bin/ls
file ~/scripts/aula01/usuarios.sh
```

### ✅ Checkpoint 4

✔ `wc -l usuarios.txt` responde um número maior que zero.
✔ `file universidade` responde `directory`.
✔ `file /bin/ls` menciona `ELF` e `executable`.

### ❓ Pergunta

O `file` respondeu coisas diferentes para `usuarios.txt`, `universidade` e
`/bin/ls`. Como ele descobre isso, se a extensão do nome não é usada no Linux?

---

## 🏁 Entrega da Aula — 1,0 ponto (Nota 1)

Individualmente, nos últimos 25 minutos.

No servidor, dentro de `~/scripts/aula02`, monte a estrutura abaixo — que vamos
continuar usando na próxima aula:

```
meucurso/
├── disciplinas/
│   ├── fundamentos_de_programacao.txt
│   ├── ... (uma para cada disciplina obrigatória do seu curso)
├── professores/
│   ├── joao_marcelo_uchoa_de_alencar.txt
│   ├── ... (um para cada professor que você já teve)
└── historico/
```

Regras:

1. Consulte a grade do seu curso em <http://www.quixada.ufc.br> e crie **um arquivo
   vazio por disciplina obrigatória** em `disciplinas/`.
2. Crie **um arquivo vazio por professor** que você já teve, em `professores/`.
3. Os nomes seguem o padrão: tudo **minúsculo**, **sem acento**, espaços trocados
   por `_`, extensão `.txt`. Exemplo: *Fundamentos de Programação* vira
   `fundamentos_de_programacao.txt`.
4. O diretório `historico/` fica vazio por enquanto.
5. Os arquivos podem ficar vazios — o que importa são os nomes.

### Critérios de correção

| # | Critério | Valor |
|---|---|---|
| 1 | Os três subdiretórios existem com os nomes exatos | 0,2 |
| 2 | `disciplinas/` tem um arquivo por disciplina obrigatória | 0,3 |
| 3 | `professores/` tem pelo menos 5 arquivos | 0,2 |
| 4 | Todos os nomes seguem o padrão (minúsculo, sem acento, `_`, `.txt`) | 0,3 |

Correção:

```bash
cd ~/scripts/aula02/meucurso && ls -R
```

> 💡 **Vale a pena pensar antes de digitar.** Dá para criar tudo isso com poucos
> comandos, usando expansão de chaves e `touch` com vários argumentos. Quem criar
> arquivo por arquivo vai terminar, mas vai gastar o tempo todo.

---

## ✅ Checklist de Encerramento

| # | Verificação | Comando |
|---|---|---|
| 1 | A estrutura da entrega existe | `ls -R ~/scripts/aula02/meucurso` |
| 2 | Não sobrou nome com maiúscula ou acento | `ls ~/scripts/aula02/meucurso/disciplinas` |
| 3 | O `historico` existe e está vazio | `ls -la ~/scripts/aula02/meucurso/historico` |

---

## 💬 Para Discutir em Sala

- Você criou os arquivos com `touch`, um por um, ou usou expansão? Quanto tempo
  cada abordagem levou?
- O padrão de nome (minúsculo, sem acento, `_` no lugar de espaço) parece
  frescura. Que problema concreto ele evita na linha de comando?

## 📌 Para a Próxima Aula

Na **Aula 03** vamos completar o capítulo `02_comandos_basicos`: permissões,
ligações simbólicas (`ln`) e busca (`find`, `grep`). O diretório `meucurso` que
você acabou de criar é o ponto de partida — **não apague**.
