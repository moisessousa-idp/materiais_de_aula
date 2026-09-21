# Locking, Deadlocks e MVCC
## Simulação de disputa por assentos em um sistema de aeroporto

## 1. Contextualização

Um aeroporto precisa controlar os voos recebidos e a quantidade de assentos disponíveis em cada aeronave. O sistema deve permitir que passageiros consultem e reservem assentos, evitando que duas pessoas consigam reservar o mesmo assento simultaneamente.

Neste exercício, será criada uma entidade responsável por receber os voos e armazenar informações da aeronave, incluindo a quantidade total de assentos e os assentos disponíveis.

A situação-problema será:

> Dois passageiros diferentes tentam reservar simultaneamente o mesmo assento de um voo.

A partir desse cenário, serão estudados:

- **Locking (bloqueios)**;
- **Deadlocks (impasses)**;
- **MVCC (Multi-Version Concurrency Control)**;
- Isolamento de transações;
- Condições de corrida;
- Consistência dos dados;
- `SELECT ... FOR UPDATE`;
- `COMMIT` e `ROLLBACK`.

---

## 2. Objetivos

Ao final da atividade, o estudante deverá ser capaz de:

1. Modelar entidades relacionadas a voos, aeronaves, passageiros e reservas.
2. Identificar o problema de concorrência na reserva de assentos.
3. Utilizar transações para preservar a consistência dos dados.
4. Aplicar bloqueios explícitos com `FOR UPDATE`.
5. Explicar como ocorre um deadlock.
6. Compreender o funcionamento geral do MVCC.
7. Comparar diferentes estratégias de controle de concorrência.
8. Testar o comportamento do banco de dados com duas sessões simultâneas.

---

## 3. Modelo conceitual simplificado

O sistema será composto pelas seguintes entidades:

### 3.1. Aeronave

Representa a aeronave utilizada no voo.

Atributos sugeridos:

- `id`;
- `modelo`;
- `fabricante`;
- `quantidade_assentos`.

### 3.2. Voo

Representa um voo recebido pelo aeroporto.

Atributos sugeridos:

- `id`;
- `codigo`;
- `origem`;
- `destino`;
- `data_hora_saida`;
- `aeronave_id`;
- `status`.

### 3.3. Passageiro

Representa uma pessoa que pode realizar uma reserva.

Atributos sugeridos:

- `id`;
- `nome`;
- `documento`.

### 3.4. Assento

Representa um assento específico de uma aeronave ou de um voo.

Atributos sugeridos:

- `id`;
- `voo_id`;
- `numero`;
- `classe`;
- `status`.

O campo `status` pode assumir valores como:

- `DISPONIVEL`;
- `RESERVADO`;
- `BLOQUEADO`.

### 3.5. Reserva

Representa a associação entre um passageiro e um assento em determinado voo.

Atributos sugeridos:

- `id`;
- `passageiro_id`;
- `assento_id`;
- `data_reserva`;
- `status`.

---

## 4. Regra de negócio principal

Um assento não pode ser reservado por dois passageiros diferentes no mesmo voo.

A regra pode ser expressa da seguinte forma:

> Para cada voo e assento, deve existir no máximo uma reserva ativa.

Essa regra precisa ser protegida em dois níveis:

1. **Na aplicação**, por meio de validações;
2. **No banco de dados**, por meio de transações, bloqueios e restrições de integridade.

A validação realizada apenas na aplicação não é suficiente, pois duas transações podem consultar o mesmo assento como disponível antes que qualquer uma delas faça a atualização.

---

## 5. Estrutura inicial das tabelas

Os exemplos abaixo utilizam uma sintaxe próxima do PostgreSQL.

> Adapte os tipos e comandos caso esteja utilizando MySQL, MariaDB ou outro SGBD.

