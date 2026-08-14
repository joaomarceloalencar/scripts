# 🧪 Aula 28 — Ansible (parte 2): Inventário Dinâmico e *Roles*

**Disciplina:** Programação de *Scripts* — UFC Quixadá
**Material de apoio:** `slides/21_Ansible`
**Sessão:** Semana 15 — quarta, 18/11
**Entrega desta aula:** 0,7 ponto (Nota 3)
**Duração estimada:** 100 minutos

---

## 🎯 Objetivos da Aula

Ao final desta aula você deve ser capaz de:

- Configurar o inventário dinâmico da AWS pelo *plugin* `amazon.aws.aws_ec2`.
- Agrupar máquinas automaticamente pelas **tags** definidas no Terraform.
- Referenciar variáveis de uma máquina a partir de outra (`hostvars`).
- Organizar um projeto em *roles*.
- Entregar uma configuração ponta a ponta, do provisionamento à validação.

## 🧰 Pré-requisitos

- Aula 27 concluída. A infraestrutura da Aula 26 de pé.
- Credenciais AWS válidas.

## 🗺️ Roteiro

| Etapa | Assunto | Tempo |
|---|---|---|
| 0 | Inventário dinâmico | 25 min |
| 1 | `hostvars`: uma máquina falando da outra | 20 min |
| 2 | *Roles* | 25 min |
| 🏁 | Entrega | 30 min |

---

## 🧩 Etapa 0 — Inventário dinâmico

O inventário estático da Aula 27 tem um defeito grave: os IPs mudam a cada
`terraform destroy` e `apply`. O inventário dinâmico **pergunta à AWS**.

### Ação

```bash
ssh disciplina
mkdir -p ~/scripts/aula28
cd ~/scripts/aula28
export PATH="$HOME/local/bin:$PATH"

ansible-galaxy collection install amazon.aws
pip3 install --user boto3 botocore
```

Garanta que a infraestrutura está de pé:

```bash
cd ~/scripts/aula26/entrega && terraform apply -auto-approve && terraform output
cd ~/scripts/aula28
```

O arquivo de inventário dinâmico **precisa** terminar em `.aws_ec2.yml`:

```bash
cat > aws.aws_ec2.yml
---
plugin: amazon.aws.aws_ec2
regions:
  - us-east-1

filters:
  instance-state-name: running
  "tag:grupo":
    - cliente
    - bancodedados

keyed_groups:
  - key: tags.grupo
    prefix: ""
    separator: ""

hostnames:
  - tag:Name
  - dns-name
  - public-ip-address

compose:
  ansible_host: public_ip_address
```

Ctrl+D, e:

```bash
cat > ansible.cfg
[defaults]
inventory = aws.aws_ec2.yml
host_key_checking = False
interpreter_python = auto_silent

[inventory]
enable_plugins = amazon.aws.aws_ec2
```

Ctrl+D. Configure as credenciais SSH para todas as máquinas:

```bash
mkdir -p group_vars
cat > group_vars/all.yml
---
ansible_user: ubuntu
ansible_ssh_private_key_file: ~/.ssh/labsuser.pem
ansible_ssh_common_args: "-o StrictHostKeyChecking=no"
```

Ctrl+D. Agora veja a mágica:

```bash
ansible-inventory --graph
ansible-inventory --list | head -40
```

O `keyed_groups` criou os grupos `cliente` e `bancodedados` a partir da **tag
`grupo`** que você definiu no Terraform na Aula 26. Nenhum IP foi digitado.

```bash
ansible all -m ping
ansible cliente -m command -a hostname
ansible bancodedados -m command -a hostname
```

Teste a promessa: destrua e recrie a infraestrutura, e confirme que o inventário
continua funcionando.

```bash
cd ~/scripts/aula26/entrega
terraform destroy -auto-approve
cd ~/scripts/aula28
ansible-inventory --graph          # vazio agora

cd ~/scripts/aula26/entrega
terraform apply -auto-approve
cd ~/scripts/aula28
sleep 45
ansible-inventory --graph          # de volta, com IPs novos
ansible all -m ping
```

> ⚠️ Os erros mais comuns aqui: (1) o arquivo não termina em `.aws_ec2.yml`;
> (2) o `enable_plugins` não está no `ansible.cfg`; (3) as credenciais do Academy
> expiraram. Diagnostique com `ansible-inventory --list -vvv`.

### ✅ Checkpoint 0

✔ `ansible-inventory --graph` mostra os grupos `cliente` e `bancodedados`.
✔ `ansible all -m ping` responde `pong` nas duas máquinas.
✔ Depois de destruir e recriar, o inventário se atualizou sozinho.

### ❓ Pergunta

O inventário dinâmico consulta a AWS a cada execução. Que problema isso cria em um
ambiente com 500 instâncias, e o que o Ansible oferece para mitigá-lo?

---

## 🧩 Etapa 1 — `hostvars`: uma máquina falando da outra

O cliente precisa do IP **privado** do banco para se conectar. Esse dado está nos
*facts* da outra máquina.

