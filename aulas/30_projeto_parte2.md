# 🧪 Aula 30 — Projeto Integrador (parte 2): Configuração e Orquestração

**Disciplina:** Programação de *Scripts* — UFC Quixadá
**Material de apoio:** `slides/19` a `slides/21` (revisão do Bloco 3)
**Sessão:** Semana 16 — quarta, 25/11
**Entrega desta aula:** 0,9 ponto (Nota 3) — *última entrega da disciplina*
**Duração estimada:** 100 minutos

---

## 🎯 Objetivos da Aula

Fechar o projeto iniciado na Aula 29:

- Configurar as três camadas com Ansible, através do *bastion*.
- Usar inventário dinâmico com `ProxyJump` para as máquinas sem IP público.
- Escrever o orquestrador em *shell* que amarra Terraform e Ansible.
- Validar a aplicação ponta a ponta.

Esta aula fecha a Nota 3 e a disciplina. O que você vai escrever aqui usa **todos os
três blocos**: *shell script* (Blocos 1 e 2) para orquestrar, e as ferramentas de
nuvem (Bloco 3) para o resto.

## 🧰 Pré-requisitos

- Aula 29 entregue: o `infra/` funcionando.
- Credenciais AWS válidas.

## 🗺️ Roteiro

| Etapa | Assunto | Tempo |
|---|---|---|
| 0 | Subindo a infraestrutura | 10 min |
| 1 | Inventário dinâmico com *bastion* | 25 min |
| 🏁 | Entrega — configuração e orquestrador | 65 min |

---

## 🧩 Etapa 0 — Subindo a infraestrutura

### Ação

```bash
ssh disciplina
cd ~/scripts/projeto/infra
export PATH="$HOME/local/bin:$PATH"
aws sts get-caller-identity

terraform apply -auto-approve
terraform output
```

Guarde os valores:

```bash
IP_WEB=$(terraform output -raw ip_web)
echo "bastion: $IP_WEB"
```

Aguarde o SSH aceitar conexões:

```bash
for i in $(seq 1 20); do
    ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 \
        -i ~/.ssh/labsuser.pem ubuntu@"$IP_WEB" true 2>/dev/null && break
    echo "aguardando SSH... ($i)"
    sleep 10
done
echo "pronto"
```

### ✅ Checkpoint 0

✔ `terraform output` mostra os cinco valores.
✔ O SSH na máquina web funciona.

---

## 🧩 Etapa 1 — Inventário dinâmico com *bastion*

Aqui está o problema novo desta aula: as máquinas `app` e `banco` **não têm IP
público**. O inventário dinâmico precisa usar o IP **privado** e passar pela `web`.

### Ação

```bash
cd ~/scripts/projeto/config
cat > aws.aws_ec2.yml
---
plugin: amazon.aws.aws_ec2
regions:
  - us-east-1

filters:
  instance-state-name: running
  "tag:Aluno": "SEU_USUARIO"

keyed_groups:
  - key: tags.grupo
    prefix: ""
    separator: ""

hostnames:
  - tag:Name

compose:
  ansible_host: private_ip_address
```

Ctrl+D — troque `SEU_USUARIO`:

```bash
sed -i "s/SEU_USUARIO/$USER/" aws.aws_ec2.yml
```

> 💡 Repare no `ansible_host: private_ip_address`. Todas as máquinas passam a ser
> endereçadas pelo IP privado — inclusive a `web`. Isso simplifica: uma regra só.

```bash
cat > ansible.cfg
[defaults]
inventory = aws.aws_ec2.yml
host_key_checking = False
interpreter_python = auto_silent

[inventory]
enable_plugins = amazon.aws.aws_ec2

[ssh_connection]
pipelining = True
```

Ctrl+D. Agora o `group_vars`, com o `ProxyJump`:

```bash
mkdir -p group_vars
cat > group_vars/all.yml
---
ansible_user: ubuntu
ansible_ssh_private_key_file: ~/.ssh/labsuser.pem

bastion_ip: "{{ lookup('env', 'IP_WEB') }}"

ansible_ssh_common_args: >-
  -o StrictHostKeyChecking=no
  -o UserKnownHostsFile=/dev/null
  -o ProxyCommand="ssh -W %h:%p -q
     -i {{ ansible_ssh_private_key_file }}
     -o StrictHostKeyChecking=no
     ubuntu@{{ bastion_ip }}"
```

Ctrl+D. O `ProxyCommand` faz cada conexão passar pela `web`.

