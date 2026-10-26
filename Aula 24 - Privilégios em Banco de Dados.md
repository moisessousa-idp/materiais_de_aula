# Prática: Privilégios no projeto do aeroporto

**Duração:** 20 minutos
**Tema:** usuários do SGBD × usuários da aplicação, `CREATE USER`, `GRANT`, `REVOKE`
**Projeto:** o sistema do aeroporto que vocês vêm construindo (PHP + MySQL, CRUD de voos)

> Os nomes de banco e tabelas abaixo (`aeroporto`, `voos`, `passageiros`) são os do exemplo. Se no seu projeto forem diferentes, adapte os comandos.

---

## Objetivo

Ao final, você deve conseguir:

1. Criar uma conta **do SGBD** com privilégios mínimos para a aplicação.
2. Trocar a conexão do PHP de `root` para essa conta.
3. Explicar por que a conta do SGBD e os usuários da tabela `usuarios` são coisas diferentes.

## Antes de começar

- Banco `aeroporto` criado e CRUD de voos funcionando com `root`.
- Acesso ao terminal do MySQL como administrador:

```bash
mysql -u root -p
```

---

## Parte 1: Criar a conta da aplicação (5 min)

Conectado como `root`, crie a conta e conceda **apenas** o necessário para o CRUD de voos:

```sql
CREATE USER 'app_aeroporto'@'localhost'
  IDENTIFIED BY 'SenhaForte#123';

GRANT SELECT, INSERT, UPDATE
  ON aeroporto.voos
  TO 'app_aeroporto'@'localhost';
```

Confira o que a conta pode:

```sql
SHOW GRANTS FOR 'app_aeroporto'@'localhost';
```

**Atenção:**

- Se o seu CRUD de voos consulta outras tabelas (por exemplo, listas de aeroportos ou companhias), conceda também `SELECT` nelas.
- Não é preciso rodar `FLUSH PRIVILEGES` após `GRANT`.
- Troque a senha do exemplo por uma sua.

**Registre:** quais privilégios aparecem no `SHOW GRANTS`?

---

## Parte 2: Trocar a conexão do PHP (5 min)

No arquivo de conexão do projeto, troque o usuário e a senha. O restante do código não muda.

```php
<?php
$dsn = "mysql:host=localhost;dbname=aeroporto;charset=utf8mb4";

$pdo = new PDO($dsn, "app_aeroporto", "SenhaForte#123", [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
]);
```

- Antes: `"root"`. Agora: `"app_aeroporto"`.
- O modo de exceções (`ERRMODE_EXCEPTION`) faz o PDO lançar erro quando o banco negar uma operação, o que facilita o teste.
- Em um sistema real, a senha ficaria em variável de ambiente, não no código.

---

## Parte 3: Testar o CRUD (6 min)

Teste cada operação pela aplicação e preencha a tabela.

| Operação | Esperado | O que aconteceu? |
|---|---|---|
| Listar voos (`SELECT`) | funciona | |
| Criar voo (`INSERT`) | funciona | |
| Editar voo (`UPDATE`) | funciona | |
| Excluir voo (`DELETE`) | **erro** | |

Para ver a mensagem de erro do banco, rode no terminal com a conta nova:

```bash
mysql -u app_aeroporto -p aeroporto
```

```sql
DELETE FROM voos WHERE id = 1;
-- ERROR 1142 (42000): DELETE command denied to user 'app_aeroporto'@'localhost' ...

DROP TABLE voos;
-- ERROR 1142 (42000): DROP command denied to user 'app_aeroporto'@'localhost' ...
```

Na aplicação, trate a exceção sem mostrar a mensagem bruta do banco ao usuário:

```php
try {
    $stmt = $pdo->prepare("DELETE FROM voos WHERE id = :id");
    $stmt->execute([":id" => $id]);
} catch (PDOException $e) {
    error_log($e->getMessage());          // detalhe fica no log
    echo "Operação não permitida.";       // mensagem genérica para o usuário
}
```

> **Se o seu projeto usa soft delete** (excluir = `UPDATE ... SET ativo = 0`), o "excluir" continuará funcionando, porque ele é um `UPDATE`. Anote isso: é a conta sem `DELETE` que impede apagar de verdade, não o botão da tela.

---

## Parte 4: Discussão (4 min)

Responda em duas ou três linhas cada:

1. Na tabela `usuarios`, a Maria tem perfil de atendente. O que **mudou para ela** quando você trocou `root` por `app_aeroporto`? E o que mudou para a **conexão**?
2. Quem decide se a Maria pode excluir um voo: o banco ou o código PHP? Por quê?
3. Se alguém conseguisse uma SQL Injection nesta aplicação **agora**, o que o atacante ainda conseguiria fazer? E se a conexão ainda fosse `root`?

---

## Desafio: conta só de leitura

Para quem terminar antes.

```sql
-- como root
CREATE USER 'relatorios'@'localhost' IDENTIFIED BY 'OutraSenha#456';
GRANT SELECT ON aeroporto.* TO 'relatorios'@'localhost';
```

1. Conecte com `relatorios` e tente um `INSERT` em `voos`. Qual foi o erro?
2. Restrinja a conta para que ela **não leia a coluna de CPF** de `passageiros`:

```sql
-- como root
REVOKE SELECT ON aeroporto.* FROM 'relatorios'@'localhost';
GRANT SELECT (id, nome) ON aeroporto.passageiros TO 'relatorios'@'localhost';
```

3. Conecte com `relatorios` e rode `SELECT cpf FROM passageiros;`. Qual foi o erro? (Algo como `ERROR 1143: SELECT command denied ... for column 'cpf'`.)
4. Alternativa: crie uma **view** só com as colunas permitidas e conceda `SELECT` apenas nela.

---

## O que entregar

- Saída do `SHOW GRANTS FOR 'app_aeroporto'@'localhost'`.
- Tabela da Parte 3 preenchida, com a mensagem de erro do `DELETE`.
- Respostas da Parte 4.
- (Desafio) Mensagens de erro dos itens 1 e 3.

---

## Problemas comuns

| Sintoma | Causa provável | O que fazer |
|---|---|---|
| `ERROR 1045: Access denied for user` | Senha errada ou host diferente do criado | Confira usuário, senha e se a conta é `'...'@'localhost'` |
| `ERROR 1044` ao criar usuário ou conceder | Você não está como `root` | Reconecte como administrador |
| CRUD quebrou no `SELECT` | A tela usa outra tabela sem `GRANT` | Conceda `SELECT` nela, ou revise a consulta |
| `SQLSTATE[42000] ... denied` na tela | Operação não concedida à conta | É o comportamento esperado para `DELETE` e `DROP` |

---

## Limpeza (opcional)

```sql
-- como root
DROP USER 'relatorios'@'localhost';
-- Mantenha app_aeroporto: ela será usada nas próximas aulas.
```
