# 🧪 Aula 22 — `dialog` (parte 2): Fluxos Completos

**Disciplina:** Programação de *Scripts* — UFC Quixadá
**Material de apoio:** `slides/18_dialog`
**Sessão:** Semana 12 — quarta, 28/10
**Entrega desta aula:** 0,7 ponto (Nota 3)
**Duração estimada:** 100 minutos

---

## 🎯 Objetivos da Aula

Ao final desta aula você deve ser capaz de:

- Usar `--form`, `--fselect` e `--dselect`.
- Mostrar progresso real de uma tarefa com `--gauge`.
- Construir um fluxo com navegação para trás.
- Encapsular caixas em funções reaproveitáveis.
- Garantir que o terminal fique limpo em qualquer saída, usando `trap`.

## 🧰 Pré-requisitos

- Aula 21 concluída: `--stdout`, códigos de retorno, `--menu` e `--checklist`.

## 🗺️ Roteiro

| Etapa | Assunto | Tempo |
|---|---|---|
| 0 | `--form` | 20 min |
| 1 | Seleção de arquivos e diretórios | 15 min |
| 2 | `--gauge` com progresso real | 15 min |
| 3 | Fluxo com navegação e `trap` | 25 min |
| 🏁 | Entrega | 25 min |

---

## 🧩 Etapa 0 — `--form`

Pedir cinco dados com cinco `--inputbox` é ruim: o usuário não vê o conjunto e não
consegue voltar. O `--form` resolve.

### Ação

```bash
ssh disciplina
mkdir -p ~/scripts/aula22
cd ~/scripts/aula22
```

Cada campo do `--form` leva oito parâmetros:

```
<rótulo> <lin_rót> <col_rót> <valor> <lin_campo> <col_campo> <largura> <máximo>
```

```bash
DADOS=$(dialog --stdout --title "Cadastro" \
    --form "Preencha os dados:" 15 60 4 \
    "Nome:"     1 1 ""              1 12 30 40 \
    "E-mail:"   2 1 "@alu.ufc.br"   2 12 30 40 \
    "Curso:"    3 1 "Computação"    3 12 30 40 \
    "Matrícula:" 4 1 ""             4 12 12 12)
CODIGO=$?
clear
echo "retorno: $CODIGO"
echo "--- dados ---"
echo "$DADOS"
```

O resultado vem com **um campo por linha**, na ordem em que foram declarados. Para
separá-los:

```bash
{ read -r NOME; read -r EMAIL; read -r CURSO; read -r MATRICULA; } <<< "$DADOS"
echo "Nome: [$NOME]"
echo "E-mail: [$EMAIL]"
echo "Matrícula: [$MATRICULA]"
```

> 💡 Um campo com **largura máxima 0** vira somente leitura — útil para mostrar
> dados que o usuário não deve alterar. E o `--passwordform` esconde tudo.

Um campo deixado em branco devolve uma **linha vazia**, não some. Isso preserva a
ordem — mas exige que você valide:

```bash
[ -z "$NOME" ] && echo "Nome é obrigatório"
```

### ✅ Checkpoint 0

✔ O formulário aparece com os quatro campos e os valores iniciais.
✔ O `read` separa corretamente as quatro variáveis.
✔ Deixando um campo vazio, a ordem dos demais não se perde.

### ❓ Pergunta

O `--form` devolve os campos por posição, sem nome. O que acontece com o seu código
se alguém acrescentar um campo no meio do formulário?

---

## 🧩 Etapa 1 — Seleção de arquivos e diretórios

### Ação

```bash
ARQUIVO=$(dialog --stdout --title "Escolha um arquivo" --fselect "$HOME/" 14 60)
clear
echo "[$ARQUIVO]"

DIRETORIO=$(dialog --stdout --title "Escolha um diretório" --dselect "$HOME/" 10 60)
clear
echo "[$DIRETORIO]"
```

A navegação usa TAB para alternar entre os painéis de diretórios e arquivos, e as
setas para mover.

> ⚠️ A **barra final** no caminho inicial importa. Com `$HOME/`, o `dialog` abre
> dentro do diretório; sem ela, ele o trata como um arquivo a ser selecionado.
>
> ⚠️ O `--fselect` devolve o caminho digitado **mesmo que ele não exista**. Sempre
> valide depois:
>
> ```bash
> [ -f "$ARQUIVO" ] || { clear; echo "Arquivo inválido"; exit 1; }
> ```

