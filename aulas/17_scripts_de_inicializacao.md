# 🧪 Aula 17 — *Scripts* de Inicialização e `systemd`

**Disciplina:** Programação de *Scripts* — UFC Quixadá
**Material de apoio:** `slides/14_scripts_de_inicializacao`
**Sessão:** Semana 10 — terça, 13/10
**Entrega desta aula:** 0,7 ponto (Nota 3)
**Duração estimada:** 100 minutos

---

## 🎯 Objetivos da Aula

Ao final desta aula você deve ser capaz de:

- Explicar o papel do `systemd` como processo `PID 1`.
- Consultar e controlar serviços com `systemctl`.
- Ler *logs* de serviço com `journalctl`.
- Escrever uma **unidade de serviço** para um *script* seu.
- Distinguir um serviço de sistema de um serviço de usuário.

## 🧰 Pré-requisitos

- Bloco 2 concluído. A Aula 10 (processos) é a base direta desta.

## 🗺️ Roteiro

| Etapa | Assunto | Tempo |
|---|---|---|
| 0 | Quem é o PID 1 | 15 min |
| 1 | `systemctl` | 20 min |
| 2 | `journalctl` | 15 min |
| 3 | Criando um serviço | 25 min |
| 🏁 | Entrega | 25 min |

---

## 🧩 Etapa 0 — Quem é o PID 1

### Ação

```bash
ssh disciplina
mkdir -p ~/scripts/aula17
cd ~/scripts/aula17

ps -p 1 -o pid,comm
ps -ef | head -3
```

O processo de PID 1 é o primeiro que o *kernel* inicia, e é o **pai** (direto ou
indireto) de todos os outros. Em distribuições modernas, ele é o `systemd`.

Veja a árvore:

```bash
pstree -p 1 | head -20
```

Antes do `systemd`, esse papel era do `init` do System V, que executava *scripts* de
*shell* em `/etc/init.d`. Alguns ainda existem por compatibilidade:

```bash
ls /etc/init.d/ 2>/dev/null | head -5
```

### ✅ Checkpoint 0

✔ `ps -p 1 -o comm` responde `systemd`.
✔ O `pstree` mostra os demais processos pendurados nele.

### ❓ Pergunta

O `systemd` é o pai de tudo. O que acontece com um processo cujo pai morre antes
dele — quem passa a ser o pai?

---

## 🧩 Etapa 1 — `systemctl`

O `systemd` organiza tudo em **unidades**. As mais comuns:

| Sufixo | O que é |
|---|---|
| `.service` | um serviço (processo gerenciado) |
| `.timer` | um agendamento (alternativa ao `cron`) |
| `.socket` | um ponto de escuta que ativa um serviço sob demanda |
| `.target` | um agrupamento de unidades |

### Ação

```bash
systemctl list-units --type=service | head -15
systemctl list-units --type=service --state=running | wc -l
systemctl status ssh
```

Leia a saída do `status` com atenção. Ela traz:

- **Loaded**: onde está o arquivo da unidade e se ela inicia no *boot* (`enabled`).
- **Active**: o estado atual e há quanto tempo.
- **Main PID**: o processo principal.
- As últimas linhas do *log*.

Os verbos que você mais vai usar:

| Comando | Ação |
|---|---|
| `systemctl status <u>` | consulta o estado |
| `systemctl start <u>` | inicia agora |
| `systemctl stop <u>` | encerra agora |
| `systemctl restart <u>` | reinicia |
| `systemctl reload <u>` | relê a configuração sem derrubar |
| `systemctl enable <u>` | passa a iniciar no *boot* |
| `systemctl disable <u>` | deixa de iniciar no *boot* |

> ⚠️ `enable` e `start` são **independentes**. `enable` sem `start` não inicia agora;
> `start` sem `enable` não sobrevive ao *reboot*. O `--now` faz os dois:
> `systemctl enable --now <unidade>`.

Descubra onde mora o arquivo de uma unidade:

```bash
systemctl cat ssh | head -20
systemctl show ssh -p FragmentPath
```

### ✅ Checkpoint 1

✔ `systemctl status ssh` mostra `active (running)`.
✔ `systemctl cat ssh` exibe o conteúdo do arquivo `.service`.

### ❓ Pergunta

