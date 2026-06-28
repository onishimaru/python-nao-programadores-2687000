import asyncio
import edge_tts
import pygame
import tempfile
import os
import time
import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wav
import keyboard
from faster_whisper import WhisperModel
from datetime import datetime
from groq import Groq

# ============================================================
#  CONFIGURAÇÃO — edite apenas esta seção
# ============================================================
VOZ = "pt-BR-AntonioNeural"   # Voz masculina em português
NOME = "Jarvis"
TECLA_FALAR = "ctrl"          # Segure esta tecla para falar

# Cole aqui sua chave gratuita do Groq (console.groq.com)
GROQ_API_KEY = "cole_sua_chave_aqui"
# ============================================================

SAMPLE_RATE = 16000
MAX_HISTORICO = 20  # lembra as últimas 10 trocas de conversa

print("=" * 45)
print(f"    {NOME} - Assistente Pessoal")
print("=" * 45)
print("Carregando reconhecimento de voz...")
print("(Primeira vez: faz download do modelo ~150MB)")

modelo_voz = WhisperModel("base", device="cpu", compute_type="int8")
pygame.mixer.init()

if GROQ_API_KEY == "cole_sua_chave_aqui":
    print("\n⚠️  ATENÇÃO: Substitua GROQ_API_KEY no código pela sua chave do Groq.")
    print("   Acesse console.groq.com para obter sua chave gratuita.\n")

cliente_ia = Groq(api_key=GROQ_API_KEY)
historico = []

print("Pronto!")
print(f"  Segure [{TECLA_FALAR.upper()}] para falar")
print("  Pressione [ESC] para sair")
print("=" * 45)


def obter_data_hora():
    dias = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira",
            "sexta-feira", "sábado", "domingo"]
    meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
             "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    d = datetime.now()
    return (
        f"{dias[d.weekday()]}, {d.day} de {meses[d.month - 1]} de {d.year}, "
        f"{d.strftime('%H:%M')}"
    )


def responder_ia(texto):
    """Envia a mensagem para a IA e retorna a resposta."""
    global historico

    sistema = (
        f"Você é {NOME}, um assistente pessoal inteligente, eficiente e discreto. "
        "Responda sempre em português brasileiro. "
        "Seja direto e conciso, pois suas respostas serão convertidas em fala. "
        "Nunca use listas com traços, asteriscos, hashtags ou símbolos especiais. "
        "Fale de forma natural e conversacional, como se estivesse ao lado da pessoa. "
        f"Data e hora atual: {obter_data_hora()}."
    )

    historico.append({"role": "user", "content": texto})

    if len(historico) > MAX_HISTORICO:
        historico = historico[-MAX_HISTORICO:]

    resposta = cliente_ia.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": sistema}] + historico,
        max_tokens=300,
        temperature=0.7,
    )

    texto_resposta = resposta.choices[0].message.content.strip()
    historico.append({"role": "assistant", "content": texto_resposta})

    return texto_resposta


def falar(texto):
    """Faz o Jarvis falar em voz alta."""
    print(f"\n{NOME}: {texto}")

    async def _falar():
        tts = edge_tts.Communicate(texto, VOZ)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            caminho = f.name
        await tts.save(caminho)
        pygame.mixer.music.load(caminho)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.1)
        pygame.mixer.music.unload()
        os.unlink(caminho)

    asyncio.run(_falar())


def gravar_voz():
    """Grava áudio com push-to-talk e transcreve com Whisper."""
    print(f"\n[ Segure [{TECLA_FALAR.upper()}] para falar | ESC para sair ]")

    while True:
        if keyboard.is_pressed("esc"):
            return None
        if keyboard.is_pressed(TECLA_FALAR):
            break
        time.sleep(0.05)

    print("  Gravando... (solte quando terminar)")

    frames = []
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="float32") as stream:
        while keyboard.is_pressed(TECLA_FALAR):
            data, _ = stream.read(SAMPLE_RATE // 10)
            frames.append(data.copy())

    if len(frames) < 3:
        return ""

    audio = np.concatenate(frames, axis=0).squeeze()

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        caminho_wav = f.name

    wav.write(caminho_wav, SAMPLE_RATE, (audio * 32767).astype(np.int16))

    print("  Transcrevendo...")
    segments, _ = modelo_voz.transcribe(caminho_wav, language="pt")
    texto = " ".join([s.text for s in segments]).strip()

    os.unlink(caminho_wav)
    return texto


def main():
    falar(
        f"Sistemas inicializados. Olá, sou o {NOME}, seu assistente pessoal. "
        "Segure a tecla control para falar comigo."
    )

    while True:
        texto = gravar_voz()

        if texto is None:
            falar("Encerrando sistemas. Até a próxima.")
            break

        if not texto:
            continue

        print(f"\nVocê: {texto}")

        if any(p in texto.lower() for p in ["sair", "encerrar", "desligar", "tchau", "até logo"]):
            falar("Encerrando sistemas. Até a próxima.")
            break

        print("  Pensando...")
        try:
            resposta = responder_ia(texto)
        except Exception as e:
            resposta = "Desculpe, tive um problema de conexão. Tente novamente em instantes."
            print(f"  Erro: {e}")

        falar(resposta)


if __name__ == "__main__":
    main()
