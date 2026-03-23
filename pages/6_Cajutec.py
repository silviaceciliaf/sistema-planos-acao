import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Tokyo - Planos de Ação",
    layout="wide"
)

ARQUIVO = "base_planos_acao.xlsx"
ABA = "TRATAMENTO"
EMPRESA_FIXA = "Cajutec"

@st.cache_data
def carregar_dados():
    df = pd.read_excel(ARQUIVO, sheet_name=ABA)
    df.columns = [str(col).strip().upper() for col in df.columns]

    if "ATIVIDADE" in df.columns:
        df = df[df["ATIVIDADE"].notna()]
        df = df[df["ATIVIDADE"].astype(str).str.strip() != ""]

    return df

df = carregar_dados()

if "EMPRESA" in df.columns:
    df = df[df["EMPRESA"].astype(str).str.strip().str.upper() == EMPRESA_FIXA.upper()]

st.title(f"Planos de Ação - {EMPRESA_FIXA}")

c1, c2, c3, c4 = st.columns(4)

total = len(df)
concluidas = len(df[df["STATUS"].astype(str).str.upper() == "CONCLUÍDO"]) if "STATUS" in df.columns else 0
em_andamento = len(df[df["STATUS"].astype(str).str.upper() == "EM ANDAMENTO"]) if "STATUS" in df.columns else 0
atrasadas = len(df[df["SITUAÇÃO PRAZO"].astype(str).str.upper() == "ATRASADO"]) if "SITUAÇÃO PRAZO" in df.columns else 0

c1.metric("Total de ações", total)
c2.metric("Concluídas", concluidas)
c3.metric("Em andamento", em_andamento)
c4.metric("Atrasadas", atrasadas)

st.divider()

f1, f2, f3 = st.columns(3)

with f1:
    unidade = st.multiselect(
        "Unidade",
        sorted(df["UNIDADE"].dropna().unique()) if "UNIDADE" in df.columns else []
    )

with f2:
    status = st.multiselect(
        "Status",
        sorted(df["STATUS"].dropna().unique()) if "STATUS" in df.columns else []
    )

with f3:
    responsavel = st.multiselect(
        "Responsável",
        sorted(df["RESPONSÁVEL"].dropna().unique()) if "RESPONSÁVEL" in df.columns else []
    )

df_filtrado = df.copy()

if unidade:
    df_filtrado = df_filtrado[df_filtrado["UNIDADE"].isin(unidade)]

if status:
    df_filtrado = df_filtrado[df_filtrado["STATUS"].isin(status)]

if responsavel:
    df_filtrado = df_filtrado[df_filtrado["RESPONSÁVEL"].isin(responsavel)]

g1, g2 = st.columns(2)

with g1:
    st.subheader("Ações por status")
    if "STATUS" in df_filtrado.columns:
        st.bar_chart(df_filtrado["STATUS"].value_counts())

with g2:
    st.subheader("Ações por unidade")
    if "UNIDADE" in df_filtrado.columns:
        st.bar_chart(df_filtrado["UNIDADE"].value_counts())

st.divider()

st.subheader("Tabela detalhada")
st.dataframe(df_filtrado, use_container_width=True)