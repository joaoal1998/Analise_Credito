import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier


def one_hot_encode(data, label):

    data_unique = pd.read_csv('clientes_treinamento.csv', sep=';')
    unique_values = list(set(data_unique[f'{label}']))

    value_to_index = {value: i for i, value in enumerate(unique_values)}

    one_hot_matrix = []
    for item in data:
        one_hot_vector = [0] * len(unique_values)

        index = value_to_index[item]
        one_hot_vector[index] = 1

        one_hot_matrix.append(one_hot_vector)

    return one_hot_matrix, unique_values


def tratar_dados(data):

    data.dropna(axis=0, inplace=True)
    data.reset_index(inplace=True)

    data = data.drop(data[data['idade_pessoa'] > 80].index, axis=0)
    data = data.drop(data[data['tempo_emprego'] > 60].index, axis=0)

    data['grupo_idade'] = pd.cut(data['idade_pessoa'],
                                 bins=[20, 26, 36, 46, 56, 66],
                                 labels=['20-25', '26-35', '36-45', '46-55', '56-65'])
    data['grupo_renda'] = pd.cut(data['renda_pessoa'],
                                 bins=[0, 25000, 50000, 75000,
                                       100000, float('inf')],
                                 labels=['baixo', 'baixo-medio', 'medio', 'alto-medio', 'alto'])
    data['grupo_valor_emprestimo'] = pd.cut(data['valor_emprestimo'],
                                            bins=[0, 5000, 10000,
                                                  15000, float('inf')],
                                            labels=['pequeno', 'medio', 'grande', 'muito grande'])

    data = data.drop(['index'], axis=1)
    data.reset_index(inplace=True)
    data = data.drop(['index'], axis=1)

    def criar_colunas(categories, one_hot_result):
        for j in range(len(categories)):
            lista = []
            for i in one_hot_result:
                lista.append(i[j])
            data[f'{categories[j]}'] = lista

    categorias = ['tipo_residencia', 'finalidade_emprestimo',
                  'classificacao_emprestimo', 'historico_inadimplencia']

    for _ in range(len(categorias)):
        one_hot_result, categories = one_hot_encode(
            data[f'{categorias[_]}'], categorias[_])
        criar_colunas(categories, one_hot_result)

    colunas_para_excluir = ['idade_pessoa', 'renda_pessoa', 'grupo_idade',
                            'tipo_residencia', 'finalidade_emprestimo', 'grupo_renda',
                            'classificacao_emprestimo', 'valor_emprestimo', 'historico_inadimplencia', 'grupo_valor_emprestimo']

    data = data.drop(columns=colunas_para_excluir)

    return data


def treinar_modelo():

    data = pd.read_csv('clientes_treinamento.csv', sep=';')
    data = data.drop(columns=['cpf'])

    data = tratar_dados(data)

    X = data.drop(columns=['status_emprestimo'])
    y = data['status_emprestimo']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42)

    modelo = DecisionTreeClassifier(
        random_state=42, max_depth=5, min_samples_split=10)
    modelo.fit(X_train, y_train)

    return modelo


def analisar_credito(modelo, ARQUIVO_PREDICAO):
    
    if os.path.exists(ARQUIVO_PREDICAO):
        df = pd.read_csv(ARQUIVO_PREDICAO, dtype={"cpf": str})
    else:
        print("\nNenhum cliente cadastrado.\n")
        return
    
    if df.empty:
        print("\nNenhum cliente cadastrado.\n")
        return

    chave = input("Informe o CPF (somente números): ").strip()
    resultado = df[df['cpf'] == chave]

    if resultado.empty:
        print("\nCliente não encontrado.\n")
        return
    
    cliente_tratado = tratar_dados(resultado.drop(columns='cpf'))

    predicao = modelo.predict(cliente_tratado)
    resultado = "Crédito Aprovado!" if predicao[0] == 0 else "Crédito Recusado!"
    
    print(f"\n{resultado}")
