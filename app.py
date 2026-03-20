import streamlit as st
import json
import os
import pandas as pd
from datetime import date
import requests
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Controle de Viagem", layout="wide")

ARQUIVO = "dados_viagem.json"

# -------------------------
# GEOLOCALIZAÇÃO
# -------------------------
@st.cache_data
def buscar_coordenadas(cidade, pais):
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": f"{cidade}, {pais}", "format": "json"}
        headers = {"User-Agent": "app-viagem"}

        response = requests.get(url, params=params, headers=headers, timeout=5)
        data = response.json()

        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except:
        pass

    return None, None

# -------------------------
# FUNÇÕES
# -------------------------
def carregar():
    if os.path.exists(ARQUIVO):
        with open(ARQUIVO, "r") as f:
            return json.load(f)
    return []

def salvar(dados):
    with open(ARQUIVO, "w") as f:
        json.dump(dados, f, indent=4)

dados = carregar()

# -------------------------
# MENU
# -------------------------
menu = st.sidebar.radio("Menu", [
    "Dashboard",
    "Registrar",
    "Mapa",
    "Backup",
    "Configurações"
])

# -------------------------
# DASHBOARD
# -------------------------
if menu == "Dashboard":

    st.title("🌍 Dashboard")

    if not dados:
        st.info("Sem dados ainda")
    else:
        df = pd.DataFrame(dados)

        km_total = df["km_motorhome"].sum() + df["km_moto"].sum()
        gasto_total = (
            df["gasto_motorhome"].sum() +
            df["gasto_moto"].sum() +
            df["pedagio"].sum() +
            df["ferry"].sum() +
            df["bus"].sum() +
            df["aviao"].sum()
        )

        col1, col2, col3 = st.columns(3)
        col1.metric("KM Total", round(km_total,2))
        col2.metric("Gasto Total", f"R$ {round(gasto_total,2)}")
        col3.metric("Custo/KM", round(gasto_total/km_total,2) if km_total else 0)

# -------------------------
# REGISTRAR
# -------------------------
elif menu == "Registrar":

    st.title("Registrar trecho")

    col1, col2 = st.columns(2)

    with col1:
        cidade = st.text_input("Cidade")
        pais = st.text_input("País")
        data = st.date_input("Data", value=date.today())
        dias = st.number_input("Dias", 0)

    with col2:
        km_motorhome = st.number_input("KM Motorhome", 0.0)
        consumo_motorhome = st.number_input("Consumo MH", 0.1)
        preco_diesel = st.number_input("Preço Diesel", 0.0)

        km_moto = st.number_input("KM Moto", 0.0)
        consumo_moto = st.number_input("Consumo Moto", 0.1)
        preco_gasolina = st.number_input("Preço Gasolina", 0.0)

    pedagio = st.number_input("Pedágio", 0.0)
    ferry = st.number_input("Ferry", 0.0)
    bus = st.number_input("Ônibus", 0.0)
    aviao = st.number_input("Avião", 0.0)

    if st.button("📍 Ver localização"):
        lat, lon = buscar_coordenadas(cidade, pais)

        if lat:
            mapa_temp = folium.Map(location=[lat, lon], zoom_start=6)
            folium.Marker([lat, lon], tooltip=f"{cidade}, {pais}").add_to(mapa_temp)
            st_folium(mapa_temp, width=700)
        else:
            st.error("Local não encontrado")

    if st.button("💾 Salvar"):
        if cidade and pais:
            lat, lon = buscar_coordenadas(cidade, pais)

            if lat:
                gasto_motorhome = (km_motorhome/consumo_motorhome)*preco_diesel if consumo_motorhome else 0
                gasto_moto = (km_moto/consumo_moto)*preco_gasolina if consumo_moto else 0

                dados.append({
                    "cidade":cidade,
                    "pais":pais,
                    "data":str(data),
                    "dias":dias,
                    "lat":lat,
                    "lon":lon,
                    "km_motorhome":km_motorhome,
                    "gasto_motorhome":gasto_motorhome,
                    "km_moto":km_moto,
                    "gasto_moto":gasto_moto,
                    "pedagio":pedagio,
                    "ferry":ferry,
                    "bus":bus,
                    "aviao":aviao
                })

                salvar(dados)
                st.success("Salvo com sucesso!")
            else:
                st.error("Erro na localização")

# -------------------------
# MAPA
# -------------------------
elif menu == "Mapa":

    st.title("🗺 Mapa da viagem")

    if not dados:
        st.info("Sem dados")
    else:
        df = pd.DataFrame(dados)
        df["data"] = pd.to_datetime(df["data"])
        df = df.sort_values("data")

        mapa = folium.Map(location=[df["lat"].mean(), df["lon"].mean()], zoom_start=3)

        coords = []

        for _, row in df.iterrows():
            coords.append([row["lat"], row["lon"]])

            folium.Marker(
                [row["lat"], row["lon"]],
                popup=f"{row['cidade']} - {row['pais']}<br>{row['data'].date()}",
                icon=folium.Icon(color="blue")
            ).add_to(mapa)

        # Linha da rota
        folium.PolyLine(coords, color="red", weight=4).add_to(mapa)

        st_folium(mapa, width=1000, height=600)

# -------------------------
# BACKUP
# -------------------------
elif menu == "Backup":

    st.title("Backup")

    st.download_button("Baixar JSON", json.dumps(dados), "backup.json")

    if dados:
        df = pd.DataFrame(dados)
        st.download_button("Baixar Excel", df.to_csv(index=False), "dados.csv")

# -------------------------
# CONFIG
# -------------------------
elif menu == "Configurações":

    if st.button("Apagar dados"):
        salvar([])
        st.success("Dados apagados")git add .
git commit -m "update1"
git push