import asyncio
import random
import string
from datetime import datetime, timedelta
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import nest_asyncio
from random import choice
from telegram.error import TelegramError
import json
import os
import requests
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler, JobQueue
)
import re
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram import Update  # Certifique-se de que essa importação está correta
from datetime import datetime, timedelta

# Token do bot (substitua pelo token real do seu bot)
TOKEN = '7885570198:AAEygg1UP__uLi-nQhq0gEWEFfxqCk-6JrY'
# ID do canal específico
CANAL_ID = '-1003745308914'
# Link para o seu chat
CHAT_LINK = 'https://t.me/jhonatamsilva'

# Dicionário para armazenar as informações dos usuários
usuarios = {}
# Conjunto para armazenar os IDs dos usuários
user_ids = set()
# Caminho para o arquivo onde os IDs serão armazenados
USER_IDS_FILE = 'user_ids.json'
ARQUIVO_USUARIOS = 'usuarios.json'
PERGUNTA_PLATAFORMA, PERGUNTA_MARTINGALE, RECEBE_LISTA = range(3)


MAPA_CORES = {
    "⚫️": "black",
    "🔴": "red",
    "🟢": "green",
    "⚪️": "white"
}
def sinais_tem_verde(sinais_com_hora):
    for sinal_hora in sinais_com_hora:
        if '🟢' in sinal_hora:
            return True
    return False

def salvar_usuarios(usuarios):
    with open(ARQUIVO_USUARIOS, 'w') as f:
        json.dump(usuarios, f, default=str, indent=4)

def carregar_usuarios():
    if os.path.exists(ARQUIVO_USUARIOS):
        with open(ARQUIVO_USUARIOS, 'r') as f:
            return json.load(f)
    return {}



# Mapeamento dos valores numéricos da API para cores
MAPA_CORES_API_BLAZE = {1: "red", 2: "black", 0: "white"}
MAPA_CORES_API_JONBET = {1: "green", 2: "black", 0: "white"}


ARQUIVO_HISTORICO_BLAZE = "historico_blaze.json"
ARQUIVO_HISTORICO_JONBET = "historico_jonbet.json"

def carregar_historico_local():
    if os.path.exists(ARQUIVO_HISTORICO_BLAZE):
        with open(ARQUIVO_HISTORICO_BLAZE, "r") as f:
            try:
                return json.load(f)
            except Exception as e:
                print(f"Erro ao carregar histórico Blaze: {e}")
                return []
    return []

def salvar_historico_local(historico):
    with open(ARQUIVO_HISTORICO_BLAZE, "w") as f:
        json.dump(historico, f, indent=4)

def pegar_ultima_rodada_blaze():
    url = "https://blaze.bet.br/api/singleplayer-originals/originals/roulette_games/recent/1"  # Verifique se essa URL está correta para a Blaze
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        resposta = requests.get(url, headers=headers, timeout=10)
        resposta.raise_for_status()
        dados = resposta.json()
        return dados
    except Exception as e:
        print(f"Erro ao acessar API Blaze: {e}")
        return []

def atualizar_historico_incremental_blaze():
    # Buscar a rodada mais recente da API
    url = "https://blaze.bet.br/api/singleplayer-originals/originals/roulette_games/recent/1"
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resposta = requests.get(url, headers=headers, timeout=10)
        resposta.raise_for_status()
        dados = resposta.json()
        if not dados:
            print("Nenhuma rodada nova encontrada na API Blaze.")
            return carregar_historico_local()

        rodada_nova = dados[0]  # Como retorna lista com 1 elemento

        # Carregar histórico local
        historico = carregar_historico_local()

        # Verificar se a rodada já está no histórico
        ids_historico = {r['id'] for r in historico}
        if rodada_nova['id'] in ids_historico:
            print("Rodada já está no histórico, nada a atualizar.")
            return historico

        # Adicionar nova rodada no início (mais recente primeiro)
        historico.insert(0, rodada_nova)

        # Manter tamanho máximo de 900 rodadas
        if len(historico) > 900:
            historico = historico[:900]

        # Salvar histórico atualizado
        salvar_historico_local(historico)
        print(f"Histórico Blaze atualizado. Total de rodadas: {len(historico)}")
        return historico

    except Exception as e:
        print(f"Erro ao acessar API Blaze: {e}")
        return carregar_historico_local()

def carregar_historico_jonbet():
    if os.path.exists(ARQUIVO_HISTORICO_JONBET):
        with open(ARQUIVO_HISTORICO_JONBET, "r") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def salvar_historico_jonbet(historico):
    with open(ARQUIVO_HISTORICO_JONBET, "w") as f:
        json.dump(historico, f, indent=4)

def pegar_ultima_rodada_jonbet():
    url = "https://jonbet.bet.br/api/singleplayer-originals/originals/roulette_games/recent/1"
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        resposta = requests.get(url, headers=headers, timeout=10)
        resposta.raise_for_status()
        dados = resposta.json()
        return dados
    except Exception as e:
        print(f"Erro ao acessar API Jonbet: {e}")
        return []

def atualizar_historico_incremental_jonbet():
    url = "https://jonbet.bet.br/api/singleplayer-originals/originals/roulette_games/recent/1"
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resposta = requests.get(url, headers=headers, timeout=10)
        resposta.raise_for_status()
        dados = resposta.json()
        if not dados:
            print("Nenhuma rodada nova encontrada na API Jonbet.")
            return carregar_historico_jonbet()

        rodada_nova = dados[0]

        historico = carregar_historico_jonbet()
        ids_historico = {r['id'] for r in historico}
        if rodada_nova['id'] in ids_historico:
            print("Rodada já está no histórico Jonbet.")
            return historico

        historico.insert(0, rodada_nova)

        if len(historico) > 900:
            historico = historico[:900]

        salvar_historico_jonbet(historico)
        print(f"Histórico Jonbet atualizado. Total de rodadas: {len(historico)}")
        return historico

    except Exception as e:
        print(f"Erro ao acessar API Jonbet: {e}")
        return carregar_historico_jonbet()

def extrair_cores_previstas(sinal: str):
    cores = []
    for simbolo, cor in MAPA_CORES.items():
        if simbolo in sinal:
            cores.append(cor)
    return cores


def converter_horario_utc_para_local(timestamp_str, offset_horas=-3):
    try:
        dt_utc = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        dt_local = dt_utc + timedelta(hours=offset_horas)
        return dt_local.strftime("%H:%M")
    except Exception as e:
        print(f"Erro ao converter horário: {e}")
        return ""

def extrair_hora_do_sinal(sinal_com_hora: str):
    partes = sinal_com_hora.strip().split()
    if len(partes) < 2:
        return None
    hora_str = partes[-1]
    try:
        hora = datetime.strptime(hora_str, "%H:%M").time()
        return hora
    except ValueError:
        return None

def corrigir_lista_com_gales_por_hora_exata(sinais_com_hora, dados_api, max_gale, mapa_cores_api):
    resultados = []
    placar_acertos = 0
    placar_erros = 0
    placar_brancos = 0

    gale_atual = 0

    for sinal_com_hora in sinais_com_hora:
        cores_previstas = extrair_cores_previstas(sinal_com_hora)
        hora_sinal = extrair_hora_do_sinal(sinal_com_hora)
        if hora_sinal is None:
            print(f"Erro: não foi possível extrair hora do sinal '{sinal_com_hora}'")
            continue

        registros_filtrados = []
        for registro in dados_api:
            timestamp_api = registro.get('created_at', '')
            if not timestamp_api:
                continue
            try:
                dt_api_utc = datetime.fromisoformat(timestamp_api.replace("Z", "+00:00"))
                dt_api_local = dt_api_utc + timedelta(hours=-3)
                dt_api_local = dt_api_local.replace(tzinfo=None)

                minuto_seguinte = (datetime(2000,1,1,hora_sinal.hour,hora_sinal.minute) + timedelta(minutes=1)).replace(year=dt_api_local.year, month=dt_api_local.month, day=dt_api_local.day)
                if (dt_api_local.hour == hora_sinal.hour and dt_api_local.minute == hora_sinal.minute) or \
                   (dt_api_local.hour == minuto_seguinte.hour and dt_api_local.minute == minuto_seguinte.minute):
                    registros_filtrados.append((dt_api_local, registro))
            except Exception as e:
                print(f"Erro ao processar timestamp: {e}")
                continue

        if not registros_filtrados:
            print(f"Erro: não foi encontrado registro da API para o sinal '{sinal_com_hora}'")
            continue

        registros_filtrados.sort(key=lambda x: x[0].second)

        achou_acerto = False
        registro_acertado = None
        gale_usado = 0

        for tentativa_gale in range(0, max_gale + 1):
            if tentativa_gale < 2:
                hora_busca = hora_sinal.hour
                minuto_busca = hora_sinal.minute
                indice_pedra = tentativa_gale
            else:
                dt_sinal = datetime(2000, 1, 1, hora_sinal.hour, hora_sinal.minute)
                dt_minuto_seguinte = dt_sinal + timedelta(minutes=1)
                hora_busca = dt_minuto_seguinte.hour
                minuto_busca = dt_minuto_seguinte.minute
                indice_pedra = 0

            registros_gale = [(dt, reg) for dt, reg in registros_filtrados if dt.hour == hora_busca and dt.minute == minuto_busca]

            if indice_pedra < len(registros_gale):
                dt, reg = registros_gale[indice_pedra]
                cor_num = reg.get('color', -1)
                cor_real = mapa_cores_api.get(cor_num, "unknown")

                if cor_real in cores_previstas:
                    achou_acerto = True
                    registro_acertado = reg
                    gale_usado = tentativa_gale
                    break
                elif cor_real == "white":
                    achou_acerto = None
                    registro_acertado = reg
                    gale_usado = tentativa_gale
                    break

        if registro_acertado is None:
            registros_minuto_sinal = [(dt, reg) for dt, reg in registros_filtrados if dt.hour == hora_sinal.hour and dt.minute == hora_sinal.minute]
            if registros_minuto_sinal:
                registros_minuto_sinal.sort(key=lambda x: x[0].second)
                registro_acertado = registros_minuto_sinal[0][1]
                gale_usado = 0
                achou_acerto = False
            else:
                print(f"Erro: nenhum registro para o minuto do sinal '{sinal_com_hora}'")
                continue

        hora_local = hora_sinal.strftime("%H:%M")

        print(f"Debug: Sinal previsto: '{sinal_com_hora}' -> cores previstas: {cores_previstas} | "
              f"Cor real API: {mapa_cores_api.get(registro_acertado.get('color', -1), 'unknown')} | Horário sinal: {hora_local} | Gale usado: {gale_usado}")

        if achou_acerto is None:  # Branco
            placar_brancos += 1
            acertou = None
            gale_atual = 0
        elif achou_acerto:
            placar_acertos += 1
            acertou = True
            gale_atual = 0
        else:
            placar_erros += 1
            acertou = False
            if gale_atual < max_gale:
                gale_atual += 1

        resultados.append({
            "previsao": sinal_com_hora,
            "resultado_real": mapa_cores_api.get(registro_acertado.get('color', -1), "unknown"),
            "acertou": acertou,
            "gale": gale_usado,
            "hora": hora_local
        })

    return resultados, placar_acertos, placar_erros, placar_brancos



