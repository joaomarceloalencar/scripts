# 🧪 Aula 19 — Compilação e Configuração de Programas

**Disciplina:** Programação de *Scripts* — UFC Quixadá
**Material de apoio:** `slides/16_compilacao_e_configuracao_de_programas`
**Sessão:** Semana 11 — terça, 20/10
**Entrega desta aula:** 0,7 ponto (Nota 3)
**Duração estimada:** 100 minutos

---

## 🎯 Objetivos da Aula

Ao final desta aula você deve ser capaz de:

- Percorrer as quatro etapas da compilação com `gcc`.
- Criar e usar uma biblioteca estática e uma compartilhada.
- Escrever um `Makefile` com alvos, dependências e variáveis.
- Instalar um programa a partir do código-fonte com `./configure && make && make install`.
- Automatizar essa instalação em um *script*.

## 🧰 Pré-requisitos

- Bloco 2 concluído. Não é preciso saber C — os programas são de três linhas.

## 🗺️ Roteiro

| Etapa | Assunto | Tempo |
|---|---|---|
| 0 | As quatro etapas da compilação | 20 min |
| 1 | Bibliotecas | 20 min |
| 2 | `make` | 20 min |
| 3 | Instalando a partir do fonte | 15 min |
| 🏁 | Entrega | 25 min |

---

## 🧩 Etapa 0 — As quatro etapas da compilação

### Ação

```bash
ssh disciplina
mkdir -p ~/scripts/aula19
cd ~/scripts/aula19

gcc --version | head -1
```

Crie o programa:

```bash
cat > ola.c
#include <stdio.h>

#define MENSAGEM "Olá, Programação de Scripts!"

int main(void) {
    printf("%s\n", MENSAGEM);
    return 0;
}
```

Ctrl+D. O `gcc` faz quatro coisas em sequência. Rode uma de cada vez:

```bash
gcc -E ola.c -o ola.i        # 1. pré-processamento
gcc -S ola.i -o ola.s        # 2. compilação para assembly
gcc -c ola.s -o ola.o        # 3. montagem para código objeto
gcc ola.o -o ola             # 4. ligação
./ola
```

Inspecione o resultado de cada etapa:

```bash
wc -l ola.c ola.i            # o pré-processador expandiu os includes
grep MENSAGEM ola.i          # a macro sumiu, virou o texto
head -15 ola.s               # assembly
file ola.o ola               # objeto vs. executável
```

Repare que `ola.o` é `relocatable` e `ola` é `executable`.

E o atalho, que faz tudo de uma vez:

```bash
gcc ola.c -o ola2 && ./ola2
```

As opções que você mais vai usar:

| Opção | Efeito |
|---|---|
| `-o <arquivo>` | nome da saída |
| `-Wall -Wextra` | liga os avisos (**use sempre**) |
| `-g` | inclui símbolos de depuração |
| `-O2` | otimiza |
| `-c` | só compila, não liga |
| `-I<dir>` | onde procurar cabeçalhos |
| `-L<dir>` / `-l<nome>` | onde procurar bibliotecas / qual ligar |

```bash
gcc -Wall -Wextra -O2 ola.c -o ola3
```

### ✅ Checkpoint 0

✔ `./ola` imprime a mensagem.
✔ `ola.i` tem muito mais linhas que `ola.c`.
✔ `file ola.o` e `file ola` mostram tipos diferentes.

### ❓ Pergunta

O `ola.i` tem centenas de linhas para um programa de 7. De onde vem tudo isso, e por
que o `#define` desapareceu?

---

## 🧩 Etapa 1 — Bibliotecas

### Ação

Separe o código em módulo e programa principal:

```bash
cat > saudacao.h
#ifndef SAUDACAO_H
#define SAUDACAO_H
void saudar(const char *nome);
#endif
```

Ctrl+D.

```bash
cat > saudacao.c
#include <stdio.h>
#include "saudacao.h"

void saudar(const char *nome) {
    printf("Olá, %s!\n", nome);
}
```

Ctrl+D.

```bash
cat > principal.c
#include "saudacao.h"

int main(int argc, char *argv[]) {
    saudar(argc > 1 ? argv[1] : "mundo");
    return 0;
}
```

Ctrl+D.

#### Biblioteca estática (`.a`)

```bash
gcc -c saudacao.c -o saudacao.o
ar rcs libsaudacao.a saudacao.o
ar t libsaudacao.a

gcc principal.c -L. -lsaudacao -o prog_estatico
./prog_estatico
./prog_estatico Ana
```

O código da biblioteca foi **copiado para dentro** do executável.

#### Biblioteca compartilhada (`.so`)

```bash
gcc -fPIC -c saudacao.c -o saudacao_pic.o
gcc -shared saudacao_pic.o -o libsaudacao.so

gcc principal.c -L. -lsaudacao -o prog_dinamico
./prog_dinamico
```

