from loguru import logger
from .config import Settings
from .utils import ensure_dirs

from faster_whisper import WhisperModel
import subprocess
from pathlib import Path

class Subtitler:
    def __init__(self, settings: Settings, model_size: str = 'small'):
        self.s = settings
        ensure_dirs(self.s.work_dir)
        self.model = WhisperModel(model_size, device='cpu', compute_type='int8')

    def transcribe_to_srt(self, src_path: str) -> str:
        segments, info = self.model.transcribe(src_path, beam_size=1)
        srt_path = str(Path(self.s.work_dir) / (Path(src_path).stem + '.srt'))
        with open(srt_path,'w') as f:
            idx = 1
            for seg in segments:
                start = self._fmt(seg.start)
                end = self._fmt(seg.end)
                text = seg.text.strip()
                f.write(f"{idx}\n{start} --> {end}\n{text}\n\n")
                idx += 1
        logger.info(f'Generated SRT: {srt_path}')
        return srt_path

    def burn_in(self, video_path: str, srt_path: str) -> str:
        out_path = str(Path(self.s.output_dir) / (Path(video_path).stem + '_subs.mp4'))
        draw = f"subtitles='{srt_path}':force_style='Fontsize={self.s.subtitle_font_size}'"
        cmd = ['ffmpeg','-y','-i', video_path, '-vf', draw, '-c:a','copy', out_path]
        subprocess.run(cmd, check=True)
        logger.info(f'Burnt-in subtitles: {out_path}')
        return out_path

    def _fmt(self, t: float) -> str:
        h = int(t//3600); m = int((t%3600)//60); s = int(t%60); ms = int((t*1000)%1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
