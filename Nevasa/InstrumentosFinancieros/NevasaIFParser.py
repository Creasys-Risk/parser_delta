# %%
import os
import pandas as pd
from PyPDF2 import PdfReader
from datetime import datetime
# %%
def nevasa_if_parser(process_date: str, main_folder: str):
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

            _, data = text.split('AGENTE: ')
            aux, data = data.split('\n', maxsplit=1)

            aux = list(aux.split(' '))
            fecha = aux[-2]
            fecha = datetime.strptime(fecha, "%d-%m-%Y").date()

            _, data = data.split('HEMOS ')

            compra_venta, data = data.split(' ', maxsplit=1)
            compra_venta = 'COMPRA' if compra_venta == 'RECIBIDO' else 'VENTA'

            _, data = data.split('EMISOR')
            _, data = data.split('\n', maxsplit=1)
            table, data = data.split('\n', maxsplit=1)

            table = list(table.split(' '))

            instrumento = table[0].replace('*', '')
            valor_nominal = float(table[4].replace('.', '').replace(',', '.'))
            moneda_nominal = table[5]
            precio = float(table[6].replace(',', '.'))
            valor_final = int(table[7].replace('.', ''))

            result.append({
                "fecha": fecha,
                "tipo_instrumento": compra_venta,
                "nemotecnico": instrumento,
                "valor_nominal": valor_nominal,
                "moneda_nominal": moneda_nominal,
                "precio": precio,
                "valor_final": valor_final,
            })

        df = pd.DataFrame(result)

        df.to_excel(f"{folder}{process_date}_nevasa_instrumentos_financieros_results.xlsx", index=False, engine="openpyxl")

    except Exception as err:
        print(f"Error en Parser de Instrumentos Financieros Nevasa: {err}")

if __name__ == "__main__":
    process_date = datetime.today().strftime("%Y%m%d")
    main_folder = os.getcwd()

    nevasa_if_parser(process_date, main_folder)