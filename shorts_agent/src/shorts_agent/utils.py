from loguru import logger
import os

def ensure_dirs(*dirs: str) -> None:
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        logger.debug(f'Ensured directory exists: {d}')
