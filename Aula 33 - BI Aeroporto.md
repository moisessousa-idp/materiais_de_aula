# Prática: Painéis do Aeroporto

## Situação

A direção do aeroporto quer acompanhar a operação por meio de **painéis**. O sistema que vocês estão montando é **OLTP**; para alimentar os painéis, é preciso um **modelo dimensional** e **consultas analíticas**.

Usem as tabelas e os campos do projeto de vocês. Se faltar algum dado, anotem como **lacuna do modelo**.

## Painéis a construir

| # | Painel | Tipo de pergunta |
|---|---|---|
| 1 | **Destinos mais frequentes** do aeroporto | Ranking |
| 2 | **Número de passageiros por mês** | Evolução |
| 3 | **Número de voos** | Quanto? |
| 4 | **Companhia aérea mais atuante** | Ranking / participação |
| 5 | **Painel livre**, escolhido pela dupla | A critério da dupla |

---

## Tarefas

### 1. Modelo estrela (10 min)

Definam o modelo que alimenta os painéis:

- O **grão**: *"Uma linha do fato representa..."*
- As **medidas** (aditivas, semiaditivas ou não aditivas).
- As **dimensões** e seus atributos principais (inclua a **dimensão tempo**).
- Desenhem a estrela.

> **Pergunta para pensar:** uma única tabela fato atende aos cinco painéis? Justifiquem a resposta.

### 2. Ficha de cada painel (15 min)

Preencham **uma ficha por painel**:

```
PAINEL: ______________________________
Pergunta de negócio:   ______________________________
Indicador (medida):    ______________________________
Dimensões usadas:      ______________________________
Filtros do painel:     ______________________________
Gráfico sugerido:      ______________________________
Operação OLAP:         ( ) roll up  ( ) drill down  ( ) slice  ( ) dice  ( ) pivot
```

### 3. Estrutura das consultas (10 min)

Escrevam a **estrutura da consulta** de cada painel, a partir da fato:

```sql
SELECT   <dimensões>, <agregação da medida>
FROM     <fato> f
JOIN     <dimensão> d ON d.sk = f.sk_d
WHERE    <filtros nas dimensões>
GROUP BY <dimensões do SELECT>
ORDER BY <medida> DESC
LIMIT    <N>;
```

Para cada consulta, indiquem: **o que entra no `GROUP BY`**, **o que entra no `WHERE`** e **a operação OLAP**.

### 4. ETL e wireframe (5 min)

- **ETL:** em 3 linhas, digam de onde os dados saem no OLTP (Extract), o que precisa ser tratado (Transform) e a ordem de carga (Load).
- **Wireframe:** desenhem **um painel** à mão, com gráficos, filtros e indicador principal.

---

## Entregáveis

1. Modelo estrela com **grão, medidas e dimensões**.
2. **Cinco fichas** de painel.
3. **Estrutura das cinco consultas**.
4. **Resumo do ETL** e **wireframe** de um painel.
5. Lista de **lacunas do modelo OLTP**, se houver.

---

## Checklist

- [ ] O grão da fato está escrito em uma frase.
- [ ] A dimensão tempo permite ver o painel **por mês**.
- [ ] Toda consulta parte da **fato** e usa só as dimensões necessárias.
- [ ] Todo atributo do `SELECT` sem agregação está no `GROUP BY`.
- [ ] Rankings usam `ORDER BY ... DESC` e `LIMIT`.
- [ ] Contagem de voos e de passageiros foi pensada para **não contar em duplicidade**.
- [ ] O ETL carrega **dimensões antes da fato**.

---