### Ação

```bash
cat > conectividade.yml
---
- name: Coletar os facts de todas as máquinas
  hosts: all
  gather_facts: true
  tasks: []

- name: Configurar o cliente para falar com o banco
  hosts: cliente
  become: true

  vars:
    banco_host: "{{ hostvars[groups['bancodedados'][0]]['ansible_default_ipv4']['address'] }}"

  tasks:
    - name: Mostrar o IP privado do banco descoberto
      ansible.builtin.debug:
        msg: "O banco está em {{ banco_host }}"

    - name: Registrar o endereço do banco em /etc/hosts
      ansible.builtin.lineinfile:
        path: /etc/hosts
        regexp: '\sbanco$'
        line: "{{ banco_host }} banco"
        state: present

    - name: Testar a resolução do nome
      ansible.builtin.command: getent hosts banco
      register: resultado
      changed_when: false

    - name: Mostrar o resultado
      ansible.builtin.debug:
        var: resultado.stdout
```

Ctrl+D, e:

```bash
ansible-playbook conectividade.yml
```

Três coisas importantes acontecem aqui:

- O **primeiro *play*** existe só para coletar os *facts* de todas as máquinas. Sem
  ele, o `hostvars` do banco estaria vazio quando o segundo *play* rodasse.
- `groups['bancodedados'][0]` pega o primeiro membro do grupo, e o `hostvars[...]`
  acessa as variáveis dele.
- `changed_when: false` diz que aquele `command` é uma consulta, não uma alteração —
  sem isso, ele reportaria `changed` toda vez, quebrando a idempotência.

### ✅ Checkpoint 1

✔ O `debug` mostra um IP privado (começando com `172.` ou `10.`).
✔ `ansible-playbook conectividade.yml` rodado duas vezes dá `changed=0` na segunda.

### ❓ Pergunta

Por que o primeiro *play* é necessário? Teste removê-lo e veja o erro.

---

## 🧩 Etapa 2 — *Roles*

Um *playbook* de 200 linhas é ilegível. As *roles* separam a configuração em
componentes reutilizáveis.

### Ação

```bash
ansible-galaxy init roles/mysql_cliente
find roles/mysql_cliente -type d
```

A estrutura padrão:

| Diretório | Conteúdo |
|---|---|
| `tasks/main.yml` | as tarefas (obrigatório na prática) |
| `handlers/main.yml` | os *handlers* |
| `defaults/main.yml` | variáveis com prioridade **baixa** |
| `vars/main.yml` | variáveis com prioridade **alta** |
| `templates/` | arquivos Jinja2 (`.j2`) |
| `files/` | arquivos copiados como estão |
| `meta/main.yml` | dependências de outras *roles* |

Preencha a *role*:

```bash
cat > roles/mysql_cliente/defaults/main.yml
---
mysql_pacotes:
  - mysql-client
  - python3-pymysql
banco_nome: scripts
```

Ctrl+D.

```bash
cat > roles/mysql_cliente/tasks/main.yml
---
- name: Instalar o cliente MySQL
  ansible.builtin.apt:
    name: "{{ mysql_pacotes }}"
    state: present
    update_cache: true
    cache_valid_time: 3600

- name: Instalar o script de criação do banco
  ansible.builtin.template:
    src: criar_banco.sh.j2
    dest: /usr/local/bin/criar_banco.sh
    mode: "0755"
```

Ctrl+D.

```bash
cat > roles/mysql_cliente/templates/criar_banco.sh.j2
#!/bin/bash
# Gerado pelo Ansible em {{ ansible_date_time.iso8601 }}
set -euo pipefail

BANCO_HOST="{{ banco_host }}"
BANCO_USUARIO="{{ banco_usuario }}"
BANCO_SENHA="{{ banco_senha }}"
BANCO_NOME="{{ banco_nome }}"

mysql -h "$BANCO_HOST" -u "$BANCO_USUARIO" -p"$BANCO_SENHA" \
    -e "CREATE DATABASE IF NOT EXISTS $BANCO_NOME;"

echo "Bancos disponíveis em $BANCO_HOST:"
mysql -h "$BANCO_HOST" -u "$BANCO_USUARIO" -p"$BANCO_SENHA" -e "SHOW DATABASES;"
```

Ctrl+D.

> ⚠️ Repare no `set -euo pipefail` no *template*: `{{ }}` é do Ansible, mas
> `$BANCO_HOST` é do *shell*. O Ansible só substitui o que está entre chaves duplas —
> o resto passa intacto. Diferente do `templatefile` do Terraform (Aula 26), aqui não
> é preciso escapar o `$`.

Use a *role* em um *playbook*:

```bash
cat > site.yml
---
- name: Coletar facts
  hosts: all
  tasks: []

- name: Configurar o cliente
  hosts: cliente
  become: true

  vars:
    banco_host: "{{ hostvars[groups['bancodedados'][0]]['ansible_default_ipv4']['address'] }}"
    banco_usuario: aluno
    banco_senha: SenhaForte123!
    banco_nome: scripts

  roles:
    - mysql_cliente
```

