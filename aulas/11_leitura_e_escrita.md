# 🧪 Aula 11 — Leitura e Escrita

**Disciplina:** Programação de *Scripts* — UFC Quixadá
**Material de apoio:** `slides/10_leitura_e_escrita`
**Sessão:** Semana 6 — quarta, 16/09
**Entrega desta aula:** 1,25 pontos (Nota 2)
**Duração estimada:** 100 minutos

---

## 🎯 Objetivos da Aula

Ao final desta aula você deve ser capaz de:

- Capturar entrada do usuário com `read` e suas opções.
- Formatar saída com `printf`, alinhando colunas.
- Controlar cor, posição do cursor e limpeza de tela com `tput`.
- Montar um menu interativo em laço.

## 🧰 Pré-requisitos

- Aula 10 concluída. Esta aula usa `case`, `while` e variáveis.

## 🗺️ Roteiro

| Etapa | Assunto | Tempo |
|---|---|---|
| 0 | `read` | 20 min |
| 1 | `printf` | 20 min |
| 2 | `tput`: cores e estilos | 15 min |
| 3 | `tput`: posição e tela | 15 min |
| 4 | Juntando: um menu | 10 min |
| 🏁 | Entrega | 20 min |

---

## 🧩 Etapa 0 — `read`

### Ação

```bash
ssh disciplina
mkdir -p ~/scripts/aula11
cd ~/scripts/aula11
```

A forma mais simples:

```bash
read NOME
echo "Olá, $NOME"
```

Com um texto de convite, tudo em um comando:

```bash
read -p "Qual seu nome? " NOME
echo "Olá, $NOME"
```

As opções que mais importam:

| Opção | Efeito |
|---|---|
| `-p "texto"` | imprime o convite antes de ler |
| `-r` | não interpreta `\` como escape (**use sempre**) |
| `-s` | não ecoa o que foi digitado (senhas) |
| `-n N` | lê no máximo N caracteres e retorna |
| `-t N` | desiste depois de N segundos |
| `-a VETOR` | guarda as palavras em um vetor |

Experimente cada uma:

```bash
read -rsp "Senha: " SENHA; echo
echo "Você digitou ${#SENHA} caracteres"

read -rn 1 -p "Pressione uma tecla para continuar..." ; echo

read -rt 5 -p "Você tem 5 segundos: " RESPOSTA || echo "Tempo esgotado!"
```

O `read` também divide a linha em várias variáveis:

```bash
read -r PRIMEIRO RESTO <<< "João Marcelo Uchôa de Alencar"
echo "Primeiro: [$PRIMEIRO]"
echo "Resto: [$RESTO]"
```

> 💡 A última variável recebe **todo** o resto da linha, não apenas a próxima palavra.

### ✅ Checkpoint 0

✔ `read -rsp "Senha: "` não mostra o que você digita.
✔ `read -rt 5` desiste sozinho depois de 5 segundos.
✔ `[$RESTO]` contém `Marcelo Uchôa de Alencar`.

### ❓ Pergunta

Na Aula 09 você usou `while read -r linha; do ... done < arquivo`. Agora usou
`read` para ler do teclado. O que muda entre os dois casos, do ponto de vista do
*script*?

---

## 🧩 Etapa 1 — `printf`

O `echo` só imprime texto. O `printf` **formata**.

### Ação

```bash
printf "Olá, mundo\n"
printf "Nome: %s, Idade: %d\n" "Ana" 25
printf "Valor: %.2f\n" 3.14159
```

O `\n` é obrigatório — diferente do `echo`, o `printf` não quebra linha sozinho.

Os formatos mais úteis:

| Formato | Significado |
|---|---|
| `%s` | texto |
| `%d` | número inteiro |
| `%.2f` | número com 2 casas decimais |
| `%5d` | inteiro alinhado à direita em 5 colunas |
| `%-15s` | texto alinhado à **esquerda** em 15 colunas |
| `%%` | um `%` literal |

O alinhamento é o que torna o `printf` insubstituível:

```bash
printf "%-15s %8s\n" "PRODUTO" "VALOR"
printf "%-15s %8d\n" "Playstation5" 4999
printf "%-15s %8d\n" "MacBook" 9799
printf "%-15s %8d\n" "iPad" 3499
```

Saída:

```
PRODUTO            VALOR
Playstation5        4999
MacBook             9799
iPad                3499
```

Compare com o `echo`, que não alinha nada:

```bash
echo -e "Playstation5\t4999"
echo -e "MacBook\t9799"
```

Um detalhe poderoso: se você der mais argumentos que formatos, o `printf`
**reaplica** o formato:

```bash
printf "%-10s\n" alfa beta gama
```

### ✅ Checkpoint 1

✔ A tabela de produtos sai com as colunas alinhadas.
✔ `printf "%-10s\n" alfa beta gama` imprime três linhas.
✔ `printf "Valor: %.2f\n" 3.14159` imprime `Valor: 3.14`.

### ❓ Pergunta

O `echo` é mais curto e não exige `\n`. Em que situação vale a pena o trabalho
extra do `printf`?

---

## 🧩 Etapa 2 — `tput`: cores e estilos

O `tput` consulta a base de dados do terminal e devolve a sequência de controle certa.

### Ação

```bash
tput setaf 1; echo "vermelho"; tput sgr0
tput setaf 2; echo "verde";    tput sgr0
tput setaf 4; echo "azul";     tput sgr0
```

As cores básicas de `setaf` (*set foreground*):

| Número | Cor |
|---|---|
| 0 | preto |
| 1 | vermelho |
| 2 | verde |
| 3 | amarelo |
| 4 | azul |
| 5 | magenta |
| 6 | ciano |
| 7 | branco |

Use `setab` para o fundo:

```bash
tput setab 3; tput setaf 0; echo " ATENÇÃO "; tput sgr0
```

Os estilos:

```bash
tput bold;  echo "negrito";     tput sgr0
tput smul;  echo "sublinhado";  tput rmul
tput rev;   echo "invertido";   tput sgr0
```

> ⚠️ O `tput sgr0` **restaura tudo**. Se você esquecer dele, o terminal fica
> colorido para sempre — inclusive o seu *prompt*. Se acontecer, rode `tput sgr0`
> ou `reset`.

A forma limpa é guardar em variáveis:

```bash
VERMELHO=$(tput setaf 1)
NEGRITO=$(tput bold)
NORMAL=$(tput sgr0)

