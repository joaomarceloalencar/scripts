# 🧪 Aula 29 — Projeto Integrador (parte 1): Provisionamento

**Disciplina:** Programação de *Scripts* — UFC Quixadá
**Material de apoio:** `slides/19` a `slides/21` (revisão do Bloco 3)
**Sessão:** Semana 16 — terça, 24/11
**Entrega desta aula:** 0,7 ponto (Nota 3)
**Duração estimada:** 100 minutos

---

## 🎯 O Projeto

As Aulas 29 e 30 formam **um único projeto**, entregue em duas partes:

| Aula | Entrega | Vale |
|---|---|---|
| 29 | A infraestrutura em Terraform, funcionando | 0,7 |
| 30 | A configuração em Ansible e o orquestrador | 0,9 |

O objetivo é provisionar e configurar, **do zero e com um comando só**, uma
aplicação web de três camadas na AWS.

```
                    Internet
                       │
                       ▼
              ┌─────────────────┐
              │   web (nginx)   │  porta 80 aberta ao mundo
              │   grupo: web    │  SSH aberto
              └────────┬────────┘
                       │ 8080
                       ▼
              ┌─────────────────┐
              │  app (Python)   │  porta 8080, só do grupo web
              │   grupo: app    │  SSH só do grupo web
              └────────┬────────┘
                       │ 3306
                       ▼
              ┌─────────────────┐
              │  banco (MySQL)  │  porta 3306, só do grupo app
              │  grupo: banco   │  SSH só do grupo web
              └─────────────────┘
```

Cada camada só aceita conexão da camada imediatamente acima. A máquina `web` é a
única com acesso externo — as outras duas são alcançadas **através dela**.

## 🧰 Pré-requisitos

- Aulas 25 e 26 (Terraform), 27 e 28 (Ansible).
- Credenciais AWS válidas.

> ⚠️ Três instâncias `t2.micro` consomem crédito mais rápido. **Destrua tudo ao fim
> de cada aula** e recrie na seguinte — é justamente isso que a automação torna
> barato.

## 🗺️ Roteiro

| Etapa | Assunto | Tempo |
|---|---|---|
| 0 | Estrutura do projeto | 15 min |
| 1 | Rede e segurança em camadas | 25 min |
| 🏁 | Entrega — a infraestrutura | 60 min |

---

## 🧩 Etapa 0 — Estrutura do projeto

### Ação

```bash
ssh disciplina
mkdir -p ~/scripts/projeto/{infra,config}
cd ~/scripts/projeto
export PATH="$HOME/local/bin:$PATH"
aws sts get-caller-identity
```

A organização que vamos seguir:

```
projeto/
├── infra/                 ← Aula 29: Terraform
│   ├── main.tf
│   ├── dados.tf
│   ├── seguranca.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── locals.tf
├── config/                ← Aula 30: Ansible
│   ├── ansible.cfg
│   ├── aws.aws_ec2.yml
│   ├── group_vars/
│   ├── roles/
│   └── site.yml
└── implantar.sh           ← Aula 30: o orquestrador
```

```bash
cat > .gitignore
.terraform/
*.tfstate
*.tfstate.*
*.tfvars
*.retry
__pycache__/
```

Ctrl+D.

### ✅ Checkpoint 0

✔ A árvore de diretórios existe.
✔ `aws sts get-caller-identity` responde.

---

## 🧩 Etapa 1 — Rede e segurança em camadas

O ponto central do projeto é o encadeamento dos grupos de segurança. Vamos montá-lo
junto, porque é onde todo mundo erra.

### Ação

```bash
cd ~/scripts/projeto/infra
cat > seguranca.tf
resource "aws_security_group" "web" {
  name        = "${local.prefixo}-web"
  description = "Camada web: HTTP e SSH do mundo"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

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

  tags = merge(local.tags_comuns, { Name = "${local.prefixo}-web" })
}

resource "aws_security_group" "app" {
  name        = "${local.prefixo}-app"
  description = "Camada app: 8080 e SSH apenas da web"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description     = "Aplicacao"
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.web.id]
  }

  ingress {
    description     = "SSH via web"
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = [aws_security_group.web.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.tags_comuns, { Name = "${local.prefixo}-app" })
}
```

Ctrl+D.

Repare na cadeia: `app` referencia `web`. O grupo do banco vai referenciar `app` —
é a sua tarefa na entrega.

> ⚠️ **A armadilha do SSH.** Se o grupo do `app` só aceita SSH vindo do grupo `web`,
> você **não consegue** conectar nele direto da sua máquina. Isso é o desejado — mas
> significa que o Ansible precisa passar pela `web`. A solução é o `ProxyJump`:
>
> ```bash
> ssh -i ~/.ssh/labsuser.pem -J ubuntu@<IP_WEB> ubuntu@<IP_PRIVADO_APP>
> ```
>
> No Ansible, isso vira `ansible_ssh_common_args` no `group_vars`. Você vai precisar
> disso na Aula 30 — pense nisso já ao escrever os `output`.

Complete os arquivos de apoio:

```bash
cat > locals.tf
locals {
  prefixo = "${var.aluno}-projeto"

  tags_comuns = {
    Disciplina = "Programacao de Scripts"
    Aluno      = var.aluno
    Semestre   = "2026.2"
    Projeto    = "integrador"
  }

  camadas = {
    web   = { tipo = "t2.micro", grupo = "web" }
    app   = { tipo = "t2.micro", grupo = "app" }
    banco = { tipo = "t2.micro", grupo = "banco" }
  }
}
```

