# %%
import os
import pandas as pd
from PyPDF2 import PdfReader
from datetime import datetime
# %%
def nevasa_compra_simultanea_parser(process_date: str, main_folder: str):
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

            _, data = text.split('RUT:\n')
            instrumento, data = data.split('Cuenta:\n')
            _, data = data.split('$ ', maxsplit=1)
            monto_contado, data = data.split("Precio Contado: ")
            _, data = data.split('$ ', maxsplit=1)
            monto_compromiso, data = data.split('\n', maxsplit=1)
            _, data = data.split('Plazo:', maxsplit=1)
            diferencia_precio, data = data.split('\n', maxsplit=1)
            _, data = data.split('Fecha Vencimiento:')
            fecha_movimiento, fecha_vencimiento, data = data.split('\n', maxsplit=2)

            result.append({
                'instrumento': instrumento,
                'monto_contado': int(monto_contado.replace('.', '')),
                'monto_compromiso': int(monto_compromiso.replace('.', '')),
                'diferencia_precio': float(diferencia_precio.replace('%', '').replace('.', '').replace(',', '.')),
                'fecha_movimiento': datetime.strptime(fecha_movimiento, "%d/%m/%Y").date(),
                'fecha_vencimiento': datetime.strptime(fecha_vencimiento, "%d/%m/%Y").date(),
            })

        df = pd.DataFrame(result)

        df.to_excel(f"{folder}{process_date}_nevasa_compras_simultaneas_results.xlsx", index=False, engine="openpyxl")

    except Exception as err:
        print(f"Error en Parser de Compra de Simultaneas Nevasa: {err}")

if __name__ == "__main__":
    process_date = datetime.today().strftime("%Y%m%d")
    main_folder = os.getcwd()

    nevasa_compra_simultanea_parser(process_date, main_folder)