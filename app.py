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
# BUSCA DE CIDADES (AUTOCOMPLETE)
# -------------------------
@st.cache_data
def buscar_cidades(query):
    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": query,
        "format": "json",
        "addressdetails": 1,
        "limit": 5
    }

    headers = {"User-Agent": "app-viagem"}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
        data = response.json()

        resultados = []
        for item in data:
            resultados.append({
                "nome": item.get("display_name"),
                "lat": float(item.get("lat")),
                "lon": float(item.get("lon"))
            })

        return resultados
    except:
        return []

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
menu = st.sidebar.radio("Menu", [
    "Dashboard",
    "Registrar trecho",
    "Histórico da viagem",
    "Mapa da viagem",
    "Estatísticas",
    "Backup",
    "Configurações"
])

# -------------------------
# DASHBOARD
# -------------------------
if menu == "Dashboard":

    st.title("🌍 Dashboard")

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

        col1,col2,col3,col4 = st.columns(4)
        col1.metric("KM Total", round(km_total,2))
        col2.metric("Gasto Total", f"R$ {round(gasto_total,2)}")
        col3.metric("Cidades", df["cidade"].nunique())
        col4.metric("Países", df["pais"].nunique())

        st.metric("Custo/KM", round(gasto_total/km_total,2) if km_total else 0)

# -------------------------
# REGISTRAR TRECHO
# -------------------------
elif menu == "Registrar trecho":

    st.title("Registrar trecho")

    busca = st.text_input("🔍 Buscar cidade")

    coordenada_escolhida = None
    cidade = ""
    pais = ""

    if busca:
        resultados = buscar_cidades(busca)

        if resultados:
            opcoes = [r["nome"] for r in resultados]
            escolha = st.selectbox("Selecione a cidade", opcoes)

            for r in resultados:
                if r["nome"] == escolha:
                    coordenada_escolhida = r
                    cidade = r["nome"]
                    break

    # PREVIEW
    if coordenada_escolhida:
        st.map(pd.DataFrame({
            "lat":[coordenada_escolhida["lat"]],
            "lon":[coordenada_escolhida["lon"]]
        }))

    col1, col2 = st.columns(2)

    with col1:
        data = st.date_input("Data", value=date.today())
        dias = st.number_input("Dias",0)

    with col2:
        km_motorhome = st.number_input("KM Motorhome",0.0)
        consumo_motorhome = st.number_input("Consumo MH",0.1)
        preco_diesel = st.number_input("Preço Diesel",0.0)

        km_moto = st.number_input("KM Moto",0.0)
        consumo_moto = st.number_input("Consumo Moto",0.1)
        preco_gasolina = st.number_input("Preço Gasolina",0.0)

    pedagio = st.number_input("Pedágio",0.0)
    ferry = st.number_input("Ferry",0.0)
    bus = st.number_input("Ônibus",0.0)
    aviao = st.number_input("Avião",0.0)

    if st.button("💾 Salvar trecho"):

        if not coordenada_escolhida:
            st.error("Selecione uma cidade válida")
        else:

            lat = coordenada_escolhida["lat"]
            lon = coordenada_escolhida["lon"]

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
            st.success("Trecho salvo!")

# -------------------------
# HISTÓRICO
# -------------------------
elif menu == "Histórico da viagem":

    st.title("📜 Histórico")

    if not dados:
        st.info("Sem dados")
    else:
        df = garantir_colunas(pd.DataFrame(dados))
        df["data"] = pd.to_datetime(df["data"])
        df = df.sort_values("data")

        st.dataframe(df, use_container_width=True)

# -------------------------
# MAPA
# -------------------------
elif menu == "Mapa da viagem":

    st.title("🗺 Mapa")

    if not dados:
        st.info("Sem dados")
    else:
        df = garantir_colunas(pd.DataFrame(dados))
        df = df.dropna(subset=["lat","lon"])

        if len(df) > 0:

            df["data"] = pd.to_datetime(df["data"])
            df = df.sort_values("data")

            coords = df[["lon","lat"]].values.tolist()

            layer_line = pdk.Layer(
                "PathLayer",
                data=[{"path": coords}],
                get_path="path",
                width_min_pixels=4,
            )

            layer_points = pdk.Layer(
                "ScatterplotLayer",
                data=df,
                get_position='[lon, lat]',
                get_radius=50000,
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
                tooltip={"text": "{cidade}"}
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

    st.title("Backup")

    st.download_button("Baixar JSON", json.dumps(dados), "backup.json")

    if dados:
        df = pd.DataFrame(dados)
        st.download_button("Baixar CSV", df.to_csv(index=False), "dados.csv")

# -------------------------
# CONFIG
# -------------------------
elif menu == "Configurações":

    if st.button("Apagar dados"):
        salvar([])
        st.success("Dados apagados")