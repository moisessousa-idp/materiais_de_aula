# Laboratório – Locadora v2

**Duração:** 2h | **Formato:** duplas | **Stack:** PHP + MySQL (PDO)
**Projeto:** continuação da locadora de carros desenvolvida no Bimestre I

## Objetivo

Evoluir o sistema da locadora aplicando, na prática, os temas das Aulas 20 a 25: integração frontend + backend, estrutura de arquivos (MVC), backup e recuperação, segurança, privilégios no banco e autenticação com validação e tratamento de erros.

## Regras

- Trabalhem em dupla, alternando quem digita a cada etapa.
- Ao terminar cada etapa, confirmem o **checklist** da etapa antes de avançar.
- Adaptem os nomes de tabelas e colunas ao esquema que vocês criaram no Bimestre I. Os exemplos abaixo são modelos.
- Se o tempo apertar, priorizem as etapas 1, 4, 5 e 6. As etapas 2 e 3 podem ser feitas de forma reduzida.

## Cronograma sugerido

| Tempo | Etapa | Tema |
|---|---|---|
| 0–10 min | 0 | Preparação |
| 10–30 min | 1 | Estrutura de arquivos (Aula 21) |
| 30–45 min | 2 | Frontend + Backend (Aula 20) |
| 45–60 min | 3 | Backup e recuperação (Aula 22) |
| 60–75 min | 4 | Segurança (Aula 23) |
| 75–90 min | 5 | Privilégios no banco (Aula 24) |
| 90–115 min | 6 | Autenticação, validação e erros (Aula 25) |
| 115–120 min | 7 | Entrega |

---

## Etapa 0 – Preparação (10 min)

1. Abram o projeto do Bimestre I e confirmem que ele roda.
2. Confirmem a conexão com o MySQL.
3. Definam quem começa digitando.

**Checklist**
- [ ] O sistema abre no navegador e lista ao menos um registro do banco.

---

## Etapa 1 – Estrutura de arquivos (Aula 21)

Reorganizem o projeto no padrão MVC, com a única porta de entrada em `public/`:

```
locadora/
├── config/
│   ├── config.php        # credenciais e parâmetros
│   └── database.php      # conexão PDO
├── controllers/
├── models/
├── views/
├── logs/
└── public/
    └── index.php         # front controller
```

Conexão centralizada (`config/database.php`):

```php
<?php
require_once __DIR__ . '/config.php';

function getConnection(): PDO {
    $dsn = 'mysql:host=' . DB_HOST . ';dbname=' . DB_NAME . ';charset=utf8mb4';
    return new PDO($dsn, DB_USER, DB_PASS, [
        PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_EMULATE_PREPARES   => false,
    ]);
}
```

**Tarefa:** implementar o CRUD de **Carros** (listar, criar, editar, excluir) separando `CarroModel`, `CarroController` e as views.

**Checklist**
- [ ] Nenhuma consulta SQL dentro de views.
- [ ] Credenciais do banco apenas em `config/config.php`.
- [ ] Só a pasta `public/` fica exposta ao navegador.
- [ ] CRUD de Carros funcionando pelo padrão MVC.

---

## Etapa 2 – Frontend + Backend (Aula 20)

**Tarefa:** conectar formulários e listagens de **Clientes** ou **Locações** ao banco.

- Formulário HTML enviando por `POST` para o controller.
- Listagem dinâmica a partir de uma consulta ao banco.
- Mensagem de sucesso ou erro após cada ação.

**Checklist**
- [ ] É possível cadastrar e listar pelo navegador sem tocar no banco manualmente.
- [ ] O formulário de edição vem preenchido com os dados atuais.

---

## Etapa 3 – Backup e recuperação (Aula 22)

**Parte A – Soft delete em Carros**

```sql
ALTER TABLE carros ADD COLUMN deleted_at DATETIME NULL DEFAULT NULL;
```

- "Excluir" passa a executar `UPDATE carros SET deleted_at = NOW() WHERE id = ?`.
- Todas as listagens passam a filtrar `WHERE deleted_at IS NULL`.

**Parte B – Backup e restauração**

```bash
mysqldump -u root -p locadora > backup_locadora.sql
```

1. Criem uma tabela de teste (`teste_restore`) e façam o backup.
2. Apaguem a tabela de teste.
3. Restaurem:

```bash
mysql -u root -p locadora < backup_locadora.sql
```

