import os
from datetime import datetime
import logging
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent
from Nevasa.InformeCompleto.InformeCompletoParser import informe_completo_parser

logger = logging.getLogger(__name__)

def on_created(event: FileCreatedEvent):
    time.sleep(1)
    filename = event.src_path

    if "informeMensual.do.pdf" in filename:
        main_folder = os.getcwd() + "\\Nevasa\\InformeCompleto"
        process_date = datetime.today().strftime("%Y%m%d")

        informe_completo_parser(process_date, main_folder)
        logger.info(f'Excel resultados del informe de Nevasa creado con fecha {process_date}')

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    event_handler = FileSystemEventHandler()
    event_handler.on_created = on_created
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()