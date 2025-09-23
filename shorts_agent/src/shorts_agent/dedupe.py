from loguru import logger
from PIL import Image
import imagehash
import cv2
import numpy as np
from pathlib import Path

class Dedupe:
    def __init__(self, library_dir: str):
        self.library_dir = Path(library_dir)
        self.library_dir.mkdir(parents=True, exist_ok=True)

    def video_phash(self, path: str) -> str:
        cap = cv2.VideoCapture(path)
        frame_hashes = []
        success, frame = cap.read()
        step = int(cap.get(cv2.CAP_PROP_FPS)) or 30
        idx = 0
        while success:
            if idx % step == 0:
                img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                frame_hashes.append(str(imagehash.phash(img)))
            success, frame = cap.read()
            idx += 1
        cap.release()
        return '|'.join(frame_hashes[:10])

    def is_duplicate(self, new_hash: str, threshold: int = 8) -> bool:
        for hp in self.library_dir.glob('*.phash'):
            with open(hp,'r') as f:
                old_hash = f.read().strip()
            if self._distance(new_hash, old_hash) <= threshold:
                logger.warning(f'Near-duplicate detected vs {hp.name}')
                return True
        return False

    def store_hash(self, name: str, phash: str) -> None:
        with open(self.library_dir / f"{name}.phash", 'w') as f:
            f.write(phash)

    def _distance(self, h1: str, h2: str) -> int:
        a = imagehash.hex_to_hash(h1.split('|')[0])
        b = imagehash.hex_to_hash(h2.split('|')[0])
        return (a - b)
