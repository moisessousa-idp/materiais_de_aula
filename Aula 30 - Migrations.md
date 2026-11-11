# Atividade prática: migrations no projeto do aeroporto

**Disciplina:** Banco de Dados
**Tema:** Versionamento de esquema, migrations e mudança segura em produção
**Duração sugerida:** 60 minutos (laboratório) ou tarefa para casa
**Formato:** individual ou em duplas
**Projeto:** o sistema do aeroporto (PHP + MySQL) que vocês vêm construindo

---

## Objetivo

Versionar as mudanças do banco do projeto do aeroporto com migrations e praticar o padrão **expandir e contrair** para alterar uma coluna sem derrubar o sistema.

Ao final, você deve ser capaz de:

- escrever uma migration com `up` e `down`;
- aplicar e desfazer migrations com um runner simples e uma tabela de controle;
- renomear uma coluna em passos pequenos e compatíveis com o código em produção;
- explicar o que muda quando o banco tem réplicas.

---

## Antes de começar: trabalhe em uma cópia

Nunca teste migrations no banco que você usa para o projeto. Crie uma cópia:

```bash
mysqldump -u root -p aeroporto > aeroporto_backup.sql
mysql -u root -p -e "CREATE DATABASE aeroporto_lab CHARACTER SET utf8mb4"
mysql -u root -p aeroporto_lab < aeroporto_backup.sql
```

Todas as etapas abaixo usam o banco `aeroporto_lab`.

---

## Estrutura de pastas

Dentro do projeto, crie:

```
projeto-aeroporto/
├── migrate.php
└── migrations/
    ├── 001_baseline.sql
    ├── 002_add_portao_embarque.sql
    ├── 003_add_aeroporto_origem.sql
    └── 004_drop_origem.sql
```

O número no início do nome define a ordem de aplicação.

---

## Parte 1: o runner de migrations (15 min)

Crie o arquivo `migrate.php`. Ele faz o que ferramentas como Flyway ou Phinx fazem, em versão mínima.

```php
<?php
// Uso: php migrate.php up    (aplica as pendentes)
//      php migrate.php down  (desfaz a última aplicada)

$pdo = new PDO(
    'mysql:host=localhost;dbname=aeroporto_lab;charset=utf8mb4',
    'root',
    '',
    [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]
);

$pdo->exec("CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(100) PRIMARY KEY,
    aplicada_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
)");

// Separa o arquivo em duas partes: antes e depois da linha "-- down"
function separar(string $sql): array {
    $partes = preg_split('/^-- down\s*$/m', $sql);
    return [trim($partes[0]), trim($partes[1] ?? '')];
}

$comando = $argv[1] ?? 'up';

if ($comando === 'up') {
    $aplicadas = $pdo->query("SELECT version FROM schema_migrations")
                     ->fetchAll(PDO::FETCH_COLUMN);
    $arquivos = glob(__DIR__ . '/migrations/*.sql');
    sort($arquivos);

    foreach ($arquivos as $arquivo) {
        $versao = basename($arquivo, '.sql');
        if (in_array($versao, $aplicadas)) {
            continue;
        }
        [$up] = separar(file_get_contents($arquivo));
        $pdo->exec($up);
        $pdo->prepare("INSERT INTO schema_migrations (version) VALUES (?)")
            ->execute([$versao]);
        echo "Aplicada: $versao\n";
    }
} elseif ($comando === 'down') {
    $ultima = $pdo->query(
        "SELECT version FROM schema_migrations ORDER BY version DESC LIMIT 1"
    )->fetchColumn();

    if (!$ultima) {
        echo "Nada a desfazer.\n";
        exit;
    }
    [, $down] = separar(file_get_contents(__DIR__ . "/migrations/$ultima.sql"));
    $pdo->exec($down);
    $pdo->prepare("DELETE FROM schema_migrations WHERE version = ?")
        ->execute([$ultima]);
    echo "Desfeita: $ultima\n";
}
```

**Limitações desta versão (propositais):**

- cada seção (`up` e `down`) deve ter **uma única instrução SQL**;
- no MySQL, `ALTER TABLE` faz commit implícito, então não existe rollback automático se algo falhar no meio.

Crie a migration `001_baseline.sql`, que só marca o ponto de partida do banco:

```sql
-- 001_baseline.sql
-- up
SELECT 1;

-- down
SELECT 1;
```

Rode `php migrate.php up` e confira:

```sql
SELECT * FROM schema_migrations;
```

**Checkpoint:** a tabela deve ter uma linha, `001_baseline`.

---

## Parte 2: sua primeira migration real (10 min)

Crie `migrations/002_add_portao_embarque.sql`:

```sql
-- 002_add_portao_embarque.sql
-- up
ALTER TABLE voos ADD COLUMN portao_embarque VARCHAR(5) NULL;

-- down
ALTER TABLE voos DROP COLUMN portao_embarque;
```