```sql
CREATE TABLE aeronaves (
    id BIGSERIAL PRIMARY KEY,
    fabricante VARCHAR(100) NOT NULL,
    modelo VARCHAR(100) NOT NULL,
    quantidade_assentos INTEGER NOT NULL
        CHECK (quantidade_assentos > 0)
);

CREATE TABLE voos (
    id BIGSERIAL PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    origem VARCHAR(100) NOT NULL,
    destino VARCHAR(100) NOT NULL,
    data_hora_saida TIMESTAMP NOT NULL,
    aeronave_id BIGINT NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'PROGRAMADO',

    CONSTRAINT fk_voo_aeronave
        FOREIGN KEY (aeronave_id)
        REFERENCES aeronaves(id)
);

CREATE TABLE passageiros (
    id BIGSERIAL PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    documento VARCHAR(30) NOT NULL UNIQUE
);

CREATE TABLE assentos (
    id BIGSERIAL PRIMARY KEY,
    voo_id BIGINT NOT NULL,
    numero VARCHAR(10) NOT NULL,
    classe VARCHAR(30) NOT NULL DEFAULT 'ECONOMICA',
    status VARCHAR(30) NOT NULL DEFAULT 'DISPONIVEL',

    CONSTRAINT fk_assento_voo
        FOREIGN KEY (voo_id)
        REFERENCES voos(id),

    CONSTRAINT uq_assento_voo
        UNIQUE (voo_id, numero)
);

CREATE TABLE reservas (
    id BIGSERIAL PRIMARY KEY,
    passageiro_id BIGINT NOT NULL,
    assento_id BIGINT NOT NULL,
    data_reserva TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(30) NOT NULL DEFAULT 'CONFIRMADA',

    CONSTRAINT fk_reserva_passageiro
        FOREIGN KEY (passageiro_id)
        REFERENCES passageiros(id),

    CONSTRAINT fk_reserva_assento
        FOREIGN KEY (assento_id)
        REFERENCES assentos(id)
);
```

---

## 6. Dados para teste

```sql
INSERT INTO aeronaves
    (fabricante, modelo, quantidade_assentos)
VALUES
    ('Airbus', 'A320', 180);

INSERT INTO voos
    (codigo, origem, destino, data_hora_saida, aeronave_id)
VALUES
    (
        'AB1234',
        'Brasília',
        'São Paulo',
        '2026-10-10 10:00:00',
        1
    );

INSERT INTO passageiros
    (nome, documento)
VALUES
    ('Passageiro A', 'DOC001'),
    ('Passageiro B', 'DOC002');
```

Exemplo de criação de assentos:

```sql
INSERT INTO assentos (voo_id, numero, classe)
VALUES
    (1, '10A', 'ECONOMICA'),
    (1, '10B', 'ECONOMICA'),
    (1, '10C', 'ECONOMICA');
```

---

## 7. Problema: condição de corrida

Imagine que o assento `10A` está disponível.

Duas transações são executadas simultaneamente:

- A transação T1 pertence ao Passageiro A;
- A transação T2 pertence ao Passageiro B.

As duas transações executam:

```sql
SELECT *
FROM assentos
WHERE voo_id = 1
  AND numero = '10A'
  AND status = 'DISPONIVEL';
```

Se não existir um controle adequado de concorrência, as duas transações podem ler o assento como disponível.

Em seguida:

- T1 tenta reservar o assento;
- T2 também tenta reservar o mesmo assento.

Esse cenário é conhecido como **condição de corrida**, pois o resultado depende da ordem e da interação entre operações concorrentes.

---

## 8. Transação sem bloqueio explícito

Exemplo conceitual:

```sql
BEGIN;

SELECT id, status
FROM assentos
WHERE voo_id = 1
  AND numero = '10A'
  AND status = 'DISPONIVEL';

UPDATE assentos
SET status = 'RESERVADO'
WHERE id = 1;

INSERT INTO reservas
    (passageiro_id, assento_id)
VALUES
    (1, 1);

COMMIT;
```

Esse exemplo não demonstra uma estratégia completa de proteção contra concorrência.

O problema é que a consulta e a atualização precisam ser tratadas como uma operação consistente. Apenas colocar os comandos dentro de uma transação não significa, por si só, que qualquer conflito será resolvido da maneira esperada.

---

## 9. Locking: bloqueio de registros

Locking é o mecanismo utilizado pelo SGBD para controlar o acesso concorrente aos dados.

Um bloqueio pode impedir que outra transação altere determinado registro enquanto a primeira transação não finalizar.

