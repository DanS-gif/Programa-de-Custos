"""
Sistema Inteligente para Cálculo e Orçamento de Obras
======================================================
MVP desenvolvido com Streamlit, Pandas e Matplotlib.

Autor: Engenheiro de Software Sênior
Versão: 1.0.0
"""

import io
import textwrap
from typing import Optional

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Configuração global da página
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="ObraCalc – Orçamento Inteligente",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Constantes e índices técnicos de referência (por m²)
# ---------------------------------------------------------------------------

INDICES_TECNICOS: dict[str, float] = {
    "Mão de Obra (h)": 6.0,
    "Cimento (kg)": 12.0,
    "Areia (m³)": 0.04,
    "Brita (m³)": 0.03,
    "Blocos/Tijolos (un)": 18.0,
    "Ferro/Aço (kg)": 4.5,
    "Impermeabilizante (L)": 0.5,
    "Revestimento/Azulejo (m²)": 1.05,
    "Tinta (L)": 0.35,
    "Elétrica (pt)": 0.8,
    "Hidráulica (pt)": 0.5,
    "Esquadrias (un)": 0.15,
}

COLUNAS_OBRIGATORIAS: list[str] = [
    "Material / Serviço",
    "Unidade",
    "Custo Unitário (R$)",
    "Perfil",
]

PERFIS: list[str] = ["Econômico", "Intermediário", "Premium"]

CORES_PERFIS: dict[str, str] = {
    "Econômico": "#4CAF50",
    "Intermediário": "#2196F3",
    "Premium": "#FF9800",
}

SUGESTOES_MATERIAIS: dict[str, dict] = {
    "Econômico": {
        "icone": "💚",
        "titulo": "Perfil Econômico",
        "itens": [
            "Bloco cerâmico 9x19x19 cm — excelente isolamento térmico/acústico.",
            "Cimento CP II-Z — versátil e amplamente disponível no mercado.",
            "Areia média lavada de rio — melhor trabalhabilidade na argamassa.",
            "Tinta PVA acrílica — custo-benefício para áreas internas secas.",
            "Tubulações PVC rígido — durabilidade e fácil instalação.",
        ],
    },
    "Intermediário": {
        "icone": "💙",
        "titulo": "Perfil Intermediário",
        "itens": [
            "Bloco de concreto estrutural — maior resistência e precisão dimensional.",
            "Cimento CP V-ARI — alta resistência inicial, acelera o cronograma.",
            "Argamassa industrializada — controle de qualidade superior ao traço manual.",
            "Tinta acrílica semibrilho — lavável e indicada para áreas úmidas.",
            "Cerâmica retificada — acabamento mais refinado com rejuntes finos.",
        ],
    },
    "Premium": {
        "icone": "🧡",
        "titulo": "Perfil Premium",
        "itens": [
            "Steel frame ou alvenaria estrutural de concreto — máxima durabilidade.",
            "Cimento branco CP IV — ideal para rejuntes e acabamentos nobres.",
            "Porcelanato polido ou técnico — alta resistência e estética superior.",
            "Tinta texturizada acrílica — proteção extra e efeito decorativo.",
            "Automação elétrica e hidráulica — conforto e eficiência energética.",
        ],
    },
}

# ---------------------------------------------------------------------------
# CSS personalizado — tema blueprint técnico
# ---------------------------------------------------------------------------

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Exo+2:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Exo 2', sans-serif;
}

.stApp {
    background: #0a0e1a;
    color: #c8d8e8;
}

/* Header principal */
.main-header {
    background: linear-gradient(135deg, #0d1b2a 0%, #1a2744 50%, #0d1b2a 100%);
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 28px 36px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.main-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 39px,
        rgba(30, 90, 160, 0.08) 39px,
        rgba(30, 90, 160, 0.08) 40px
    ),
    repeating-linear-gradient(
        90deg,
        transparent,
        transparent 39px,
        rgba(30, 90, 160, 0.08) 39px,
        rgba(30, 90, 160, 0.08) 40px
    );
}
.main-header h1 {
    font-family: 'Share Tech Mono', monospace;
    font-size: 2.2rem;
    color: #5ba3d9;
    letter-spacing: 2px;
    margin: 0;
    position: relative;
    text-shadow: 0 0 20px rgba(91, 163, 217, 0.4);
}
.main-header p {
    color: #7a9ab5;
    margin: 6px 0 0 0;
    font-size: 0.95rem;
    letter-spacing: 0.5px;
    position: relative;
}

