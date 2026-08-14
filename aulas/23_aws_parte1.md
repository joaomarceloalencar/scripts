# 🧪 Aula 23 — AWS (parte 1): CLI e Primeira Instância

**Disciplina:** Programação de *Scripts* — UFC Quixadá
**Material de apoio:** `slides/19_AWS`
**Sessão:** Semana 13 — terça, 03/11
**Entrega desta aula:** 0,7 ponto (Nota 3)
**Duração estimada:** 100 minutos

---

## 🎯 Objetivos da Aula

Ao final desta aula você deve ser capaz de:

- Instalar e configurar a AWS CLI com as credenciais do Academy.
- Consultar recursos com `aws ec2 describe-*` e filtrar a saída.
- Criar uma instância EC2 pela linha de comando.
- Recuperar o IP público e conectar por SSH.
- Encerrar recursos para não desperdiçar crédito.

## 🧰 Pré-requisitos

- **AWS Academy com o laboratório iniciado** (indicador verde).
- Aula 13 (`getopts`) e Aula 20 (`curl`, JSON).

## ⚙️ Antes de começar

A partir desta aula você usa a AWS CLI **de dentro da sua máquina de trabalho**, e
dali cria e acessa outras instâncias. Para isso, a chave precisa estar lá também.

Da sua **máquina local**, copie a chave para a máquina de trabalho:

```bash
scp ~/.ssh/labsuser.pem disciplina:~/.ssh/
ssh disciplina 'chmod 600 ~/.ssh/labsuser.pem && ls -l ~/.ssh/labsuser.pem'
```

> ⚠️ **A sua máquina de trabalho é uma instância EC2 da mesma conta.** Quando você
> listar instâncias pela CLI, ela vai aparecer junto com as que você criar.
> Identifique-a pela tag `Name` (`<seu_usuario>-trabalho`, definida na Aula 01) e
> nunca a encerre por engano. Detalhes no [guia de ambiente](00_ambiente.md).
>
> ⚠️ **As credenciais do Academy expiram** ao fim de cada sessão do laboratório. Se
> um comando falhar com `ExpiredToken`, volte ao Academy, clique em **AWS Details**
> e copie as credenciais novamente. Isso vai acontecer — não é erro seu.
>
> ⚠️ **O crédito é limitado e compartilhado.** Encerre as instâncias ao fim da aula.
> A Etapa 4 é obrigatória.

## 🗺️ Roteiro

| Etapa | Assunto | Tempo |
|---|---|---|
| 0 | Instalação e configuração | 20 min |
| 1 | Consultando recursos | 20 min |
| 2 | Criando a instância | 20 min |
| 3 | Conectando | 10 min |
| 4 | **Encerrando** | 5 min |
| 🏁 | Entrega | 25 min |

---

## 🧩 Etapa 0 — Instalação e configuração

### Ação

```bash
ssh disciplina
mkdir -p ~/scripts/aula23
cd ~/scripts/aula23

command -v aws && aws --version
```

Se não estiver instalada:

```bash
curl -s "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o awscliv2.zip
unzip -q awscliv2.zip
./aws/install -i ~/local/aws-cli -b ~/local/bin
export PATH="$HOME/local/bin:$PATH"
aws --version
```

Agora as credenciais. No AWS Academy, clique em **AWS Details → AWS CLI → Show**.
Você verá algo assim:

```
[default]
aws_access_key_id=ASIA...
aws_secret_access_key=...
aws_session_token=...
```

Copie esse bloco para o arquivo de credenciais:

```bash
mkdir -p ~/.aws
nano ~/.aws/credentials
chmod 600 ~/.aws/credentials
```

E configure a região e o formato:

```bash
cat > ~/.aws/config
[default]
region = us-east-1
output = json
```

Ctrl+D. Confirme que funcionou:

```bash
aws sts get-caller-identity
```

Saída esperada:

```json
{
    "UserId": "AROA...:user123",
    "Account": "123456789012",
    "Arn": "arn:aws:sts::123456789012:assumed-role/voclabs/user123"
}
```

> ⚠️ O `~/.aws/credentials` contém chaves de acesso à conta. `chmod 600` nele, e
> **nunca** o coloque em um repositório Git.