Ctrl+D.

```bash
cp ~/scripts/aula25/dados.tf .
cat dados.tf
```

### ✅ Checkpoint 1

✔ `terraform init && terraform validate` passa com o que existe até agora.
✔ Você entendeu por que o `app` não será acessível por SSH direto.

### ❓ Pergunta

A máquina `web` é a única com SSH aberto ao mundo. Isso tem nome em arquitetura de
redes: *bastion host*, ou *jump host*. Qual a vantagem de segurança dessa
concentração — e qual o risco?

---

## 🏁 Entrega da Aula — 0,7 ponto (Nota 3)

Você tem **60 minutos**. Individual.

Complete a infraestrutura em `~/scripts/projeto/infra/`.

### Requisitos

1. **Três instâncias**, criadas com **`for_each`** sobre `local.camadas`:
   - Ubuntu, via `data` (nada fixo);
   - tipo vindo do mapa;
   - chave `vockey`;
   - tag `Name` no padrão `<aluno>-projeto-<camada>`;
   - tag **`grupo`** com o valor da camada — é o que o Ansible vai usar na Aula 30;
   - as tags comuns do `locals` aplicadas em todas.

2. **Três grupos de segurança**, encadeados:

   | Grupo | Entrada permitida |
   |---|---|
   | `web` | 80 e 22 de `0.0.0.0/0` |
   | `app` | 8080 e 22 apenas do grupo `web` |
   | `banco` | 3306 apenas do grupo `app`; 22 apenas do grupo `web` |

3. **Disco** de 10 GB em todas, com `delete_on_termination = true`.

4. **`output`** que a Aula 30 vai consumir:
   - `ip_web` — IP público da web;
   - `ip_app_privado` e `ip_banco_privado`;
   - `ids` — mapa de camada para *instance id*;
   - `comando_ssh` — a linha pronta de SSH para a máquina web.

5. O `terraform validate` e o `terraform fmt -check` devem passar.

### Critérios de correção

| # | Critério | Valor |
|---|---|---|
| 1 | As três instâncias são criadas com `for_each` | 0,15 |
| 2 | As tags `grupo` e `Name` estão corretas nas três | 0,10 |
| 3 | O encadeamento dos grupos de segurança está correto | 0,20 |
| 4 | O disco de 10 GB com `delete_on_termination` | 0,05 |
| 5 | Os cinco `output` funcionam | 0,10 |
| 6 | `validate` e `fmt -check` passam; nada fixo no código | 0,10 |

Correção:

```bash
cd ~/scripts/projeto/infra
terraform init && terraform validate && terraform fmt -check
terraform apply -auto-approve
terraform output

# As três existem, com as tags certas
aws ec2 describe-instances \
  --filters "Name=tag:Aluno,Values=$USER" "Name=instance-state-name,Values=running" \
  --query 'Reservations[*].Instances[*].[Tags[?Key==`grupo`].Value|[0],InstanceType]' \
  --output table

# A web responde SSH
ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 \
    -i ~/.ssh/labsuser.pem ubuntu@$(terraform output -raw ip_web) hostname

# O banco NÃO responde SSH direto (deve dar timeout)
timeout 10 ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 \
    -i ~/.ssh/labsuser.pem ubuntu@$(terraform output -raw ip_banco_privado) hostname \
    && echo "FALHOU: banco acessível" || echo "OK: banco isolado"

# Mas responde ATRAVÉS da web
ssh -o StrictHostKeyChecking=no -i ~/.ssh/labsuser.pem \
    -J ubuntu@$(terraform output -raw ip_web) \
    ubuntu@$(terraform output -raw ip_banco_privado) hostname

grep -c "ami-" *.tf     # deve ser 0
```

> ⚠️ **Destrua tudo antes de sair**: `terraform destroy -auto-approve`.
> Você recria em 3 minutos na Aula 30 — é para isso que serve o Terraform.

---

## ✅ Checklist de Encerramento

| # | Verificação | Comando |
|---|---|---|
| 1 | `terraform validate` passa | `terraform validate` |
| 2 | Usa `for_each`, não três blocos repetidos | `grep -c "resource \"aws_instance\"" *.tf` |
| 3 | Sem AMI fixa | `grep -c "ami-" *.tf` |
| 4 | O `ProxyJump` funciona para o banco | veja o comando de correção |
| 5 | **Tudo destruído** | `terraform state list` |
| 6 | Nenhuma instância órfã | `aws ec2 describe-instances --filters "Name=tag:Aluno,Values=$USER" "Name=instance-state-name,Values=running" --query 'Reservations[*].Instances[*].InstanceId' --output text` |

O item 2 deve responder `1`. Os itens 3, 5 e 6 devem sair vazios ou `0`.

---

## 💬 Para Discutir em Sala

- A camada de banco não tem IP público e não é acessível de fora. Como você faria
  um *backup* dela para a sua máquina?
- Você destruiu a infraestrutura ao fim da aula e vai recriá-la na próxima. Isso
  seria impensável há 15 anos. O que mudou?

## 📌 Para a Próxima Aula

A **Aula 30** fecha a disciplina: o Ansible configurando as três camadas através do
*bastion*, e um `implantar.sh` que roda tudo com um comando. Vale **0,9 ponto**.

Traga o `infra/` funcionando — a Aula 30 depende dele.