Tarefas:

1. Aplique com `php migrate.php up`.
2. Confira com `DESCRIBE voos;` que a coluna existe.
3. Desfaça com `php migrate.php down` e confira que ela sumiu.
4. Aplique de novo.

**Pergunta 1.** A coluna foi criada como `NULL`. O que aconteceria com o código do projeto, que ainda não conhece `portao_embarque`, se ela fosse `NOT NULL` sem valor padrão?

---

## Parte 3: expandir e contrair (25 min)

Cenário: o campo `origem` da tabela `voos` precisa ser renomeado para `aeroporto_origem`. O sistema está em produção e não pode parar.

> Se a tabela `voos` do seu projeto não tiver a coluna `origem`, use outra coluna de texto que exista (por exemplo, `destino`) e adapte os nomes.

Um `RENAME COLUMN` direto quebraria o código antigo no instante da migration. Por isso, vamos em passos.

### Passo 1: expandir

Crie `migrations/003_add_aeroporto_origem.sql`:

```sql
-- 003_add_aeroporto_origem.sql
-- up
ALTER TABLE voos ADD COLUMN aeroporto_origem VARCHAR(80) NULL;

-- down
ALTER TABLE voos DROP COLUMN aeroporto_origem;
```

Aplique com `php migrate.php up`.

### Passo 2: migrar os dados em lotes

Crie o script `backfill_origem.php`:

```php
<?php
$pdo = new PDO(
    'mysql:host=localhost;dbname=aeroporto_lab;charset=utf8mb4',
    'root',
    '',
    [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]
);

do {
    $afetadas = $pdo->exec(
        "UPDATE voos SET aeroporto_origem = origem
          WHERE aeroporto_origem IS NULL
          LIMIT 1000"
    );
    echo "Lote: $afetadas linhas\n";
    usleep(200000); // pausa de 0,2 s para não sobrecarregar o banco
} while ($afetadas > 0);
```

Rode o script e confira:

```sql
SELECT COUNT(*) FROM voos WHERE aeroporto_origem IS NULL;
```

**Checkpoint:** o resultado deve ser 0.

### Passo 3: trocar o código da aplicação

Este passo não é SQL. No código do projeto:

1. Primeiro, faça o `INSERT` e o `UPDATE` de voos gravarem **nos dois campos** (`origem` e `aeroporto_origem`).
2. Depois, faça as consultas (`SELECT`, listagens, formulários) lerem **só** `aeroporto_origem`.
3. Teste listar, criar, editar e excluir voos.

### Passo 4: contrair

Só depois de o código novo estar funcionando, crie `migrations/004_drop_origem.sql`:

```sql
-- 004_drop_origem.sql
-- up
ALTER TABLE voos DROP COLUMN origem;

-- down
ALTER TABLE voos ADD COLUMN origem VARCHAR(80) NULL;
```

Aplique com `php migrate.php up`.

**Pergunta 2.** Execute `php migrate.php down` logo em seguida. A coluna `origem` volta, mas os dados voltam? Escreva, em uma frase, o que o `down` desta migration **não** consegue desfazer e o que você faria para recuperar os dados.

---

## Parte 4: e se houvesse réplicas? (10 min)

Responda por escrito, em poucas linhas cada:

1. **Lag.** Se o backfill rodasse em um único `UPDATE` sem `LIMIT` em uma tabela de 5 milhões de voos, o que aconteceria com o primário e com as réplicas?
2. **Ordem.** Por que o passo 3 (trocar o código) precisa vir depois do passo 1 e antes do passo 4?
3. **Imutabilidade.** Depois de aplicar a `002` em todos os ambientes, você descobre que o tamanho certo de `portao_embarque` era 10, não 5. Por que não se edita a `002`? Qual migration você cria?
4. **Backup.** Qual dos quatro passos da Parte 3 é irreversível sem backup? Por quê?

---

## Entrega

Envie, em um único arquivo `.zip` ou em um repositório Git:

- [ ] `migrate.php`
- [ ] a pasta `migrations/` com as quatro migrations
- [ ] `backfill_origem.php`
- [ ] captura de tela (ou texto) da tabela `schema_migrations` após aplicar tudo
- [ ] as respostas das Perguntas 1 e 2 e da Parte 4, em um arquivo `respostas.md`


## Erros comuns

- **"Table already exists" ou "Duplicate column":** a migration foi aplicada na mão antes. Confira o estado do banco e a tabela `schema_migrations`.
- **`down` não encontra o arquivo:** o nome do arquivo precisa ser igual ao valor da coluna `version`, sem a extensão `.sql`.
- **`LIMIT` no `UPDATE` com `ORDER BY`:** o MySQL aceita `UPDATE ... LIMIT`, mas só em uma tabela por vez. Não use `JOIN` no backfill.
- **Esqueceu de trabalhar na cópia:** restaure o banco com o `aeroporto_backup.sql`.
