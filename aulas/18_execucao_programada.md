# 🧪 Aula 18 — Execução Programada

**Disciplina:** Programação de *Scripts* — UFC Quixadá
**Material de apoio:** `slides/15_execucao_programada`
**Sessão:** Semana 10 — quarta, 14/10
**Entrega desta aula:** 0,7 ponto (Nota 3)
**Duração estimada:** 100 minutos

---

## 🎯 Objetivos da Aula

Ao final desta aula você deve ser capaz de:

- Ler e escrever uma linha de `crontab`.
- Editar a sua `crontab` e entender por que ela roda em ambiente reduzido.
- Usar os diretórios `/etc/cron.*` para tarefas de sistema.
- Agendar tarefas pontuais com `at`.
- Criar um `systemd timer` como alternativa ao `cron`.

## 🧰 Pré-requisitos

- Aula 17 concluída. Você vai reaproveitar o coletor.

## 🗺️ Roteiro

| Etapa | Assunto | Tempo |
|---|---|---|
| 0 | A sintaxe do `cron` | 20 min |
| 1 | Sua `crontab` | 20 min |
| 2 | A armadilha do ambiente | 15 min |
| 3 | `at` e `systemd timers` | 20 min |
| 🏁 | Entrega | 25 min |

---

## 🧩 Etapa 0 — A sintaxe do `cron`

Cada linha da `crontab` tem cinco campos de tempo e um comando:

```
┌───────────── minuto (0-59)
│ ┌─────────── hora (0-23)
│ │ ┌───────── dia do mês (1-31)
│ │ │ ┌─────── mês (1-12)
│ │ │ │ ┌───── dia da semana (0-7, 0 e 7 = domingo)
│ │ │ │ │
* * * * *  comando
```

Os operadores em cada campo:

| Operador | Significado | Exemplo |
|---|---|---|
| `*` | todos os valores | `* * * * *` = a cada minuto |
| `,` | lista | `0,30 * * * *` = nos minutos 0 e 30 |
| `-` | intervalo | `0 9-17 * * *` = de hora em hora, das 9 às 17 |
| `/` | passo | `*/15 * * * *` = a cada 15 minutos |

### Ação

```bash
ssh disciplina
mkdir -p ~/scripts/aula18
cd ~/scripts/aula18
```

Traduza cada uma destas para português, **antes** de conferir a resposta:

```
30 3 * * *          →
0 */6 * * *         →
0 0 1 * *           →
*/5 9-18 * * 1-5    →
0 22 * * 0          →
```

<details>
<summary>Respostas</summary>

- `30 3 * * *` — todo dia às 03:30.
- `0 */6 * * *` — a cada 6 horas (00:00, 06:00, 12:00, 18:00).
- `0 0 1 * *` — à meia-noite do dia 1º de cada mês.
- `*/5 9-18 * * 1-5` — a cada 5 minutos, das 9h às 18h, de segunda a sexta.
- `0 22 * * 0` — todo domingo às 22:00.

</details>

> ⚠️ **A pegadinha do dia do mês com dia da semana.** Se os dois campos forem
> diferentes de `*`, o `cron` executa quando **qualquer um** casar, não os dois.
> `0 0 13 * 5` roda todo dia 13 **e** toda sexta-feira.

Existem ainda os atalhos:

```
@reboot     @yearly     @monthly     @weekly     @daily     @hourly
```

### ✅ Checkpoint 0

✔ Você traduziu as cinco linhas antes de abrir as respostas.
✔ Entendeu a regra do dia do mês com dia da semana.

### ❓ Pergunta

Como você escreveria "a cada 90 minutos"? Tente — e descubra o limite da sintaxe.

---

## 🧩 Etapa 1 — Sua `crontab`

### Ação

```bash
crontab -l           # lista (pode dizer "no crontab for ...")
crontab -e           # edita
```

> 💡 Na primeira vez o sistema pergunta qual editor usar. Escolha o `nano` se estiver
> em dúvida.

Adicione uma linha de teste que roda a cada minuto:

```
* * * * * date >> /home/SEU_USUARIO/scripts/aula18/cron_teste.log 2>&1
```

Troque `SEU_USUARIO` pelo seu. Salve e saia. Confirme:

```bash
crontab -l
```

Espere dois minutos e verifique:

```bash
sleep 120
cat ~/scripts/aula18/cron_teste.log
```

