import re
from datetime import datetime
import json
import os
from pathlib import Path
import time

# Configuração do diretório de dados
DATA_DIR = Path.home() / "dados_transporte_rural"
PROPRIEDADES_FILE = DATA_DIR / "propriedades.json"
VEICULOS_FILE = DATA_DIR / "veiculos.json"
PRODUTOS_FILE = DATA_DIR / "produtos.json"
CALCULOS_FILE = DATA_DIR / "calculos.json"

# Garantir que o diretório de dados existe
def setup_data_directory():
    """Cria o diretório de dados e arquivos JSON caso não existam"""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Inicializar os arquivos JSON se não existirem
    for file_path, initial_data in [
        (PROPRIEDADES_FILE, []),
        (VEICULOS_FILE, []),
        (PRODUTOS_FILE, []),
        (CALCULOS_FILE, [])
    ]:
        if not file_path.exists():
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(initial_data, f, ensure_ascii=False, indent=2)
    
    print(f"Arquivos de dados serão armazenados em: {DATA_DIR}")

def carregar_dados(arquivo):
    """Carrega dados de um arquivo JSON com verificação de tipo"""
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            if not isinstance(dados, list):  # Verifica se é uma lista
                print(f"Aviso: Dados em {arquivo} não estão no formato esperado. Inicializando como lista vazia.")
                return []
            return dados
    except json.JSONDecodeError:
        return []
    except Exception as e:
        print(f"Erro ao carregar {arquivo}: {e}")
        return []

def salvar_dados(dados, arquivo):
    """Salva dados em um arquivo JSON"""
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

def gerar_id(lista):
    """Gera um novo ID para um item baseado no maior ID existente + 1"""
    if not lista:
        return 1
    return max(item.get('id', 0) for item in lista) + 1

def limpar_localizacao(localizacao):
    return re.sub(r'\(.*?\)', '', localizacao).strip()[:128]

def input_float(msg):
    while True:
        try:
            valor = input(msg).strip().replace(',', '.')
            if valor == '':
                print("Este campo não pode ser vazio.")
                continue
            return float(valor)
        except ValueError:
            print("Valor inválido. Insira um número válido com ponto (.) para decimais.")

def input_nao_vazio(msg):
    while True:
        valor = input(msg).strip()
        if valor == '':
            print("Este campo não pode ser vazio.")
        else:
            return valor

def input_id(msg):
    while True:
        try:
            id_val = int(input(msg))
            if id_val <= 0:
                print("ID deve ser um número positivo.")
                continue
            return id_val
        except ValueError:
            print("Por favor, digite um número inteiro válido.")

