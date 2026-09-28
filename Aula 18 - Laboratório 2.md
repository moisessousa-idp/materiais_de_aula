# Roteiro Prático: Laboratório 01 – Parte 2

**Disciplina:** Banco de Dados  
**Carga Horária Prática:** 2 horas (120 minutos)  
**Organização:** Trabalho em Dupla (Sessão A - Aluno A / Sessão B - Aluno B)  
**Pré-requisito:** Tabelas criadas, normalizadas e povoadas (Etapas 1 a 5).

---

> **Aviso Importante sobre Variáveis:**  
> Este roteiro é genérico. Como cada dupla definiu nomes próprios de tabelas e colunas no seu modelo físico, você deverá adaptar os nomes indicados entre `<CHAVES_ANGULARES>` para corresponderem exatamente à estrutura do seu banco de dados.

---

## Parte 1 – Views e Índices (30 min)

### Exercício 1.1: Agregação e Abstração com Views
Crie em seu banco 3 visões para simplificar a extração de relatórios recorrentes:

1. **`vw_locacoes_ativas`**: Deve listar cliente, veículo e datas de retirada e devolução prevista, filtrando apenas as locações que **ainda não possuem** data real de devolução.
2. **`vw_veiculos_disponiveis`**: Deve listar os veículos prontos para locação com suas respectivas categorias e valores de diária.
3. **`vw_faturamento_mensal`**: Deve somar os valores das locações agrupados por mês/ano e por filial de retirada.

---

### Exercício 1.2: Otimização e Análise do Plano de Execução
Escolha 3 consultas frequentes no seu banco para analisar e otimizar com o comando `EXPLAIN` (ou `EXPLAIN ANALYZE`):

1. **Consulta A:** Busca de cliente por número de documento/CPF.
2. **Consulta B:** Busca de locações filtradas por intervalo de datas de retirada.
3. **Consulta C:** Filtro de veículos por categoria.

**Passos:**
1. Execute o `EXPLAIN` para as 3 consultas **antes** de criar os índices. Anote/evidencie a estratégia de busca utilizada pelo SGBD (ex: *Seq Scan* / *Full Table Scan*).
2. Crie um índice adequado para cada uma das 3 consultas.
3. Execute o `EXPLAIN` novamente **após** a criação dos índices e registre as mudanças no plano de execução e no custo estimado.

> ** Pergunta de Reflexão (incluir no relatório):**  
> Em que situações a presença de múltiplos índices pode prejudicar o desempenho do banco de dados (ex: tabelas com alta taxa de `INSERT`, `UPDATE` ou `DELETE`)?

---

## Parte 2 – Triggers, Procedures e Functions (30 min)

### Exercício 2.1: Automação e Auditoria com Triggers
1. **Trigger de Atualização de Status de Veículo:**
   * Crie um gatilho que altere automaticamente o status do veículo para `"locado"` ao inserir um novo registro na tabela de locações.
   * O mesmo gatilho (ou um segundo) deve alterar o status do veículo de volta para `"disponível"` quando a data real de devolução for preenchida em uma atualização.
2. **Trigger de Auditoria (`log_locacao`):**
   * Crie uma tabela de auditoria `log_locacao` com a estrutura mínima: `id_log`, `id_locacao`, `valor_antigo`, `valor_novo`, `status_antigo`, `status_novo`, `usuario` e `data_alteracao`.
   * Crie um trigger que registre uma linha nessa tabela toda vez que o valor total ou o status de uma locação for alterado via `UPDATE`.

---

### Exercício 2.2: Lógica de Negócio com Stored Procedures e Functions
1. **Procedure `sp_abrir_locacao`:**
   * Crie uma procedure (ou função armazenada) que receba os parâmetros: `<id_cliente>`, `<id_veiculo>`, `<id_filial>` e `<dias_locacao>`.
   * A procedure deve:
     1. Validar se o veículo está disponível. Se não estiver, disparar uma mensagem de erro/exceção.
     2. Buscar a taxa diária associada à categoria do veículo.
     3. Calcular o valor total e realizar o `INSERT` na tabela de locações.
2. **Function `fn_calcula_multa`:**
   * Crie uma função que receba o `<id_locacao>` e a `<taxa_diaria_multa>`.
   * Ela deve calcular a diferença de dias entre a data prevista de devolução e a data real de devolução.
   * Caso haja atraso, retornar o valor total da multa; caso contrário, retornar `0`.

