import os
from datetime import datetime
from Prudential.PrudentialParser import prudential_parser
from Nevasa.Renta import nevasa_renta_parser

process_date = datetime.today().strftime("%Y%m%d")
prudential_folder = f"{os.getcwd()}/Prudential"
nevasa_renta_folder = f"{os.getcwd()}/Nevasa/Renta"

prudential_parser(process_date, prudential_folder)
nevasa_renta_parser(process_date, nevasa_renta_folder)
