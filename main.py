# %%
import os
from datetime import datetime
import pandas as pd
from PyPDF2 import PdfReader

process_date = datetime.today().strftime("%Y%m%d")

pass_dict = dict()
with open(f"{process_date}/pass.txt", 'r') as pass_file:
    for line in pass_file:
        key, value = line.split(":")
        pass_dict[key] = value.replace("\n", "")
# %%
folder = os.getcwd()+"/"+process_date+"/"

files = [f for f in os.listdir(folder) if '.pdf' in f]
# %%
result = []

for file in files:
    output_file = file.replace('.pdf', '.txt')
    _, _, pass_key, _ = file.split('_')
    reader = PdfReader(folder+file)
    reader.decrypt(pass_dict[pass_key])

    text = ''

    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text += page.extract_text()

    with open(folder+output_file, 'w') as txt_file:
        txt_file.write(text)

    _, data = text.split("Fecha  ")
    fecha, data = data.split(",", maxsplit=1)
    _, data = data.split("Detalle del Rescate\n")
    _, data = data.split("Fondo :")
    fondo, data = data.split("\n", maxsplit=1)
    _, data = data.split("Número de Cuotas :")
    aux, data = data.split("\n", maxsplit=1)
    numero_cuota, tipo_rescate = aux.split("Tipo de Rescate :")
    _, data = data.split("Valor Cuota :")
    valor_cuota, data = data.split("\n", maxsplit=1)
    _, data = data.split(": Comisión ")
    aux, data= data.split("\n", maxsplit=1)
    comision, monto = aux.split("Monto :")
    _, data = data.split("Forma de Pago :")
    forma_pago, data = data.split("\n", maxsplit=1)
    _, data = data.split("Nombre o Razón Social :")
    nombre, _ = data.split("\n", maxsplit=1)

    moneda, monto = monto.split(" $")

    result.append({
        "fondo": nombre,
        "monto": monto, 
        "moneda": moneda,
        "tipo": "VENTA",
        "concepto": "RESCATE",
        "fecha_operacion": fecha, 
        "fecha_liquidacion": datetime.today().strftime("%d/%m/%Y"),
        "cantidad": numero_cuota, 
        "precio": valor_cuota, 
        "nemotecnico": "CFMPRULCLP",
    })

df = pd.DataFrame(result)

df.to_excel(f"{folder}{process_date}_results.xlsx", index=False, engine="openpyxl")