No PostgreSQL, um bloqueio explícito pode ser solicitado com:

```sql
SELECT ...
FOR UPDATE;
```

Esse comando solicita um bloqueio de atualização sobre as linhas retornadas.

O bloqueio permanece, em regra, até:

- `COMMIT`; ou
- `ROLLBACK`.

---

## 10. Reserva segura com `FOR UPDATE`

### 10.1. Sessão 1 — Passageiro A

```sql
BEGIN;

SELECT id, status
FROM assentos
WHERE voo_id = 1
  AND numero = '10A'
  AND status = 'DISPONIVEL'
FOR UPDATE;

UPDATE assentos
SET status = 'RESERVADO'
WHERE id = 1
  AND status = 'DISPONIVEL';

INSERT INTO reservas
    (passageiro_id, assento_id)
VALUES
    (1, 1);

COMMIT;
```

### 10.2. Sessão 2 — Passageiro B

Execute a segunda transação enquanto a primeira ainda estiver aberta:

```sql
BEGIN;

SELECT id, status
FROM assentos
WHERE voo_id = 1
  AND numero = '10A'
  AND status = 'DISPONIVEL'
FOR UPDATE;
```

A segunda sessão poderá ficar aguardando a liberação do bloqueio mantido pela primeira sessão.

Quando a Sessão 1 executar `COMMIT`, a Sessão 2 continuará sua execução e deverá verificar novamente se o assento ainda está disponível.

Essa nova verificação é importante porque o estado do registro pode ter sido alterado pela primeira transação.

---

## 11. Fluxo esperado da disputa

```text
Sessão 1                         Sessão 2
---------                        ---------
BEGIN                            BEGIN

SELECT ... FOR UPDATE            SELECT ... FOR UPDATE
Bloqueia o assento               Aguarda o bloqueio

UPDATE assento                   Em espera

INSERT reserva                   Em espera

COMMIT                           Recebe o controle

                                 Verifica novamente
                                 se o assento está disponível

                                 Se não estiver:
                                 ROLLBACK
```

A segunda sessão não deve simplesmente inserir uma reserva sem verificar o resultado da operação anterior.

---

## 12. Implementação mais segura com atualização condicional

Uma alternativa é realizar a alteração somente se o assento ainda estiver disponível:

```sql
BEGIN;

UPDATE assentos
SET status = 'RESERVADO'
WHERE id = 1
  AND status = 'DISPONIVEL'
RETURNING id;
```

Interpretação:

- Se a consulta retornar uma linha, a reserva pode prosseguir;
- Se não retornar nenhuma linha, o assento já não está disponível.

Depois da atualização bem-sucedida:

```sql
INSERT INTO reservas
    (passageiro_id, assento_id)
VALUES
    (1, 1);

COMMIT;
```

Caso nenhuma linha seja atualizada:

```sql
ROLLBACK;
```

Essa abordagem reduz a janela entre a verificação e a atualização.

---

## 13. Restrição de unicidade

Além do controle transacional, é recomendável impedir reservas duplicadas no banco.

Exemplo:

```sql
CREATE UNIQUE INDEX uq_reserva_assento_ativa
ON reservas (assento_id)
WHERE status = 'CONFIRMADA';
```

Essa solução é específica do PostgreSQL, pois utiliza um índice único parcial.

Ela impede que exista mais de uma reserva confirmada para o mesmo assento.

> Caso o sistema permita cancelamentos, o campo `status` deve ser considerado na regra de unicidade.

---

## 14. Deadlocks

Um deadlock ocorre quando duas ou mais transações ficam esperando indefinidamente por recursos bloqueados umas pelas outras.

Exemplo:

- A transação T1 bloqueia o assento 10A e tenta bloquear o assento 10B;
- A transação T2 bloqueia o assento 10B e tenta bloquear o assento 10A.

Representação:

```text
T1 bloqueia 10A
T2 bloqueia 10B

T1 aguarda 10B
T2 aguarda 10A

Resultado: DEADLOCK
```

O SGBD normalmente identifica o ciclo de espera e cancela uma das transações para permitir que a outra prossiga.

---

## 15. Exemplo prático de deadlock

### Sessão 1

