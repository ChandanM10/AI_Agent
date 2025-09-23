from loguru import logger
from .config import Settings
from .utils import ensure_dirs
import subprocess
from pathlib import Path

class Processor:
    def __init__(self, settings: Settings):
        self.s = settings
        ensure_dirs(self.s.work_dir, self.s.output_dir)

    def to_vertical_60s(self, src_path: str) -> str:
        out_path = str(Path(self.s.output_dir) / (Path(src_path).stem + '_vertical.mp4'))
        w, h = self.s.resolution
        vf = f"scale=w={w}:h={h}:force_original_aspect_ratio=decrease, pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=black, fps={self.s.frame_rate}"
        cmd = ['ffmpeg','-y','-i', src_path, '-t', str(self.s.video_max_seconds), '-vf', vf, '-c:v','libx264','-preset','veryfast','-profile:v','high','-b:v','6M','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k', out_path]
        logger.info(f'Processing to vertical: {src_path} -> {out_path}')
        subprocess.run(cmd, check=True)
        return out_path
