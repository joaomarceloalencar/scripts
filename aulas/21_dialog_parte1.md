# 🧪 Aula 21 — `dialog` (parte 1): As Caixas

**Disciplina:** Programação de *Scripts* — UFC Quixadá
**Material de apoio:** `slides/18_dialog`
**Sessão:** Semana 12 — terça, 27/10
**Entrega desta aula:** 0,7 ponto (Nota 3)
**Duração estimada:** 100 minutos

---

## 🎯 Objetivos da Aula

Ao final desta aula você deve ser capaz de:

- Exibir as caixas básicas do `dialog`: mensagem, confirmação, entrada e menu.
- Capturar a resposta do usuário com `--stdout`.
- Interpretar o código de retorno para tratar Cancelar e Esc.
- Encadear caixas em um fluxo com estado.

## 🧰 Pré-requisitos

- Aulas 11 (`read`, `tput`) e 13 (funções). Terminal com pelo menos 24×80.

## 🗺️ Roteiro

| Etapa | Assunto | Tempo |
|---|---|---|
| 0 | A primeira caixa | 15 min |
| 1 | Capturando a resposta | 20 min |
| 2 | Códigos de retorno | 20 min |
| 3 | Menus e listas | 20 min |
| 🏁 | Entrega | 25 min |

---

## 🧩 Etapa 0 — A primeira caixa

### Ação

```bash
ssh disciplina
mkdir -p ~/scripts/aula21
cd ~/scripts/aula21

command -v dialog || sudo apt install -y dialog
dialog --version
```

A caixa mais simples:

```bash
dialog --msgbox "Olá, Programação de Scripts!" 8 50
```

Os dois números no fim são **obrigatórios**: altura e largura, em caracteres. Todo
comando do `dialog` termina com eles.

```bash
dialog --title "Aviso" --msgbox "Uma caixa com título." 8 50
dialog --msgbox "Uma caixa maior." 15 70
dialog --msgbox "Muito pequena para este texto tão longo que não cabe." 5 20
```

A última fica cortada — o `dialog` não quebra o texto sozinho para caber.

As caixas que vamos usar hoje:

| Caixa | Para quê |
|---|---|
| `--msgbox` | mostrar uma mensagem (botão OK) |
| `--yesno` | perguntar sim ou não |
| `--inputbox` | pedir um texto |
| `--passwordbox` | pedir um texto sem ecoar |
| `--menu` | escolher **uma** opção |
| `--checklist` | escolher **várias** |
| `--radiolist` | escolher uma, com marcador |
| `--infobox` | mostrar sem esperar (não bloqueia) |

Experimente a diferença entre `--msgbox` e `--infobox`:

```bash
dialog --infobox "Isto some sozinho em 2 segundos..." 5 50; sleep 2
dialog --msgbox "Isto espera você apertar OK." 5 50
```

### ✅ Checkpoint 0

✔ As caixas aparecem centralizadas, em azul.
✔ Você viu o texto ser cortado ao passar uma caixa pequena demais.
✔ Entendeu que `--infobox` não bloqueia e `--msgbox` bloqueia.

### ❓ Pergunta

Rode `dialog --msgbox "teste" 8 40 > saida.txt` e depois `cat saida.txt`. O arquivo
está vazio? Onde a caixa foi desenhada, então?

---

## 🧩 Etapa 1 — Capturando a resposta

Aqui está a parte que confunde todo mundo na primeira vez.

### Ação

```bash
dialog --inputbox "Qual seu nome?" 8 50
```

O texto digitado apareceu **no terminal**, mas você não consegue capturá-lo com
`$( )` do jeito óbvio:

```bash
NOME=$(dialog --inputbox "Qual seu nome?" 8 50)
echo "[$NOME]"
```

Vazio. O `dialog` desenha a interface no `stdout` e devolve a resposta no `stderr`.
Existem duas soluções:

```bash
# Solução 1: --stdout (a mais limpa)
NOME=$(dialog --stdout --inputbox "Qual seu nome?" 8 50)
echo "[$NOME]"

# Solução 2: trocar os canais (aparece em material antigo)
NOME=$(dialog --inputbox "Qual seu nome?" 8 50 3>&1 1>&2 2>&3)
echo "[$NOME]"
```

> 💡 **Use sempre `--stdout`.** A construção `3>&1 1>&2 2>&3` faz a mesma coisa —
> cria o descritor 3, joga o `stdout` nele, o `stderr` no `stdout` e vice-versa —
> mas é ilegível.

Com valor inicial e senha:

```bash
NOME=$(dialog --stdout --inputbox "Nome:" 8 50 "João")
echo "[$NOME]"

SENHA=$(dialog --stdout --passwordbox "Senha:" 8 50)
echo "tamanho: ${#SENHA}"
```