Teste — a variável `IP_WEB` precisa estar exportada:

```bash
export IP_WEB
ansible-inventory --graph
ansible all -m ping
```

Saída esperada: `pong` das três máquinas.

> ⚠️ A `web` também passa pelo *proxy* — ela conecta em si mesma através de si mesma.
> Funciona, mas é desnecessário. Se quiser otimizar, sobrescreva o
> `ansible_ssh_common_args` em `group_vars/web.yml` com apenas o
> `StrictHostKeyChecking=no`.
>
> ⚠️ Se der `Permission denied`, confirme que o `labsuser.pem` está com `chmod 600` e
> que a chave usada pelo `ProxyCommand` é a mesma.

### ✅ Checkpoint 1

✔ `ansible-inventory --graph` mostra os grupos `web`, `app` e `banco`.
✔ `ansible all -m ping` responde `pong` nas **três**.
✔ `ansible banco -m command -a hostname` funciona, mesmo sem IP público.

### ❓ Pergunta

O `ProxyCommand` abre uma conexão SSH dentro de outra. Que outra ferramenta desta
disciplina resolveria isso de forma parecida? (Lembre da Aula 01 e do
`~/.ssh/config`.)

---

## 🏁 Entrega da Aula — 0,9 ponto (Nota 3)

Você tem **65 minutos**. Individual. Esta é a última entrega da disciplina.

### Parte A — A configuração (0,5 ponto)

Em `~/scripts/projeto/config/`, complete o projeto Ansible com **três *roles***.

**`roles/banco`** — na máquina do grupo `banco`:

- instalar MySQL Server e `python3-pymysql`;
- serviço iniciado e habilitado;
- `bind-address` configurado para aceitar conexões externas, com *handler*;
- criar o banco `aplicacao` e um usuário com senha, acessível de `%`;
- criar uma tabela `visitas` com as colunas `id` (auto-incremento) e `momento`
  (*timestamp*).

**`roles/app`** — na máquina do grupo `app`:

- instalar Python 3 e o cliente MySQL;
- instalar, a partir de um `template`, um serviço HTTP simples que escute na
  **porta 8080** e, a cada requisição, insira uma linha em `visitas` e devolva o
  total de visitas em JSON;
- o endereço do banco deve ser **descoberto via `hostvars`**, nunca fixo;
- o serviço deve ser gerenciado por uma **unidade `systemd`** (Aula 17), iniciada e
  habilitada.

**`roles/web`** — na máquina do grupo `web`:

- instalar o nginx;
- configurar, via `template`, um *proxy reverso* que encaminhe a porta 80 para a
  porta 8080 da máquina `app` — endereço obtido via `hostvars`;
- *handler* que recarrega o nginx quando a configuração muda.

O `site.yml` deve aplicar as três *roles* na ordem correta, com um *play* inicial de
coleta de *facts*.

### Parte B — O orquestrador (0,4 ponto)

Escreva `~/scripts/projeto/implantar.sh`, que faz **tudo com um comando**.

**Uso:** `./implantar.sh [-a] [-d] [-v] [-h]`

| Opção | Ação |
|---|---|
| `-a` | implanta: `terraform apply` + espera SSH + `ansible-playbook` + valida |
| `-d` | destrói: `terraform destroy` |
| `-v` | apenas valida a aplicação já implantada |
| `-h` | ajuda |

Requisitos:

1. Trate as opções com `getopts`; sem nenhuma, mostre a ajuda e retorne `1`.
2. Verifique os pré-requisitos antes de agir: `terraform`, `ansible` e `aws`
   instalados, e credenciais válidas (`aws sts get-caller-identity`). Falhando
   qualquer um, mensagem no `stderr` e saída diferente de zero.
3. No `-a`, em sequência, **verificando cada etapa**:
   - `terraform apply` em `infra/`;
   - exportar o `IP_WEB` a partir do `terraform output`;
   - esperar o SSH da `web` responder, com limite de tentativas;
   - `ansible-playbook site.yml` em `config/`;
   - validar com `curl` na porta 80, com limite de tentativas;
   - imprimir a URL final.
4. Registre cada etapa em `implantacao.log`, com data e hora (Aula 18).
5. Use `trap` para, em caso de interrupção, avisar que pode haver recursos criados e
   sugerir o `-d`.
6. A validação (`-v`) deve chamar a URL **duas vezes** e confirmar que o contador de
   visitas **aumentou** — provando que a cadeia web → app → banco funciona.

