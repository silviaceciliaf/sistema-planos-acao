import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Painel Geral - Planos de Ação",
    layout="wide"
)

ARQUIVO = "base_planos_acao.xlsx"
ABA = "TRATAMENTO"

@st.cache_data
def carregar_dados():
    df = pd.read_excel(ARQUIVO, sheet_name=ABA)
    df.columns = [str(col).strip().upper() for col in df.columns]

    if "ATIVIDADE" in df.columns:
        df = df[df["ATIVIDADE"].notna()]
        df = df[df["ATIVIDADE"].astype(str).str.strip() != ""]

    # Padronização de texto
    colunas_texto = [
        "EMPRESA", "UNIDADE", "CATEGORIA", "ATIVIDADE", "RESPONSÁVEL",
        "STATUS", "PRIORIDADE", "SITUAÇÃO PRAZO", "ALERTA ATUALIZAÇÃO"
    ]
    for col in colunas_texto:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # Conversão numérica
    colunas_numericas = ["% AVANÇO", "DIAS PARA PRAZO", "DIAS EM ATRASO", "DIAS SEM ATUALIZAÇÃO"]
    for col in colunas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df

df = carregar_dados()

st.title("Painel Geral de Planos de Ação")
st.caption("Visão executiva consolidada da holding")

# Filtros
f1, f2, f3, f4, f5 = st.columns(5)

with f1:
    empresa = st.multiselect(
        "Empresa",
        sorted(df["EMPRESA"].dropna().unique()) if "EMPRESA" in df.columns else []
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

with f4:
    situacao_prazo = st.multiselect(
        "Situação prazo",
        sorted(df["SITUAÇÃO PRAZO"].dropna().unique()) if "SITUAÇÃO PRAZO" in df.columns else []
    )

with f5:
    prioridade = st.multiselect(
        "Prioridade",
        sorted(df["PRIORIDADE"].dropna().unique()) if "PRIORIDADE" in df.columns else []
    )

df_filtrado = df.copy()

if empresa:
    df_filtrado = df_filtrado[df_filtrado["EMPRESA"].isin(empresa)]

if status:
    df_filtrado = df_filtrado[df_filtrado["STATUS"].isin(status)]

if responsavel:
    df_filtrado = df_filtrado[df_filtrado["RESPONSÁVEL"].isin(responsavel)]

if situacao_prazo:
    df_filtrado = df_filtrado[df_filtrado["SITUAÇÃO PRAZO"].isin(situacao_prazo)]

if prioridade:
    df_filtrado = df_filtrado[df_filtrado["PRIORIDADE"].isin(prioridade)]

# Indicadores
total = len(df_filtrado)

concluidas = len(df_filtrado[df_filtrado["STATUS"].str.upper() == "CONCLUÍDO"]) if "STATUS" in df_filtrado.columns else 0
em_andamento = len(df_filtrado[df_filtrado["STATUS"].str.upper() == "EM ANDAMENTO"]) if "STATUS" in df_filtrado.columns else 0
pendentes = len(df_filtrado[df_filtrado["STATUS"].str.upper() == "PENDENTE"]) if "STATUS" in df_filtrado.columns else 0
atrasadas = len(df_filtrado[df_filtrado["SITUAÇÃO PRAZO"].str.upper() == "ATRASADO"]) if "SITUAÇÃO PRAZO" in df_filtrado.columns else 0
sem_atualizacao = len(
    df_filtrado[df_filtrado["ALERTA ATUALIZAÇÃO"].str.upper() == "MAIS DE 7 DIAS SEM ATUALIZAR"]
) if "ALERTA ATUALIZAÇÃO" in df_filtrado.columns else 0

percentual_medio_avanco = round(df_filtrado["% AVANÇO"].fillna(0).mean(), 1) if "% AVANÇO" in df_filtrado.columns else 0
percentual_concluidas = round((concluidas / total) * 100, 1) if total > 0 else 0
percentual_atrasadas = round((atrasadas / total) * 100, 1) if total > 0 else 0
media_dias_atraso = round(df_filtrado["DIAS EM ATRASO"].fillna(0).mean(), 1) if "DIAS EM ATRASO" in df_filtrado.columns else 0
media_dias_sem_atualizacao = round(df_filtrado["DIAS SEM ATUALIZAÇÃO"].fillna(0).mean(), 1) if "DIAS SEM ATUALIZAÇÃO" in df_filtrado.columns else 0

# Linha 1 de cards
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Total de ações", total)
c2.metric("Concluídas", concluidas)
c3.metric("Em andamento", em_andamento)
c4.metric("Pendentes", pendentes)
c5.metric("Atrasadas", atrasadas)
c6.metric("Sem atualização", sem_atualizacao)

# Linha 2 de cards
c7, c8, c9, c10 = st.columns(4)
c7.metric("% concluídas", f"{percentual_concluidas}%")
c8.metric("% atrasadas", f"{percentual_atrasadas}%")
c9.metric("% médio de avanço", f"{percentual_medio_avanco}%")
c10.metric("Média dias sem atualização", media_dias_sem_atualizacao)

st.divider()

# Gráficos
g1, g2 = st.columns(2)

with g1:
    st.subheader("Ações por empresa")
    if "EMPRESA" in df_filtrado.columns:
        st.bar_chart(df_filtrado["EMPRESA"].value_counts())

with g2:
    st.subheader("Ações por status")
    if "STATUS" in df_filtrado.columns:
        st.bar_chart(df_filtrado["STATUS"].value_counts())

g3, g4 = st.columns(2)

with g3:
    st.subheader("Situação de prazo")
    if "SITUAÇÃO PRAZO" in df_filtrado.columns:
        st.bar_chart(df_filtrado["SITUAÇÃO PRAZO"].value_counts())

with g4:
    st.subheader("Ações por responsável")
    if "RESPONSÁVEL" in df_filtrado.columns:
        st.bar_chart(df_filtrado["RESPONSÁVEL"].value_counts())

st.divider()

# Bloco de insights rápidos
i1, i2, i3 = st.columns(3)

with i1:
    st.subheader("Empresa com mais ações")
    if "EMPRESA" in df_filtrado.columns and not df_filtrado["EMPRESA"].empty:
        empresa_top = df_filtrado["EMPRESA"].value_counts().idxmax()
        qtd_empresa_top = df_filtrado["EMPRESA"].value_counts().max()
        st.info(f"{empresa_top} ({qtd_empresa_top} ações)")

with i2:
    st.subheader("Responsável com mais ações")
    if "RESPONSÁVEL" in df_filtrado.columns and not df_filtrado["RESPONSÁVEL"].empty:
        resp_top = df_filtrado["RESPONSÁVEL"].value_counts().idxmax()
        qtd_resp_top = df_filtrado["RESPONSÁVEL"].value_counts().max()
        st.info(f"{resp_top} ({qtd_resp_top} ações)")

with i3:
    st.subheader("Média de dias em atraso")
    st.info(f"{media_dias_atraso} dias")

st.divider()
st.info("A tabela detalhada das ações está disponível nas páginas individuais de cada empresa.")