Limpe a tela ao final — o `dialog` deixa resíduo:

```bash
clear
```

### ✅ Checkpoint 1

✔ Sem `--stdout`, a variável fica vazia.
✔ Com `--stdout`, ela recebe o texto digitado.
✔ O `--passwordbox` não mostra os caracteres.

### ❓ Pergunta

Por que o `dialog` foi projetado para escrever a resposta no `stderr`, e não no
`stdout`? (Dica: pense em qual canal ele precisa para desenhar a tela.)

---

## 🧩 Etapa 2 — Códigos de retorno

Toda caixa devolve um código que diz **qual botão** o usuário apertou.

| Código | Botão |
|---|---|
| 0 | OK / Sim |
| 1 | Cancelar / Não |
| 2 | Ajuda |
| 3 | Extra |
| 255 | Esc ou erro |

### Ação

```bash
dialog --yesno "Você quer continuar?" 8 50
echo "retorno: $?"
```

Rode três vezes: apertando Sim, Não e Esc. Compare os códigos.

O padrão correto de uso captura resposta **e** código:

```bash
cat > entrada.sh
#!/bin/bash

NOME=$(dialog --stdout --title "Cadastro" --inputbox "Qual seu nome?" 8 50)
CODIGO=$?

clear

case "$CODIGO" in
    0)
        if [ -z "$NOME" ]; then
            echo "Você apertou OK mas não digitou nada."
            exit 1
        fi
        echo "Bem-vindo, $NOME!"
        ;;
    1)  echo "Operação cancelada pelo usuário."; exit 1 ;;
    255) echo "Cancelado com Esc."; exit 1 ;;
esac
```

Ctrl+D, `chmod +x entrada.sh`, e teste os três caminhos:

```bash
./entrada.sh; echo "saída: $?"
```

> ⚠️ **A captura do `$?` tem que ser a linha seguinte.** Qualquer comando no meio —
> inclusive um `echo` — sobrescreve o valor. Se precisar de mais de um uso, guarde
> em variável imediatamente, como acima.
>
> ⚠️ **OK com campo vazio devolve 0**, não 1. Validar o conteúdo é responsabilidade
> sua, como no `if -z` acima.

### ✅ Checkpoint 2

✔ Sim devolve `0`, Não devolve `1`, Esc devolve `255`.
✔ O `entrada.sh` trata os três casos.
✔ OK com o campo vazio é detectado.

### ❓ Pergunta

O código `255` cobre tanto "usuário apertou Esc" quanto "houve um erro". Isso é um
problema? Como você distinguiria os dois casos?

---

## 🧩 Etapa 3 — Menus e listas

### Ação — `--menu`

O `--menu` recebe, além de altura e largura, a **altura da lista** e depois pares de
`tag` e `descrição`:

```bash
OPCAO=$(dialog --stdout --title "Menu principal" \
    --menu "Escolha uma opção:" 15 50 4 \
    1 "Ver data e hora" \
    2 "Ver uso de disco" \
    3 "Ver usuários logados" \
    4 "Sair")
echo "escolheu: [$OPCAO]"
```

O valor devolvido é a **tag**, não a descrição.

### Ação — `--checklist`

Cada item leva um terceiro campo: `on` ou `off`, o estado inicial.

```bash
ITENS=$(dialog --stdout --title "Pacotes" \
    --checklist "Marque com ESPAÇO:" 15 50 4 \
    vim    "Editor de texto"   on \
    git    "Controle de versão" on \
    tmux   "Multiplexador"     off \
    htop   "Monitor"           off)
echo "marcados: [$ITENS]"
```

O resultado vem como uma lista separada por espaço: `"vim" "git"`. Para percorrê-la:

```bash
for i in $ITENS; do echo "- $i"; done
```

> ⚠️ As aspas vêm **dentro** do resultado. Se um item tiver espaço no nome, isso
> quebra. O `--separate-output` resolve, devolvendo um item por linha:
>
> ```bash
> ITENS=$(dialog --stdout --separate-output --checklist "..." 15 50 4 ...)
> while read -r i; do echo "- $i"; done <<< "$ITENS"
> ```

### Ação — `--radiolist` e `--gauge`

```bash
DISTRO=$(dialog --stdout --radiolist "Escolha uma:" 15 50 3 \
    ubuntu "Ubuntu"  on \
    debian "Debian"  off \
    fedora "Fedora"  off)
echo "[$DISTRO]"
```

A barra de progresso lê os percentuais da entrada padrão:

```bash
for i in $(seq 0 10 100); do
    echo "$i"
    sleep 0.2
done | dialog --gauge "Processando..." 8 50 0
clear
```

