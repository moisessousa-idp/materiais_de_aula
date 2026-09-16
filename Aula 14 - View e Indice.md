# Aula Prática — Views e Índices no Projeto Aeroporto

**Contexto:** cada aluno modelou o próprio banco de dados do projeto aeroporto, então não há um schema único para todo mundo seguir. Em vez de um exercício com SQL pronto, esta aula prática é uma **metodologia**: cada aluno aplica os mesmos passos ao seu próprio banco, e a correção acontece comparando abordagens diferentes para o mesmo tipo de problema.

**Objetivo da aula:** ao final, cada aluno terá (1) proposto pelo menos duas views para o seu banco e (2) testado pelo menos um índice, comprovando com dados reais se ele ajudou ou não.

---

## Roteiro sugerido

| Etapa | Descrição | Tempo |
|---|---|---|
| 1 | Diagnóstico do próprio schema | 10 min |
| 2 | Propor views recomendadas | 15 min |
| 3 | Testar índices e medir com `performance_schema` | 20 min |
| 4 | Registro de resultados | 10 min |
| 5 | Compartilhamento com a turma | 5 min |

---

## Etapa 1 — Diagnóstico do próprio schema (10 min)

Antes de propor qualquer view ou índice, cada aluno responde, sobre o **seu próprio** banco:

- Quais são as tabelas principais e como elas se relacionam? (fazer um esboço rápido, mesmo que só no papel)
- Quais consultas eu já escrevi mais de uma vez neste projeto? (esse é o primeiro candidato a virar view)
- Quais colunas eu mais uso em `WHERE`, `JOIN` ou `ORDER BY`? (esses são os primeiros candidatos a índice)

> Instrução em sala: peça para cada aluno listar de 3 a 5 consultas reais que ele já rodou no projeto (do histórico do terminal, de um arquivo `.sql`, ou de memória mesmo). É a partir dessa lista que as próximas etapas vão funcionar.

---

## Etapa 2 — Propor views recomendadas (15 min)

Cada aluno preenche este checklist para decidir **se** e **que tipo** de view faz sentido para cada consulta candidata da Etapa 1.

### Checklist de decisão

- [ ] Essa consulta combina duas ou mais tabelas com frequência? → candidata a **view com JOIN**
- [ ] Essa consulta calcula totais, médias ou contagens para um relatório/painel? → candidata a **view com agregação**
- [ ] Essa consulta filtra sempre pelas mesmas condições (ex.: só voos ativos, só passageiros confirmados)? → candidata a **view simples**, possivelmente **atualizável**
- [ ] Essa view vai receber `INSERT`/`UPDATE` através dela? → considerar `WITH CHECK OPTION`
- [ ] Essa consulta é pesada e repetida com muita frequência, podendo tolerar dados com um pequeno atraso? → candidata a **view materializada** (ou tabela + rotina de atualização, já que MySQL não tem suporte nativo)

### Formulário de proposta de view

Cada aluno preenche isso para **pelo menos duas** views propostas:

```
Nome da view: 
Tabelas de origem: 
Tipo (simples / JOIN / agregação): 
É atualizável? (sim/não, por quê): 
Problema que ela resolve: 
Esboço do SELECT:
```

---

## Etapa 3 — Testar índices e medir com `performance_schema` (20 min)

Aqui é onde a aula fica prática de verdade: em vez de "criar índice porque a teoria manda", o aluno **mede antes, cria, mede depois** e só então decide se valeu a pena.

### Passo a passo

**1. Escolher uma consulta candidata** (da lista da Etapa 1) que filtre por uma coluna sem índice.

**2. Confirmar que o `performance_schema` está ativo:**

```sql
SHOW VARIABLES LIKE 'performance_schema';
-- deve retornar ON. Se estiver OFF, avisar o professor (precisa mudar no my.cnf).
```

**3. Medir o "antes" com EXPLAIN:**

```sql
EXPLAIN SELECT * FROM voos WHERE status = 'atrasado';
```

Anotar as colunas `type` e `rows`.

**4. Medir o "antes" com dados reais de execução**, usando a tabela de resumo por consulta do `performance_schema`:

