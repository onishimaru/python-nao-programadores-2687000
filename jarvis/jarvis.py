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

VOZ = "pt-BR-AntonioNeural"  # Voz masculina em português brasileiro
NOME = "Jarvis"
TECLA_FALAR = "ctrl"        # Segure esta tecla para falar
SAMPLE_RATE = 16000

print("=" * 45)
print(f"    {NOME} - Assistente Pessoal")
print("=" * 45)
print("Carregando reconhecimento de voz...")
print("(Na primeira vez faz download do modelo ~150MB)")

modelo = WhisperModel("base", device="cpu", compute_type="int8")
pygame.mixer.init()

print("Pronto!")
print(f"  Segure [{TECLA_FALAR.upper()}] para falar")
print("  Pressione [ESC] para sair")
print("=" * 45)


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
    """
    Aguarda o usuário segurar CTRL, grava o áudio e transcreve com Whisper.
    Retorna o texto transcrito, string vazia se muito curto, ou None se ESC.
    """
    print(f"\n[ Segure [{TECLA_FALAR.upper()}] para falar | ESC para sair ]")

    # Aguarda o usuário pressionar a tecla ou ESC
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
            data, _ = stream.read(SAMPLE_RATE // 10)  # lê em blocos de 100ms
            frames.append(data.copy())

    if len(frames) < 3:  # menos de 300ms — muito curto para transcrever
        return ""

    audio = np.concatenate(frames, axis=0).squeeze()

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        caminho_wav = f.name

    wav.write(caminho_wav, SAMPLE_RATE, (audio * 32767).astype(np.int16))

    print("  Transcrevendo...")
    segments, _ = modelo.transcribe(caminho_wav, language="pt")
    texto = " ".join([s.text for s in segments]).strip()

    os.unlink(caminho_wav)
    return texto


def responder(texto):
    """Lógica de resposta do assistente."""
    t = texto.lower().strip()

    if not t:
        return "Não entendi. Tente falar novamente."

    if any(p in t for p in ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite"]):
        hora = datetime.now().hour
        if hora < 12:
            return "Bom dia! Como posso ajudá-lo?"
        elif hora < 18:
            return "Boa tarde! Estou à disposição."
        else:
            return "Boa noite! Em que posso ser útil?"

    if any(p in t for p in ["que horas", "hora", "horas"]):
        return f"São {datetime.now().strftime('%H e %M minutos')}."

    if any(p in t for p in ["que dia", "data", "hoje"]):
        dias = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira",
                "sexta-feira", "sábado", "domingo"]
        meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
                 "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
        d = datetime.now()
        return f"Hoje é {dias[d.weekday()]}, {d.day} de {meses[d.month - 1]} de {d.year}."

    if any(p in t for p in ["quem é você", "seu nome", "como se chama"]):
        return f"Sou {NOME}, seu assistente pessoal. Estou aqui para facilitar sua vida."

    if any(p in t for p in ["obrigado", "obrigada", "valeu"]):
        return "Disponha. É para isso que estou aqui."

    if any(p in t for p in ["sair", "encerrar", "desligar", "tchau", "até logo"]):
        return "ENCERRAR"

    return "Entendido. Ainda estou em fase inicial. Em breve terei muito mais capacidades."


def main():
    falar(
        f"Sistemas inicializados. Olá, sou o {NOME}, seu assistente pessoal. "
        f"Segure a tecla control para falar comigo."
    )

    while True:
        texto = gravar_voz()

        if texto is None:  # ESC pressionado
            falar("Encerrando sistemas. Até a próxima.")
            break

        if not texto:
            continue

        print(f"\nVocê: {texto}")

        resposta = responder(texto)

        if resposta == "ENCERRAR":
            falar("Encerrando sistemas. Até a próxima.")
            break

        falar(resposta)


if __name__ == "__main__":
    main()