def formatar_resposta_com_linhas_originais(resultados, acertos, erros, brancos, max_gale):
    linhas = []
    cont_gales = [0] * (max_gale + 1)

    for r in resultados:
        partes = r['previsao'].split()
        sinal = partes[0] if partes else r['previsao']

        cor_real = r.get("resultado_real", "")
        acertou = r.get("acertou", False)

        gale_str = ""
        status = ""

        if acertou is True:
            status = "✅"
            gale_str = "SG" if r['gale'] == 0 else f"G{r['gale']}"
            cont_gales[r['gale']] += 1
        elif acertou is None:
            status = "⚪️"
            gale_str = f"G{r['gale']}"
            cont_gales[r['gale']] += 1
        else:
            status = "❌"
            gale_str = ""

        # Se a cor real for branca, acrescenta o símbolo ⚪️ antes do status
        if cor_real == "white" and acertou is not None:
            status = "⚪️" + status

        linha = f"{sinal} {r['hora']} {status}"
        if gale_str:
            linha += f" {gale_str}"
        linhas.append(linha)

    placar = (
        f"\n🎯 Placar: ✅ {acertos} | ❌ {erros} | ⚪️ {brancos}\n" +
        " | ".join([f"G{idx}: {cont}" for idx, cont in enumerate(cont_gales)])
    )

    return "\n".join(linhas) + placar


def inicializar_arquivo():
    # Cria o arquivo com uma lista vazia se não existir
    if not os.path.exists(USER_IDS_FILE):
        with open(USER_IDS_FILE, 'w') as file:
            json.dump([], file)  # Inicializa com uma lista vazia

def carregar_ids():
    # Verifica se o arquivo existe e não está vazio
    if os.path.exists(USER_IDS_FILE) and os.path.getsize(USER_IDS_FILE) > 0:
        with open(USER_IDS_FILE, 'r') as file:
            try:
                data = json.load(file)
                # Verifica se o dado carregado é uma lista
                if isinstance(data, list):
                    return set(data)
                else:
                    print("O conteúdo do arquivo não é uma lista. Retornando conjunto vazio.")
                    return set()
            except json.JSONDecodeError:
                print("Erro ao decodificar JSON. Retornando conjunto vazio.")
                return set()
    return set()


def salvar_ids(user_ids):
    with open(USER_IDS_FILE, 'w') as file:
        json.dump(list(user_ids), file)

# Função para gerar um ID único
def gerar_id_unico():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

# Função para gerar uma lista de sinais para Blaze com diferentes opções de proteção
def gerar_lista_sinais_jonbet_protegida(inicio: datetime, fim: datetime, protecao: str):
    cores = ['🟢', '⚫️']
    lista_sinais = []
    horario_atual = inicio

    while horario_atual < fim:
        if protecao == "somente_branco":
            cor = '⚪️'
        else:
            cor = random.choice(cores)
            if protecao == "branco":
                cor += '⚪️'
        
        intervalo_minutos = random.randint(2, 5)
        horario_sinal = horario_atual + timedelta(minutes=intervalo_minutos)
        if horario_sinal <= fim:
            lista_sinais.append(f"{cor} {horario_sinal.strftime('%H:%M')}")
        horario_atual = horario_sinal

    return lista_sinais

# Função para gerar uma lista de sinais para Blaze dentro de um intervalo
def gerar_lista_sinais_smashup(inicio: datetime, fim: datetime):
    cores = ['🔴⚪️', '⚫️⚪️']
    lista_sinais = []
    horario_atual = inicio

    while horario_atual < fim:
        cor = random.choice(cores)
        intervalo_minutos = random.randint(2, 5)
        horario_sinal = horario_atual + timedelta(minutes=intervalo_minutos)
        if horario_sinal <= fim:
            lista_sinais.append(f"{cor} {horario_sinal.strftime('%H:%M')}")
        horario_atual = horario_sinal

    return lista_sinais

def gerar_lista_sinais_smashup(inicio: datetime, fim: datetime, protecao: str):
    cores = ['🔴', '⚫️']
    lista_sinais = []
    horario_atual = inicio

    while horario_atual < fim:
        if protecao == "somente_branco":
            cor = '⚪️'
        else:
            cor = random.choice(cores)
            if protecao == "branco":
                cor += '⚪️'
        
        intervalo_minutos = random.randint(2, 5)
        horario_sinal = horario_atual + timedelta(minutes=intervalo_minutos)
        if horario_sinal <= fim:
            lista_sinais.append(f"{cor} {horario_sinal.strftime('%H:%M')}")
        horario_atual = horario_sinal

    return lista_sinais

def gerar_lista_sinais_blaze(inicio: datetime, fim: datetime, protecao: str):
    cores = ['🔴⚪️', '⚫️⚪️']
    lista_sinais = []
    horario_atual = inicio

    while horario_atual < fim:
        cor = random.choice(cores)
        intervalo_minutos = random.randint(2, 5)
        horario_sinal = horario_atual + timedelta(minutes=intervalo_minutos)
        if horario_sinal <= fim:
            lista_sinais.append(f"{cor} {horario_sinal.strftime('%H:%M')}")
        horario_atual = horario_sinal

    return lista_sinais

# Função para gerar uma lista de sinais para Jonbet dentro de um intervalo
def gerar_lista_sinais_jonbet(inicio: datetime, fim: datetime):
    cores = ['🟢⚪️', '⚫️⚪️']
    lista_sinais = []
    horario_atual = inicio

    while horario_atual < fim:
        cor = random.choice(cores)
        intervalo_minutos = random.randint(2, 5)
        horario_sinal = horario_atual + timedelta(minutes=intervalo_minutos)
        if horario_sinal <= fim:
            lista_sinais.append(f"{cor} {horario_sinal.strftime('%H:%M')}")
        horario_atual = horario_sinal

    return lista_sinais

# Função para gerar uma lista de sinais para Crash dentro de um intervalo com base nas velas
def gerar_lista_sinais_crash(inicio: datetime, fim: datetime, valor_vela: str):
    lista_sinais = []
    horario_atual = inicio

    while horario_atual < fim:
        intervalo_minutos = random.randint(2, 5)
        horario_sinal = horario_atual + timedelta(minutes=intervalo_minutos)
        if horario_sinal <= fim:
            lista_sinais.append(f"{horario_sinal.strftime('%H:%M')} 🚀 {valor_vela}📊")
        horario_atual = horario_sinal

    return lista_sinais

# Dicionário para armazenar as informações dos usuários
usuarios = {}

# Função para gerar um ID único
def gerar_id_unico():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

