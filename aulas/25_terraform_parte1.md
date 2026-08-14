# 🧪 Aula 25 — Terraform (parte 1): Infraestrutura Declarativa

**Disciplina:** Programação de *Scripts* — UFC Quixadá
**Material de apoio:** `slides/20_Terraform`
**Sessão:** Semana 14 — terça, 10/11
**Entrega desta aula:** 0,7 ponto (Nota 3)
**Duração estimada:** 100 minutos

---

## 🎯 Objetivos da Aula

Ao final desta aula você deve ser capaz de:

- Explicar a diferença entre imperativo e declarativo em infraestrutura.
- Escrever um `main.tf` com `provider`, `resource` e `data`.
- Executar o ciclo `init` → `plan` → `apply` → `destroy`.
- Entender o papel do arquivo de estado.
- Reconstruir, em Terraform, a infraestrutura da Aula 24.

## 🧰 Pré-requisitos

- Aulas 23 e 24. Credenciais da AWS configuradas e válidas.
- Tenha o `deploy.sh` da Aula 24 à mão para comparar.

## 🗺️ Roteiro

| Etapa | Assunto | Tempo |
|---|---|---|
| 0 | Instalação e o primeiro `main.tf` | 20 min |
| 1 | O ciclo de vida | 20 min |
| 2 | O estado | 15 min |
| 3 | `data`, `variable` e `output` | 20 min |
| 🏁 | Entrega | 25 min |

---

## 🧩 Etapa 0 — Instalação e o primeiro `main.tf`

### Ação

```bash
ssh disciplina
mkdir -p ~/scripts/aula25
cd ~/scripts/aula25

command -v terraform || {
    wget -q https://releases.hashicorp.com/terraform/1.9.8/terraform_1.9.8_linux_amd64.zip
    unzip -q terraform_1.9.8_linux_amd64.zip
    mkdir -p ~/local/bin && mv terraform ~/local/bin/
    export PATH="$HOME/local/bin:$PATH"
}
terraform version
```

Confirme que as credenciais estão válidas:

```bash
aws sts get-caller-identity
```

Agora o arquivo. A linguagem é o **HCL**:

```bash
cat > main.tf
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_security_group" "web" {
  name        = "aula25-${var.aluno}"
  description = "Grupo da Aula 25"

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "aula25-${var.aluno}"
  }
}

variable "aluno" {
  description = "Identificador do aluno"
  type        = string
}
```

Ctrl+D.

Os três blocos fundamentais:

| Bloco | Papel |
|---|---|
| `terraform` | de quais *providers* o projeto depende |
| `provider` | como falar com a nuvem (região, credenciais) |
| `resource` | **algo que o Terraform cria e gerencia** |
| `data` | algo que já existe e o Terraform apenas consulta |
| `variable` | entrada parametrizável |
| `output` | valor exposto ao final |

> 💡 A referência a um recurso segue o padrão `<tipo>.<nome>.<atributo>` — por
> exemplo, `aws_security_group.web.id`. É assim que os recursos se conectam, e é o
> que permite ao Terraform descobrir sozinho a ordem de criação.

### ✅ Checkpoint 0

✔ `terraform version` responde.
✔ O `main.tf` existe e o `terraform fmt` não reclama:

```bash
terraform fmt -check || terraform fmt
```

### ❓ Pergunta

Compare com o `deploy.sh` da Aula 24: lá você **mandou** criar o grupo e depois
liberar as portas, em ordem. Aqui você **descreveu** o grupo com as portas dentro.
Qual a diferença conceitual?

---

## 🧩 Etapa 1 — O ciclo de vida

### Ação

```bash
terraform init
```

O `init` baixa o *provider* da AWS e cria o `.terraform/`. Rode uma vez por projeto.

```bash
ls -a
du -sh .terraform
```

Agora o `plan` — ele mostra o que **seria** feito, sem fazer nada:

```bash
terraform plan -var="aluno=$USER"
```

Leia a saída com atenção. Os marcadores:

| Símbolo | Significado |
|---|---|
| `+` | será criado |
| `-` | será destruído |
| `~` | será alterado no lugar |
| `-/+` | será destruído e recriado |

Aplique:

```bash
terraform apply -var="aluno=$USER"
```

Ele mostra o plano de novo e pede confirmação. Digite `yes`.

Confirme pelo outro lado:

```bash
aws ec2 describe-security-groups --filters "Name=group-name,Values=aula25-$USER" \
    --query 'SecurityGroups[0].[GroupId,GroupName]' --output text
```

