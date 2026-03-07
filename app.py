import streamlit as st
import json
import os
from datetime import date

st.title("Controle de Viagem")

ARQUIVO = "dados_viagem.json"

# -------------------------
# CARREGAR DADOS
# -------------------------
def carregar_dados():
    if os.path.exists(ARQUIVO):
        with open(ARQUIVO, "r") as f:
            return json.load(f)
    return []

# -------------------------
# SALVAR DADOS
# -------------------------
def salvar_dados(dados):
    with open(ARQUIVO, "w") as f:
        json.dump(dados, f, indent=4)

dados = carregar_dados()

# -------------------------
# FORMULÁRIO
# -------------------------
st.header("Adicionar Trecho")

cidade = st.text_input("Cidade")
data = st.date_input("Data", value=date.today())
dias = st.number_input("Dias na cidade", min_value=0)

st.subheader("Motorhome")

km_motorhome = st.number_input("KM rodados Motorhome", min_value=0.0)
consumo_motorhome = st.number_input("Consumo Motorhome (km/L)", min_value=0.1)
preco_diesel = st.number_input("Preço do Diesel", min_value=0.0)
pedagio = st.number_input("Pedágio", min_value=0.0)

st.subheader("Moto")

km_moto = st.number_input("KM rodados Moto", min_value=0.0)
consumo_moto = st.number_input("Consumo Moto (km/L)", min_value=0.1)
preco_gasolina = st.number_input("Preço da Gasolina", min_value=0.0)

st.subheader("Outros Transportes")

ferry = st.number_input("Ferry", min_value=0.0)
bus = st.number_input("Ônibus", min_value=0.0)
aviao = st.number_input("Avião", min_value=0.0)
outros = st.number_input("Outros", min_value=0.0)

if st.button("Salvar Trecho"):

    litros_motorhome = km_motorhome / consumo_motorhome if consumo_motorhome > 0 else 0
    gasto_motorhome = litros_motorhome * preco_diesel

    litros_moto = km_moto / consumo_moto if consumo_moto > 0 else 0
    gasto_moto = litros_moto * preco_gasolina

    trecho = {
        "cidade": cidade,
        "data": str(data),
        "dias": dias,

        "km_motorhome": km_motorhome,
        "litros_motorhome": litros_motorhome,
        "gasto_motorhome": gasto_motorhome,
        "pedagio": pedagio,

        "km_moto": km_moto,
        "litros_moto": litros_moto,
        "gasto_moto": gasto_moto,

        "ferry": ferry,
        "bus": bus,
        "aviao": aviao,
        "outros": outros
    }

    dados.append(trecho)
    salvar_dados(dados)

    st.success("Trecho salvo!")

# -------------------------
# RESUMO
# -------------------------
st.header("Resumo da Viagem")

total_km_motorhome = sum(t.get("km_motorhome", 0) for t in dados)
total_litros_motorhome = sum(t.get("litros_motorhome", 0) for t in dados)
total_gasto_motorhome = sum(t.get("gasto_motorhome", 0) for t in dados)
total_pedagio = sum(t.get("pedagio", 0) for t in dados)

total_km_moto = sum(t.get("km_moto", 0) for t in dados)
total_litros_moto = sum(t.get("litros_moto", 0) for t in dados)
total_gasto_moto = sum(t.get("gasto_moto", 0) for t in dados)

total_dias = sum(t.get("dias", 0) for t in dados)

total_outros = sum(
    t.get("ferry", 0) +
    t.get("bus", 0) +
    t.get("aviao", 0) +
    t.get("outros", 0)
    for t in dados
)

total_cidades = len(dados)

st.subheader("Motorhome")

st.metric("KM Motorhome", round(total_km_motorhome, 2))
st.metric("Litros Consumidos", round(total_litros_motorhome, 2))
st.metric("Gasto Diesel", round(total_gasto_motorhome, 2))
st.metric("Pedágio", round(total_pedagio, 2))

st.subheader("Moto")

st.metric("KM Moto", round(total_km_moto, 2))
st.metric("Litros Moto", round(total_litros_moto, 2))
st.metric("Gasto Gasolina", round(total_gasto_moto, 2))

st.subheader("Resumo Geral")

total_viagem = total_gasto_motorhome + total_gasto_moto + total_pedagio + total_outros

st.metric("Total Dias", total_dias)
st.metric("Total Viagem", round(total_viagem, 2))
st.metric("Cidades Visitadas", total_cidades)

# -------------------------
# TABELA
# -------------------------
st.subheader("Trechos Registrados")

st.table(dados)