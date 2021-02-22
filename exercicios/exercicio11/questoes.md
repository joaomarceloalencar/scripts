# Exercício 11 

Data: 23/02/2021

Coloque os arquivos na pasta _exercicios/exercicio11_.

## Questão Única

O objetivo é desenvolver um _script_ _criarInstancia.sh_ que crie uma instância na AWS. Ele deve funcionar assim:

```
$ ./criarInstancia.sh nomedachave
Instância criada.
Endereço público: 87.43.129.12
```

Ou seja, a única informação que o usuário deve fornecer é o nome da chave, criada previamente. O _script_ deve funcionar em qualquer conta da AWS na região _us-east-1_. Observe os seguintes pontos:

1. Você pode anotar no _script_ o ID da AMI (imagem) do Ubuntu, que é o mesmo para todos os usuários.
2. Recupere a subrede do VPC padrão.
3. Crie um grupo de segurança liberando a porta 22 e 80, TCP.
4. Crie a instância. 

Durante a aula de exercícios irei testar na minha conta a solução de vocês e tirar qualquer dúvida. Também farei a correção ao vivo na aula.  

Para ajudar, consulte a documentação da [linha de comando](https://docs.aws.amazon.com/cli/latest/index.html) e o [tutorial da AWS](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html).