Agora a parte reveladora — rode o `apply` **de novo**:

```bash
terraform apply -var="aluno=$USER"
```

```
No changes. Your infrastructure matches the configuration.
```

Ele não criou um segundo grupo. Essa é a **idempotência**: o resultado descreve um
estado desejado, não uma sequência de ações.

Provoque uma divergência. Apague o grupo pela CLI e rode o `plan`:

```bash
SG=$(aws ec2 describe-security-groups --filters "Name=group-name,Values=aula25-$USER" \
    --query 'SecurityGroups[0].GroupId' --output text)
aws ec2 delete-security-group --group-id "$SG"
terraform plan -var="aluno=$USER"
```

O Terraform detecta que o recurso sumiu e propõe recriá-lo.

```bash
terraform apply -var="aluno=$USER" -auto-approve
```

### ✅ Checkpoint 1

✔ O primeiro `apply` criou o grupo.
✔ O segundo `apply` respondeu `No changes`.
✔ Depois de apagar o grupo por fora, o `plan` propôs recriá-lo.

### ❓ Pergunta

Rodar o `deploy.sh` da Aula 24 duas vezes criaria duas instâncias. Rodar o
`terraform apply` duas vezes não cria nada na segunda. De onde vem essa diferença?

---

## 🧩 Etapa 2 — O estado

### Ação

```bash
ls -l terraform.tfstate
terraform state list
terraform state show aws_security_group.web | head -20
```

O `terraform.tfstate` é um JSON que registra **o que o Terraform criou e com quais
atributos**. É o "livro-caixa" que faltava no seu `recursos.txt` da Aula 23 — mas
mantido automaticamente.

```bash
head -20 terraform.tfstate
grep -c '"type"' terraform.tfstate
```

> ⚠️ **O estado é crítico.** Se você o perder, o Terraform esquece o que criou e vai
> tentar criar tudo de novo — deixando os recursos antigos órfãos. Em equipe, ele
> **nunca** fica no disco local: vai para um *backend* remoto (S3 com trava no
> DynamoDB, por exemplo).
>
> ⚠️ **O estado guarda dados sensíveis** em texto claro — senhas, chaves, IPs
> privados. Nunca versione o `terraform.tfstate` no Git.

O `.gitignore` mínimo de um projeto Terraform:

```bash
cat > .gitignore
.terraform/
*.tfstate
*.tfstate.*
*.tfvars
```

Ctrl+D.

### ✅ Checkpoint 2

✔ `terraform state list` mostra `aws_security_group.web`.
✔ O `.gitignore` existe com as quatro entradas.

### ❓ Pergunta

O Terraform poderia consultar a AWS toda vez, em vez de manter estado. Por que ele
não faz isso? (Dica: como ele saberia que *aquele* grupo de segurança é dele?)

---

## 🧩 Etapa 3 — `data`, `variable` e `output`

### Ação

O bloco `data` consulta algo que **já existe** e você não gerencia:

```bash
cat > dados.tf
data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

output "vpc_id" {
  value = data.aws_vpc.default.id
}

output "ami_id" {
  value = data.aws_ami.ubuntu.id
}

output "subnet_ids" {
  value = data.aws_subnets.default.ids
}
```

Ctrl+D, e:

```bash
terraform apply -var="aluno=$USER" -auto-approve
terraform output
terraform output -raw ami_id
```

Compare com o que você fez na Aula 23 — três chamadas ao `aws ec2 describe-*` com
`--query` cheio de JMESPath. Aqui é declaração.

Variáveis podem ter valor padrão e vir de arquivo:

```bash
cat > variables.tf
variable "tipo_instancia" {
  description = "Tipo da instância EC2"
  type        = string
  default     = "t2.micro"
}

variable "tamanho_disco" {
  description = "Tamanho do disco raiz em GB"
  type        = number
  default     = 8
}
```

Ctrl+D.

```bash
cat > terraform.tfvars
aluno          = "SEU_USUARIO"
tipo_instancia = "t2.micro"
tamanho_disco  = 10
```

Ctrl+D — troque `SEU_USUARIO`. Com o `terraform.tfvars` presente, o `-var` deixa de
ser necessário:

```bash
terraform plan
```

A precedência, da menor para a maior: `default` → `terraform.tfvars` →
variável de ambiente `TF_VAR_nome` → `-var` na linha de comando.

Limpe tudo:

```bash
terraform destroy -auto-approve
terraform state list
```

### ✅ Checkpoint 3

✔ `terraform output` mostra `vpc_id`, `ami_id` e `subnet_ids`.
✔ Com o `terraform.tfvars`, o `plan` roda sem `-var`.
✔ Depois do `destroy`, o `state list` está vazio.

### ❓ Pergunta

`data "aws_vpc"` e `resource "aws_security_group"` parecem blocos irmãos. Qual a
diferença essencial entre eles, do ponto de vista do que o Terraform faz no
`destroy`?

---

## 🏁 Entrega da Aula — 0,7 ponto (Nota 3)

Individualmente, nos últimos 25 minutos.

Reconstrua, em Terraform, a infraestrutura que você criou com *shell script* na
Aula 24. Trabalhe em `~/scripts/aula25/entrega/`.

Organize em **quatro arquivos**:

| Arquivo | Conteúdo |
|---|---|
| `main.tf` | `terraform`, `provider` e os `resource` |
| `dados.tf` | os blocos `data` |
| `variables.tf` | as declarações de `variable` |
| `outputs.tf` | as declarações de `output` |

A infraestrutura deve ter:

1. Um **grupo de segurança** liberando as portas 22 e 80 na entrada, e tudo na saída.
2. Uma **instância EC2** que:
   - use a AMI mais recente do Ubuntu 22.04, vinda de um `data`;
   - seja do tipo definido pela variável `tipo_instancia` (padrão `t2.micro`);
   - use a chave `vockey`;
   - tenha o disco raiz do tamanho da variável `tamanho_disco` (padrão `8`), com
     `delete_on_termination = true`;
   - receba o `user_data` que instala o **nginx** e publica uma página com o nome do
     aluno (reaproveite o da Aula 24, com `file()` ou `templatefile()`);
   - tenha a tag `Name` com o valor `<aluno>-aula25`.
3. **Três `output`**: o `id` da instância, o IP público e a URL completa
   (`http://<ip>`).

### Critérios de correção

| # | Critério | Valor |
|---|---|---|
| 1 | Os quatro arquivos existem, com o conteúdo separado corretamente | 0,10 |
| 2 | A AMI vem de um `data`, não fixa no código | 0,10 |
| 3 | O grupo de segurança tem as regras certas | 0,10 |
| 4 | A instância sobe com disco e tags conforme as variáveis | 0,15 |
| 5 | O `user_data` funciona: a porta 80 responde | 0,15 |
| 6 | Os três `output` aparecem no `terraform output` | 0,10 |

Correção:

```bash
cd ~/scripts/aula25/entrega
terraform init
terraform plan
terraform apply -auto-approve
terraform output
curl -s "$(terraform output -raw url)" | head -5
grep -c "ami-" *.tf          # deve ser 0
terraform destroy -auto-approve
```

> ⚠️ **Rode o `terraform destroy` antes de sair.** É o item 5 do *checklist*.

---

## ✅ Checklist de Encerramento

| # | Verificação | Comando |
|---|---|---|
| 1 | O `terraform validate` passa | `terraform validate` |
| 2 | O `terraform fmt` não reclama | `terraform fmt -check` |
| 3 | Nenhuma AMI fixa no código | `grep -c "ami-" *.tf` |
| 4 | O estado não está no Git | `cat .gitignore` |
| 5 | **Tudo destruído** | `terraform state list` |
| 6 | **Só a máquina de trabalho rodando** | `aws ec2 describe-instances --filters "Name=instance-state-name,Values=running" --query 'Reservations[*].Instances[*].[Tags[?Key==`Name`].Value\|[0]]' --output text` — só a sua máquina de trabalho deve aparecer |

Os itens 3, 5 e 6 devem sair vazios ou responder `0`.

---

## 💬 Para Discutir em Sala

- Conte as linhas do seu `deploy.sh` (Aula 24) e as dos seus `.tf`. Qual a diferença?
  E, mais importante: qual dos dois você conseguiria ler daqui a seis meses?
- O Terraform mantém estado em um arquivo. Isso resolve um problema e cria outro.
  Qual é o novo problema, e como as equipes o resolvem?

## 📌 Para a Próxima Aula

Na **Aula 26** vamos a duas máquinas se comunicando: `count`, `for_each`, referências
entre recursos e grupos de segurança que se apontam mutuamente. É a infraestrutura
que o Ansible vai configurar nas Aulas 27 e 28.
