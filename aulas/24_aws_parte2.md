# 🧪 Aula 24 — AWS (parte 2): Provisionamento Automático

**Disciplina:** Programação de *Scripts* — UFC Quixadá
**Material de apoio:** `slides/19_AWS`
**Sessão:** Semana 13 — quarta, 04/11
**Entrega desta aula:** 0,7 ponto (Nota 3)
**Duração estimada:** 100 minutos

---

## 🎯 Objetivos da Aula

Ao final desta aula você deve ser capaz de:

- Provisionar uma instância no *boot* com `--user-data`.
- Depurar um `user-data` que falhou, lendo os *logs* na instância.
- Personalizar o disco com `--block-device-mappings`.
- Consultar metadados de dentro da instância.
- Escrever um *script* de implantação completo, ponta a ponta.

## 🧰 Pré-requisitos

- Aula 23 concluída, com a AWS CLI configurada e funcionando.
- Laboratório do Academy iniciado.

> ⚠️ Se as credenciais expiraram desde a última aula, atualize o `~/.aws/credentials`
> antes de começar. Confirme com `aws sts get-caller-identity`.

## 🗺️ Roteiro

| Etapa | Assunto | Tempo |
|---|---|---|
| 0 | `--user-data` | 20 min |
| 1 | Depurando o provisionamento | 20 min |
| 2 | Disco personalizado | 10 min |
| 3 | Metadados da instância | 15 min |
| 🏁 | Entrega | 30 min |

---

## 🧩 Etapa 0 — `--user-data`

O `user-data` é um *script* que a instância executa **como root, no primeiro *boot***.

### Ação

```bash
ssh disciplina
mkdir -p ~/scripts/aula24
cd ~/scripts/aula24
```

Recupere os dados do ambiente (como na Aula 23):

```bash
VPC_ID=$(aws ec2 describe-vpcs --query 'Vpcs[?IsDefault==`true`].VpcId' --output text)
SUBNET_ID=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" \
    --query 'Subnets[0].SubnetId' --output text)
AMI_ID=$(aws ec2 describe-images --owners 099720109477 \
    --filters "Name=name,Values=ubuntu/images/hvm-ssd*22.04*server*" \
              "Name=state,Values=available" \
    --query 'sort_by(Images, &CreationDate)[-1].ImageId' --output text)
echo "$VPC_ID / $SUBNET_ID / $AMI_ID"
```

Escreva o *script* de provisionamento:

```bash
cat > user_data.sh
#!/bin/bash
exec > >(tee /var/log/user-data.log) 2>&1
set -x

apt-get update -y
apt-get install -y nginx

HOSTNAME_LOCAL=$(hostname)
cat > /var/www/html/index.html <<HTML
<!doctype html>
<html>
<head><meta charset="utf-8"><title>Aula 24</title></head>
<body>
  <h1>Provisionado automaticamente</h1>
  <p>Máquina: ${HOSTNAME_LOCAL}</p>
  <p>Provisionado em: $(date)</p>
</body>
</html>
HTML

systemctl enable --now nginx
echo "provisionamento concluído" >> /var/log/user-data.log
```

Ctrl+D.

> 💡 A primeira linha do *script* — `exec > >(tee /var/log/user-data.log) 2>&1` —
> redireciona **toda** a saída do *script* para um arquivo, mantendo-a também no
> canal original. Sem isso, depurar um `user-data` que falhou é quase impossível.
> O `set -x` complementa: registra cada comando executado.

Crie o grupo e a instância:

```bash
SG_ID=$(aws ec2 create-security-group --group-name "aula24-$USER" \
    --description "Aula 24" --vpc-id "$VPC_ID" --query 'GroupId' --output text)
aws ec2 authorize-security-group-ingress --group-id "$SG_ID" --protocol tcp --port 22 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id "$SG_ID" --protocol tcp --port 80 --cidr 0.0.0.0/0

INSTANCE_ID=$(aws ec2 run-instances \
    --image-id "$AMI_ID" --instance-type t2.micro --key-name vockey \
    --security-group-ids "$SG_ID" --subnet-id "$SUBNET_ID" \
    --user-data file://user_data.sh \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$USER-aula24}]" \
    --query 'Instances[0].InstanceId' --output text)

aws ec2 wait instance-running --instance-ids "$INSTANCE_ID"
IP=$(aws ec2 describe-instances --instance-ids "$INSTANCE_ID" \
    --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)
echo "IP: $IP"
```

> ⚠️ O `file://` é obrigatório. Sem ele, a CLI trataria a string `user_data.sh` como
> o conteúdo do *script*.

A instância está `running`, mas o `user-data` ainda está rodando. Espere:

```bash
for i in $(seq 1 30); do
    if curl -sf -m 3 "http://$IP" > /dev/null; then echo "no ar!"; break; fi
    echo "aguardando... ($i)"
    sleep 10
done

curl -s "http://$IP" | head -10
```

### ✅ Checkpoint 0

