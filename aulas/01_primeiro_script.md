# 🧪 Aula 01 — O *Shell* e o Primeiro *Script*

**Disciplina:** Programação de *Scripts* — UFC Quixadá
**Material de apoio:** `slides/01_introducao`
**Sessão:** Semana 1 — terça, 11/08
**Entrega desta aula:** 1,0 ponto (Nota 1)
**Duração estimada:** 100 minutos

---

## ⚙️ Antes de começar

Esta aula cria o ambiente que você vai usar o **semestre inteiro**: uma máquina
virtual própria na AWS Academy.

Leia o [guia de ambiente](00_ambiente.md) antes da aula. Você vai precisar de:

| Item | Onde conseguir |
|---|---|
| Acesso ao AWS Academy | convite enviado pelo professor |
| Laboratório iniciado | botão **Start Lab**, indicador verde |
| Chave `labsuser.pem` | **AWS Details → Download PEM** |

---

## 🎯 Objetivos da Aula

Ao final desta aula você deve ser capaz de:

- Identificar qual *shell* está executando e por que isso importa.
- Combinar dois comandos com um *pipe* (`|`).
- Transformar uma sequência de comandos em um *script* executável.
- Explicar o papel da **permissão de execução** e do **shebang** (`#!`).
- Criar uma instância EC2 e acessá-la com `ssh`.
- Criar um apelido de conexão no `~/.ssh/config` e copiar arquivos com `scp`.

---

## 🧰 Pré-requisitos

- Um terminal Linux (máquina do laboratório, WSL ou macOS).
- Conta do AWS Academy funcionando.
- Nenhum conhecimento prévio de programação em *shell*.

---

## 🗺️ Roteiro

| Etapa | Assunto | Tempo |
|---|---|---|
| 0 | Reconhecendo o terreno | 10 min |
| 1 | Um comando, dois comandos, um *pipe* | 10 min |
| 2 | Do comando ao *script* | 20 min |
| 3 | O *shebang* | 10 min |
| 4 | Criando a sua máquina na AWS | 15 min |
| 5 | Um apelido para a sua máquina | 15 min |
| 6 | Levando o *script* com SCP | 10 min |
| 🏁 | Entrega | 10 min |

As etapas 0 a 3 são feitas **na sua máquina local**. Da etapa 4 em diante, e em todas
as aulas seguintes, o trabalho acontece **na sua máquina da AWS**.

---

## 🧩 Etapa 0 — Reconhecendo o terreno

Todo mundo abre um terminal. Antes de escrever qualquer *script*, precisamos saber
**onde estamos** e **quem está interpretando o que digitamos**.

### Ação

```bash
whoami          # qual usuário eu sou
hostname        # em qual máquina eu estou
pwd             # em qual diretório eu estou
echo $SHELL     # qual shell é o meu padrão
```

Agora veja quais *shells* estão instalados na máquina:

```bash
cat /etc/shells
```

Saída típica no Ubuntu:

```
# /etc/shells: valid login shells
/bin/sh
/bin/bash
/usr/bin/bash
/bin/rbash
/usr/bin/rbash
/usr/bin/dash
```

### ✅ Checkpoint 0

Execute `echo $SHELL`.

✔ Deve aparecer um caminho terminando em `bash` — normalmente `/bin/bash`.
✔ O comando `pwd` deve mostrar o seu diretório pessoal, algo como `/home/aluno`.

> ⚠️ Se o `echo $SHELL` mostrar `/bin/zsh` (comum no macOS), tudo bem: nesta aula
> vamos executar os *scripts* com o `bash` explicitamente. Avise o professor.

### ❓ Pergunta

O `/etc/shells` lista vários programas diferentes. Se todos servem para a mesma
coisa — interpretar comandos —, por que o sistema mantém mais de um?

---

## 🧩 Etapa 1 — Um comando, dois comandos, um *pipe*

O primeiro exemplo do curso é contar quantos usuários estão logados na máquina.

### Ação

Comece vendo a informação crua:

```bash
who
```

Saída (exemplo):

```
aluno    tty2         2026-08-11 08:14 (tty2)
aluno    pts/0        2026-08-11 08:30 (192.168.0.42)
```

Cada linha é uma sessão aberta. Para **contar** essas linhas, usamos o `wc -l`
(*word count*, opção *lines*):