Provavelmente deu erro:

```
./prog_dinamico: error while loading shared libraries: libsaudacao.so: cannot open shared object file
```

O ligador achou a biblioteca na **compilação**, mas o carregador não a acha na
**execução** — ele procura em `/lib`, `/usr/lib` e no `LD_LIBRARY_PATH`.

```bash
ldd prog_dinamico
LD_LIBRARY_PATH=. ./prog_dinamico
ldd prog_estatico | grep saudacao || echo "(o estático não depende da lib)"
```

Compare os tamanhos:

```bash
ls -l prog_estatico prog_dinamico
```

> 💡 O `-fPIC` (*Position Independent Code*) é obrigatório em bibliotecas
> compartilhadas: o código precisa funcionar em qualquer endereço de memória, já que
> vários programas a carregam ao mesmo tempo.

### ✅ Checkpoint 1

✔ `./prog_estatico Ana` imprime `Olá, Ana!`.
✔ `./prog_dinamico` falha sem o `LD_LIBRARY_PATH` e funciona com ele.
✔ `ldd prog_dinamico` lista `libsaudacao.so`; `ldd prog_estatico` não.

### ❓ Pergunta

O executável estático é maior e não depende de nada. O dinâmico é menor mas exige a
biblioteca presente. Quando você escolheria cada um?

---

## 🧩 Etapa 2 — `make`

Recompilar tudo à mão a cada mudança não escala. O `make` recompila **só o que
mudou**.

### Ação

```bash
cat > Makefile
CC      = gcc
CFLAGS  = -Wall -Wextra -O2
OBJETOS = principal.o saudacao.o
ALVO    = programa

all: $(ALVO)

$(ALVO): $(OBJETOS)
	$(CC) $(OBJETOS) -o $(ALVO)

principal.o: principal.c saudacao.h
	$(CC) $(CFLAGS) -c principal.c

saudacao.o: saudacao.c saudacao.h
	$(CC) $(CFLAGS) -c saudacao.c

clean:
	rm -f $(OBJETOS) $(ALVO)

.PHONY: all clean
```

Ctrl+D.

> ⚠️ **A indentação do `Makefile` é TAB, não espaços.** Se o `nano` converter, você
> recebe `Makefile:8: *** missing separator. Stop.` Confira com `cat -A Makefile`:
> as linhas de comando devem começar com `^I`.

Agora veja o `make` trabalhando:

```bash
make
./programa Carlos

make                 # nada mudou: "make: Nada a ser feito para 'all'."

touch saudacao.c
make                 # recompila só saudacao.o e religa

touch saudacao.h
make                 # recompila os DOIS: ambos dependem do cabeçalho

make clean
ls
```

A anatomia de uma regra:

```
alvo: dependências
<TAB>comando
```

O `make` compara as datas: se alguma dependência é mais nova que o alvo, o comando
roda.

O `.PHONY` declara alvos que não geram arquivo. Sem ele, um arquivo chamado `clean`
no diretório faria o `make clean` parar de funcionar. Teste:

```bash
touch clean
make clean
rm -f clean
```

### ✅ Checkpoint 2

✔ `make` compila e `./programa Carlos` funciona.
✔ Rodando `make` de novo, ele diz que não há nada a fazer.
✔ Depois de `touch saudacao.h`, os dois `.o` são recompilados.
✔ Você viu o `.PHONY` sendo necessário.

### ❓ Pergunta

O `make` decide o que recompilar comparando datas de modificação. Que problema isso
causa se o relógio da máquina estiver errado?

---

## 🧩 Etapa 3 — Instalando a partir do fonte

O trio `./configure && make && make install` é o padrão histórico do software GNU.

### Ação

```bash
mkdir -p ~/scripts/aula19/fontes
cd ~/scripts/aula19/fontes

wget -q https://ftp.gnu.org/gnu/hello/hello-2.12.1.tar.gz || \
  echo "Sem rede? Peça o arquivo ao professor."
tar xzf hello-2.12.1.tar.gz
cd hello-2.12.1
ls
```

Todo pacote GNU traz os mesmos arquivos: `README`, `INSTALL`, `configure`,
`Makefile.in`.

```bash
head -20 INSTALL
./configure --help | head -25
```

Configure para instalar no seu diretório, sem precisar de `root`:

```bash
./configure --prefix="$HOME/local"
```

O `configure` testa o sistema — compilador, bibliotecas, cabeçalhos — e **gera** o
`Makefile` adequado.

```bash
ls Makefile config.log
make
./hello
make install
~/local/bin/hello
```

Adicione ao `PATH`:

```bash
export PATH="$HOME/local/bin:$PATH"
hello
which hello
```

