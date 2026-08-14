# 🧪 Aula 27 — Ansible (parte 1): Inventário e *Playbooks*

**Disciplina:** Programação de *Scripts* — UFC Quixadá
**Material de apoio:** `slides/21_Ansible`
**Sessão:** Semana 15 — terça, 17/11
**Entrega desta aula:** 0,7 ponto (Nota 3)
**Duração estimada:** 100 minutos

---

## 🎯 Objetivos da Aula

Ao final desta aula você deve ser capaz de:

- Explicar por que o Ansible não exige agente nas máquinas gerenciadas.
- Escrever um inventário estático e testar a conectividade.
- Executar comandos *ad-hoc* com módulos.
- Escrever um *playbook* com tarefas, variáveis e *handlers*.
- Reconhecer idempotência na saída de uma execução.

## 🧰 Pré-requisitos

- Aula 26: a infraestrutura de duas máquinas provisionada com Terraform.
- Credenciais AWS válidas.

## 🗺️ Roteiro

| Etapa | Assunto | Tempo |
|---|---|---|
| 0 | Instalação e infraestrutura | 15 min |
| 1 | Inventário estático | 20 min |
| 2 | Comandos *ad-hoc* | 15 min |
| 3 | O primeiro *playbook* | 25 min |
| 🏁 | Entrega | 25 min |

---

## 🧩 Etapa 0 — Instalação e infraestrutura

O Ansible roda **na sua máquina** e se conecta às gerenciadas por SSH. Não há nada a
instalar do outro lado — é o que se chama *agentless*.

### Ação

```bash
ssh disciplina
mkdir -p ~/scripts/aula27
cd ~/scripts/aula27
export PATH="$HOME/local/bin:$PATH"

command -v ansible || pip3 install --user ansible
ansible --version
```

Suba a infraestrutura da Aula 26:

```bash
cd ~/scripts/aula26/entrega
terraform apply -auto-approve
terraform output

IP_CLIENTE=$(terraform output -raw ip_cliente)
IP_BANCO=$(terraform output -raw ip_banco)
IP_BANCO_PRIVADO=$(terraform output -raw ip_banco_privado)
cd ~/scripts/aula27
echo "$IP_CLIENTE / $IP_BANCO / $IP_BANCO_PRIVADO"
```

> ⚠️ Se os nomes dos seus `output` forem diferentes, ajuste. Rode `terraform output`
> para ver os que você definiu.
>
> ⚠️ Espere cerca de 1 minuto após o `apply` — o SSH das instâncias leva um tempo
> para aceitar conexões.

### ✅ Checkpoint 0

✔ `ansible --version` responde.
✔ As três variáveis de IP estão preenchidas.

### ❓ Pergunta

O Ansible não instala nada nas máquinas gerenciadas. O que ele exige que elas
tenham, então?

---

## 🧩 Etapa 1 — Inventário estático

O inventário diz **quais máquinas existem** e como se agrupam.

### Ação

```bash
cat > inventario.ini
[cliente]
maquina-cliente ansible_host=IP_CLIENTE

[bancodedados]
maquina-banco ansible_host=IP_BANCO

[todas:children]
cliente
bancodedados

[todas:vars]
ansible_user=ubuntu
ansible_ssh_private_key_file=~/.ssh/labsuser.pem
ansible_ssh_common_args='-o StrictHostKeyChecking=no'
```

Ctrl+D. Substitua os endereços de verdade:

```bash
sed -i "s/IP_CLIENTE/$IP_CLIENTE/; s/IP_BANCO/$IP_BANCO/" inventario.ini
cat inventario.ini
```

Confira como o Ansible enxerga o inventário:

```bash
ansible-inventory -i inventario.ini --list
ansible-inventory -i inventario.ini --graph
```

Teste a conectividade:

```bash
ansible -i inventario.ini todas -m ping
```

Saída esperada:

```
maquina-cliente | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
```

> 💡 O módulo `ping` do Ansible **não** é o `ping` de rede. Ele conecta por SSH,
> executa Python do outro lado e responde `pong`. Se ele funciona, tudo funciona.

Um `ansible.cfg` no diretório evita repetir o `-i`:

```bash
cat > ansible.cfg
[defaults]
inventory = inventario.ini
host_key_checking = False
interpreter_python = auto_silent
```

Ctrl+D, e agora:

```bash
ansible todas -m ping
ansible cliente -m ping
ansible bancodedados -m ping
```

### ✅ Checkpoint 1

✔ `ansible todas -m ping` responde `SUCCESS` nas duas máquinas.
✔ `ansible-inventory --graph` mostra os grupos `cliente` e `bancodedados`.
✔ Depois do `ansible.cfg`, o `-i` não é mais necessário.

