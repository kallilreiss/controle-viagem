import streamlit as st
import random
import time
import base64

st.set_page_config(page_title="Fique Rico ou Quebre", layout="centered")

# ---------- ESTILO / INTERFACE ----------
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

/* Detalhe matemático sutil */
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

# ---------- FUNÇÃO PARA TOCAR SOM ----------
def tocar_som(file):
    try:
        with open(file, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""
            <audio autoplay>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
            st.markdown(md, unsafe_allow_html=True)
    except:
        pass

# ---------- ESTADO ----------
if "tela" not in st.session_state:
    st.session_state.tela = "menu"

if "ranking" not in st.session_state:
    st.session_state.ranking = []

# ---------- PERGUNTAS ----------
def gerar_pergunta(dificuldade):
    valores = {"Fácil":[100,200], "Médio":[200,500,1000], "Difícil":[500,1000,2000]}
    taxas = {"Fácil":[10,20], "Médio":[5,10,15], "Difícil":[10,15,20]}
    tempos = {"Fácil":[1,2], "Médio":[2,3], "Difícil":[2,3,4]}

    tipo = random.choice(["porcentagem","juros_simples","juros_compostos"])

    v = random.choice(valores[dificuldade])
    t = random.choice(taxas[dificuldade])
    tempo = random.choice(tempos[dificuldade])

    if tipo == "porcentagem":
        res = v*(1-t/100)
        return f"R${v} com {t}% de desconto → valor final?", round(res,2), f"Final = {res}"

    if tipo == "juros_simples":
        juros = v*(t/100)*tempo
        res = v+juros
        return f"R${v} a {t}% por {tempo} meses (simples)", round(res,2), f"Total = {res}"

    res = v*((1+t/100)**tempo)
    return f"R${v} a {t}% por {tempo} meses (composto)", round(res,2), f"Total = {round(res,2)}"

# ---------- MENU ----------
if st.session_state.tela == "menu":
    st.title("💰 Fique Rico ou Quebre")

    nome = st.text_input("Nome")
    dificuldade = st.selectbox("Dificuldade", ["Fácil","Médio","Difícil"])
    tempo = st.slider("Tempo por rodada",5,30,15)

    if st.button("🚀 Jogar"):
        st.session_state.nome = nome or "Jogador"
        st.session_state.dificuldade = dificuldade
        st.session_state.tempo = tempo
        st.session_state.dinheiro = 1000
        st.session_state.rodada = 1
        st.session_state.inicio = time.time()
        st.session_state.tela = "jogo"
        st.rerun()

# ---------- JOGO ----------
elif st.session_state.tela == "jogo":

    st.markdown("## 💰 Fique Rico ou Quebre")
    st.markdown(f"### 💵 R${round(st.session_state.dinheiro,2)} | Rodada {st.session_state.rodada}/10")

    restante = st.session_state.tempo - int(time.time() - st.session_state.inicio)

    if restante <= 0:
        st.error("⏱️ Tempo acabou!")
        tocar_som("erro.mp3")
        st.session_state.dinheiro -= 150
        st.session_state.rodada += 1
        st.session_state.inicio = time.time()
        st.rerun()

    st.progress(restante/st.session_state.tempo)
    st.write(f"⏳ {restante}s")

    if "p" not in st.session_state:
        p,r,e = gerar_pergunta(st.session_state.dificuldade)
        st.session_state.p = p
        st.session_state.r = r
        st.session_state.e = e

    st.subheader("📊 Resolva:")
    st.write(st.session_state.p)

    resp = st.number_input("Resposta:", step=0.1)

    if st.button("Confirmar resposta"):
        if abs(resp - st.session_state.r) < 0.1:
            st.success("✅ Acertou! +200")
            tocar_som("acerto.mp3")
            st.balloons()
            st.session_state.dinheiro += 200
        else:
            st.error(f"❌ Errado! Correto: {st.session_state.r}")
            tocar_som("erro.mp3")
            st.session_state.dinheiro -= 100

        st.info(st.session_state.e)
        del st.session_state.p

    acao = st.radio("Escolha:", ["Investir","Guardar","Arriscar"])

    if st.button("Confirmar ação"):
        if acao == "Investir":
            st.session_state.dinheiro *= 1.1
        elif acao == "Arriscar":
            st.session_state.dinheiro *= random.choice([0.7,1.3])

        st.session_state.rodada += 1
        st.session_state.inicio = time.time()

        if st.session_state.rodada > 10:
            st.session_state.tela = "final"

        st.rerun()

# ---------- FINAL ----------
else:
    d = round(st.session_state.dinheiro,2)

    st.title("🏁 Resultado")

    if d>2000:
        st.success(f"🤑 Rico! R${d}")
        st.balloons()
    elif d>1000:
        st.info(f"🙂 Estável R${d}")
    else:
        st.error(f"😬 Endividado R${d}")

    st.session_state.ranking.append((st.session_state.nome,d))
    st.session_state.ranking = sorted(st.session_state.ranking, key=lambda x:x[1], reverse=True)[:5]

    st.subheader("🏆 Ranking")
    for i,(n,v) in enumerate(st.session_state.ranking,1):
        st.write(f"{i}. {n} - R${v}")

    if st.button("🔁 Jogar novamente"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()