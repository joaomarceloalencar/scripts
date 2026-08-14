# 🧪 Aula 05 — Redirecionamento e *Pipes*

**Disciplina:** Programação de *Scripts* — UFC Quixadá
**Material de apoio:** `slides/04_redirecionamento_de_saida`
**Sessão:** Semana 3 — terça, 25/08
**Entrega desta aula:** 1,0 ponto (Nota 1)
**Duração estimada:** 100 minutos

---

## 🎯 Objetivos da Aula

Ao final desta aula você deve ser capaz de:

- Explicar o que são os três descritores padrão: `stdin`, `stdout` e `stderr`.
- Redirecionar saída com `>` e `>>`, e entrada com `<`.
- Separar mensagens de erro da saída normal com `2>`.
- Encadear comandos com `|` e usar `tee` para gravar no meio do caminho.
- Incorporar o resultado de um comando dentro de outro com `$( )`.

## 🧰 Pré-requisitos

- Aulas 01 a 04 concluídas.

## 🗺️ Roteiro

| Etapa | Assunto | Tempo |
|---|---|---|
| 0 | Os três descritores | 10 min |
| 1 | Saída: `>` e `>>` | 15 min |
| 2 | Erro: `2>` e `2>&1` | 20 min |
| 3 | Entrada: `<` | 10 min |
| 4 | *Pipes* e `tee` | 15 min |
| 5 | Substituição de comandos | 10 min |
| 🏁 | Entrega | 20 min |

---

## 🧩 Etapa 0 — Os três descritores

Todo processo no Linux nasce com três canais abertos:

| Número | Nome | Papel | Padrão |
|---|---|---|---|
| 0 | `stdin` | entrada | teclado |
| 1 | `stdout` | saída normal | tela |
| 2 | `stderr` | saída de erro | tela |

Como 1 e 2 vão os dois para a tela, eles **parecem** o mesmo canal. Não são.

### Ação

```bash
ssh disciplina
mkdir -p ~/scripts/aula05
cd ~/scripts/aula05

ls /etc /naoexiste
```

A saída mistura as duas coisas:

```
ls: não foi possível acessar '/naoexiste': Arquivo ou diretório inexistente
/etc:
adduser.conf
...
```

### ✅ Checkpoint 0

✔ O comando imprimiu **as duas coisas**: o erro e a listagem de `/etc`.

### ❓ Pergunta

Se os dois textos apareceram juntos na tela, como o sistema sabe qual é qual?

---

## 🧩 Etapa 1 — Saída: `>` e `>>`

### Ação

O `>` grava a saída em um arquivo, **destruindo** o conteúdo anterior:

```bash
ls /etc > listagem.txt
wc -l listagem.txt

ls /var > listagem.txt
wc -l listagem.txt
```

O segundo `wc -l` mostra um número diferente: o conteúdo do `/etc` foi perdido.

O `>>` **acrescenta** ao final:

```bash
ls /etc >> listagem.txt
wc -l listagem.txt
```

Agora o arquivo tem as duas listagens.

Um caso especial que aparece muito: esvaziar um arquivo sem apagá-lo.

```bash
> listagem.txt
wc -l listagem.txt
ls -l listagem.txt
```

O arquivo continua existindo, com zero bytes.

### ✅ Checkpoint 1

✔ Depois do `>>`, o `wc -l` cresceu.
✔ Depois do `>` sozinho, `wc -l` responde `0` e o arquivo ainda existe.

### ❓ Pergunta

Por que este comando esvazia o arquivo em vez de duplicá-lo?

```bash
sort arquivo.txt > arquivo.txt
```

---

## 🧩 Etapa 2 — Erro: `2>` e `2>&1`

### Ação

Volte ao comando misturado e separe os canais:

```bash
ls /etc /naoexiste > saida.txt
```

O erro continuou aparecendo na tela — porque `>` redireciona apenas o canal 1.
A listagem foi para o arquivo:

```bash
head -3 saida.txt
```

Agora redirecione o canal 2:

```bash
ls /etc /naoexiste 2> erro.txt
cat erro.txt
```

Dessa vez a listagem apareceu na tela e o erro foi para o arquivo.

Para separar os dois em arquivos diferentes:

```bash
ls /etc /naoexiste > saida.txt 2> erro.txt
wc -l saida.txt erro.txt
```

Para juntar os dois no **mesmo** arquivo:

```bash
ls /etc /naoexiste > tudo.txt 2>&1
wc -l tudo.txt
```

A notação `2>&1` significa "mande o canal 2 para onde o canal 1 já está apontando".

> ⚠️ A **ordem importa**. Compare:
>
> ```bash
> ls /naoexiste > a.txt 2>&1     # erro vai para a.txt
> ls /naoexiste 2>&1 > b.txt     # erro vai para a TELA
> ```
>
> No segundo caso, o `2>&1` foi processado quando o canal 1 ainda era a tela.

E o descarte universal:

```bash
ls /etc /naoexiste 2> /dev/null
ls /etc /naoexiste > /dev/null 2>&1
```

O `/dev/null` é um arquivo especial que aceita tudo e não guarda nada.

### ✅ Checkpoint 2

✔ `wc -l erro.txt` responde `1` e `wc -l saida.txt` responde muito mais.
✔ `ls /etc /naoexiste 2> /dev/null` mostra só a listagem, sem o erro.
✔ Você conferiu que `2>&1 > b.txt` deixa o erro na tela.

### ❓ Pergunta

Por que existe um canal separado só para erros? Que problema apareceria se tudo
saísse pelo canal 1?

---

## 🧩 Etapa 3 — Entrada: `<`

### Ação

Muitos comandos leem de um arquivo passado como argumento:

```bash
wc -l /etc/passwd
```

Mas também leem da entrada padrão, se ela for redirecionada:

```bash
wc -l < /etc/passwd
```

O resultado é quase o mesmo — com uma diferença reveladora:

```bash
wc -l /etc/passwd
wc -l < /etc/passwd
```

```
40 /etc/passwd
40
```

No primeiro caso o `wc` **sabe** o nome do arquivo e o imprime. No segundo ele
recebeu apenas um fluxo de bytes, sem nome.

O `sort` é outro que aceita as duas formas:

```bash
sort < /etc/passwd | head -3
```

### ✅ Checkpoint 3

✔ `wc -l /etc/passwd` imprime o número **e** o nome.
✔ `wc -l < /etc/passwd` imprime só o número.

### ❓ Pergunta

Se `comando < arquivo` e `comando arquivo` dão quase o mesmo resultado, para que
serve o `<`? (Dica: nem todo comando aceita nome de arquivo como argumento.)

---

## 🧩 Etapa 4 — *Pipes* e `tee`

### Ação

O `|` conecta a saída de um comando à entrada do próximo, sem passar por disco:

```bash
cat /etc/passwd | wc -l
cut -d: -f1 /etc/passwd | sort | head -5
cut -d: -f7 /etc/passwd | sort | uniq -c | sort -rn
```

Aquele último encadeamento responde "quantos usuários usam cada *shell*". Leia da
esquerda para a direita: recorta o campo 7, ordena, conta repetições, ordena pelo
número em ordem decrescente.

Às vezes você quer ver o resultado **e** guardá-lo. É o papel do `tee`:

```bash
cut -d: -f1 /etc/passwd | sort | tee usuarios.txt | wc -l
cat usuarios.txt | head -3
```

A saída do `sort` foi para o arquivo **e** seguiu adiante para o `wc -l`.

Cuidado com uma armadilha clássica:

```bash
grep "root" /etc/passwd | wc -l          # funciona
grep "root" /etc/passwd > res.txt | wc -l  # não funciona como esperado
```

No segundo, o `>` capturou a saída antes de o *pipe* recebê-la, e o `wc -l`
recebeu um fluxo vazio.

### ✅ Checkpoint 4

✔ `cut -d: -f7 /etc/passwd | sort | uniq -c | sort -rn` imprime uma contagem por *shell*.
✔ O `tee` criou `usuarios.txt` **e** o `wc -l` imprimiu o número.

### ❓ Pergunta

O `|` e o `>` parecem fazer coisas parecidas: os dois desviam a saída. Qual a
diferença essencial entre eles?

---

## 🧩 Etapa 5 — Substituição de comandos

### Ação

O `$( )` executa um comando e coloca a **saída dele** no lugar:

```bash
echo "Hoje é $(date)"
echo "A máquina é $(hostname)"
echo "Existem $(wc -l < /etc/passwd) usuários cadastrados"
```

Isso permite montar nomes de arquivo dinâmicos:

```bash
cp /etc/passwd backup_$(date +%Y%m%d).txt
ls -l backup_*
```

> 💡 A forma antiga usa crases: `` `date` ``. Funciona, mas não pode ser aninhada e
> é fácil de confundir com aspas simples. **Prefira sempre `$( )`.**

E lembra do `eval "$(ssh-agent -s)"` da Aula 01? Agora dá para entender: o
`ssh-agent -s` imprime comandos, o `$( )` captura esse texto e o `eval` o executa.

### ✅ Checkpoint 5

✔ `ls -l backup_*` mostra um arquivo com a data de hoje no nome.
✔ `echo "Existem $(wc -l < /etc/passwd) usuários"` imprime uma frase com o número
no meio.

### ❓ Pergunta

Qual a diferença entre estes dois comandos?

```bash
echo $(date)
echo "$(date)"
```

Rode os dois e compare com atenção os espaços.

---

## 🏁 Entrega da Aula — 1,0 ponto (Nota 1)

Individualmente, nos últimos 20 minutos.

Crie o *script* `~/scripts/aula05/relatorio.sh` que, ao ser executado, produza um
arquivo chamado `relatorio.txt` no diretório atual, contendo:

1. Uma primeira linha com a data e hora da geração, no formato
   `Relatório gerado em <data>`.
2. Uma linha com o nome da máquina, no formato `Máquina: <hostname>`.
3. Uma linha com o total de usuários do `/etc/passwd`, no formato
   `Usuários cadastrados: <número>`.
4. Em seguida, a lista dos nomes de usuário em ordem alfabética, um por linha.

Além disso:

5. Qualquer mensagem de erro produzida pelo *script* deve ir para `erros.log`, e
   **não** para a tela.
6. O *script* deve imprimir na tela apenas a frase `Relatório pronto.`

Exemplo de execução:

```
$ ./relatorio.sh
Relatório pronto.
$ head -4 relatorio.txt
Relatório gerado em qua 25 ago 2026 09:12:44 -03
Máquina: servidor
Usuários cadastrados: 40
_apt
```

### Critérios de correção

| # | Critério | Valor |
|---|---|---|
| 1 | O `relatorio.txt` é criado com as três linhas de cabeçalho corretas | 0,3 |
| 2 | A lista de usuários vem ordenada e completa | 0,2 |
| 3 | Usa `$( )` para inserir data, *hostname* e contagem | 0,2 |
| 4 | Erros vão para `erros.log` e não para a tela | 0,2 |
| 5 | Tem *shebang* e permissão de execução | 0,1 |

Correção:

```bash
cd ~/scripts/aula05 && rm -f relatorio.txt && ./relatorio.sh && head -4 relatorio.txt
```

> 💡 Repare no item 1 do cabeçalho *versus* item 4 da lista: o primeiro `>` cria o
> arquivo, e os seguintes precisam ser `>>` — senão cada linha apaga a anterior.

---

## ✅ Checklist de Encerramento

| # | Verificação | Comando |
|---|---|---|
| 1 | O *script* roda e imprime só uma frase | `./relatorio.sh` |
| 2 | O relatório tem cabeçalho e lista | `head -5 relatorio.txt` |
| 3 | O `erros.log` existe | `ls -l erros.log` |
| 4 | A lista está ordenada | `tail -n +4 relatorio.txt \| sort -c` |

O `sort -c` não imprime nada se a entrada já estiver ordenada, e reclama se não estiver.

---

## 💬 Para Discutir em Sala

- O encadeamento `cut | sort | uniq -c | sort -rn` resolve em uma linha algo que
  em outra linguagem levaria umas quinze. Onde está o limite dessa abordagem?
- Você redirecionou os erros para um arquivo. Em que situação isso é perigoso?

## 📌 Para a Próxima Aula

Na **Aula 06** vamos aos comandos avançados de manipulação de texto
(`slides/05_comandos_avancados`): `sed`, `cut`, `tr`, `uniq` e aritmética no *shell*.
