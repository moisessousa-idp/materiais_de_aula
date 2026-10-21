# Aula prática: SQL Injection no sistema do Aeroporto

**Duração:** 30 a 40 minutos | **Formato:** individual ou em dupla | **Stack:** PHP + MySQL (PDO), MVC

## Objetivo

Implementar a mesma busca de voos de **duas formas** (sem e com *prepared statements*), aplicar os mesmos ataques nas duas e comparar os resultados.

> Teste apenas no projeto local de vocês. Nunca em sistemas de terceiros.

---

## 1. Preparação (5 min)

Garanta que existem dados de teste em `voos` e `usuarios`. Adapte os nomes de tabelas e colunas abaixo para o seu projeto.

A busca será por **destino**, via GET:

```
index.php?acao=buscar&versao=a&destino=Lisboa
```

---

## 2. Implementação (10 min)

No `VooModel`, crie os dois métodos.

**Versão A: sem prepared statements (vulnerável)**

```php
public function buscarVulneravel(string $destino): array
{
    $sql = "SELECT id, numero_voo, origem, destino, status
            FROM voos WHERE destino = '$destino'";
    return $this->pdo->query($sql)->fetchAll();
}
```

**Versão B: com prepared statements (seguro)**

```php
public function buscarSeguro(string $destino): array
{
    $stmt = $this->pdo->prepare(
        'SELECT id, numero_voo, origem, destino, status
         FROM voos WHERE destino = :destino'
    );
    $stmt->execute([':destino' => $destino]);
    return $stmt->fetchAll();
}
```

No `VooController`, escolha a versão pelo parâmetro `versao`:

```php
public function buscar(): void
{
    $destino = $_GET['destino'] ?? '';
    $voos = ($_GET['versao'] ?? 'b') === 'a'
        ? $this->model->buscarVulneravel($destino)
        : $this->model->buscarSeguro($destino);

    require 'views/voos/listar.php';
}
```

---

## 3. Ataques (15 min)

Execute **cada payload nas duas versões** (`versao=a` e `versao=b`) e anote o resultado.

| # | Payload no campo `destino` | O que tenta fazer |
|---|---|---|
| 1 | `Lisboa` | Busca normal (controle) |
| 2 | `'` | Quebrar a consulta e provocar erro |
| 3 | `' OR '1'='1` | Listar todos os voos, ignorando o filtro |
| 4 | `x' UNION SELECT id, email, senha_hash, 4, 5 FROM usuarios -- ` | Vazar dados de outra tabela |

Observações:

- No payload 4, o `UNION` exige o **mesmo número de colunas** do `SELECT` original (aqui, 5). Ajuste se o seu `SELECT` for diferente.
- Depois do `--` é necessário um **espaço** no MySQL.
- Para enviar na URL, o navegador codifica os caracteres especiais automaticamente ao usar um formulário. Se colar direto na barra de endereço, troque espaços por `%20`.

---

## 4. Comparação (5 min)

Preencha a tabela com o que aconteceu:

| Payload | Versão A (sem prepared) | Versão B (com prepared) |
|---|---|---|
| 1 `Lisboa` | | |
| 2 `'` | | |
| 3 `' OR '1'='1` | | |
| 4 `UNION ...` | | |

Responda em 2 ou 3 linhas cada:

1. Por que a versão B se comporta diferente com o mesmo texto de entrada?
2. O que o banco recebe como **comando** e o que recebe como **dado** em cada versão?
3. Se só a versão A existisse em produção, qual seria o pior dano do payload 4?

---

## 5. Entrega

A tabela de comparação preenchida e as respostas das 3 perguntas (arquivo `.md` ou PDF no Moodle).

Depois da entrega, **remova o método `buscarVulneravel`** do projeto.
