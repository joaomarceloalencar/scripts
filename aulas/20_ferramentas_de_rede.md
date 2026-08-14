# 🧪 Aula 20 — Ferramentas de Rede

**Disciplina:** Programação de *Scripts* — UFC Quixadá
**Material de apoio:** `slides/17_ferramentas_de_rede`
**Sessão:** Semana 11 — quarta, 21/10
**Entrega desta aula:** 0,7 ponto (Nota 3)
**Duração estimada:** 100 minutos

---

## 🎯 Objetivos da Aula

Ao final desta aula você deve ser capaz de:

- Baixar arquivos e consultar APIs com `wget` e `curl`.
- Inspecionar cabeçalhos HTTP e códigos de status.
- Listar portas em escuta com `ss`.
- Abrir e testar conexões TCP com `nc`.
- Extrair dados de uma resposta JSON em um *script*.

## 🧰 Pré-requisitos

- Aulas 04 (regex), 06 (texto) e 13 (`getopts`).

## 🗺️ Roteiro

| Etapa | Assunto | Tempo |
|---|---|---|
| 0 | `wget` | 15 min |
| 1 | `curl` e o protocolo HTTP | 20 min |
| 2 | `ss`: o que está escutando | 15 min |
| 3 | `nc`: conexões na unha | 20 min |
| 🏁 | Entrega | 25 min |

---

## 🧩 Etapa 0 — `wget`

O `wget` é feito para **baixar arquivos**.

### Ação

```bash
ssh disciplina
mkdir -p ~/scripts/aula20
cd ~/scripts/aula20

wget https://www.gnu.org/software/hello/manual/hello.txt
ls -l hello.txt
```

As opções mais úteis:

```bash
wget -q -O saida.txt https://www.gnu.org/software/hello/manual/hello.txt
wget -c https://ftp.gnu.org/gnu/hello/hello-2.12.1.tar.gz    # continua download parcial
wget --spider -S https://www.gnu.org 2>&1 | head -12         # só checa, não baixa
```

| Opção | Efeito |
|---|---|
| `-q` | silencioso |
| `-O <arq>` | grava com este nome (`-O -` manda para o `stdout`) |
| `-c` | continua um download interrompido |
| `--spider` | só verifica se existe |
| `-r` | recursivo (espelha um site) |
| `--limit-rate=200k` | limita a banda |

O `-O -` permite encanar direto:

```bash
wget -q -O - https://www.gnu.org/software/hello/manual/hello.txt | wc -l
```

### ✅ Checkpoint 0

✔ `hello.txt` foi baixado e tem conteúdo.
✔ `wget -q -O - ... | wc -l` conta as linhas sem gravar arquivo.

### ❓ Pergunta

O `wget` sem `-q` imprime uma barra de progresso. Para onde ela vai — `stdout` ou
`stderr`? Descubra rodando `wget URL > /dev/null` e observando.

---

## 🧩 Etapa 1 — `curl` e o protocolo HTTP

O `curl` é feito para **conversar com serviços**.

### Ação

```bash
curl -s https://api.github.com/users/joaomarceloalencar | head -20
```

Veja o que acontece por baixo:

```bash
curl -I https://www.gnu.org                       # só os cabeçalhos
curl -s -o /dev/null -w "%{http_code}\n" https://www.gnu.org
curl -s -o /dev/null -w "%{http_code}\n" https://www.gnu.org/naoexiste
```

Os códigos de status que importam:

| Faixa | Significado |
|---|---|
| 2xx | sucesso (200 OK, 201 Created) |
| 3xx | redirecionamento (301, 302) |
| 4xx | erro do cliente (404 não encontrado, 403 proibido) |
| 5xx | erro do servidor |

O `-w` aceita várias variáveis, úteis para medir:

```bash
curl -s -o /dev/null -w "código: %{http_code}\ntempo: %{time_total}s\ntamanho: %{size_download} bytes\n" https://www.gnu.org
```

Seguindo redirecionamentos e enviando dados:

```bash
curl -s -o /dev/null -w "%{http_code} -> %{url_effective}\n" -L http://www.gnu.org
curl -s -X POST -d "campo=valor" https://httpbin.org/post | head -20
curl -s -H "Accept: application/json" https://api.github.com/zen
```