✔ `curl http://$IP` devolve o HTML com o nome da máquina.
✔ Você não precisou entrar na instância para instalar nada.

### ❓ Pergunta

A instância ficou `running` bem antes de o site responder. Por que o
`aws ec2 wait instance-running` não é suficiente para saber que a aplicação subiu?

---

## 🧩 Etapa 1 — Depurando o provisionamento

Quando o `user-data` falha, a instância sobe normalmente — e nada funciona. É aqui
que a maioria trava.

### Ação

```bash
ssh -i ~/.ssh/labsuser.pem -o StrictHostKeyChecking=no ubuntu@"$IP"
```

Dentro da instância, os três lugares para olhar:

```bash
sudo cat /var/log/user-data.log | tail -20        # o seu log, se você o criou
sudo cat /var/log/cloud-init-output.log | tail -30 # a saída padrão do cloud-init
sudo cloud-init status --long                      # o estado do provisionamento
```

Confirme que o serviço subiu:

```bash
systemctl status nginx --no-pager | head -5
curl -s localhost | head -5
exit
```

Agora provoque um erro de propósito. Crie um `user-data` quebrado:

```bash
cat > user_data_ruim.sh
#!/bin/bash
exec > >(tee /var/log/user-data.log) 2>&1
set -x
apt-get install -y nginx        # sem o update antes: pode falhar
comando_que_nao_existe
systemctl enable --now nginx
```

Ctrl+D. Não vamos criar outra instância só para isso — em vez disso, discuta:

1. O `comando_que_nao_existe` falha, mas o *script* **continua** (não há `set -e`).
2. O `apt-get install` sem `update` pode falhar em uma AMI com índice velho.
3. O `user-data` roda **uma vez só**, no primeiro *boot*. Reiniciar não o executa
   de novo.

Para testar um `user-data` corrigido, o caminho é **destruir e recriar** a instância —
ou rodar o *script* à mão dentro dela, o que descaracteriza o teste.

> 💡 Isso é imutabilidade: você não conserta a instância, você a substitui. O
> Terraform (Aula 25) transforma essa ideia em ferramenta.

### ✅ Checkpoint 1

✔ Você localizou o `/var/log/cloud-init-output.log` na instância.
✔ `cloud-init status` responde `done`.
✔ Entendeu que o `user-data` não roda de novo no *reboot*.

### ❓ Pergunta

Se o `user-data` roda uma única vez, como se atualiza a configuração de uma
instância já em produção? Cite duas abordagens.

---

## 🧩 Etapa 2 — Disco personalizado

### Ação

Veja o disco atual:

```bash
ssh -i ~/.ssh/labsuser.pem -o StrictHostKeyChecking=no ubuntu@"$IP" 'df -h / && lsblk'
```

O padrão da AMI é 8 GB. Para pedir outro tamanho, use `--block-device-mappings`.
Descubra primeiro o nome do dispositivo raiz da AMI:

```bash
aws ec2 describe-images --image-ids "$AMI_ID" \
    --query 'Images[0].[RootDeviceName,BlockDeviceMappings[0].Ebs.VolumeSize]' --output text
```

O parâmetro fica assim:

```
--block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":20,"VolumeType":"gp3","DeleteOnTermination":true}}]'
```

> ⚠️ O `DeleteOnTermination: true` é importante: sem ele, o volume sobrevive ao
> encerramento da instância e continua sendo cobrado. Volumes órfãos são a forma
> mais comum de desperdiçar crédito sem perceber.

Você vai usar isso na entrega — não crie outra instância agora.

### ✅ Checkpoint 2

✔ Você identificou o `RootDeviceName` da AMI.
✔ Entendeu o papel do `DeleteOnTermination`.

---

## 🧩 Etapa 3 — Metadados da instância

Toda instância EC2 pode consultar dados sobre si mesma em um endereço especial,
`169.254.169.254`, acessível **apenas de dentro dela**.

### Ação

```bash
ssh -i ~/.ssh/labsuser.pem -o StrictHostKeyChecking=no ubuntu@"$IP"
```

Na instância, obtenha o *token* (IMDSv2) e consulte:

```bash
TOKEN=$(curl -sX PUT "http://169.254.169.254/latest/api/token" \
    -H "X-aws-ec2-metadata-token-ttl-seconds: 300")

md() { curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
    "http://169.254.169.254/latest/meta-data/$1"; echo; }

md instance-id
md instance-type
md local-ipv4
md public-ipv4
md placement/availability-zone
md ami-id
```

Isso é o que permite um *script* de provisionamento se auto-configurar — descobrir o
próprio IP, a própria zona, o próprio papel.

```bash
exit
```

Encerre tudo:

```bash
aws ec2 terminate-instances --instance-ids "$INSTANCE_ID" --output text --query 'TerminatingInstances[0].CurrentState.Name'
aws ec2 wait instance-terminated --instance-ids "$INSTANCE_ID"
aws ec2 delete-security-group --group-id "$SG_ID"
```

