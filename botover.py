import requests
from datetime import datetime
import time

# --- CONFIGURAÇÕES ---
# Coloquei sua nova chave aqui
API_KEY = "599828fb82d9733e4b73e586a1f4bb96c57ca6304d1516dbc3f678de951a2a74"
TOKEN = "8250855619:AAHDskywDr3a1zg6WPoZTnWLIF24rDvvTNE"
CHAT_ID = "7997581470"

headers = {'x-apisports-key': API_KEY}

def enviar_alerta(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={mensagem}&parse_mode=Markdown"
    try:
        requests.get(url)
    except:
        pass

def rodar_automacao():
    jogos_notificados = set()
    print(f"🚀 {datetime.now().strftime('%H:%M:%S')} | Ronny P v7.5: NOVA CHAVE ATIVADA")
    print(f"📡 Monitorando jogos em tempo real...")

    while True:
        try:
            # Busca todos os jogos em LIVE (Modo Global para garantir volume)
            url = "https://v3.football.api-sports.io/fixtures?live=all&timezone=America/Sao_Paulo"
            response = requests.get(url, headers=headers).json()
            
            # Verifica se a chave deu erro de limite
            if 'errors' in response and response['errors']:
                print(f"⚠️ Alerta da API: {response['errors']}")
                break

            jogos = response.get('response', [])
            print(f"--- Varredura {datetime.now().strftime('%H:%M:%S')} | {len(jogos)} jogos detectados ---")

            for j in jogos:
                id_jogo = j['fixture']['id']
                
                if id_jogo not in jogos_notificados:
                    status = j['fixture']['status']['short']
                    minuto = j['fixture']['status']['elapsed']
                    g_casa = j['goals']['home'] or 0
                    g_fora = j['goals']['away'] or 0
                    
                    # ESTRATÉGIA: Over 0.5 HT (0x0 entre 15' e 35' do 1º Tempo)
                    if status == '1H' and 15 <= minuto <= 35 and g_casa == 0 and g_fora == 0:
                        time_casa = j['teams']['home']['name']
                        time_fora = j['teams']['away']['name']
                        liga = j['league']['name']
                        
                        msg = (
                            f"⚠️ *ENTRADA LIVE: OVER 0.5 HT* ⚠️\n\n"
                            f"🆚 *{time_casa} x {time_fora}*\n"
                            f"🏆 Liga: {liga}\n"
                            f"⏰ Minuto: {minuto}' | Placar: 0-0\n"
                            f"🎯 Estratégia: Golo na 1ª Parte\n\n"
                            f"🤖 *Ronny P Scanner*"
                        )
                        enviar_alerta(msg)
                        jogos_notificados.add(id_jogo)
                        print(f"✅ SINAL ENVIADO: {time_casa} x {time_fora}")

        except Exception as e:
            print(f"❌ Erro no loop: {e}")
        
        # Espera 1 minuto para a próxima varredura
        time.sleep(60)

if __name__ == "__main__":
    rodar_automacao()