```sql
BEGIN;

SELECT *
FROM assentos
WHERE id = 1
FOR UPDATE;

-- Aguarde antes de executar o próximo comando

SELECT *
FROM assentos
WHERE id = 2
FOR UPDATE;
```

### Sessão 2

```sql
BEGIN;

SELECT *
FROM assentos
WHERE id = 2
FOR UPDATE;

-- Aguarde antes de executar o próximo comando

SELECT *
FROM assentos
WHERE id = 1
FOR UPDATE;
```

As duas sessões podem entrar em uma situação de espera circular.

### Como evitar deadlocks

Uma estratégia comum é estabelecer uma ordem fixa para adquirir bloqueios.

Por exemplo:

- Sempre bloquear o assento de menor ID primeiro;
- Depois bloquear o assento de maior ID.

Assim, todas as transações seguem a mesma ordem de aquisição de recursos.

Outras medidas:

- Manter transações curtas;
- Evitar interação com o usuário dentro de uma transação;
- Confirmar ou desfazer a transação rapidamente;
- Tratar erros de deadlock na aplicação;
- Reexecutar a operação quando apropriado.

---

## 16. MVCC — Multi-Version Concurrency Control

MVCC significa **Controle de Concorrência por Múltiplas Versões**.

Em vez de fazer com que todas as leituras aguardem bloqueios de escrita, o banco pode disponibilizar uma versão consistente dos dados para cada transação.

No PostgreSQL, o MVCC permite que leitores e escritores trabalhem de maneira concorrente em muitos cenários.

De forma simplificada:

- Uma transação pode ler uma versão consistente de uma linha;
- Outra transação pode atualizar essa linha;
- A leitura não necessariamente precisa aguardar a conclusão da escrita;
- As regras de isolamento determinam quais versões podem ser observadas.

MVCC não significa que todos os conflitos desaparecem. Atualizações concorrentes, bloqueios explícitos, restrições de integridade e deadlocks continuam sendo relevantes.

---

## 17. Leitura e escrita com MVCC

Considere o seguinte cenário:

1. T1 inicia uma transação;
2. T1 lê o assento 10A como disponível;
3. T2 altera o assento para reservado;
4. T1 realiza uma nova leitura.

O resultado da segunda leitura dependerá do nível de isolamento utilizado.

No nível `READ COMMITTED`, cada comando normalmente observa uma visão consistente iniciada no começo daquele comando.

No nível `REPEATABLE READ`, a transação trabalha com uma visão consistente mantida durante toda a transação, respeitando as regras do SGBD.

No nível `SERIALIZABLE`, o banco tenta garantir um resultado equivalente à execução serial das transações, podendo abortar transações conflitantes para preservar a serialização.

---

## 18. Níveis de isolamento

### 18.1. READ UNCOMMITTED

Em alguns SGBDs, esse nível é apresentado como permitindo leituras não confirmadas. No PostgreSQL, `READ UNCOMMITTED` é tratado como `READ COMMITTED`.

### 18.2. READ COMMITTED

É o nível padrão do PostgreSQL.

Características gerais:

- Uma consulta não lê dados não confirmados;
- Cada comando possui sua própria visão consistente;
- Uma mesma transação pode observar mudanças confirmadas por outras transações entre comandos.

### 18.3. REPEATABLE READ

Características gerais:

- A transação mantém uma visão consistente;
- Leituras repetidas tendem a observar a mesma versão lógica dos dados;
- Conflitos de atualização podem causar falhas na transação.

### 18.4. SERIALIZABLE

Características gerais:

- Busca produzir um resultado equivalente a uma execução serial;
- Pode abortar transações devido a conflitos de serialização;
- A aplicação deve estar preparada para repetir transações abortadas quando adequado.

---

## 19. Simulação com duas sessões

### Preparação

Verifique o estado inicial:

```sql
SELECT
    id,
    voo_id,
    numero,
    status
FROM assentos
WHERE voo_id = 1
  AND numero = '10A';
```

O resultado esperado é:

```text
id | voo_id | numero | status
---+--------+--------+-----------
1  | 1      | 10A    | DISPONIVEL
```

### Experimento A — Sem `FOR UPDATE`

