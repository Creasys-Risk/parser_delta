# %%
import os
import pandas as pd
from PyPDF2 import PdfReader
from datetime import datetime
# %%
def nevasa_venta_simultanea_parser(process_date: str, main_folder: str):
    try:
        folder = f"{main_folder}/{process_date}/"
        files = [f for f in os.listdir(folder) if '.pdf' in f]

        result = []

        for file in files: 
            try:
                reader = PdfReader(folder+file)

                text = ''

                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    text += page.extract_text()

                _, data = text.split('Fecha Pago: ')
                fecha, data = data.split('\n', maxsplit=1)
                fecha = datetime.strptime(fecha, "%d/%m/%Y").date()
                _, data = data.split('COMPRA VENTA\n')
                data, _ = data.split('SUB TOTAL(1)')
                data_rows = data.split('\n')[:-1]

                for row in data_rows:
                    row = row.replace('VENTA ', '')
                    row = row.replace('AC ', '')
                    row = row.replace('OD ', '')
                    row = row.replace('CF ', '')
                    row = row.replace('COR ', '')
                    row = row.replace('Cust ', '')
                    row = row.split(' ')
                    monto = int(row[len(row)-1].replace('.', ''))
                    cantidad = int(row[len(row)-2].replace('.', ''))
                    row = row[:-5]
                    row = row[1:]
                    precio = float(row.pop(len(row)-1).replace('%', '').replace(',', '.'))
                    nemotecnico = ' '.join(row)
                    
                    result.append({
                        "fecha": fecha,
                        "nemotecnico": nemotecnico,
                        "precio": precio,
                        "cantidad": cantidad,
                        "monto": monto,
                    })
            except Exception as err:
                print(f"Error en Parser de Venta de Simultaneas Nevasa, archivo {file}: {err}")
                continue

        df = pd.DataFrame(result)

        df.to_excel(f"{folder}{process_date}_nevasa_ventas_simultaneas_results.xlsx", index=False, engine="openpyxl")

    except Exception as err:
        print(f"Error en Parser de Venta de Simultaneas Nevasa: {err}")

if __name__ == "__main__":
    process_date = datetime.today().strftime("%Y%m%d")
    main_folder = os.getcwd()

    nevasa_venta_simultanea_parser(process_date, main_folder)