import random

# ================= CONFIGURAÇÕES =================
DIAS = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
HORARIOS_POR_DIA = 6

TURMAS = [
    "1A", "1B", "1C", "1D",
    "2A", "2B", "2C", "2D",
    "3A", "3B", "3C", "3D"
]

# ================= ENTRADA DE DADOS =================
materias = {}

qtd_materias = int(input("Quantas matérias existem? "))

for i in range(qtd_materias):
    nome = input(f"\nNome da matéria {i+1}: ").upper()
    professor = input(f"Professor de {nome}: ")
    aulas = int(input(f"Quantas aulas semanais de {nome}? "))

    materias[nome] = {
        "professor": professor,
        "aulas": aulas
    }

# ================= FUNÇÃO PARA GERAR CRONOGRAMA =================
def gerar_cronograma(materias):
    cronograma = {dia: [] for dia in DIAS}

    lista_aulas = []

    for materia, dados in materias.items():
        for _ in range(dados["aulas"]):
            lista_aulas.append(f"{materia} ({dados['professor']})")

    total_horarios = len(DIAS) * HORARIOS_POR_DIA

    while len(lista_aulas) < total_horarios:
        lista_aulas.append("Livre")

    random.shuffle(lista_aulas)

    i = 0
    for dia in DIAS:
        for _ in range(HORARIOS_POR_DIA):
            cronograma[dia].append(lista_aulas[i])
            i += 1

    return cronograma

# ================= GERAÇÃO PARA TODAS AS TURMAS =================
cronogramas = {}

for turma in TURMAS:
    cronogramas[turma] = gerar_cronograma(materias)

# ================= EXIBIÇÃO =================
for turma, cronograma in cronogramas.items():
    print(f"\n📘 CRONOGRAMA – TURMA {turma}")
    print("-" * 40)

    for dia in DIAS:
        print(f"\n{dia}:")
        for i, aula in enumerate(cronograma[dia], 1):
            print(f"  {i}º horário: {aula}")