1. Abra duas conexões com o banco;
2. Execute a consulta de disponibilidade nas duas conexões;
3. Tente atualizar o mesmo assento;
4. Observe os resultados;
5. Verifique se o banco impediu a duplicidade por meio de restrições.

### Experimento B — Com `FOR UPDATE`

1. Inicie uma transação na Sessão 1;
2. Bloqueie o assento com `FOR UPDATE`;
3. Inicie uma transação na Sessão 2;
4. Tente bloquear o mesmo assento;
5. Observe que a Sessão 2 aguarda;
6. Faça `COMMIT` ou `ROLLBACK` na Sessão 1;
7. Observe o comportamento da Sessão 2;
8. Revalide a disponibilidade antes de confirmar a reserva.

### Experimento C — Deadlock

1. Na Sessão 1, bloqueie o assento 10A;
2. Na Sessão 2, bloqueie o assento 10B;
3. Na Sessão 1, tente bloquear o assento 10B;
4. Na Sessão 2, tente bloquear o assento 10A;
5. Observe a detecção do deadlock;
6. Identifique qual transação foi cancelada.

---

## 20. Perguntas para discussão

1. Por que uma consulta simples de disponibilidade não é suficiente para proteger uma reserva?
2. Qual é a finalidade do `FOR UPDATE`?
3. Quando o bloqueio é liberado?
4. O que acontece com a segunda sessão enquanto a primeira mantém o bloqueio?
5. Por que a segunda transação precisa validar novamente o status do assento?
6. O que é uma condição de corrida?
7. Qual é a diferença entre bloqueio e MVCC?
8. Como ocorre um deadlock?
9. Por que adquirir bloqueios sempre na mesma ordem pode reduzir deadlocks?
10. Qual é a diferença entre `READ COMMITTED`, `REPEATABLE READ` e `SERIALIZABLE`?
11. Por que uma restrição `UNIQUE` pode ser importante mesmo quando a aplicação já valida a disponibilidade?
12. Como a aplicação deve tratar uma transação abortada por deadlock ou falha de serialização?

---

## 21. Atividade prática

### Desafio

Implemente um procedimento de reserva de assento que:

1. Receba o ID do passageiro;
2. Receba o ID do voo;
3. Receba o número do assento;
4. Verifique se o assento existe;
5. Verifique se o assento está disponível;
6. Utilize uma transação;
7. Proteja o registro contra atualizações concorrentes;
8. Atualize o status do assento;
9. Insira a reserva;
10. Confirme a transação somente quando todas as etapas forem concluídas;
11. Faça `ROLLBACK` quando houver erro;
12. Impeça a duplicidade de reservas.

### Requisitos adicionais

- Testar dois passageiros tentando reservar o mesmo assento;
- Testar dois passageiros reservando assentos diferentes;
- Simular um deadlock;
- Registrar o resultado de cada transação;
- Explicar qual estratégia de concorrência foi utilizada.

---

## 22. Boas práticas

- Usar transações curtas;
- Bloquear somente os registros necessários;
- Adquirir bloqueios em uma ordem consistente;
- Utilizar restrições de integridade no banco;
- Não confiar exclusivamente na validação da aplicação;
- Revalidar o estado após a aquisição de bloqueios;
- Tratar erros de concorrência;
- Registrar falhas e tentativas de repetição;
- Evitar manter transações abertas durante a interação do usuário;
- Escolher o nível de isolamento de acordo com os requisitos do sistema.

---

## 23. Conclusão

O controle de concorrência é fundamental em sistemas de reservas, como os utilizados por aeroportos, companhias aéreas, hotéis e plataformas de venda de ingressos.

No cenário de disputa por assentos, duas pessoas podem tentar reservar o mesmo recurso ao mesmo tempo. Para evitar inconsistências, o sistema deve combinar:

- Modelagem adequada;
- Transações;
- Bloqueios;
- Restrições de integridade;
- Estratégias de isolamento;
- Tratamento de deadlocks;
- Conhecimento sobre MVCC.

A principal ideia é garantir que, independentemente da ordem em que as transações sejam executadas, o banco de dados não permita que dois passageiros confirmem o mesmo assento.
