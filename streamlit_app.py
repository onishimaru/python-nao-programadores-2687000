"""Gerador de anúncios para WhatsApp — interface web (Streamlit)."""

import os
import anthropic
import streamlit as st

FOOTER = "*📌O preço e disponibilidade do produto podem variar, pois as promoções são por tempo limitado.*\n\n#anúncio"


def get_secret(key):
    try:
        return st.secrets[key]
    except Exception:
        return os.environ.get(key, "")


def check_password():
    app_password = get_secret("APP_PASSWORD")
    if not app_password:
        return  # sem senha configurada, libera acesso

    if st.session_state.get("authenticated"):
        return

    st.title("🔒 Acesso restrito")
    senha = st.text_input("Senha:", type="password", placeholder="Digite a senha de acesso")
    if st.button("Entrar", type="primary"):
        if senha == app_password:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Senha incorreta.")
    st.stop()


def get_api_key():
    return get_secret("ANTHROPIC_API_KEY")


def generate_phrase(client, description, price_display, shipping_info):
    prompt_parts = [f"Produto: {description}"]
    if price_display:
        prompt_parts.append(f"Preço: {price_display}")
    if shipping_info:
        prompt_parts.append(f"Informação de entrega: {shipping_info}")

    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=150,
        messages=[
            {
                "role": "user",
                "content": (
                    "Crie uma frase curta e chamativa em português para anúncio no WhatsApp sobre este produto. "
                    "Use no máximo 2 linhas, seja empolgante, use emojis relevantes e destaque o benefício principal. "
                    f"Retorne APENAS a frase, sem aspas, sem explicações.\n\n{chr(10).join(prompt_parts)}"
                ),
            }
        ],
    )
    return response.content[0].text.strip()


def format_price_section(price_type, **kwargs):
    if price_type == "unico":
        return kwargs["price"]
    elif price_type == "promocao":
        return f"~{kwargs['old_price']}~\n{kwargs['new_price']}"
    elif price_type == "faixa":
        return kwargs["range_price"]
    return ""


# ── Página ──────────────────────────────────────────────────────────────────

st.set_page_config(page_title="Gerador de Anúncios", page_icon="🛒", layout="centered")
check_password()
st.title("🛒 Gerador de Anúncios para WhatsApp")
st.markdown("Preencha os campos abaixo e clique em **Gerar Anúncio**.")

api_key = get_api_key()
if not api_key:
    st.error(
        "⚠️ Chave da API não encontrada. "
        "Adicione `ANTHROPIC_API_KEY` nos Secrets do Streamlit Cloud "
        "ou na variável de ambiente antes de rodar."
    )
    st.stop()

st.divider()

link = st.text_input("🔗 Link do produto", placeholder="https://...")
description = st.text_area("📝 Enunciado do produto", placeholder="Descreva o produto aqui...", height=100)

st.markdown("**💰 Tipo de preço**")
price_type_label = st.radio(
    "Tipo de preço",
    ["Preço único", "Promoção (preço antigo + novo preço)", "Faixa de preço"],
    label_visibility="collapsed",
)

price_section = ""
price_display = ""

if price_type_label == "Preço único":
    price = st.text_input("Preço", placeholder="R$ 99,90")
    if price:
        price_section = format_price_section("unico", price=price)
        price_display = price

elif price_type_label == "Promoção (preço antigo + novo preço)":
    col1, col2 = st.columns(2)
    with col1:
        old_price = st.text_input("Preço antigo", placeholder="R$ 149,90")
    with col2:
        new_price = st.text_input("Novo preço", placeholder="R$ 89,90")
    if old_price and new_price:
        price_section = format_price_section("promocao", old_price=old_price, new_price=new_price)
        price_display = f"{old_price} → {new_price}"

else:
    range_price = st.text_input("Faixa de preço", placeholder="De R$ 15,00 a R$ 27,00")
    if range_price:
        price_section = format_price_section("faixa", range_price=range_price)
        price_display = range_price

st.markdown("**🚚 Informação de envio**")
shipping_label = st.radio(
    "Envio",
    ["Sem informação de envio", "🌍 Compra internacional", "🇧🇷 Já está no Brasil"],
    label_visibility="collapsed",
)

if shipping_label == "🌍 Compra internacional":
    shipping_line = "🌍 Compra internacional"
    shipping_info = "compra internacional"
elif shipping_label == "🇧🇷 Já está no Brasil":
    shipping_line = "🇧🇷 Já está no Brasil"
    shipping_info = "já está no Brasil"
else:
    shipping_line = ""
    shipping_info = ""

st.divider()

if st.button("✨ Gerar Anúncio", type="primary", use_container_width=True):
    if not link:
        st.warning("Por favor, informe o link do produto.")
    elif not description:
        st.warning("Por favor, informe o enunciado do produto.")
    elif not price_section:
        st.warning("Por favor, preencha as informações de preço.")
    else:
        with st.spinner("Gerando frase com IA..."):
            try:
                client = anthropic.Anthropic(api_key=api_key)
                phrase = generate_phrase(client, description, price_display, shipping_info)

                lines = [phrase, price_section]
                if shipping_line:
                    lines.append(shipping_line)
                lines += ["", description, "", link, "", FOOTER]

                ad = "\n".join(lines)

                st.success("Anúncio gerado com sucesso!")
                st.text_area("📣 Seu anúncio (copie o texto abaixo):", value=ad, height=320)
                st.download_button(
                    label="💾 Baixar como .txt",
                    data=ad,
                    file_name="anuncio.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
            except anthropic.AuthenticationError:
                st.error("❌ Chave de API inválida. Verifique o valor de ANTHROPIC_API_KEY.")
            except Exception as e:
                st.error(f"❌ Erro ao gerar anúncio: {e}")