| Opção | Efeito |
|---|---|
| `-s` | silencioso |
| `-I` | só cabeçalhos (HEAD) |
| `-L` | segue redirecionamentos |
| `-X <verbo>` | método HTTP |
| `-d <dados>` | corpo da requisição |
| `-H <cabeçalho>` | adiciona cabeçalho |
| `-o <arq>` | grava a saída |
| `-w <formato>` | imprime métricas ao final |
| `-f` | falha (retorno ≠ 0) em erro HTTP |

> ⚠️ Por padrão o `curl` retorna `0` mesmo em um 404 — para ele, receber a resposta
> **é** sucesso. Em *scripts*, use `-f` para que o código HTTP vire código de saída.
>
> ```bash
> curl -s https://www.gnu.org/naoexiste  > /dev/null; echo "sem -f: $?"
> curl -sf https://www.gnu.org/naoexiste > /dev/null; echo "com -f: $?"
> ```

### Ação — extraindo dados do JSON

```bash
curl -s https://api.github.com/users/joaomarceloalencar > perfil.json

grep '"public_repos"' perfil.json
grep '"public_repos"' perfil.json | cut -d: -f2 | tr -d ' ,'
awk -F'"' '/"login"/ { print $4; exit }' perfil.json
```

Se o `jq` estiver disponível, fica bem melhor:

```bash
command -v jq && jq -r '.login, .public_repos' perfil.json
```

### ✅ Checkpoint 1

✔ `curl -I` mostra os cabeçalhos e o `HTTP/2 200`.
✔ Uma URL inexistente devolve `404`.
✔ Você extraiu o número de repositórios do JSON.
✔ Confirmou a diferença de retorno entre `curl -s` e `curl -sf`.

### ❓ Pergunta

`wget` e `curl` fazem coisas parecidas. Depois desta etapa, em que situação cada um
é a escolha natural?

---

## 🧩 Etapa 2 — `ss`: o que está escutando

### Ação

```bash
ss -tuln
```

| Letra | Significado |
|---|---|
| `-t` | TCP |
| `-u` | UDP |
| `-l` | só o que está em escuta (*listening*) |
| `-n` | números, sem resolver nomes |
| `-p` | mostra o processo (exige privilégio) |

```bash
ss -tuln | head -10
ss -tn state established | head -5      # conexões ativas
sudo ss -tulnp 2>/dev/null | head -5    # com o processo dono
```

Encontre quem está na porta 22:

```bash
ss -tln '( sport = :22 )'
```

> 💡 O `netstat` faz o mesmo e ainda aparece em muito material antigo, mas está
> obsoleto e nem sempre vem instalado. Prefira o `ss`.

### ✅ Checkpoint 2

✔ `ss -tuln` lista a porta 22 em escuta.
✔ `ss -tn state established` mostra a sua própria conexão SSH.

### ❓ Pergunta

O `ss -tuln` mostra endereços como `0.0.0.0:22` e `127.0.0.1:631`. Qual a diferença
prática entre os dois, do ponto de vista de quem consegue conectar?

---

## 🧩 Etapa 3 — `nc`: conexões na unha

O `nc` (*netcat*) abre uma conexão TCP crua. Serve tanto para testar quanto para
transferir dados.

### Ação — testando portas

```bash
nc -zv localhost 22
nc -zv localhost 9999
```

O `-z` só testa e o `-v` fala o que aconteceu. Uma varredura simples:

```bash
for p in 21 22 25 80 443; do
    nc -z -w1 localhost "$p" 2>/dev/null && echo "porta $p aberta"
done
```

### Ação — cliente e servidor

Você precisa de **dois terminais**. Use o `tmux` da Aula 10:

```bash
tmux new -s rede
# Ctrl+B % para dividir
```

No painel da **esquerda** (servidor):

```bash
nc -l 12345
```

No painel da **direita** (cliente):

```bash
nc localhost 12345
```

Digite no cliente e veja aparecer no servidor. É um bate-papo. Ctrl+C encerra os dois.

### Ação — transferindo um arquivo

Servidor (esquerda) — fica esperando e grava o que chegar:

```bash
nc -l 12345 > recebido.txt
```

Cliente (direita) — envia:

```bash
nc -q1 localhost 12345 < hello.txt
```

Confira:

```bash
wc -l hello.txt recebido.txt
diff hello.txt recebido.txt && echo "idênticos"
```

### Ação — falando HTTP na mão

```bash
printf 'GET / HTTP/1.1\r\nHost: www.gnu.org\r\nConnection: close\r\n\r\n' | nc www.gnu.org 80 | head -12
```

Você acabou de fazer manualmente o que o `curl` faz. Repare no `\r\n` — o HTTP exige
esse par, não apenas `\n`.

