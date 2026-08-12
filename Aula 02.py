ARQUIVO_ALUNOS = "alunos.txt"
ARQUIVO_NOTAS = "notas.txt"


def cadastrar_aluno():
    print("\n--- CADASTRAR ALUNO ---")

    id_aluno = input("ID: ")
    nome = input("Nome: ")
    telefone = input("Telefone: ")
    email = input("E-mail: ")

    with open(ARQUIVO_ALUNOS, "a", encoding="utf-8") as arquivo:
        arquivo.write(
            f"{id_aluno};{nome};{telefone};{email}\n"
        )

    print("Aluno cadastrado com sucesso!")


def listar_alunos():
    print("\n--- LISTA DE ALUNOS ---")

    try:
        with open(ARQUIVO_ALUNOS, "r", encoding="utf-8") as arquivo:

            for linha in arquivo:
                dados = linha.strip().split(";")

                print(f"ID: {dados[0]}")
                print(f"Nome: {dados[1]}")
                print(f"Telefone: {dados[2]}")
                print(f"E-mail: {dados[3]}")
                print("-" * 30)

    except FileNotFoundError:
        print("Nenhum aluno cadastrado.")


def buscar_aluno_por_nome(nome_busca):

    try:
        with open(ARQUIVO_ALUNOS, "r", encoding="utf-8") as arquivo:

            for linha in arquivo:
                dados = linha.strip().split(";")

                id_aluno = dados[0]
                nome = dados[1]

                if nome.lower() == nome_busca.lower():
                    return id_aluno, nome

    except FileNotFoundError:
        return None

    return None


def cadastrar_nota():
    print("\n--- CADASTRAR NOTA ---")

    nome_aluno = input("Nome do aluno: ")

    aluno = buscar_aluno_por_nome(nome_aluno)

    if aluno is None:
        print("Aluno não encontrado.")
        return

    id_aluno = aluno[0]

    disciplina = input("Disciplina: ")
    nota = input("Nota: ")

    with open(ARQUIVO_NOTAS, "a", encoding="utf-8") as arquivo:
        arquivo.write(
            f"{id_aluno};{disciplina};{nota}\n"
        )

    print("Nota cadastrada com sucesso!")


def consultar_nota():
    print("\n--- CONSULTAR NOTA ---")

    nome_aluno = input("Nome do aluno: ")
    disciplina_busca = input("Disciplina: ")

    # TODO:
    # 1. Buscar o aluno pelo nome.
    # 2. Obter o ID do aluno.
    # 3. Abrir o arquivo notas.txt.
    # 4. Procurar uma nota com o ID do aluno.
    # 5. Verificar se a disciplina corresponde.
    # 6. Exibir a nota encontrada.

    print("Funcionalidade a ser implementada.")


def listar_notas_aluno():
    print("\n--- LISTAR NOTAS DO ALUNO ---")

    # TODO:
    # Solicitar o nome do aluno.
    # Descobrir seu ID.
    # Procurar todas as notas relacionadas a esse ID.

    print("Funcionalidade a ser implementada.")


def calcular_media():
    print("\n--- CALCULAR MÉDIA ---")

    # TODO:
    # Solicitar o nome do aluno.
    # Buscar todas as notas relacionadas ao seu ID.
    # Calcular e exibir a média.

    print("Funcionalidade a ser implementada.")


def menu():

    while True:

        print("\n==============================")
        print(" SISTEMA ACADÊMICO")
        print("==============================")
        print("1 - Cadastrar aluno")
        print("2 - Listar alunos")
        print("3 - Cadastrar nota")
        print("4 - Consultar nota")
        print("5 - Listar notas de um aluno")
        print("6 - Calcular média")
        print("0 - Sair")

        opcao = input("\nEscolha uma opção: ")

        if opcao == "1":
            cadastrar_aluno()

        elif opcao == "2":
            listar_alunos()

        elif opcao == "3":
            cadastrar_nota()

        elif opcao == "4":
            consultar_nota()

        elif opcao == "5":
            listar_notas_aluno()

        elif opcao == "6":
            calcular_media()

        elif opcao == "0":
            print("Sistema encerrado.")
            break

        else:
            print("Opção inválida!")


menu()