echo "${VERMELHO}${NEGRITO}Erro:${NORMAL} arquivo não encontrado"
```

### ✅ Checkpoint 2

✔ As três cores aparecem corretamente.
✔ Depois do `sgr0`, o texto volta ao normal.
✔ A versão com variáveis funciona igual à versão com comandos soltos.

### ❓ Pergunta

Rode `tput setaf 1 | cat -A`. O que o `tput` realmente devolve? Por que isso
justifica guardar o resultado em variável, em vez de chamá-lo em todo `echo`?

---

## 🧩 Etapa 3 — `tput`: posição e tela

### Ação

```bash
tput clear                       # limpa a tela
tput cup 10 20; echo "aqui"      # linha 10, coluna 20
tput lines                       # quantas linhas o terminal tem
tput cols                        # quantas colunas
```

> ⚠️ O `tput cup` conta a partir de **zero**, e a ordem é **linha, coluna** — não
> `x, y`. É a fonte de metade dos erros com essa ferramenta.

Um exemplo que usa o tamanho real do terminal:

```bash
cat > centralizado.sh
#!/bin/bash
TEXTO="PROGRAMAÇÃO DE SCRIPTS"
LINHA=$(( $(tput lines) / 2 ))
COLUNA=$(( ($(tput cols) - ${#TEXTO}) / 2 ))
tput clear
tput cup "$LINHA" "$COLUNA"
tput bold; tput setaf 6
echo "$TEXTO"
tput sgr0
tput cup $(( $(tput lines) - 1 )) 0
```

Ctrl+D, e:

```bash
chmod +x centralizado.sh
./centralizado.sh
```

Redimensione a janela do terminal e rode de novo — o texto continua centralizado.

Outros comandos úteis:

```bash
tput civis        # esconde o cursor
tput cnorm        # mostra o cursor de novo
tput el           # apaga do cursor até o fim da linha
```

### ✅ Checkpoint 3

✔ `./centralizado.sh` centraliza o texto na tela.
✔ Ao mudar o tamanho da janela e rodar de novo, continua centralizado.
✔ Depois de `tput civis`, o cursor some; com `tput cnorm`, volta.

### ❓ Pergunta

Por que o *script* calcula `(cols - tamanho_do_texto) / 2` em vez de simplesmente
usar uma coluna fixa?

---

## 🧩 Etapa 4 — Juntando: um menu

### Ação

```bash
cat > menu.sh
#!/bin/bash
NEGRITO=$(tput bold)
CIANO=$(tput setaf 6)
NORMAL=$(tput sgr0)

menu() {
    tput clear
    echo "${NEGRITO}${CIANO}=== MONITOR DO SISTEMA ===${NORMAL}"
    echo
    printf "  %s) %s\n" 1 "Tempo ligado"
    printf "  %s) %s\n" 2 "Memória física"
    printf "  %s) %s\n" 3 "Sair"
    echo
}

while true; do
    menu
    read -rp "Opção: " OPCAO
    case "$OPCAO" in
        1) tput clear; uptime ;;
        2) tput clear; free -m ;;
        3) tput clear; echo "Até logo."; exit 0 ;;
        *) tput clear; echo "Opção inválida." ;;
    esac
    read -rn 1 -p "Pressione qualquer tecla para voltar ao menu..."
