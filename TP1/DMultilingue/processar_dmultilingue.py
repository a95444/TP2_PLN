import json
import re
from collections import defaultdict


# Função para verificar se é sigla
def is_sigla(chave):
    return re.fullmatch(r'[A-ZÀ-Ý]{2,}', chave) is not None


# Função para extrair termos de traduções
def extrair_termos(traducao_str):
    """Extrai os termos de uma string de tradução, removendo categorias lexicais"""
    termos = []
    for item in traducao_str.split(','):
        # Remover categorias lexicais (n m, adj, etc.)
        termo = re.sub(r'\b(n m|n f|adj|v tr|v intr|etc\.?)\b', '', item, flags=re.IGNORECASE).strip()
        # Remover colchetes e conteúdo dentro
        termo = re.sub(r'\[.*?\]', '', termo).strip()
        if termo:
            termos.append(termo)
    return termos


# Função principal para adicionar dados multilingues
def adicionar_multilingue(glossario_existente):
    # 1. Processar abreviações multilingues
    with open('./Abreviaturas/Abreviacoes.json', 'r', encoding='utf-8') as f:
        abreviacoes = json.load(f)

        # Converter ABREVS para dicionário de listas se necessário
        if glossario_existente['ABREVS'] and isinstance(next(iter(glossario_existente['ABREVS'].values())), str):
            glossario_existente['ABREVS'] = {k: [v] for k, v in glossario_existente['ABREVS'].items()}

        for categoria, conteudo in abreviacoes.items():
            for abrev, definicao in conteudo.items():
                # Processar definições que são listas
                if isinstance(definicao, list):
                    for d in definicao:
                        if abrev in glossario_existente['ABREVS']:
                            if d not in glossario_existente['ABREVS'][abrev]:
                                glossario_existente['ABREVS'][abrev].append(d)
                        else:
                            glossario_existente['ABREVS'][abrev] = [d]
                else:
                    if abrev in glossario_existente['ABREVS']:
                        if definicao not in glossario_existente['ABREVS'][abrev]:
                            glossario_existente['ABREVS'][abrev].append(definicao)
                    else:
                        glossario_existente['ABREVS'][abrev] = [definicao]

    # 2. Processar conceitos multilingues
    with open('./conceitos/limpeza_conceitos_testando.json', 'r', encoding='utf-8') as f:
        conceitos_multilingue = json.load(f)

        for conceito in conceitos_multilingue:
            denominacao_catala = conceito['denominacao_catala']

            # Obter denominação em português (se existir)
            denominacao_pt = None
            if 'pt' in conceito.get('traducao', {}):
                # Usar a primeira tradução em português como denominação principal
                primeira_trad = conceito['traducao']['pt'][0]
                termos_pt = extrair_termos(primeira_trad)
                if termos_pt:
                    denominacao_pt = termos_pt[0]

            # Se não encontrou tradução para PT, usar catalão como fallback
            chave_conceito = denominacao_pt if denominacao_pt else denominacao_catala

            # Verificar se o conceito já existe
            conceito_existente = glossario_existente['CONCEITOS'].get(chave_conceito)

            if conceito_existente:
                print(f"Atualizando conceito existente: {chave_conceito}")

                # Adicionar traduções
                for lingua, traducoes in conceito.get('traducao', {}).items():
                    # Ignorar português já que é a língua principal
                    if lingua == 'pt':
                        continue

                    # Adicionar cada tradução da língua
                    for trad in traducoes:
                        termos = extrair_termos(trad)
                        for termo in termos:
                            if termo not in conceito_existente['traducoes'].get(lingua, []):
                                conceito_existente['traducoes'].setdefault(lingua, []).append(termo)

                # Adicionar sinônimos em catalão
                sinonimos_ca = conceito.get('sinonimos_complementares', [])
                for sinonimo in sinonimos_ca:
                    if sinonimo and sinonimo not in conceito_existente['sinonimos'].get('ca', []):
                        conceito_existente['sinonimos'].setdefault('ca', []).append(sinonimo)

                # Adicionar CAS se não existir
                if conceito.get('cas') and not conceito_existente['CAS']:
                    conceito_existente['CAS'] = conceito['cas']

                # Adicionar área temática
                area_tematica = conceito.get('area_tematica')
                if area_tematica and area_tematica not in conceito_existente['categoria_area']:
                    conceito_existente['categoria_area'].append(area_tematica)

                # Adicionar definição
                definicao = conceito.get('definicao')
                if definicao:
                    nova_def = [definicao, "Dicionario Multilingue"]
                    if nova_def not in conceito_existente['definicoes']:
                        conceito_existente['definicoes'].append(nova_def)

                # Adicionar notas como informação enciclopédica
                notas = conceito.get('nota', [])
                if notas:
                    info_enc = " ".join(notas)
                    if conceito_existente['info_enc']:
                        conceito_existente['info_enc'] += "\n" + info_enc
                    else:
                        conceito_existente['info_enc'] = info_enc

            else:
                # Criar novo conceito
                novo_conceito = {
                    "categoria_lexica": [],
                    "sinonimos": defaultdict(list),
                    "traducoes": defaultdict(list),
                    "CAS": conceito.get('cas'),
                    "categoria_area": [conceito['area_tematica']] if conceito.get('area_tematica') else [],
                    "definicoes": [[conceito['definicao'], "Dicionario Multilingue"]] if conceito.get(
                        'definicao') else [],
                    "sigla": None,
                    "info_enc": " ".join(conceito.get('nota', [])) if conceito.get('nota') else None,
                    "artigos": []
                }

                # Adicionar traduções
                for lingua, traducoes in conceito.get('traducao', {}).items():
                    for trad in traducoes:
                        termos = extrair_termos(trad)
                        for termo in termos:
                            if lingua == 'pt' and not denominacao_pt:
                                # Usar primeira tradução PT como denominação se não tivermos
                                denominacao_pt = termo
                                chave_conceito = denominacao_pt
                            elif termo not in novo_conceito['traducoes'][lingua]:
                                novo_conceito['traducoes'][lingua].append(termo)

                # Adicionar sinônimos em catalão
                for sinonimo in conceito.get('sinonimos_complementares', []):
                    if sinonimo:
                        novo_conceito['sinonimos']['ca'].append(sinonimo)

                # Adicionar ao glossário
                glossario_existente['CONCEITOS'][chave_conceito] = novo_conceito

    return glossario_existente


# Carregar o JSON existente
try:
    with open('../GlossarioMini/glossario_final_atualizado.json', 'r', encoding='utf-8') as f:
        glossario_final = json.load(f) #
except FileNotFoundError:
    print("Erro: Arquivo glossario_final_atualizado.json não encontrado")
    exit()

# Atualizar com dados multilingues
glossario_atualizado = adicionar_multilingue(glossario_final)

# Salvar o resultado final
with open('glossario_final_completo.json', 'w', encoding='utf-8') as outfile:
    json.dump(glossario_atualizado, outfile, ensure_ascii=False, indent=2)

print("Processo completo! Glossário final salvo como 'glossario_final_completo.json'")