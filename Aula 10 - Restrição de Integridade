# Atividade — Regras de Integridade do Banco de Dados

## 1. Banco de dados utilizado

O grupo deverá utilizar **o mesmo banco de dados desenvolvido desde o início do semestre**.

A atividade deverá ser realizada sobre o banco de dados atual do projeto, considerando sua estrutura, suas tabelas e suas regras de negócio.

Não deverá ser criado um banco de dados fictício ou um exemplo diferente do projeto do grupo.

---

## 2. Identificação das regras de integridade

O grupo deverá analisar o banco de dados e identificar as regras de integridade necessárias para garantir a consistência e a validade dos dados armazenados.

Deverão ser analisadas, no mínimo:

* Integridade de entidade;
* Integridade referencial;
* Integridade de domínio;
* Integridade de chave;
* Restrições de unicidade;
* Obrigatoriedade de preenchimento;
* Regras relacionadas ao negócio do sistema.

Para cada regra identificada, o grupo deverá explicar **qual problema ela evita e como será implementada no banco de dados**.

---

## 3. Aplicação das regras de integridade

As regras identificadas deverão ser implementadas no banco utilizando os recursos disponíveis no SGBD.

Deverão ser analisadas e utilizadas, quando necessárias:

```sql
PRIMARY KEY
FOREIGN KEY
NOT NULL
UNIQUE
CHECK
DEFAULT
```

Também deverão ser consideradas as ações relacionadas às chaves estrangeiras, quando aplicáveis:

```sql
ON DELETE
ON UPDATE
```

O grupo deverá justificar a utilização de cada restrição.

Exemplo:

```sql
CREATE TABLE cliente (
    id_cliente INT PRIMARY KEY,
    cpf VARCHAR(11) NOT NULL UNIQUE,
    nome VARCHAR(100) NOT NULL
);
```

Nesse exemplo, deverão ser identificadas e explicadas as regras de integridade aplicadas a cada atributo.

---

## 4. Regras de negócio

O grupo deverá identificar regras específicas do funcionamento do sistema que precisam ser garantidas pelo banco de dados.

Exemplos:

* Um CPF não pode pertencer a dois clientes;
* Um pedido deve estar associado a um cliente existente;
* Uma quantidade de produto não pode ser menor ou igual a zero;
* Uma data de término não pode ser anterior à data de início;
* Um registro não pode ser excluído enquanto existir outro registro dependente dele.

As regras deverão ser definidas de acordo com **o sistema desenvolvido pelo próprio grupo**.

Não é necessário utilizar os exemplos acima caso eles não sejam aplicáveis ao projeto.

---

## 5. Testes das regras de integridade

O grupo deverá realizar testes para demonstrar que as regras implementadas estão funcionando.

Para cada regra relevante, deverá ser apresentado:

* Situação testada;
* Comando SQL utilizado;
* Resultado esperado;
* Resultado obtido.

Exemplo:

```sql
INSERT INTO cliente (id_cliente, cpf, nome)
VALUES (2, '11111111111', 'João');
```

Caso o CPF já esteja cadastrado e exista uma restrição `UNIQUE`, o banco deverá impedir a operação.

O grupo deverá registrar o resultado do teste.

---

## 6. SQL final

Após implementar as regras de integridade, o grupo deverá entregar o SQL atualizado do banco.

O arquivo deverá conter a criação das tabelas e suas respectivas restrições.

```text
sql_integridade.sql
```

O SQL deverá permitir recriar o banco já com as regras de integridade implementadas.

---

## 7. Observação importante

As regras de integridade deverão estar relacionadas ao **banco de dados real do projeto**.

Não deverão ser criadas restrições apenas para aumentar a quantidade de comandos SQL.

Cada restrição deverá possuir uma justificativa relacionada à estrutura ou às regras de negócio do sistema.

Também deverá ser evitada a utilização de regras que impeçam operações válidas do sistema.

---

## 8. Entrega

A entrega deverá conter:

```text
/
├── sql_integridade.sql
└── integridade.md
```

O arquivo `integridade.md` deverá apresentar:

* Regras de integridade identificadas;
* Justificativa de cada regra;
* Restrições utilizadas;
* Regras de negócio implementadas;
* Testes realizados;
* Resultados dos testes.

### Critério fundamental

A avaliação será baseada na capacidade do grupo de **identificar, implementar e testar corretamente as regras de integridade do próprio banco de dados**, demonstrando que o SGBD é capaz de impedir a inserção ou alteração de dados inconsistentes.
