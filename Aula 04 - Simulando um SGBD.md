# Atividade Prática: Simulando um SGBD sobre Arquivos de Texto

## Objetivo
Compreender como os Sistemas de Gerenciamento de Bancos de Dados (SGBDs) acessam, interpretam e recuperam dados armazenados em disco, simulando operações de consulta, filtragem e projeção diretamente sobre um arquivo `.txt`.

---

## Pré-requisitos
* Certifique-se de ter o arquivo de dados fornecido salvo no mesmo diretório do seu código.
* Identifique o delimitador utilizado no arquivo (ex: `;`, `,`, ou `\t`) para realizar a separação dos campos durante a leitura.

---

## Desafios Práticos

### Desafio 1: "Full Table Scan" (`SELECT *`)
Escreva uma função que abra o arquivo `.txt`, leia todas as linhas sequencialmente e faça o *parsing* (divisão) dos registros com base no delimitador, exibindo os dados de forma estruturada no console.

### Desafio 2: Busca por Chave Primária (`WHERE id = X`)
Crie um algoritmo de busca por registro único:
1. Receba um identificador único (ID) informado pelo usuário.
2. Percorra o arquivo linha a linha até encontrar o registro correspondente.
3. Interrompa a leitura imediatamente após encontrar o dado (**Early Exit**) e exiba as informações.
4. Trate o caso em que o ID não existe no arquivo.

### Desafio 3: Filtro e Projeção (`SELECT coluna1, coluna2 WHERE condição`)
Implemente uma consulta com filtro condicional e seleção de campos específicos:
1. Aplique um critério de filtragem sobre um campo numérico ou textual (ex: valores acima de um limite ou correspondência de categoria).
2. Exiba no terminal apenas colunas específicas do registro, omitindo os demais campos.

---

## Questões para Reflexão
1. **Desempenho:** Se esse arquivo de texto crescesse para milhões de linhas, qual seria o impacto do método de leitura utilizado no Desafio 2?
2. **Indexação:** Como um índice (ex: Tabela Hash ou Árvore B) ajudaria a evitar a leitura sequencial do arquivo inteiro?
3. **Concorrência:** Se dois processos tentassem ler e alterar esse arquivo de texto ao mesmo tempo, quais problemas poderiam ocorrer?
