import os
from dataclasses import dataclass
from dotenv import load_dotenv
import yaml

load_dotenv()

@dataclass
class Settings:
    youtube_client_secrets: str = os.getenv('YOUTUBE_CLIENT_SECRETS', 'client_secret.json')
    youtube_token: str = os.getenv('YOUTUBE_TOKEN', 'youtube_token.json')
    brand_overlay: str = os.getenv('BRAND_OVERLAY', 'assets/branding/brand_overlay.png')
    audio_music_dir: str = os.getenv('AUDIO_MUSIC_DIR', 'assets/music')
    output_dir: str = os.getenv('OUTPUT_DIR', 'data/outputs')
    download_dir: str = os.getenv('DOWNLOAD_DIR', 'data/downloads')
    work_dir: str = os.getenv('WORK_DIR', 'data/work')
    log_dir: str = os.getenv('LOG_DIR', 'data/logs')
    timezone: str = os.getenv('TIMEZONE', 'America/New_York')
    video_max_seconds: int = 60
    frame_rate: int = 30
    resolution: tuple[int, int] = (1080, 1920)
    loudness_lufs: float = -14.0
    true_peak_db: float = -1.0
    subtitle_font_size: int = 42
    subtitle_max_lines: int = 2

    @classmethod
    def from_yaml(cls, path: str = 'config.yaml'):
        if os.path.exists(path):
            with open(path, 'r') as f:
                data = yaml.safe_load(f) or {}
            s = cls()
            s.video_max_seconds = data.get('video_max_seconds', s.video_max_seconds)
            s.frame_rate = data.get('frame_rate', s.frame_rate)
            res = data.get('resolution', {'width': 1080, 'height': 1920})
            s.resolution = (res.get('width', 1080), res.get('height', 1920))
            s.loudness_lufs = float(data.get('loudness_lufs', s.loudness_lufs))
            s.true_peak_db = float(data.get('true_peak_db', s.true_peak_db))
            s.subtitle_font_size = int(data.get('subtitle_font_size', s.subtitle_font_size))
            s.subtitle_max_lines = int(data.get('subtitle_max_lines', s.subtitle_max_lines))
            return s
        return cls()
