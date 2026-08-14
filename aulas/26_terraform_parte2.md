# 🧪 Aula 26 — Terraform (parte 2): Vários Recursos

**Disciplina:** Programação de *Scripts* — UFC Quixadá
**Material de apoio:** `slides/20_Terraform`
**Sessão:** Semana 14 — quarta, 11/11
**Entrega desta aula:** 0,7 ponto (Nota 3)
**Duração estimada:** 100 minutos

---

## 🎯 Objetivos da Aula

Ao final desta aula você deve ser capaz de:

- Criar vários recursos com `count` e com `for_each`.
- Ligar recursos entre si por referência, deixando o Terraform ordenar a criação.
- Escrever grupos de segurança que se referenciam mutuamente.
- Usar `locals` e `templatefile()` para reduzir repetição.
- Entregar uma infraestrutura de duas máquinas, cliente e banco de dados.

## 🧰 Pré-requisitos

- Aula 25 concluída. Credenciais da AWS válidas.

> ⚠️ Renove as credenciais do Academy antes de começar. Confirme com
> `aws sts get-caller-identity`.

## 🗺️ Roteiro

| Etapa | Assunto | Tempo |
|---|---|---|
| 0 | Dependências entre recursos | 15 min |
| 1 | `count` e `for_each` | 25 min |
| 2 | Grupos que se referenciam | 20 min |
| 3 | `locals` e `templatefile()` | 15 min |
| 🏁 | Entrega | 25 min |

---

## 🧩 Etapa 0 — Dependências entre recursos

### Ação

```bash
ssh disciplina
mkdir -p ~/scripts/aula26
cd ~/scripts/aula26
export PATH="$HOME/local/bin:$PATH"
```

Copie a base da aula anterior:

```bash
cp ~/scripts/aula25/dados.tf .
cat > main.tf
terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}

provider "aws" {
  region = "us-east-1"
}

variable "aluno" {
  type = string
}

resource "aws_security_group" "acesso" {
  name        = "aula26-${var.aluno}"
  description = "SSH de qualquer lugar"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "exemplo" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t2.micro"
  key_name               = "vockey"
  subnet_id              = data.aws_subnets.default.ids[0]
  vpc_security_group_ids = [aws_security_group.acesso.id]

  tags = { Name = "${var.aluno}-exemplo" }
}
```

Ctrl+D, e:

```bash
terraform init
terraform plan -var="aluno=$USER"
```

Repare: a instância referencia `aws_security_group.acesso.id`. O Terraform lê essa
referência e **deduz** que o grupo precisa existir primeiro. Você não escreveu
nenhuma ordem.

Veja o grafo de dependências:

```bash
terraform graph | head -20
```

Quando não há referência mas a ordem importa, existe o `depends_on` explícito — mas
ele é raro e quase sempre sinal de que faltou uma referência.

### ✅ Checkpoint 0

✔ O `plan` mostra 2 recursos a criar.
✔ `terraform graph` mostra a instância dependendo do grupo.

### ❓ Pergunta

O `deploy.sh` da Aula 24 criava o grupo, esperava, e só então criava a instância —
tudo na ordem escrita por você. Aqui a ordem é deduzida. O que isso permite que o
Terraform faça, que o *script* não podia?

---

## 🧩 Etapa 1 — `count` e `for_each`

### Ação — `count`

```bash
cat > count_exemplo.tf
resource "aws_instance" "trabalhador" {
  count = 3

  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t2.micro"
  key_name               = "vockey"
  subnet_id              = data.aws_subnets.default.ids[0]
  vpc_security_group_ids = [aws_security_group.acesso.id]

  tags = {
    Name = "${var.aluno}-trabalhador-${count.index}"
  }
}

output "ips_trabalhadores" {
  value = aws_instance.trabalhador[*].public_ip
}
```

Ctrl+D, e:

```bash
terraform plan -var="aluno=$USER" | grep -E "will be created|Plan:"
```

O `count.index` vai de 0 a 2, e os recursos viram uma lista:
`aws_instance.trabalhador[0]`, `[1]`, `[2]`.

> ⚠️ **O problema do `count`.** Se você mudar de 3 para 2, o Terraform destrói o
> `[2]`. Mas se você quisesse remover o **do meio**, ele renumera tudo — destruindo
> e recriando recursos que deveriam ficar intactos. Por isso o `count` só serve para
> recursos **idênticos e intercambiáveis**.

### Ação — `for_each`