Na prática, um menu montado a partir do `ls` costuma ser mais confortável que o
`--fselect` — foi o que você fez no `escolhe_arquivo.sh` da Aula 21.

### ✅ Checkpoint 1

✔ O `--fselect` devolve um caminho completo.
✔ Você confirmou que ele devolve caminhos inexistentes sem reclamar.

### ❓ Pergunta

Por que o `--fselect` não valida a existência do arquivo sozinho?

---

## 🧩 Etapa 2 — `--gauge` com progresso real

Na Aula 21 a barra foi alimentada por um `seq`. Agora com trabalho de verdade.

### Ação

```bash
cat > progresso.sh
#!/bin/bash
ARQUIVOS=(/etc/passwd /etc/hosts /etc/hostname /etc/os-release /etc/fstab)
TOTAL=${#ARQUIVOS[@]}
DESTINO=$(mktemp -d)

trap 'rm -rf "$DESTINO"; clear' EXIT

for i in "${!ARQUIVOS[@]}"; do
    ARQ="${ARQUIVOS[$i]}"
    PERCENTUAL=$(( (i + 1) * 100 / TOTAL ))
    echo "XXX"
    echo "$PERCENTUAL"
    echo "Copiando $(basename "$ARQ")..."
    echo "XXX"
    cp "$ARQ" "$DESTINO/" 2>/dev/null
    sleep 0.6
done | dialog --title "Backup" --gauge "Iniciando..." 10 60 0

dialog --msgbox "Concluído: $TOTAL arquivos." 8 50
```

Ctrl+D, `chmod +x progresso.sh`, e rode.

O protocolo do `--gauge` é simples: ele lê a entrada padrão esperando números. Para
trocar **também a mensagem**, mande o bloco:

```
XXX
<percentual>
<nova mensagem>
XXX
```

> ⚠️ O laço inteiro está do lado esquerdo do *pipe*, então roda em um **subshell**
> (Aula 12). Variáveis alteradas lá dentro não sobrevivem. Se precisar de um
> resultado, grave em arquivo ou use `--gauge` com um FIFO.

### ✅ Checkpoint 2

✔ A barra avança de 20 em 20 e a mensagem muda a cada arquivo.
✔ O `trap ... EXIT` apagou o temporário e limpou a tela.

### ❓ Pergunta

O `trap ... EXIT` deste *script* faz duas coisas. Por que o `clear` está ali dentro,
e não no final do *script*?

---

## 🧩 Etapa 3 — Fluxo com navegação e `trap`

Um assistente de verdade deixa o usuário voltar. Isso pede uma máquina de estados.

### Ação

```bash
cat > assistente.sh
#!/bin/bash

trap 'clear; echo "Interrompido."; exit 130' INT TERM
trap 'clear' EXIT

NOME=""
LINGUAGEM=""
ETAPA=1

caixa_nome() {
    NOME=$(dialog --stdout --title "Passo 1 de 2" \
        --cancel-label "Sair" \
        --inputbox "Seu nome:" 8 50 "$NOME")
}

caixa_linguagem() {
    LINGUAGEM=$(dialog --stdout --title "Passo 2 de 2" \
        --cancel-label "Voltar" \
        --menu "Linguagem preferida:" 12 50 3 \
        bash "Shell Script" \
        python "Python" \
        c "C")
}

while true; do
    case "$ETAPA" in
        1)
            caixa_nome
            if [ $? -ne 0 ]; then exit 1; fi
            [ -z "$NOME" ] && continue
            ETAPA=2
            ;;
        2)
            caixa_linguagem
            if [ $? -ne 0 ]; then ETAPA=1; continue; fi
            ETAPA=3
            ;;
        3)
            dialog --yesno "Nome: $NOME\nLinguagem: $LINGUAGEM\n\nConfirma?" 10 50
            case $? in
                0) clear; echo "Cadastro concluído."; exit 0 ;;
                1) ETAPA=2 ;;
                *) exit 1 ;;
            esac
            ;;
    esac
done
```

Ctrl+D, `chmod +x assistente.sh`, e teste **todos** os caminhos: avançar, voltar do
passo 2 para o 1, recusar a confirmação, e sair com Esc.

Três coisas a observar:

- O estado fica na variável `ETAPA`, e o `while` decide o que desenhar.
- O `--cancel-label` renomeia o botão conforme o significado local ("Sair" no passo 1,
  "Voltar" no passo 2).
