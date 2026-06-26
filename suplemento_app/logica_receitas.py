# logica_receitas.py
# Lógica de geração de receitas e cálculo nutricional

from banco_ingredientes import INGREDIENTES, OBJETIVOS


# Receitas base para cada objetivo (ingrediente_id -> gramas)
RECEITAS_BASE = {
    "massa": {
        "nome": "Power Shake de Massa Natural",
        "ingredientes": {
            "clara_de_ovo_em_po": 30,
            "aveia_em_flocos": 50,
            "semente_de_canhamo": 15,
            "cacau_em_po": 10,
            "linhaca_dourada": 10,
            "levedo_de_cerveja": 8,
        },
        "preparo": [
            "Misture todos os ingredientes secos em um recipiente com tampa hermética.",
            "Na hora de consumir, adicione 250–300 ml de água, leite vegetal (aveia, coco ou amêndoa) ou leite desnatado.",
            "Agite vigorosamente por 30 segundos ou bata no liquidificador por 20 segundos.",
            "Consuma imediatamente após o preparo para preservar os nutrientes.",
        ],
        "rendimento_doses": 1,
        "armazenamento": "O pó seco pode ser pré-misturado e armazenado em pote hermético por até 30 dias em local seco e fresco.",
    },
    "gordura": {
        "nome": "Shake Termogênico Natural",
        "ingredientes": {
            "proteina_de_ervilha": 25,
            "espirulina": 8,
            "semente_de_chia": 15,
            "linhaca_dourada": 10,
            "cacau_em_po": 12,
            "canela_em_po": 3,
            "gengibre_em_po": 2,
            "maca_peruana": 5,
        },
        "preparo": [
            "Misture todos os ingredientes secos em um pote ou shaker.",
            "Adicione 250 ml de água gelada ou leite vegetal sem açúcar.",
            "Agite bem ou bata no liquidificador com cubos de gelo.",
            "Para a chia não empelotar, agite primeiro com metade da água, espere 2 minutos e adicione o resto.",
        ],
        "rendimento_doses": 1,
        "armazenamento": "Pó seco em pote hermético por até 30 dias. Shake pronto consumir em até 30 minutos.",
    },
    "resistencia": {
        "nome": "Pré-Treino de Endurance Natural",
        "ingredientes": {
            "beterraba_em_po": 10,
            "farinha_de_banana_verde": 30,
            "aveia_em_flocos": 30,
            "tamara_em_po": 15,
            "espirulina": 8,
            "linhaca_dourada": 10,
        },
        "preparo": [
            "Misture todos os ingredientes secos.",
            "Dissolva em 300–400 ml de água fria (ou água de coco para ainda mais eletrólitos).",
            "Agite bem no shaker ou bata no liquidificador.",
            "Consuma 45–60 minutos antes do treino ou prova.",
        ],
        "rendimento_doses": 1,
        "armazenamento": "Pó seco em pote hermético por até 30 dias. Consuma o líquido em até 1 hora.",
    },
    "recuperacao": {
        "nome": "Shake Recuperação Muscular Natural",
        "ingredientes": {
            "clara_de_ovo_em_po": 28,
            "semente_de_canhamo": 18,
            "tamara_em_po": 20,
            "cacau_em_po": 10,
            "curcuma": 3,
            "gengibre_em_po": 2,
            "linhaca_dourada": 10,
        },
        "preparo": [
            "Misture todos os ingredientes secos.",
            "Adicione 250 ml de leite vegetal (aveia ou coco recomendados) ou leite desnatado.",
            "Bata no liquidificador por 30 segundos para textura cremosa.",
            "Opcionalmente adicione 1 banana madura para mais carboidratos e potássio.",
            "Consuma imediatamente após o treino.",
        ],
        "rendimento_doses": 1,
        "armazenamento": "Pó seco em pote hermético por até 30 dias.",
    },
    "energia": {
        "nome": "Pré-Treino Energético Natural",
        "ingredientes": {
            "farinha_de_banana_verde": 25,
            "tamara_em_po": 20,
            "amendoim_em_po": 15,
            "guarana_em_po": 3,
            "levedo_de_cerveja": 8,
            "cacau_em_po": 8,
            "canela_em_po": 3,
        },
        "preparo": [
            "Misture todos os ingredientes secos.",
            "Dissolva em 200–250 ml de água morna (ajuda a dissolver melhor) ou água gelada.",
            "Agite no shaker ou misture bem com colher.",
            "Consuma 20–30 minutos antes do treino.",
            "⚠️ O guaraná contém cafeína natural (~120mg/dose). Evite após as 16h se sensível à cafeína.",
        ],
        "rendimento_doses": 1,
        "armazenamento": "Pó seco em pote hermético por até 30 dias em local seco.",
    },
}


