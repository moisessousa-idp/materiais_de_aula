# Laboratório – Locadora v2 (Parte 02)

**Duração:** 2h | **Formato:** duplas | **Stack:** PHP + MySQL (PDO)
**Projeto:** continuação do Laboratório – Locadora v2 (Parte 01)

## Objetivo

Evoluir a locadora aplicando os temas das Aulas 29 a 33: **migrations** para versionar o esquema (Aula 30), **otimização de consultas** com índices e `EXPLAIN` (Aula 29) e **modelagem dimensional e painéis de BI** (Aula 33).

## Regras

- Pré-requisito: Parte 01 concluída (MVC, soft delete, usuários `app_locadora` e `admin_locadora`, login).
- Trabalhem em dupla, alternando quem digita a cada etapa.
- Ao terminar cada etapa, confirmem o **checklist** antes de avançar.
- **Nunca** trabalhem no banco `locadora` original: toda a Parte 02 roda em uma cópia, `locadora_lab`.
- Adaptem os nomes ao esquema de vocês. Os exemplos assumem: `locacoes(id, cliente_id, carro_id, data_retirada, data_devolucao, valor, status)`, `clientes(id, nome, cpf, cidade)` e `carros(id, placa, modelo, cor, deleted_at)`. Se faltar algum campo (ex.: `cidade`), anotem como **lacuna do modelo**.
- Se o tempo apertar, priorizem as etapas 2 e 3. Na etapa 1, façam o runner e o expandir/contrair de forma reduzida (sem o backfill em lotes).

## Como esta parte conversa com a Parte 01

| Parte 01 | Aparece aqui como |
|---|---|
| Backup e restauração (Aula 22) | Cópia `locadora_lab` antes de mexer; o passo “contrair” só é reversível com backup |
| Soft delete (`deleted_at`) | O backfill precisa tratar carros “excluídos”; o ETL precisa decidir o que fazer com eles |
| Privilégios (Aula 24) | `app_locadora` **não** pode alterar esquema: migrations e ETL usam o usuário administrativo |
| Prepared statements (Aula 23) | `LIKE '%termo%'` seguro continua sendo lento: vejam no `EXPLAIN` |
| Login e perfil (Aula 25) | Desafio final: painel protegido por login e perfil `admin` |

## Cronograma sugerido

| Tempo | Etapa | Tema |
|---|---|---|
| 0–10 min | 0 | Preparação e carga de volume |
| 10–45 min | 1 | Migrations (Aula 30) |
| 45–75 min | 2 | Otimização de consultas (Aula 29) |
| 75–115 min | 3 | Modelo dimensional e painéis (Aula 33) |
| 115–120 min | 4 | Entrega |

---

## Etapa 0 – Preparação (10 min)

**1. Cópia do banco**

```bash
mysqldump -u root -p locadora > locadora_backup_parte02.sql
mysql -u root -p -e "CREATE DATABASE locadora_lab CHARACTER SET utf8mb4"
mysql -u root -p locadora_lab < locadora_backup_parte02.sql
```

**2. Privilégios na cópia**

```sql
GRANT SELECT, INSERT, UPDATE ON locadora_lab.* TO 'app_locadora'@'localhost';
GRANT ALL PRIVILEGES ON locadora_lab.* TO 'admin_locadora'@'localhost';
FLUSH PRIVILEGES;
```

**3. Configuração.** Em `config/config.php`, aponte `DB_NAME` para `locadora_lab` e acrescente as credenciais usadas só por scripts de linha de comando:

```php
define('MIG_USER', 'admin_locadora');
define('MIG_PASS', 'troque_esta_senha_admin');
```

**4. Novas pastas** (fora de `public/`):

```
locadora/
├── migrations/
│   ├── 001_baseline.sql
│   └── ...
└── scripts/
    ├── migrate.php
    ├── backfill_cor.php
    ├── gerar_carga.sql
    └── etl_dw.sql
```

