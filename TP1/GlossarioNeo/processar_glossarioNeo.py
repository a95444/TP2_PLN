import json
from collections import defaultdict
import os
import re


print(os.getcwd())

# Estrutura final inicial
final_json = {
    "SIGLAS": {},
    "ABREVS": {},
    "CONCEITOS": {},
    "CATEGORIAS": {},
    "ANEXOS": []
}

def is_sigla(chave):
    """Verifica se a chave é uma sigla (composta apenas por letras maiúsculas)"""
    return re.fullmatch(r'[A-ZÀ-Ý]{2,}', chave) is not None  # Pelo menos 2 caracteres maiúsculos

# Modificar a função processar_abreviaturas
def processar_abreviaturas(arquivo):
    with open(arquivo, 'r', encoding='utf-8') as f:
        dados = json.load(f)
        for chave, valor in dados.items():
            if is_sigla(chave):
                final_json['SIGLAS'][chave] = valor  # Vai para SIGLAS
            else:
                final_json['ABREVS'][chave] = valor  # Vai para ABREVS


# Passo 2: Processar glossário
def processar_glossario(arquivo):
    with open(arquivo, 'r', encoding='utf-8') as f:
        glossario = json.load(f)

        for termo in glossario:
            nome = termo['Termo']

            # Mapear traduções
            traducoes = {
                "en": [termo['Termo ing']] if termo['Termo ing'] else [],
                "es": [termo['Termo esp']] if termo['Termo esp'] else []
            }

            # Adicionar sigla ao dicionário de SIGLAS se existir
            # Modificação na adição de siglas
            if termo['Sigla']:
                sigla = termo['Sigla'].strip()
                if is_sigla(sigla):  # Verificar se é sigla válida
                    final_json['SIGLAS'][sigla] = nome
                else:
                    # Se não for sigla, tratar como abreviatura
                    final_json['ABREVS'][sigla] = nome

            # Construir objeto do conceito
            conceito = {
                "categoria_lexica": [termo['Substantivo']] if termo['Substantivo'] else [],
                "sinonimos": {"pt": [], "es": [], "en": []},  # Inicialmente vazio
                "traducoes": traducoes,
                "CAS": None,  # Não disponível nos dados
                "categoria_area": [],  # Inicialmente vazio
                "definicoes": [[termo['Descricao'], "GlossarioNeo"]],
                "sigla": termo['Sigla'] if termo['Sigla'] else None,
                "info_enc": termo['Informacao Enciclopedia'],
                "artigos": termo['nr_artigos']
            }

            final_json['CONCEITOS'][nome] = conceito


# Passo 3: Processar anexos
def processar_anexos(arquivo):
    with open(arquivo, 'r', encoding='utf-8') as f:
        final_json['ANEXOS'] = json.load(f)


# Passo 4: Processar todos os arquivos
def processar_todos_arquivos():
    # Processar abreviaturas
    processar_abreviaturas('./AbreviaturasSiglas/Abreviaturas_page10.json')
    processar_abreviaturas('./AbreviaturasSiglas/Abreviaturas_page86.json')

    # Mover 'et al.' para ABREVS e remover de SIGLAS
    if 'et al.' in final_json['ABREVS']:
        final_json['ABREVS']['et al.'] = final_json['ABREVS']['et al.']

    # Processar glossário
    processar_glossario('./Glossario/glossario.json')

    # Processar anexos
    processar_anexos('./Anexos/anexos_pesquisa.json')

    # Salvar resultado final
    with open('glossario_final.json', 'w', encoding='utf-8') as outfile:
        json.dump(final_json, outfile, ensure_ascii=False, indent=2)


# Executar o processamento
if __name__ == "__main__":
    processar_todos_arquivos()
    print("Processamento concluído! JSON final salvo como 'glossario_final.json'")