### Ação — construindo a lista dinamicamente

Um menu com nomes fixos serve para pouca coisa. Monte a partir do sistema:

```bash
cat > escolhe_arquivo.sh
#!/bin/bash
DIR="${1:-.}"
OPCOES=()
i=1
for arq in "$DIR"/*; do
    [ -f "$arq" ] || continue
    OPCOES+=("$i" "$(basename "$arq")")
    i=$(( i + 1 ))
done

if [ ${#OPCOES[@]} -eq 0 ]; then
    dialog --msgbox "Nenhum arquivo em $DIR" 8 50
    clear
    exit 1
fi

ESCOLHA=$(dialog --stdout --menu "Arquivos em $DIR:" 20 60 10 "${OPCOES[@]}")
clear
echo "tag escolhida: $ESCOLHA"
```

Ctrl+D, `chmod +x escolhe_arquivo.sh`, e:

```bash
./escolhe_arquivo.sh ~/scripts/aula21
./escolhe_arquivo.sh /etc
```

O `"${OPCOES[@]}"` expande o vetor (Aula 12) como argumentos separados — é o que
permite montar a lista em tempo de execução.

### ✅ Checkpoint 3

✔ O `--menu` devolve a tag escolhida.
✔ O `--checklist` devolve os itens marcados.
✔ O `escolhe_arquivo.sh` monta o menu com os arquivos reais do diretório.

### ❓ Pergunta

O `--menu` devolve a *tag*, não a descrição. Por que isso é uma boa decisão de
projeto?

---

## 🏁 Entrega da Aula — 0,7 ponto (Nota 3)

Individualmente, nos últimos 25 minutos.

Crie o *script* `~/scripts/aula21/cantina.sh`, um autoatendimento para a cantina.

O fluxo, em sequência de caixas:

1. **Identificação** — `--inputbox` pedindo o nome do cliente.
   - Cancelar, Esc **ou nome vazio** encerram o *script* com uma mensagem de erro e
     retorno `1`.
2. **Prato principal** — `--menu` com escolha única: Hambúrguer, Pizza, Pastel.
3. **Adicionais** — `--checklist` onde o usuário marca zero ou mais: Refrigerante,
   Suco, Batata Frita, Molho Extra.
4. **Confirmação** — `--yesno` perguntando "O seu pedido está correto?".
   - **Não** → `--msgbox` "Pedido cancelado" e sai com retorno `1`.
   - **Sim** → segue.
5. **Recibo** — `--msgbox` com o resumo: nome do cliente, prato escolhido e a lista
   de adicionais (ou "nenhum", se não marcou nada).

Requisitos:

- Use `--stdout` em todas as caixas.
- Trate o código de retorno (`$?`) em **pelo menos** as etapas 1 e 4.
- Limpe a tela (`clear`) antes de qualquer saída do *script*.

### Critérios de correção

| # | Critério | Valor |
|---|---|---|
| 1 | As cinco caixas aparecem na ordem correta | 0,20 |
| 2 | Usa `--stdout` e captura as respostas | 0,10 |
| 3 | Cancelar/Esc/vazio na etapa 1 encerra com retorno 1 | 0,15 |
| 4 | "Não" na confirmação cancela o pedido | 0,10 |
| 5 | O recibo mostra os três dados, tratando "nenhum adicional" | 0,15 |

Correção: o professor executa três vezes — o fluxo completo, cancelando na primeira
caixa, e respondendo "Não" na confirmação.

```bash
cd ~/scripts/aula21 && ./cantina.sh; echo "retorno=$?"
grep -c "stdout" cantina.sh
```

---

## ✅ Checklist de Encerramento

| # | Verificação | Comando |
|---|---|---|
| 1 | O *script* é executável | `ls -l cantina.sh` |
| 2 | Usa `--stdout` em todas as caixas | `grep -c "\-\-stdout" cantina.sh` |
| 3 | Trata `$?` | `grep -c "\$?" cantina.sh` |
| 4 | Limpa a tela ao sair | `grep -c clear cantina.sh` |
| 5 | O terminal está limpo depois de rodar | visual |

O item 2 deve responder pelo menos `4`.

---

## 💬 Para Discutir em Sala

- O `dialog` desenha janelas em modo texto e existe desde os anos 90. Por que ele
  ainda é usado em instaladores de sistema hoje?
- Comparado com o menu que você fez com `tput` na Aula 11, o `dialog` é mais bonito
  mas tem um custo. Qual?

## 📌 Para a Próxima Aula

Na **Aula 22** completamos o `dialog`: formulários, seleção de arquivos, `--gauge`
com processo real e a construção de um fluxo com navegação para trás.
