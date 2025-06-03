import requests
import time

def obter_endereco_real(lat: float, lon: float, tentativas: int = 3) -> str:
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&accept-language=pt-BR"
    headers = {
        "User-Agent": "DacaSystem/1.0 (contato@dacasystem.com)"
    }

    for tentativa in range(tentativas):
        try:
            resposta = requests.get(url, headers=headers, timeout=5)
            if resposta.status_code == 200:
                dados = resposta.json()
                endereco = dados.get("display_name")
                if endereco:
                    print(f"[✓] Endereço resolvido: {endereco}")
                    return endereco
                else:
                    print("[!] Endereço não encontrado")
                    return "Endereço não encontrado"
            else:
                print(f"[!] HTTP {resposta.status_code}")
                return "Erro ao buscar endereço"
        except requests.Timeout:
            print(f"[⏳] Timeout ({tentativa + 1}/{tentativas})")
            time.sleep(1)
        except Exception as e:
            print(f"[‼️] Erro inesperado: {e}")
            return "Erro inesperado"

    return "Erro: timeout após várias tentativas"