```bash
who | wc -l
```

Saída:

```
2
```

O caractere `|` é o **pipe**. Ele pega a saída do comando da esquerda e entrega
como entrada para o comando da direita. Nada foi salvo em disco no meio do caminho.

### ✅ Checkpoint 1

Execute os dois comandos em sequência.

✔ `who` imprime uma ou mais linhas.
✔ `who | wc -l` imprime **um único número**, igual à quantidade de linhas do `who`.

### ❓ Pergunta

Rode `who | wc -l` e depois peça para o colega ao lado rodar na máquina dele.
Os números batem? Por que o resultado do mesmo comando muda de máquina para máquina?

---

## 🧩 Etapa 2 — Do comando ao *script*

Digitar `who | wc -l` toda vez é chato. Vamos guardar esse comando em um arquivo.

### Ação

Primeiro, um lugar organizado para trabalhar:

```bash
mkdir -p ~/scripts/aula01
cd ~/scripts/aula01
pwd
```

Agora crie o arquivo. O comando `cat >` escreve no arquivo tudo o que você digitar,
até que você pressione **Ctrl+D** para encerrar:

```bash
cat > usuarios.sh
```

O cursor fica esperando. Digite a linha abaixo e pressione **Enter**:

```
who | wc -l
```

Agora pressione **Ctrl+D**. Você volta para o *prompt*. Confira o que foi gravado:

```bash
cat usuarios.sh
```

Tente executar:

```bash
./usuarios.sh
```

E leve um erro na cara:

```
bash: ./usuarios.sh: Permission denied
```

O arquivo existe e tem o conteúdo certo, mas **não tem permissão de execução**.
Veja isso com seus próprios olhos:

```bash
ls -l usuarios.sh
```

```
-rw-rw-r-- 1 aluno aluno 12 ago 11 09:02 usuarios.sh
```

Não há nenhum `x` nas permissões. Vamos adicionar:

```bash
chmod +x usuarios.sh
ls -l usuarios.sh
```

```
-rwxrwxr-x 1 aluno aluno 12 ago 11 09:02 usuarios.sh
```

Agora sim:

```bash
./usuarios.sh
```

### ✅ Checkpoint 2

✔ `ls -l usuarios.sh` mostra `x` nas permissões (`-rwxrwxr-x`).
✔ `./usuarios.sh` imprime um número, o mesmo que `who | wc -l` imprime.

> 💡 **Por que `./`?** O *shell* procura programas apenas nos diretórios listados na
> variável `PATH`, e o diretório atual **não** está nessa lista. O `./` diz
> explicitamente "o `usuarios.sh` que está aqui nesta pasta". Experimente digitar
> só `usuarios.sh` e veja a mensagem `command not found`.

### ❓ Pergunta

Um arquivo de texto comum virou um programa apenas com o `chmod +x` — nada foi
compilado. O que isso diz sobre a diferença entre um *script* e um programa em C?

---

## 🧩 Etapa 3 — O *shebang*

Nosso *script* funcionou, mas há uma fragilidade escondida nele.

### Ação

Pergunte ao sistema que tipo de arquivo é esse:

```bash
file usuarios.sh
```

```
usuarios.sh: ASCII text
```

Para o sistema, ainda é apenas **texto**. Quando você executou `./usuarios.sh`, o
*kernel* percebeu que não era um binário compilado, devolveu o arquivo para o
*shell*, e o *shell* o executou usando o interpretador padrão do sistema. Isso
funciona — mas só por sorte, porque o padrão era o `bash`.

A forma correta é declarar o interpretador na **primeira linha** do arquivo:

```bash
cat > usuarios.sh
```

Digite as **duas** linhas abaixo e encerre com **Ctrl+D**:

```
#!/bin/bash
who | wc -l
```

Confira o resultado:

```bash
cat usuarios.sh
file usuarios.sh
```

Agora o `file` responde diferente:

```
usuarios.sh: Bourne-Again shell script, ASCII text executable
```

### ✅ Checkpoint 3

✔ A primeira linha do arquivo é exatamente `#!/bin/bash`.
✔ `file usuarios.sh` menciona `Bourne-Again shell script`.
✔ `./usuarios.sh` continua imprimindo o número de usuários.