**5. Carga de volume.** Com poucos registros, o `EXPLAIN` não mostra diferença. Como cada grupo tem o seu próprio banco, **cada dupla gera a sua carga de teste** em `locadora_lab`: podem e devem usar IA para isso. Passem à IA o `SHOW CREATE TABLE` de `clientes`, `carros` e `locacoes` e peçam um script que cumpra os requisitos abaixo.

- cerca de **10 mil clientes** e **200 mil locações**, usando clientes e carros já existentes, sem violar chaves estrangeiras;
- nomes de clientes no formato `Cliente teste <n>` e CPFs únicos de 11 dígitos;
- datas de retirada entre 2023-01-01 e 2025-12-30 (cobrindo junho de 2025), com devolução de 1 a 7 dias depois;
- valores entre 100 e 499;
- `status` variado: cerca de 2% canceladas, 25% abertas e 73% concluídas;
- clientes distribuídos em pelo menos 5 cidades;
- inserção em lote ou com CTE recursiva, para rodar em segundos.

Salvem o script em `scripts/gerar_carga.sql` (ou no formato que a IA gerar). **Revisem o script antes de rodar** (nada de `DROP` ou `DELETE` inesperado) e executem uma vez com `admin_locadora`. Se o padrão de dados de vocês for outro, ajustem os valores das consultas da Etapa 2.

> Esta carga **não** é migration: são dados de teste, não mudança de esquema. Ela nunca rodaria em produção.

**Checklist**

- [ ] O sistema abre no navegador usando `locadora_lab` e `app_locadora`.
- [ ] `SELECT COUNT(*) FROM locacoes;` retorna mais de 200 mil.
- [ ] O MySQL é 8.0.18 ou superior (`SELECT VERSION();`), necessário para `EXPLAIN ANALYZE`.

---

## Etapa 1 – Migrations (Aula 30) – 35 min

### Parte A – O runner (10 min)

Copiem o `migrate.php` da Aula 30 para `scripts/migrate.php` com **três mudanças**:

```php
<?php
// 1) só roda pela linha de comando, nunca pelo navegador
if (PHP_SAPI !== 'cli') { exit('Somente linha de comando.'); }

// 2) lê a configuração central e usa o usuário administrativo
require_once __DIR__ . '/../config/config.php';
$pdo = new PDO(
    'mysql:host=' . DB_HOST . ';dbname=' . DB_NAME . ';charset=utf8mb4',
    MIG_USER,
    MIG_PASS,
    [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]
);

// 3) as migrations ficam em ../migrations/ (ajustem os dois glob/caminhos)
// ... restante igual ao runner da Aula 30 (up, down, schema_migrations)
```

Crie `migrations/001_baseline.sql` (`SELECT 1;` em `up` e em `down`), rode `php scripts/migrate.php up` e confira `SELECT * FROM schema_migrations;`.

### Parte B – Expandir e contrair em Carros (25 min)

Cenário: a coluna `carros.cor` precisa virar `cor_externa`, **sem derrubar o sistema**. Se a coluna não existir no seu esquema, use outra coluna de texto de `carros`.

**Passo 1 – Expandir.** `migrations/002_add_cor_externa.sql`:

```sql
-- 002_add_cor_externa.sql
-- up
ALTER TABLE carros ADD COLUMN cor_externa VARCHAR(30) NULL;

-- down
ALTER TABLE carros DROP COLUMN cor_externa;
```

Aplique com `up`. Teste também `down` e `up` de novo.

**Passo 2 – Migrar os dados em lotes.** `scripts/backfill_cor.php`:

```php
<?php
require_once __DIR__ . '/../config/config.php';
$pdo = new PDO(
    'mysql:host=' . DB_HOST . ';dbname=' . DB_NAME . ';charset=utf8mb4',
    MIG_USER,
    MIG_PASS,
    [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]
);

do {
    // sem filtro em deleted_at: carros "excluídos" também precisam migrar
    $afetadas = $pdo->exec(
        'UPDATE carros SET cor_externa = cor
          WHERE cor_externa IS NULL AND cor IS NOT NULL
          LIMIT 1000'
    );
    echo 'Lote: ' . $afetadas . ' linhas' . PHP_EOL;
    usleep(200000);
} while ($afetadas > 0);
```