def menu():
    while True:
        print("\n--- Simulador de Logística de Transporte Rural ---")
        print("1. Gerenciar Propriedades Rurais")
        print("2. Gerenciar Veículos de Transporte")
        print("3. Gerenciar Produtos Agrícolas")
        print("4. Realizar Cálculo de Transporte")
        print("5. Listar Cálculos Realizados")
        print("6. Exportar Todos os Dados")
        print("0. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            menu_propriedades()
        elif opcao == '2':
            menu_veiculos()
        elif opcao == '3':
            menu_produtos()
        elif opcao == '4':
            calcular_transporte()
        elif opcao == '5':
            listar_calculos()
        elif opcao == '6':
            exportar_dados()
        elif opcao == '0':
            break
        else:
            print("Opção inválida.")

def menu_propriedades():
    while True:
        print("\n--- Propriedades Rurais ---")
        print("1. Adicionar")
        print("2. Alterar")
        print("3. Remover")
        print("4. Listar")
        print("0. Voltar")
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            adicionar_propriedade()
        elif opcao == '2':
            alterar_propriedade()
        elif opcao == '3':
            remover_propriedade()
        elif opcao == '4':
            listar_propriedades()
        elif opcao == '0':
            break

def adicionar_propriedade():
    nome = input_nao_vazio("Nome da propriedade: ")
    localizacao = limpar_localizacao(input_nao_vazio("Localização: "))
    area_producao = input_float("Área de produção (ha): ")
    distancia = input_float("Distância até o centro de distribuição (km): ")
    
    propriedades = carregar_dados(PROPRIEDADES_FILE)
    nova_propriedade = {
        'id': gerar_id(propriedades),
        'nome': nome,
        'localizacao': localizacao,
        'area_producao': area_producao,
        'distancia': distancia,
        'data_cadastro': datetime.now().strftime("%d/%m/%Y %H:%M")
    }
    
    propriedades.append(nova_propriedade)
    salvar_dados(propriedades, PROPRIEDADES_FILE)
    print("Propriedade adicionada com sucesso!")

def alterar_propriedade():
    propriedades = listar_propriedades()
    if not propriedades:
        return
    
    id_prop = input_id("Escolha o ID da propriedade para alterar: ")
    
    # Buscar a propriedade pelo ID
    for i, prop in enumerate(propriedades):
        if prop['id'] == id_prop:
            nome = input_nao_vazio(f"Novo nome [{prop['nome']}]: ") or prop['nome']
            localizacao = limpar_localizacao(input_nao_vazio(f"Nova localização [{prop['localizacao']}]: ")) or prop['localizacao']
            area_producao = input_float(f"Nova área de produção (ha) [{prop['area_producao']}]: ") or prop['area_producao']
            distancia = input_float(f"Nova distância (km) [{prop['distancia']}]: ") or prop['distancia']
            
            propriedades[i].update({
                'nome': nome,
                'localizacao': localizacao,
                'area_producao': area_producao,
                'distancia': distancia
            })
            
            salvar_dados(propriedades, PROPRIEDADES_FILE)
            print("Propriedade atualizada com sucesso!")
            return
    
    print("Propriedade não encontrada.")

def remover_propriedade():
    propriedades = listar_propriedades()
    if not propriedades:
        return
    
    id_prop = input_id("Escolha o ID da propriedade para remover: ")
    calculos = carregar_dados(CALCULOS_FILE)
    
    # Verificar se existem cálculos associados
    if any(calc['propriedade_id'] == id_prop for calc in calculos):
        print("Não é possível remover. Existem cálculos associados a esta propriedade.")
        return
    
    # Filtrar a lista para manter apenas as propriedades com ID diferente
    nova_lista = [prop for prop in propriedades if prop['id'] != id_prop]
    
    if len(nova_lista) < len(propriedades):
        salvar_dados(nova_lista, PROPRIEDADES_FILE)
        print("Propriedade removida com sucesso!")
    else:
        print("Propriedade não encontrada.")

def listar_propriedades():
    propriedades = carregar_dados(PROPRIEDADES_FILE)
    
    if not propriedades:
        print("Nenhuma propriedade encontrada.")
        return []
    
    print("\n--- Lista de Propriedades ---")
    for prop in propriedades:
        print(f"ID {prop['id']}: {prop['nome']}")
        print(f"  Localização: {prop['localizacao']}")
        print(f"  Área: {prop['area_producao']} ha")
        print(f"  Distância para o próximo centro de distribuição: {prop['distancia']} km")
        print(f"  Data de cadastro: {prop['data_cadastro']}")
    
    return propriedades

def menu_veiculos():
    while True:
        print("\n--- Veículos de Transporte ---")
        print("1. Adicionar")
        print("2. Alterar")
        print("3. Remover")
        print("4. Listar")
        print("0. Voltar")
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            adicionar_veiculo()
        elif opcao == '2':
            alterar_veiculo()
        elif opcao == '3':
            remover_veiculo()
        elif opcao == '4':
            listar_veiculos()
        elif opcao == '0':
            break

def adicionar_veiculo():
    tipo = input_nao_vazio("Tipo de veículo: ")
    capacidade = input_float("Capacidade de carga (kg): ")
    custo_km = input_float("Custo por km (R$): ")
    
    veiculos = carregar_dados(VEICULOS_FILE)
    novo_veiculo = {
        'id': gerar_id(veiculos),
        'tipo': tipo,
        'capacidade': capacidade,
        'custo_km': custo_km,
        'data_cadastro': datetime.now().strftime("%d/%m/%Y %H:%M")
    }
    
    veiculos.append(novo_veiculo)
    salvar_dados(veiculos, VEICULOS_FILE)
    print("Veículo adicionado com sucesso!")

def alterar_veiculo():
    veiculos = listar_veiculos()
    if not veiculos:
        return
    
    id_veic = input_id("Escolha o ID do veículo para alterar: ")
    
    for i, veic in enumerate(veiculos):
        if veic['id'] == id_veic:
            tipo = input_nao_vazio(f"Novo tipo [{veic['tipo']}]: ") or veic['tipo']
            capacidade = input_float(f"Nova capacidade (kg) [{veic['capacidade']}]: ") or veic['capacidade']
            custo_km = input_float(f"Novo custo por km (R$) [{veic['custo_km']}]: ") or veic['custo_km']
            
            veiculos[i].update({
                'tipo': tipo,
                'capacidade': capacidade,
                'custo_km': custo_km
            })
            
            salvar_dados(veiculos, VEICULOS_FILE)
            print("Veículo atualizado com sucesso!")
            return
    
    print("Veículo não encontrado.")

def remover_veiculo():
    veiculos = listar_veiculos()
    if not veiculos:
        return
    
    id_veic = input_id("Escolha o ID do veículo para remover: ")
    calculos = carregar_dados(CALCULOS_FILE)
    
    # Verificar se existem cálculos associados
    if any(calc['veiculo_id'] == id_veic for calc in calculos):
        print("Não é possível remover. Existem cálculos associados a este veículo.")
        return
    
    nova_lista = [veic for veic in veiculos if veic['id'] != id_veic]
    
    if len(nova_lista) < len(veiculos):
        salvar_dados(nova_lista, VEICULOS_FILE)
        print("Veículo removido com sucesso!")
    else:
        print("Veículo não encontrado.")

def listar_veiculos():
    veiculos = carregar_dados(VEICULOS_FILE)
    
    if not veiculos:
        print("Nenhum veículo encontrado.")
        return []
    
    print("\n--- Lista de Veículos ---")
    for veic in veiculos:
        print(f"ID {veic['id']}: {veic['tipo']}")
        print(f"  Capacidade: {veic['capacidade']} kg")
        print(f"  Custo por km: R$ {veic['custo_km']}")
        print(f"  Data de cadastro: {veic['data_cadastro']}")
    
    return veiculos

def menu_produtos():
    while True:
        print("\n--- Produtos Agrícolas ---")
        print("1. Adicionar")
        print("2. Alterar")
        print("3. Remover")
        print("4. Listar")
        print("0. Voltar")
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            adicionar_produto()
        elif opcao == '2':
            alterar_produto()
        elif opcao == '3':
            remover_produto()
        elif opcao == '4':
            listar_produtos()
        elif opcao == '0':
            break

def adicionar_produto():
    nome = input_nao_vazio("Nome do produto: ")
    peso_cesto = input_float("Peso por cesto/unidade (kg): ")
    
    produtos = carregar_dados(PRODUTOS_FILE)
    novo_produto = {
        'id': gerar_id(produtos),
        'nome': nome,
        'peso_cesto': peso_cesto,
        'data_cadastro': datetime.now().strftime("%d/%m/%Y %H:%M")
    }
    
    produtos.append(novo_produto)
    salvar_dados(produtos, PRODUTOS_FILE)
    print("Produto adicionado com sucesso!")

def alterar_produto():
    produtos = listar_produtos()
    if not produtos:
        return
    
    id_prod = input_id("Escolha o ID do produto para alterar: ")
    
    for i, prod in enumerate(produtos):
        if prod['id'] == id_prod:
            nome = input_nao_vazio(f"Novo nome [{prod['nome']}]: ") or prod['nome']
            peso_cesto = input_float(f"Novo peso por cesto/unidade (kg) [{prod['peso_cesto']}]: ") or prod['peso_cesto']
            
            produtos[i].update({
                'nome': nome,
                'peso_cesto': peso_cesto
            })
            
            salvar_dados(produtos, PRODUTOS_FILE)
            print("Produto atualizado com sucesso!")
            return
    
    print("Produto não encontrado.")

def remover_produto():
    produtos = listar_produtos()
    if not produtos:
        return
    
    id_prod = input_id("Escolha o ID do produto para remover: ")
    calculos = carregar_dados(CALCULOS_FILE)
    
    # Verificar se existem cálculos associados
    if any(calc['produto_id'] == id_prod for calc in calculos):
        print("Não é possível remover. Existem cálculos associados a este produto.")
        return
    
    nova_lista = [prod for prod in produtos if prod['id'] != id_prod]
    
    if len(nova_lista) < len(produtos):
        salvar_dados(nova_lista, PRODUTOS_FILE)
        print("Produto removido com sucesso!")
    else:
        print("Produto não encontrado.")

def listar_produtos():
    produtos = carregar_dados(PRODUTOS_FILE)
    
    if not produtos:
        print("Nenhum produto encontrado.")
        return []
    
    print("\n--- Lista de Produtos ---")
    for prod in produtos:
        print(f"ID {prod['id']}: {prod['nome']}")
        print(f"  Peso por cesto/unidade: {prod['peso_cesto']} kg")
        print(f"  Data de cadastro: {prod['data_cadastro']}")
    
    return produtos

def calcular_transporte():
    propriedades = listar_propriedades()
    if not propriedades:
        return
    
    id_prop = input_id("ID da propriedade: ")
    
    # Buscar propriedade
    prop = next((p for p in propriedades if p['id'] == id_prop), None)
    if not prop:
        print("Propriedade não encontrada.")
        return
    
    veiculos = listar_veiculos()
    if not veiculos:
        return
    
    id_veic = input_id("ID do veículo: ")
    
    # Buscar veículo
    veic = next((v for v in veiculos if v['id'] == id_veic), None)
    if not veic:
        print("Veículo não encontrado.")
        return
    
    produtos = listar_produtos()
    if not produtos:
        return
    
    id_prod = input_id("ID do produto: ")
    
    # Buscar produto
    prod = next((p for p in produtos if p['id'] == id_prod), None)
    if not prod:
        print("Produto não encontrado.")
        return
    
    peso_total = input_float("Peso total a ser transportado (kg): ")
    viagens = -(-peso_total // veic['capacidade'])  # Arredondamento para cima
    distancia_total = viagens * 2 * prop['distancia']  # ida e volta

    # Tempo estimado considerando velocidade média de 55km/h, 8h/dia de estrada e 3h de paradas
    velocidade_media = 55
    horas_dia_viagem = 8
    horas_paradas_dia = 3
    km_por_dia = velocidade_media * horas_dia_viagem
    dias_viagem = distancia_total / km_por_dia
    tempo_total_horas = dias_viagem * (horas_dia_viagem + horas_paradas_dia)

    # Custo estimado
    custo_combustivel = veic['custo_km'] * distancia_total
    custo_manutencao = custo_combustivel
    custo_motorista = 2 * 250 * dias_viagem  # 2x salário por dia (R$250/dia)

    custo_total = custo_combustivel + custo_manutencao + custo_motorista

    print("\nNúmero de viagens: {}".format(int(viagens)))
    print("Distância total: {:.2f} km".format(distancia_total))
    print("Velocidade média: 55 km/h | 8h de estrada + 3h de paradas por dia")
    print("Tempo estimado total de transporte: {:.2f} horas (~{:.1f} dias)".format(tempo_total_horas, dias_viagem))
    print("\nCálculo do custo:")
    print("  - Combustível: R$ {:.2f}".format(custo_combustivel))
    print("  - Manutenção (1x combustível): R$ {:.2f}".format(custo_manutencao))
    print("  - Motorista (2x R$250 por dia): R$ {:.2f}".format(custo_motorista))
    print("Custo total estimado: R$ {:.2f}".format(custo_total))

    # Salvar o cálculo
    calculos = carregar_dados(CALCULOS_FILE)
    novo_calculo = {
        'id': gerar_id(calculos),
        'propriedade_id': id_prop,
        'veiculo_id': id_veic,
        'produto_id': id_prod,
        'peso_total': peso_total,
        'viagens': int(viagens),
        'distancia_total': distancia_total,
        'custo_total': custo_total,
        'tempo_total': tempo_total_horas,
        'data_calculo': datetime.now().strftime("%d/%m/%Y %H:%M")
    }
    
    calculos.append(novo_calculo)
    salvar_dados(calculos, CALCULOS_FILE)
    print("\nCálculo salvo com sucesso!")

def listar_calculos():
    calculos = carregar_dados(CALCULOS_FILE)
    propriedades = carregar_dados(PROPRIEDADES_FILE)
    veiculos = carregar_dados(VEICULOS_FILE)
    produtos = carregar_dados(PRODUTOS_FILE)
    
    if not calculos:
        print("Nenhum cálculo encontrado.")
        return
    
    print("\n--- Lista de Cálculos ---")
    for calc in calculos:
        # Buscar nomes relacionados
        prop_nome = next((p['nome'] for p in propriedades if p['id'] == calc['propriedade_id']), "Desconhecido")
        veic_tipo = next((v['tipo'] for v in veiculos if v['id'] == calc['veiculo_id']), "Desconhecido")
        prod_nome = next((p['nome'] for p in produtos if p['id'] == calc['produto_id']), "Desconhecido")
        
        print(f"ID {calc['id']}: {prod_nome} de {prop_nome} com {veic_tipo}")
        print(f"  Peso: {calc['peso_total']} kg, Viagens: {calc['viagens']}, Distância total: {calc['distancia_total']:.2f} km")
        print(f"  Custo: R$ {calc['custo_total']:.2f}, Tempo: {calc['tempo_total']:.2f} h")
        if 'data_calculo' in calc:
            print(f"  Data do cálculo: {calc['data_calculo']}")

def exportar_dados():
    """Exporta todos os dados para um único arquivo JSON na pasta Downloads"""
    print("\n--- Exportar Dados ---")
    
    # Pedir confirmação
    confirmacao = input("Tem certeza que deseja exportar todos os dados? (s/n): ").strip().lower()
    if confirmacao != 's':
        print("Exportação cancelada.")
        return
    
    nome_arquivo = input("Nome do arquivo (sem extensão) [dados_transporte_rural_export]: ").strip()
    
    if nome_arquivo == "":
        nome_arquivo = "dados_transporte_rural_export"
    
    # Adicionar extensão se não tiver
    if not nome_arquivo.endswith('.json'):
        nome_arquivo += '.json'
    
    # Carregar todos os dados
    try:
        propriedades = carregar_dados(PROPRIEDADES_FILE)
        veiculos = carregar_dados(VEICULOS_FILE)
        produtos = carregar_dados(PRODUTOS_FILE)
        calculos = carregar_dados(CALCULOS_FILE)
    except Exception as e:
        print(f"Erro ao carregar dados para exportação: {e}")
        return
    
    # Criar estrutura consolidada
    dados_consolidados = {
        "propriedades": propriedades,
        "veiculos": veiculos,
        "produtos": produtos,
        "calculos_realizados": calculos
    }
    
    try:
        # Definir caminho da pasta Downloads
        caminho_downloads = Path.home() / "Downloads" / nome_arquivo
        
        # Garantir que a pasta Downloads existe
        os.makedirs(Path.home() / "Downloads", exist_ok=True)
        
        # Salvar o arquivo
        with open(caminho_downloads, 'w', encoding='utf-8') as f:
            json.dump(dados_consolidados, f, ensure_ascii=False, indent=2)
        
        print(f"\nDados exportados com sucesso para: {caminho_downloads}")
        print("O arquivo está disponível na sua pasta Downloads.")
        
    except Exception as e:
        print(f"\nErro ao exportar dados: {e}")
        print("Verifique se você tem permissão para escrever na pasta Downloads.")

# Execução principal
if __name__ == "__main__":
    try:
        setup_data_directory()
        print("Simulador de Logística de Transporte Rural iniciado com sucesso!")
        menu()
    except Exception as e:
        print(f"Erro inesperado: {e}")
        time.sleep(3)  # Pausa para visualizar o erro antes de fechar