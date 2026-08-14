# 🧰 Ambiente da Disciplina — Sua Máquina na AWS Academy

**Disciplina:** Programação de *Scripts* — UFC Quixadá

Este documento não é uma aula. É a referência do ambiente de trabalho, para consulta
o semestre inteiro. Leia antes da Aula 01 e volte aqui sempre que algo parar de
funcionar.

---

## 🖥️ O que é o seu ambiente

Cada aluno tem uma **máquina virtual própria** (instância EC2) na AWS Academy. Todo o
trabalho da disciplina acontece nela:

- Você é `ubuntu` e tem `sudo` — pode instalar o que quiser e quebrar o que quiser.
- O diretório `~/scripts/aulaNN` guarda o trabalho de cada aula.
- Ninguém mais usa a sua máquina. Se ela quebrar, o prejuízo é só seu — e você pode
  criar outra.

A máquina é criada por você na [Aula 01](01_primeiro_script.md) e usada até o fim do
semestre.

---

## ⚠️ As três regras do AWS Academy

Estas três coisas vão te pegar de surpresa pelo menos uma vez. Leia agora.

### 1. A sessão do laboratório expira

O Learner Lab funciona por sessões com duração limitada. Quando a sessão acaba:

- **As instâncias são desligadas**, não destruídas.
- **Os dados no disco permanecem.** Seu `~/scripts` continua lá.
- As credenciais da AWS CLI param de valer.

Ao voltar, inicie o laboratório de novo e **ligue a instância**.

### 2. O IP público muda a cada religamento

Este é o incômodo diário. Toda vez que a instância é desligada e religada, ela ganha
um **IP público novo**. O `~/.ssh/config` que você configurou na Aula 01 fica
desatualizado, e o `ssh disciplina` passa a dar *timeout*.