### ✅ Checkpoint 0

✔ `aws --version` responde a versão.
✔ `aws sts get-caller-identity` devolve o JSON com o `Account`.
✔ O `~/.aws/credentials` está com permissão `600`.

### ❓ Pergunta

O Academy fornece um `aws_session_token` além da chave e do segredo. Contas comuns
da AWS não têm esse terceiro campo. O que ele indica?

---

## 🧩 Etapa 1 — Consultando recursos

A CLI segue sempre o padrão `aws <serviço> <operação> [opções]`.

### Ação

```bash
aws ec2 describe-instances
```

A saída é enorme. É aí que entra o `--query`, que usa a linguagem **JMESPath** para
filtrar do lado do cliente:

```bash
aws ec2 describe-instances --query 'Reservations[*].Instances[*].InstanceId'
aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,State.Name]' --output table
aws ec2 describe-instances --query 'Reservations[*].Instances[*].InstanceId' --output text
```

O `--output` muda tudo:

| Formato | Quando usar |
|---|---|
| `json` | quando outro programa vai ler |
| `table` | quando **você** vai ler |
| `text` | quando um *script* em *shell* vai processar |

O `text` é o que interessa para nós — sai limpo, sem aspas:

```bash
aws ec2 describe-vpcs --query 'Vpcs[?IsDefault==`true`].VpcId' --output text
```

Guarde os dados de que vamos precisar:

```bash
VPC_ID=$(aws ec2 describe-vpcs --query 'Vpcs[?IsDefault==`true`].VpcId' --output text)
echo "VPC padrão: $VPC_ID"

SUBNET_ID=$(aws ec2 describe-subnets \
    --filters "Name=vpc-id,Values=$VPC_ID" \
    --query 'Subnets[0].SubnetId' --output text)
echo "Subrede: $SUBNET_ID"
```

Descubra a AMI mais recente do Ubuntu, em vez de fixar um ID que envelhece:

```bash
AMI_ID=$(aws ec2 describe-images \
    --owners 099720109477 \
    --filters "Name=name,Values=ubuntu/images/hvm-ssd*22.04*server*" \
              "Name=state,Values=available" \
    --query 'sort_by(Images, &CreationDate)[-1].ImageId' \
    --output text)
echo "AMI: $AMI_ID"
```

> 💡 `--filters` filtra no **servidor** (é rápido e reduz tráfego); `--query` filtra
> na **sua máquina**, depois da resposta chegar. Use `--filters` sempre que possível.

### ✅ Checkpoint 1

✔ `VPC_ID`, `SUBNET_ID` e `AMI_ID` estão preenchidos, sem espaços.
✔ `--output table` mostra uma tabela legível.

### ❓ Pergunta

O `sort_by(Images, &CreationDate)[-1]` pega a AMI mais recente. Por que isso é
melhor do que anotar o ID no *script*, como faziam os enunciados antigos?

---

## 🧩 Etapa 2 — Criando a instância

### Ação

Primeiro o grupo de segurança:

```bash
SG_ID=$(aws ec2 create-security-group \
    --group-name "aula23-$USER" \
    --description "Grupo da Aula 23" \
    --vpc-id "$VPC_ID" \
    --query 'GroupId' --output text)
echo "Grupo: $SG_ID"

aws ec2 authorize-security-group-ingress \
    --group-id "$SG_ID" --protocol tcp --port 22 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-id "$SG_ID" --protocol tcp --port 80 --cidr 0.0.0.0/0

aws ec2 describe-security-groups --group-ids "$SG_ID" \
    --query 'SecurityGroups[0].IpPermissions[*].FromPort' --output text
```

> ⚠️ `--cidr 0.0.0.0/0` libera para a internet inteira. Aceitável em um laboratório
> descartável, **inaceitável** em produção. O correto é restringir ao seu IP:
> `--cidr $(curl -s https://checkip.amazonaws.com)/32`.

Agora a instância:

```bash
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id "$AMI_ID" \
    --instance-type t2.micro \
    --key-name vockey \
    --security-group-ids "$SG_ID" \
    --subnet-id "$SUBNET_ID" \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$USER-aula23}]" \
    --query 'Instances[0].InstanceId' --output text)
echo "Instância: $INSTANCE_ID"
```