Saída esperada:

```
$ ./implantar.sh -a
[10:02:11] Verificando pré-requisitos... OK
[10:02:13] Provisionando infraestrutura...
[10:04:48] Infraestrutura pronta. Bastion: 54.234.12.98
[10:04:49] Aguardando SSH...
[10:05:20] Configurando as três camadas...
[10:08:02] Validando a aplicação...
[10:08:05] Visitas: 1 -> 2 (OK)

Aplicação disponível em: http://54.234.12.98
```

### Critérios de correção

**Parte A — 0,5**

| # | Critério | Valor |
|---|---|---|
| 1 | As três *roles* existem, com estrutura correta | 0,10 |
| 2 | O banco é criado com a tabela `visitas` | 0,10 |
| 3 | O `app` sobe como serviço `systemd` e descobre o banco via `hostvars` | 0,15 |
| 4 | O nginx faz *proxy* para o `app`, com endereço via `hostvars` | 0,10 |
| 5 | Segunda execução do `site.yml` dá `changed=0` | 0,05 |

**Parte B — 0,4**

| # | Critério | Valor |
|---|---|---|
| 6 | `getopts` com as quatro opções e ajuda sem argumentos | 0,05 |
| 7 | Verifica pré-requisitos e credenciais antes de agir | 0,05 |
| 8 | O `-a` executa as etapas verificando cada uma | 0,15 |
| 9 | O `-v` prova que o contador aumentou | 0,10 |
| 10 | `trap` e `implantacao.log` com data e hora | 0,05 |

Correção:

```bash
cd ~/scripts/projeto
./implantar.sh; echo "retorno=$?"
./implantar.sh -a
curl -s "http://$(cd infra && terraform output -raw ip_web)"
./implantar.sh -v
cat implantacao.log

# Nada fixo:
grep -rE "([0-9]{1,3}\.){3}[0-9]{1,3}" config/ --include="*.yml" | grep -v "0.0.0.0"
cd config && ansible-playbook site.yml     # deve dar changed=0

cd ~/scripts/projeto && ./implantar.sh -d
```

> ⚠️ **Rode o `./implantar.sh -d` antes de sair.** É o item 5 do *checklist* e vale
> a nota do critério 8.

---

## ✅ Checklist de Encerramento

| # | Verificação | Comando |
|---|---|---|
| 1 | O `implantar.sh` é executável e tem `getopts` | `grep -c getopts implantar.sh` |
| 2 | Nenhum IP fixo na configuração | `grep -rE "([0-9]{1,3}\.){3}[0-9]{1,3}" config/ --include="*.yml"` |
| 3 | O `site.yml` é idempotente | `cd config && ansible-playbook site.yml` |
| 4 | O `implantacao.log` registrou as etapas | `cat implantacao.log` |
| 5 | **Tudo destruído** | `cd infra && terraform state list` |
| 6 | Nenhuma instância órfã | `aws ec2 describe-instances --filters "Name=tag:Aluno,Values=$USER" "Name=instance-state-name,Values=running" --query 'Reservations[*].Instances[*].InstanceId' --output text` |

---

## 💬 Para Discutir em Sala

- Seu `implantar.sh` tem talvez 100 linhas de *shell*, e ele comanda duas ferramentas
  de milhares. Na Aula 01 você escreveu `who | wc -l`. O que mudou, e o que **não**
  mudou, na forma de pensar?
- O `implantar.sh` é *shell script* orquestrando ferramentas declarativas. Por que o
  *shell* continua sendo a cola, mesmo com tudo que existe hoje?
- Se você tivesse que entregar este projeto para um colega manter, o que faltaria?

---

## 🎓 Fechamento da Disciplina

A próxima sessão (semana 17) é de **preparação de seminários**. As entregas das
Aulas 17 a 30 fecham a Nota 3 — as **duas piores são descartadas**.

Confira o que você tem:

```bash
ls -d ~/scripts/aula1[7-9] ~/scripts/aula2* ~/scripts/projeto
```

E, para fechar: guarde o diretório `~/scripts` inteiro. Ele é o registro de um
semestre — do primeiro `who | wc -l` até uma aplicação de três camadas provisionada
por um comando.

```bash
cd ~ && tar czf scripts_2026_2_$USER.tar.gz scripts/
ls -lh scripts_2026_2_$USER.tar.gz
```

Copie para a sua máquina com `scp` (Aula 01):

```bash
scp disciplina:~/scripts_2026_2_*.tar.gz .
```
