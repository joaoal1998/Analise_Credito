import pandas as pd
import os
from modelo import analisar_credito, treinar_modelo
import warnings
warnings.filterwarnings('ignore')


ARQUIVO_TREINAMENTO = "clientes_treinamento.csv"
ARQUIVO_PREDICAO = "clientes_predicao.csv"
CAMPOS = ['cpf', 'idade_pessoa', 'renda_pessoa', 'tipo_residencia', 'tempo_emprego',
          'finalidade_emprestimo', 'classificacao_emprestimo', 'valor_emprestimo',
          'taxa_juros_emprestimo', 'percentual_renda_comprometida', 'historico_inadimplencia',
          'tempo_historico_credito']


def carregar_clientes(arquivo):

    if os.path.exists(arquivo):
        return pd.read_csv(arquivo, sep=",", dtype={"cpf": str})
    else:
        return pd.DataFrame(columns=CAMPOS)


def salvar_clientes(df, arquivo):
    df.to_csv(arquivo, sep=",", index=False)


def cadastrar_cliente():
    df = carregar_clientes(ARQUIVO_PREDICAO)

    cpf_cliente = input("CPF (somente números): ").strip()

    if cpf_cliente in df["cpf"].values:
        print("\nErro: CPF já cadastrado.\n")
        return

    cliente = {campo: input(f"{campo.replace('_', ' ')}: ").upper() for campo in CAMPOS[1:]}

    cliente["cpf"] = cpf_cliente

    df = pd.concat([df, pd.DataFrame([cliente])], ignore_index=True)
    salvar_clientes(df, ARQUIVO_PREDICAO)

    print("\nCliente cadastrado com sucesso!\n")


def cadastrar_varios_clientes(arquivo_csv):

    if not os.path.exists(arquivo_csv):
        print("\nErro: Arquivo não encontrado.\n")
        return

    df_novos = pd.read_csv(arquivo_csv, sep=";", dtype={"cpf": str})

    df_existente = carregar_clientes(ARQUIVO_PREDICAO)

    df_novos = df_novos[~df_novos["cpf"].isin(df_existente["cpf"])]

    if df_novos.empty:
        print("\nNenhum cliente novo para adicionar.\n")
        return

    df_atualizado = pd.concat([df_existente, df_novos], ignore_index=True)
    salvar_clientes(df_atualizado, ARQUIVO_PREDICAO)

    print(f"\n{len(df_novos)} clientes cadastrados com sucesso!\n")


def alterar_cliente():
    df = carregar_clientes(ARQUIVO_PREDICAO)

    if df.empty:
        print("\nNenhum cliente cadastrado.\n")
        return

    cpf_cliente = input("Digite o CPF do cliente que deseja alterar: ").strip()
    indice = df[df["cpf"] == cpf_cliente].index

    if indice.empty:
        print("\nCliente não encontrado.\n")
        return

    print("\nDigite os novos dados (deixe em branco para manter o valor atual):\n")

    for campo in CAMPOS[1:]:
        valor = input(f"{campo.replace('_', ' ')} ({df.loc[indice, campo].values[0]}): ").upper()
        if valor:
            df.loc[indice, campo] = valor

    salvar_clientes(df, ARQUIVO_PREDICAO)
    print("\nDados atualizados com sucesso!\n")


def pesquisar_cliente():
    df = carregar_clientes(ARQUIVO_PREDICAO)

    if df.empty:
        print("\nNenhum cliente cadastrado.\n")
        return

    cpf_cliente = input("Informe o CPF (somente números): ").strip()
    resultado = df[df['cpf'] == cpf_cliente]

    if resultado.empty:
        print("\nCliente não encontrado.\n")
    else:
        print(F"\nCliente encontrado:\n{resultado.iloc[0].T}")


def menu():
    
    modelo = treinar_modelo()
    
    while True:
        print("\n=== Sistema de Análise de Crédito ===")
        print("1. Cadastrar Novo Cliente")
        print("2. Importar Clientes")
        print("3. Pesquisar Cliente")
        print("4. Alterar Dados do Cliente")
        print("5. Analisar crédito")
        print("6. Sair")

        opcao = input("Escolha uma opção: ")

        match opcao:

            case '1':
                cadastrar_cliente()
            case '2':
                arquivo_csv = input('Informe o caminho do arquivo: ')
                cadastrar_varios_clientes(arquivo_csv)
            case '3':
                pesquisar_cliente()
            case '4':
                alterar_cliente()
            case '5':
                analisar_credito(modelo, ARQUIVO_PREDICAO)
            case '6':
                print('\nSistema encerrado!')
                break

            case _:
                print("\nOpção inválida. Tente novamente.\n")


menu()
