# Prática — Modelagem de Dados: Sistema de Aeroporto

**Duração:** 25–30 minutos  
**Modalidade:** Individual

## Objetivo

A partir de entidades já identificadas anteriormente, construir parte do modelo de dados de um sistema de aeroporto, trabalhando:

- Atributos
- Chaves primárias
- Chaves estrangeiras
- Relacionamentos
- Cardinalidade
- Tabela associativa
- Modelo lógico

---

## Cenário

Um aeroporto deseja organizar as informações relacionadas aos seus voos.

As seguintes entidades já foram identificadas:

- **PASSAGEIRO**
- **VOO**
- **AERONAVE**

### Regras do sistema

1. Um passageiro pode realizar vários voos.
2. Um voo pode possuir vários passageiros.
3. Uma aeronave pode realizar vários voos.
4. Cada voo é realizado por uma aeronave.
5. Para cada passageiro em um voo, deve ser registrado o assento ocupado.

---

## 1. Definição dos atributos — 5 minutos

Para cada entidade, defina os atributos necessários.

### PASSAGEIRO

Defina pelo menos 4 atributos.

| Atributo | Observação |
| -------- | ---------- |
|          |            |
|          |            |
|          |            |
|          |            |

**Qual atributo será a chave primária?**

---

### VOO

Defina pelo menos 5 atributos.

| Atributo | Observação |
| -------- | ---------- |
|          |            |
|          |            |
|          |            |
|          |            |
|          |            |

**Qual atributo será a chave primária?**

---

### AERONAVE

Defina pelo menos 3 atributos.

| Atributo | Observação |
| -------- | ---------- |
|          |            |
|          |            |
|          |            |

**Qual atributo será a chave primária?**

---

## 2. Identificação dos relacionamentos — 5 minutos

Com base nas regras do sistema, determine a cardinalidade de cada relacionamento.

### PASSAGEIRO ↔ VOO

Um passageiro pode realizar vários voos.

Um voo pode possuir vários passageiros.

**Cardinalidade:**

```text
________________
```

---

### AERONAVE ↔ VOO

Uma aeronave pode realizar vários voos.

Cada voo é realizado por uma aeronave.

**Cardinalidade:**

```text
________________
```

---

## 3. Resolva o relacionamento N:N — 5 minutos

Existe um relacionamento **N:N entre PASSAGEIRO e VOO**.

Responda:

> Como podemos representar esse relacionamento no modelo lógico?

Crie uma **tabela associativa** para representar a relação entre passageiros e voos.

### Nome da tabela:

```text
________________
```

### Atributos:

| Atributo | Tipo de chave |
| -------- | ------------- |
|          |               |
|          |               |
|          |               |
|          |               |

---

## 4. Modelo lógico — 10 minutos

Agora transforme o modelo desenvolvido em tabelas.

Utilize a seguinte representação:

```text
TABELA
----------------
atributo PK
atributo
atributo FK
```

### PASSAGEIRO

```text
____________________________
____________________________
____________________________
____________________________
____________________________
```

### AERONAVE

```text
____________________________
____________________________
____________________________
____________________________
```

### VOO

```text
____________________________
____________________________
____________________________
____________________________
____________________________
____________________________
```

### Tabela associativa

```text
____________________________
____________________________
____________________________
____________________________
____________________________
```

---

## 5. Questões finais

### Questão 1

Por que não podemos simplesmente colocar `id_passageiro` dentro da tabela `VOO`?

**Resposta:**

---

---

---

### Questão 2

Por que precisamos de uma tabela associativa entre PASSAGEIRO e VOO?

**Resposta:**

---

---

---

### Questão 3

Qual é a diferença entre uma **chave primária (PK)** e uma **chave estrangeira (FK)**?

**Resposta:**

---

---

---

## Desafio

Considere agora a seguinte regra:

> Um passageiro não pode ocupar dois assentos diferentes no mesmo voo.

Como você poderia modificar o modelo para garantir essa regra?

**Resposta:**

---

---

---

---

### Entrega

Ao final da atividade, o **aluno deverá entregar individualmente**:

- [ ] Atributos das entidades
- [ ] Chaves primárias
- [ ] Relacionamentos
- [ ] Cardinalidades
- [ ] Tabela associativa
- [ ] Modelo lógico
- [ ] Respostas às questões finais