Checkpoint: `SELECT COUNT(*) FROM carros WHERE cor_externa IS NULL AND cor IS NOT NULL;` deve dar 0, **contando os carros com `deleted_at` preenchido**.

**Passo 3 – Trocar o código.** No `CarroModel`, nesta ordem:

1. `INSERT` e `UPDATE` gravam **nos dois campos** (`cor` e `cor_externa`);
2. `SELECT`, listagens e formulários passam a ler **só** `cor_externa`;
3. Testem listar, criar, editar e excluir carros pelo navegador.

**Passo 4 – Contrair.** Só depois de o código novo funcionar, crie `migrations/003_drop_cor.sql` (`up`: `ALTER TABLE carros DROP COLUMN cor;`, `down`: `ALTER TABLE carros ADD COLUMN cor VARCHAR(30) NULL;`) e aplique.

### Perguntas (respondam em `respostas.md`)

1. **Privilégio.** Por que o runner usa `MIG_USER` e não `app_locadora`? Com `app_locadora` no cliente `mysql`, tentem um `ALTER TABLE carros ADD COLUMN x INT;` e anotem a mensagem de erro.
2. **NOT NULL.** A coluna da `002` nasceu `NULL`. O que aconteceria com o código que ainda não conhece `cor_externa` se ela fosse `NOT NULL` sem valor padrão?
3. **Soft delete.** Por que o backfill não filtra `deleted_at IS NULL`? O que o usuário veria ao restaurar um carro que ficou de fora?
4. **Irreversível.** Rodem `down` logo após a `003`. A coluna `cor` volta, mas os dados voltam? O que o `down` não consegue desfazer e o que vocês usariam para recuperar (dica: Parte 01, Etapa 3)? Depois, expliquem por que, ao descobrir que `cor_externa` deveria ter 40 caracteres, **não se edita a `002`** e qual migration se cria.

**Checklist**

- [ ] `schema_migrations` lista `001`, `002` e `003`.
- [ ] `migrate.php` só roda pela linha de comando; a aplicação continua usando `app_locadora`.
- [ ] Nenhum carro, inclusive os excluídos, ficou sem `cor_externa`.
- [ ] O CRUD de Carros funcionou antes e depois do contrair.
- [ ] Nenhuma migration foi editada depois de aplicada.

---

## Etapa 2 – Otimização de consultas (Aula 29) – 30 min

### Parte A – Diagnóstico (8 min)

```sql
SHOW INDEX FROM locacoes;
```

Anotem os índices existentes. Atenção: **chaves estrangeiras criam índice automaticamente** no InnoDB, então `cliente_id` e `carro_id` podem já estar indexados.

Rodem `EXPLAIN` nas quatro consultas (ajustem o `cliente_id` para um que exista):

```sql
-- Q1: faixa de datas
EXPLAIN SELECT * FROM locacoes
WHERE data_retirada >= '2025-06-01' AND data_retirada < '2025-07-01';

-- Q2: mesma pergunta, com função na coluna
EXPLAIN SELECT * FROM locacoes
WHERE DATE_FORMAT(data_retirada, '%Y-%m') = '2025-06';

-- Q3: nome terminando em...
EXPLAIN SELECT * FROM clientes WHERE nome LIKE '%123';

-- Q4: cliente + data
EXPLAIN SELECT * FROM locacoes
WHERE cliente_id = 4242 AND data_retirada >= '2025-01-01';
```

Meçam o tempo real da Q1 com `EXPLAIN ANALYZE` e preencham as colunas “antes” da tabela de registro (mais abaixo).

### Parte B – Índices por migration (10 min)

Índice é mudança de esquema, então **entra como migration**:

```sql
-- 004_idx_locacoes_data.sql
-- up
CREATE INDEX idx_loc_data ON locacoes(data_retirada);

-- down
DROP INDEX idx_loc_data ON locacoes;
```

Criem no mesmo padrão:

- `005_idx_clientes_nome.sql`: índice em `clientes(nome)`;
- `006_idx_locacoes_cliente_data.sql`: índice composto em `locacoes(cliente_id, data_retirada)`.

Aplique com `up`, rode `ANALYZE TABLE clientes, locacoes;` e repita o `EXPLAIN` das quatro consultas.

### Parte C – Índices que o MySQL ignora (8 min)

Com os índices criados, Q2 e Q3 continuam ruins. Reescrevam e confirmem no plano:

- **Q2 → faixa de datas** (já é a Q1: comparem as duas).
- **Q3 → prefixo:** `nome LIKE 'Cliente teste 123%'`.
- **Q5 (conversão implícita):** `cpf` é texto. Comparem `WHERE cpf = 4242` com `WHERE cpf = '00000004242'` (precisa de índice em `cpf`; se ainda não houver, criem outra migration `007_idx_clientes_cpf`, e a numeração do BI sobe uma casa).

**Registro**

| Consulta | `type` antes | `key` antes | `rows` antes | `type` depois | `key` depois | `rows` depois |
|---|---|---|---|---|---|---|
| Q1 | | | | | | |
| Q2 | | | | | | |
| Q3 | | | | | | |
| Q4 | | | | | | |

Tempo real da Q1: antes ______ ms | depois ______ ms

### Perguntas (em `respostas.md`)

1. Qual consulta teve o maior ganho e como vocês perceberam isso no plano (`type`, `key`, `rows`)?
2. Cite um caso em que o índice existia e **não** foi usado, e a razão. Como isso se relaciona com a busca `LIKE '%modelo%'` da Etapa 4 da Parte 01?
3. **Seletividade.** Em `locacoes`, `status` tem poucos valores (cerca de 2% canceladas, 25% abertas, 73% concluídas). Em qual filtro um índice só em `status` valeria a pena? E um índice só em `carros.deleted_at`, usado em toda listagem?
4. **Custo.** Que custo esses índices trazem para `INSERT`, `UPDATE` e `DELETE`? E por que `app_locadora` não consegue criar um índice?

**Checklist**

- [ ] Existe uma migration para cada índice criado, com `down` que o remove.
- [ ] A tabela de registro está preenchida, com `type`, `key` e `rows` antes e depois.
- [ ] Pelo menos um caso de índice ignorado foi reescrito e confirmado no `EXPLAIN`.

---

## Etapa 3 – Modelo dimensional e painéis (Aula 33) – 40 min

A direção da locadora quer acompanhar a operação por painéis. O sistema é **OLTP**; para alimentar os painéis, vocês vão construir um **modelo estrela** de verdade, no mesmo banco, e testar as consultas.

### Painéis

| # | Painel | Tipo |
|---|---|---|
| 1 | **Modelos de carro mais alugados** | Ranking |
| 2 | **Locações por mês** | Evolução |
| 3 | **Faturamento** (total e ticket médio) | Quanto? |
| 4 | **Cidade com mais locações** (ou filial, se existir) | Ranking / participação |
| 5 | **Painel livre**, escolhido pela dupla | A critério da dupla |

### Parte A – Modelo estrela no papel (10 min)

Registrem no `LEIAME.md`:

- O **grão:** “Uma linha do fato representa...” (sugestão: uma locação).
- As **medidas** e se são aditivas, semiaditivas ou não aditivas.
- As **dimensões** e seus atributos (inclua tempo).
- As **decisões de modelagem**: locações *canceladas* entram no faturamento? Carros *excluídos* (soft delete) continuam na dimensão? Locação aberta, sem devolução, tem quantos dias?

**Pergunta:** uma única tabela fato atende aos cinco painéis? Justifiquem.

### Parte B – Criar o esquema dimensional por migrations (10 min)