> ⚠️ O `#!` precisa estar nos **dois primeiros caracteres** do arquivo. Um espaço
> antes, uma linha em branco antes, ou `# !/bin/bash` com espaço no meio: qualquer
> um desses quebra o mecanismo silenciosamente.

### ❓ Pergunta

Com o *shebang*, estas duas execuções são equivalentes:

```bash
./usuarios.sh
/bin/bash usuarios.sh
```

Se são equivalentes, por que nos damos ao trabalho de colocar o *shebang* e a
permissão de execução, em vez de sempre chamar `/bin/bash arquivo`?

---

## 🧩 Etapa 4 — Criando a sua máquina na AWS

Até aqui, tudo local. Agora vamos criar a máquina que você vai usar o semestre
inteiro.

### Ação — criando a instância pelo console

No AWS Academy, com o laboratório iniciado (indicador verde), clique em **AWS** para
abrir o console. Vá em **EC2 → Instances → Launch instances** e preencha:

| Campo | Valor |
|---|---|
| **Name** | `<seu_usuario>-trabalho` |
| **Application and OS Images** | Ubuntu Server 22.04 LTS |
| **Instance type** | `t2.micro` |
| **Key pair** | `vockey` |
| **Network → Auto-assign public IP** | `Enable` |
| **Security group** | criar novo, permitindo **SSH (22)** de qualquer origem |
| **Storage** | 20 GiB, `gp3` |

Clique em **Launch instance** e espere o estado ficar `running`.

> ⚠️ A **tag `Name`** não é decoração. A partir da Aula 23 você vai listar instâncias
> pela linha de comando, e a sua máquina de trabalho vai aparecer no meio das que
> você criar. É por esse nome que você vai distingui-la — e evitar encerrá-la por
> engano.

Copie o **Public IPv4 address** da instância.

### Ação — conectando