Por que o `systemd` separa "iniciar agora" de "iniciar no *boot*"? Dê um caso real
em que você quer um sem o outro.

---

## 🧩 Etapa 2 — `journalctl`

O `systemd` centraliza os *logs* de todos os serviços.

### Ação

```bash
journalctl -u ssh --no-pager | tail -10
journalctl -u ssh -n 20 --no-pager
journalctl -u ssh --since "1 hour ago" --no-pager
journalctl -p err --no-pager | tail -10
journalctl -b --no-pager | head -10
```

| Opção | Efeito |
|---|---|
| `-u <unidade>` | filtra por serviço |
| `-n N` | as últimas N linhas |
| `-f` | acompanha em tempo real (como `tail -f`) |
| `--since` / `--until` | recorte por tempo |
| `-p err` | só prioridade de erro ou pior |
| `-b` | só o *boot* atual |
| `--no-pager` | não abre o `less` |

> 💡 Sem `--no-pager`, o `journalctl` abre o `less`. Dentro de um *script*, isso
> trava a execução — use `--no-pager` sempre que for automatizar.

Acompanhe em tempo real, em um painel `tmux`:

```bash
journalctl -f -u ssh
```

Ctrl+C para sair.

### ✅ Checkpoint 2

✔ `journalctl -u ssh -n 5 --no-pager` mostra as cinco últimas entradas.
✔ `journalctl -f` acompanha em tempo real.

### ❓ Pergunta

Na Aula 04 você leu `/var/log/auth.log`, um arquivo de texto. O `journalctl` lê um
formato binário. O que se ganha e o que se perde nessa mudança?

---

## 🧩 Etapa 3 — Criando um serviço

Na sua máquina você é administrador, então vamos criar um **serviço de sistema** de
verdade — o mesmo tipo que gerencia o `ssh` e o `nginx`.

### Ação

Primeiro, o *script* a ser gerenciado:

```bash
cat > ~/scripts/aula17/relogio.sh
#!/bin/bash
while true; do
    echo "$(date '+%Y-%m-%d %H:%M:%S') - relógio ativo"
    sleep 5
done
```

Ctrl+D, e:

```bash
chmod +x ~/scripts/aula17/relogio.sh
```

Agora a unidade. Serviços de sistema ficam em `/etc/systemd/system/`, que só o
`root` pode escrever — daí o `sudo tee`:

```bash
sudo tee /etc/systemd/system/relogio.service > /dev/null <<'UNIDADE'
[Unit]
Description=Relógio de exemplo da Aula 17
After=network.target

[Service]
Type=simple
User=ubuntu
ExecStart=/home/ubuntu/scripts/aula17/relogio.sh
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIDADE

sudo systemctl cat relogio
```

> 💡 **Por que `sudo tee` e não `sudo cat >`?** No `sudo cat > arquivo`, o
> redirecionamento é feito pelo **seu** *shell*, que não é `root` — e falha com
> `Permission denied`. O `sudo tee` roda o programa que escreve com privilégio. É um
> erro clássico; guarde este.

As três seções:

| Seção | Papel |
|---|---|
| `[Unit]` | descrição e dependências (`After`, `Requires`) |
| `[Service]` | como executar (`ExecStart`, `Type`, `User`, `Restart`) |
| `[Install]` | quando ativar no *boot* (`WantedBy`) |

> ⚠️ O `ExecStart` exige **caminho absoluto**, e não expande `~`. Como a unidade roda
> como serviço de sistema, `~` seria o diretório do `root`, não o seu — por isso o
> caminho completo `/home/ubuntu/...` e a diretiva `User=ubuntu`. Errar isso produz
> `status=203/EXEC`.

Recarregue e inicie:

```bash
sudo systemctl daemon-reload
sudo systemctl start relogio
sudo systemctl status relogio
```

Veja o *log*:

```bash
sudo journalctl -u relogio -n 10 --no-pager
```

Teste o `Restart=on-failure` — mate o processo e veja o `systemd` ressuscitá-lo:

```bash
sudo systemctl show relogio -p MainPID
sudo kill $(sudo systemctl show relogio -p MainPID --value)
sleep 7
sudo systemctl status relogio
```

Confirme que sobrevive ao *reboot*:

```bash
sudo systemctl enable relogio
sudo systemctl is-enabled relogio
```