### ✅ Checkpoint 3

✔ `md instance-id` devolve o mesmo ID que você tem na variável `INSTANCE_ID`.
✔ A instância e o grupo foram encerrados.

### ❓ Pergunta

O endereço `169.254.169.254` é acessível apenas de dentro da instância. Por que a
AWS migrou do IMDSv1 (só um `GET`) para o IMDSv2 (com *token*)?

---

## 🏁 Entrega da Aula — 0,7 ponto (Nota 3)

Individualmente, nos últimos 30 minutos.

Escreva um par de *scripts* que provisiona um **servidor web funcional**, do zero,
sem tocar no console da AWS.

### `~/scripts/aula24/user_data.sh`

O *script* de provisionamento, que deve:

1. Registrar toda a sua saída em `/var/log/user-data.log`.
2. Atualizar o índice de pacotes e instalar o **nginx**.
3. Substituir a página padrão por uma que mostre, obtidos dos **metadados**:
   - o `instance-id`;
   - o tipo da instância;
   - a zona de disponibilidade;
   - a data do provisionamento.
4. Garantir que o nginx suba no *boot*.

### `~/scripts/aula24/deploy.sh`

O *script* de implantação, que deve:

1. Aceitar `-n <nome>` (obrigatório) e `-d <tamanho do disco em GB>` (padrão: 8).
2. Descobrir VPC, subrede e AMI dinamicamente.
3. Criar o grupo de segurança liberando **22 e 80**.
4. Criar a instância `t2.micro` com:
   - a tag `Name` igual ao valor de `-n`;
   - o disco no tamanho pedido, com `DeleteOnTermination`;
   - o `user_data.sh` como `--user-data`.
5. Esperar a instância ficar `running` **e** o site responder — testando com `curl`
   em laço, com limite de tentativas.
6. Imprimir ao final:

   ```
   Instância: i-0123456789abcdef0
   IP público: 54.234.12.98
   URL: http://54.234.12.98
   ```

7. Gravar os IDs em `recursos.txt` e falhar com mensagem no `stderr` se qualquer
   etapa não funcionar.

### Critérios de correção

| # | Critério | Valor |
|---|---|---|
| 1 | `getopts` com `-n` obrigatória e `-d` com padrão | 0,05 |
| 2 | O disco é criado no tamanho pedido, com `DeleteOnTermination` | 0,10 |
| 3 | O `user-data` instala o nginx e a porta 80 responde | 0,20 |
| 4 | A página mostra os dados vindos dos metadados | 0,15 |
| 5 | Espera o site responder, com limite de tentativas | 0,10 |
| 6 | Verifica as etapas e grava o `recursos.txt` | 0,10 |

Correção:

```bash
cd ~/scripts/aula24
./deploy.sh -n web-$USER -d 20
curl -s http://<IP> | grep -E "i-|t2.micro|us-east-1"
aws ec2 describe-instances --instance-ids <ID> \
    --query 'Reservations[0].Instances[0].BlockDeviceMappings' --output table
ssh -i ~/.ssh/labsuser.pem ubuntu@<IP> 'df -h /'
```

O `df -h /` deve mostrar cerca de 20 GB.

> ⚠️ **Encerre tudo antes de sair.** Reaproveite o `destruir.sh` da Aula 23.

---

## ✅ Checklist de Encerramento

| # | Verificação | Comando |
|---|---|---|
| 1 | Os dois *scripts* existem | `ls -l ~/scripts/aula24/*.sh` |
| 2 | O `user_data.sh` registra em *log* | `grep -c "user-data.log" user_data.sh` |
| 3 | O `deploy.sh` usa `file://` no user-data | `grep -c "file://" deploy.sh` |
| 4 | **Só a máquina de trabalho rodando** | `aws ec2 describe-instances --filters "Name=instance-state-name,Values=running" --query 'Reservations[*].Instances[*].[Tags[?Key==`Name`].Value\|[0]]' --output text` — só a sua máquina de trabalho deve aparecer |
| 5 | **Nenhum volume órfão** | `aws ec2 describe-volumes --filters "Name=status,Values=available" --query 'Volumes[*].VolumeId' --output text` |

Os itens 4 e 5 devem sair vazios.

---

## 💬 Para Discutir em Sala

- Seu `deploy.sh` tem provavelmente umas 80 linhas, metade delas de verificação de
  erro. Na Aula 25 você vai fazer o mesmo com 20 linhas de Terraform. O que a
  ferramenta declarativa está fazendo por você?
- O `user-data` roda uma vez e a instância vira "artesanal" a partir daí. Isso tem
  nome: *snowflake server*. Por que é considerado um problema?

## 📌 Para a Próxima Aula

A **Aula 25** começa o Terraform (`slides/20_Terraform`). Você vai reconstruir
exatamente a infraestrutura desta aula, de forma declarativa — e ver a diferença
aparecer sozinha.

Mantenha o `deploy.sh` à mão: vamos compará-los lado a lado.
