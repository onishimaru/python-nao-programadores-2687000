import os
import tempfile
from datetime import datetime
from groq import Groq
from faster_whisper import WhisperModel
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

# ============================================================
#  CONFIGURAÇÃO
#
#  Na nuvem (Railway): configure as variáveis de ambiente no painel.
#  No computador local: preencha os valores entre aspas abaixo.
# ============================================================
GROQ_API_KEY    = os.environ.get("GROQ_API_KEY",    "cole_sua_chave_do_groq_aqui")
TELEGRAM_TOKEN  = os.environ.get("TELEGRAM_TOKEN",  "cole_o_token_do_botfather_aqui")

# Seu ID do Telegram (mande /start no bot para descobrir).
# 0 = aceita qualquer pessoa (não recomendado).
MEU_ID_TELEGRAM = int(os.environ.get("MEU_ID_TELEGRAM", "0"))
# ============================================================

NOME = "Jarvis"
MAX_HISTORICO = 20

print("Carregando modelo de reconhecimento de voz...")
modelo_voz = WhisperModel("base", device="cpu", compute_type="int8")
cliente_ia = Groq(api_key=GROQ_API_KEY)
historicos = {}

print("Pronto! Conectando ao Telegram...")


def obter_data_hora():
    dias = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira",
            "sexta-feira", "sábado", "domingo"]
    meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
             "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    d = datetime.now()
    return f"{dias[d.weekday()]}, {d.day} de {meses[d.month - 1]} de {d.year}, {d.strftime('%H:%M')}"


def autorizado(update: Update) -> bool:
    if MEU_ID_TELEGRAM == 0:
        return True
    return update.effective_user.id == MEU_ID_TELEGRAM


def responder_ia(texto, chat_id):
    if chat_id not in historicos:
        historicos[chat_id] = []

    historico = historicos[chat_id]

    sistema = (
        f"Você é {NOME}, um assistente pessoal inteligente, eficiente e discreto. "
        "Responda sempre em português brasileiro. "
        "Seja direto e conciso. "
        "Pode usar negrito com *texto* quando quiser destacar algo. "
        f"Data e hora atual: {obter_data_hora()}."
    )

    historico.append({"role": "user", "content": texto})

    if len(historico) > MAX_HISTORICO:
        historicos[chat_id] = historico[-MAX_HISTORICO:]
        historico = historicos[chat_id]

    resposta = cliente_ia.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": sistema}] + historico,
        max_tokens=500,
        temperature=0.7,
    )

    texto_resposta = resposta.choices[0].message.content.strip()
    historico.append({"role": "assistant", "content": texto_resposta})

    return texto_resposta


async def comando_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    nome = update.effective_user.first_name

    mensagem = (
        f"Sistemas inicializados\\. Olá, {nome}\\!\n\n"
        f"Sou o {NOME}, seu assistente pessoal\\.\n\n"
        f"💡 *Seu ID do Telegram é:* `{user_id}`\n"
        "Cole esse número em MEU\\_ID\\_TELEGRAM para ativar a segurança\\.\n\n"
        "Pode me mandar mensagens de texto ou áudio\\!"
    )

    await update.message.reply_text(mensagem, parse_mode="MarkdownV2")


async def comando_limpar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not autorizado(update):
        return
    historicos[update.effective_chat.id] = []
    await update.message.reply_text("Memória da conversa apagada. Podemos começar do zero.")


async def handle_texto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not autorizado(update):
        await update.message.reply_text("Acesso não autorizado.")
        return

    chat_id = update.effective_chat.id
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    try:
        resposta = responder_ia(update.message.text, chat_id)
    except Exception as e:
        resposta = "Desculpe, tive um problema de conexão. Tente novamente em instantes."
        print(f"Erro IA: {e}")

    await update.message.reply_text(resposta)


async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not autorizado(update):
        await update.message.reply_text("Acesso não autorizado.")
        return

    chat_id = update.effective_chat.id
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    arquivo = await context.bot.get_file(update.message.voice.file_id)

    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as f:
        caminho_ogg = f.name

    await arquivo.download_to_drive(caminho_ogg)

    try:
        segments, _ = modelo_voz.transcribe(caminho_ogg, language="pt")
        texto = " ".join([s.text for s in segments]).strip()
        os.unlink(caminho_ogg)
    except Exception as e:
        os.unlink(caminho_ogg)
        print(f"Erro Whisper: {e}")
        await update.message.reply_text("Não consegui entender o áudio. Pode repetir?")
        return

    if not texto:
        await update.message.reply_text("Não entendi o que foi dito. Pode repetir?")
        return

    try:
        resposta = responder_ia(texto, chat_id)
    except Exception as e:
        resposta = "Desculpe, tive um problema de conexão. Tente novamente."
        print(f"Erro IA: {e}")

    await update.message.reply_text(f'🎤 "{texto}"\n\n{resposta}')


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", comando_start))
    app.add_handler(CommandHandler("limpar", comando_limpar))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_texto))
    app.add_handler(MessageHandler(filters.VOICE, handle_audio))

    print(f"{NOME} está online no Telegram!")
    app.run_polling()


if __name__ == "__main__":
    main()