**Checklist**
- [ ] Um carro "excluído" some da listagem, mas continua no banco.
- [ ] Existe um arquivo `.sql` de backup e a restauração foi testada.

---

## Etapa 4 – Segurança (Aula 23)

1. Converter **todas** as consultas para prepared statements:

```php
$stmt = $pdo->prepare('SELECT * FROM carros WHERE modelo LIKE :modelo AND deleted_at IS NULL');
$stmt->execute([':modelo' => '%' . $busca . '%']);
```

2. Escapar toda saída exibida em HTML:

```php
<?= htmlspecialchars($carro['modelo'], ENT_QUOTES, 'UTF-8') ?>
```

3. **Teste de ataque:** na busca de carros, digitem `' OR '1'='1`. Registrem o comportamento (ou como ficaria) com consulta concatenada e com prepared statement.

**Checklist**
- [ ] Não existe SQL montado por concatenação de entrada do usuário.
- [ ] Digitar `<script>alert(1)</script>` em um campo não executa o script na tela.
- [ ] O teste de SQL Injection foi feito e o resultado anotado.

---

## Etapa 5 – Privilégios no banco (Aula 24)

Atenção: **usuário do SGBD** (quem conecta ao MySQL) não é o mesmo que **usuário do sistema** (linha na tabela `usuarios`).

```sql
CREATE USER 'app_locadora'@'localhost' IDENTIFIED BY 'troque_esta_senha';
GRANT SELECT, INSERT, UPDATE ON locadora.* TO 'app_locadora'@'localhost';

CREATE USER 'admin_locadora'@'localhost' IDENTIFIED BY 'troque_esta_senha_admin';
GRANT ALL PRIVILEGES ON locadora.* TO 'admin_locadora'@'localhost';

FLUSH PRIVILEGES;
```

**Tarefa**
1. Trocar `DB_USER` e `DB_PASS` em `config/config.php` para o usuário `app_locadora`.
2. Tentar executar um `DELETE` físico pela aplicação e confirmar que o MySQL nega.
3. Anotar quais comandos cada usuário do SGBD consegue e não consegue executar.

**Checklist**
- [ ] A aplicação conecta com o usuário limitado, não com `root`.
- [ ] Um `DELETE` ou `DROP` com `app_locadora` é negado.

---

## Etapa 6 – Autenticação, validação e erros (Aula 25)

**Tabela de usuários do sistema**

```sql
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    perfil ENUM('admin','atendente') NOT NULL DEFAULT 'atendente',
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

**Cadastro e login**

```php
// cadastro
$hash = password_hash($senha, PASSWORD_DEFAULT);

// login
if ($usuario && password_verify($senha, $usuario['senha_hash'])) {
    session_regenerate_id(true);
    $_SESSION['usuario_id'] = $usuario['id'];
    $_SESSION['perfil']     = $usuario['perfil'];
}
```

**Proteção de rotas**

```php
function exigirLogin(): void {
    if (empty($_SESSION['usuario_id'])) {
        header('Location: /login');
        exit;
    }
}
```

**Validação no servidor** (nunca confiem só no HTML):
- campos obrigatórios preenchidos;
- placa no formato esperado;
- data de devolução posterior à data de retirada;
- e-mail válido (`filter_var($email, FILTER_VALIDATE_EMAIL)`).

**Tratamento de erros e log**

```php
try {
    // operação com o banco
} catch (PDOException $e) {
    error_log('[' . date('c') . '] ' . $e->getMessage() . PHP_EOL, 3, __DIR__ . '/../logs/erros.log');
    $erro = 'Não foi possível concluir a operação. Tente novamente.';
}
```

O usuário vê uma mensagem genérica. O detalhe técnico vai só para o log.

**Mensagem de login:** use sempre a mesma frase para e-mail inexistente e senha errada ("E-mail ou senha inválidos").

**Checklist**
- [ ] Senhas armazenadas com `password_hash`, nunca em texto puro.
- [ ] Acessar a listagem de carros sem login redireciona para o login.
- [ ] Dados inválidos são recusados pelo servidor com mensagem clara.
- [ ] Um erro de banco gera linha em `logs/erros.log` e não expõe detalhes na tela.

---

## Etapa 7 – Entrega (5 min)

Entreguem a pasta do projeto compactada (ou o link do repositório), incluindo:

- código do sistema;
- `backup_locadora.sql`;
- um arquivo `LEIAME.md` com: nomes da dupla, o que foi feito em cada etapa, resultado do teste de SQL Injection e os comandos de `GRANT` usados.
