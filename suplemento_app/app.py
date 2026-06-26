"""
SuplemEx – Criador de Suplementos Naturais para Academia
=========================================================
Aplicativo para academistas que preferem criar seus próprios suplementos
naturais, sem produtos industrializados.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from banco_ingredientes import INGREDIENTES, OBJETIVOS
from logica_receitas import gerar_receita_completa

# ─── Configuração da página ───────────────────────────────────────────────────

st.set_page_config(
    page_title="SuplemEx – Suplementos Naturais",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Estilos CSS personalizados ───────────────────────────────────────────────

st.markdown("""
<style>
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(135deg, #e74c3c, #f39c12);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        text-align: center;
        color: #7f8c8d;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .card-objetivo {
        border: 2px solid #e0e0e0;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s;
        background: white;
    }
    .card-objetivo:hover { border-color: #e74c3c; }
    .tag-tem { background: #d4edda; color: #155724; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem; }
    .tag-falta { background: #fff3cd; color: #856404; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem; }
    .secao-titulo {
        font-size: 1.4rem;
        font-weight: 700;
        border-left: 4px solid #e74c3c;
        padding-left: 0.8rem;
        margin: 1.5rem 0 0.8rem 0;
    }
    .ingrediente-item {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        margin-bottom: 0.4rem;
        display: flex;
        justify-content: space-between;
    }
    .badge-essencial {
        background: #ffeeba;
        color: #856404;
        padding: 1px 6px;
        border-radius: 8px;
        font-size: 0.7rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ─── Estado da sessão ─────────────────────────────────────────────────────────

def inicializar_estado():
    defaults = {
        "etapa": 1,
        "objetivo": None,
        "modo_ingredientes": None,
        "ingredientes_usuario": [],
        "receita_gerada": None,
    }
    for chave, valor in defaults.items():
        if chave not in st.session_state:
            st.session_state[chave] = valor

inicializar_estado()


# ─── Funções auxiliares de UI ─────────────────────────────────────────────────

def voltar_etapa(etapa: int):
    st.session_state.etapa = etapa


def ir_para_etapa(etapa: int):
    st.session_state.etapa = etapa


def mostrar_barra_progresso():
    etapas = {1: "Objetivo", 2: "Ingredientes", 3: "Receita"}
    total = len(etapas)
    atual = min(st.session_state.etapa, total)
    progresso = atual / total

    cols = st.columns(total)
    for i, (num, nome) in enumerate(etapas.items()):
        with cols[i]:
            if num < atual:
                st.markdown(f"✅ **{nome}**")
            elif num == atual:
                st.markdown(f"🔵 **{nome}**")
            else:
                st.markdown(f"⬜ {nome}")
    st.progress(progresso)
    st.markdown("---")


# ─── ETAPA 1: Tela inicial + seleção de objetivo ─────────────────────────────

def etapa_objetivo():
    st.markdown('<div class="main-title">💪 SuplemEx</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Crie seus próprios suplementos naturais — sem industrializados, '
        'sem mistério, com ciência.</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("### 🎯 Qual é o seu objetivo com o suplemento?")
    st.markdown("Escolha o que mais representa o que você quer alcançar:")

    st.markdown("")

    cols = st.columns(len(OBJETIVOS))
    for i, (obj_id, obj) in enumerate(OBJETIVOS.items()):
        with cols[i]:
            selecionado = st.session_state.objetivo == obj_id
            borda = f"border: 3px solid {obj['cor']};" if selecionado else "border: 2px solid #ddd;"
            bg = f"background: {obj['cor']}10;" if selecionado else "background: white;"

            st.markdown(
                f"""
                <div style="border-radius:12px; padding:1.2rem; text-align:center;
                            {borda} {bg} min-height: 160px;">
                    <div style="font-size:2.5rem">{obj['emoji']}</div>
                    <div style="font-weight:700; font-size:0.95rem; margin: 0.4rem 0">{obj['nome']}</div>
                    <div style="font-size:0.78rem; color:#666">{obj['descricao']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(
                "✓ Selecionar" if selecionado else "Selecionar",
                key=f"btn_{obj_id}",
                use_container_width=True,
                type="primary" if selecionado else "secondary",
            ):
                st.session_state.objetivo = obj_id
                st.rerun()

    st.markdown("")

    if st.session_state.objetivo:
        obj = OBJETIVOS[st.session_state.objetivo]
        st.success(
            f"{obj['emoji']} **{obj['nome']}** selecionado! "
            f"Dica: {obj['dica']}"
        )
        st.markdown("")
        col_btn = st.columns([3, 1, 3])
        with col_btn[1]:
            if st.button("Continuar ➡️", type="primary", use_container_width=True):
                ir_para_etapa(2)
                st.rerun()
    else:
        st.info("👆 Selecione um objetivo acima para continuar.")


# ─── ETAPA 2: Ingredientes disponíveis ───────────────────────────────────────

def etapa_ingredientes():
    obj = OBJETIVOS[st.session_state.objetivo]

    st.markdown(f"### {obj['emoji']} Objetivo: **{obj['nome']}**")
    st.markdown("---")
    st.markdown("### 🧂 Você já tem algum ingrediente em casa?")

    col1, col2 = st.columns(2)
    with col1:
        if st.button(
            "✅ Sim, tenho alguns ingredientes",
            type="primary",
            use_container_width=True,
            help="Você seleciona o que tem e a gente complementa com o que falta",
        ):
            st.session_state.modo_ingredientes = "tem_alguns"
            st.rerun()

    with col2:
        if st.button(
            "🛒 Não, me diga tudo que preciso comprar",
            use_container_width=True,
            help="Geraremos a receita completa com lista de compras",
        ):
            st.session_state.modo_ingredientes = "comprar_tudo"
            st.session_state.ingredientes_usuario = []
            ir_para_etapa(3)
            st.rerun()

    if st.session_state.modo_ingredientes == "tem_alguns":
        st.markdown("")
        st.markdown("#### Marque os ingredientes que você já tem:")

        obj_id = st.session_state.objetivo
        ingredientes_relevantes = [
            (ing_id, info)
            for ing_id, info in INGREDIENTES.items()
            if obj_id in info["objetivos"]
        ]

        outros = [
            (ing_id, info)
            for ing_id, info in INGREDIENTES.items()
            if obj_id not in info["objetivos"]
        ]

        selecionados = list(st.session_state.ingredientes_usuario)

        with st.expander("⭐ Ingredientes Recomendados para o seu Objetivo", expanded=True):
            for ing_id, info in ingredientes_relevantes:
                col_check, col_info = st.columns([0.5, 5])
                with col_check:
                    marcado = st.checkbox(
                        "", value=(ing_id in selecionados), key=f"chk_{ing_id}"
                    )
                with col_info:
                    st.markdown(
                        f"**{info['emoji']} {info['nome']}** "
                        f"<span style='color:#666; font-size:0.85rem'>— {info['funcao']}</span> "
                        f"<span style='color:#aaa; font-size:0.8rem'>({info['onde_comprar']})</span>",
                        unsafe_allow_html=True,
                    )
                if marcado and ing_id not in selecionados:
                    selecionados.append(ing_id)
                elif not marcado and ing_id in selecionados:
                    selecionados.remove(ing_id)

        with st.expander("➕ Outros ingredientes disponíveis"):
            for ing_id, info in outros:
                col_check, col_info = st.columns([0.5, 5])
                with col_check:
                    marcado = st.checkbox(
                        "", value=(ing_id in selecionados), key=f"chk_{ing_id}"
                    )
                with col_info:
                    st.markdown(
                        f"**{info['emoji']} {info['nome']}** "
                        f"<span style='color:#666; font-size:0.85rem'>— {info['funcao']}</span>",
                        unsafe_allow_html=True,
                    )
                if marcado and ing_id not in selecionados:
                    selecionados.append(ing_id)
                elif not marcado and ing_id in selecionados:
                    selecionados.remove(ing_id)

        st.session_state.ingredientes_usuario = selecionados

        if selecionados:
            st.success(f"✅ {len(selecionados)} ingrediente(s) selecionado(s).")

        st.markdown("")
        col_voltar, _, col_avancar = st.columns([1, 2, 1])
        with col_voltar:
            if st.button("⬅️ Voltar", use_container_width=True):
                st.session_state.modo_ingredientes = None
                voltar_etapa(1)
                st.rerun()
        with col_avancar:
            if st.button("Gerar Receita 🧪", type="primary", use_container_width=True):
                ir_para_etapa(3)
                st.rerun()
    else:
        st.markdown("")
        if st.button("⬅️ Voltar para objetivos"):
            voltar_etapa(1)
            st.rerun()


# ─── ETAPA 3: Exibição da receita ────────────────────────────────────────────

def exibir_tabela_nutricional(nutricao: dict):
    st.markdown('<div class="secao-titulo">📊 Tabela Nutricional por Porção</div>', unsafe_allow_html=True)

    peso = nutricao.get("peso_total_g", 0)

    macro_cols = st.columns(4)
    metricas = [
        ("🔥 Calorias", f"{nutricao['kcal']:.0f} kcal", None),
        ("🥩 Proteínas", f"{nutricao['proteinas_g']:.1f} g", None),
        ("🌾 Carboidratos", f"{nutricao['carboidratos_g']:.1f} g", None),
        ("🥑 Gorduras", f"{nutricao['gorduras_g']:.1f} g", None),
    ]
    for col, (label, valor, delta) in zip(macro_cols, metricas):
        with col:
            st.metric(label, valor)

    st.markdown("")

    # Macros em tabela completa
    dados_macro = {
        "Nutriente": [
            "Valor Energético",
            "Proteínas",
            "Carboidratos Totais",
            "  ↳ Fibras Alimentares",
            "Gorduras Totais",
            "  ↳ Gorduras Saturadas",
        ],
        "Por Porção": [
            f"{nutricao['kcal']:.0f} kcal",
            f"{nutricao['proteinas_g']:.1f} g",
            f"{nutricao['carboidratos_g']:.1f} g",
            f"{nutricao['fibras_g']:.1f} g",
            f"{nutricao['gorduras_g']:.1f} g",
            f"{nutricao['gorduras_sat_g']:.1f} g",
        ],
        "%VD*": [
            f"{nutricao['kcal'] / 2000 * 100:.0f}%",
            f"{nutricao['proteinas_g'] / 75 * 100:.0f}%",
            f"{nutricao['carboidratos_g'] / 300 * 100:.0f}%",
            f"{nutricao['fibras_g'] / 25 * 100:.0f}%",
            f"{nutricao['gorduras_g'] / 55 * 100:.0f}%",
            f"{nutricao['gorduras_sat_g'] / 22 * 100:.0f}%",
        ],
    }

    df_macro = pd.DataFrame(dados_macro)
    st.dataframe(df_macro, use_container_width=True, hide_index=True)

    # Micronutrientes
    st.markdown("**Micronutrientes por porção:**")
    dados_micro = {
        "Mineral": ["Sódio", "Potássio", "Cálcio", "Ferro", "Magnésio", "Zinco"],
        "Quantidade": [
            f"{nutricao['sodio_mg']:.0f} mg",
            f"{nutricao['potassio_mg']:.0f} mg",
            f"{nutricao['calcio_mg']:.0f} mg",
            f"{nutricao['ferro_mg']:.1f} mg",
            f"{nutricao['magnesio_mg']:.0f} mg",
            f"{nutricao['zinco_mg']:.1f} mg",
        ],
        "%VD*": [
            f"{nutricao['sodio_mg'] / 2300 * 100:.0f}%",
            f"{nutricao['potassio_mg'] / 4700 * 100:.0f}%",
            f"{nutricao['calcio_mg'] / 1000 * 100:.0f}%",
            f"{nutricao['ferro_mg'] / 14 * 100:.0f}%",
            f"{nutricao['magnesio_mg'] / 420 * 100:.0f}%",
            f"{nutricao['zinco_mg'] / 11 * 100:.0f}%",
        ],
    }
    df_micro = pd.DataFrame(dados_micro)
    st.dataframe(df_micro, use_container_width=True, hide_index=True)

    st.caption(
        f"*VD = Valores Diários com base em dieta de 2.000 kcal. "
        f"Porção: {peso:.0f}g de pó seco (adicionar 250–350ml de líquido). "
        "Valores podem variar conforme marcas e processamento dos ingredientes."
    )


def exibir_aminograma(aminograma: dict, proteinas_total_g: float):
    st.markdown('<div class="secao-titulo">🧬 Aminograma Completo (por porção)</div>', unsafe_allow_html=True)

    st.caption(
        "Aminoácidos marcados com ★ são **essenciais** (o corpo não produz, devem vir da alimentação). "
        "Os BCAAs (Leucina, Isoleucina, Valina) são os mais importantes para construção e recuperação muscular."
    )

    # Separar essenciais e não-essenciais
    essenciais = {aa: v for aa, v in aminograma.items() if aa.endswith("*")}
    nao_essenciais = {aa: v for aa, v in aminograma.items() if not aa.endswith("*")}

    # Renomear para exibição (remover o *)
    def limpar_nome(nome):
        return nome.replace("*", " ★")

    aa_labels = []
    aa_valores = []
    aa_tipos = []

    for aa, v in sorted(essenciais.items(), key=lambda x: -x[1]):
        aa_labels.append(limpar_nome(aa))
        aa_valores.append(round(v, 2))
        aa_tipos.append("Essencial ★")

    for aa, v in sorted(nao_essenciais.items(), key=lambda x: -x[1]):
        aa_labels.append(limpar_nome(aa))
        aa_valores.append(round(v, 2))
        aa_tipos.append("Não Essencial")

    df_aa = pd.DataFrame({
        "Aminoácido": aa_labels,
        "Quantidade (g)": aa_valores,
        "Tipo": aa_tipos,
    })

    fig = px.bar(
        df_aa,
        x="Quantidade (g)",
        y="Aminoácido",
        color="Tipo",
        orientation="h",
        color_discrete_map={"Essencial ★": "#e74c3c", "Não Essencial": "#3498db"},
        text="Quantidade (g)",
        height=520,
        title=f"Perfil de Aminoácidos — {proteinas_total_g:.1f}g de proteína total",
    )

    fig.update_traces(texttemplate="%{text:.2f}g", textposition="outside")
    fig.update_layout(
        yaxis=dict(categoryorder="total ascending"),
        legend_title="Tipo de Aminoácido",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=12),
        margin=dict(l=10, r=60, t=50, b=20),
    )
    fig.update_xaxes(showgrid=True, gridcolor="#f0f0f0")
    fig.update_yaxes(showgrid=False)

    st.plotly_chart(fig, use_container_width=True)

    # Tabela detalhada em expander
    with st.expander("📋 Ver tabela detalhada de aminoácidos"):
        df_exib = df_aa.copy()
        df_exib["Quantidade (g)"] = df_exib["Quantidade (g)"].apply(lambda x: f"{x:.3f} g")
        st.dataframe(df_exib, use_container_width=True, hide_index=True)


def etapa_receita():
    objetivo_id = st.session_state.objetivo
    ingredientes_usuario = st.session_state.ingredientes_usuario
    obj = OBJETIVOS[objetivo_id]

    # Gera a receita (com cache no session_state para não reprocessar)
    if st.session_state.receita_gerada is None or st.session_state.get("_ultima_geracao") != (objetivo_id, tuple(sorted(ingredientes_usuario))):
        with st.spinner("🧪 Formulando sua receita personalizada..."):
            receita = gerar_receita_completa(objetivo_id, ingredientes_usuario)
            st.session_state.receita_gerada = receita
            st.session_state["_ultima_geracao"] = (objetivo_id, tuple(sorted(ingredientes_usuario)))
    else:
        receita = st.session_state.receita_gerada

    # ── Cabeçalho ──────────────────────────────────────────────────────────
    st.markdown(f"## {obj['emoji']} {receita['nome']}")

    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        peso = receita["nutricao"]["peso_total_g"]
        st.metric("⚖️ Porção (pó seco)", f"{peso:.0f} g")
    with col_info2:
        st.metric("🔥 Calorias / Dose", f"{receita['nutricao']['kcal']:.0f} kcal")
    with col_info3:
        st.metric("🥩 Proteína / Dose", f"{receita['nutricao']['proteinas_g']:.1f} g")

    st.success(f"💡 **Quando usar:** {obj['dica']}")

    st.markdown("---")

    # ── Ingredientes ───────────────────────────────────────────────────────
    st.markdown('<div class="secao-titulo">🧂 Ingredientes da Receita</div>', unsafe_allow_html=True)

    col_ing, col_lista_compras = st.columns([3, 2])

    with col_ing:
        st.markdown("**Ingredientes e quantidades (por porção):**")
        for item in receita["ingredientes"]:
            status_tag = (
                '<span class="tag-tem">✅ Você tem</span>'
                if item["usuario_tem"]
                else '<span class="tag-falta">🛒 Comprar</span>'
            ) if ingredientes_usuario else ""

            st.markdown(
                f"""
                <div style="background:#f8f9fa; border-radius:8px; padding:0.6rem 1rem;
                            margin-bottom:0.4rem; display:flex; justify-content:space-between;
                            align-items:center;">
                    <div>
                        <span style="font-size:1.2rem">{item['emoji']}</span>
                        <strong> {item['nome']}</strong>
                        <br><span style="font-size:0.8rem; color:#666; margin-left:1.8rem">
                        {item['funcao']}</span>
                    </div>
                    <div style="text-align:right; white-space:nowrap; padding-left:1rem;">
                        <strong>{item['gramas']}g</strong><br>
                        {status_tag}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col_lista_compras:
        if receita["falta_comprar"]:
            st.markdown("**🛒 Lista de Compras:**")

            # Agrupar por onde comprar
            por_local = {}
            for item in receita["falta_comprar"]:
                local = item["onde_comprar"]
                por_local.setdefault(local, []).append(item)

            for local, itens in por_local.items():
                st.markdown(f"*📍 {local}:*")
                for item in itens:
                    st.markdown(f"  - {item['emoji']} **{item['nome']}** ({item['gramas_na_receita']}g/dose)")
        else:
            if ingredientes_usuario:
                st.success("🎉 Você já tem todos os ingredientes necessários!")
            else:
                st.info("📋 Todos os ingredientes listados à esquerda.")

    st.markdown("---")

    # ── Modo de Preparo ────────────────────────────────────────────────────
    st.markdown('<div class="secao-titulo">👨‍🍳 Modo de Preparo</div>', unsafe_allow_html=True)

    for i, passo in enumerate(receita["preparo"], 1):
        st.markdown(
            f"""
            <div style="display:flex; gap:1rem; margin-bottom:0.6rem; align-items:flex-start;">
                <div style="background:#e74c3c; color:white; border-radius:50%; width:28px; height:28px;
                            display:flex; align-items:center; justify-content:center; flex-shrink:0;
                            font-weight:700; font-size:0.85rem;">{i}</div>
                <div style="padding-top:3px">{passo}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <div style="background:#e8f4f8; border-radius:8px; padding:0.8rem 1rem; margin-top:0.8rem;">
            📦 <strong>Armazenamento:</strong> {receita['armazenamento']}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # ── Tabela Nutricional ─────────────────────────────────────────────────
    exibir_tabela_nutricional(receita["nutricao"])

    st.markdown("---")

    # ── Aminograma ────────────────────────────────────────────────────────
    exibir_aminograma(receita["aminograma"], receita["nutricao"]["proteinas_g"])

    st.markdown("---")

    # ── Aviso e rodapé ────────────────────────────────────────────────────
    st.warning(
        "⚠️ **Aviso Importante:** Este aplicativo tem finalidade educacional e informativa. "
        "As receitas apresentadas são sugestões baseadas em ingredientes naturais. "
        "Consulte sempre um nutricionista ou médico antes de iniciar qualquer protocolo de suplementação, "
        "especialmente se você possui condições de saúde ou faz uso de medicamentos."
    )

    st.markdown("---")
    col_nova, col_mod = st.columns(2)
    with col_nova:
        if st.button("🔄 Criar nova receita", use_container_width=True, type="primary"):
            st.session_state.etapa = 1
            st.session_state.objetivo = None
            st.session_state.modo_ingredientes = None
            st.session_state.ingredientes_usuario = []
            st.session_state.receita_gerada = None
            st.rerun()
    with col_mod:
        if st.button("✏️ Mudar ingredientes", use_container_width=True):
            st.session_state.etapa = 2
            st.session_state.receita_gerada = None
            st.rerun()


# ─── Roteador principal ───────────────────────────────────────────────────────

def main():
    mostrar_barra_progresso()

    etapa = st.session_state.etapa

    if etapa == 1:
        etapa_objetivo()
    elif etapa == 2:
        etapa_ingredientes()
    elif etapa == 3:
        etapa_receita()


if __name__ == "__main__":
    main()
