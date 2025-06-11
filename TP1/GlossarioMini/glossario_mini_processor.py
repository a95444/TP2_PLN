import json
import re
from collections import defaultdict


# Função para verificar se é sigla (todas maiúsculas)
def is_sigla(chave):
    """Verifica se a chave é uma sigla (composta apenas por letras maiúsculas)"""
    return re.fullmatch(r'[A-ZÀ-Ý]{2,}', chave) is not None


# Função principal para atualizar o glossário
def atualizar_glossario(glossario_existente):
    # 1. Processar categorias (Areas.json)
    with open('Areas.json', 'r', encoding='utf-8') as f:
        areas = json.load(f)
        for categoria, definicao in areas.items():
            glossario_existente['CATEGORIAS'][categoria] = {
                "definicao": definicao,
                "subcategorias": []
            }

    # 2. Processar descritores (subcategorias)
    with open('descritores.json', 'r', encoding='utf-8') as f:
        descritores = json.load(f)
        for categoria, subcategorias in descritores.items():
            if categoria in glossario_existente['CATEGORIAS']:
                # Limpar subcategorias (remover quebras de linha e espaços extras)
                subcategorias_limpas = [s.strip() for s in subcategorias if s.strip()]
                glossario_existente['CATEGORIAS'][categoria]['subcategorias'] = subcategorias_limpas

    # 3. Processar siglas
    with open('siglas.json', 'r', encoding='utf-8') as f:
        siglas = json.load(f)
        for sigla, definicao in siglas.items():
            sigla_limpa = sigla.strip()
            if is_sigla(sigla_limpa):
                glossario_existente['SIGLAS'][sigla_limpa] = definicao.strip()
            else:
                glossario_existente['ABREVS'][sigla_limpa] = definicao.strip()

    # 4. Processar conceitos
    with open('conceitos.json', 'r', encoding='utf-8') as f:
        conceitos = json.load(f)
        for termo, dados in conceitos.items():
            termo_limpo = termo.strip()

            # Se o conceito já existe, atualizar campos
            if termo_limpo in glossario_existente['CONCEITOS']:
                conceito = glossario_existente['CONCEITOS'][termo_limpo]

                # Adicionar novas categorias de área
                if 'Categoria' in dados:
                    novas_categorias = [c.strip() for c in dados['Categoria'] if c.strip()]
                    for cat in novas_categorias:
                        if cat not in conceito['categoria_area']:
                            conceito['categoria_area'].append(cat)

                # Adicionar nova definição com fonte
                if 'Descrição' in dados and dados['Descrição'].strip():
                    nova_definicao = [dados['Descrição'].strip(), "Glossario Ministerio da Saude"]
                    conceito['definicoes'].append(nova_definicao)

            # Se é um novo conceito, criar estrutura completa
            else:
                novo_conceito = {
                    "categoria_lexica": [],
                    "sinonimos": {"pt": [], "es": [], "en": []},
                    "traducoes": {"pt": [], "es": [], "en": []},
                    "CAS": None,
                    "categoria_area": [c.strip() for c in dados.get('Categoria', []) if c.strip()],
                    "definicoes": [
                        [dados['Descrição'].strip(), "Glossario Ministerio da Saude"]] if 'Descrição' in dados else [],
                    "sigla": None,
                    "info_enc": None,
                    "artigos": []
                }
                glossario_existente['CONCEITOS'][termo_limpo] = novo_conceito

    return glossario_existente


# Carregar o JSON existente
try:
    with open('../GlossarioNeo/glossario_final.json', 'r', encoding='utf-8') as f:
        glossario_final = json.load(f)
except FileNotFoundError:
    # Caso o arquivo não exista, criar estrutura vazia
    glossario_final = {
        "SIGLAS": {},
        "ABREVS": {},
        "CONCEITOS": {},
        "CATEGORIAS": {},
        "ANEXOS": []
    }

# Atualizar o glossário com novos dados
glossario_atualizado = atualizar_glossario(glossario_final)

# Salvar o resultado final
with open('glossario_final_atualizado.json', 'w', encoding='utf-8') as outfile:
    json.dump(glossario_atualizado, outfile, ensure_ascii=False, indent=2)

print("Glossário atualizado com sucesso! Arquivo salvo como 'glossario_final_atualizado.json'")