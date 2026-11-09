# Atividade prática: lendo o plano de execução com EXPLAIN

**Duração:** 30 minutos
**Formato:** individual ou em duplas
**SGBD:** MySQL 8.0.18 ou superior (necessário para `EXPLAIN ANALYZE`)
**Tema:** locadora de carros, em um banco separado só para esta atividade

## Objetivo

Aplicar o que foi visto na aula: executar consultas sobre uma base com centenas de milhares de linhas, ler o plano com `EXPLAIN`, criar índices e verificar, pelo plano, se eles foram usados ou ignorados.
---

## Parte 0 — Preparação

Execute o script abaixo de uma só vez. Ele cria o banco `lab_otimizacao` com 50 mil clientes e 500 mil locações. **Só as chaves primárias existem**; os índices serão criados por vocês durante a atividade. A carga leva alguns segundos.

```sql
DROP DATABASE IF EXISTS lab_otimizacao;
CREATE DATABASE lab_otimizacao;
USE lab_otimizacao;

CREATE TABLE cliente (
  id     INT PRIMARY KEY,
  nome   VARCHAR(60) NOT NULL,
  cpf    VARCHAR(11) NOT NULL,
  cidade VARCHAR(30) NOT NULL
);

CREATE TABLE locacao (
  id             INT PRIMARY KEY,
  id_cliente     INT NOT NULL,
  id_veiculo     INT NOT NULL,
  data_retirada  DATE NOT NULL,
  valor          DECIMAL(8,2) NOT NULL,
  status         VARCHAR(10) NOT NULL
);

SET SESSION cte_max_recursion_depth = 1000000;

INSERT INTO cliente (id, nome, cpf, cidade)
WITH RECURSIVE seq AS (
  SELECT 1 AS n UNION ALL SELECT n + 1 FROM seq WHERE n < 50000
)
SELECT n,
       CONCAT('Cliente ', n),
       LPAD(n, 11, '0'),
       ELT(1 + n % 5, 'Brasilia', 'Goiania', 'Anapolis', 'Taguatinga', 'Gama')
FROM seq;

INSERT INTO locacao (id, id_cliente, id_veiculo, data_retirada, valor, status)
WITH RECURSIVE seq AS (
  SELECT 1 AS n UNION ALL SELECT n + 1 FROM seq WHERE n < 500000
)
SELECT n,
       1 + (n * 7919) % 50000,
       1 + (n * 31) % 200,
       DATE_ADD('2023-01-01', INTERVAL n % 1095 DAY),
       100 + n % 400,
       CASE WHEN n % 50 = 0 THEN 'cancelada'
            WHEN n % 4  = 0 THEN 'aberta'
            ELSE 'concluida' END
FROM seq;

ANALYZE TABLE cliente, locacao;
```

Confira a carga e os índices existentes:

```sql
SELECT (SELECT COUNT(*) FROM cliente) AS clientes,
       (SELECT COUNT(*) FROM locacao) AS locacoes;

SHOW INDEX FROM locacao;   -- deve aparecer apenas PRIMARY
```

---

## Parte 1 — Diagnóstico sem índices

Rode `EXPLAIN` nas duas consultas e preencha a tabela.

**Q1 — Locações de um cliente**

```sql
EXPLAIN SELECT * FROM locacao WHERE id_cliente = 4242;
```

**Q2 — Locações de um cliente, buscando pelo CPF**

```sql
EXPLAIN
SELECT c.nome, l.data_retirada, l.valor
FROM cliente c
JOIN locacao l ON l.id_cliente = c.id
WHERE c.cpf = '00000004242';
```

Agora meça o tempo real da Q1:

```sql
EXPLAIN ANALYZE SELECT * FROM locacao WHERE id_cliente = 4242;
```

**Registro (sem índices)**

| Consulta | Tabela | `type` | `key` | `rows` | Observações (`Extra`) |
|---|---|---|---|---|---|
| Q1 | locacao | | | | |
| Q2 | cliente | | | | |
| Q2 | locacao | | | | |

Tempo real da Q1 (`actual time` do `EXPLAIN ANALYZE`): ______ ms

**Pergunta:** por que o MySQL não teve alternativa a ler a tabela inteira?

---

## Parte 2 — Criando índices e comparando