# Funções para gerar listas de sinais
def gerar_lista_sinais_blaze_protegida(inicio: datetime, fim: datetime, protecao: str, max_sinais=None):
    lista_sinais = []
    horario_atual = inicio

    # Ajuste para o caso "somente_branco"
    if protecao == "somente_branco":
        max_sinais = 4  # Definindo um limite para sinais
        cor = '⚪️'
        while horario_atual < fim and len(lista_sinais) < max_sinais:
            intervalo_minutos = random.randint(8, 14)  # Distância de 8 a 14 minutos
            horario_sinal = horario_atual + timedelta(minutes=intervalo_minutos)
            if horario_sinal <= fim:
                lista_sinais.append(f"{cor} {horario_sinal.strftime('%H:%M')}")
            horario_atual = horario_sinal

    elif protecao == "protecao_nao_branco":
        # Gera uma lista apenas com as cores 🔴 e ⚫️
        while horario_atual < fim:
            cor = random.choice(['🔴', '⚫️'])  # Seleciona aleatoriamente entre 🔴 e ⚫️
            intervalo_minutos = random.randint(2, 5)  # Distância padrão
            horario_sinal = horario_atual + timedelta(minutes=intervalo_minutos)
            if horario_sinal <= fim:
                lista_sinais.append(f"{cor} {horario_sinal.strftime('%H:%M')}")
            horario_atual = horario_sinal

    else:  # Para a proteção "proteger o branco"
        # Gera uma lista grande misturando as cores
        while horario_atual < fim:
            cor = random.choice(['🔴⚪️', '⚫️⚪️'])  # Seleciona uma combinação de cores
            intervalo_minutos = random.randint(2, 5)  # Distância padrão
            horario_sinal = horario_atual + timedelta(minutes=intervalo_minutos)
            if horario_sinal <= fim:
                lista_sinais.append(f"{cor} {horario_sinal.strftime('%H:%M')}")
            horario_atual = horario_sinal

    # Formatação para "somente_branco"
    if protecao == "somente_branco":
        return "⏱️ Horários das Probabilidade:\n\n" + "\n".join(lista_sinais) + "\n\nEntre 2 min antes e 2 min depois "
    else:
        return lista_sinais
def gerar_metadiaria_blaze(inicio: datetime, fim: datetime, protecao="nao_branco", max_sinais=8):
    cores = ['🔴⚪️', '⚫️⚪️']  # As opções de cores padrão
    lista_sinais = []
    horario_atual = inicio

    # Verificando se max_sinais é um número inteiro, caso contrário, atribuir um valor padrão
    try:
        max_sinais = int(max_sinais)
    except ValueError:
        print(f"Valor inválido para max_sinais: '{max_sinais}', usando valor padrão de 8.")
        max_sinais = 8  # Valor padrão caso max_sinais seja inválido

    while horario_atual < fim and len(lista_sinais) < max_sinais:
        # Verifica se a proteção é "somente_branco"
        if protecao == "somente_branco":
            cor = '⚪️'  # Gera apenas sinais com a cor branca
        else:
            cor = random.choice(cores)  # Gera normalmente com as cores predefinidas

        intervalo_minutos = random.randint(2, 5)
        horario_sinal = horario_atual + timedelta(minutes=intervalo_minutos)

        if horario_sinal <= fim:
            lista_sinais.append(f"{cor} {horario_sinal.strftime('%H:%M')}")
        horario_atual = horario_sinal

    return lista_sinais
def gerar_metadiaria_jonbet(inicio: datetime, fim: datetime, max_sinais=8):
    
    cores = ['🟢⚪️', '⚫️⚪️']
    lista_sinais = []
    horario_atual = inicio

    # Verificando se max_sinais é um número inteiro, caso contrário, atribuir um valor padrão
    try:
        max_sinais = int(max_sinais)
    except ValueError:
        print(f"Valor inválido para max_sinais: '{max_sinais}', usando valor padrão de 8.")
        max_sinais = 8  # Valor padrão caso max_sinais seja inválido

    while horario_atual < fim and len(lista_sinais) < max_sinais:
        cor = random.choice(cores)
        intervalo_minutos = random.randint(2, 5)
        horario_sinal = horario_atual + timedelta(minutes=intervalo_minutos)
        if horario_sinal <= fim:
            lista_sinais.append(f"{cor} {horario_sinal.strftime('%H:%M')}")
        horario_atual = horario_sinal

    return lista_sinais
def gerar_lista_sinais_bacbo(inicio: datetime, fim: datetime):
    cores = ['🔴🟠', '🔵🟠']  # vermelho ou azul, protegendo no laranja
    lista_sinais = []
    horario_atual = inicio

    while horario_atual < fim:
        cor = random.choice(cores)
        intervalo_minutos = random.randint(2, 5)
        horario_sinal = horario_atual + timedelta(minutes=intervalo_minutos)
        if horario_sinal <= fim:
            lista_sinais.append(f"{cor} {horario_sinal.strftime('%H:%M')}")
        horario_atual = horario_sinal

    return lista_sinais

def gerar_lista_sinais_jonbet_protegida(inicio: datetime, fim: datetime, protecao: str):
    cores = ['🟢', '⚫️']
    lista_sinais = []
    horario_atual = inicio

    # Ajuste para o caso "somente_branco"
    if protecao == "somente_branco":
        max_sinais = 4  # Definindo um limite para sinais
        cor = '⚪️'
        while horario_atual < fim and len(lista_sinais) < max_sinais:
            intervalo_minutos = random.randint(8, 14)  # Distância de 8 a 14 minutos
            horario_sinal = horario_atual + timedelta(minutes=intervalo_minutos)
            if horario_sinal <= fim:
                lista_sinais.append(f"{cor} {horario_sinal.strftime('%H:%M')}")
            horario_atual = horario_sinal

    elif protecao == "protecao_nao_branco":
        # Gera uma lista apenas com as cores 🟢 e ⚫️
        while horario_atual < fim:
            cor = random.choice(['🟢', '⚫️'])  # Seleciona aleatoriamente entre 🔴 e ⚫️
            intervalo_minutos = random.randint(2, 5)  # Distância padrão
            horario_sinal = horario_atual + timedelta(minutes=intervalo_minutos)
            if horario_sinal <= fim:
                lista_sinais.append(f"{cor} {horario_sinal.strftime('%H:%M')}")
            horario_atual = horario_sinal

    else:  # Para a proteção "proteger o branco"
        # Gera uma lista grande misturando as cores
        while horario_atual < fim:
            cor = random.choice(['🟢⚪️', '⚫️⚪️'])  # Seleciona uma combinação de cores
            intervalo_minutos = random.randint(2, 5)  # Distância padrão
            horario_sinal = horario_atual + timedelta(minutes=intervalo_minutos)
            if horario_sinal <= fim:
                lista_sinais.append(f"{cor} {horario_sinal.strftime('%H:%M')}")
            horario_atual = horario_sinal

    # Formatação para "somente_branco"
    if protecao == "somente_branco":
        return "⏱️ Horários das Probabilidade:\n\n" + "\n".join(lista_sinais) + "\n\nEntre 2 min antes e 2 min depois "
    else:
        return lista_sinais
def gerar_lista_sinais_crash(inicio: datetime, fim: datetime, valor_vela: str):
    lista_sinais = []
    horario_atual = inicio

    while horario_atual < fim:
        intervalo_minutos = random.randint(2, 5)
        horario_sinal = horario_atual + timedelta(minutes=intervalo_minutos)
        if horario_sinal <= fim:
            lista_sinais.append(f"{horario_sinal.strftime('%H:%M')} 🚀 {valor_vela}📊")
        horario_atual = horario_sinal

    return lista_sinais

# Função para enviar mensagem de venda após o término do teste
async def enviar_mensagem_venda(context: ContextTypes.DEFAULT_TYPE):
    job_data = context.job.data
    user_id = job_data['user_id']
    chat_id = job_data['chat_id']

    # Bloquear o usuário após o término do teste
    usuarios[user_id]['bloqueado'] = True

    # Mensagem de venda
    mensagem_venda = (
        "🕒 Seu teste gratuito terminou! Aproveite a oportunidade e continue tendo acesso aos sinais!\n"
        "💸 [Clique aqui para comprar agora](https://t.me/Desbloqueie_Seu_Gerador_Bot)"
    )
    await context.bot.send_message(chat_id=chat_id, text=mensagem_venda, parse_mode=ParseMode.MARKDOWN)

