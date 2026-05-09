import logging
import sys

def setup_logging():
    """Настройка глобального логирования для всего приложения."""
    
    # Формат: [2026-05-09 18:00:00] [INFO] [app.adapters.russia_adapter]: Сообщение
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