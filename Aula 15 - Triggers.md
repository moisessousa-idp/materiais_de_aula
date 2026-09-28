# Atividade Prática: Automação e Integridade com Triggers em SGBD

**Curso:** Ciência da Computação / Sistemas de Informação  
**Disciplina:** Banco de Dados II  
**Tema:** Triggers (Gatilhos) em Linguagem SQL (`BEFORE`, `AFTER`, `INSERT`, `UPDATE`, `DELETE`, `NEW` e `OLD`)  
**Contexto:** Sistema de Gestão Aeroportuária (Projeto Individual)

---

## 1. Objetivos da Atividade

A presente atividade prática tem como objetivo consolidar a aplicação de **Triggers (Gatilhos)** na camada de banco de dados para a automação de regras de negócio, garantia da integridade referencial complexa e implementação de mecanismos de auditoria.

Considerando que cada discente desenvolveu um modelo relacional individual para a gestão de um aeroporto (possuindo variações na modelagem de entidades como voos, aeronaves, passagens, portões e passageiros), a atividade exige a adaptação das diretrizes genéricas às especificidades do esquema conceitual e lógico de cada projeto.

---

## 2. Fundamentação Teórica e Síntese de Conceitos

Um *Trigger* é um objeto procedural armazenado no SGBD que é executado automaticamente em resposta a um evento de manipulação de dados (`DML`: `INSERT`, `UPDATE` ou `DELETE`) em uma tabela específica.

### 2.1. Classificação por Momento de Execução
*   **`BEFORE`:** O gatilho é disparado *antes* de a operação de manipulação ser persistida na tabela. É a abordagem recomendada para **validações de dados**, sanitização de entradas e prevenção de estados inválidos.
*   **`AFTER`:** O gatilho é disparado *após* a conclusão e gravação da operação na tabela. É a abordagem indicada para **auditoria**, rastreabilidade e **propagação de alterações** para tabelas derivadas.

### 2.2. Variáveis Especiais de Escopo (`NEW` e `OLD`)
Durante a execução de um gatilho orientado a linha (`FOR EACH ROW`), o SGBD disponibiliza pseudo-estruturas para acesso aos estados dos dados:
*   **`NEW`:** Referencia a nova linha que está sendo inserida (`INSERT`) ou a nova versão da linha resultante de uma alteração (`UPDATE`). Indisponível em operações `DELETE`.
*   **`OLD`:** Referencia o estado original da linha antes da alteração (`UPDATE`) ou a linha que está sendo removida (`DELETE`). Indisponível em operações `INSERT`.

### 2.3. Controle de Exceções e Interrupção
Para cancelar uma operação `DML` e reverter a transação em decorrência do descumprimento de uma regra de negócio, utiliza-se a instrução de lançamento de exceções do padrão ANSI SQL:
```sql
SIGNAL SQLSTATE '45000'
SET MESSAGE_TEXT = 'Descrição formal do erro de validação.';
```

---

## 3. Diretrizes e Requisitos da Atividade

Cada discente deverá implementar **três gatilhos distintos** em seu banco de dados aeroportuário, atendendo aos cenários operacionais descritos a seguir.

### Desafio 1: Validação de Regra de Negócio Operacional (`BEFORE INSERT` ou `BEFORE UPDATE`)

*   **Objetivo:** Impedir a persistência de registros em desacordo com as restrições operacionais do aeroporto.
*   **Descrição:** O discente deve selecionar uma regra de negócio aplicável à sua estrutura e criar um gatilho do tipo `BEFORE`.
*   **Exemplos de Aplicação (Escolher uma opção compatível com seu modelo):**
    1.  *Capacidade Operacional:* Verificar se a inclusão de uma nova reserva/passagem excede a capacidade máxima da aeronave vinculada ao voo.
    2.  *Coerência Temporal:* Impedir a gravação de um voo cuja data/hora estimada de partida seja posterior à data/hora de chegada.
    3.  *Disponibilidade de Infraestrutura:* Impedir a alocação de uma aeronave em um portão de embarque com status diferente de `LIVRE` ou `OPERACIONAL`.
*   **Requisito Obrigatório:** Interromper a execução via `SIGNAL SQLSTATE '45000'` exibindo uma mensagem descritiva em caso de violação da regra.

### Desafio 2: Auditoria e Rastreabilidade de Modificações (`AFTER UPDATE`)

