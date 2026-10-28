# Aula 25 – Prática: Login e Validação no Sistema do Aeroporto

**Duração:** 20 min
**Projeto:** o sistema do aeroporto (PHP + MySQL) que vocês já vêm construindo, com o model de voos (listar, criar, editar e excluir).

## Objetivo

Ao final, o cadastro de voos só deve funcionar para quem fez login, rejeitar dados inválidos e nunca mostrar erro de banco na tela.

## Parte 1 – Tabela de usuários (3 min)

Crie a tabela no banco do aeroporto:

```sql
CREATE TABLE usuarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(120) NOT NULL UNIQUE,
  senha_hash VARCHAR(255) NOT NULL,
  perfil VARCHAR(20) NOT NULL DEFAULT 'operador'
);
```

Cadastre um usuário de teste. Gere o hash em um script PHP e grave o resultado na coluna `senha_hash`:

```php
echo password_hash('senha123', PASSWORD_DEFAULT);
```

## Parte 2 – Login e logout (6 min)

1. Crie `login.php` com um formulário (e-mail e senha) enviado por POST.
2. Busque o usuário com **prepared statement**.
3. Confira a senha com `password_verify`.
4. Se estiver correto, chame `session_regenerate_id(true)`, grave `$_SESSION['usuario_id']` e redirecione para a lista de voos.
5. Se estiver errado, mostre sempre a mesma mensagem: `E-mail ou senha inválidos`.
6. Crie `logout.php`, que limpa `$_SESSION` e chama `session_destroy()`.

## Parte 3 – Proteger as páginas (3 min)

Crie `auth.php`:

```php
session_start();
if (empty($_SESSION['usuario_id'])) {
    header('Location: /login');
    exit;
}
```

Use `require 'auth.php';` no topo das páginas de listar, criar, editar e excluir voos.

**Teste:** abra a lista de voos sem estar logado. Você deve ser redirecionado para o login.

## Parte 4 – Validar o cadastro de voo (5 min)

No cadastro de voo, valide no servidor:

- `codigo` no formato de duas letras e 3 ou 4 números (ex.: `LA1234`);
- origem diferente de destino;
- data de partida no futuro.

Guarde as mensagens em um array `$erros` e só salve se ele estiver vazio. Se houver erros, reexiba o formulário com a lista.

## Parte 5 – Tratar erros do banco (3 min)

1. Configure o PDO com `PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION`.
2. Envolva o `salvar()` do model em `try/catch (PDOException $e)`.
3. No `catch`, use `error_log($e->getMessage())` e mostre ao usuário apenas: `Não foi possível salvar o voo.`

**Teste:** force um erro (por exemplo, renomeie temporariamente a tabela `voo`). A tela deve mostrar só a mensagem genérica, e o detalhe técnico deve aparecer no log.

## Critério de pronto

- [ ] Senhas gravadas como hash, nunca em texto puro
- [ ] Login funciona e a mensagem de erro é a mesma para e-mail ou senha errados
- [ ] Páginas de voos redirecionam para o login quando não há sessão
- [ ] Logout encerra a sessão
- [ ] Voo inválido é rejeitado com mensagem clara
- [ ] Erro de banco não aparece na tela e é registrado no log

## Desafio opcional

Permitir a exclusão de voos apenas para o perfil `admin`, respondendo com 403 para os demais.