Crie os índices que as consultas da Parte 1 pedem:

```sql
CREATE INDEX idx_loc_cliente ON locacao(id_cliente);
CREATE INDEX idx_cli_cpf     ON cliente(cpf);
ANALYZE TABLE cliente, locacao;
```

Rode de novo `EXPLAIN` para Q1 e Q2 e também o `EXPLAIN ANALYZE` da Q1.

**Registro (com índices)**

| Consulta | Tabela | `type` | `key` | `rows` |
|---|---|---|---|---|
| Q1 | locacao | | | |
| Q2 | cliente | | | |
| Q2 | locacao | | | |

Tempo real da Q1 agora: ______ ms

### Seletividade na prática

Crie um índice em uma coluna de poucos valores distintos e compare dois filtros:

```sql
CREATE INDEX idx_loc_status ON locacao(status);
ANALYZE TABLE locacao;

EXPLAIN SELECT * FROM locacao WHERE status = 'cancelada';
EXPLAIN SELECT * FROM locacao WHERE status = 'concluida';
```

| Filtro | Parcela aproximada da tabela | `type` | `key` |
|---|---|---|---|
| `status = 'cancelada'` | cerca de 2% | | |
| `status = 'concluida'` | cerca de 73% | | |

**Pergunta:** o índice `idx_loc_status` existe nos dois casos. Por que o resultado do plano é diferente?

---

## Parte 3 — Índices que o MySQL ignora

Crie mais dois índices e teste três consultas que **parecem** usar índice, mas não usam. Para cada uma, **reescreva a consulta** para que o índice seja aproveitado e confirme no `EXPLAIN`.

```sql
CREATE INDEX idx_loc_data ON locacao(data_retirada);
CREATE INDEX idx_cli_nome ON cliente(nome);
ANALYZE TABLE cliente, locacao;
```

### 3A — Função aplicada na coluna

```sql
EXPLAIN SELECT * FROM locacao
WHERE DATE_FORMAT(data_retirada, '%Y-%m') = '2025-06';
```

Reescreva usando uma faixa de datas e compare: ______________________________

### 3B — `LIKE` com `%` no início

```sql
EXPLAIN SELECT * FROM cliente WHERE nome LIKE '%123';
```

Reescreva para buscar clientes cujo nome **começa** com `Cliente 123`: ______________________________

### 3C — Conversão implícita de tipo

`cpf` é `VARCHAR`, mas a consulta abaixo compara com um número:

```sql
EXPLAIN SELECT * FROM cliente WHERE cpf = 4242;
```

Reescreva comparando com texto: ______________________________

**Registro**

| Caso | `type` antes | `type` depois | Por que o índice não era usado? |
|---|---|---|---|
| 3A | | | |
| 3B | | | |
| 3C | | | |

---

## Parte 4 — Índice composto

```sql
CREATE INDEX idx_loc_cli_data ON locacao(id_cliente, data_retirada);
ANALYZE TABLE locacao;

-- (a) filtra pelas duas colunas
EXPLAIN SELECT * FROM locacao
WHERE id_cliente = 4242 AND data_retirada >= '2025-01-01';

-- (b) filtra só pela segunda coluna do índice composto
EXPLAIN SELECT * FROM locacao
WHERE data_retirada >= '2025-06-01' AND data_retirada < '2025-07-01';
```

Na consulta (a), qual índice o MySQL escolheu (`key`)? ______________________

**Desafio (se der tempo):** torne invisível o índice simples de data e repita a consulta (b). O composto ajuda? Por quê?

```sql
ALTER TABLE locacao ALTER INDEX idx_loc_data INVISIBLE;
EXPLAIN SELECT * FROM locacao
WHERE data_retirada >= '2025-06-01' AND data_retirada < '2025-07-01';

-- volte ao normal
ALTER TABLE locacao ALTER INDEX idx_loc_data VISIBLE;
```

---

## Parte 5 — Fechamento

Responda em duas ou três linhas:

1. Qual consulta teve o maior ganho com o índice e como você percebeu isso no plano?
2. Cite um caso em que existia índice e ele **não** foi usado, e a razão.
3. Que custo todos esses índices trazem para as operações de escrita (`INSERT`, `UPDATE`, `DELETE`)?