import json
from datetime import datetime, timezone
from urllib.request import Request, urlopen

import streamlit as st

st.set_page_config(page_title="Radar B3 Long CALL", page_icon="📈", layout="wide")

DATA_URL = "https://raw.githubusercontent.com/MarcGynBr/radar-b3-painel/main/indicadores.json"

st.markdown("""
<style>
.stApp {background-color:#0b1220;color:#e5edf7}
h1,h2,h3 {color:#e5edf7!important}
[data-testid="stMetric"] {background-color:#172338;border:1px solid #293b55;border-radius:12px;padding:12px}
[data-testid="stAlert"] {color:#172338}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300, show_spinner=False)
def carregar_indicadores():
    req = Request(DATA_URL, headers={"User-Agent": "RadarB3-MVP7/1.0"})
    with urlopen(req, timeout=12) as resposta:
        dados = json.load(resposta)
    if not isinstance(dados.get("assets"), dict):
        raise ValueError("JSON sem o campo 'assets' esperado")
    return dados


def numero(valor, casas=2):
    if valor is None:
        return "Indisponível"
    return f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")

st.title("📈 Radar B3 Long CALL")
st.caption("MVP 7 • Monitoramento observacional • Sem execução de ordens")

if st.button("🔄 Verificar atualização"):
    carregar_indicadores.clear()
    st.rerun()

try:
    dados = carregar_indicadores()
except Exception as erro:
    st.error("Não foi possível carregar os indicadores do GitHub público.")
    st.caption(f"Detalhe técnico: {type(erro).__name__}: {erro}")
    st.info("Confira se indicadores.json está na raiz do repositório público radar-b3-painel.")
    st.stop()

ativos = dados["assets"]
ranking = dados.get("ranking", [])
ordem = [item.get("ticker") for item in ranking if item.get("ticker") in ativos]
ordem += [ticker for ticker in ativos if ticker not in ordem]

pregoes = sorted({a.get("last_candle_date") for a in ativos.values() if a.get("last_candle_date")})
st.info("Pregão dos dados: " + ", ".join(pregoes) + " • Fonte declarada: " + str(dados.get("source", "não informada")) + " • Não são cotações em tempo real")

try:
    ultima_data = max(datetime.strptime(d, "%Y-%m-%d").date() for d in pregoes)
    if (datetime.now(timezone.utc).date() - ultima_data).days > 4:
        st.warning("Atenção: o arquivo pode estar desatualizado. Verifique a coleta no GitHub privado.")
except (ValueError, TypeError):
    pass

st.subheader("Ranking técnico dos ativos")
cols = st.columns(3)
for i, ticker in enumerate(ordem):
    a = ativos[ticker]
    with cols[i % 3]:
        with st.container(border=True):
            st.subheader(ticker)
            st.metric("Pontuação técnica", f"{a.get('technical_score', '—')}/10")
            st.metric("Fechamento", "R$ " + numero(a.get("close")))
            classificacao = a.get("classification", "NÃO INFORMADA").replace("_", " ")
            st.caption("Classificação: " + classificacao)
            with st.expander("Indicadores e justificativas"):
                st.write("**MM20:**", numero(a.get("mm20")))
                st.write("**MM50:**", numero(a.get("mm50")))
                st.write("**MM200:**", numero(a.get("mm200")))
                st.write("**RSI14:**", numero(a.get("rsi14")))
                st.write("**Histograma MACD:**", numero((a.get("macd") or {}).get("histogram"), 4))
                st.write("**Volume relativo:**", numero(a.get("volume_relative"), 2) + "x")
                st.write("**Suporte de referência:** R$", numero(a.get("recent_support_reference")))
                st.write("**Resistência de referência:** R$", numero(a.get("recent_resistance_reference")))
                st.write("**Critérios da pontuação:**")
                for motivo in a.get("technical_reasons", []):
                    st.write("•", motivo)
                for aviso in a.get("warnings", []):
                    st.warning(aviso)

st.divider()
st.subheader("Grades de opções CALL")
st.info("Ainda não integradas. Não há contratos, strikes, vencimentos ou preços de opções carregados.")
st.subheader("Situação do sistema")
st.write("Indicadores: carregados de arquivo JSON público no GitHub")
st.write("Atualização do arquivo: manual nesta etapa; automação pendente")
st.write("Execução de operações: desativada")
st.caption("Uso experimental. Não constitui recomendação de investimento.")