---

## Parte 3 – Concorrência e Transações em Dupla (35 min)

> **Instrução de Ambiente:**  
> Abram dois terminais, abas ou conexões de banco de dados independentes.  
> * **Sessão A:** Aluno A  
> * **Sessão B:** Aluno B  

---

### Experimento 3.1: Bloqueio Explícito (`FOR UPDATE`)
Simulem a tentativa simultânea de reservar o mesmo veículo por dois usuários concorrentes:

1. **Sessão A (Aluno A):**
   ```sql
   BEGIN;
   SELECT * FROM <tabela_veiculo> WHERE <id_veiculo> = 1 FOR UPDATE;
   -- Mantenha a transação aberta (NÃO faça COMMIT ainda)
   ```
2. **Sessão B (Aluno B):**
   ```sql
   BEGIN;
   SELECT * FROM <tabela_veiculo> WHERE <id_veiculo> = 1 FOR UPDATE;
   -- Observe: A Sessão B ficará bloqueada (aguardando a liberação do lock).
   ```
3. **Sessão A (Aluno A):**
   ```sql
   COMMIT;
   -- Observe que a Sessão B é liberada imediatamente após o COMMIT.
   ```
4. **Sessão B (Aluno B):** Finalize a transação com `COMMIT;` ou `ROLLBACK;`.

---

### Experimento 3.2: Indução de Deadlock
Executem os comandos exatamente na ordem abaixo para forçar o SGBD a detectar um Deadlock:

| Passo | Sessão A (Aluno A) | Sessão B (Aluno B) |
| :---: | :--- | :--- |
| **1** | `BEGIN;` | — |
| **2** | `UPDATE <tabela_cliente> SET <nome> = 'Teste A' WHERE <id_cliente> = 1;` | — |
| **3** | — | `BEGIN;` |
| **4** | — | `UPDATE <tabela_veiculo> SET <modelo> = 'Teste B' WHERE <id_veiculo> = 1;` |
| **5** | `UPDATE <tabela_veiculo> SET <modelo> = 'Teste A' WHERE <id_veiculo> = 1;`<br>*(Fica aguardando Sessão B)* | — |
| **6** | — | `UPDATE <tabela_cliente> SET <nome> = 'Teste B' WHERE <id_cliente> = 1;`<br>**(PROVOCA DEADLOCK!)** |

> **📸 Registro Prático:**  
> Capturem o print ou copiem a mensagem oficial de erro de Deadlock retornada pelo SGBD. Expliquem no documento como uma ordem padronizada de acesso às tabelas evita essa situação.

---

### Experimento 3.3: Níveis de Isolamento e MVCC
Verifiquem o comportamento do versionamento de dados (*Multi-Version Concurrency Control*):

1. **Sessão A:** Inicie uma transação e altere um valor em uma locação ou cliente (`UPDATE`), **sem** dar `COMMIT`.
2. **Sessão B:** Em nível de isolamento padrão (`READ COMMITTED`), consulte o registro alterado pela Sessão A. Confirmem que a Sessão B enxerga a versão antiga (impedindo Leitura Suja).
3. **Sessão A:** Execute o `COMMIT;`.
4. **Sessão B:** Repita a consulta e observe a atualização do dado (Leitura Não Repetível).
5. **Teste com `REPEATABLE READ`:** Repitam o teste configurando a Sessão B com `SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;` e observem como o snapshot dos dados se mantém inalterado durante toda a transação da Sessão B.

---

## Entregáveis do Laboratório

A dupla deverá disponibilizar no repositório GitHub do grupo:

1. **`script_parte2.sql`**: Contendo todos os scripts de criação de Views, Índices, Triggers, Procedures e Functions.
2. **`relatorio_evidencias.pdf`**:
   * Prints ou logs do `EXPLAIN` antes e depois dos índices (Parte 1.2).
   * Resposta da pergunta de reflexão sobre degradação por excesso de índices (Parte 1.2).
   * Print da mensagem de Deadlock gerada pelo SGBD e explicação de prevenção (Parte 3.2).
   * Breve relato da experiência e divisão de tarefas entre os integrantes da dupla.
