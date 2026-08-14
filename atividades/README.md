# Atividades

**Não há mais atividades para casa.** Toda avaliação acontece em sala, como a
entrega final de cada aula prática em [`../aulas/`](../aulas/).

Este diretório guarda duas coisas:

- Este índice, que mapeia cada nota às aulas que a compõem.
- O [banco de questões de reserva](questoes_reserva.md), com enunciados não usados
  nas aulas — material para prova, segunda chamada ou substituição de entrega.

## Composição das notas

Cada nota vale **10,0 pontos**, somados a partir das entregas das aulas do bloco.
Ao fechar cada nota, as **duas piores entregas do bloco são descartadas**.

### Nota 1 — Caps. 01 a 08

| Aula | Tema | Entrega | Pontos |
|---|---|---|---|
| [01](../aulas/01_primeiro_script.md) | Introdução, SSH, primeiro *script* | `registro.sh` | 1,0 |
| [02](../aulas/02_navegacao_e_arquivos.md) | Navegação e arquivos | estrutura `meucurso/` | 1,0 |
| [03](../aulas/03_links_permissoes_e_busca.md) | Ligações, permissões, busca | `historico/` com *links* relativos | 1,0 |
| [04](../aulas/04_expressoes_regulares.md) | Expressões regulares | `logins.sh` | 1,0 |
| [05](../aulas/05_redirecionamento.md) | Redirecionamento e *pipes* | `relatorio.sh` | 1,0 |
| [06](../aulas/06_comandos_avancados.md) | `cut`, `tr`, `sed`, `uniq` | três *scripts* sobre `acessos.log` | 1,0 |
| [07](../aulas/07_variaveis_e_parametros.md) | Variáveis e parâmetros | `saudacao.sh` | 1,0 |
| [08](../aulas/08_condicionais.md) | Condicionais | `valida_dir.sh`, `classifica_num.sh` | 1,0 |
| [09](../aulas/09_iteracoes.md) | Iterações | `cinco_diretorios.sh`, `ordenar_linhas.sh` | 2,0 |

### Nota 2 — Caps. 09 a 13

| Aula | Tema | Entrega | Pontos |
|---|---|---|---|
| [10](../aulas/10_gerencia_de_processos.md) | Processos | `varredura.sh` | 1,25 |
| [11](../aulas/11_leitura_e_escrita.md) | `read`, `printf`, `tput` | `sistema.sh` | 1,25 |
| [12](../aulas/12_variaveis_e_vetores.md) | Vetores e *subshell* | `contaPalavras.sh`, `contadorVetor.sh` | 1,25 |
| [13](../aulas/13_miscelanea.md) | Funções, `getopts`, `trap` | `hosts.sh` | 1,25 |
| [14](../aulas/14_awk_parte1.md) | AWK: padrões e campos | quatro programas `.awk` | 1,25 |
| [15](../aulas/15_awk_parte2.md) | AWK: laços e vetores | `disciplina.awk`, `marajas.awk` | 1,25 |
| [16](../aulas/16_integradora.md) | Integradora | `monitor.sh` | 2,5 |

### Nota 3 — Caps. 14 a 21

| Aula | Tema | Entrega | Pontos |
|---|---|---|---|
| [17](../aulas/17_scripts_de_inicializacao.md) | `systemd` | serviço `coletor` | 0,7 |
| [18](../aulas/18_execucao_programada.md) | `cron` e *timers* | `rotaciona.sh` | 0,7 |
| [19](../aulas/19_compilacao.md) | Compilação e `make` | `instalador.sh` | 0,7 |
| [20](../aulas/20_ferramentas_de_rede.md) | `wget`, `curl`, `nc`, `ss` | `monitor_web.sh` | 0,7 |
| [21](../aulas/21_dialog_parte1.md) | `dialog`: as caixas | `cantina.sh` | 0,7 |
| [22](../aulas/22_dialog_parte2.md) | `dialog`: fluxos | `compactador.sh` | 0,7 |
| [23](../aulas/23_aws_parte1.md) | AWS CLI | `criar_instancia.sh`, `destruir.sh` | 0,7 |
| [24](../aulas/24_aws_parte2.md) | Provisionamento | `deploy.sh`, `user_data.sh` | 0,7 |
| [25](../aulas/25_terraform_parte1.md) | Terraform: básico | infraestrutura de uma máquina | 0,7 |
| [26](../aulas/26_terraform_parte2.md) | Terraform: `for_each` | cliente + banco de dados | 0,7 |
| [27](../aulas/27_ansible_parte1.md) | Ansible: *playbooks* | `banco.yml` | 0,7 |
| [28](../aulas/28_ansible_parte2.md) | Ansible: dinâmico e *roles* | projeto com três *roles* | 0,7 |
| [29](../aulas/29_projeto_parte1.md) | Projeto: infraestrutura | `infra/` em Terraform | 0,7 |
| [30](../aulas/30_projeto_parte2.md) | Projeto: configuração | `config/` e `implantar.sh` | 0,9 |

## De onde veio cada aula

As aulas foram construídas a partir dos enunciados das antigas atividades 01 a 13,
usadas até 2025.2. O mapeamento, para referência:

| Atividade antiga | Absorvida por |
|---|---|
| 01 — AWS Academy e SSH | Aula 01 |
| 02 — Estrutura de diretórios e *links* | Aulas 02 e 03 |
| 03 — `grep` e `saudacao.sh` | Aulas 04 e 07 |
| 04 — `pipe`, `cut`, `sort`, `uniq` | Aula 06 |
| 05 — Condicionais e `agenda.sh` | Aula 08 (e o padrão CRUD na Aula 13) |
| 06 — Laços aninhados e ordenação | Aula 09 |
| 07 — Processos em segundo plano e `tput` | Aulas 10 e 11 |
| 08 — `contaPalavras.sh` e `getopts`/`trap` | Aulas 12 e 13 |
| 09 — `hosts.sh` e `sistema.sh` | Aulas 13 e 11 |
| 10 — AWK | Aulas 14 e 15 |
| 11 — `dialog` | Aulas 21 e 22 |
| 12 — AWS CLI | Aulas 23 e 24 |
| 13 — Terraform e Ansible | Aulas 25 a 28 |

Os enunciados originais permanecem no histórico do Git, no *commit* anterior à
reorganização.
