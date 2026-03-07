from dataclasses import dataclass

# =========================
# CLASSE VEÍCULO
# =========================

@dataclass
class Veiculo:
    nome: str
    consumo_km_por_litro: float
    km_total: float = 0
    litros_total: float = 0
    gasto_combustivel_total: float = 0
    pedagio_total: float = 0

    def adicionar_trecho(self, km_rodado, preco_combustivel, pedagio=0):
        litros_gastos = 0
        gasto_combustivel = 0

        if km_rodado > 0:
            litros_gastos = km_rodado / self.consumo_km_por_litro
            gasto_combustivel = litros_gastos * preco_combustivel

            self.km_total += km_rodado
            self.litros_total += litros_gastos
            self.gasto_combustivel_total += gasto_combustivel

        self.pedagio_total += pedagio

        return litros_gastos, gasto_combustivel


# =========================
# CONSUMO FIXO DEFINIDO
# =========================

motorhome = Veiculo(nome="Motorhome", consumo_km_por_litro=5)   # FIXO
moto = Veiculo(nome="Moto", consumo_km_por_litro=25)          # FIXO

# =========================
# EXEMPLO DE TRECHO
# =========================

data = "05/07/25"
origem = "Playa El Agua"
destino = "Juan Griego"

# ----- MOTORHOME -----
km_mh = 22
preco_diesel = 2.85
pedagio_mh = 0

litros_mh, gasto_mh = motorhome.adicionar_trecho(
    km_rodado=km_mh,
    preco_combustivel=preco_diesel,
    pedagio=pedagio_mh
)

# ----- MOTO -----
km_moto = 0
preco_gasolina = 2.85
pedagio_moto = 0

litros_moto, gasto_moto = moto.adicionar_trecho(
    km_rodado=km_moto,
    preco_combustivel=preco_gasolina,
    pedagio=pedagio_moto
)

# =========================
# RELATÓRIO
# =========================

print(f"\n📆 {data}")
print(f"🛣 {origem} → {destino}")

print("\n🚍 MOTORHOME")
print(f"KM trecho: {km_mh}")
print(f"Litros trecho: {litros_mh:.2f}")
print(f"Gasto trecho: R$ {gasto_mh:.2f}")
print(f"KM total: {motorhome.km_total:.2f}")
print(f"Litros total: {motorhome.litros_total:.2f}")
print(f"Gasto combustível total: R$ {motorhome.gasto_combustivel_total:.2f}")
print(f"Pedágio total: R$ {motorhome.pedagio_total:.2f}")

print("\n🛵 MOTO")
print(f"KM trecho: {km_moto}")
print(f"Litros trecho: {litros_moto:.2f}")
print(f"Gasto trecho: R$ {gasto_moto:.2f}")
print(f"KM total: {moto.km_total:.2f}")
print(f"Litros total: {moto.litros_total:.2f}")
print(f"Gasto combustível total: R$ {moto.gasto_combustivel_total:.2f}")
print(f"Pedágio total: R$ {moto.pedagio_total:.2f}")

total_geral = (
    motorhome.gasto_combustivel_total +
    motorhome.pedagio_total +
    moto.gasto_combustivel_total +
    moto.pedagio_total
)

print(f"\n💰 TOTAL GERAL: R$ {total_geral:.2f}")