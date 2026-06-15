#!/usr/bin/env python3
"""Gerador de anúncios para WhatsApp com afiliados."""

import os
import anthropic

FOOTER = "*📌O preço e disponibilidade do produto podem variar, pois as promoções são por tempo limitado.*\n\n#anúncio"


def generate_phrase(client, description, price_display, shipping):
    prompt_parts = [f"Produto: {description}"]
    if price_display:
        prompt_parts.append(f"Preço: {price_display}")
    if shipping:
        prompt_parts.append(f"Informação de entrega: {shipping}")

    prompt = "\n".join(prompt_parts)

    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=150,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Crie uma frase curta e chamativa em português para anúncio no WhatsApp sobre este produto. "
                    f"Use no máximo 2 linhas, seja empolgante, use emojis relevantes e destaque o benefício principal. "
                    f"Retorne APENAS a frase, sem aspas, sem explicações.\n\n{prompt}"
                ),
            }
        ],
    )
    return response.content[0].text.strip()


def format_price_section(price_type, **kwargs):
    if price_type == "unico":
        return kwargs["price"]
    elif price_type == "promocao":
        old = kwargs["old_price"]
        new = kwargs["new_price"]
        return f"~{old}~\n{new}"
    elif price_type == "faixa":
        return kwargs["range_price"]
    return ""


def get_input(prompt, required=True):
    while True:
        value = input(prompt).strip()
        if value or not required:
            return value
        print("  ⚠️  Este campo é obrigatório. Por favor, preencha.")


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ Erro: a variável de ambiente ANTHROPIC_API_KEY não está definida.")
        print("   Configure-a com: export ANTHROPIC_API_KEY='sua-chave'")
        return

    client = anthropic.Anthropic(api_key=api_key)

    print("\n🛒 Gerador de Anúncios para WhatsApp")
    print("=" * 40)

    link = get_input("\n🔗 Link do produto: ")
    description = get_input("📝 Enunciado do produto: ")

    print("\n💰 Tipo de preço:")
    print("  1 - Preço único")
    print("  2 - Promoção (preço antigo + novo preço)")
    print("  3 - Faixa de preço")

    while True:
        choice = get_input("Escolha (1/2/3): ")
        if choice in ("1", "2", "3"):
            break
        print("  ⚠️  Opção inválida. Digite 1, 2 ou 3.")

    price_display = ""
    if choice == "1":
        price = get_input("Preço (ex: R$ 99,90): ")
        price_section = format_price_section("unico", price=price)
        price_display = price
    elif choice == "2":
        old_price = get_input("Preço antigo (ex: R$ 149,90): ")
        new_price = get_input("Novo preço (ex: R$ 89,90): ")
        price_section = format_price_section("promocao", old_price=old_price, new_price=new_price)
        price_display = f"{old_price} → {new_price}"
    else:
        range_price = get_input("Faixa de preço (ex: De R$ 15,00 a R$ 27,00): ")
        price_section = format_price_section("faixa", range_price=range_price)
        price_display = range_price

    print("\n🚚 Informação de envio:")
    print("  1 - Compra internacional")
    print("  2 - Já está no Brasil")
    print("  3 - Sem informação de envio")

    while True:
        ship_choice = get_input("Escolha (1/2/3): ")
        if ship_choice in ("1", "2", "3"):
            break
        print("  ⚠️  Opção inválida. Digite 1, 2 ou 3.")

    if ship_choice == "1":
        shipping_line = "🌍 Compra internacional"
        shipping_info = "compra internacional"
    elif ship_choice == "2":
        shipping_line = "🇧🇷 Já está no Brasil"
        shipping_info = "já está no Brasil"
    else:
        shipping_line = ""
        shipping_info = ""

    print("\n⏳ Gerando frase com IA...")
    phrase = generate_phrase(client, description, price_display, shipping_info)

    lines = [phrase, price_section]
    if shipping_line:
        lines.append(shipping_line)
    lines += ["", description, "", link, "", FOOTER]

    ad = "\n".join(lines)

    print("\n" + "=" * 40)
    print("📣 ANÚNCIO GERADO:\n")
    print(ad)
    print("=" * 40)

    save = input("\n💾 Deseja salvar o anúncio em um arquivo .txt? (s/N): ").strip().lower()
    if save == "s":
        filename = input("Nome do arquivo (sem extensão): ").strip() or "anuncio"
        filepath = f"{filename}.txt"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(ad)
        print(f"✅ Anúncio salvo em: {filepath}")


if __name__ == "__main__":
    main()