> ⚠️ **Use caminhos absolutos.** O `cron` não roda no seu diretório pessoal e não
> conhece o seu `PATH` completo. `date >> cron_teste.log` gravaria em um lugar
> imprevisível — ou falharia em silêncio.

Veja o registro de execução:

```bash
grep CRON /var/log/syslog 2>/dev/null | tail -5
journalctl -u cron -n 10 --no-pager 2>/dev/null
```

Remova a linha de teste:

```bash
crontab -e      # apague a linha, salve e saia
crontab -l
```

### ✅ Checkpoint 1

✔ O `cron_teste.log` recebeu uma linha por minuto.
✔ Você removeu a linha de teste — `crontab -l` não a mostra mais.

### ❓ Pergunta

Por que a linha termina com `2>&1`? O que acontece com a saída de erro de uma tarefa
`cron` que não redireciona nada?

---

## 🧩 Etapa 2 — A armadilha do ambiente

O motivo número um de "funciona no terminal, mas não no `cron`".

### Ação

Compare o ambiente das duas execuções. No terminal:

```bash
env | sort > ~/scripts/aula18/env_terminal.txt
wc -l ~/scripts/aula18/env_terminal.txt
echo $PATH
```

Agora pelo `cron`. Adicione temporariamente:

```
* * * * * /usr/bin/env | sort > /home/SEU_USUARIO/scripts/aula18/env_cron.txt
```

Espere e compare:

```bash
sleep 70
wc -l ~/scripts/aula18/env_cron.txt
diff ~/scripts/aula18/env_terminal.txt ~/scripts/aula18/env_cron.txt | head -20
grep ^PATH ~/scripts/aula18/env_cron.txt
```

O `PATH` do `cron` costuma ser apenas `/usr/bin:/bin`. Qualquer comando fora daí
não é encontrado.

As três formas de resolver:

```bash
# 1. Caminho absoluto no comando
* * * * * /usr/bin/python3 /home/aluno/script.py

# 2. Definir PATH no topo da crontab
PATH=/usr/local/bin:/usr/bin:/bin
* * * * * meu_comando

# 3. Fazer o script carregar o próprio ambiente
* * * * * /bin/bash -lc '/home/aluno/scripts/tarefa.sh'
```

Remova a linha de teste antes de seguir.

### ✅ Checkpoint 2

✔ O `env_cron.txt` tem **menos** variáveis que o `env_terminal.txt`.
✔ O `PATH` do `cron` é mais curto que o seu.
✔ Você removeu a linha de teste.

### ❓ Pergunta

O `cron` roda com ambiente mínimo de propósito, não por descuido. Qual o argumento
a favor dessa decisão?

---

## 🧩 Etapa 3 — `at` e `systemd timers`

### Ação — `at`, para uma vez só

```bash
which at || echo "at não instalado"

echo "date >> ~/scripts/aula18/at_teste.log" | at now + 2 minutes
atq                      # lista as tarefas agendadas
```

Aguarde e confira:

```bash
sleep 130
cat ~/scripts/aula18/at_teste.log
atq
```

Para cancelar antes da hora: `atrm <número da fila>`.

### Ação — `systemd timer`

Um *timer* precisa de **duas** unidades: o serviço e o gatilho.

```bash
sudo tee /etc/systemd/system/marcador.service > /dev/null <<'UNIDADE'
[Unit]
Description=Grava um marcador de horário

[Service]
Type=oneshot
User=ubuntu
ExecStart=/bin/bash -c 'date >> /home/ubuntu/scripts/aula18/timer_teste.log'
UNIDADE
```

Repare no `Type=oneshot`: o serviço executa, termina, e isso é o esperado.

```bash
sudo tee /etc/systemd/system/marcador.timer > /dev/null <<'UNIDADE'
[Unit]
Description=Dispara o marcador a cada minuto

[Timer]
OnCalendar=*:0/1
Persistent=true

[Install]
WantedBy=timers.target
UNIDADE
```