> 💡 O `--prefix` é a resposta para "instalar sem `sudo`". Tudo vai para dentro do
> diretório indicado: binários em `bin/`, bibliotecas em `lib/`, manuais em `share/`.

### ✅ Checkpoint 3

✔ `./configure --prefix="$HOME/local"` gera o `Makefile`.
✔ `~/local/bin/hello` executa.
✔ Depois do `export PATH`, `which hello` aponta para o seu diretório.

### ❓ Pergunta

O `./configure` demorou e produziu um `config.log` enorme. O que exatamente ele
estava testando, e por que isso não pode ser decidido na hora de escrever o código?

---

## 🏁 Entrega da Aula — 0,7 ponto (Nota 3)

Individualmente, nos últimos 25 minutos.

Crie o *script* `~/scripts/aula19/instalador.sh`, que automatiza a instalação de um
pacote GNU a partir do fonte.

**Uso:** `./instalador.sh -u <URL do tarball> [-p <prefixo>] [-j <threads>]`

1. Trate as opções com `getopts`. A `-u` é obrigatória; o padrão de `-p` é
   `$HOME/local` e o de `-j` é `1`.
2. Sem `-u`, imprima a ajuda no `stderr` e retorne `1`.
3. O *script* deve, em sequência:
   - criar um diretório de trabalho temporário;
   - baixar o *tarball* com `wget` (ou `curl`);
   - descompactar e entrar no diretório gerado — **sem** o nome estar fixo no código,
     já que ele varia por pacote;
   - rodar `./configure --prefix=<prefixo>`, `make -j<threads>` e `make install`;
   - imprimir o caminho final do binário instalado.
4. **Cada etapa deve ser verificada**: se qualquer uma falhar, o *script* imprime
   qual etapa falhou, no `stderr`, e encerra com retorno diferente de zero.
5. Use `trap` para remover o diretório temporário ao final, inclusive em caso de
   erro ou interrupção.
6. Registre cada etapa em `instalador.log`, com data e hora.

Teste com:

```
$ ./instalador.sh -u https://ftp.gnu.org/gnu/hello/hello-2.12.1.tar.gz -p ~/local2 -j 2
[09:41:02] Baixando hello-2.12.1.tar.gz...
[09:41:05] Descompactando...
[09:41:06] Configurando...
[09:41:30] Compilando...
[09:41:38] Instalando...
Instalado em: /home/aluno/local2/bin/hello
```

### Critérios de correção

| # | Critério | Valor |
|---|---|---|
| 1 | `getopts` com `-u` obrigatória e padrões para `-p` e `-j` | 0,15 |
| 2 | Descobre o diretório do fonte sem tê-lo fixo no código | 0,15 |
| 3 | Executa as três etapas e o binário funciona ao final | 0,15 |
| 4 | Verifica cada etapa e falha com mensagem no `stderr` | 0,15 |
| 5 | `trap` remove o temporário em qualquer saída | 0,05 |
| 6 | O `instalador.log` registra as etapas com hora | 0,05 |

Correção:

```bash
cd ~/scripts/aula19
./instalador.sh; echo "retorno=$?"
./instalador.sh -u https://ftp.gnu.org/gnu/hello/hello-2.12.1.tar.gz -p ~/local2
~/local2/bin/hello
./instalador.sh -u http://exemplo.invalido/nada.tar.gz 2>&1 | tail -2; echo "retorno=$?"
ls /tmp | grep -c instalador     # deve ser 0: o trap limpou
cat instalador.log
```

> 💡 Para o critério 2: depois de descompactar em um diretório vazio, o único
> subdiretório presente é o do fonte. Ou use `tar tzf` para inspecionar antes.

---

## ✅ Checklist de Encerramento

| # | Verificação | Comando |
|---|---|---|
| 1 | O *script* é executável | `ls -l ~/scripts/aula19/instalador.sh` |
| 2 | Usa `getopts` e `trap` | `grep -c -E "getopts\|trap" instalador.sh` |
| 3 | O binário instalado funciona | `~/local2/bin/hello` |
| 4 | Nenhum temporário sobrou | `ls /tmp \| grep instalador` |
| 5 | O *log* tem as cinco etapas | `wc -l instalador.log` |

---

## 💬 Para Discutir em Sala

- Você automatizou `configure && make && make install` em um *script*. É basicamente
  o que um gerenciador de pacotes faz. O que falta no seu para virar um `apt`?
- O `make install` sem `--prefix` escreve em `/usr/local` e exige `sudo`. Por que
  instalar software fora do gerenciador de pacotes é considerado arriscado?

## 📌 Para a Próxima Aula

Na **Aula 20** vamos às ferramentas de rede (`slides/17_ferramentas_de_rede`):
`wget`, `curl`, `nc` e `ss`. É a última aula antes de o curso migrar para a nuvem.