A chave privada é um arquivo sensível, e o cliente `ssh` **se recusa** a usar uma
chave que outros usuários possam ler. Ajuste as permissões primeiro:

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
mv ~/Downloads/labsuser.pem ~/.ssh/
chmod 600 ~/.ssh/labsuser.pem
```

Conecte, trocando pelo IP que você copiou:

```bash
ssh -i ~/.ssh/labsuser.pem ubuntu@<IP_PUBLICO>
```

Na primeira conexão aparece um aviso:

```
The authenticity of host '54.234.12.98' can't be established.
ED25519 key fingerprint is SHA256:LKdo00AkJT7haicaM.
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```

Digite `yes` e pressione Enter.

Já logado na sua máquina, repita os comandos da Etapa 0:

```bash
whoami
hostname
pwd
who | wc -l
```

Confirme que você tem privilégio administrativo — vai precisar dele o semestre todo:

```bash
sudo whoami
```

Para voltar à sua máquina local:

```bash
exit
```

### ✅ Checkpoint 4

✔ A instância aparece como `running` no console, com a tag `Name` preenchida.
✔ O `hostname` dentro da sessão SSH é **diferente** do da sua máquina local.
✔ `sudo whoami` responde `root`.
✔ O `exit` devolve você ao *prompt* local.

> 🔧 **Deu `UNPROTECTED PRIVATE KEY FILE`?** A chave está com permissão aberta demais.
> Rode `chmod 600` nela de novo e confira com `ls -l ~/.ssh/`.
>
> 🔧 **Deu `Permission denied (publickey)`?** O usuário é `ubuntu` — não é o seu nome
> nem `root`. Em imagens Amazon Linux seria `ec2-user`, mas escolhemos Ubuntu.
>
> 🔧 **Deu *timeout*?** O grupo de segurança não liberou a porta 22, ou a instância
> ainda não terminou o *status check*. Espere um minuto e confira as regras.

### ❓ Pergunta

Você escolheu `Auto-assign public IP: Enable`. O que aconteceria se tivesse deixado
desabilitado? A máquina existiria, mas você conseguiria alcançá-la?

---

## 🧩 Etapa 5 — Um apelido para a sua máquina

Digitar `ssh -i ~/.ssh/labsuser.pem ubuntu@54.234.12.98` dez vezes por aula é
insustentável. E há um agravante: **esse IP vai mudar**.

### Ação — o agente

O `ssh-agent` guarda a chave destravada na memória durante a sessão. Veja se já
existe um agente rodando:

```bash
echo $SSH_AUTH_SOCK
```

Se a saída for **vazia**, inicie o agente:

```bash
eval "$(ssh-agent -s)"
```

```
Agent pid 3412
```

Carregue a chave:

```bash
ssh-add ~/.ssh/labsuser.pem
ssh-add -l
```

### Ação — o apelido

Crie o arquivo de configuração:

```bash
nano ~/.ssh/config
```

Conteúdo — troque `<IP_PUBLICO>` pelo IP da sua instância:

```
# Minha máquina da disciplina de Programação de Scripts
Host disciplina
    HostName <IP_PUBLICO>
    User ubuntu
    IdentityFile ~/.ssh/labsuser.pem
    IdentitiesOnly yes
    AddKeysToAgent yes
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
```

> ⚠️ **As duas últimas diretivas são específicas deste ambiente.** O IP público muda
> a cada religamento da instância, e a AWS recicla IPs entre contas — sem elas, o
> `ssh` acusaria `REMOTE HOST IDENTIFICATION HAS CHANGED` e recusaria a conexão.
>
> Em um servidor de verdade, com endereço fixo, desligar essa verificação seria uma
> **falha de segurança**: é justamente ela que detecta um servidor trocado por um
> impostor. Aqui, o risco é aceitável porque a máquina é descartável.

Salve com **Ctrl+O**, Enter, e saia com **Ctrl+X**. Proteja o arquivo:

```bash
chmod 600 ~/.ssh/config
```

Agora teste:

```bash
ssh disciplina
```

### ✅ Checkpoint 5

✔ `ssh disciplina` conecta sem pedir `-i`, sem pedir usuário e sem pedir senha.
✔ `ssh-add -l` lista a sua chave.

> 💡 Se algo der errado, `ssh -v disciplina` mostra qual bloco de configuração foi
> lido e qual chave foi oferecida.

> ⚠️ **Guarde isto para a próxima aula.** Quando a sessão do laboratório expirar, a
> sua instância é **desligada** — os arquivos continuam lá, mas ao religá-la o IP
> público muda, e o `ssh disciplina` passa a dar *timeout*.
>
> A correção é atualizar o `HostName` no `~/.ssh/config`. O passo a passo está na
> [rotina de início de aula](00_ambiente.md#-rotina-de-início-de-aula), e você vai
> repeti-la em toda aula deste semestre.
>
> Depois da Aula 07 você já terá ferramentas para automatizar isso.

### ❓ Pergunta

Execute `ssh-agent -s` **sem** o `eval` e observe a saída. O que exatamente esse
comando imprime? Por que o `eval` é necessário para que a coisa funcione?

> Guarde a resposta: vamos revisitar o `eval` quando estudarmos substituição de
> comandos, no capítulo de variáveis e parâmetros.

---

## 🧩 Etapa 6 — Levando o *script* com SCP

O `usuarios.sh` está na sua máquina local. Vamos colocá-lo na máquina da AWS.

### Ação

Primeiro, prepare o diretório de destino na máquina remota — sem sair da sua máquina local:

```bash
ssh disciplina 'mkdir -p ~/scripts/aula01'
```

> 👀 Repare no que acabou de acontecer: o `ssh` executou um comando na máquina
> remota e devolveu você ao *prompt* local, sem abrir uma sessão interativa.

Copie o arquivo:

```bash
cd ~/scripts/aula01
scp usuarios.sh disciplina:~/scripts/aula01/
```

```
usuarios.sh                          100%   24     1.2KB/s   00:00
```

Antes de executar, confira as permissões do arquivo que chegou lá:

```bash
ssh disciplina 'ls -l ~/scripts/aula01'
```

> ⚠️ **Chegou com `x` ou sem `x`?** Depende da versão do `scp` da sua máquina.
> Até o OpenSSH 8.x o `scp` usava um protocolo que transmitia as permissões junto
> com o arquivo; a partir do OpenSSH 9.0 ele passou a usar SFTP por baixo, e o bit
> de execução pode não vir. Descubra a sua versão com `ssh -V`.
>
> Se o `x` não veio, resolva na máquina remota:
>
> ```bash
> ssh disciplina 'chmod +x ~/scripts/aula01/usuarios.sh'
> ```

Execute o *script* na máquina da AWS:

```bash
ssh disciplina '~/scripts/aula01/usuarios.sh'
```

Compare com o resultado local:

```bash
./usuarios.sh
```

### ✅ Checkpoint 6

✔ O arquivo aparece em `ssh disciplina 'ls -l ~/scripts/aula01'`.
✔ `ssh disciplina '~/scripts/aula01/usuarios.sh'` imprime um número.

### ❓ Pergunta

O mesmo *script*, com o mesmo conteúdo, imprimiu números diferentes na sua máquina
e na máquina da AWS. Isso é um defeito do *script*? O que ele está realmente medindo?

E sobre a permissão de execução: se ela **não** tivesse atravessado a cópia, o que
`ssh disciplina '~/scripts/aula01/usuarios.sh'` teria respondido? Compare com o
erro que você viu na Etapa 2.

---

## 🏁 Entrega da Aula — 1,0 ponto (Nota 1)

Agora sem passo a passo, e individualmente. Você tem os últimos 25 minutos da aula.

Crie, no diretório `~/scripts/aula01` **da sua máquina da AWS**, um *script* chamado
`registro.sh` que:

1. Comece com o *shebang* correto.
2. Imprima a data e a hora atuais (investigue o comando `date`).
3. Imprima o nome da máquina onde está executando.
4. Imprima quantos usuários estão logados.
5. Tenha permissão de execução.

Saída esperada (os valores mudam a cada execução e a cada máquina):

```
$ ./registro.sh
qua 12 ago 2026 09:41:07 -03
servidor
2
```

### Critérios de correção

| # | Critério | Valor |
|---|---|---|
| 1 | O arquivo existe em `~/scripts/aula01/registro.sh` na máquina da AWS | 0,2 |
| 2 | A primeira linha é `#!/bin/bash` | 0,2 |
| 3 | O `ls -l` mostra permissão de execução | 0,2 |
| 4 | `./registro.sh` roda e imprime as três informações | 0,4 |

