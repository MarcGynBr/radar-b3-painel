
import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Radar B3 Long CALL",
    page_icon="📈",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #0b1220;
    color: #e5edf7;
}
h1, h2, h3 {
    color: #e5edf7 !important;
}
[data-testid="stMetric"] {
    background-color: #172338;
    border: 1px solid #293b55;
    border-radius: 12px;
    padding: 16px;
}
</style>
""", unsafe_allow_html=True)

st.title("📈 Radar B3 Long CALL")
st.caption("MVP 7 • Monitoramento de mercado • Sem execução de ordens")

st.info(
    "Painel demonstrativo. Os indicadores reais ainda "
    "não estão conectados ao coletor do GitHub."
)

ativos = ["PETR4", "VALE3", "BOVA11", "ITUB4", "BBAS3", "BBDC4"]

st.subheader("Ativos monitorados")

colunas = st.columns(3)

for i, ativo in enumerate(ativos):
    with colunas[i % 3]:
        with st.container(border=True):
            st.subheader(ativo)
            st.metric("Pontuação técnica", "—")
            st.caption("Aguardando dados atualizados")
            st.button(
                "Ver detalhes",
                key=f"detalhes_{ativo}",
                disabled=True
            )

st.divider()

st.subheader("Grades de opções CALL")
st.warning(
    "Módulo em desenvolvimento. "
    "Ainda não há contratos ou cotações de opções carregados."
)

st.subheader("Situação do sistema")
st.write("Coleta de ações: existente no repositório privado")
st.write("Integração dos indicadores: pendente")
st.write("Grades de opções: pendente")
st.write("Execução de operações: desativada")

st.caption("Uso experimental. Não constitui recomendação de investimento.")
