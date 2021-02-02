# Exercício 08

Data: 02/02/2021

Coloque os arquivos na pasta _exercicios/exercicio08_.

## Questão 01

O objetivo é criar um _script_ chamado _sistema.sh_ para permitir monitorar o desempenho de um servidor Linux. 
  
1. Ele deve exibir um menu com opções para o usuário. O menu e o _prompt_ de opção devem ser encapsulados em uma **função**.
2. Ao digitar uma das opções, a tela deve ser limpa, um comando executado e o resultado exibido. 
3. Após o usuário apertar _enter_ retornar para o menu inicial.
  
Opções devem ser, de acordo com [Performance Analysis](http://techblog.netflix.com/2015/11/linux-performance-analysis-in-60s.html):

1. Tempo ligado (uptime)
2. Últimas Mensagens do Kernel (dmesg | tail -n 10)
3. Memória Virtual (vmstat 1 10)
4. Uso da CPU por núcleo (mpstat -P ALL 1 5)
5. Uso da CPU por processos (pidstat 1 5)
6. Uso da Memória Física (free -m)
  
Por mais simples que sejam os comandos, também coloque-os em funções. Para sair, o usuário deve pressionar CTRL-C, a tela deve ser limpa
e uma mensagem de despedida deve ser exibida. 