Ela nasce em `pending`. Acompanhe:

```bash
aws ec2 describe-instances --instance-ids "$INSTANCE_ID" \
    --query 'Reservations[0].Instances[0].State.Name' --output text

aws ec2 wait instance-running --instance-ids "$INSTANCE_ID"
echo "pronta"
```

O `aws ec2 wait` bloqueia até a condição ser satisfeita — é bem melhor que um laço
com `sleep`.

Recupere o IP público:

```bash
IP=$(aws ec2 describe-instances --instance-ids "$INSTANCE_ID" \
    --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)
echo "IP: $IP"
```

### ✅ Checkpoint 2

✔ `describe-instances` mostra o estado `running`.
✔ A variável `IP` tem um endereço válido, não `None`.
✔ O grupo de segurança tem as portas 22 e 80 liberadas.

### ❓ Pergunta

Se o `PublicIpAddress` vier como `None`, o que pode ter acontecido? Cite duas causas
possíveis.

---

## 🧩 Etapa 3 — Conectando

### Ação

```bash
chmod 600 ~/.ssh/labsuser.pem
ssh -i ~/.ssh/labsuser.pem -o StrictHostKeyChecking=no ubuntu@"$IP"
```

Dentro da instância:

```bash
hostname
lsb_release -a
df -h /
exit
```

E remotamente, sem abrir sessão (Aula 01):

```bash
ssh -i ~/.ssh/labsuser.pem -o StrictHostKeyChecking=no ubuntu@"$IP" 'uptime; free -m'
```

> 💡 O `-o StrictHostKeyChecking=no` evita a pergunta de confirmação. Em instâncias
> descartáveis isso é conveniente; em servidores permanentes, é uma má prática — a
> pergunta existe para detectar troca de servidor.

### ✅ Checkpoint 3

✔ O SSH conecta e o `hostname` é o da instância.
✔ O comando remoto sem sessão interativa funciona.

---

## 🧩 Etapa 4 — Encerrando (obrigatório)

### Ação

```bash
aws ec2 terminate-instances --instance-ids "$INSTANCE_ID" \
    --query 'TerminatingInstances[0].CurrentState.Name' --output text

aws ec2 wait instance-terminated --instance-ids "$INSTANCE_ID"

aws ec2 delete-security-group --group-id "$SG_ID"
```

Confirme que não sobrou nada rodando:

```bash
aws ec2 describe-instances \
    --filters "Name=instance-state-name,Values=running,pending" \
    --query 'Reservations[*].Instances[*].[InstanceId,Tags[?Key==`Name`].Value|[0]]' \
    --output table
```

> ⚠️ O grupo de segurança só pode ser apagado **depois** de a instância terminar —
> por isso o `wait` no meio.
>
> ⚠️ **A sua máquina de trabalho vai aparecer nessa tabela.** Ela é uma instância EC2
> da mesma conta — é dela que você está rodando estes comandos. Identifique-a pela
> tag `Name` (`<seu_usuario>-trabalho`, definida na Aula 01) e **nunca** a encerre.
> Confirme antes de qualquer `terminate-instances`:
>
> ```bash
> curl -s http://169.254.169.254/latest/meta-data/instance-id; echo
> ```
>
> Esse comando, rodado de dentro da sua máquina, devolve o ID **dela**. É o ID que
> não pode entrar em nenhum `terminate`.

### ✅ Checkpoint 4

✔ A tabela final mostra **apenas** a sua máquina de trabalho.
✔ A instância que você criou nesta aula não aparece mais.

---

## 🏁 Entrega da Aula — 0,7 ponto (Nota 3)

Individualmente, nos últimos 25 minutos.

Crie o *script* `~/scripts/aula23/criar_instancia.sh`, que automatiza tudo que você
fez na mão.

**Uso:** `./criar_instancia.sh -n <nome> [-t <tipo>] [-p <porta extra>]`

1. Trate as opções com `getopts`. A `-n` (nome da tag) é obrigatória; `-t` tem padrão
   `t2.micro` e `-p` é opcional.