```bash
rm count_exemplo.tf
cat > foreach_exemplo.tf
variable "maquinas" {
  type = map(string)
  default = {
    cliente = "t2.micro"
    banco   = "t2.micro"
  }
}

resource "aws_instance" "servidor" {
  for_each = var.maquinas

  ami                    = data.aws_ami.ubuntu.id
  instance_type          = each.value
  key_name               = "vockey"
  subnet_id              = data.aws_subnets.default.ids[0]
  vpc_security_group_ids = [aws_security_group.acesso.id]

  tags = {
    Name  = "${var.aluno}-${each.key}"
    grupo = each.key
  }
}

output "servidores" {
  value = { for k, v in aws_instance.servidor : k => v.public_ip }
}
```

Ctrl+D, e:

```bash
terraform plan -var="aluno=$USER" | grep -E "will be created|Plan:"
```

Agora os recursos são endereçados por **chave**: `aws_instance.servidor["cliente"]`.
Remover o `banco` do mapa não afeta o `cliente`.

| | `count` | `for_each` |
|---|---|---|
| Endereço | por índice `[0]` | por chave `["nome"]` |
| Entrada | número | mapa ou conjunto |
| Remover do meio | renumera e recria | não afeta os outros |
| Quando usar | réplicas idênticas | recursos com identidade |

Aplique e confira:

```bash
terraform apply -var="aluno=$USER" -auto-approve
terraform output servidores
terraform state list
```

### ✅ Checkpoint 1

✔ `terraform state list` mostra `aws_instance.servidor["cliente"]` e `["banco"]`.
✔ `terraform output servidores` mostra um mapa com os dois IPs.

### ❓ Pergunta

Você tem um cluster de 5 máquinas iguais e um conjunto de 3 serviços distintos. Qual
mecanismo para cada caso, e por quê?

---

## 🧩 Etapa 2 — Grupos que se referenciam

Cenário real: o banco de dados deve aceitar conexões **apenas do cliente**, não da
internet.

### Ação

```bash
cat > seguranca.tf
resource "aws_security_group" "cliente" {
  name        = "aula26-cliente-${var.aluno}"
  description = "Maquina cliente: SSH de fora"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "cliente-${var.aluno}" }
}

resource "aws_security_group" "banco" {
  name        = "aula26-banco-${var.aluno}"
  description = "Banco: MySQL apenas do cliente"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description     = "SSH via cliente"
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = [aws_security_group.cliente.id]
  }

  ingress {
    description     = "MySQL apenas do cliente"
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.cliente.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "banco-${var.aluno}" }
}
```

Ctrl+D.

O `security_groups` no lugar de `cidr_blocks` é a construção-chave: em vez de liberar
uma faixa de IPs, ele libera **quem pertence àquele outro grupo**. Os IPs podem mudar;
a regra continua valendo.

```bash
terraform plan -var="aluno=$USER" | grep -E "will be created|Plan:"
```

> ⚠️ **Cuidado com referências circulares.** Se o grupo A referencia o B no `ingress`
> e o B referencia o A, o Terraform não consegue ordenar e falha com
> `Cycle: ...`. A saída é usar `aws_security_group_rule` como recurso separado.

### ✅ Checkpoint 2

✔ O `plan` mostra os dois grupos.
✔ O grupo `banco` não tem nenhum `cidr_blocks` no `ingress`.

### ❓ Pergunta

Por que liberar por grupo de segurança é melhor que liberar pelo IP privado da outra
máquina, mesmo dentro da mesma VPC?

---

## 🧩 Etapa 3 — `locals` e `templatefile()`

### Ação — `locals`

O `locals` guarda valores calculados, usados em vários lugares:

```bash
cat > locais.tf
locals {
  prefixo = "${var.aluno}-aula26"

  tags_comuns = {
    Disciplina = "Programacao de Scripts"
    Aluno      = var.aluno
    Semestre   = "2026.2"
  }
}
```

Ctrl+D. Use nas tags:

```
tags = merge(local.tags_comuns, { Name = "${local.prefixo}-cliente" })
```

A diferença entre `variable` e `local`: a `variable` é **entrada** do módulo (quem
usa define); o `local` é **cálculo interno** (você define uma vez e reaproveita).

### Ação — `templatefile()`

Na Aula 24 o `user_data` era fixo. Agora ele pode receber valores:

```bash
cat > init.sh.tpl
#!/bin/bash
exec > >(tee /var/log/user-data.log) 2>&1
set -x

apt-get update -y
apt-get install -y ${pacotes}

echo "${papel}" > /etc/papel-da-maquina
hostnamectl set-hostname "${nome_host}"
```

Ctrl+D. E no recurso:

```
user_data = templatefile("${path.module}/init.sh.tpl", {
  pacotes   = "nginx curl"
  papel     = "cliente"
  nome_host = "${local.prefixo}-cliente"
})
```