*   **Objetivo:** Garantir a irrefutabilidade e o histórico de alterações em entidades críticas do sistema.
*   **Descrição:** 
    1.  Projetar e criar uma tabela de auditoria (exemplo: `LOG_ALTERACAO_VOO` ou `AUDITORIA_STATUS`) contendo os campos: chave primária do log, chave primária do registro afetado, valor anterior, valor posterior, data/hora da alteração (`TIMESTAMP`) e usuário do SGBD responsável pela operação (`CURRENT_USER`).
    2.  Implementar um gatilho do tipo `AFTER UPDATE` que capture mudanças de atributos críticos (ex: status do voo, portão alocado ou tarifa da passagem) e insira o registro correspondente na tabela de auditoria.
*   **Requisito Obrigatório:** Utilizar conjuntamente as pseudo-tabelas `OLD` e `NEW` para registrar a transição de estados dos atributos monitorados.

### Desafio 3: Sincronização Automática de Dados em Cascata (`AFTER INSERT` ou `AFTER DELETE`)

*   **Objetivo:** Manter a consistência de colunas derivadas ou status de entidades associadas sem a necessidade de intervenção da aplicação cliente.
*   **Descrição:** Criar um gatilho do tipo `AFTER` que execute um comando `UPDATE` em uma segunda tabela a partir de uma alteração efetuada na tabela principal.
*   **Exemplos de Aplicação (Escolher uma opção compatível com seu modelo):**
    1.  *Atualização de Assentos:* Ao inserir um registro na tabela de passagens emitidas, decrementar automaticamente o saldo de assentos disponíveis no voo correspondente.
    2.  *Atualização de Status de Recursos:* Ao registrar a finalização de um voo (status alterado para `CONCLUIDO`), atualizar automaticamente o status da aeronave para `EM SOLO` ou do piloto para `DISPONIVEL`.
*   **Requisito Obrigatório:** A alteração secundária deve utilizar a chave estrangeira contida na estrutura `NEW` ou `OLD` para delimitar o registro a ser atualizado.

---

## 4. Roteiro de Validação e Testes

Para demonstrar a efetividade das soluções desenvolvidas, o script final deve conter os comandos de teste e verificação para cada um dos gatilhos implementados.

### 4.1. Validação do Desafio 1 (Gatilho de Validação)
1.  Executar uma instrução SQL (`INSERT` ou `UPDATE`) enviando dados propositalmente inválidos. **Resultado esperado:** Bloqueio pelo SGBD com o código de erro retornado pelo `SIGNAL SQLSTATE`.
2.  Executar a mesma instrução com dados válidos. **Resultado esperado:** Inserção/Atualização realizada com sucesso.

### 4.2. Validação do Desafio 2 (Gatilho de Auditoria)
1.  Executar um comando `UPDATE` em um registro monitorado da tabela principal.
2.  Realizar uma consulta (`SELECT *`) na tabela de auditoria criada e comprovar o registro correto dos valores antigo e novo, com o carimbo de data/hora e usuário.

### 4.3. Validação do Desafio 3 (Gatilho de Sincronização)
1.  Consultar o estado do registro que sofrerá o impacto indireto antes da operação.
2.  Executar a operação DML (`INSERT` ou `DELETE`) que dispara o gatilho.
3.  Consultar novamente o registro impactado e comprovar a atualização automática efetuada pelo SGBD.

---

## 5. Critérios de Avaliação e Entregáveis

O trabalho deve ser entregue em um único arquivo de script SQL (`.sql`) estruturado contendo:

1.  **Cabeçalho:** Identificação do aluno, nome do banco de dados e descrição sintética das tabelas utilizadas no seu modelo.
2.  **DDL da Tabela de Auditoria:** Comando de criação da tabela de log utilizada no Desafio 2.
3.  **Código-Fonte dos Triggers:** Implementação completa dos 3 gatilhos, devidamente comentados quanto ao propósito e lógica adotada.
4.  **Bateria de Testes:** Instruções SQL demonstrando a execução bem-sucedida e o bloqueio de operações para cada um dos gatilhos.

### Matriz de Avaliação:
*   **Adereço à Sintaxe e Boas Práticas:** Correctitude no uso de delimitadores, estrutura do bloco procedural e nomes identificadores.
*   **Adequação ao Modelo Individual:** Correta adaptação das regras ao esquema relacional do próprio discente.
*   **Tratamento de Exceções e Consistência:** Uso adequado de `SIGNAL SQLSTATE`, `NEW` e `OLD`.
*   **Validação Prática:** Cobertura de cenários válidos e inválidos nos testes apresentados.