Ctrl+D, e:

```bash
ansible-playbook site.yml
ansible cliente -m command -a "cat /usr/local/bin/criar_banco.sh"
```

### ✅ Checkpoint 2

✔ `ansible-playbook site.yml` termina sem erro.
✔ O `criar_banco.sh` está na máquina cliente, com os valores substituídos.
✔ Segunda execução: `changed=0`.

### ❓ Pergunta

A *role* tem `defaults/` e `vars/`, ambos com variáveis. Se a mesma variável estiver
nos dois, qual vence? E por que essa distinção existe?

---

## 🏁 Entrega da Aula — 0,7 ponto (Nota 3)

Individualmente, nos últimos 30 minutos.

Em `~/scripts/aula28/entrega/`, monte o projeto Ansible completo que configura a
infraestrutura da Aula 26 e **valida a conectividade** entre as duas máquinas.

Estrutura esperada:

```
entrega/
├── ansible.cfg
├── aws.aws_ec2.yml
├── group_vars/
│   └── all.yml
├── roles/
│   ├── mysql_servidor/
│   └── mysql_cliente/
└── site.yml
```

O `site.yml` deve:

1. Usar **inventário dinâmico da AWS**, agrupando pelas tags `grupo` do Terraform.
   Nenhum IP pode aparecer escrito nos arquivos.
2. Na máquina do grupo `bancodedados`, via a *role* `mysql_servidor`:
   - instalar e iniciar o MySQL;
   - criar um usuário com senha e permissão de criar bancos, acessível de `%`;
   - configurar o `bind-address` para aceitar conexões externas, com *handler* de
     reinício.
3. Na máquina do grupo `cliente`, via a *role* `mysql_cliente`:
   - instalar o cliente MySQL;
   - **descobrir o IP privado do banco** via `hostvars`, sem valor fixo;
   - instalar um *script* que se conecta ao banco e cria um banco de dados chamado
     `scripts`;
   - executar esse *script* e registrar a saída.
4. Ao final, exibir com `debug` a lista de bancos existentes no servidor, provando
   que a conexão funcionou.

### Critérios de correção

| # | Critério | Valor |
|---|---|---|
| 1 | Inventário dinâmico funciona, sem IP fixo em lugar nenhum | 0,15 |
| 2 | As duas *roles* existem, com a estrutura correta | 0,10 |
| 3 | O servidor MySQL é configurado e aceita conexão externa | 0,15 |
| 4 | O cliente descobre o IP do banco via `hostvars` | 0,10 |
| 5 | O banco `scripts` é criado **a partir do cliente** | 0,15 |
| 6 | Segunda execução resulta em `changed=0` | 0,05 |

Correção:

```bash
cd ~/scripts/aula28/entrega
ansible-inventory --graph
grep -rE "([0-9]{1,3}\.){3}[0-9]{1,3}" . --include="*.yml" --include="*.cfg" | grep -v "0.0.0.0"
ansible-playbook site.yml --syntax-check
ansible-playbook site.yml
ansible-playbook site.yml            # segunda: changed=0

# Prova final: entrar no servidor e conferir que o banco existe
ansible bancodedados -m shell -a "mysql -e 'SHOW DATABASES;'" --become
```

O `grep` de IPs não deve encontrar nada (critério 1). O `SHOW DATABASES` deve
listar `scripts` (critério 5).

> ⚠️ **Ao final, destrua a infraestrutura**:
> `cd ~/scripts/aula26/entrega && terraform destroy -auto-approve`

---

## ✅ Checklist de Encerramento

| # | Verificação | Comando |
|---|---|---|
| 1 | O inventário lista as duas máquinas | `ansible-inventory --graph` |
| 2 | Nenhum IP fixo nos arquivos | `grep -rE "([0-9]{1,3}\.){3}[0-9]{1,3}" . --include="*.yml"` |
| 3 | O `site.yml` passa no `--syntax-check` | `ansible-playbook site.yml --syntax-check` |
| 4 | O banco `scripts` existe | `ansible bancodedados -m shell -a "mysql -e 'SHOW DATABASES;'" --become` |
| 5 | **Infraestrutura destruída** | `cd ~/scripts/aula26/entrega && terraform state list` |

---

## 💬 Para Discutir em Sala

- O Terraform pôs a tag `grupo` nas instâncias e o Ansible a usou para montar os
  grupos. As duas ferramentas nunca conversaram diretamente. Por que esse
  acoplamento fraco é uma boa ideia?
- A senha do MySQL ainda está em texto claro nos seus arquivos. Como o *Ansible
  Vault* resolveria isso, e por que ele não foi usado nesta aula?

## 📌 Para a Próxima Aula

As **Aulas 29 e 30** são o **projeto integrador** do Bloco 3: provisionar e
configurar, do zero e com um comando só, uma aplicação web com banco de dados.
Valem **0,7 e 0,9 ponto** e são a última entrega da disciplina.

Revise as Aulas 23 a 28 — e guarde todos os arquivos.
