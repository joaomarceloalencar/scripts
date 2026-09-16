# Atividade de Emergência (Sem Energia/Computador)

Este documento contém duas opções de atividades para serem aplicadas em sala de aula quando não houver disponibilidade de computadores ou projetores. O foco é o raciocínio lógico, a estrutura de comandos e a introdução a novas ferramentas de manipulação de fluxo.

---

## Opção 01: O Terminal Humano (Desafio de Estruturação)

**Objetivo:** Praticar a criação de estruturas de diretórios e arquivos usando comandos básicos (`mkdir`, `touch`, `cp`, `mv`) e caminhos relativos.

**Instruções para a turma:**
"Vocês são administradores de sistemas. O cliente pediu para organizar a estrutura de arquivos de um novo projeto de software. Vocês devem escrever a sequência de comandos `shell` que, se executados em um terminal, criariam a estrutura abaixo, partindo de um diretório vazio chamado `projeto_final`."

**O Cenário (Escrever no quadro):**
Estrutura desejada:
```text
projeto_final/
├── docs/
│   ├── manual.txt
│   └── notas.txt
├── src/
│   ├── main.py
│   ├── utils.py
│   └── config.json
├── tests/
│   └── test_main.py
└── scripts/
    └── setup.sh
```

**Regras Adicionais:**
1. O arquivo `manual.txt` deve ser criado inicialmente na raiz e depois movido para `docs/`.
2. O arquivo `test_main.py` deve ser copiado de `src/` para `tests/`.
3. Devem usar comandos de criação (`mkdir`, `touch`), movimentação (`mv`) e cópia (`cp`).
4. **Proibido** usar caminhos absolutos. Use apenas caminhos relativos.

---

## Opção 02: Fluxograma de Automação + Introdução ao `xargs`

**Objetivo:** Introduzir o conceito de "ponte" de dados entre comandos e aplicar em um problema de automação de organização de arquivos.

**Explicação para a Lousa (Conteúdo Teórico):**
> **Ferramenta Nova: `xargs`**
> 
> **O que é?** O `xargs` lê a saída de um comando anterior (padrão de entrada) e a transforma em **argumentos** para outro comando.
> 
> **Por que usar?** Alguns comandos (como `mv`, `rm`, `cp`) não aceitam listas de arquivos vindas de um "pipe" (`|`) diretamente. O `xargs` serve como uma "ponte".
> 
> **Sintaxe Básica:**
> `comando1 | xargs comando2`
> 
> **Dica de Sintaxe para `mv` com `xargs`:**
> Por padrão, o `mv` espera: `mv origem destino`.
> O `xargs` coloca os itens no **final** do comando. Para evitar confusão, use a flag `-t` (target) para definir o destino primeiro:
> `xargs mv -t pasta_destino/`
> 
> **Exemplo:**
> `ls *.pdf | xargs mv -t documentos_pdf/`

**O Problema para a turma resolver:**
"Temos uma pasta chamada `downloads_baguncados` com vários arquivos. Precisamos criar um script que:
1. Crie uma pasta chamada `documentos_pdf`.
2. Identifique todos os arquivos que terminam em `.pdf` no diretório atual (use `ls`).
3. Mova todos esses arquivos para a pasta `documentos_pdf` usando a nova ferramenta `xargs`."

**Resposta esperada:**
```bash
mkdir -p documentos_pdf
ls *.pdf | xargs mv -t documentos_pdf/
```
