# Atividade Prática — Relacionamento de Entidades utilizando Arquivos

## Objetivo

Desenvolver um pequeno sistema acadêmico utilizando **Python e arquivos**, sem utilizar banco de dados.

O objetivo é compreender como diferentes entidades podem ser armazenadas em arquivos separados e como seus dados podem ser relacionados.

---

## Contexto

Você já possui um sistema de cadastro de alunos. Agora, será necessário armazenar também as notas dos alunos em diferentes disciplinas.

O desafio é permitir consultas como:

> Qual nota João tirou em Banco de Dados?

Para responder a essa pergunta, o programa deverá relacionar as informações de dois arquivos diferentes.

---

## Arquivo de alunos

Crie e utilize o arquivo:

```text
alunos.txt
```

Cada linha representa um aluno.

Formato:

```text
ID;NOME;TELEFONE;EMAIL
```

Exemplo:

```text
1;João Silva;99999-9999;joao@email.com
2;Maria Santos;98888-8888;maria@email.com
3;Pedro Souza;97777-7777;pedro@email.com
```

O **ID** deve identificar cada aluno de forma única.

---

## Arquivo de notas

Crie e utilize o arquivo:

```text
notas.txt
```

Cada linha representa uma nota de um aluno em determinada disciplina.

Formato:

```text
ID_ALUNO;DISCIPLINA;NOTA
```

Exemplo:

```text
1;Banco de Dados;9.5
1;Programação;8.0
2;Banco de Dados;7.5
2;Programação;9.0
3;Banco de Dados;10.0
```

---

## Relacionamento

Observe os dois arquivos:

```text
ALUNOS

1;João Silva;99999-9999;joao@email.com
2;Maria Santos;98888-8888;maria@email.com
```

```text
NOTAS

1;Banco de Dados;9.5
1;Programação;8.0
2;Banco de Dados;7.5
```

Como descobrir a nota de João em Banco de Dados?

1. Procurar João no arquivo `alunos.txt`;
2. Descobrir seu ID;
3. Procurar no arquivo `notas.txt` registros com esse mesmo ID;
4. Encontrar a disciplina desejada;
5. Exibir a nota.

Nesse exemplo, o campo **ID_ALUNO** permite relacionar as duas entidades.

---

# Funcionalidades obrigatórias

## 1. Cadastrar aluno

Cadastrar um novo aluno contendo:

- ID;
- Nome;
- Telefone;
- E-mail.

## 2. Listar alunos

Exibir todos os alunos cadastrados.

## 3. Buscar aluno

Permitir localizar um aluno pelo nome.

## 4. Cadastrar nota

Cadastrar uma nota contendo:

- ID do aluno;
- Disciplina;
- Nota.

O sistema deve verificar se o aluno existe antes de cadastrar sua nota.

## 5. Consultar nota

Permitir consultas como:

```text
Digite o nome do aluno: João Silva
Digite a disciplina: Banco de Dados
```

Resultado esperado:

```text
Aluno: João Silva
Disciplina: Banco de Dados
Nota: 9.5
```

---

# Desafios extras

Após concluir as funcionalidades obrigatórias, implemente:

- Listar todas as notas de um aluno;
- Calcular a média de um aluno;
- Editar uma nota;
- Excluir uma nota;
- Impedir IDs de alunos duplicados;
- Impedir notas para alunos inexistentes;
- Buscar alunos por disciplina;
- Buscar alunos com nota acima de determinado valor.

---

# Regras

- Não utilizar MySQL, PostgreSQL, SQLite ou qualquer outro SGBD;
- Utilizar apenas arquivos;
- Os dados devem continuar existindo após o encerramento do programa;
- Utilizar Python;
- Os arquivos devem ser lidos e atualizados pelo próprio programa.

---

# Reflexão

Ao final da atividade, responda:

> Como o programa consegue identificar a qual aluno uma determinada nota pertence?

Reflita também:

- Por que utilizamos um identificador único?
- O que aconteceria se utilizássemos apenas o nome do aluno?
- Como garantir que uma nota pertença a um aluno existente?
- Quais dificuldades aparecem quando as informações estão distribuídas em diferentes arquivos?
