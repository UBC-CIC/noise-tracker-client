import logging.config

from constants import BASE_PATH

logging.config.dictConfig({"version": 1, "disable_existing_loggers": True})
logging.basicConfig(
    filename=f"{BASE_PATH}/logs",
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("main")