/* Cards de métricas customizados */
.metric-card {
    background: linear-gradient(145deg, #0f1e30, #162540);
    border: 1px solid #1e4060;
    border-left: 4px solid #5ba3d9;
    border-radius: 10px;
    padding: 20px 24px;
    margin: 8px 0;
}
.metric-card .label {
    font-size: 0.78rem;
    color: #6a8fa8;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-family: 'Share Tech Mono', monospace;
}
.metric-card .value {
    font-size: 2.1rem;
    font-weight: 700;
    color: #5ba3d9;
    font-family: 'Share Tech Mono', monospace;
    line-height: 1.2;
}
.metric-card .delta {
    font-size: 0.82rem;
    color: #4caf7d;
    margin-top: 4px;
}

/* Cards de sugestões */
.suggestion-card {
    background: #0f1e30;
    border: 1px solid #1e3a5f;
    border-radius: 10px;
    padding: 20px;
    margin: 10px 0;
    height: 100%;
}
.suggestion-card h4 {
    color: #5ba3d9;
    margin: 0 0 12px 0;
    font-size: 1.0rem;
    font-family: 'Share Tech Mono', monospace;
}
.suggestion-card ul {
    padding-left: 16px;
    margin: 0;
}
.suggestion-card ul li {
    color: #a8c4d8;
    font-size: 0.88rem;
    margin-bottom: 7px;
    line-height: 1.5;
}

/* Abas */
.stTabs [data-baseweb="tab-list"] {
    background: #0d1b2a;
    border-bottom: 2px solid #1e3a5f;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #6a8fa8;
    border: 1px solid transparent;
    border-radius: 8px 8px 0 0;
    padding: 10px 22px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.9rem;
    letter-spacing: 0.5px;
}
.stTabs [aria-selected="true"] {
    background: #162540 !important;
    color: #5ba3d9 !important;
    border-color: #1e4060 !important;
    border-bottom-color: #162540 !important;
}

/* Inputs */
.stNumberInput input, .stTextInput input {
    background: #0f1e30 !important;
    border: 1px solid #1e4060 !important;
    color: #c8d8e8 !important;
    border-radius: 6px !important;
    font-family: 'Exo 2', sans-serif !important;
}
.stSlider [data-baseweb="slider"] {
    margin-top: 8px;
}

/* Botões */
.stDownloadButton button, .stButton button {
    background: linear-gradient(135deg, #1a3a5c, #1e4a7a) !important;
    color: #5ba3d9 !important;
    border: 1px solid #2a5a8c !important;
    border-radius: 8px !important;
    font-family: 'Share Tech Mono', monospace !important;
    letter-spacing: 0.5px !important;
    transition: all 0.2s ease !important;
}
.stDownloadButton button:hover, .stButton button:hover {
    background: linear-gradient(135deg, #1e4a7a, #2460a0) !important;
    border-color: #5ba3d9 !important;
    box-shadow: 0 0 12px rgba(91, 163, 217, 0.3) !important;
}

/* Alertas */
.stAlert {
    border-radius: 8px !important;
    border-left: 4px solid !important;
}

/* Divisor */
hr {
    border-color: #1e3a5f !important;
    margin: 28px 0 !important;
}

/* Data editor */
.stDataFrame {
    border: 1px solid #1e4060 !important;
    border-radius: 8px !important;
    overflow: hidden !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0a0e1a; }
::-webkit-scrollbar-thumb { background: #1e4060; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #2a5a8c; }
</style>
"""


# ---------------------------------------------------------------------------
# Funções utilitárias
# ---------------------------------------------------------------------------


def gerar_tabela_padrao() -> pd.DataFrame:
    """
    Gera o DataFrame padrão com os materiais e serviços de referência,
    contendo três perfis de custo (Econômico, Intermediário, Premium).

    Retorna
    -------
    pd.DataFrame
        Tabela com colunas: Material / Serviço, Unidade, Custo Unitário (R$), Perfil.
    """
    registros = [
        # ---- Mão de Obra ----
        ("Mão de Obra (h)", "hora", 40.00, "Econômico"),
        ("Mão de Obra (h)", "hora", 65.00, "Intermediário"),
        ("Mão de Obra (h)", "hora", 95.00, "Premium"),
        # ---- Cimento ----
        ("Cimento (kg)", "kg", 0.72, "Econômico"),
        ("Cimento (kg)", "kg", 0.85, "Intermediário"),
        ("Cimento (kg)", "kg", 1.10, "Premium"),
        # ---- Areia ----
        ("Areia (m³)", "m³", 90.00, "Econômico"),
        ("Areia (m³)", "m³", 110.00, "Intermediário"),
        ("Areia (m³)", "m³", 130.00, "Premium"),
        # ---- Brita ----
        ("Brita (m³)", "m³", 110.00, "Econômico"),
        ("Brita (m³)", "m³", 130.00, "Intermediário"),
        ("Brita (m³)", "m³", 155.00, "Premium"),
        # ---- Blocos/Tijolos ----
        ("Blocos/Tijolos (un)", "unidade", 0.85, "Econômico"),
        ("Blocos/Tijolos (un)", "unidade", 1.40, "Intermediário"),
        ("Blocos/Tijolos (un)", "unidade", 2.20, "Premium"),
        # ---- Ferro/Aço ----
        ("Ferro/Aço (kg)", "kg", 7.50, "Econômico"),
        ("Ferro/Aço (kg)", "kg", 8.80, "Intermediário"),
        ("Ferro/Aço (kg)", "kg", 10.50, "Premium"),
        # ---- Impermeabilizante ----
        ("Impermeabilizante (L)", "litro", 18.00, "Econômico"),
        ("Impermeabilizante (L)", "litro", 28.00, "Intermediário"),
        ("Impermeabilizante (L)", "litro", 45.00, "Premium"),
        # ---- Revestimento ----
        ("Revestimento/Azulejo (m²)", "m²", 35.00, "Econômico"),
        ("Revestimento/Azulejo (m²)", "m²", 75.00, "Intermediário"),
        ("Revestimento/Azulejo (m²)", "m²", 180.00, "Premium"),
        # ---- Tinta ----
        ("Tinta (L)", "litro", 22.00, "Econômico"),
        ("Tinta (L)", "litro", 40.00, "Intermediário"),
        ("Tinta (L)", "litro", 75.00, "Premium"),
        # ---- Elétrica ----
        ("Elétrica (pt)", "ponto", 120.00, "Econômico"),
        ("Elétrica (pt)", "ponto", 200.00, "Intermediário"),
        ("Elétrica (pt)", "ponto", 350.00, "Premium"),
        # ---- Hidráulica ----
        ("Hidráulica (pt)", "ponto", 150.00, "Econômico"),
        ("Hidráulica (pt)", "ponto", 250.00, "Intermediário"),
        ("Hidráulica (pt)", "ponto", 420.00, "Premium"),
        # ---- Esquadrias ----
        ("Esquadrias (un)", "unidade", 350.00, "Econômico"),
        ("Esquadrias (un)", "unidade", 700.00, "Intermediário"),
        ("Esquadrias (un)", "unidade", 1500.00, "Premium"),
    ]
    df = pd.DataFrame(registros, columns=COLUNAS_OBRIGATORIAS)
    return df


def carregar_csv(arquivo_enviado) -> tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Carrega e valida um arquivo CSV enviado pelo usuário.

    Realiza tratamento robusto de codificação (UTF-8 / latin1) e
    conversão de separadores decimais (vírgula → ponto).

    Parâmetros
    ----------
    arquivo_enviado : UploadedFile
        Arquivo CSV proveniente do st.file_uploader.

    Retorna
    -------
    tuple[Optional[pd.DataFrame], Optional[str]]
        (DataFrame carregado, mensagem de erro) — um dos dois será None.
    """
    conteudo = arquivo_enviado.read()

    # Tentativa de leitura com UTF-8, fallback para latin1
    for codificacao in ("utf-8", "latin1", "utf-8-sig"):
        try:
            df = pd.read_csv(
                io.BytesIO(conteudo),
                encoding=codificacao,
                sep=None,          # detecção automática de separador
                engine="python",
            )
            break
        except (UnicodeDecodeError, pd.errors.ParserError):
            continue
    else:
        return None, "❌ Não foi possível decodificar o arquivo. Use UTF-8 ou latin1."

    # Verificação das colunas obrigatórias
    colunas_faltantes = set(COLUNAS_OBRIGATORIAS) - set(df.columns)
    if colunas_faltantes:
        return None, (
            f"❌ Colunas ausentes no CSV: {', '.join(colunas_faltantes)}. "
            "Baixe o template correto e preencha os dados."
        )

    # Normalização da coluna de preços (vírgula → ponto)
    col_preco = "Custo Unitário (R$)"
    if df[col_preco].dtype == object:
        df[col_preco] = (
            df[col_preco]
            .astype(str)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
        )
    df[col_preco] = pd.to_numeric(df[col_preco], errors="coerce").fillna(0.0)

    # Validação de perfis
    perfis_invalidos = set(df["Perfil"].unique()) - set(PERFIS)
    if perfis_invalidos:
        return None, (
            f"❌ Perfis inválidos encontrados: {perfis_invalidos}. "
            f"Use apenas: {PERFIS}."
        )

    return df, None


def calcular_orcamento(
    df_precos: pd.DataFrame,
    area: float,
    desperdicio_pct: float,
    perfil: str,
) -> pd.DataFrame:
    """
    Cruza os índices técnicos com a tabela de preços para gerar o orçamento.

    Parâmetros
    ----------
    df_precos : pd.DataFrame
        Tabela de preços filtrada por perfil.
    area : float
        Área da obra em m².
    desperdicio_pct : float
        Percentual de desperdício (ex: 0.10 para 10%).
    perfil : str
        Perfil de custo selecionado.

    Retorna
    -------
    pd.DataFrame
        Tabela de orçamento consolidado com quantidades e custos.
    """
    fator = 1.0 + desperdicio_pct
    df_filtrado = df_precos[df_precos["Perfil"] == perfil].copy()

    linhas = []
    for material, indice in INDICES_TECNICOS.items():
        row = df_filtrado[df_filtrado["Material / Serviço"] == material]
        if row.empty:
            continue
        custo_unit = float(row["Custo Unitário (R$)"].iloc[0])
        unidade = str(row["Unidade"].iloc[0])
        qtd_teorica = area * indice
        qtd_com_desperdicio = qtd_teorica * fator
        custo_total = qtd_com_desperdicio * custo_unit
        linhas.append(
            {
                "Material / Serviço": material,
                "Unidade": unidade,
                "Índice Técnico/m²": indice,
                "Qtd. Teórica": round(qtd_teorica, 3),
                "Qtd. c/ Desperdício": round(qtd_com_desperdicio, 3),
                "Custo Unit. (R$)": round(custo_unit, 2),
                "Custo Total (R$)": round(custo_total, 2),
            }
        )

    return pd.DataFrame(linhas)


def calcular_custo_total_por_perfil(
    df_precos: pd.DataFrame,
    area: float,
    desperdicio_pct: float,
) -> dict[str, float]:
    """
    Calcula o custo total de obra para cada perfil de acabamento.

    Parâmetros
    ----------
    df_precos : pd.DataFrame
        Tabela de preços completa.
    area : float
        Área da obra em m².
    desperdicio_pct : float
        Percentual de desperdício.

    Retorna
    -------
    dict[str, float]
        Dicionário {perfil: custo_total}.
    """
    return {
        perfil: calcular_orcamento(df_precos, area, desperdicio_pct, perfil)[
            "Custo Total (R$)"
        ].sum()
        for perfil in PERFIS
    }


# ---------------------------------------------------------------------------
# Funções de visualização
# ---------------------------------------------------------------------------


def plotar_planta_baixa(largura: float, comprimento: float) -> plt.Figure:
    """
    Gera a planta baixa técnica no estilo blueprint ABNT.

    Aplica cotagem nas quatro arestas com linhas auxiliares,
    setas técnicas e valores dimensionais anotados.

    Parâmetros
    ----------
    largura : float
        Largura da planta em metros.
    comprimento : float
        Comprimento da planta em metros.

    Retorna
    -------
    plt.Figure
        Figura Matplotlib pronta para exibição.
    """
    fig, ax = plt.subplots(figsize=(9, 7))
    fig.patch.set_facecolor("#040d1a")
    ax.set_facecolor("#04111f")

    # Grade sutil estilo papel milimetrado
    ax.set_xlim(-2.5, largura + 2.5)
    ax.set_ylim(-2.5, comprimento + 2.5)
    ax.set_aspect("equal")

    grade_maior = max(largura, comprimento) / 10
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(grade_maior / 5))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(grade_maior / 5))
    ax.xaxis.set_major_locator(ticker.MultipleLocator(grade_maior))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(grade_maior))
    ax.grid(which="major", color="#0d2a45", linewidth=0.6, linestyle="-")
    ax.grid(which="minor", color="#071a2e", linewidth=0.3, linestyle="-")
    ax.set_axisbelow(True)

    # Planta principal — polígono da edificação
    planta = plt.Polygon(
        [(0, 0), (largura, 0), (largura, comprimento), (0, comprimento)],
        closed=True,
        facecolor="#071e35",
        edgecolor="#3d8bc4",
        linewidth=2.5,
        zorder=3,
    )
    ax.add_patch(planta)

    # Hachura interna leve
    hachura = plt.Polygon(
        [(0, 0), (largura, 0), (largura, comprimento), (0, comprimento)],
        closed=True,
        fill=False,
        hatch="////",
        edgecolor="#0d2a45",
        linewidth=0,
        zorder=2,
    )
    ax.add_patch(hachura)

    # ---------- COTAGEM ABNT ----------
    offset_cota = 1.0    # distância da cota à aresta da planta
    tick_tam = 0.25      # comprimento do traço de limite de cota
    cor_cota = "#5ba3d9"
    cor_texto = "#7fc4e8"
    estilo_seta = dict(
        arrowstyle="<->",
        color=cor_cota,
        lw=1.0,
    )

    # --- Cota inferior (largura) ---
    y_cota_inf = -offset_cota
    ax.annotate(
        "",
        xy=(largura, y_cota_inf),
        xytext=(0, y_cota_inf),
        arrowprops=estilo_seta,
        zorder=5,
    )
    # Linhas auxiliares
    for x_pos in (0, largura):
        ax.plot(
            [x_pos, x_pos],
            [0, y_cota_inf - 0.1],
            color=cor_cota,
            lw=0.8,
            linestyle="--",
            zorder=4,
        )
    # Traços de limite (ABNT — traço oblíquo a 45°)
    for x_pos in (0, largura):
        ax.plot(
            [x_pos - tick_tam / 2, x_pos + tick_tam / 2],
            [y_cota_inf - tick_tam / 2, y_cota_inf + tick_tam / 2],
            color=cor_cota,
            lw=1.2,
            zorder=5,
        )
    ax.text(
        largura / 2,
        y_cota_inf - 0.45,
        f"{largura:.2f} m",
        ha="center",
        va="top",
        fontsize=10,
        color=cor_texto,
        fontfamily="monospace",
        fontweight="bold",
        zorder=5,
    )

    # --- Cota superior (largura) ---
    y_cota_sup = comprimento + offset_cota
    ax.annotate(
        "",
        xy=(largura, y_cota_sup),
        xytext=(0, y_cota_sup),
        arrowprops=estilo_seta,
        zorder=5,
    )
    for x_pos in (0, largura):
        ax.plot(
            [x_pos, x_pos],
            [comprimento, y_cota_sup + 0.1],
            color=cor_cota,
            lw=0.8,
            linestyle="--",
            zorder=4,
        )
        ax.plot(
            [x_pos - tick_tam / 2, x_pos + tick_tam / 2],
            [y_cota_sup - tick_tam / 2, y_cota_sup + tick_tam / 2],
            color=cor_cota,
            lw=1.2,
            zorder=5,
        )
    ax.text(
        largura / 2,
        y_cota_sup + 0.45,
        f"{largura:.2f} m",
        ha="center",
        va="bottom",
        fontsize=10,
        color=cor_texto,
        fontfamily="monospace",
        fontweight="bold",
        zorder=5,
    )

    # --- Cota lateral esquerda (comprimento) ---
    x_cota_esq = -offset_cota
    ax.annotate(
        "",
        xy=(x_cota_esq, comprimento),
        xytext=(x_cota_esq, 0),
        arrowprops=estilo_seta,
        zorder=5,
    )
    for y_pos in (0, comprimento):
        ax.plot(
            [0, x_cota_esq - 0.1],
            [y_pos, y_pos],
            color=cor_cota,
            lw=0.8,
            linestyle="--",
            zorder=4,
        )
        ax.plot(
            [x_cota_esq - tick_tam / 2, x_cota_esq + tick_tam / 2],
            [y_pos - tick_tam / 2, y_pos + tick_tam / 2],
            color=cor_cota,
            lw=1.2,
            zorder=5,
        )
    ax.text(
        x_cota_esq - 0.5,
        comprimento / 2,
        f"{comprimento:.2f} m",
        ha="right",
        va="center",
        fontsize=10,
        color=cor_texto,
        fontfamily="monospace",
        fontweight="bold",
        rotation=90,
        zorder=5,
    )

    # --- Cota lateral direita (comprimento) ---
    x_cota_dir = largura + offset_cota
    ax.annotate(
        "",
        xy=(x_cota_dir, comprimento),
        xytext=(x_cota_dir, 0),
        arrowprops=estilo_seta,
        zorder=5,
    )
    for y_pos in (0, comprimento):
        ax.plot(
            [largura, x_cota_dir + 0.1],
            [y_pos, y_pos],
            color=cor_cota,
            lw=0.8,
            linestyle="--",
            zorder=4,
        )
        ax.plot(
            [x_cota_dir - tick_tam / 2, x_cota_dir + tick_tam / 2],
            [y_pos - tick_tam / 2, y_pos + tick_tam / 2],
            color=cor_cota,
            lw=1.2,
            zorder=5,
        )
    ax.text(
        x_cota_dir + 0.5,
        comprimento / 2,
        f"{comprimento:.2f} m",
        ha="left",
        va="center",
        fontsize=10,
        color=cor_texto,
        fontfamily="monospace",
        fontweight="bold",
        rotation=90,
        zorder=5,
    )

    # Ponto central e área
    cx, cy = largura / 2, comprimento / 2
    ax.plot(cx, cy, "+", color="#5ba3d9", markersize=14, lw=1.5, zorder=6)
    area = largura * comprimento
    ax.text(
        cx,
        cy + 0.6,
        f"A = {area:.2f} m²",
        ha="center",
        va="center",
        fontsize=11,
        color="#7fc4e8",
        fontfamily="monospace",
        fontweight="bold",
        zorder=6,
    )

    # Título e rodapé técnico
    ax.set_title(
        "PLANTA BAIXA  –  LAYOUT ESQUEMÁTICO",
        color="#5ba3d9",
        fontfamily="monospace",
        fontsize=12,
        fontweight="bold",
        pad=14,
    )
    fig.text(
        0.5,
        0.01,
        "ObraCalc MVP  |  Escala: sem escala  |  ABNT NBR 6492",
        ha="center",
        fontsize=7.5,
        color="#2a5a8c",
        fontfamily="monospace",
    )

    # Remove eixos visíveis
    ax.tick_params(colors="#1e4060", labelsize=7)
    for spine in ax.spines.values():
        spine.set_edgecolor("#0d2a45")

    plt.tight_layout(pad=1.2)
    return fig


def plotar_comparativo_perfis(custos: dict[str, float]) -> plt.Figure:
    """
    Gera gráfico de barras comparando os custos totais por perfil.

    Parâmetros
    ----------
    custos : dict[str, float]
        Dicionário {perfil: custo_total_R$}.

    Retorna
    -------
    plt.Figure
        Figura Matplotlib com o gráfico comparativo.
    """
    fig, ax = plt.subplots(figsize=(8, 4.5))
    fig.patch.set_facecolor("#04111f")
    ax.set_facecolor("#04111f")

    perfis = list(custos.keys())
    valores = list(custos.values())
    cores = [CORES_PERFIS[p] for p in perfis]

    x = np.arange(len(perfis))
    barras = ax.bar(x, valores, color=cores, width=0.55, zorder=3, edgecolor="#0a0e1a", linewidth=1.5)

    # Gradiente nas barras com alpha overlay
    for barra, cor in zip(barras, cores):
        barra.set_alpha(0.85)

    # Rótulos de valor no topo de cada barra
    for barra, valor in zip(barras, valores):
        ax.text(
            barra.get_x() + barra.get_width() / 2,
            barra.get_height() + max(valores) * 0.015,
            f"R$ {valor:,.0f}".replace(",", "."),
            ha="center",
            va="bottom",
            fontsize=10,
            color="#c8d8e8",
            fontfamily="monospace",
            fontweight="bold",
        )

    ax.set_xticks(x)
    ax.set_xticklabels(perfis, fontsize=11, color="#7fc4e8", fontfamily="monospace")
    ax.yaxis.set_major_formatter(
        ticker.FuncFormatter(lambda v, _: f"R$ {v:,.0f}".replace(",", "."))
    )
    ax.tick_params(axis="y", colors="#2a5a8c", labelsize=8)
    ax.set_ylabel("Custo Total Estimado", color="#2a5a8c", fontsize=9, fontfamily="monospace")
    ax.set_title(
        "COMPARATIVO DE CUSTO POR PERFIL DE ACABAMENTO",
        color="#5ba3d9",
        fontsize=11,
        fontfamily="monospace",
        fontweight="bold",
        pad=12,
    )
    ax.grid(axis="y", color="#0d2a45", linewidth=0.8, linestyle="--", zorder=0)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_edgecolor("#0d2a45")

    plt.tight_layout(pad=1.0)
    return fig


# ---------------------------------------------------------------------------
# Inicialização do estado da sessão
# ---------------------------------------------------------------------------


def inicializar_estado() -> None:
    """Inicializa as variáveis do session_state do Streamlit."""
    if "df_precos" not in st.session_state:
        st.session_state["df_precos"] = gerar_tabela_padrao()
    if "largura" not in st.session_state:
        st.session_state["largura"] = 10.0
    if "comprimento" not in st.session_state:
        st.session_state["comprimento"] = 12.0
    if "desperdicio" not in st.session_state:
        st.session_state["desperdicio"] = 10
    if "perfil_selecionado" not in st.session_state:
        st.session_state["perfil_selecionado"] = "Intermediário"


# ---------------------------------------------------------------------------
# Componentes de UI
# ---------------------------------------------------------------------------


def renderizar_header() -> None:
    """Renderiza o cabeçalho principal da aplicação."""
    st.markdown(
        """
        <div class="main-header">
            <h1>🏗️ ObraCalc</h1>
            <p>Sistema Inteligente para Cálculo e Orçamento de Obras · MVP v1.0</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def renderizar_metricas(area: float, custo_total: float, perfil: str) -> None:
    """
    Exibe os cards de métricas destacadas (área e custo estimado).

    Parâmetros
    ----------
    area : float
        Área calculada em m².
    custo_total : float
        Custo total estimado em R$.
    perfil : str
        Perfil de acabamento selecionado.
    """
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f"""<div class="metric-card">
                <div class="label">📐 Área Total</div>
                <div class="value">{area:.2f} m²</div>
                <div class="delta">Área útil calculada</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col2:
        custo_m2 = custo_total / area if area > 0 else 0
        st.markdown(
            f"""<div class="metric-card">
                <div class="label">💰 Custo Estimado</div>
                <div class="value">R$ {custo_total:,.0f}</div>
                <div class="delta">Perfil {perfil}</div>
            </div>""".replace(",", "."),
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""<div class="metric-card">
                <div class="label">📊 Custo por m²</div>
                <div class="value">R$ {custo_m2:,.0f}</div>
                <div class="delta">Referência SINAPI/PINI</div>
            </div>""".replace(",", "."),
            unsafe_allow_html=True,
        )
    with col4:
        largura = st.session_state["largura"]
        comprimento = st.session_state["comprimento"]
        perim = 2 * (largura + comprimento)
        st.markdown(
            f"""<div class="metric-card">
                <div class="label">📏 Perímetro</div>
                <div class="value">{perim:.2f} m</div>
                <div class="delta">L={largura}m · C={comprimento}m</div>
            </div>""",
            unsafe_allow_html=True,
        )


def renderizar_sugestoes() -> None:
    """Renderiza os cards de sugestões técnicas de materiais por perfil."""
    st.markdown("#### 💡 Sugestões Técnicas por Perfil de Acabamento")
    cols = st.columns(3)
    for col, perfil in zip(cols, PERFIS):
        dados = SUGESTOES_MATERIAIS[perfil]
        itens_html = "".join(f"<li>{item}</li>" for item in dados["itens"])
        with col:
            st.markdown(
                f"""<div class="suggestion-card">
                    <h4>{dados['icone']} {dados['titulo']}</h4>
                    <ul>{itens_html}</ul>
                </div>""",
                unsafe_allow_html=True,
            )


# ---------------------------------------------------------------------------
# Abas principais
# ---------------------------------------------------------------------------


def aba_parametros() -> None:
    """Renderiza a aba de parâmetros geométricos da obra."""
    st.markdown("### 📐 Parâmetros Geométricos da Obra")
    st.caption("Informe as dimensões da planta baixa e configure as opções de cálculo.")

    col_dim, col_plot = st.columns([1, 2], gap="large")

    with col_dim:
        st.markdown("**Dimensões da Planta**")

        largura = st.number_input(
            "Largura (m)",
            min_value=1.0,
            max_value=500.0,
            value=float(st.session_state["largura"]),
            step=0.5,
            format="%.2f",
            help="Largura da edificação em metros. Mínimo: 1 m.",
        )
        comprimento = st.number_input(
            "Comprimento (m)",
            min_value=1.0,
            max_value=500.0,
            value=float(st.session_state["comprimento"]),
            step=0.5,
            format="%.2f",
            help="Comprimento da edificação em metros. Mínimo: 1 m.",
        )

        # Validação extra de negativos (redundante com min_value, mas defensivo)
        if largura <= 0 or comprimento <= 0:
            st.error("⚠️ Dimensões devem ser maiores que zero.")
            return

        st.session_state["largura"] = largura
        st.session_state["comprimento"] = comprimento

        area = largura * comprimento
        st.metric("Área Calculada", f"{area:.2f} m²", delta=f"Perímetro: {2*(largura+comprimento):.2f} m")

        st.divider()
        st.markdown("**Configurações de Cálculo**")

        desperdicio = st.select_slider(
            "Margem de Desperdício",
            options=[5, 10, 15],
            value=st.session_state["desperdicio"],
            format_func=lambda v: f"{v}%",
            help="Percentual de material adicional previsto para perdas e cortes.",
        )
        st.session_state["desperdicio"] = desperdicio

        perfil = st.radio(
            "Perfil de Acabamento",
            options=PERFIS,
            index=PERFIS.index(st.session_state["perfil_selecionado"]),
            horizontal=False,
            help="Define a faixa de custo dos materiais e serviços utilizados.",
        )
        st.session_state["perfil_selecionado"] = perfil

        st.info(
            f"ℹ️ Com {desperdicio}% de desperdício, cada m² teórico gera "
            f"**{1 + desperdicio/100:.2f}×** a quantidade de material comprado.",
            icon="📊",
        )

    with col_plot:
        st.markdown("**Planta Baixa — Estilo Blueprint ABNT**")
        fig = plotar_planta_baixa(largura, comprimento)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)


def aba_precos() -> None:
    """Renderiza a aba de gestão da tabela de preços locais."""
    st.markdown("### 💲 Tabela de Preços Locais")
    st.caption(
        "Edite os custos unitários diretamente na tabela, importe sua planilha CSV "
        "ou exporte os dados da sessão atual."
    )

    col_import, col_export, col_template = st.columns(3)

    with col_template:
        template_csv = st.session_state["df_precos"].to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Baixar Template CSV",
            data=template_csv,
            file_name="template_precos_obra.csv",
            mime="text/csv",
            help="Baixe a estrutura correta do CSV para preencher com seus preços locais.",
            use_container_width=True,
        )

    with col_import:
        arquivo = st.file_uploader(
            "📂 Importar Tabela CSV",
            type=["csv"],
            help="Carregue um CSV com as colunas: Material / Serviço, Unidade, Custo Unitário (R$), Perfil.",
            label_visibility="collapsed",
        )
        if arquivo is not None:
            df_importado, erro = carregar_csv(arquivo)
            if erro:
                st.error(erro)
            else:
                st.session_state["df_precos"] = df_importado
                st.success(
                    f"✅ Tabela importada com sucesso! "
                    f"{len(df_importado)} registros carregados."
                )

    with col_export:
        csv_sessao = st.session_state["df_precos"].to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📤 Exportar Tabela da Sessão",
            data=csv_sessao,
            file_name="precos_atualizados.csv",
            mime="text/csv",
            help="Salve a tabela atual (com suas edições) em CSV.",
            use_container_width=True,
        )

    st.divider()
    st.markdown("**Editor de Preços** — clique nas células para editar os valores:")

    df_editado = st.data_editor(
        st.session_state["df_precos"],
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "Material / Serviço": st.column_config.TextColumn(
                "Material / Serviço", width="medium"
            ),
            "Unidade": st.column_config.TextColumn("Unidade", width="small"),
            "Custo Unitário (R$)": st.column_config.NumberColumn(
                "Custo Unitário (R$)",
                min_value=0.0,
                format="R$ %.2f",
                width="medium",
            ),
            "Perfil": st.column_config.SelectboxColumn(
                "Perfil",
                options=PERFIS,
                width="small",
            ),
        },
        hide_index=True,
        height=480,
    )

    # Persiste edições no session_state
    st.session_state["df_precos"] = df_editado

    total_registros = len(df_editado)
    col_i1, col_i2, col_i3 = st.columns(3)
    col_i1.metric("Total de Registros", total_registros)
    col_i2.metric("Materiais Únicos", df_editado["Material / Serviço"].nunique())
    col_i3.metric("Perfis Cadastrados", df_editado["Perfil"].nunique())


def aba_resultados() -> None:
    """Renderiza a aba de resultados com orçamento e comparativo de perfis."""
    largura: float = st.session_state["largura"]
    comprimento: float = st.session_state["comprimento"]
    desperdicio_pct: float = st.session_state["desperdicio"] / 100
    perfil: str = st.session_state["perfil_selecionado"]
    df_precos: pd.DataFrame = st.session_state["df_precos"]

    area = largura * comprimento

    # Calcula orçamento do perfil selecionado
    df_orcamento = calcular_orcamento(df_precos, area, desperdicio_pct, perfil)
    custo_total = df_orcamento["Custo Total (R$)"].sum() if not df_orcamento.empty else 0.0

    # Cards de destaque
    renderizar_metricas(area, custo_total, perfil)

    st.divider()

    # Orçamento detalhado
    col_orc, col_comp = st.columns([3, 2], gap="large")

    with col_orc:
        st.markdown(f"#### 📋 Orçamento Detalhado — Perfil {perfil}")
        st.caption(
            f"Desperdício: {st.session_state['desperdicio']}% · "
            f"Área: {area:.2f} m² · Fator: {1+desperdicio_pct:.2f}×"
        )

        if df_orcamento.empty:
            st.warning(
                "⚠️ Nenhum dado encontrado para o perfil selecionado. "
                "Verifique a tabela de preços na aba anterior."
            )
        else:
            # Formatação da tabela de exibição
            df_exib = df_orcamento.copy()
            df_exib["Custo Unit. (R$)"] = df_exib["Custo Unit. (R$)"].apply(
                lambda v: f"R$ {v:,.2f}".replace(",", ".")
            )
            df_exib["Custo Total (R$)"] = df_exib["Custo Total (R$)"].apply(
                lambda v: f"R$ {v:,.2f}".replace(",", ".")
            )
            st.dataframe(
                df_exib,
                use_container_width=True,
                hide_index=True,
                height=400,
            )

            # Exportar orçamento
            csv_orc = df_orcamento.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Exportar Orçamento CSV",
                data=csv_orc,
                file_name=f"orcamento_{perfil.lower()}_{area:.0f}m2.csv",
                mime="text/csv",
                use_container_width=True,
            )

    with col_comp:
        st.markdown("#### 📊 Comparativo Entre Perfis")
        st.caption("Custo total estimado para a mesma obra nos três padrões de acabamento.")

        custos_perfis = calcular_custo_total_por_perfil(df_precos, area, desperdicio_pct)
        fig_comp = plotar_comparativo_perfis(custos_perfis)
        st.pyplot(fig_comp, use_container_width=True)
        plt.close(fig_comp)

        # Mini tabela comparativa
        dados_comp = {
            "Perfil": list(custos_perfis.keys()),
            "Custo Total (R$)": [
                f"R$ {v:,.0f}".replace(",", ".") for v in custos_perfis.values()
            ],
            "Custo/m² (R$)": [
                f"R$ {v/area:,.0f}".replace(",", ".") if area > 0 else "—"
                for v in custos_perfis.values()
            ],
        }
        st.dataframe(
            pd.DataFrame(dados_comp),
            use_container_width=True,
            hide_index=True,
        )

    st.divider()
    renderizar_sugestoes()


# ---------------------------------------------------------------------------
# Ponto de entrada principal
# ---------------------------------------------------------------------------


def main() -> None:
    """
    Função principal — inicializa o estado e renderiza a aplicação completa.
    """
    # Estilos CSS globais
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # Estado da sessão
    inicializar_estado()

    # Cabeçalho
    renderizar_header()

    # Abas principais
    aba1, aba2, aba3 = st.tabs(
        [
            "📐  Parâmetros da Obra",
            "💲  Tabela de Preços Locais",
            "📊  Resultados e Orçamento",
        ]
    )

    with aba1:
        aba_parametros()

    with aba2:
        aba_precos()

    with aba3:
        aba_resultados()

    # Rodapé
    st.markdown("---")
    st.markdown(
        "<p style='text-align:center;color:#2a5a8c;font-size:0.78rem;font-family:monospace;'>"
        "ObraCalc MVP v1.0 · Desenvolvido com Streamlit · "
        "Índices de referência: SINAPI / PINI / TCPO · "
        "Os valores são estimativas e devem ser validados com profissional habilitado."
        "</p>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