A [rotina de início de aula](#-rotina-de-início-de-aula) resolve isso.

### 3. As credenciais da CLI expiram junto com a sessão

A partir da [Aula 23](23_aws_parte1.md) você usa a AWS CLI. As credenciais do Academy
incluem um `aws_session_token` temporário. Quando ele expira, qualquer comando `aws`
falha com `ExpiredToken` ou `InvalidClientTokenId`.

A correção é sempre a mesma: copiar as credenciais novas do Academy.

---

## 🚀 Rotina de início de aula

Faça isso no começo de **toda** aula. Leva dois minutos.

### 1. Inicie o laboratório

No AWS Academy, entre no curso, abra o laboratório e clique em **Start Lab**. Espere
o indicador ficar **verde**.

### 2. Ligue a sua instância

No console da AWS, vá em **EC2 → Instances**. Se a sua instância estiver `stopped`,
selecione-a e clique em **Instance state → Start instance**.

Espere o estado ficar `running` e o *status check* passar (leva 1 a 2 minutos).

### 3. Anote o novo IP público

Ainda na tela da instância, copie o valor de **Public IPv4 address**.

### 4. Atualize o apelido SSH

Na **sua máquina local**, edite o `~/.ssh/config` e troque o `HostName`:

```bash
nano ~/.ssh/config
```

```
Host disciplina
    HostName <COLE O NOVO IP AQUI>
    User ubuntu
    IdentityFile ~/.ssh/labsuser.pem
    IdentitiesOnly yes
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
```

### 5. Confirme

```bash
ssh disciplina hostname
```

Se responder o nome da máquina, você está pronto para a aula.

> 💡 **Automatize isso.** Depois da [Aula 07](07_variaveis_e_parametros.md) você já
> tem ferramentas para escrever um `atualizar_ip.sh` que recebe o IP como parâmetro e
> reescreve a linha do `HostName` com `sed`. Depois da
> [Aula 23](23_aws_parte1.md), dá para descobrir o IP sozinho com a AWS CLI, sem
> abrir o console. Faça — é o tipo de automação que a disciplina existe para ensinar.

---

## 🔑 A chave `labsuser.pem`

A AWS Academy usa um par de chaves chamado **`vockey`**. A chave privada é o arquivo
`labsuser.pem`, baixado em **AWS Details → Download PEM**.

Guarde-a em lugar fixo e com a permissão correta:

```bash
mkdir -p ~/.ssh
mv ~/Downloads/labsuser.pem ~/.ssh/
chmod 700 ~/.ssh
chmod 600 ~/.ssh/labsuser.pem
```

> ⚠️ Se o `ssh` reclamar de `UNPROTECTED PRIVATE KEY FILE`, a permissão está aberta
> demais. Rode o `chmod 600` de novo.
>
> ⚠️ **Nunca coloque o `labsuser.pem` em um repositório Git.** Quem tem a chave entra
> na sua máquina.

---

## ☁️ Credenciais da AWS CLI (a partir da Aula 23)

No Academy, clique em **AWS Details → AWS CLI → Show**. Copie o bloco e cole em
`~/.aws/credentials` **dentro da sua instância**:

```bash
mkdir -p ~/.aws
nano ~/.aws/credentials
chmod 600 ~/.aws/credentials
```

```
[default]
aws_access_key_id=ASIA...
aws_secret_access_key=...
aws_session_token=...
```

E a região, uma vez só:

```bash
cat > ~/.aws/config
[default]
region = us-east-1
output = json
```

Teste sempre com:

```bash
aws sts get-caller-identity
```

> ⚠️ **A sua própria máquina de trabalho é uma instância EC2 da mesma conta.** A
> partir da Aula 23, quando você listar instâncias com a CLI, ela vai aparecer no
> meio das que você criou.
>
> Marque a sua máquina com uma *tag* que a distinga — a Aula 01 pede a tag
> `Name = <seu_usuario>-trabalho`. Daí em diante, use filtros nos comandos:
>
> ```bash
> aws ec2 describe-instances \
>   --filters "Name=instance-state-name,Values=running" \
>   --query 'Reservations[*].Instances[*].[Tags[?Key==`Name`].Value|[0],InstanceId]' \
>   --output table
> ```
>
> **Nunca** rode um `terminate-instances` sem conferir o ID. Encerrar a própria
> máquina de trabalho no meio da aula é um jeito rápido de perder a entrega.

---

## 💾 O que persiste e o que não persiste

| Item | Sobrevive ao fim da sessão? |
|---|---|
| Arquivos em `~/scripts` | ✅ sim (ficam no disco EBS) |
| Pacotes instalados com `apt` | ✅ sim |
| Instância EC2 | ✅ sim, mas **desligada** |
| IP público | ❌ muda a cada religamento |
| Credenciais da AWS CLI | ❌ expiram |
| Processos em execução | ❌ morrem no desligamento |
| Sessões `tmux` | ❌ morrem no desligamento |

> 💡 **Faça cópia do seu trabalho.** O disco persiste, mas a instância pode ser
> perdida — por um erro seu, por um `terraform destroy` mal mirado ou pelo fim do
> crédito. Ao final de cada aula:
>
> ```bash
> scp -r disciplina:~/scripts ~/backup-scripts
> ```

---

## 🔧 Problemas comuns

| Sintoma | Causa provável | Solução |
|---|---|---|
| `ssh disciplina` dá *timeout* | IP mudou ou instância desligada | rotina de início de aula |
| `UNPROTECTED PRIVATE KEY FILE` | permissão da chave | `chmod 600 ~/.ssh/labsuser.pem` |
| `Permission denied (publickey)` | usuário errado | o usuário é `ubuntu`, não o seu nome |
| `REMOTE HOST IDENTIFICATION HAS CHANGED` | IP reciclado por outra máquina | o `UserKnownHostsFile /dev/null` do `config` evita isso |
| `ExpiredToken` no comando `aws` | credenciais expiraram | copie de novo em AWS Details |
| `Unable to locate credentials` | `~/.aws/credentials` ausente na instância | crie o arquivo **dentro** da instância |
| Laboratório não inicia | crédito esgotado | fale com o professor |

---

## 💰 Crédito

O laboratório tem orçamento limitado e **compartilhado com a turma**. Uma instância
esquecida ligada por um fim de semana consome crédito de todo mundo.

Por isso, todas as aulas do Bloco 3 terminam com uma etapa obrigatória de destruição,
e o *checklist* de encerramento verifica recursos órfãos. Não pule.

Ao final de cada aula, confira:

```bash
# Instâncias rodando além da sua máquina de trabalho
aws ec2 describe-instances \
  --filters "Name=instance-state-name,Values=running" \
  --query 'Reservations[*].Instances[*].[Tags[?Key==`Name`].Value|[0]]' --output text

# Volumes órfãos (desanexados, mas ainda cobrados)
aws ec2 describe-volumes --filters "Name=status,Values=available" \
  --query 'Volumes[*].VolumeId' --output text
```

O segundo comando deve sair vazio.
