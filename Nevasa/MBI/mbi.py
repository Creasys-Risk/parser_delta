# %%
from datetime import datetime
import os
import re
from PyPDF2 import PdfReader
import pandas as pd
# %%
main_folder = os.getcwd()
process_date_raw = datetime.now().date()
process_date = process_date_raw.strftime("%Y%m%d")

folder = f"{main_folder}/{process_date}/"
files = [f for f in os.listdir(folder) if '.pdf' in f]

results = []
for file in files: 
    filename,_ = file.split(".pdf")
    reader = PdfReader(folder+file)

    text = ''

    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text += page.extract_text()

    # with open(f"{main_folder}/{filename}.txt", "w", encoding="utf-8") as f:
    #     f.write(text)

    data = text.split("Detalle Operaciones Vigentes Simultáneas")

    del data[0]

    data_operations: list[str] = []
    for aux in data:
        if "Total" in aux:
            aux,_ = aux.split("Total", maxsplit=1)
        if "Av. Presidente Riesco 5711" in aux:
            aux,_ = aux.split("Av. Presidente Riesco 5711", maxsplit=1)
        rows = aux.split("\n")
        rows = [r for r in rows if r != '']

        insert_row = ""
        for row in rows:
            if re.search(r"[a-zA-Z]", row[0]) and 'Venta' not in row:
                if insert_row == "":
                    insert_row = row
                    continue
                data_operations.append(insert_row)
                insert_row = row
            else:
                insert_row += f" {row}"
        
        data_operations.append(insert_row)
    
    for row in data_operations:
        data = row.split(" ")
        nemo = []

        for aux in data:
            if re.search(r"[a-zA-Z]", aux):
                nemo.append(aux)
            else:
                break
        
        data = data[len(nemo):]
        nemotecnico = " ".join(nemo)

        if '-' in data[-1]:
            day_pago, month_pago, year_pago, _ = data[-1].split("-")
            fecha_ingreso = data[-2].replace("Plazo", "")
        else:
            day_pago, month_pago, year_pago = data[-2].split("-")
            year_pago = year_pago.replace("+", "")
            fecha_ingreso = data[-3].replace("Plazo", "")

        fecha_pago = datetime(int(year_pago), int(month_pago), int(day_pago)).date()
        fecha_ingreso = datetime.strptime(fecha_ingreso, "%d-%m-%Y").date()

        if fecha_ingreso != process_date_raw:
            continue

        precio = float(data[2].replace(".", "").replace(",", "."))
        cantidad = float(data[9].replace("%", "").replace(".", "").replace(",", "."))
        monto = float(data[4].replace(".", "").replace(",", "."))
        cantidad_factura = float(data[0].replace(".", "").replace(",", "."))
        precio_factura = float(data[3].replace(".", "").replace(",", "."))
        nemotecnico = f"SMT_{fecha_pago.strftime('%d%m%Y')}_{fecha_ingreso.strftime('%d%m%Y')}_{precio}_{nemotecnico.replace(' ', '_')}"

        if cantidad == 0:
            cantidad = monto * 1+(precio/100)

        else:
            cantidad = cantidad
            
        results.append({
            "nombre_fondo": "FONDO DE INVERSION NEVASA AHORRO",
            "fecha_pago":fecha_ingreso,
            "fecha_ingreso":fecha_ingreso,
            "precio":precio,
            "cantidad":cantidad,
            "monto":monto,
            "comision": 0,
            "nemotecnico":nemotecnico,
            "compra/venta/vencimiento": "COMPRA",
            "tipo_operacion": "SIMULTANEA",
            "precio_factura": precio_factura,
            "cantidad_factura": cantidad_factura
        })

df = pd.DataFrame(results)
df.to_excel(f"{folder}{process_date}_informe_operaciones_mbi.xlsx", index=False, engine="openpyxl")
# %%