Encerre a sessão:

```bash
tmux kill-session -t rede
```

### ✅ Checkpoint 3

✔ `nc -zv localhost 22` reporta sucesso e a porta 9999, falha.
✔ O bate-papo entre os dois painéis funcionou.
✔ O `recebido.txt` é idêntico ao `hello.txt`.
✔ A requisição HTTP manual devolveu `HTTP/1.1 200 OK`.

### ❓ Pergunta

Você transferiu um arquivo com `nc`, sem senha e sem criptografia. Por que isso é
útil em uma rede local de laboratório e inaceitável na internet?

---

## 🏁 Entrega da Aula — 0,7 ponto (Nota 3)

Individualmente, nos últimos 25 minutos.

Crie o *script* `~/scripts/aula20/monitor_web.sh`, que verifica a saúde de uma lista
de serviços web.

**Uso:** `./monitor_web.sh -f <arquivo de urls> [-t <timeout>] [-o <saida.csv>]`

1. Trate as opções com `getopts`. A `-f` é obrigatória; `-t` tem padrão `5` e `-o`
   tem padrão `resultado.csv`.
2. O arquivo de entrada tem **uma URL por linha**; linhas em branco e linhas
   começadas com `#` devem ser ignoradas.
3. Para cada URL, o *script* deve obter, em **uma única chamada** ao `curl`:
   - o código de status HTTP;
   - o tempo total da requisição;
   - o tamanho da resposta em bytes.
4. Gravar tudo em CSV, com cabeçalho:

   ```
   url;status;tempo_s;tamanho_bytes;situacao
   https://www.gnu.org;200;0.412;12043;OK
   https://exemplo.invalido;000;5.001;0;FALHA
   ```

   A coluna `situacao` é `OK` para status 2xx ou 3xx, e `FALHA` para o resto.
5. Ao final, imprimir na tela um resumo, **usando AWK** sobre o CSV gerado:

   ```
   Verificadas: 5 | OK: 3 | FALHA: 2 | Tempo médio: 0.83s
   ```

6. O código de saída do *script* deve ser `0` se todas passaram e `1` se alguma
   falhou.

Arquivo de teste — crie como `urls.txt`:

```
# serviços para monitorar
https://www.gnu.org
https://api.github.com
https://www.gnu.org/naoexiste

https://exemplo.invalido
```

### Critérios de correção

| # | Critério | Valor |
|---|---|---|
| 1 | `getopts` com `-f` obrigatória e padrões corretos | 0,10 |
| 2 | Ignora linhas em branco e comentários | 0,10 |
| 3 | Obtém status, tempo e tamanho em uma só chamada ao `curl` | 0,20 |
| 4 | O CSV sai no formato pedido, com a coluna `situacao` | 0,15 |
| 5 | O resumo é calculado com AWK | 0,10 |
| 6 | Código de saída reflete o resultado | 0,05 |

Correção:

```bash
cd ~/scripts/aula20
./monitor_web.sh; echo "retorno=$?"
./monitor_web.sh -f urls.txt -t 3
cat resultado.csv
echo "retorno=$?"
grep -c awk monitor_web.sh
```

> 💡 O critério 3 é o mais valioso e tem um caminho direto: o `-w` do `curl` aceita
> várias variáveis em um só formato. Escolha um separador e quebre o resultado com
> `IFS` no `read` (Aula 09).

---

## ✅ Checklist de Encerramento

| # | Verificação | Comando |
|---|---|---|
| 1 | O *script* é executável | `ls -l monitor_web.sh` |
| 2 | O CSV tem cabeçalho e uma linha por URL válida | `cat resultado.csv` |
| 3 | Usa `curl` uma vez por URL | `grep -c curl monitor_web.sh` |
| 4 | O resumo usa AWK | `grep -c awk monitor_web.sh` |
| 5 | Nenhuma sessão `tmux` ficou aberta | `tmux ls` |

---

## 💬 Para Discutir em Sala

- Seu *script* faz o que ferramentas como o Zabbix e o Nagios fazem, em 40 linhas.
  O que falta para ele ser usável de verdade em produção?
- Você usou `nc` para falar HTTP na mão. Isso ajudou a entender o protocolo? Onde
  esse tipo de exercício é útil no trabalho real?

## 📌 Para a Próxima Aula

Na **Aula 21** começamos o `dialog` (`slides/18_dialog`): interfaces de texto com
janelas, menus e formulários — o último assunto antes da nuvem.