- O valor anterior é passado de volta para a caixa (`"$NOME"` no `--inputbox`), para
  o usuário não redigitar ao voltar.

### ✅ Checkpoint 3

✔ Do passo 2, "Voltar" retorna ao passo 1 **com o nome preenchido**.
✔ Recusar a confirmação volta ao passo 2.
✔ Esc em qualquer ponto sai limpando a tela.

### ❓ Pergunta

O `if [ $? -ne 0 ]` vem logo depois da chamada da função. O que aconteceria se
houvesse um `echo` de depuração entre as duas linhas?

---

## 🏁 Entrega da Aula — 0,7 ponto (Nota 3)

Individualmente, nos últimos 25 minutos.

Crie o *script* `~/scripts/aula22/compactador.sh`, um assistente de compactação.

O fluxo:

1. Pedir o caminho de um **diretório** (via `--dselect` ou `--inputbox`).
   - Validar que existe e é diretório. Se não, mostrar erro em `--msgbox` e voltar
     a perguntar.
2. Montar dinamicamente uma `--checklist` com os **arquivos comuns** do diretório
   (sem subdiretórios). O usuário escolhe um ou mais.
   - Se o diretório não tiver arquivos, avisar e encerrar com retorno `1`.
   - Se o usuário não marcar nenhum, avisar e voltar à seleção.
3. Oferecer o formato de compactação em um `--radiolist`: **gzip** (`.tar.gz`) ou
   **bzip2** (`.tar.bz2`).
4. Pedir o nome do arquivo final em um `--inputbox` (sem a extensão).
5. Criar o arquivo compactado com os arquivos selecionados, mostrando o andamento em
   um `--gauge`.
6. Exibir uma tela final de sucesso com o nome do arquivo criado e o tamanho dele.

Requisitos:

- Use `--stdout` em todas as caixas e trate Cancelar/Esc em **todas** as etapas.
- Use `trap` para garantir que a tela seja limpa e temporários removidos em qualquer
  saída.
- O `--checklist` deve usar `--separate-output`, para suportar nomes com espaço.

### Critérios de correção

| # | Critério | Valor |
|---|---|---|
| 1 | Pede e **valida** o diretório, repetindo em caso de erro | 0,10 |
| 2 | Monta a `--checklist` dinamicamente com os arquivos reais | 0,15 |
| 3 | Trata "nenhum arquivo" e "nenhum marcado" | 0,10 |
| 4 | Cria o arquivo no formato escolhido, com os arquivos certos | 0,20 |
| 5 | Mostra progresso com `--gauge` e a tela final com o tamanho | 0,10 |
| 6 | `trap` limpa tela e temporários em qualquer saída | 0,05 |

Correção:

```bash
cd ~/scripts/aula22
mkdir -p arquivos && printf 'a\n' > arquivos/a.txt && printf 'b\n' > arquivos/b.txt
printf 'c\n' > "arquivos/c com espaco.txt"
./compactador.sh
ls -l *.tar.*
mkdir -p correcao && tar xf *.tar.* -C correcao && ls -R correcao
```

O teste com `c com espaco.txt` é o critério do `--separate-output`.

---

## ✅ Checklist de Encerramento

| # | Verificação | Comando |
|---|---|---|
| 1 | O *script* é executável | `ls -l compactador.sh` |
| 2 | Usa `--separate-output` | `grep -c "separate-output" compactador.sh` |
| 3 | Tem `trap` | `grep -c trap compactador.sh` |
| 4 | O compactado abre e traz os arquivos certos | `tar tf *.tar.*` |
| 5 | O terminal está limpo | visual |

---

## 💬 Para Discutir em Sala

- Você implementou navegação para trás com uma variável de estado e um `while`. É a
  mesma ideia de uma máquina de estados. Onde mais você já viu esse padrão?
- Entre o `--fselect` do `dialog` e um `--menu` montado com `ls`, qual dá melhor
  experiência? E qual dá menos trabalho de programar?

## 📌 Para a Próxima Aula

A **Aula 23** inicia o bloco de nuvem (`slides/19_AWS`). Traga o acesso ao **AWS
Academy** funcionando — sem ele você não consegue acompanhar. Confira antes:

1. Login no AWS Academy.
2. Laboratório iniciado (indicador verde).
3. Credenciais e o arquivo `labsuser.pem` baixados.