async def verificar_usuario_vip(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    try:
        # Verifica se o usuário é membro do canal
        membro = await context.bot.get_chat_member(chat_id=CANAL_ID, user_id=user_id)
        # Verifica se o status do usuário é 'member' ou superior (como 'administrator' ou 'creator')
        return membro.status in ['member', 'administrator', 'creator']
    except TelegramError as e:
        print(f"Erro ao verificar a associação do usuário: {e}")
        return False

user_ids = carregar_ids()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    user_id = user.id

    # Adiciona o ID do usuário ao conjunto e salva no arquivo
    user_ids.add(user_id)
    salvar_ids(user_ids)

    # Verifica se o usuário já está registrado
    if user_id not in usuarios:
        user_id_gerado = gerar_id_unico()
        usuarios[user_id] = {
            'id': user_id_gerado,
            'nome': user.first_name,
            'teste_inicio': None,
            'teste_fim': None,
            'plataforma': None,
            'modo': None,
            'bloqueado': False,
            'token_valido': False,
            'configuracao': {
                'favor_tendencia': '❌',
                'contra_tendencia': '❌',
                'inteligencia_ia': '❌',
                'estrategias_cores': '❌',
                'estrategias_numeros': '❌'
            }
        }

    # Verifica se o usuário é VIP (membro do canal) ou tem token válido
    is_vip = await verificar_usuario_vip(context, user_id)

    if is_vip or usuarios[user_id]['token_valido']:
        # Usuário VIP ou com token válido, atribuir permissões
        keyboard = [
            [InlineKeyboardButton("🔸Gere Sua LISTA AQUI!🔸", callback_data='voltar')],
            [InlineKeyboardButton("💰Comprar seu Plano Mensal ou Anual aqui!", url='https://t.me/jhonatamsilva')]
        ]
        mensagem = '💸 Bem-vindo VIP! Escolha a PLATAFORMA que você deseja criar sua LISTA Double ou Crash ✅'
    else:
        # Usuário não é VIP e não tem token válido
        if not usuarios[user_id].get('teste_inicio'):
            # Iniciar o teste de 1 dia
            usuarios[user_id]['teste_inicio'] = datetime.now(pytz.timezone('America/Sao_Paulo'))
            usuarios[user_id]['teste_fim'] = usuarios[user_id]['teste_inicio'] + timedelta(days=1)
            usuarios[user_id]['bloqueado'] = False

            mensagem = '💸 Bem-vindo ao GERADOR BLISS! Escolha a PLATAFORMA que você deseja criar sua LISTA Double ou Crash ✅'
        else:
            mensagem = '⛔ Seu teste gratuito já foi iniciado. Aproveite o tempo restante!'

        keyboard = [
            [InlineKeyboardButton("Peça seu Teste GRATUITO", url='https://t.me/jhonatamsilva')],
            [InlineKeyboardButton("💰Comprar seu Plano Mensal ou Anual aqui!", url='https://t.me/jhonatamsilva')]
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(mensagem, reply_markup=reply_markup)

async def enviar_mensagem_em_massa(context: ContextTypes.DEFAULT_TYPE, mensagem: str) -> None:
    for user_id in user_ids:
        try:
            await context.bot.send_message(chat_id=user_id, text=mensagem, parse_mode=ParseMode.MARKDOWN)
        except TelegramError as e:
            print(f"Erro ao enviar mensagem para {user_id}: {e}")

async def enviar_mensagem_massa(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Verifica se o comando foi enviado por um administrador (ou quem você quiser)
    if update.message.from_user.id == 5444910869:  # Substitua SEU_ID_ADMIN pelo ID do administrador
        mensagem = " ".join(context.args)
        if mensagem:
            await enviar_mensagem_em_massa(context, mensagem)
            await update.message.reply_text("Mensagem enviada para todos os usuários.")
        else:
            await update.message.reply_text("Por favor, forneça uma mensagem para enviar.")
    else:
        await update.message.reply_text("Você não tem permissão para enviar mensagens em massa.")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user = query.from_user
    await query.answer()
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    user_id = user.id
    if user_id not in usuarios:
        return
    if query.data == 'corrigir_listas':
        # Inicia o corretor via ConversationHandler
        return await iniciar_corretor(update, context)

    # Verifica se o usuário é membro do canal
    is_vip = await verificar_usuario_vip(context, user_id)

    # Se o usuário não é VIP e já teve um teste gratuito
    if not is_vip and usuarios[user_id].get('bloqueado', False):
        await query.edit_message_text(
            text="⛔ Seu teste gratuito terminou. Não deu tempo de testar? [Clique aqui para comprar agora](https://t.me/Desbloqueie_Seu_Gerador_Bot)",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # Se o usuário não é VIP e ainda não começou um teste
    if query.data == 'teste_gratuito':
        if not usuarios[user_id].get('teste_inicio'):  # Verifica se o teste já começou
            # Iniciar o teste de 10 minutos
            usuarios[user_id]['teste_inicio'] = datetime.now(pytz.timezone('America/Sao_Paulo'))
            usuarios[user_id]['teste_fim'] = usuarios[user_id]['teste_inicio'] + timedelta(minutes=10)
            usuarios[user_id]['bloqueado'] = False  # Define que o usuário não está bloqueado inicialmente

            # Libera o acesso aos botões
            keyboard = [
                [InlineKeyboardButton("🔸Gere Sua LISTA AQUI!🔸", callback_data='voltar')],
                [InlineKeyboardButton("Duvidas e Suporte📥", url='https://t.me/jhonatamsilva')]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                text="🕐 Seu teste gratuito de 10 minutos começou!",
                reply_markup=reply_markup
            )

            # Agendar o envio da mensagem de venda após 10 minutos
            context.job_queue.run_once(
                enviar_mensagem_venda,
                when=timedelta(minutes=10),  # 10 minutos
                data={'user_id': user_id, 'chat_id': query.message.chat_id}
            )
        else:
            await query.edit_message_text(
                text="⛔ Você já iniciou seu teste gratuito. Aguarde até que termine para solicitar outro.",
                parse_mode=ParseMode.MARKDOWN
            )
        return

    # Aqui você pode adicionar outras funcionalidades para usuários VIP ou não VIP

    # Continue com as outras opções...


    # Novo fluxo para Sinais Ao Vivo
    if query.data == 'sinais_ao_vivo':
        # Escolha da casa de apostas
        keyboard = [
            [InlineKeyboardButton("Blaze", callback_data='casa_blaze'),
             InlineKeyboardButton("JonBet", callback_data='casa_jonbet'),
             InlineKeyboardButton("Bac Bo", callback_data='casa_bacbo')],
             [InlineKeyboardButton("Smashup", callback_data='casa_smashup'),
             InlineKeyboardButton("Roleta Brasileira", callback_data='casa_roleta'),
            InlineKeyboardButton("Brabet", callback_data='casa_betfiery')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text="🎳 Escolha qual plataforma voce quer gerar os sinais:",
            reply_markup=reply_markup
        )
    elif query.data in ['casa_smashup', 'casa_betfiery', 'casa_bacbo', 'casa_blaze', 'casa_jonbet']:
        await query.edit_message_text(text="📡 conectando com a plataforma 📡")
        await asyncio.sleep(2)  # Aguardar 2 segundos
        await query.edit_message_text(text="🧩 validando estratégia 🧩")
        await asyncio.sleep(2)  # Aguardar mais 2 segundos    
    if query.data == 'casa_smashup':
    # Modo Double BetFiery
        entrada = choice(['🔴', '⚫️'])  # Alterna aleatoriamente entre 🔴 e ⚫️
        mensagem = (
        f"🎲 - Modo: Double Smashup\n"
        f"🎰 - Entrada será para: {entrada}\n"
        f"💰 - Com proteção no: ⚪️\n"
        f"♻️ - Utilize até o Gale: 2"
    )
        keyboard = [
        [InlineKeyboardButton("🎁 ENTRE AQUI NA PLATAFORMA!", url='https://www.smashup.com/invite/s1mw0QEX')],
        [InlineKeyboardButton("🔁 Gerar Novo Sinal 🔁", callback_data='gerar_smashup')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
        text=mensagem,
        reply_markup=reply_markup
    )
    elif query.data == 'gerar_smashup':
        await query.edit_message_text(text="🤖")
        await asyncio.sleep(1)  # Aguardar 1 segundo
    # Gera uma nova mensagem aleatória para BetFiery
        entrada = choice(['🔴', '⚫️'])  # Alterna aleatoriamente entre 🔴 e ⚫️
        mensagem = (
        f"🎲 - Modo: Double Smashup\n"
        f"🎰 - Entrada será para: {entrada}\n"
        f"💰 - Com proteção no: ⚪️\n"
        f"♻️ - Utilize até o Gale: 2"
    )
        keyboard = [
        [InlineKeyboardButton("🎁 ENTRE AQUI NA PLATAFORMA!", url='https://www.smashup.com/invite/s1mw0QEX')],
        [InlineKeyboardButton("🔁 Gerar Novo Sinal 🔁", callback_data='gerar_smashup')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
        text=mensagem,
        reply_markup=reply_markup
    )
    elif query.data == 'casa_smashup':
    # Modo Double BetFiery
        entrada = choice(['🔴', '⚫️'])  # Alterna aleatoriamente entre 🔴 e ⚫️
        mensagem = (
        f"🎲 - Modo: Double Smashup\n"
        f"🎰 - Entrada será para: {entrada}\n"
        f"💰 - Com proteção no: ⚪️\n"
        f"♻️ - Utilize até o Gale: 2"
    )
        keyboard = [
        [InlineKeyboardButton("🎁 ENTRE AQUI NA PLATAFORMA!", url='https://www.smashup.com/invite/s1mw0QEX')],
        [InlineKeyboardButton("🔁 Gerar Novo Sinal 🔁", callback_data='gerar_smashup')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
        text=mensagem,
        reply_markup=reply_markup
    )
    elif query.data == 'gerar_smashup':
        await query.edit_message_text(text="🤖")
        await asyncio.sleep(1)  # Aguardar 1 segundo
    # Gera uma nova mensagem aleatória para BetFiery
        entrada = choice(['🔴', '⚫️'])  # Alterna aleatoriamente entre 🔴 e ⚫️
        mensagem = (
        f"🎲 - Modo: Double Smashup\n"
        f"🎰 - Entrada será para: {entrada}\n"
        f"💰 - Com proteção no: ⚪️\n"
        f"♻️ - Utilize até o Gale: 2"
    )
        keyboard = [
        [InlineKeyboardButton("🎁 ENTRE AQUI NA PLATAFORMA!", url='https://www.smashup.com/invite/s1mw0QEX')],
        [InlineKeyboardButton("🔁 Gerar Novo Sinal 🔁", callback_data='gerar_smashup')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
        text=mensagem,
        reply_markup=reply_markup
    )
    if query.data == 'casa_betfiery':
    # Modo Double BetFiery
        entrada = choice(['🔴', '⚫️'])  # Alterna aleatoriamente entre 🔴 e ⚫️
        mensagem = (
        f"🎲 - Modo: Double BetFiery\n"
        f"🎰 - Entrada será para: {entrada}\n"
        f"💰 - Com proteção no: ⚪️\n"
        f"♻️ - Utilize até o Gale: 2"
    )
        keyboard = [
        [InlineKeyboardButton("🎁 ENTRE AQUI NA PLATAFORMA!", url='https://betfiery2.com?referralcode=66f8924b98caaf13463ffd3a')],
        [InlineKeyboardButton("🔁 Gerar Novo Sinal 🔁", callback_data='gerar_betfiery')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
        text=mensagem,
        reply_markup=reply_markup
    )
    elif query.data == 'gerar_betfiery':
        await query.edit_message_text(text="🤖")
        await asyncio.sleep(1)  # Aguardar 1 segundo
    # Gera uma nova mensagem aleatória para BetFiery
        entrada = choice(['🔴', '⚫️'])  # Alterna aleatoriamente entre 🔴 e ⚫️
        mensagem = (
        f"🎲 - Modo: Double BetFiery\n"
        f"🎰 - Entrada será para: {entrada}\n"
        f"💰 - Com proteção no: ⚪️\n"
        f"♻️ - Utilize até o Gale: 2"
    )
        keyboard = [
        [InlineKeyboardButton("🎁 ENTRE AQUI NA PLATAFORMA!", url='https://betfiery2.com?referralcode=66f8924b98caaf13463ffd3a')],
        [InlineKeyboardButton("🔁 Gerar Novo Sinal 🔁", callback_data='gerar_betfiery')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
        text=mensagem,
        reply_markup=reply_markup
    )
    
        
    elif query.data == 'casa_blaze':
        # Modo Double Blaze
        entrada = choice(['🔴', '⚫️'])  # Alterna aleatoriamente entre 🔴 e ⚫️
        mensagem = (
            f"🎲 - Modo: Double Blaze\n"
            f"🎰 - Entrada será para: {entrada}\n"
            f"💰 - Com proteção no: ⚪️\n"
            f"♻️ - Utilize até o Gale: 2"
        )

        keyboard = [
            [InlineKeyboardButton("🎁 ENTRE AQUI NA PLATAFORMA!", url='https://blaze-codigo.com/r/Vj6Q1V')],
            [InlineKeyboardButton("🔁 Gerar Novo Sinal 🔁", callback_data='gerar_blaze')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text=mensagem,
            reply_markup=reply_markup
        )

    elif query.data == 'gerar_blaze':
        await query.edit_message_text(text="🤖")
        await asyncio.sleep(1)  # Aguardar 1 segundo
        # Gera uma nova mensagem aleatória para Blaze
        entrada = choice(['🔴', '⚫️'])  # Alterna aleatoriamente entre 🔴 e ⚫️
        mensagem = (
            f"🎲 - Modo: Double Blaze\n"
            f"🎰 - Entrada será para: {entrada}\n"
            f"💰 - Com proteção no: ⚪️\n"
            f"♻️ - Utilize até o Gale: 2"
        )

        keyboard = [
            [InlineKeyboardButton("🎁 ENTRE AQUI NA PLATAFORMA!", url='https://blaze-codigo.com/r/Vj6Q1V')],
            [InlineKeyboardButton("🔁 Gerar Novo Sinal 🔁", callback_data='gerar_blaze')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text=mensagem,
            reply_markup=reply_markup
        )

    elif query.data == 'casa_bacbo':
        # Modo Double Blaze
        entrada = choice(['🔴', '🔵'])  # Alterna aleatoriamente entre 🔴 e 🔵
        mensagem = (
            f"🚨ENTRADA CONFIRMADA🚨\n"
            f"🎲 Modo: Bac Bo\n\n"
            f"💰 apostar na  {entrada}\n\n"
            f"🎰 Proteger o empate\n"
            f"➡️ Fazer até 2 gales"
        )
        keyboard = [
            [InlineKeyboardButton("🎁 ENTRE AQUI NA PLATAFORMA!", url='https://jonbet.com/pt/games/bac-bo')],
            [InlineKeyboardButton("🔁 Gerar Novo Sinal 🔁", callback_data='gerar_bacbo')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text=mensagem,
            reply_markup=reply_markup
        )

    elif query.data == 'gerar_bacbo':
        await query.edit_message_text(text="🤖")
        await asyncio.sleep(1)  # Aguardar 1 segundo
        # Gera uma nova mensagem aleatória para Blaze
        entrada = choice(['🔴', '🔵'])  # Alterna aleatoriamente entre 🔴 e 🔵
        mensagem = (
            f"🚨ENTRADA CONFIRMADA🚨\n"
            f"🎲 Modo: Bac Bo\n\n"
            f"💰 apostar na  {entrada}\n\n"
            f"🎰 Proteger o empate\n"
            f"➡️ Fazer até 2 gales"
        )
    elif query.data == 'casa_roleta':
        # Modo Double Blaze
        entrada = choice(['1º e na 3º coluna ', '2º e na 3º coluna'])  # Alterna aleatoriamente entre 🔴 e 🔵
        mensagem = (
            f"🚨ENTRADA CONFIRMADA🚨\n"
            f"🎲 Modo: Roleta\n\n"
            f"🎯 Apostar na {entrada}\n\n"
            f"🎰 Proteger o 0️⃣\n"
            f"➡️ Fazer até 2 gales"
        )
        keyboard = [
            [InlineKeyboardButton("🎁 ENTRE AQUI NA PLATAFORMA!", url='https://blaze1.space/pt/games/roleta-brasileira')],
            [InlineKeyboardButton("🔁 Gerar Novo Sinal 🔁", callback_data='gerar_roleta')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text=mensagem,
            reply_markup=reply_markup
        )

    elif query.data == 'gerar_roleta':
        await query.edit_message_text(text="🤖")
        await asyncio.sleep(1)  # Aguardar 1 segundo
        # Gera uma nova mensagem aleatória para Blaze
        entrada = choice(['1º e na 3º coluna ', '2º e na 3º coluna'])  # Alterna aleatoriamente entre 🔴 e 🔵
        mensagem = (
            f"🚨ENTRADA CONFIRMADA🚨\n"
            f"🎲 Modo: Roleta\n\n"
            f"🎯 Apostar na {entrada}\n\n"
            f"🎰 Proteger o 0️⃣\n"
            f"➡️ Fazer até 2 gales"
        )

        keyboard = [
            [InlineKeyboardButton("🎁 ENTRE AQUI NA PLATAFORMA!", url='https://blaze1.space/pt/games/roleta-brasileira')],
            [InlineKeyboardButton("🔁 Gerar Novo Sinal 🔁", callback_data='gerar_roleta')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text=mensagem,
            reply_markup=reply_markup
        )

    elif query.data == 'casa_jonbet':
        # Modo Double JonBet
        entrada = choice(['🟢', '⚫️'])  # Alterna aleatoriamente entre 🟢 e ⚫️
        mensagem = (
            f"🎲 - Modo: Double JonBet\n"
            f"🎰 - Entrada será para: {entrada}\n"
            f"💰 - Com proteção no: ⚪️\n"
            f"♻️ - Utilize até o Gale: 2"
        )

        keyboard = [
            [InlineKeyboardButton("🎁 ENTRE AQUI NA PLATAFORMA!", url='https://jon.ceo/r/XOVGK')],
            [InlineKeyboardButton("🔁 Gerar Novo Sinal 🔁", callback_data='gerar_jonbet')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text=mensagem,
            reply_markup=reply_markup
        )

    elif query.data == 'gerar_jonbet':
        await query.edit_message_text(text="🤖")
        await asyncio.sleep(1)  # Aguardar 1 segundo
        # Gera uma nova mensagem aleatória para JonBet
        entrada = choice(['🟢', '⚫️'])  # Alterna aleatoriamente entre 🟢 e ⚫️
        mensagem = (
            f"🎲 - Modo: Double JonBet\n"
            f"🎰 - Entrada será para: {entrada}\n"
            f"💰 - Com proteção no: ⚪️\n"
            f"♻️ - Utilize até o Gale: 2"
        )

        keyboard = [
            [InlineKeyboardButton("🎁 ENTRE AQUI NA PLATAFORMA!", url='https://jon.ceo/r/XOVGK')],
            [InlineKeyboardButton("🔁 Gerar Novo Sinal 🔁", callback_data='gerar_jonbet')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text=mensagem,
            reply_markup=reply_markup
        )

        # Inicializar valores padrão
        if usuarios[user_id]['plataforma'] is None:
            usuarios[user_id]['plataforma'] = 'BLAZE'
        if usuarios[user_id]['modo'] is None:
            usuarios[user_id]['modo'] = 'Double 🔴⚫️⚪️'

        # Atualizar teclado com ambas as opções de casa de aposta
        keyboard = [
            [InlineKeyboardButton(f"🚧 Casa de aposta = {usuarios[user_id]['plataforma']}", callback_data='toggle_casa')],
            [InlineKeyboardButton(f"🎮 Tipo de Modo = {usuarios[user_id]['modo']}", callback_data='toggle_modo')],
            [InlineKeyboardButton("Configurações ⚙️", callback_data='configuracao'),
             InlineKeyboardButton("🎰 Sinais Ao vivo", callback_data='sinais_ao_vivo')],
            [InlineKeyboardButton("♻️ CHECK LIST", callback_data='corrigir_listas')],
             [InlineKeyboardButton("Meta Diária! 🏹", callback_data='meta_diaria')],
            [InlineKeyboardButton("Continua LISTA ➡️", callback_data='continua')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text=f"🏠 𝙀𝙨𝙘𝙤𝙡𝙝𝙖 𝙪𝙢𝙖 𝙙𝙖𝙨 𝙤𝙥𝙘̧𝙤̃𝙚𝙨 {usuarios[user_id]['nome']}",
            reply_markup=reply_markup
        )

    elif query.data == 'toggle_casa':
        # Alternar entre as casas de aposta
        if usuarios[user_id]['plataforma'] == 'BLAZE':
            usuarios[user_id]['plataforma'] = 'JONBET'
        elif usuarios[user_id]['plataforma'] == 'JONBET':
            usuarios[user_id]['plataforma'] = 'SMASHUP'
        elif usuarios[user_id]['plataforma'] == 'SMASHUP':
            usuarios[user_id]['plataforma'] = 'BRABET'
        else:
            usuarios[user_id]['plataforma'] = 'BLAZE'  # Volta para Blaze

        # Atualizar o teclado com a nova opção de casa de aposta
        keyboard = [
            [InlineKeyboardButton(f"🚧 Casa de aposta = {usuarios[user_id]['plataforma']}", callback_data='toggle_casa')],
            [InlineKeyboardButton(f"🎮 Tipo de Modo = {usuarios[user_id]['modo']}", callback_data='toggle_modo')],
            [InlineKeyboardButton("Configurações ⚙️", callback_data='configuracao'),
             InlineKeyboardButton("🎰 Sinais Ao vivo", callback_data='sinais_ao_vivo')],
            [InlineKeyboardButton("♻️ CHECK LIST", callback_data='corrigir_listas')],
             [InlineKeyboardButton("Meta Diária! 🏹", callback_data='meta_diaria')],
            [InlineKeyboardButton("Continua LISTA ➡️", callback_data='continua')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text=f"🏠 𝙀𝙨𝙘𝙤𝙡𝙝𝙖 𝙪𝙢𝙖 𝙙𝙖𝙨 𝙤𝙥𝙘̧𝙤̃𝙚𝙨 {usuarios[user_id]['nome']}",
            reply_markup=reply_markup
        )

    elif query.data == 'toggle_modo':
        usuario = usuarios[user_id]
        modo_atual = usuario['modo']

        modos = ['Crash 🚀', 'Double 🎲', 'Aviator 🔺', 'Bac Bo 🎲']


        modo_atual = usuario.get('modo')

        if modo_atual not in modos:
            # Se o modo atual não estiver definido ou for inválido, defina um padrão
            modo_atual = modos[0]  # Por exemplo, 'Crash 🚀'
            usuario['modo'] = modo_atual

        indice_atual = modos.index(modo_atual)
        indice_novo = (indice_atual + 1) % len(modos)
        novo_modo = modos[indice_novo]

        usuario['modo'] = novo_modo


        # Atualizar o teclado com o novo modo de jogo
        keyboard = [
            [InlineKeyboardButton(f"🚧 Casa de aposta = {usuarios[user_id]['plataforma']}", callback_data='toggle_casa')],
            [InlineKeyboardButton(f"🎮 Tipo de Modo = {usuarios[user_id]['modo']}", callback_data='toggle_modo')],
            [InlineKeyboardButton("Configurações ⚙️", callback_data='configuracao'),
             InlineKeyboardButton("🎰 Sinais Ao vivo", callback_data='sinais_ao_vivo')],
            [InlineKeyboardButton("♻️ CHECK LIST", callback_data='corrigir_listas')],
             [InlineKeyboardButton("Meta Diária! 🏹", callback_data='meta_diaria')],
            [InlineKeyboardButton("Continua LISTA ➡️", callback_data='continua')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text=f"🏠 𝙀𝙨𝙘𝙤𝙡𝙝𝙖 𝙪𝙢𝙖 𝙙𝙖𝙨 𝙤𝙥𝙘̧𝙤̃𝙚𝙨 {usuarios[user_id]['nome']}",
            reply_markup=reply_markup
        )

    elif query.data == 'configuracao':
        configuracao = usuarios[user_id]['configuracao']
        keyboard = [
            [InlineKeyboardButton(f"Favor da tendência = {configuracao['favor_tendencia']}", callback_data='toggle_favor_tendencia')],
            [InlineKeyboardButton(f"Contra tendência = {configuracao['contra_tendencia']}", callback_data='toggle_contra_tendencia')],
            [InlineKeyboardButton(f"Ativar Inteligência I.A = {configuracao['inteligencia_ia']}", callback_data='toggle_inteligencia_ia')],
            [InlineKeyboardButton(f"Estrategias com Cores = {configuracao['estrategias_cores']}", callback_data='toggle_estrategias_cores')],
            [InlineKeyboardButton(f"Estrategias com Números = {configuracao['estrategias_numeros']}", callback_data='toggle_estrategias_numeros')],
            [InlineKeyboardButton("Voltar ⬅️", callback_data='voltar')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text="Escolha sua Configurações ⚙️",
            reply_markup=reply_markup
        )

    elif query.data.startswith('toggle_'):
        configuracao_chave = query.data.replace('toggle_', '')
        configuracao = usuarios[user_id]['configuracao']
        configuracao[configuracao_chave] = '✅' if configuracao[configuracao_chave] == '❌' else '❌'
        
        keyboard = [
            [InlineKeyboardButton(f"Favor da tendência = {configuracao['favor_tendencia']}", callback_data='toggle_favor_tendencia')],
            [InlineKeyboardButton(f"Contra tendência = {configuracao['contra_tendencia']}", callback_data='toggle_contra_tendencia')],
            [InlineKeyboardButton(f"Ativar Inteligência I.A = {configuracao['inteligencia_ia']}", callback_data='toggle_inteligencia_ia')],
            [InlineKeyboardButton(f"Estrategias com Cores = {configuracao['estrategias_cores']}", callback_data='toggle_estrategias_cores')],
            [InlineKeyboardButton(f"Estrategias com Números = {configuracao['estrategias_numeros']}", callback_data='toggle_estrategias_numeros')],
            [InlineKeyboardButton("Voltar ⬅️", callback_data='voltar')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text="⚙️ Configurações",
            reply_markup=reply_markup
        )

    elif query.data == 'voltar':
        keyboard = [
            [InlineKeyboardButton(f"🚧 Casa de aposta = {usuarios[user_id]['plataforma']}", callback_data='toggle_casa')],
            [InlineKeyboardButton(f"🎮 Tipo de Modo = {usuarios[user_id]['modo']}", callback_data='toggle_modo')],
            [InlineKeyboardButton("Configurações ⚙️", callback_data='configuracao'),
             InlineKeyboardButton("🎰 Sinais Ao vivo", callback_data='sinais_ao_vivo')],
            [InlineKeyboardButton("♻️ CHECK LIST", callback_data='corrigir_listas')],
             [InlineKeyboardButton("Meta Diária! 🏹", callback_data='meta_diaria')],
            [InlineKeyboardButton("Continua LISTA ➡️", callback_data='continua')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text=f"🏠 𝙀𝙨𝙘𝙤𝙡𝙝𝙖 𝙪𝙢𝙖 𝙙𝙖𝙨 𝙤𝙥𝙘̧𝙤̃𝙚𝙨 {usuarios[user_id]['nome']}",
            reply_markup=reply_markup
        )
    elif query.data == 'meta_diaria':
        keyboard = [
            [InlineKeyboardButton("Meta Diária 🏹", callback_data='meta_diaria1')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text="Escolha uma opção:",
            reply_markup=reply_markup
        )
        return

    elif query.data == 'meta_diaria1':
        usuarios[user_id]['meta_diaria'] = True
        # Pergunta ao usuário a quantidade de giros
        keyboard = [
            [InlineKeyboardButton("800", callback_data='giro_300')],
            [InlineKeyboardButton("900", callback_data='giro_400')],
            [InlineKeyboardButton("1000", callback_data='giro_500')],
            [InlineKeyboardButton("1200", callback_data='giro_600')]
        ] 
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text="📈 Selecione a quantidade de giros:",
            reply_markup=reply_markup
        )
        return

    elif query.data.startswith('giro_'):
        quantidade_giros = int(query.data.replace('giro_', ''))
        usuarios[user_id]['quantidade_giros'] = quantidade_giros

        keyboard = [
            [InlineKeyboardButton("0 Gales", callback_data='gales_0'),
                 InlineKeyboardButton("1 Gales", callback_data='gales_1'),
                 InlineKeyboardButton("2 Gales", callback_data='gales_2'),
                 InlineKeyboardButton("3 Gales", callback_data='gales_3'),],
                [InlineKeyboardButton("4 Gales", callback_data='gales_4'),
                 InlineKeyboardButton("5 Gales", callback_data='gales_5'),
                 InlineKeyboardButton("6 Gales", callback_data='gales_6'),
                 InlineKeyboardButton("7 Gales", callback_data='gales_7'),]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text="🎯 Escolha a quantidade de gales:",
            reply_markup=reply_markup
        )
        return
    elif query.data.startswith('gales_'):
        quantidade_gales = int(query.data.replace('gales_', ''))
        usuarios[user_id]['quantidade_gales'] = quantidade_gales

        modo = usuarios[user_id]['modo']

        if modo == 'Double 🎲':
            keyboard = [
                [InlineKeyboardButton("Proteger Branco", callback_data='protecao_branco')],
                [InlineKeyboardButton("Não Proteger", callback_data='protecao_nao_branco')],
                [InlineKeyboardButton("Lista Somente Branco", callback_data='protecao_somente_branco')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                text="🛡️ Escolha a proteção:",
                reply_markup=reply_markup
            )
            return
        else:
            # Para Crash e Aviator, ir direto para seleção de horário
            keyboard = []
            for hora in range(0, 24, 4):
                fila_horas = [InlineKeyboardButton(f"{h:02d}:00", callback_data=f'horario_{h:02d}:00') for h in range(hora, min(hora + 4, 24))]
                keyboard.append(fila_horas)

            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                text="⏳ Selecione o horário para gerar a lista:",
                reply_markup=reply_markup
            )
            return


    elif query.data.startswith('protecao_'):
        protecao = query.data.replace('protecao_', '')
        usuarios[user_id]['protecao'] = protecao

        # Agora que temos a escolha de proteção, continuar com o fluxo, selecionando o horário
        keyboard = []
        for hora in range(0, 24, 4):
            fila_horas = [InlineKeyboardButton(f"{h:02d}:00", callback_data=f'horario_{h:02d}:00') for h in range(hora, min(hora + 4, 24))]
            keyboard.append(fila_horas)

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text="⏳ Selecione o horário para gerar a lista:",
            reply_markup=reply_markup
        )
        return

    elif query.data == 'continua':
        modo = usuarios[user_id]['modo']
        if modo == 'Aviator 🔺' or modo == 'Crash 🚀':
            keyboard = [
                [InlineKeyboardButton("Vela 1.50 até 2x", callback_data='vela_1_80_2_80')],
                [InlineKeyboardButton("Vela 2x até 3x", callback_data='vela_2_80_3_00')],
                [InlineKeyboardButton("Vela 5x até 10x", callback_data='vela_5_10_')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                text="🎮 Escolha o valor das velas para gerar sua lista:",
                reply_markup=reply_markup
            )
        else:
            keyboard = [
                [InlineKeyboardButton("300", callback_data='giro_300'),
                InlineKeyboardButton("400", callback_data='giro_400'),
                InlineKeyboardButton("500", callback_data='giro_500'),
                InlineKeyboardButton("600", callback_data='giro_600')],
                [InlineKeyboardButton("700", callback_data='giro_700'),
                InlineKeyboardButton("800", callback_data='giro_800'),
                InlineKeyboardButton("900", callback_data='giro_900'),
                InlineKeyboardButton("1000", callback_data='giro_1000')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                text="📈 Selecione a quantidade de giros:",
                reply_markup=reply_markup
            )
        return


    elif query.data.startswith('giro_'):
        quantidade_giros = int(query.data.replace('giro_', ''))
        usuarios[user_id]['quantidade_giros'] = quantidade_giros

        # Sempre ir direto para a seleção de horário (sem proteção)
        keyboard = []
        for hora in range(0, 24, 4):
            fila_horas = [InlineKeyboardButton(f"{h:02d}:00", callback_data=f'horario_{h:02d}:00') for h in range(hora, min(hora + 4, 24))]
            keyboard.append(fila_horas)

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text="⏳ Selecione o horário para gerar a lista:",
            reply_markup=reply_markup
        )
        return
    elif query.data == 'continua':
        if usuarios[user_id]['modo'] == 'Crash 🚀':
            keyboard = [
                [InlineKeyboardButton("Vela 1.50 até 2x", callback_data='vela_1_80_2_80')],
                [InlineKeyboardButton("Vela 2x até 3x", callback_data='vela_2_80_3_00')],
                [InlineKeyboardButton("Vela 5x até 10x", callback_data='vela_5_10_')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                text="🎮 Escolha o valor das velas para gerar sua lista:",
                reply_markup=reply_markup
            )
        else:
            keyboard = [
                [InlineKeyboardButton("300", callback_data='giro_300'),
                InlineKeyboardButton("400", callback_data='giro_400'),
                InlineKeyboardButton("500", callback_data='giro_500'),
                InlineKeyboardButton("600", callback_data='giro_600')],
                [InlineKeyboardButton("700", callback_data='giro_700'),
                InlineKeyboardButton("800", callback_data='giro_800'),
                InlineKeyboardButton("900", callback_data='giro_900'),
                InlineKeyboardButton("1000", callback_data='giro_1000')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                text="📈 Selecione a quantidade de giros:",
                reply_markup=reply_markup
            )
        return

    elif query.data.startswith('giro_'):
        quantidade_giros = int(query.data.replace('giro_', ''))
        usuarios[user_id]['quantidade_giros'] = quantidade_giros

        # Verificar o modo e decidir se mostrar a proteção
        if usuarios[user_id]['modo'] != 'Crash 🚀':
            # Enviar a nova opção para escolha de gales
            keyboard = [
                [InlineKeyboardButton("0 Gales", callback_data='gales_0'),
                 InlineKeyboardButton("1 Gales", callback_data='gales_1'),
                 InlineKeyboardButton("2 Gales", callback_data='gales_2'),
                 InlineKeyboardButton("3 Gales", callback_data='gales_3'),],
                [InlineKeyboardButton("4 Gales", callback_data='gales_4'),
                 InlineKeyboardButton("5 Gales", callback_data='gales_5'),
                 InlineKeyboardButton("6 Gales", callback_data='gales_6'),
                 InlineKeyboardButton("7 Gales", callback_data='gales_7'),]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                text="🎯 Escolha a quantidade de gales:",
                reply_markup=reply_markup
            )
            return
        else:
            # Continuar para a seleção de horário diretamente se for modo Crash
            keyboard = []
            for hora in range(0, 24, 4):
                fila_horas = [InlineKeyboardButton(f"{h:02d}:00", callback_data=f'horario_{h:02d}:00') for h in range(hora, min(hora + 4, 24))]
                keyboard.append(fila_horas)

            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                text="⏳ Selecione o horário para gerar a lista:",
                reply_markup=reply_markup
            )
            return

    elif query.data.startswith('gales_'):
        quantidade_gales = int(query.data.replace('gales_', ''))
        usuarios[user_id]['quantidade_gales'] = quantidade_gales

        # Enviar a nova opção para escolha de proteção apenas se o modo não for "Crash 🚀"
        if usuarios[user_id]['modo'] != 'Crash 🚀':
            keyboard = [
                [InlineKeyboardButton("Proteger Branco", callback_data='protecao_branco')],
                [InlineKeyboardButton("Não Proteger", callback_data='protecao_nao_branco')],
                [InlineKeyboardButton("Lista Somente Branco", callback_data='protecao_somente_branco')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                text="🛡️ Escolha a proteção:",
                reply_markup=reply_markup
            )
            return
        else:
            # Pular para a seleção de horário diretamente
            keyboard = []
            for hora in range(0, 24, 4):
                fila_horas = [InlineKeyboardButton(f"{h:02d}:00", callback_data=f'horario_{h:02d}:00') for h in range(hora, min(hora + 4, 24))]
                keyboard.append(fila_horas)

            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                text="⏳ Selecione o horário para gerar a lista:",
                reply_markup=reply_markup
            )
            return

    elif query.data.startswith('protecao_'):
        protecao = query.data.replace('protecao_', '')
        usuarios[user_id]['protecao'] = protecao

        # Agora que temos a escolha de proteção, continuar com o fluxo, selecionando o horário
        keyboard = []
        for hora in range(0, 24, 4):
            fila_horas = [InlineKeyboardButton(f"{h:02d}:00", callback_data=f'horario_{h:02d}:00') for h in range(hora, min(hora + 4, 24))]
            keyboard.append(fila_horas)

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text="⏳ Selecione o horário para gerar a lista:",
            reply_markup=reply_markup
        )
        return

    elif query.data.startswith('vela_'):
        if query.data == 'vela_1_80_2_80':
            usuarios[user_id]['valor_vela'] = "1.50x a 2x"
        elif query.data == 'vela_2_80_3_00':
            usuarios[user_id]['valor_vela'] = "2X a 3X"
        elif query.data == 'vela_5_10_':
            usuarios[user_id]['valor_vela'] = "5X a 10X"

        keyboard = [
            [InlineKeyboardButton("0 Gales", callback_data='gales_0'),
                 InlineKeyboardButton("1 Gales", callback_data='gales_1'),
                 InlineKeyboardButton("2 Gales", callback_data='gales_2'),
                 InlineKeyboardButton("3 Gales", callback_data='gales_3'),],
                [InlineKeyboardButton("4 Gales", callback_data='gales_4'),
                 InlineKeyboardButton("5 Gales", callback_data='gales_5'),
                 InlineKeyboardButton("6 Gales", callback_data='gales_6'),
                 InlineKeyboardButton("7 Gales", callback_data='gales_7'),]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text="🎯 Escolha a quantidade de gales:",
            reply_markup=reply_markup
        )
        return


    elif query.data.startswith('horario_'):
        horario = query.data.replace('horario_', '')
        usuario = usuarios[user_id]
        plataforma = usuario['plataforma']
        modo = usuario['modo']
        protecao = usuario.get('protecao', 'nao_branco')

        # Definir o horário corretamente
        try:
            inicio = datetime.strptime(f'{horario}:00', '%H:%M:%S')
            fim = inicio + timedelta(hours=1)
        except ValueError:
            await query.edit_message_text(text="Formato de horário inválido. Por favor, tente novamente.")
            return

        lista_sinais = []

        # Lógica para gerar a lista de sinais
        if modo == 'Crash 🚀':
            valor_vela = usuario.get('valor_vela')
            lista_sinais = gerar_lista_sinais_crash(inicio, fim, valor_vela)
        elif modo == 'Aviator 🔺':
            valor_vela = usuario.get('valor_vela')
            lista_sinais = gerar_lista_sinais_crash(inicio, fim, valor_vela)
        elif modo == 'Bac Bo 🎲':
            lista_sinais = gerar_lista_sinais_bacbo(inicio, fim)
        elif plataforma == 'BLAZE':
            # Verifica se o usuário deseja gerar sinais apenas com a cor branca
            if usuario.get('somente_branco'):
                protecao = 'somente_branco'  # Define a proteção como somente branco
            else:
               protecao = usuario.get('protecao', 'protecao_nao_branco')  # Proteção padrão
            if usuario.get('meta_diaria'):
                lista_sinais = gerar_metadiaria_blaze(inicio, fim, protecao)
            else:
                lista_sinais = gerar_lista_sinais_blaze_protegida(inicio, fim, protecao)
        elif plataforma == 'JONBET':
            if usuario.get('meta_diaria'):
                lista_sinais = gerar_metadiaria_jonbet(inicio, fim, protecao)
            else:
                lista_sinais = gerar_lista_sinais_jonbet_protegida(inicio, fim, protecao)
        elif plataforma == 'SMASHUP':
            lista_sinais = gerar_lista_sinais_smashup(inicio, fim, protecao)
        elif plataforma == 'BRABET':
            lista_sinais = gerar_lista_sinais_smashup(inicio, fim, protecao)
        else:
            # Gera lista genérica ou mensagem de erro
            lista_sinais = gerar_lista_sinais_crash(inicio, fim, valor_vela)
        print(lista_sinais)  # Debug: imprime a lista de sinais gerada

        if not lista_sinais:
            mensagem_final = "Nenhum sinal gerado."
        else:
            if isinstance(lista_sinais, list):
                lista_formatada = "\n".join(lista_sinais)
                if modo == 'Bac Bo 🎲':
                    mensagem_final = f"{lista_formatada}\n\n🔴=VERMELHO\n🔵=AZUL\n🟠=EMPATE"
                else:
                    mensagem_final = f"\n\n{lista_formatada}"
            else:
                mensagem_final = lista_sinais  # Caso "somente_branco", já está formatado

        keyboard = [
            # Adicione os botões aqui, se necessário
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Atualiza o estado do usuário
        usuario['meta_diaria'] = False  # Reseta o estado se necessário

        await query.edit_message_text(
            text=mensagem_final,
            reply_markup=reply_markup
        )
async def iniciar_corretor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    teclado = [["Blaze", "Jonbet"]]
    if update.message:
        await update.message.reply_text(
            "Escolha a plataforma para corrigir a lista:",
            reply_markup=ReplyKeyboardMarkup(teclado, one_time_keyboard=True),
        )
    elif update.callback_query:
        await update.callback_query.answer()  # responde o callback para remover "loading"
        await update.callback_query.message.reply_text(
            "Escolha a plataforma para corrigir a lista:",
            reply_markup=ReplyKeyboardMarkup(teclado, one_time_keyboard=True),
        )
    else:
        # Caso não seja mensagem nem callback, pode logar ou ignorar
        print("Update inesperado sem message nem callback_query")
    return PERGUNTA_PLATAFORMA


async def receber_plataforma(update, context):
    plataforma = update.message.text.strip().lower()
    if plataforma not in ["blaze", "jonbet"]:
        await update.message.reply_text("Por favor, envie um valor válido: Blaze ou Jonbet")
        return PERGUNTA_PLATAFORMA
    context.user_data['plataforma'] = plataforma
    await update.message.reply_text(f"Você escolheu a plataforma: {plataforma.capitalize()}\nAgora, envie a quantidade de Gale (ex: G0, G1, G2):")
    return PERGUNTA_MARTINGALE

async def receber_martingale(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        texto = update.callback_query.data.upper()
        await update.callback_query.answer()
        chat_id = update.callback_query.from_user.id
    elif update.message:
        texto = update.message.text.upper()
        chat_id = update.message.chat_id
    else:
        return PERGUNTA_MARTINGALE  # ou outra ação

    if texto.startswith("G") and texto[1:].isdigit():
        max_gale = int(texto[1:])
        context.user_data["max_gale"] = max_gale
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"📊 Quantidade de Gale: {max_gale}\n👇 Cole sua lista de sinais aqui (separados por linha):",
            reply_markup=ReplyKeyboardRemove()
        )
        return RECEBE_LISTA
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Por favor, envie um valor válido, ex: G0, G1, G2"
        )
        return PERGUNTA_MARTINGALE


async def receber_lista(update: Update, context: ContextTypes.DEFAULT_TYPE):
    plataforma = context.user_data.get("plataforma", "blaze")
    max_gale = context.user_data.get("max_gale", 0)
    texto = update.message.text.strip()
    linhas = texto.splitlines()
    sinais_com_hora = []

    for linha in linhas:
        match_sinal = re.findall(r"[⚫️🔴🟢⚪️]{1,2}", linha)
        match_hora = re.findall(r"\b\d{2}:\d{2}\b", linha)
        if match_sinal and match_hora:
            sinal = "".join(match_sinal)
            hora = match_hora[0]
            sinais_com_hora.append(f"{sinal} {hora}")

    if not sinais_com_hora:
        await update.message.reply_text("Lista inválida! Envie sinais no formato: 🔴⚪️ 22:48")
        return RECEBE_LISTA

    print(f"DEBUG: Plataforma escolhida: {plataforma}")
    if plataforma == "blaze":
        if sinais_tem_verde(sinais_com_hora):
            await update.message.reply_text(
                "⚠️ Você escolheu Blaze, mas a lista contém sinais com verde, que só existem na Jonbet. Por favor, escolha Jonbet."
            )
            return RECEBE_LISTA
        historico = carregar_historico_local()
        mapa_cores_api = MAPA_CORES_API_BLAZE  # corrigido aqui
        
    else:
        historico = carregar_historico_jonbet()
        mapa_cores_api = MAPA_CORES_API_JONBET

    if not historico:
        await update.message.reply_text("Histórico vazio. Aguarde a atualização automática ou tente novamente mais tarde.")
        return ConversationHandler.END

    historico = list(reversed(historico))  # ordem cronológica

    resultados, acertos, erros, brancos = corrigir_lista_com_gales_por_hora_exata(
        sinais_com_hora, historico, max_gale, mapa_cores_api
    )

    mensagem = formatar_resposta_com_linhas_originais(resultados, acertos, erros, brancos, max_gale)
    await update.message.reply_text(mensagem)
    return ConversationHandler.END



async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operação cancelada.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def job_atualizar_historico(context: ContextTypes.DEFAULT_TYPE):
    atualizar_historico_incremental_blaze()
    atualizar_historico_incremental_jonbet()


async def main() -> None:
    # Habilitar o suporte para nested async loops
    nest_asyncio.apply()
    # Fix: APScheduler (usado pelo JobQueue) só aceita timezones pytz;
    # get_localzone() pode retornar zoneinfo no Python 3.9+, causando TypeError.
    import apscheduler.util
    apscheduler.util.get_localzone = lambda: pytz.UTC
    application = ApplicationBuilder().token(TOKEN).build()
    job_queue = application.job_queue

    # Definir conv_handler_corretor antes de usar
    job_queue.run_repeating(job_atualizar_historico, interval=20, first=10)  
    conv_handler_corretor = ConversationHandler(
    entry_points=[CallbackQueryHandler(iniciar_corretor, pattern='^corrigir_listas$')],
    states={
        PERGUNTA_PLATAFORMA: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receber_plataforma),
        ],
        PERGUNTA_MARTINGALE: [
            CallbackQueryHandler(receber_martingale),
            MessageHandler(filters.TEXT & ~filters.COMMAND, receber_martingale),
        ],
        RECEBE_LISTA: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receber_lista),
        ],
    },
    fallbacks=[CommandHandler("cancelar", cancelar)],
)


    # Adicionar handlers de comandos e callbacks
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('enviar_mensagem_massa', enviar_mensagem_massa))
    application.add_handler(conv_handler_corretor)
    application.add_handler(CallbackQueryHandler(button))


    # Iniciar o bot
    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