O professor corrige executando, na sua sessão, o comando:

```bash
cd ~/scripts/aula01 && ls -l registro.sh && head -1 registro.sh && ./registro.sh
```

> 💡 **Você pode escrever o *script* onde preferir** — direto na máquina da AWS com o
> `nano`, ou na sua máquina e depois `scp`. O que vale é o resultado estar lá.

---

## ✅ Checklist de Encerramento

Antes de sair da sala, confirme cada item:

| # | Verificação | Comando |
|---|---|---|
| 1 | Existe o diretório de trabalho | `ls -d ~/scripts/aula01` |
| 2 | O `usuarios.sh` tem *shebang* | `head -1 ~/scripts/aula01/usuarios.sh` |
| 3 | O `usuarios.sh` é executável | `ls -l ~/scripts/aula01/usuarios.sh` |
| 4 | O apelido SSH funciona | `ssh disciplina hostname` |
| 5 | O *script* está na máquina da AWS | `ssh disciplina 'ls ~/scripts/aula01'` |
| 6 | A entrega está na máquina da AWS e roda | `ssh disciplina '~/scripts/aula01/registro.sh'` |

---

## 💬 Para Discutir em Sala

- O `usuarios.sh` tem uma linha só. Em que momento vale a pena transformar um
  comando em *script*, e em que momento é exagero?
- O `who | wc -l` conta **sessões**, não pessoas. Se o mesmo usuário abrir três
  terminais, o número vira 3. Como você mudaria o *script* para contar pessoas
  distintas? (Dica: você ainda não tem as ferramentas para isso — vamos ter na
  Aula 04.)
- A chave `.pem` dá acesso total à sua máquina na AWS. O que acontece se ela
  vazar? Por que o `ssh` é tão rigoroso com as permissões desse arquivo?

---

## 📌 Para a Próxima Aula

Na **Aula 02** vamos trabalhar o capítulo `02_comandos_basicos`: navegação e
manipulação de arquivos e diretórios. O apelido `disciplina` e o diretório
`~/scripts` que você configurou hoje serão usados em **todas** as aulas seguintes.

> ⚠️ Se você não conseguiu fazer o `ssh disciplina` funcionar, resolva isso antes
> da próxima aula — todas as entregas a partir de agora são feitas nela.
