# Atividade 02

## Valor: 1,0 ponto na primeira nota. 
## Data Limite para Apresentação: 25/08/2023.

###  Questão 01

O objetivo desta atividade é fazer que o aluno use bastante o terminal, para se acostumar com o ambiente em linha de comando. Não use ferramentas gráficas para auxiliar, faça tudo pelo _bash_. Se você já conhecer outros comandos além dos apresentados em aula, pode utilizá-los.


Crie uma pasta chamada _atividades_ na sua máquina. Dentro dela coloque uma pasta chamada _atividade02_. O caminho completo deve ser _atividades/atividade02_.

Em seguida, dentro da pasta _atividade02_, crie três pastas:

1. professores
2. disciplinas
3. historico

Na pasta _professores_, você deve criar uma arquivo de texto vazio para cada professor do campus. Acesse a [página do Campus](https://www.quixada.ufc.br) e recupere o nome de cada docente. Por exemplo, para **João Marcelo Uchôa de Alencar**, você deve criar o arquivo _joao\_marcelo\_uchoa\_de\_alencar.txt_.

Na pasta _disciplinas_, você deve criar um arquivo de texto vazio para cada disciplina obrigatória do seu curso. Na página do curso há a grade completa. Por exemplo, para **Fundamentos de Programação**, você deve criar o arquivo _fundamentos\_de\_programacao.txt_.

Os arquivos .txt criados podem ficar vazios.

Na pasta _historico_, você deve criar, de acordo com a nomenclatura acima, uma pasta para cada disciplina que já foi aprovado. Dentro dessa pasta, deve haver dois _links_ simbólicos (_soft links_):

1.  _programa_: deve apontar para o arquivo da disciplina na pasta _disciplinas_.
2.  _professor_: deve apontar para o arquivo do professor na pasta _professores_.

**Atenção**: os _links_ deve ser relativos à pasta da disciplina no histórico. Em outras palavras, se você copiar o repositório em outra pasta, os links devem continuar válidos.

```
.
├── disciplinas
│   └── fundamentos_de_programacao.txt
├── historico
│   └── fundamentos_de_programacao
│       ├── professor -> professores/joao_marcelo_uchoa_de_alencar.txt
│       └── programa -> disciplinas/fundamentos_de_programacao.txt
└── professores
    └── joao_marcelo_uchoa_de_alencar.txt
```








