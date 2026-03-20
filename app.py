import streamlit as st
import json
import os
import pandas as pd
from datetime import date
import requests

st.set_page_config(page_title="Controle de Viagem Motorhome", layout="wide")

ARQUIVO = "dados_viagem.json"

# -------------------------
# GEOLOCALIZAÇÃO AUTOMÁTICA
# -------------------------

def buscar_coordenadas(cidade, pais):

    try:
        url = "https://nominatim.openstreetmap.org/search"

        params = {
            "city": cidade,
            "country": pais,
            "format": "json"
        }

        headers = {
            "User-Agent": "app-viagem"
        }

        response = requests.get(url, params=params, headers=headers)

        data = response.json()

        if len(data) > 0:
            return float(data[0]["lat"]), float(data[0]["lon"])

    except:
        pass

    return 0, 0

# -------------------------
# FUNÇÕES
# -------------------------

def carregar():
    if os.path.exists(ARQUIVO):
        with open(ARQUIVO,"r") as f:
            return json.load(f)
    return []

def salvar(dados):
    with open(ARQUIVO,"w") as f:
        json.dump(dados,f)

def garantir_colunas(df):

    colunas = [
        "cidade","pais","data","dias",
        "lat","lon",
        "km_motorhome","gasto_motorhome",
        "km_moto","gasto_moto",
        "pedagio","ferry","bus","aviao"
    ]

    for c in colunas:
        if c not in df.columns:
            df[c] = 0

    return df

dados = carregar()

# -------------------------
# MENU
# -------------------------

menu = st.sidebar.selectbox(
    "Menu",
    [
        "Dashboard",
        "Registrar trecho",
        "História da viagem",
        "Mapa da viagem",
        "Estatísticas",
        "Backup da viagem",
        "Configurações"
    ]
)

# -------------------------
# DASHBOARD
# -------------------------

if menu == "Dashboard":

    st.title("🌎 Dashboard da viagem")

    if len(dados) == 0:

        st.info("Nenhum trecho registrado")

    else:

        df = pd.DataFrame(dados)
        df = garantir_colunas(df)

        total_km_motorhome = df["km_motorhome"].sum()
        total_km_moto = df["km_moto"].sum()

        total_diesel = df["gasto_motorhome"].sum()
        total_gasolina = df["gasto_moto"].sum()

        total_viagem = (
            total_diesel +
            total_gasolina +
            df["pedagio"].sum() +
            df["ferry"].sum() +
            df["bus"].sum() +
            df["aviao"].sum()
        )

        cidades = len(set(df["cidade"]))
        paises = len(set(df["pais"]))

        dias_total = df["dias"].sum()

        km_total = total_km_motorhome + total_km_moto

        custo_km = total_viagem / km_total if km_total > 0 else 0

        col1,col2,col3,col4 = st.columns(4)

        col1.metric("🚐 KM Motorhome", round(total_km_motorhome,2))
        col2.metric("🛵 KM Moto", round(total_km_moto,2))
        col3.metric("🏙 Cidades", cidades)
        col4.metric("🌎 Países", paises)

        col1,col2,col3,col4 = st.columns(4)

        col1.metric("📅 Dias", dias_total)
        col2.metric("💰 Diesel", f"R$ {round(total_diesel,2)}")
        col3.metric("💰 Gasolina", f"R$ {round(total_gasolina,2)}")
        col4.metric("💰 Total", f"R$ {round(total_viagem,2)}")

        st.metric("💰 Custo/KM", f"R$ {round(custo_km,2)}")

# -------------------------
# REGISTRAR TRECHO
# -------------------------

elif menu == "Registrar trecho":

    st.title("Registrar trecho")

    cidade = st.text_input("Cidade")
    pais = st.text_input("País")

    data = st.date_input("Data",value=date.today())
    dias = st.number_input("Dias no local",0)

    st.subheader("Motorhome")

    km_motorhome = st.number_input("KM MH",0.0)
    consumo_motorhome = st.number_input("Consumo MH",0.1)
    preco_diesel = st.number_input("Preço diesel",0.0)
    pedagio = st.number_input("Pedágio",0.0)

    st.subheader("Moto")

    km_moto = st.number_input("KM moto",0.0)
    consumo_moto = st.number_input("Consumo moto",0.1)
    preco_gasolina = st.number_input("Preço gasolina",0.0)

    st.subheader("Transportes")

    ferry = st.number_input("Ferry",0.0)
    bus = st.number_input("Ônibus",0.0)
    aviao = st.number_input("Avião",0.0)

    if st.button("Salvar trecho"):

        lat, lon = buscar_coordenadas(cidade, pais)

        litros_motorhome = km_motorhome / consumo_motorhome
        gasto_motorhome = litros_motorhome * preco_diesel

        litros_moto = km_moto / consumo_moto
        gasto_moto = litros_moto * preco_gasolina

        trecho = {

            "cidade":cidade,
            "pais":pais,
            "data":str(data),
            "dias":dias,

            "lat":lat,
            "lon":lon,

            "km_motorhome":km_motorhome,
            "gasto_motorhome":gasto_motorhome,
            "pedagio":pedagio,

            "km_moto":km_moto,
            "gasto_moto":gasto_moto,

            "ferry":ferry,
            "bus":bus,
            "aviao":aviao
        }

        dados.append(trecho)
        salvar(dados)

        st.success("Trecho salvo com localização automática!")

# -------------------------
# MAPA
# -------------------------

elif menu == "Mapa da viagem":

    st.title("🗺 Mapa da viagem")

    if len(dados) == 0:

        st.info("Sem dados")

    else:

        df = pd.DataFrame(dados)
        df = garantir_colunas(df)

        mapa = df[(df["lat"] != 0) & (df["lon"] != 0)]

        if len(mapa) > 0:

            st.map(mapa[["lat","lon"]])

        else:

            st.warning("Nenhuma localização encontrada")

# -------------------------
# BACKUP
# -------------------------

elif menu == "Backup da viagem":

    st.title("💾 Backup")

    backup = json.dumps(dados).encode("utf-8")

    st.download_button(
        "Baixar backup",
        backup,
        "backup.json",
        "application/json"
    )

# -------------------------
# CONFIG
# -------------------------

elif menu == "Configurações":

    if st.button("Apagar dados"):

        salvar([])
        st.success("Dados apagados")