```sql
-- Limpa o histórico de estatísticas para começar do zero
TRUNCATE TABLE performance_schema.events_statements_summary_by_digest;

-- Roda a consulta candidata algumas vezes (simula uso real)
SELECT * FROM voos WHERE status = 'atrasado';
SELECT * FROM voos WHERE status = 'atrasado';
SELECT * FROM voos WHERE status = 'atrasado';

-- Consulta o resumo: tempo médio e linhas examinadas
SELECT
    DIGEST_TEXT,
    COUNT_STAR                AS execucoes,
    AVG_TIMER_WAIT/1000000000 AS tempo_medio_ms,
    SUM_ROWS_EXAMINED         AS linhas_examinadas_total
FROM performance_schema.events_statements_summary_by_digest
WHERE DIGEST_TEXT LIKE '%voos%'
ORDER BY AVG_TIMER_WAIT DESC;
```

**5. Criar o índice candidato:**

```sql
CREATE INDEX idx_voos_status ON voos(status);
```

**6. Repetir os passos 3 e 4** (incluindo o `TRUNCATE` antes de rodar de novo) e comparar:

- `type` no EXPLAIN mudou de `ALL` para `ref`/`range`?
- `rows` examinadas caiu?
- `tempo_medio_ms` e `linhas_examinadas_total` no `performance_schema` caíram?

**7. Checar se o índice está realmente sendo usado** (não só existindo):

```sql
SELECT
    OBJECT_NAME       AS tabela,
    INDEX_NAME        AS indice,
    COUNT_READ         AS leituras,
    COUNT_FETCH         AS buscas
FROM performance_schema.table_io_waits_summary_by_index_usage
WHERE OBJECT_NAME = 'voos'
ORDER BY COUNT_READ DESC;
```

Se o índice novo aparece com contagem de leitura crescendo à medida que a consulta roda, ele está em uso de fato.

> **Dica para quando não houver ganho:** se a tabela do aluno tiver poucas linhas (comum em projetos individuais ainda em construção), é esperado que o índice não mude quase nada — o otimizador pode até ignorar o índice e preferir a varredura completa. Isso não é um erro: é o próprio conceito de "evite índices em tabelas pequenas" se confirmando com dados reais.

### Testando mais de um índice

Incentivar quem tiver tempo a repetir o processo com:
- Um índice em coluna diferente
- Um índice composto (duas colunas do mesmo `WHERE`)
- Um índice em coluna que **não** costuma usar (para ver o caso onde não há ganho nenhum)

---

## Etapa 4 — Registro de resultados (10 min)

Cada aluno preenche esta tabela para pelo menos um índice testado:

| Consulta testada | `type` antes | `rows` antes | tempo médio antes (ms) | `type` depois | `rows` depois | tempo médio depois (ms) | Conclusão |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

**Conclusão** deve responder: o índice ajudou? Por quê (ou por que não)? Vale a pena manter esse índice considerando o custo em `INSERT`/`UPDATE`?

---

## Etapa 5 — Compartilhamento com a turma (5 min)

Como cada projeto é diferente, o valor está em ouvir abordagens variadas. Cada aluno compartilha rapidamente:

- Uma view que propôs e por quê
- Um resultado de índice (melhora, piora ou neutro) e o que isso ensinou

---

## O que entregar

- Formulário de proposta de view preenchido (mínimo 2 views)
- Tabela de registro de resultados preenchida (mínimo 1 índice testado)
- O(s) `CREATE VIEW` e `CREATE INDEX` efetivamente aplicados no banco de cada um

---

## Referência rápida — tabelas do `performance_schema` usadas hoje

| Tabela | Para que serve |
|---|---|
| `events_statements_summary_by_digest` | Tempo médio e linhas examinadas por padrão de consulta — o principal termômetro de "antes x depois" |
| `table_io_waits_summary_by_index_usage` | Mostra se um índice específico está sendo lido de fato, não só existindo |

Comando útil para verificar se o `performance_schema` está coletando dados de todas as consultas (alguns servidores vêm com instrumentação parcial):

```sql
SHOW VARIABLES LIKE 'performance_schema%';
```