> ⚠️ Dentro do `.tpl`, `${variavel}` é interpolação **do Terraform**. Se você
> precisar de uma variável de *shell* literal, escreva `$${VAR}` — o `$$` escapa.
> Esse é o erro número um em `templatefile`.

Limpe tudo antes da entrega:

```bash
terraform destroy -var="aluno=$USER" -auto-approve
rm -f foreach_exemplo.tf
```

### ✅ Checkpoint 3

✔ `terraform validate` passa com o `locals` e o `templatefile`.
✔ Você entendeu a diferença entre `${}` e `$${}` no arquivo de *template*.
✔ O `destroy` limpou tudo.

### ❓ Pergunta

O que aconteceria se você escrevesse `$(hostname)` dentro do `.tpl` sem escapar?

---

## 🏁 Entrega da Aula — 0,7 ponto (Nota 3)

Individualmente, nos últimos 25 minutos.

Em `~/scripts/aula26/entrega/`, escreva a configuração Terraform que provisiona a
infraestrutura que o Ansible vai configurar nas Aulas 27 e 28.

**Duas instâncias**, ambas Ubuntu e `t2.micro`:

| Máquina | Tag `grupo` | Acesso |
|---|---|---|
| Cliente | `cliente` | SSH liberado da internet |
| Banco de dados | `bancodedados` | SSH e MySQL (3306) **apenas do cliente** |

Requisitos:

1. Organize em `main.tf`, `dados.tf`, `variables.tf`, `outputs.tf` e `locals.tf`.
2. A AMI vem de um `data` — nada de ID fixo.
3. Crie as duas instâncias com **`for_each`**, não com dois blocos `resource`
   repetidos.
4. Cada instância deve ter a tag `grupo` com o valor da tabela — o Ansible vai usar
   essa tag no inventário dinâmico.
5. O grupo de segurança do banco deve referenciar o **grupo do cliente**, não um
   bloco CIDR.
6. Exponha como `output`: o IP público de cada máquina, o **IP privado do banco** e
   os IDs das instâncias.

### Critérios de correção

| # | Critério | Valor |
|---|---|---|
| 1 | Arquivos organizados e `terraform validate` passa | 0,10 |
| 2 | AMI vinda de `data`, sem ID fixo | 0,05 |
| 3 | As duas instâncias criadas com `for_each` | 0,15 |
| 4 | As tags `grupo` estão corretas nas duas | 0,10 |
| 5 | O banco só aceita 22 e 3306 vindos do grupo do cliente | 0,20 |
| 6 | Os `output` trazem IPs públicos, IP privado do banco e IDs | 0,10 |

Correção:

```bash
cd ~/scripts/aula26/entrega
terraform init && terraform validate && terraform fmt -check
terraform apply -auto-approve
terraform output
grep -c "ami-" *.tf                      # deve ser 0
grep -c "for_each" *.tf                  # deve ser >= 1

# O banco NÃO pode aceitar SSH da internet:
timeout 10 ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 \
    -i ~/.ssh/labsuser.pem ubuntu@$(terraform output -raw ip_banco) hostname \
    && echo "FALHOU: banco acessível de fora" || echo "OK: banco protegido"

terraform destroy -auto-approve
```

> ⚠️ **Não destrua a entrega ainda se quiser reaproveitá-la na Aula 27** — mas se
> for deixar de pé, avise o professor. Instâncias esquecidas consomem o crédito da
> turma.

---

## ✅ Checklist de Encerramento

| # | Verificação | Comando |
|---|---|---|
| 1 | `terraform validate` passa | `terraform validate` |
| 2 | Usa `for_each` | `grep -c for_each *.tf` |
| 3 | Sem AMI fixa | `grep -c "ami-" *.tf` |
| 4 | As tags `grupo` existem | `terraform state show 'aws_instance.maquina["banco"]' \| grep grupo` |
| 5 | **Estado limpo ou instâncias autorizadas** | `terraform state list` |

---

## 💬 Para Discutir em Sala

- Você liberou o MySQL por **grupo de segurança**, não por IP. Se amanhã o cliente
  for substituído por outra instância, a regra continua valendo? Por quê?
- O `for_each` sobre um mapa criou duas máquinas diferentes com um bloco só. Onde
  está o limite dessa abordagem — quando duas máquinas ficam diferentes demais?

## 📌 Para a Próxima Aula

A **Aula 27** inicia o Ansible (`slides/21_Ansible`). Vamos configurar exatamente as
máquinas que você acabou de provisionar. O Terraform cria; o Ansible configura.

Guarde os arquivos `.tf` desta aula — você vai reutilizá-los.
