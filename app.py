import streamlit as st
import json
import os
import pandas as pd
from datetime import date
import requests
import pydeck as pdk

st.set_page_config(page_title="Controle de Viagem Motorhome", layout="wide")

ARQUIVO = "dados_viagem.json"

# -------------------------
# GEOLOCALIZAÇÃO COM CACHE
# -------------------------
@st.cache_data
def buscar_coordenadas(cidade, pais):
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": f"{cidade}, {pais}", "format": "json"}
        headers = {"User-Agent": "app-viagem"}

        response = requests.get(url, params=params, headers=headers, timeout=5)
        data = response.json()

        if len(data) > 0:
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
    ["Dashboard","Registrar trecho","Mapa da viagem","Estatísticas","Backup","Configurações"]
)

# -------------------------
# DASHBOARD
# -------------------------
if menu == "Dashboard":

    st.title("🌎 Dashboard")

    if not dados:
        st.info("Nenhum dado ainda")
    else:
        df = garantir_colunas(pd.DataFrame(dados))

        km_total = df["km_motorhome"].sum() + df["km_moto"].sum()
        gasto_total = (
            df["gasto_motorhome"].sum() +
            df["gasto_moto"].sum() +
            df["pedagio"].sum() +
            df["ferry"].sum() +
            df["bus"].sum() +
            df["aviao"].sum()
        )

        col1,col2,col3 = st.columns(3)
        col1.metric("KM Total", round(km_total,2))
        col2.metric("Gasto Total", f"R$ {round(gasto_total,2)}")
        col3.metric("Custo/KM", round(gasto_total/km_total,2) if km_total>0 else 0)

# -------------------------
# REGISTRAR
# -------------------------
elif menu == "Registrar trecho":

    st.title("Registrar trecho")

    cidade = st.text_input("Cidade")
    pais = st.text_input("País")

    data = st.date_input("Data", value=date.today())
    dias = st.number_input("Dias",0)

    km_motorhome = st.number_input("KM Motorhome",0.0)
    consumo_motorhome = st.number_input("Consumo MH",0.1)
    preco_diesel = st.number_input("Preço Diesel",0.0)
    pedagio = st.number_input("Pedágio",0.0)

    km_moto = st.number_input("KM Moto",0.0)
    consumo_moto = st.number_input("Consumo Moto",0.1)
    preco_gasolina = st.number_input("Preço Gasolina",0.0)

    ferry = st.number_input("Ferry",0.0)
    bus = st.number_input("Ônibus",0.0)
    aviao = st.number_input("Avião",0.0)

    if st.button("📍 Ver localização"):
        lat, lon = buscar_coordenadas(cidade, pais)
        if lat:
            st.map(pd.DataFrame({"lat":[lat],"lon":[lon]}))
        else:
            st.error("Local não encontrado")

    if st.button("💾 Salvar"):
        if cidade and pais:
            lat, lon = buscar_coordenadas(cidade, pais)

            if lat:
                gasto_motorhome = (km_motorhome/consumo_motorhome)*preco_diesel if consumo_motorhome>0 else 0
                gasto_moto = (km_moto/consumo_moto)*preco_gasolina if consumo_moto>0 else 0

                dados.append({
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
                })

                salvar(dados)
                st.success("Salvo!")
            else:
                st.error("Erro na localização")

# -------------------------
# MAPA AVANÇADO
# -------------------------
elif menu == "Mapa da viagem":

    st.title("🗺 Mapa")

    if not dados:
        st.info("Sem dados")
    else:
        df = garantir_colunas(pd.DataFrame(dados))
        df = df.sort_values("data")

        paises = st.multiselect("Filtrar por país", df["pais"].unique())
        if paises:
            df = df[df["pais"].isin(paises)]

        df["data"] = pd.to_datetime(df["data"])
        data_range = st.date_input("Período",[df["data"].min(), df["data"].max()])

        if len(data_range)==2:
            df = df[(df["data"]>=pd.to_datetime(data_range[0])) & (df["data"]<=pd.to_datetime(data_range[1]))]

        coords = df[["lon","lat"]].values.tolist()

        layer_line = pdk.Layer(
            "PathLayer",
            data=[{"path": coords}],
            get_path="path",
            width_scale=20,
            width_min_pixels=3,
        )

        layer_points = pdk.Layer(
            "ScatterplotLayer",
            data=df,
            get_position='[lon, lat]',
            get_radius=40000,
            pickable=True
        )

        view = pdk.ViewState(
            latitude=df["lat"].mean(),
            longitude=df["lon"].mean(),
            zoom=3
        )

        deck = pdk.Deck(
            layers=[layer_line, layer_points],
            initial_view_state=view,
            tooltip={"text": "{cidade} - {pais}"}
        )

        st.pydeck_chart(deck)

# -------------------------
# ESTATÍSTICAS
# -------------------------
elif menu == "Estatísticas":

    st.title("📊 Estatísticas")

    if not dados:
        st.info("Sem dados")
    else:
        df = garantir_colunas(pd.DataFrame(dados))

        gastos = {
            "Diesel": df["gasto_motorhome"].sum(),
            "Gasolina": df["gasto_moto"].sum(),
            "Pedágio": df["pedagio"].sum(),
            "Ferry": df["ferry"].sum(),
            "Ônibus": df["bus"].sum(),
            "Avião": df["aviao"].sum()
        }

        st.bar_chart(pd.DataFrame(gastos.values(), index=gastos.keys()))

# -------------------------
# BACKUP
# -------------------------
elif menu == "Backup":

    st.download_button("Baixar JSON", json.dumps(dados), "backup.json")

    if dados:
        df = pd.DataFrame(dados)
        st.download_button("Baixar Excel", df.to_csv(index=False), "dados.csv")

# -------------------------
# CONFIG
# -------------------------
elif menu == "Configurações":

    if st.button("Apagar tudo"):
        salvar([])
        st.success("Dados apagados")