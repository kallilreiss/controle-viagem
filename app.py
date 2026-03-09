import streamlit as st
import pandas as pd
from datetime import date
import os

st.set_page_config(page_title="Controle de Viagem", layout="wide")

ARQUIVO = "dados_viagem.csv"

# Criar arquivo se não existir
if not os.path.exists(ARQUIVO):
    df = pd.DataFrame(columns=["data","cidade","categoria","descricao","valor","km"])
    df.to_csv(ARQUIVO,index=False)

df = pd.read_csv(ARQUIVO)

# MENU LATERAL
menu = st.sidebar.selectbox(
    "Menu",
    [
        "Dashboard",
        "Registrar gasto",
        "Estatísticas",
        "Diário da viagem",
        "Planejamento de rota",
        "Configurações"
    ]
)

# =========================
# DASHBOARD
# =========================

if menu == "Dashboard":

    st.title("🚐 Dashboard da Viagem")

    total_gasto = df["valor"].sum()

    total_km = df["km"].sum()

    custo_km = 0
    if total_km > 0:
        custo_km = total_gasto / total_km

    col1, col2, col3 = st.columns(3)

    col1.metric("Total gasto", f"R$ {total_gasto:.2f}")
    col2.metric("KM rodados", f"{total_km} km")
    col3.metric("Custo por KM", f"R$ {custo_km:.2f}")

    st.subheader("Últimos registros")
    st.dataframe(df.tail(10))


# =========================
# REGISTRAR GASTO
# =========================

elif menu == "Registrar gasto":

    st.title("Registrar gasto")

    data = st.date_input("Data", date.today())
    cidade = st.text_input("Cidade")

    categoria = st.selectbox(
        "Categoria",
        ["Combustível","Alimentação","Hospedagem","Manutenção","Passeio","Outros"]
    )

    descricao = st.text_input("Descrição")

    valor = st.number_input("Valor", min_value=0.0)

    km = st.number_input("KM rodados", min_value=0)

    if st.button("Salvar gasto"):

        novo = pd.DataFrame({
            "data":[data],
            "cidade":[cidade],
            "categoria":[categoria],
            "descricao":[descricao],
            "valor":[valor],
            "km":[km]
        })

        df2 = pd.concat([df,novo])
        df2.to_csv(ARQUIVO,index=False)

        st.success("Gasto registrado!")


# =========================
# ESTATÍSTICAS
# =========================

elif menu == "Estatísticas":

    st.title("Estatísticas da viagem")

    if len(df) == 0:
        st.warning("Nenhum gasto registrado ainda.")
    else:

        gasto_categoria = df.groupby("categoria")["valor"].sum()

        st.subheader("Gasto por categoria")
        st.bar_chart(gasto_categoria)

        gasto_cidade = df.groupby("cidade")["valor"].sum()

        st.subheader("Gasto por cidade")
        st.bar_chart(gasto_cidade)


# =========================
# DIÁRIO DA VIAGEM
# =========================

elif menu == "Diário da viagem":

    st.title("Diário da viagem")

    cidade = st.text_input("Cidade visitada")
    nota = st.text_area("O que aconteceu hoje?")

    if st.button("Salvar no diário"):

        with open("diario.txt","a") as f:
            f.write(f"{date.today()} - {cidade} \n {nota}\n\n")

        st.success("Diário salvo!")

    if os.path.exists("diario.txt"):
        st.subheader("Registros anteriores")

        with open("diario.txt","r") as f:
            st.text(f.read())


# =========================
# PLANEJAMENTO DE ROTA
# =========================

elif menu == "Planejamento de rota":

    st.title("Planejamento de rota")

    distancia = st.number_input("Distância da viagem (km)",min_value=0)

    consumo = st.number_input("Consumo do veículo (km/l)",min_value=1)

    preco = st.number_input("Preço da gasolina",min_value=0.0)

    if st.button("Calcular custo"):

        litros = distancia / consumo

        custo = litros * preco

        st.success(f"Litros necessários: {litros:.1f}")

        st.success(f"Custo estimado: R$ {custo:.2f}")


# =========================
# CONFIGURAÇÕES
# =========================

elif menu == "Configurações":

    st.title("Configurações da viagem")

    st.write("Aqui você pode limpar os dados.")

    if st.button("Apagar todos os dados"):

        df = pd.DataFrame(columns=["data","cidade","categoria","descricao","valor","km"])
        df.to_csv(ARQUIVO,index=False)

        st.success("Dados apagados!")