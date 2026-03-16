import streamlit as st
import json
import os
import pandas as pd
from datetime import date

st.set_page_config(page_title="Controle de Viagem Motorhome", layout="wide")

ARQUIVO = "dados_viagem.json"

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
        "km_motorhome","litros_motorhome","gasto_motorhome",
        "km_moto","litros_moto","gasto_moto",
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

        total_pedagio = df["pedagio"].sum()
        total_ferry = df["ferry"].sum()
        total_bus = df["bus"].sum()
        total_aviao = df["aviao"].sum()

        total_viagem = (
            total_diesel +
            total_gasolina +
            total_pedagio +
            total_ferry +
            total_bus +
            total_aviao
        )

        cidades = len(set(df["cidade"]))
        paises = len(set(df["pais"]))

        dias_total = df["dias"].sum()

        km_total = total_km_motorhome + total_km_moto

        if km_total > 0:
            custo_km = total_viagem / km_total
        else:
            custo_km = 0

        col1,col2,col3,col4 = st.columns(4)

        col1.metric("🚐 KM Motorhome", round(total_km_motorhome,2))
        col2.metric("🛵 KM Moto", round(total_km_moto,2))
        col3.metric("🏙 Cidades", cidades)
        col4.metric("🌎 Países", paises)

        col1,col2,col3,col4 = st.columns(4)

        col1.metric("📅 Dias de viagem", dias_total)
        col2.metric("💰 Diesel total", f"R$ {round(total_diesel,2)}")
        col3.metric("💰 Gasolina total", f"R$ {round(total_gasolina,2)}")
        col4.metric("💰 Total viagem", f"R$ {round(total_viagem,2)}")

        st.metric("💰 Custo por KM", f"R$ {round(custo_km,2)}")

        st.subheader("🧠 Planejar próxima viagem")

        km_planejado = st.number_input("KM que pretende rodar")

        if km_total > 0:

            estimativa = km_planejado * custo_km

            st.metric("💰 Custo estimado", f"R$ {round(estimativa,2)}")

# -------------------------
# REGISTRAR TRECHO
# -------------------------

elif menu == "Registrar trecho":

    st.title("Registrar trecho")

    cidade = st.text_input("Cidade")
    pais = st.text_input("País")

    data = st.date_input("Data",value=date.today())

    dias = st.number_input("Dias no local",0)

    lat = st.number_input("Latitude",value=0.0)
    lon = st.number_input("Longitude",value=0.0)

    st.subheader("Motorhome")

    km_motorhome = st.number_input("KM rodados MH",0.0)
    consumo_motorhome = st.number_input("Consumo MH (km/l)",0.1)
    preco_diesel = st.number_input("Preço diesel",0.0)
    pedagio = st.number_input("Pedágio",0.0)

    st.subheader("Moto")

    km_moto = st.number_input("KM moto",0.0)
    consumo_moto = st.number_input("Consumo moto (km/l)",0.1)
    preco_gasolina = st.number_input("Preço gasolina",0.0)

    st.subheader("Transportes")

    ferry = st.number_input("Ferry",0.0)
    bus = st.number_input("Ônibus",0.0)
    aviao = st.number_input("Avião",0.0)

    if st.button("Salvar trecho"):

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
            "litros_motorhome":litros_motorhome,
            "gasto_motorhome":gasto_motorhome,
            "pedagio":pedagio,

            "km_moto":km_moto,
            "litros_moto":litros_moto,
            "gasto_moto":gasto_moto,

            "ferry":ferry,
            "bus":bus,
            "aviao":aviao
        }

        dados.append(trecho)

        salvar(dados)

        st.success("Trecho registrado!")

# -------------------------
# HISTÓRIA
# -------------------------

elif menu == "História da viagem":

    st.title("📖 História da viagem")

    if len(dados) == 0:

        st.info("Nenhum trecho registrado")

    else:

        for t in dados:

            st.markdown(f"""
### 📆 {t.get('data','')}
📍 {t.get('cidade','')} - {t.get('pais','')}

🚐 Motorhome  
{round(t.get('km_motorhome',0),2)} km  
Diesel gasto: R$ {round(t.get('gasto_motorhome',0),2)}

🛵 Moto  
{round(t.get('km_moto',0),2)} km  
Gasolina: R$ {round(t.get('gasto_moto',0),2)}

🚧 Pedágio: R$ {round(t.get('pedagio',0),2)}

⛴ Ferry: R$ {round(t.get('ferry',0),2)}  
🚌 Bus: R$ {round(t.get('bus',0),2)}  
✈️ Avião: R$ {round(t.get('aviao',0),2)}

---
""")

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

        if "lat" in df.columns and "lon" in df.columns:

            mapa = df[(df["lat"] != 0) & (df["lon"] != 0)]

            if len(mapa) > 0:

                st.map(mapa[["lat","lon"]])

            else:

                st.info("Nenhuma coordenada registrada")

# -------------------------
# ESTATÍSTICAS
# -------------------------

elif menu == "Estatísticas":

    st.title("📊 Estatísticas")

    if len(dados) == 0:

        st.info("Nenhum dado")

    else:

        df = pd.DataFrame(dados)

        df = garantir_colunas(df)

        combustivel = {

            "Diesel":df["gasto_motorhome"].sum(),
            "Gasolina":df["gasto_moto"].sum()

        }

        df_g = pd.DataFrame(list(combustivel.items()),columns=["tipo","valor"])

        st.bar_chart(df_g.set_index("tipo"))

# -------------------------
# BACKUP
# -------------------------

elif menu == "Backup da viagem":

    st.title("💾 Backup da viagem")

    if len(dados) == 0:

        st.info("Nenhum dado")

    else:

        backup = json.dumps(dados).encode("utf-8")

        st.download_button(
            "Baixar backup da viagem",
            backup,
            "backup_viagem.json",
            "application/json"
        )

        st.subheader("Restaurar backup")

        arquivo = st.file_uploader("Enviar backup")

        if arquivo is not None:

            dados_restaurados = json.load(arquivo)

            salvar(dados_restaurados)

            st.success("Backup restaurado")

# -------------------------
# CONFIG
# -------------------------

elif menu == "Configurações":

    if st.button("Apagar todos dados"):

        salvar([])

        st.success("Dados apagados")