Uma migration por tabela, respeitando a limitação de uma instrução por seção. Modelo da `dim_tempo`:

```sql
-- 008_dim_tempo.sql
-- up
CREATE TABLE dim_tempo (
  sk_tempo   INT PRIMARY KEY,          -- AAAAMMDD
  data       DATE NOT NULL,
  ano        SMALLINT NOT NULL,
  mes        TINYINT NOT NULL,
  nome_mes   VARCHAR(15) NOT NULL,
  ano_mes    CHAR(7) NOT NULL,
  dia_semana VARCHAR(15) NOT NULL
);

-- down
DROP TABLE dim_tempo;
```

Criem as outras três, na ordem (o `down` de cada uma desfaz só a própria tabela):

- `009_dim_carro.sql`: `sk_carro INT AUTO_INCREMENT PRIMARY KEY`, `id_origem INT NOT NULL UNIQUE`, `placa`, `modelo`, `ativo TINYINT(1) NOT NULL`.
- `010_dim_cliente.sql`: `sk_cliente INT AUTO_INCREMENT PRIMARY KEY`, `id_origem INT NOT NULL UNIQUE`, `nome`, `cidade`.
- `011_fato_locacao.sql`: `id_locacao INT PRIMARY KEY`, `sk_tempo`, `sk_carro`, `sk_cliente` (cada um com `FOREIGN KEY` para a sua dimensão), `status VARCHAR(10)`, `dias INT`, `valor DECIMAL(10,2)`.

> A numeração parte da `008` supondo que a `007` foi usada no índice de `cpf`. Se não foi, comecem da `007`.

### Parte C – ETL (10 min)

Salvem como `scripts/etl_dw.sql` e rodem com `mysql -u admin_locadora -p locadora_lab < scripts/etl_dw.sql`. **Dimensões antes do fato.**

```sql
USE locadora_lab;
SET SESSION cte_max_recursion_depth = 5000;

-- dimensão tempo: um registro por dia
INSERT IGNORE INTO dim_tempo (sk_tempo, data, ano, mes, nome_mes, ano_mes, dia_semana)
WITH RECURSIVE dias AS (
  SELECT DATE('2020-01-01') AS d
  UNION ALL SELECT d + INTERVAL 1 DAY FROM dias WHERE d < '2027-12-31'
)
SELECT DATE_FORMAT(d, '%Y%m%d'), d, YEAR(d), MONTH(d),
       ELT(MONTH(d), 'Janeiro','Fevereiro','Marco','Abril','Maio','Junho',
                     'Julho','Agosto','Setembro','Outubro','Novembro','Dezembro'),
       DATE_FORMAT(d, '%Y-%m'),
       ELT(WEEKDAY(d) + 1, 'Segunda','Terca','Quarta','Quinta','Sexta','Sabado','Domingo')
FROM dias;

-- dimensão carro (inclui os excluídos, marcados como inativos)
INSERT INTO dim_carro (id_origem, placa, modelo, ativo)
SELECT id, placa, modelo, deleted_at IS NULL FROM carros
ON DUPLICATE KEY UPDATE placa = VALUES(placa), modelo = VALUES(modelo), ativo = VALUES(ativo);

-- dimensão cliente
INSERT INTO dim_cliente (id_origem, nome, cidade)
SELECT id, nome, cidade FROM clientes
ON DUPLICATE KEY UPDATE nome = VALUES(nome), cidade = VALUES(cidade);

-- fato: recarga completa
DELETE FROM fato_locacao;
INSERT INTO fato_locacao (id_locacao, sk_tempo, sk_carro, sk_cliente, status, dias, valor)
SELECT l.id,
       DATE_FORMAT(l.data_retirada, '%Y%m%d'),
       dc.sk_carro,
       dcl.sk_cliente,
       l.status,
       GREATEST(COALESCE(DATEDIFF(l.data_devolucao, l.data_retirada), 1), 1),
       l.valor
FROM locacoes l
JOIN dim_carro dc    ON dc.id_origem  = l.carro_id
JOIN dim_cliente dcl ON dcl.id_origem = l.cliente_id;
```

