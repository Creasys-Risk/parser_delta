# %%
import os
import pandas as pd
from PyPDF2 import PdfReader
from datetime import datetime, timedelta
# %%
def informe_completo_parser(process_date: str, main_folder: str):
    try:
        folder = f"{main_folder}/{process_date}/"
        process_date_simultaneas = datetime.strptime(process_date, "%Y%m%d").strftime("%d-%m-%Y")
        process_date_renta = datetime.strptime(process_date, "%Y%m%d").strftime("%d/%m/%Y")
        files = [f for f in os.listdir(folder) if '.pdf' in f]

        result = []

        for file in files: 
            reader = PdfReader(folder+file)

            text = ''

            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text()

            _, data = text.split("Informe Mensual de Cartera\n \n")
            fondo, data = data.split("\n", maxsplit=1)

            while "Detalle Operaciones Vigentes Simultáneas" in data:
                _, data = data.split("Detalle Operaciones Vigentes Simultáneas\n", maxsplit=1)
                if "$\n$\n" in data:
                    table, data = data.split("$\n$\n", maxsplit=1)
                else:
                    table, data = data.split("::\n:\n", maxsplit=1)
                lines = table.split('\n')

                for index, value in enumerate(lines):
                    if process_date_simultaneas in value:
                        row_1 = value.split(" ")
                        row_2 = lines[index+1].split(" ")
                        nemotecnico = row_1[0:-9]
                        nemotecnico = " ".join(nemotecnico)
                        precio = float(row_1[-7].replace(",", "."))
                        fecha_ingreso = datetime.strptime(row_1[-4], "%d-%m-%Y").date()
                        cantidad = int(row_2[4].replace("%", "").replace(".", ""))
                        fecha_pago = datetime.strptime(row_2[2], "%d-%m-%Y").date()
                        monto = int(row_1[-2].replace(".", ""))
                        result.append({
                            "nombre_fondo": fondo,
                            "fecha_pago":fecha_pago,
                            "fecha_ingreso":fecha_ingreso,
                            "precio":precio,
                            "cantidad":cantidad,
                            "monto":monto,
                            "comision": 0,
                            "nemotecnico":nemotecnico,
                            "compra/venta/vencimiento": "COMPRA",
                            "tipo_operacion": "SIMULTANEA"
                        })
            
            if "Detalle Operaciones Vigentes Pactos" in data:
                _, data = data.split("Detalle Operaciones Vigentes Pactos\n")
                row_1, data = data.split("\n", maxsplit=1)
                _, data = data.split("\n", maxsplit=1)
                row_2, data = data.split("\n", maxsplit=1)
                row_1 = row_1.split(" ")
                row_2 = row_2.split(" ")
                plazo = int(row_1[4])
                precio = float(row_1[5].replace(",", "."))
                fecha_ingreso = datetime.strptime(row_1[8], "%d/%m/%Y").date()
                monto = int(row_1[9].replace(".", ""))
                fecha_venta_plazo = datetime.strptime(row_2[2], "%d/%m/%Y").date()
                cantidad = int(row_2[3].replace(".", ""))

                if fecha_ingreso + timedelta(days=plazo) != fecha_venta_plazo:
                    print(f"Fecha de compra más plazo no calzan con la Fecha de venta suministrada por el archivo.")
                    print(f"Fecha de compra: {fecha_ingreso}")
                    print(f"Plazo: {plazo}")
                    print(f"Fecha de venta: {fecha_venta_plazo}")
                
                result.append({
                    "nombre_fondo": fondo,
                    "fecha_pago":fecha_ingreso + timedelta(days=plazo),
                    "fecha_ingreso":fecha_ingreso,
                    "precio":precio,
                    "cantidad":cantidad,
                    "monto":monto,
                    "comision": 0,
                    "nemotecnico":"PACTO",
                    "compra/venta/vencimiento": "COMPRA",
                    "tipo_operacion": "PACTO"
                })

            while "Movimientos de Títulos" in data:
                _, data = data.split("Movimientos de Títulos ", maxsplit=1)
                if "$\n$\n" in data:
                    table, data = data.split("$\n$\n", maxsplit=1)
                else:
                    table = data

                lines = table.split("\n")

                for line in lines:
                    if process_date_renta in line:
                        # Vencimientos
                        if "Liquidacion Venta TP" in line:
                            line = line.replace("Liquidacion Venta TP ", "")
                            row = line.split(" ")
                            fecha = datetime.strptime(row[0], "%d/%m/%Y").date()
                            nemotecnico = row[2:-5]
                            nemotecnico = " ".join(nemotecnico)
                            monto = int(row[-3].replace(".", ""))

                            result.append({
                                "nombre_fondo": fondo,
                                "fecha_pago":fecha,
                                "fecha_ingreso":fecha,
                                "precio":0,
                                "cantidad":monto,
                                "monto":monto,
                                "comision": 0,
                                "nemotecnico":nemotecnico,
                                "compra/venta/vencimiento": "VCTO",
                                "tipo_operacion": "VENCIMIENTO"
                            })
                        # Instrumentos Financieros
                        elif "FR Custodia" in line:
                            row = line.replace("FR Custodia ", "")
                            row = row.split(" ")
                            if "PAGARE" in row:
                                fecha = datetime.strptime(row[0], "%d/%m/%Y").date()
                                tipo = row[2].upper()
                                nemotecnico = f"{row[4]} {row[-3]}"
                                cantidad = float(row[6].replace(".", "").replace(",", "."))
                                precio = float(row[7].replace(".", "").replace(",", "."))
                                monto = int(row[8].replace(".", ""))
                            else:
                                fecha = datetime.strptime(row[0], "%d/%m/%Y").date()
                                tipo = row[2].upper()
                                nemotecnico = row[4]
                                monto = int(row[7].replace(".", ""))
                                cantidad = float(row[5].replace(".", "").replace(",", "."))
                                precio = 0
                            result.append({
                                "nombre_fondo": fondo,
                                "fecha_pago":fecha,
                                "fecha_ingreso":fecha,
                                "precio":precio,
                                "cantidad":cantidad,
                                "monto":monto,
                                "comision": 0,
                                "nemotecnico":nemotecnico,
                                "compra/venta/vencimiento": tipo,
                                "tipo_operacion": "INSTRUMENTO FINANCIERO"
                            })
                        # Renta Fija
                        elif ("Compra RF" in line or "Venta RF" in line) and "Retrov Nominal" not in line:
                            row = line.split(" ")
                            fecha = datetime.strptime(row[0], "%d/%m/%Y").date()
                            tipo = row[2].upper()
                            nemotecnico = row[4]
                            precio = float(row[6].replace(".", "").replace(",", "."))
                            cantidad = float(row[5].replace(".", "").replace(",", "."))
                            monto = float(row[7].replace(".", "").replace(",", "."))
                            result.append({
                                "nombre_fondo": fondo,
                                "fecha_pago":fecha,
                                "fecha_ingreso":fecha,
                                "precio":precio,
                                "cantidad":cantidad,
                                "monto":monto,
                                "comision": 0,
                                "nemotecnico":nemotecnico,
                                "compra/venta/vencimiento": tipo,
                                "tipo_operacion": "RENTA FIJA"
                            })
                        # Renta Variable
                        elif (("Compra RV" in line or "Venta RV" in line) and "CFIN" in line) or (("Compra IF" in line or "Venta IF" in line) and "Retrov" not in line):
                            row = line.split(" ")
                            fecha = datetime.strptime(row[0], "%d/%m/%Y").date()
                            tipo = row[2].upper()
                            nemotecnico = row[4]
                            precio = float(row[6].replace(".", "").replace(",", "."))
                            cantidad = float(row[5].replace(".", "").replace(",", "."))
                            monto = float(row[7].replace(".", "").replace(",", "."))
                            result.append({
                                "nombre_fondo": fondo,
                                "fecha_pago":fecha,
                                "fecha_ingreso":fecha,
                                "precio":precio,
                                "cantidad":cantidad,
                                "monto":monto,
                                "comision": 0,
                                "nemotecnico":nemotecnico,
                                "compra/venta/vencimiento": tipo,
                                "tipo_operacion": "RENTA VARIABLE"
                            })
                        # Venta Simultanea
                        elif "N.Credito Retiro TP" in line:
                            row = line.replace("N.Credito Retiro TP ", "")
                            row = row.split(" ")
                            fecha = datetime.strptime(row[0], "%d/%m/%Y").date()
                            nemotecnico = row[2:-6]
                            nemotecnico = " ".join(nemotecnico)
                            cantidad = int(row[-6].replace(".", ""))
                            precio = float(row[-5].replace(".", "").replace(",", "."))
                            monto = int(row[-4].replace(".", ""))
                            result.append({
                                "nombre_fondo": fondo,
                                "fecha_pago":fecha,
                                "fecha_ingreso":fecha,
                                "precio":0,
                                "cantidad":cantidad*precio,
                                "monto":monto,
                                "comision": 0,
                                "nemotecnico":nemotecnico,
                                "compra/venta/vencimiento": "VENTA",
                                "tipo_operacion": "SIMULTANEA"
                            })

        df = pd.DataFrame(result)
        df_variable = df[df['tipo_operacion'] == 'RENTA VARIABLE']
        df_reminder = df[df['tipo_operacion'] != 'RENTA VARIABLE']
        agg_functions = {
            'nombre_fondo': 'first',
            'fecha_pago': 'first',
            'fecha_ingreso': 'first',
            'precio': 'first',
            'cantidad': 'sum', 
            'monto': 'sum',
            'comision': 'first',
            'nemotecnico': 'first',
            'compra/venta/vencimiento': 'first',
            'tipo_operacion': 'first'
        }
        df_variable = df_variable.groupby(["nemotecnico", "precio", "compra/venta/vencimiento"]).aggregate(agg_functions)
        if len(df_variable) != 0:
            df = pd.concat([df_reminder, df_variable])
        else:
            df = df_reminder

        df.to_excel(f"{folder}{process_date}_informe_completo_results.xlsx", index=False, engine="openpyxl")
        
    except Exception as err:
        raise Exception(f"Error en Parser de Informe Completo: {err}")

if __name__ == "__main__":
    process_date = datetime.today().strftime("%Y%m%d")
    main_folder = os.getcwd()

    informe_completo_parser(process_date, main_folder)