Encerre e limpe:

```bash
sudo systemctl disable --now relogio
sudo systemctl status relogio
```

> 💡 Existe também o **serviço de usuário** (`systemctl --user`), que dispensa
> privilégio e guarda as unidades em `~/.config/systemd/user/`. Ele é útil em
> máquinas onde você não é administrador — mas exige que a sessão do usuário
> persista (`loginctl enable-linger`). Como aqui você é dono da máquina, o serviço
> de sistema é o caminho natural.

### ✅ Checkpoint 3

✔ `sudo systemctl status relogio` mostra `active (running)`.
✔ O `sudo journalctl -u relogio` mostra uma linha nova a cada 5 segundos.
✔ Depois do `kill`, o serviço voltou sozinho.

### ❓ Pergunta

Você matou o processo e ele voltou. Compare com o `nohup` da Aula 10: o que o
`systemd` oferece que o `&` e o `nohup` não oferecem?

---

## 🏁 Entrega da Aula — 0,7 ponto (Nota 3)

Individualmente, nos últimos 25 minutos.

Transforme o **coletor da Aula 16** em um serviço gerenciado pelo `systemd`.

1. Crie `~/scripts/aula17/coletor_servico.sh`, uma versão do coletor que roda
   **indefinidamente** (sem parâmetro de quantidade), gravando em
   `~/scripts/aula17/medicoes.csv` a cada 10 segundos, no mesmo formato CSV da
   Aula 16.
2. Crie a unidade `/etc/systemd/system/coletor.service`, com:
   - uma `Description` que identifique o serviço;
   - `ExecStart` apontando para o *script*, com caminho absoluto;
   - `User=ubuntu`, para que o CSV seja gravado com o seu dono;
   - `Restart=always` e `RestartSec=10`;
   - `WantedBy=multi-user.target` na seção `[Install]`.
3. Ative o serviço e comprove que ele está coletando.
4. Escreva, em `~/scripts/aula17/COMANDOS.md`, os comandos usados para: recarregar
   o `systemd`, iniciar, consultar o estado, ver o *log* e parar o serviço.

### Critérios de correção

| # | Critério | Valor |
|---|---|---|
| 1 | O `coletor_servico.sh` roda em laço e grava o CSV no formato certo | 0,20 |
| 2 | A unidade tem as três seções, `ExecStart` absoluto e `User=ubuntu` | 0,20 |
| 3 | O serviço está `active (running)` e o CSV cresce | 0,15 |
| 4 | O `Restart` traz o serviço de volta depois de um `kill` | 0,10 |
| 5 | O `COMANDOS.md` lista os cinco comandos corretos | 0,05 |

Correção:

```bash
cd ~/scripts/aula17
sudo systemctl status coletor | head -5
wc -l medicoes.csv; sleep 12; wc -l medicoes.csv
sudo kill $(sudo systemctl show coletor -p MainPID --value); sleep 12
sudo systemctl status coletor | head -3
cat COMANDOS.md
```

> ⚠️ **Ao final da aula, pare o serviço**: `sudo systemctl disable --now coletor`.
> Um coletor esquecido enche o disco da sua máquina.

---

## ✅ Checklist de Encerramento

| # | Verificação | Comando |
|---|---|---|
| 1 | A unidade existe | `sudo systemctl cat coletor` |
| 2 | O CSV está sendo alimentado | `tail -2 ~/scripts/aula17/medicoes.csv` |
| 3 | O *log* do serviço aparece | `sudo journalctl -u coletor -n 5 --no-pager` |
| 4 | **O serviço foi desativado ao sair** | `sudo systemctl is-enabled coletor` |
| 5 | Nenhum processo sobrou | `ps aux \| grep coletor_servico` |

---

## 💬 Para Discutir em Sala

- O `systemd` substituiu *scripts* de *shell* em `/etc/init.d` por arquivos de
  configuração declarativos. O que se ganhou? O que reclamam os críticos?
- `Restart=always` faz o serviço voltar sempre. Em que situação isso é uma péssima
  ideia?

## 📌 Para a Próxima Aula

Na **Aula 18** vamos ver execução programada (`slides/15_execucao_programada`): o
`cron` e os `systemd timers`. Duas formas de responder à mesma pergunta — "rode isso
toda madrugada".
