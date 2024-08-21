import os
from datetime import datetime
from Prudential.PrudentialParser import prudential_parser

process_date = datetime.today().strftime("%Y%m%d")
prudential_folder = f"{os.getcwd()}/Prudential"

prudential_parser(process_date, prudential_folder)