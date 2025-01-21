# %%
import os
import re
import pandas as pd
from PyPDF2 import PdfReader
from datetime import datetime
# %%
main_folder = os.getcwd()
process_date_raw = datetime.today().date()
process_date = process_date_raw.strftime("%Y%m%d")

folder = f"{main_folder}/{process_date}/"
process_date_simultaneas = datetime.strptime(process_date, "%Y%m%d").strftime("%d-%m-%Y")
process_date_renta = datetime.strptime(process_date, "%Y%m%d").strftime("%d/%m/%Y")
files = [f for f in os.listdir(folder) if '.pdf' in f]

result = []

results = []
for file in files: 
    filename,_ = file.split(".pdf")
    reader = PdfReader(folder+file)

    text = ''

    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text += page.extract_text()

    with open(f"{main_folder}/{filename}.txt", "w", encoding="utf-8") as f:
        f.write(text)

    _, data = text.split("Movimientos de Títulos")
    data = data.split("\n")

    for row in data:
        if not re.search(r"\d", row) or "/" not in row:
            continue
        aux = row.split(" ")
        fecha = datetime.strptime(aux[0], "%d/%m/%Y").date()

        if fecha != process_date_raw:
            continue

        for i,d in enumerate(aux[2:]):
            if re.search(r"\d", d):
                operacion = " ".join(aux[2:i+1])
                nemotecnico = aux[i+1]
                aux = aux[i+2:]
                break

        if any(test_str in operacion for test_str in ["Aporte", "Compra", "N.Credito Egreso"]):
            tipo_operacion = "COMPRA"
        elif any(test_str in operacion for test_str in ["Retiro", "Venta", "N.Credito Ingreso"]):
            tipo_operacion = "VENTA"
        else:
            raise Exception(f"Tipo de operación invalida: {operacion}")

        cantidad = float(aux[0].replace(".", "").replace(",", "."))
        precio = float(aux[1].replace(".", "").replace(",", "."))
        monto = float(aux[2].replace(".", "").replace(",", "."))

        results.append({
            "nombre_fondo": "FONDO DE INVERSION NEVASA DEUDA PRIVADA",
            "fecha_pago":fecha,
            "fecha_ingreso":fecha,
            "precio":precio,
            "cantidad":cantidad,
            "monto":monto,
            "comision": 0,
            "nemotecnico":nemotecnico,
            "compra/venta": tipo_operacion
        })

df = pd.DataFrame(results)
agg_functions = {
    'nombre_fondo': 'first',
    'fecha_pago': 'first',
    'fecha_ingreso': 'first',
    'precio': 'first',
    'cantidad': 'sum', 
    'monto': 'sum',
    'comision': 'first',
    'nemotecnico': 'first',
    'compra/venta': 'first'
}
df = df.groupby(["nemotecnico", "precio", "compra/venta"]).aggregate(agg_functions)
df.to_excel(f"{folder}{process_date}_informe_deuda_privada.xlsx", index=False, engine="openpyxl")