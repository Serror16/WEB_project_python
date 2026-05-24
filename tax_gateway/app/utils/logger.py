import logging
import sys

def setup_logging():
    """Настройка глобального логирования для всего приложения."""
    

    log_format = "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"

    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logging.getLogger("httpx").setLevel(logging.WARNING)