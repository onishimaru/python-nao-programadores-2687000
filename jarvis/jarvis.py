import asyncio
import edge_tts
import pygame
import tempfile
import os
from datetime import datetime

VOZ = "pt-BR-AntonioNeural"  # Voz masculina em português brasileiro
NOME = "Jarvis"


async def falar(texto):
    """Faz o Jarvis falar em voz alta."""
    print(f"\n{NOME}: {texto}")

    tts = edge_tts.Communicate(texto, VOZ)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        caminho = f.name

    await tts.save(caminho)

    pygame.mixer.init()
    pygame.mixer.music.load(caminho)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        await asyncio.sleep(0.1)

    pygame.mixer.music.unload()
    os.unlink(caminho)


def responder(texto):
    """Lógica de resposta do assistente."""
    t = texto.lower().strip()

    if any(p in t for p in ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite"]):
        hora = datetime.now().hour
        if hora < 12:
            return "Bom dia! Como posso ajudá-lo?"
        elif hora < 18:
            return "Boa tarde! Estou à disposição."
        else:
            return "Boa noite! Em que posso ser útil?"

    if any(p in t for p in ["hora", "horas", "que horas"]):
        return f"São {datetime.now().strftime('%H e %M minutos')}."

    if any(p in t for p in ["data", "hoje", "que dia"]):
        dias = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira",
                "sexta-feira", "sábado", "domingo"]
        meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
                 "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
        d = datetime.now()
        return f"Hoje é {dias[d.weekday()]}, {d.day} de {meses[d.month - 1]} de {d.year}."

    if any(p in t for p in ["quem é você", "seu nome", "como se chama", "o que você é"]):
        return f"Sou {NOME}, seu assistente pessoal. Estou aqui para facilitar sua vida."

    if any(p in t for p in ["obrigado", "obrigada", "valeu"]):
        return "Disponha. É para isso que estou aqui."

    return "Entendido. Ainda estou em fase inicial. Em breve terei muito mais capacidades."


async def main():
    print("=" * 45)
    print(f"    {NOME} - Assistente Pessoal")
    print("=" * 45)
    print("  Digite 'sair' para encerrar\n")

    await falar(
        f"Sistemas inicializados. Olá, sou o {NOME}, seu assistente pessoal. Pronto para servir."
    )

    while True:
        try:
            entrada = input("\nVocê: ").strip()
        except (KeyboardInterrupt, EOFError):
            await falar("Encerrando. Até a próxima.")
            break

        if not entrada:
            continue

        if entrada.lower() in ["sair", "tchau", "encerrar"]:
            await falar("Encerrando sistemas. Até a próxima.")
            break

        resposta = responder(entrada)
        await falar(resposta)


if __name__ == "__main__":
    asyncio.run(main())