Ative:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now marcador.timer
sudo systemctl list-timers --no-pager
```

Aguarde e confira:

```bash
sleep 130
cat ~/scripts/aula18/timer_teste.log
sudo journalctl -u marcador.service -n 5 --no-pager
```

Desative:

```bash
sudo systemctl disable --now marcador.timer
```

Comparando as três ferramentas:

| | `cron` | `at` | `systemd timer` |
|---|---|---|---|
| Repetitivo | sim | não | sim |
| *Log* integrado | não | não | sim (`journalctl`) |
| Recupera execução perdida | não | não | sim (`Persistent=true`) |
| Depende de outra unidade | não | não | sim |
| Sintaxe | compacta | natural | verbosa |

### ✅ Checkpoint 3

✔ O `at` gravou uma linha, uma única vez.
✔ O `sudo systemctl list-timers` mostra o `marcador.timer` com o próximo disparo.
✔ Você desativou o *timer*.

### ❓ Pergunta

O `Persistent=true` roda a tarefa perdida quando a máquina volta de um desligamento.
Em que tipo de tarefa isso é essencial, e em que tipo é indesejável?

---

## 🏁 Entrega da Aula — 0,7 ponto (Nota 3)

Individualmente, nos últimos 25 minutos.

Monte uma rotina de **rotação de *log*** para o coletor da Aula 17.

1. Crie `~/scripts/aula18/rotaciona.sh`, que:
   - recebe o caminho de um arquivo de *log* como parâmetro e o valida;
   - se o arquivo tiver **mais de 50 linhas**, renomeia-o para
     `<nome>.<AAAAMMDD-HHMMSS>` e cria um novo arquivo vazio no lugar, com o
     cabeçalho CSV;
   - apaga arquivos rotacionados com mais de **7 dias** (investigue `find -mtime`);
   - registra o que fez em `~/scripts/aula18/rotacao.log`, com data e hora;
   - **funciona quando chamado pelo `cron`** — ou seja, sem depender de `PATH`,
     de diretório atual ou de variáveis da sua sessão.
2. Agende-o na sua `crontab` para rodar **a cada 5 minutos**, redirecionando saída e
   erro para `~/scripts/aula18/cron_rotaciona.log`.
3. Deixe a linha da `crontab` também salva em `~/scripts/aula18/crontab.txt`, para
   a correção.

### Critérios de correção

| # | Critério | Valor |
|---|---|---|
| 1 | Valida o parâmetro e trata arquivo inexistente | 0,10 |
| 2 | Rotaciona pelo limite de 50 linhas, com nome datado | 0,20 |
| 3 | Recria o arquivo com o cabeçalho CSV | 0,10 |
| 4 | Remove rotacionados com mais de 7 dias | 0,10 |
| 5 | Usa **caminhos absolutos**, funcionando sob o `cron` | 0,15 |
| 6 | A linha da `crontab` está correta e salva em `crontab.txt` | 0,05 |

Correção:

```bash
cd ~/scripts/aula18
seq 1 60 > teste.log
./rotaciona.sh ~/scripts/aula18/teste.log
ls -l teste.log*                       # deve haver o novo e o rotacionado
wc -l teste.log
./rotaciona.sh /naoexiste; echo "retorno=$?"
cat rotacao.log
crontab -l | grep rotaciona
grep -c '\$HOME\|^\s*cd ' rotaciona.sh   # dependências de ambiente
```

> ⚠️ **Ao final da aula, remova a linha da `crontab`.** Uma tarefa esquecida rodando
> a cada 5 minutos em um servidor compartilhado é um problema real.

---

## ✅ Checklist de Encerramento

| # | Verificação | Comando |
|---|---|---|
| 1 | O *script* é executável | `ls -l ~/scripts/aula18/rotaciona.sh` |
| 2 | Funciona chamado com caminho absoluto de outro diretório | `cd / && ~/scripts/aula18/rotaciona.sh ~/scripts/aula18/teste.log` |
| 3 | O `rotacao.log` registrou as execuções | `cat ~/scripts/aula18/rotacao.log` |
| 4 | **A `crontab` foi limpa** | `crontab -l` |
| 5 | Nenhum *timer* ficou ativo | `sudo systemctl list-timers --no-pager` |

O item 2 é o teste real do critério 5: se o *script* só funciona de dentro do
próprio diretório, ele falharia no `cron`.

---

## 💬 Para Discutir em Sala

- Você tem três ferramentas para agendar (`cron`, `at`, *timer*). Em um servidor
  novo hoje, qual você escolheria como padrão, e por quê?
- A rotação de *log* que você escreveu já existe pronta no `logrotate`. Vale a pena
  escrever a sua? Quando sim, quando não?

## 📌 Para a Próxima Aula

Na **Aula 19** vamos compilar e instalar programas a partir do código-fonte
(`slides/16_compilacao_e_configuracao_de_programas`): `gcc`, bibliotecas
compartilhadas e `make`.