def calcular_nutricao_receita(ingredientes_com_gramas: dict) -> dict:
    """Calcula a tabela nutricional completa para uma combinação de ingredientes."""
    totais = {
        "kcal": 0.0,
        "proteinas_g": 0.0,
        "carboidratos_g": 0.0,
        "fibras_g": 0.0,
        "gorduras_g": 0.0,
        "gorduras_sat_g": 0.0,
        "sodio_mg": 0.0,
        "potassio_mg": 0.0,
        "calcio_mg": 0.0,
        "ferro_mg": 0.0,
        "magnesio_mg": 0.0,
        "zinco_mg": 0.0,
    }

    for ing_id, gramas in ingredientes_com_gramas.items():
        if ing_id not in INGREDIENTES:
            continue
        nutri = INGREDIENTES[ing_id]["nutri"]
        fator = gramas / 100.0
        for campo in totais:
            totais[campo] += nutri.get(campo, 0) * fator

    totais["peso_total_g"] = sum(ingredientes_com_gramas.values())
    return totais


def calcular_aminograma_receita(ingredientes_com_gramas: dict) -> dict:
    """Calcula o aminograma total da receita (em gramas por porção)."""
    totais_aa = {}

    for ing_id, gramas in ingredientes_com_gramas.items():
        if ing_id not in INGREDIENTES:
            continue
        aa_ing = INGREDIENTES[ing_id].get("aa", {})
        fator = gramas / 100.0
        for aa, valor in aa_ing.items():
            totais_aa[aa] = totais_aa.get(aa, 0.0) + valor * fator

    return totais_aa


def adaptar_receita(objetivo: str, ingredientes_disponiveis: list) -> dict:
    """
    Adapta a receita base ao objetivo escolhido, priorizando ingredientes
    que o usuário já tem e indicando o que ainda precisa comprar.
    """
    receita_base = RECEITAS_BASE[objetivo].copy()
    ingredientes_base = receita_base["ingredientes"].copy()

    tem = set(ingredientes_disponiveis)
    precisa_base = set(ingredientes_base.keys())

    ja_tem = precisa_base & tem
    precisa_comprar = precisa_base - tem

    # Se o usuário tem ingredientes mas nenhum coincide com a receita,
    # tenta aproveitar o que ele tem substituindo ingredientes similares
    if ingredientes_disponiveis and not ja_tem:
        info_objetivo = OBJETIVOS[objetivo]
        prioritarios = info_objetivo["ingredientes_prioritarios"]

        # Tenta incluir na receita ingredientes que o usuário tem E são relevantes
        substituicoes = {}
        for ing_disponivel in ingredientes_disponiveis:
            if ing_disponivel in INGREDIENTES:
                objetivos_ing = INGREDIENTES[ing_disponivel]["objetivos"]
                if objetivo in objetivos_ing:
                    dose = INGREDIENTES[ing_disponivel]["dose_ref_g"]
                    substituicoes[ing_disponivel] = dose

        if substituicoes:
            # Adiciona ingredientes do usuário à receita
            for ing, dose in substituicoes.items():
                if ing not in ingredientes_base:
                    ingredientes_base[ing] = dose
            ja_tem = set(substituicoes.keys())

    # Calcula o que falta comprar (itens da receita que o usuário não tem)
    falta_comprar = []
    for ing_id in ingredientes_base:
        if ing_id not in tem:
            if ing_id in INGREDIENTES:
                falta_comprar.append({
                    "id": ing_id,
                    "nome": INGREDIENTES[ing_id]["nome"],
                    "emoji": INGREDIENTES[ing_id]["emoji"],
                    "onde_comprar": INGREDIENTES[ing_id]["onde_comprar"],
                    "gramas_na_receita": ingredientes_base[ing_id],
                })

    nutricao = calcular_nutricao_receita(ingredientes_base)
    aminograma = calcular_aminograma_receita(ingredientes_base)

    ingredientes_detalhados = []
    for ing_id, gramas in ingredientes_base.items():
        if ing_id in INGREDIENTES:
            info = INGREDIENTES[ing_id]
            ingredientes_detalhados.append({
                "id": ing_id,
                "nome": info["nome"],
                "emoji": info["emoji"],
                "gramas": gramas,
                "funcao": info["funcao"],
                "usuario_tem": ing_id in tem,
            })

    return {
        "nome": receita_base["nome"],
        "objetivo": objetivo,
        "ingredientes": ingredientes_detalhados,
        "ingredientes_com_gramas": ingredientes_base,
        "preparo": receita_base["preparo"],
        "rendimento_doses": receita_base["rendimento_doses"],
        "armazenamento": receita_base["armazenamento"],
        "nutricao": nutricao,
        "aminograma": aminograma,
        "falta_comprar": falta_comprar,
        "percentual_disponivel": round(len(ja_tem) / len(ingredientes_base) * 100) if ingredientes_base else 0,
    }


def gerar_receita_completa(objetivo: str, ingredientes_usuario: list) -> dict:
    """Ponto de entrada principal: gera receita com base no objetivo e ingredientes."""
    return adaptar_receita(objetivo, ingredientes_usuario)
