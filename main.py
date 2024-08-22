import os
from datetime import datetime
from Prudential.PrudentialParser import prudential_parser
from Nevasa.Renta import nevasa_renta_parser
from Nevasa.InstrumentosFinancieros import nevasa_if_parser

process_date = datetime.today().strftime("%Y%m%d")
prudential_folder = f"{os.getcwd()}/Prudential"
nevasa_folder = f"{os.getcwd()}/Nevasa"
nevasa_renta_folder = f"{nevasa_folder}/Renta"
nevasa_if_folder = f"{nevasa_folder}/InstrumentosFinancieros"

prudential_parser(process_date, prudential_folder)
nevasa_renta_parser(process_date, nevasa_renta_folder)
nevasa_if_parser(process_date,nevasa_if_folder)