2. O *script* deve, sem nada fixo no código além do dono da AMI:
   - descobrir a VPC padrão e uma subrede dela;
   - descobrir a AMI mais recente do Ubuntu 22.04;
   - criar um grupo de segurança liberando a porta 22 (e a porta extra, se `-p` for
     passada);
   - criar a instância com a tag `Name` igual ao valor de `-n`;
   - esperar até ela estar `running`;
   - imprimir o `InstanceId` e o IP público.
3. **Verificar cada etapa.** Se qualquer comando falhar, imprima no `stderr` qual
   etapa falhou e encerre com retorno diferente de zero.
4. Gravar o `InstanceId` e o `SecurityGroupId` em `~/scripts/aula23/recursos.txt`,
   para permitir a limpeza depois.
5. Criar também o `~/scripts/aula23/destruir.sh`, que lê o `recursos.txt`, encerra a
   instância, espera terminar, apaga o grupo de segurança e limpa o arquivo.

Saída esperada:

```
$ ./criar_instancia.sh -n servidor-web -p 80
Descobrindo VPC padrão... vpc-0a1b2c3d
Descobrindo AMI do Ubuntu... ami-0f1e2d3c
Criando grupo de segurança... sg-04a5b6c7
Liberando portas 22, 80...
Criando instância t2.micro...
Aguardando inicialização...
InstanceId: i-0123456789abcdef0
IP público: 54.234.12.98
```

### Critérios de correção

| # | Critério | Valor |
|---|---|---|
| 1 | `getopts` com `-n` obrigatória e padrões corretos | 0,10 |
| 2 | Descobre VPC, subrede e AMI dinamicamente | 0,15 |
| 3 | Cria o grupo com as portas certas e a instância com a tag | 0,15 |
| 4 | Espera ficar `running` e imprime o IP | 0,10 |
| 5 | Verifica cada etapa e falha com mensagem no `stderr` | 0,10 |
| 6 | O `destruir.sh` limpa todos os recursos criados | 0,10 |

Correção:

```bash
cd ~/scripts/aula23
./criar_instancia.sh; echo "retorno=$?"
./criar_instancia.sh -n teste-$USER -p 80
cat recursos.txt
ssh -i ~/.ssh/labsuser.pem -o StrictHostKeyChecking=no ubuntu@<IP> hostname
./destruir.sh
aws ec2 describe-instances --filters "Name=tag:Name,Values=teste-$USER" \
    --query 'Reservations[*].Instances[*].State.Name' --output text
```

O último comando deve responder `terminated` ou vazio.

> ⚠️ **Rode o `destruir.sh` antes de sair da sala.** Instâncias esquecidas consomem
> o crédito da turma inteira.

---

## ✅ Checklist de Encerramento

| # | Verificação | Comando |
|---|---|---|
| 1 | Os dois *scripts* são executáveis | `ls -l ~/scripts/aula23/*.sh` |
| 2 | Usa `getopts` | `grep -c getopts criar_instancia.sh` |
| 3 | Nada fixo: sem `ami-` no código | `grep -c "ami-" criar_instancia.sh` |
| 4 | **Só a máquina de trabalho rodando** | `aws ec2 describe-instances --filters "Name=instance-state-name,Values=running" --query 'Reservations[*].Instances[*].[Tags[?Key==`Name`].Value\|[0]]' --output text` — só a sua máquina de trabalho deve aparecer |
| 5 | Nenhum grupo de segurança órfão | `aws ec2 describe-security-groups --query 'SecurityGroups[?starts_with(GroupName, \`aula23\`)].GroupName' --output text` |

O item 3 deve responder `0`.

---

## 💬 Para Discutir em Sala

- Você criou a mesma infraestrutura duas vezes: uma na mão e outra por *script*.
  Quanto tempo levou cada uma? E na décima vez?
- O *script* cria recursos mas precisa de outro para destruí-los, e do `recursos.txt`
  para lembrar o que criou. Esse "livro-caixa" à mão é frágil. Guarde a incômodo:
  é exatamente o problema que o Terraform resolve, na Aula 25.

## 📌 Para a Próxima Aula

Na **Aula 24** vamos usar `--user-data` para provisionar a instância automaticamente
no *boot*, montar discos personalizados e transformar tudo em um *script* de
implantação completo.
