import json
import re
from collections import defaultdict


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
                definicoes = definicao if isinstance(definicao, list) else [definicao]

                for d in definicoes:
                    if abrev in glossario_existente['ABREVS']:
                        if d not in glossario_existente['ABREVS'][abrev]:
                            glossario_existente['ABREVS'][abrev].append(d)
                    else:
                        glossario_existente['ABREVS'][abrev] = [d]

    # 2. Processar conceitos multilingues
    with open('./conceitos/limpeza_conceitos_testando.json', 'r', encoding='utf-8') as f:
        conceitos_multilingue = json.load(f)

        for conceito in conceitos_multilingue:
            # Tratar campos que podem ser None
            denominacao_catala = conceito.get('denominacao_catala') or ""
            if denominacao_catala:
                denominacao_catala = denominacao_catala.strip()

            # Obter todas as traduções em português
            traducoes_pt = []
            if 'traducao' in conceito and 'pt' in conceito['traducao']:
                for trad in conceito['traducao']['pt']:
                    if trad:  # Ignorar valores vazios
                        # Limpar a tradução removendo categorias lexicais
                        trad_limpa = re.sub(r'\b(n m|n f|adj|v tr|v intr|etc\.?)\b', '', trad,
                                            flags=re.IGNORECASE).strip()
                        if trad_limpa:
                            traducoes_pt.append(trad_limpa)

            # Determinar chave do conceito (primeira tradução PT ou catalão)
            if traducoes_pt:
                chave_conceito = traducoes_pt[0]
            else:
                chave_conceito = denominacao_catala

            # Se não houver chave válida, pular este conceito
            if not chave_conceito:
                continue

            # Verificar se o conceito já existe
            conceito_existente = glossario_existente['CONCEITOS'].get(chave_conceito)

            if conceito_existente:
                print(f"Atualizando conceito existente: {chave_conceito}")

                # A. Adicionar sinônimos em português (demais traduções)
                if len(traducoes_pt) > 1:
                    for sinonimo_pt in traducoes_pt[1:]:
                        if sinonimo_pt and sinonimo_pt not in conceito_existente['sinonimos']['pt']:
                            conceito_existente['sinonimos']['pt'].append(sinonimo_pt)

                # B. Adicionar denominação catalã como tradução
                if denominacao_catala:
                    if 'ca' not in conceito_existente['traducoes']:
                        conceito_existente['traducoes']['ca'] = []
                    if denominacao_catala not in conceito_existente['traducoes']['ca']:
                        conceito_existente['traducoes']['ca'].append(denominacao_catala)

                # C. Adicionar sinônimos em catalão
                sinonimos_ca = conceito.get('sinonimos_complementares', [])
                if sinonimos_ca:
                    for sinonimo_ca in sinonimos_ca:
                        if sinonimo_ca:
                            sinonimo_ca = sinonimo_ca.strip()
                            if sinonimo_ca:
                                if 'ca' not in conceito_existente['sinonimos']:
                                    conceito_existente['sinonimos']['ca'] = []
                                if sinonimo_ca not in conceito_existente['sinonimos']['ca']:
                                    conceito_existente['sinonimos']['ca'].append(sinonimo_ca)

                # D. Adicionar outras traduções (exceto português)
                if 'traducao' in conceito:
                    for lingua, trad_list in conceito['traducao'].items():
                        if lingua == 'pt':
                            continue

                        if trad_list:
                            for trad in trad_list:
                                if trad:
                                    trad_limpa = re.sub(r'\b(n m|n f|adj|v tr|v intr|etc\.?)\b', '', trad,
                                                        flags=re.IGNORECASE).strip()
                                    if trad_limpa:
                                        if lingua not in conceito_existente['traducoes']:
                                            conceito_existente['traducoes'][lingua] = []
                                        if trad_limpa not in conceito_existente['traducoes'][lingua]:
                                            conceito_existente['traducoes'][lingua].append(trad_limpa)

                # E. Adicionar outros campos
                if conceito.get('cas') and not conceito_existente['CAS']:
                    conceito_existente['CAS'] = conceito['cas']

                if conceito.get('area_tematica'):
                    area = conceito['area_tematica'].strip()
                    if area and area not in conceito_existente['categoria_area']:
                        conceito_existente['categoria_area'].append(area)

                if conceito.get('definicao'):
                    definicao = conceito['definicao'].strip()
                    if definicao:
                        nova_def = [definicao, "Dicionario Multilingue"]
                        if nova_def not in conceito_existente['definicoes']:
                            conceito_existente['definicoes'].append(nova_def)

                if conceito.get('nota'):
                    notas = [nota.strip() for nota in conceito['nota'] if nota.strip()]
                    if notas:
                        nota_texto = " ".join(notas)
                        if conceito_existente['info_enc']:
                            conceito_existente['info_enc'] += "\n" + nota_texto
                        else:
                            conceito_existente['info_enc'] = nota_texto

            else:
                # Criar NOVO conceito
                novo_conceito = {
                    "categoria_lexica": [],
                    "sinonimos": defaultdict(list),
                    "traducoes": defaultdict(list),
                    "CAS": conceito.get('cas'),
                    "categoria_area": [],
                    "definicoes": [],
                    "sigla": None,
                    "info_enc": None,
                    "artigos": []
                }

                # Preencher campos básicos
                if conceito.get('area_tematica'):
                    area = conceito['area_tematica'].strip()
                    if area:
                        novo_conceito['categoria_area'].append(area)

                if conceito.get('definicao'):
                    definicao = conceito['definicao'].strip()
                    if definicao:
                        novo_conceito['definicoes'].append([definicao, "Dicionario Multilingue"])

                if conceito.get('nota'):
                    notas = [nota.strip() for nota in conceito['nota'] if nota.strip()]
                    if notas:
                        novo_conceito['info_enc'] = " ".join(notas)

                # A. Adicionar sinônimos em português (demais traduções)
                if len(traducoes_pt) > 1:
                    for sinonimo_pt in traducoes_pt[1:]:
                        if sinonimo_pt:
                            novo_conceito['sinonimos']['pt'].append(sinonimo_pt)

                # B. Adicionar denominação catalã como tradução
                if denominacao_catala:
                    novo_conceito['traducoes']['ca'] = [denominacao_catala]

                # C. Adicionar sinônimos em catalão
                sinonimos_ca = conceito.get('sinonimos_complementares', [])
                if sinonimos_ca:
                    for sinonimo_ca in sinonimos_ca:
                        if sinonimo_ca:
                            sinonimo_ca = sinonimo_ca.strip()
                            if sinonimo_ca:
                                novo_conceito['sinonimos']['ca'].append(sinonimo_ca)

                # D. Adicionar outras traduções (exceto português)
                if 'traducao' in conceito:
                    for lingua, trad_list in conceito['traducao'].items():
                        if lingua == 'pt':
                            continue

                        if trad_list:
                            for trad in trad_list:
                                if trad:
                                    trad_limpa = re.sub(r'\b(n m|n f|adj|v tr|v intr|etc\.?)\b', '', trad,
                                                        flags=re.IGNORECASE).strip()
                                    if trad_limpa:
                                        novo_conceito['traducoes'][lingua].append(trad_limpa)

                # Adicionar ao glossário
                glossario_existente['CONCEITOS'][chave_conceito] = novo_conceito

    return glossario_existente


# Carregar o JSON existente
try:
    with open('../GlossarioMini/glossario_final_atualizado.json', 'r', encoding='utf-8') as f:
        glossario_final = json.load(f)
except FileNotFoundError:
    print("Erro: Arquivo glossario_final_atualizado.json não encontrado")
    exit()

# Atualizar com dados multilingues
glossario_atualizado = adicionar_multilingue(glossario_final)

# Salvar o resultado final
with open('glossario_final_completo.json', 'w', encoding='utf-8') as outfile:
    json.dump(glossario_atualizado, outfile, ensure_ascii=False, indent=2)

print("Processo completo! Glossário final salvo como 'glossario_final_completo.json'")