### ❓ Pergunta

O grupo `todas:children` agrupa outros grupos. Por que isso é melhor do que listar
as duas máquinas de novo em um terceiro grupo?

---

## 🧩 Etapa 2 — Comandos *ad-hoc*

Antes dos *playbooks*, o Ansible serve para rodar um comando em várias máquinas.

### Ação

```bash
ansible todas -m command -a "hostname"
ansible todas -m command -a "uptime"
ansible todas -m setup -a "filter=ansible_distribution*"
```

O módulo `setup` coleta *facts* — informações sobre a máquina, que ficam disponíveis
como variáveis nos *playbooks*:

```bash
ansible cliente -m setup | head -30
ansible cliente -m setup -a "filter=ansible_default_ipv4"
```

Operações que exigem privilégio usam `--become`:

```bash
ansible todas -m command -a "whoami"
ansible todas -m command -a "whoami" --become
ansible todas -m apt -a "update_cache=yes" --become
```

Instalando um pacote:

```bash
ansible cliente -m apt -a "name=tree state=present" --become
ansible cliente -m command -a "tree --version"
```

Rode o mesmo comando **de novo**:

```bash
ansible cliente -m apt -a "name=tree state=present" --become
```

Repare no `changed`: na primeira vez foi `changed=true`, na segunda `changed=false`.
O módulo verificou que o pacote já estava lá e não fez nada.

> ⚠️ O módulo `command` **não** é idempotente — ele executa sempre. Sempre que
> existir um módulo específico (`apt`, `copy`, `service`, `file`), prefira-o ao
> `command` ou `shell`.

### ✅ Checkpoint 2

✔ O `hostname` responde diferente em cada máquina.
✔ `whoami` responde `ubuntu` sem `--become` e `root` com ele.
✔ A segunda instalação do `tree` responde `changed=false`.

### ❓ Pergunta

Qual a diferença entre os módulos `command` e `shell`? (Teste:
`ansible cliente -m command -a "echo \$HOME"` e o mesmo com `-m shell`.)

---

## 🧩 Etapa 3 — O primeiro *playbook*

Um *playbook* é um arquivo YAML que descreve o **estado desejado**.

### Ação

```bash
cat > nginx.yml
---
- name: Configurar servidor web no cliente
  hosts: cliente
  become: true

  vars:
    porta_http: 80
    mensagem: "Configurado pelo Ansible"

  tasks:
    - name: Atualizar o índice de pacotes
      ansible.builtin.apt:
        update_cache: true
        cache_valid_time: 3600

    - name: Instalar o nginx
      ansible.builtin.apt:
        name: nginx
        state: present

    - name: Publicar a página inicial
      ansible.builtin.copy:
        dest: /var/www/html/index.html
        content: |
          <!doctype html>
          <html><head><meta charset="utf-8"><title>Aula 27</title></head>
          <body>
            <h1>{{ mensagem }}</h1>
            <p>Máquina: {{ ansible_hostname }}</p>
            <p>Sistema: {{ ansible_distribution }} {{ ansible_distribution_version }}</p>
            <p>IP privado: {{ ansible_default_ipv4.address }}</p>
          </body></html>
        owner: www-data
        mode: "0644"
      notify: Reiniciar nginx

    - name: Garantir que o nginx está ativo
      ansible.builtin.service:
        name: nginx
        state: started
        enabled: true

  handlers:
    - name: Reiniciar nginx
      ansible.builtin.service:
        name: nginx
        state: restarted
```

Ctrl+D. Verifique a sintaxe antes de executar:

```bash
ansible-playbook nginx.yml --syntax-check
ansible-playbook nginx.yml --check
```

O `--check` é uma simulação: mostra o que **seria** mudado, sem mudar nada. É o
equivalente ao `terraform plan`.

Execute:

```bash
ansible-playbook nginx.yml
```

Leia o `PLAY RECAP` no final:

```
maquina-cliente : ok=5  changed=3  unreachable=0  failed=0
```

Agora rode **de novo**:

```bash
ansible-playbook nginx.yml
```

```
maquina-cliente : ok=5  changed=0  unreachable=0  failed=0
```

Zero mudanças. Idempotência de novo — e repare que o *handler* **não** disparou,
porque a tarefa que o notifica não mudou nada.

Confirme:

```bash
curl -s "http://$IP_CLIENTE" | head -8
```

Os elementos do *playbook*:

| Elemento | Papel |
|---|---|
| `hosts` | em quais máquinas ou grupos rodar |
| `become` | executar com privilégio |
| `vars` | variáveis do *play* |
| `tasks` | a lista de estados desejados, em ordem |
| `handlers` | tarefas que só rodam se **notificadas** por uma mudança |
| `{{ }}` | interpolação (Jinja2) |

> 💡 Os *handlers* rodam **uma vez só**, ao final do *play*, mesmo que notificados
> dez vezes. É isso que evita reiniciar o serviço a cada tarefa.

### ✅ Checkpoint 3

✔ A primeira execução mostra `changed=3` (ou similar).
✔ A segunda mostra `changed=0`.
✔ `curl http://$IP_CLIENTE` mostra a página com o *hostname* e o IP privado.

### ❓ Pergunta

O *handler* não disparou na segunda execução. Por que isso é desejável? O que
aconteceria se ele rodasse sempre?

---

## 🏁 Entrega da Aula — 0,7 ponto (Nota 3)

Individualmente, nos últimos 25 minutos.

Escreva o *playbook* `~/scripts/aula27/banco.yml`, que configura o **servidor de
banco de dados**.

O *playbook* deve, na máquina do grupo `bancodedados`:

1. Atualizar o índice de pacotes.
2. Instalar o **MySQL Server** e a biblioteca Python necessária para os módulos
   `mysql_*` (investigue `python3-pymysql`).
3. Garantir que o serviço está **iniciado e habilitado no *boot***.
4. Criar um banco de dados chamado `scripts_teste`.
5. Criar um usuário MySQL com senha, **com permissão de criar bancos**, e que possa
   se conectar de **qualquer host** (`%`), não apenas de `localhost`.
6. Configurar o MySQL para **escutar conexões externas** — o padrão é aceitar apenas
   `127.0.0.1`. A alteração deve disparar um *handler* que reinicia o serviço.
7. Usar `vars` para o nome do banco, o nome do usuário e a senha — nada fixo no meio
   das tarefas.

Requisitos:

- O *playbook* deve passar no `--syntax-check`.
- Rodá-lo **duas vezes** deve resultar em `changed=0` na segunda.
- Use módulos específicos (`apt`, `service`, `lineinfile`, `mysql_db`, `mysql_user`),
  não `command` ou `shell`.

### Critérios de correção

| # | Critério | Valor |
|---|---|---|
| 1 | Instala MySQL e a dependência Python | 0,10 |
| 2 | O serviço está `started` e `enabled` | 0,10 |
| 3 | O banco e o usuário são criados com as permissões pedidas | 0,20 |
| 4 | O `bind-address` é alterado e um *handler* reinicia o serviço | 0,15 |
| 5 | Usa `vars`, sem valores fixos nas tarefas | 0,05 |
| 6 | Segunda execução resulta em `changed=0` | 0,10 |

Correção:

```bash
cd ~/scripts/aula27
ansible-playbook banco.yml --syntax-check
ansible-playbook banco.yml            # primeira: changed > 0
ansible-playbook banco.yml            # segunda: changed = 0
ansible bancodedados -m command -a "ss -tlnp sport = :3306" --become
grep -c "shell\|ansible.builtin.command" banco.yml
```

O último comando deve responder `0`.

> 💡 O `bind-address` fica em `/etc/mysql/mysql.conf.d/mysqld.cnf`. O módulo
> `lineinfile` com `regexp` resolve — e é idempotente, diferente de um `sed`.

---

## ✅ Checklist de Encerramento

| # | Verificação | Comando |
|---|---|---|
| 1 | O *playbook* passa no `--syntax-check` | `ansible-playbook banco.yml --syntax-check` |
| 2 | Segunda execução: `changed=0` | `ansible-playbook banco.yml` |
| 3 | O MySQL escuta em `0.0.0.0` | `ansible bancodedados -m shell -a "ss -tln \| grep 3306" --become` |
| 4 | Não usa `command`/`shell` | `grep -c "command\|shell" banco.yml` |
| 5 | Instâncias autorizadas ou destruídas | `cd ~/scripts/aula26/entrega && terraform state list` |

---

## 💬 Para Discutir em Sala

- O Terraform e o Ansible são os dois declarativos e idempotentes. Qual é a divisão
  de trabalho entre eles? Por que não usar um só?
- Você colocou a senha do MySQL em `vars`, em texto claro no arquivo. Isso vai para
  o Git. Qual é o problema, e o que o Ansible oferece para resolver? (Procure por
  *Ansible Vault*.)

## 📌 Para a Próxima Aula

Na **Aula 28** vamos ao **inventário dinâmico** da AWS — o Ansible descobrindo
sozinho as máquinas pelas tags do Terraform, sem você digitar IP nenhum. E vamos
organizar tudo em *roles*.