done
```

Ctrl+D, e:

```bash
chmod +x menu.sh
./menu.sh
```

Repare em três decisões de projeto:

- O menu está em uma **função**, para poder ser chamado a cada volta.
- O `while true` só termina pelo `exit` dentro do `case`.
- O `read -rn 1` segura a tela para o usuário ler o resultado.

### ✅ Checkpoint 4

✔ O menu aparece colorido e as opções funcionam.
✔ A opção 3 encerra o *script* limpando a tela.
✔ Uma opção inválida não quebra o programa.

### ❓ Pergunta

Se você tirar o `read -rn 1` do fim do laço, o que acontece com o resultado do
comando? Teste.

---

## 🏁 Entrega da Aula — 1,25 pontos (Nota 2)

Individualmente, nos últimos 20 minutos.

Crie o *script* `~/scripts/aula11/sistema.sh`, um monitor de desempenho interativo.

1. Deve começar limpando a tela e exibindo um menu **dentro de uma função**
   chamada `menu`.
2. Use `read` para capturar a escolha e `case` para tratá-la.
3. O programa roda em laço e só termina na opção **Sair**.
4. Ao escolher uma opção: limpa a tela, executa o comando, exibe o resultado e
   espera o usuário apertar uma tecla antes de voltar ao menu.
5. O título do menu deve estar **colorido e em negrito**, e o terminal deve voltar
   ao normal ao sair.
6. As opções do menu devem estar alinhadas, usando `printf`.

| Opção | Comando |
|---|---|
| 1 | `uptime` |
| 2 | `dmesg \| tail -n 10` |
| 3 | `vmstat 1 5` |
| 4 | `free -m` |
| 5 | `df -h` |
| 6 | Sair |

### Critérios de correção

| # | Critério | Valor |
|---|---|---|
| 1 | Existe a função `menu` e ela é chamada no laço | 0,25 |
| 2 | As cinco opções executam o comando correto | 0,35 |
| 3 | A opção 6 encerra e restaura o terminal | 0,20 |
| 4 | Usa `printf` para alinhar as opções | 0,20 |
| 5 | Opção inválida é tratada sem quebrar o laço | 0,25 |

Correção: o professor navega pelas opções, testa uma entrada inválida e sai pela
opção 6. Depois confere se o terminal ficou limpo:

```bash
cd ~/scripts/aula11 && ./sistema.sh
grep -c "^menu()" sistema.sh      # deve responder 1
```

> 💡 Se `dmesg` der `Operation not permitted`, use `dmesg 2>/dev/null | tail -n 10`
> ou substitua por `sudo dmesg | tail -n 10`, conforme o servidor permitir.

---

## ✅ Checklist de Encerramento

| # | Verificação | Comando |
|---|---|---|
| 1 | O *script* é executável | `ls -l ~/scripts/aula11/sistema.sh` |
| 2 | Tem a função `menu` | `grep -c "^menu()" sistema.sh` |
| 3 | Usa `printf` | `grep -c printf sistema.sh` |
| 4 | Restaura o terminal | `grep -c "sgr0" sistema.sh` |
| 5 | O terminal está normal depois de sair | `tput sgr0; echo teste` |

---

## 💬 Para Discutir em Sala

- Seu menu é uma interface de usuário feita em *shell*. Onde está o limite disso —
  em que ponto vale mais a pena usar `dialog` (Aula 21) ou outra linguagem?
- O `tput` consulta uma base de dados chamada `terminfo` para saber o que enviar.
  Por que não bastaria imprimir sempre a mesma sequência de escape?

## 📌 Para a Próxima Aula

Na **Aula 12** vamos ver vetores e *subshell*
(`slides/11_variaveis_e_vetores`) — como guardar listas em uma variável só e por
que às vezes uma variável "esquece" o valor que você acabou de atribuir.
