import streamlit as st
import json
import os
import pandas as pd
from datetime import date

st.set_page_config(page_title="Controle de Viagem", layout="wide")

ARQUIVO = "dados_viagem.json"

# -------------------------
# CARREGAR DADOS
# -------------------------

def carregar():
    if os.path.exists(ARQUIVO):
        with open(ARQUIVO,"r") as f:
            return json.load(f)
    return []

def salvar(dados):
    with open(ARQUIVO,"w") as f:
        json.dump(dados,f)

dados = carregar()

menu = st.sidebar.selectbox(
    "Menu",
    [
        "Registrar trecho",
        "Dashboard",
        "Estatísticas",
        "Exportar relatório",
        "Configurações"
    ]
)

# =========================
# REGISTRAR TRECHO
# =========================

if menu == "Registrar trecho":

    st.title("Registrar trecho")

    cidade = st.text_input("Cidade")
    data = st.date_input("Data",value=date.today())
    dias = st.number_input("Dias no local",0)

    st.subheader("Motorhome")

    km_motorhome = st.number_input("KM motorhome",0.0)
    consumo_motorhome = st.number_input("Consumo MH (km/l)",0.1)
    preco_diesel = st.number_input("Preço diesel",0.0)
    pedagio = st.number_input("Pedágio",0.0)

    st.subheader("Moto")

    km_moto = st.number_input("KM moto",0.0)
    consumo_moto = st.number_input("Consumo moto (km/l)",0.1)
    preco_gasolina = st.number_input("Preço gasolina",0.0)

    if st.button("Salvar"):

        litros_motorhome = km_motorhome / consumo_motorhome
        gasto_motorhome = litros_motorhome * preco_diesel

        litros_moto = km_moto / consumo_moto
        gasto_moto = litros_moto * preco_gasolina

        trecho = {

            "cidade":cidade,
            "data":str(data),
            "dias":dias,

            "km_motorhome":km_motorhome,
            "litros_motorhome":litros_motorhome,
            "gasto_motorhome":gasto_motorhome,
            "pedagio":pedagio,

            "km_moto":km_moto,
            "litros_moto":litros_moto,
            "gasto_moto":gasto_moto
        }

        dados.append(trecho)
        salvar(dados)

        st.success("Trecho salvo!")

# =========================
# DASHBOARD
# =========================

elif menu == "Dashboard":

    st.title("Resumo da viagem")

    total_km_motorhome = sum(t.get("km_motorhome",0) for t in dados)
    total_km_moto = sum(t.get("km_moto",0) for t in dados)

    total_gasto_motorhome = sum(t.get("gasto_motorhome",0) for t in dados)
    total_gasto_moto = sum(t.get("gasto_moto",0) for t in dados)

    total_pedagio = sum(t.get("pedagio",0) for t in dados)

    total_viagem = total_gasto_motorhome + total_gasto_moto + total_pedagio

    col1,col2,col3 = st.columns(3)

    col1.metric("KM Motorhome",round(total_km_motorhome,2))
    col2.metric("KM Moto",round(total_km_moto,2))
    col3.metric("Custo total",round(total_viagem,2))

# =========================
# ESTATÍSTICAS
# =========================

elif menu == "Estatísticas":

    st.title("Gráficos da viagem")

    if len(dados) == 0:

        st.warning("Nenhum dado registrado")

    else:

        df = pd.DataFrame(dados)

        st.subheader("Gasto combustível")

        gastos = {
            "Motorhome": df["gasto_motorhome"].sum(),
            "Moto": df["gasto_moto"].sum()
        }

        grafico = pd.DataFrame(
            list(gastos.items()),
            columns=["Tipo","Valor"]
        )

        st.bar_chart(grafico.set_index("Tipo"))

        st.subheader("KM percorridos")

        kms = {
            "Motorhome": df["km_motorhome"].sum(),
            "Moto": df["km_moto"].sum()
        }

        grafico_km = pd.DataFrame(
            list(kms.items()),
            columns=["Veículo","KM"]
        )

        st.bar_chart(grafico_km.set_index("Veículo"))

# =========================
# EXPORTAR RELATÓRIO
# =========================

elif menu == "Exportar relatório":

    st.title("Baixar relatório da viagem")

    if len(dados) == 0:

        st.warning("Nenhum dado para exportar")

    else:

        df = pd.DataFrame(dados)

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Baixar relatório CSV",
            csv,
            "relatorio_viagem.csv",
            "text/csv"
        )

# =========================
# CONFIGURAÇÕES
# =========================

elif menu == "Configurações":

    if st.button("Apagar todos os dados"):

        salvar([])

        st.success("Dados apagados")