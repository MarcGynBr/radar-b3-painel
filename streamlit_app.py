import json
from datetime import datetime, timezone
from urllib.request import Request, urlopen

import streamlit as st

st.set_page_config(page_title="Radar B3 Long CALL", page_icon="📈", layout="wide")
DATA_URL = "https://raw.githubusercontent.com/MarcGynBr/radar-b3-painel/main/indicadores.json"

st.markdown("""
<style>
.stApp {background:#0b1220;color:#f2f6ff}
h1,h2,h3 {color:#f2f6ff!important}
[data-testid="stMetric"] {background:#172338;border:1px solid #365071;border-radius:12px;padding:14px}
[data-testid="stMetricLabel"] *, [data-testid="stMetricLabel"] {color:#d5e3f7!important}
[data-testid="stMetricValue"] *, [data-testid="stMetricValue"] {color:#ffffff!important;opacity:1!important}
[data-testid="stMetricValue"] {font-weight:750!important}
[data-testid="stVerticalBlockBorderWrapper"] {border-color:#365071!important}
[data-testid="stExpander"] {border-color:#365071!important}
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary * {color:#f2f6ff!important}
.stApp [data-testid="stCaptionContainer"], .stApp [data-testid="stCaptionContainer"] * {color:#c2d2e8!important}
.stApp [data-testid="stMarkdownContainer"] p {line-height:1.5}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300, show_spinner=False)
def carregar_indicadores():
    req = Request(DATA_URL, headers={"User-Agent": "RadarB3-MVP7/2.0", "Cache-Control": "no-cache"})
    with urlopen(req, timeout=15) as resposta:
        dados = json.load(resposta)
    if not isinstance(dados, dict) or not isinstance(dados.get("assets"), dict):
        raise ValueError("Arquivo sem objeto 'assets' válido")
    return dados


def numero(valor, casas=2):
    if valor is None or isinstance(valor, bool):
        return "—"
    try:
        return f"{float(valor):,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (TypeError, ValueError, OverflowError):
        return "—"


def data_br(valor):
    try:
        return datetime.strptime(valor, "%Y-%m-%d").strftime("%d/%m/%Y")
    except (TypeError, ValueError):
        return "não informada"


st.title("📈 Radar B3 Long CALL")
st.caption("MVP 7 • Monitoramento observacional • Sem execução de ordens")
if st.button("🔄 Verificar atualização", type="secondary"):
    carregar_indicadores.clear()
    st.rerun()

try:
    dados = carregar_indicadores()
except Exception as erro:
    st.error("Não foi possível ler os indicadores publicados no GitHub.")
    st.caption(f"Diagnóstico: {type(erro).__name__}: {erro}")
    st.stop()

ativos = dados["assets"]
ranking = dados.get("ranking", [])
ordem = [item.get("ticker") for item in ranking if isinstance(item, dict) and item.get("ticker") in ativos]
ordem += [ticker for ticker in ativos if ticker not in ordem]
datas = sorted({a.get("last_candle_date") for a in ativos.values() if isinstance(a, dict) and a.get("last_candle_date")})
ultima_data = max(datas) if datas else None
st.caption(f"Último pregão nos dados: {data_br(ultima_data)} • Fonte declarada: {dados.get('source', 'não informada')} • Sem cotações em tempo real")
if ultima_data:
    try:
        idade = (datetime.now(timezone.utc).date() - datetime.strptime(ultima_data, "%Y-%m-%d").date()).days
        if idade > 4:
            st.warning(f"Dados com {idade} dias corridos desde o pregão informado. Confira a coleta automática.")
    except ValueError:
        st.warning("Data de pregão inválida no arquivo.")

st.subheader("Ranking técnico dos ativos")
colunas = st.columns(3)
for i, ticker in enumerate(ordem):
    a = ativos[ticker]
    if not isinstance(a, dict):
        continue
    with colunas[i % 3]:
        with st.container(border=True):
            st.subheader(ticker)
            pontuacao = a.get("technical_score")
            st.metric("Pontuação técnica", f"{pontuacao}/10" if pontuacao is not None else "—")
            st.metric("Fechamento", "R$ " + numero(a.get("close")))
            st.caption("Classificação: " + str(a.get("classification", "NÃO INFORMADA")).replace("_", " "))
            with st.expander("Indicadores e justificativas"):
                st.write("**Pregão:**", data_br(a.get("last_candle_date")))
                st.write("**MM20:**", numero(a.get("mm20")))
                st.write("**MM50:**", numero(a.get("mm50")))
                st.write("**MM200:**", numero(a.get("mm200")))
                st.write("**RSI14:**", numero(a.get("rsi14")))
                st.write("**Histograma MACD:**", numero((a.get("macd") or {}).get("histogram"), 4))
                st.write("**Volume relativo:**", numero(a.get("volume_relative")) + "x")
                st.write("**Suporte de referência:** R$", numero(a.get("recent_support_reference")))
                st.write("**Resistência de referência:** R$", numero(a.get("recent_resistance_reference")))
                st.write("**Critérios da pontuação:**")
                for motivo in a.get("technical_reasons", []):
                    st.write("•", str(motivo))
                for aviso in a.get("warnings", []):
                    st.warning(str(aviso))

st.divider()
st.subheader("Grades de opções CALL")
st.info("Módulo pendente: ainda não temos contratos, strikes, vencimentos ou cotações de opções.")
st.subheader("Situação do sistema")
st.write("Indicadores: lidos do JSON no GitHub público")
st.write("Publicação automática: depende da configuração do fluxo no GitHub privado")
st.write("Execução de operações: desativada")
st.caption("Uso experimental. Pontuações técnicas não são sinais confirmados de compra nem recomendação de investimento.")
