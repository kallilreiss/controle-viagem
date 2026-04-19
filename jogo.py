import streamlit as st
import random
import time
import base64

st.set_page_config(page_title="Fique Rico ou Quebre", layout="centered")

# ---------- FUNDO / ESTILO ----------
st.markdown("""
<style>

/* Fundo geral */
.stApp {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    color: white;
}

/* Caixa principal */
.block-container {
    background: rgba(255, 255, 255, 0.03);
    padding: 2rem;
    border-radius: 15px;
    backdrop-filter: blur(10px);
}

/* Títulos */
h1, h2, h3 {
    color: #38bdf8;
}

/* Botões */
.stButton>button {
    background: linear-gradient(90deg, #22c55e, #4ade80);
    color: white;
    border-radius: 10px;
    border: none;
    padding: 10px;
    transition: 0.3s;
}

.stButton>button:hover {
    transform: scale(1.05);
}

/* Inputs */
.stTextInput input, .stNumberInput input {
    background-color: #0f172a;
    color: white;
    border-radius: 8px;
}

/* Slider */
.stSlider div {
    color: #22c55e;
}

/* Barra de progresso */
.stProgress > div > div {
    background-color: #22c55e;
}

/* Detalhe matemático leve */
.stApp::before {
    content: "%   +10%   +25%   juros   gráfico   %   +5%";
    position: fixed;
    top: 20%;
    left: 10%;
    font-size: 40px;
    color: rgba(255,255,255,0.03);
    transform: rotate(-20deg);
}

</style>
""", unsafe_allow_html=True)