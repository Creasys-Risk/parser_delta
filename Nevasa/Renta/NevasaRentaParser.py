# %%

import os
import pandas as pd
from PyPDF2 import PdfReader
from datetime import datetime
# %%
def nevasa_renta_parser(process_date: str, main_folder: str):
    try:
        folder = f"{main_folder}/{process_date}/"
        files = [f for f in os.listdir(folder) if '.pdf' in f]

        result = []

        for file in files: 
            output_file = file.replace('.pdf', '.txt')
            reader = PdfReader(folder+file)

            text = ''

            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text()

            with open(folder+output_file, 'w', encoding='utf-8') as txt_file:
                txt_file.write(text)

            _, data = text.split('Condición de liquidación:  ')
            liquidacion, data = data.split('\n', maxsplit=1)
            _, data = text.split('N° FOLIO')
            _, data = data.split('\n', maxsplit=1)
            fecha_pago, data = data.split('\n', maxsplit=1)
            _, data = data.split('\n', maxsplit=1)
            data_table, data = data.split('\n', maxsplit=1)
            _, data = data.split('SALDO A FAVOR (EN CONTRA)')
            _, comision, _ = data.split('\n', maxsplit=2)

            data_table = list(data_table.split(' '))
            documento = data_table[:-4]
            data_table = data_table[len(documento):]
            tipo_renta = 'FIJA' if len(documento) == 1 else 'VARIABLE'
            documento = documento[0]
            precio, cantidad, compra, venta = data_table
            compra = int(compra.replace('.', ''))
            venta = int(venta.replace('.', ''))
            monto = compra + venta

            result.append({
                "tipo_renta": tipo_renta,
                "liquidacion": liquidacion,
                "fecha": datetime.strptime(fecha_pago, "%d/%m/%Y").date(),
                "nemotecnico": documento,
                "precio": float(precio.replace('.', '').replace(',', '.')),
                "cantidad": int(cantidad.replace('.', '')),
                "monto": monto,
                "tipo_instrumento": "COMPRA" if compra != 0 else "VENTA",
                "comision": int(comision.replace('.', ''))
            })

        df = pd.DataFrame(result)

        df.to_excel(f"{folder}{process_date}_nevasa_renta_results.xlsx", index=False, engine="openpyxl")
    except Exception as err:
        print(f"Error en Parser de Rentas Nevasa: {err}")

if __name__ == "__main__":
    process_date = datetime.today().strftime("%Y%m%d")
    main_folder = os.getcwd()

    nevasa_renta_parser(process_date, main_folder)