Confiram: `SELECT COUNT(*) FROM fato_locacao;` deve bater com `locacoes`. **Pergunta:** o que acontece se o ETL rodar duas vezes? E se uma locação for de uma data fora do intervalo da `dim_tempo`?

### Parte D – Consultas e fichas dos painéis (10 min)

Todas partem da **fato** e usam só as dimensões necessárias. Exemplo completo, painel 2:

```sql
SELECT t.ano_mes, COUNT(*) AS locacoes, SUM(f.valor) AS faturamento
FROM fato_locacao f
JOIN dim_tempo t ON t.sk_tempo = f.sk_tempo
WHERE f.status <> 'cancelada'
GROUP BY t.ano_mes
ORDER BY t.ano_mes;
```

Escrevam e rodem as consultas dos painéis 1, 3 e 4 (o 5 é livre). Para **cada** painel, preencham:

```
PAINEL: ______________________________
Pergunta de negócio:   ______________________________
Indicador (medida):    ______________________________
Dimensões usadas:      ______________________________
O que vai no GROUP BY: ______________________________
O que vai no WHERE:    ______________________________
Gráfico sugerido:      ______________________________
Operação OLAP:         ( ) roll up  ( ) drill down  ( ) slice  ( ) dice  ( ) pivot
```

Por fim, rodem `EXPLAIN` em uma consulta de painel e anotem se a fato usa os índices criados pelas chaves estrangeiras (volta da Etapa 2).

### Desafio (se sobrar tempo): painel dentro do sistema

Crie um usuário do SGBD só de leitura para o BI e uma rota `/painel` protegida:

```sql
CREATE USER 'bi_locadora'@'localhost' IDENTIFIED BY 'troque_esta_senha_bi';
GRANT SELECT ON locadora_lab.dim_tempo    TO 'bi_locadora'@'localhost';
GRANT SELECT ON locadora_lab.dim_carro    TO 'bi_locadora'@'localhost';
GRANT SELECT ON locadora_lab.dim_cliente  TO 'bi_locadora'@'localhost';
GRANT SELECT ON locadora_lab.fato_locacao TO 'bi_locadora'@'localhost';
FLUSH PRIVILEGES;
```

A rota exige login (`exigirLogin()`) e perfil `admin`, usa uma conexão `getConnectionBI()` com `bi_locadora`, escapa toda saída com `htmlspecialchars` e mostra a tabela do painel 2.

**Checklist**

- [ ] O grão da fato está escrito em uma frase.
- [ ] As quatro migrations do esquema dimensional têm `up` e `down`.
- [ ] O ETL carrega as dimensões antes da fato e o total da fato bate com `locacoes`.
- [ ] Todo atributo do `SELECT` sem agregação está no `GROUP BY`.
- [ ] Rankings usam `ORDER BY ... DESC` e `LIMIT`.
- [ ] Decisões sobre canceladas e carros excluídos estão registradas no `LEIAME.md`.
- [ ] Cada painel tem sua ficha e sua consulta executada.

---

## Etapa 4 – Entrega (5 min)

Entreguem a pasta compactada (ou o link do repositório) com:

- código do sistema atualizado;
- `scripts/` (`migrate.php`, `backfill_cor.php`, `gerar_carga.sql`, `etl_dw.sql`);
- `migrations/` completa, com `up` e `down` em todas;
- captura ou texto da tabela `schema_migrations` após aplicar tudo;
- `respostas.md` com as perguntas das etapas 1 e 2 e a pergunta da etapa 3;
- `LEIAME.md` atualizado com: nomes da dupla, o que foi feito em cada etapa, a **tabela de registro do `EXPLAIN` (antes e depois)**, o **modelo estrela** (grão, medidas, dimensões, decisões de modelagem), as consultas dos painéis e os `GRANT` novos, se usaram o desafio.

---
