from loguru import logger
from .config import Settings
from .utils import ensure_dirs

import subprocess
import json
from pathlib import Path

class Downloader:
    def __init__(self, settings: Settings):
        self.s = settings
        ensure_dirs(self.s.download_dir)

    def download(self, url: str, cookies: str | None = None) -> dict:
        out_tmpl = str(Path(self.s.download_dir) / '%(title)s-%(id)s.%(ext)s')
        cmd = ['yt-dlp','-f','mp4','-o', out_tmpl, '--no-playlist','--restrict-filenames','--write-info-json']
        if cookies:
            cmd += ['--cookies', cookies]
        cmd.append(url)
        logger.info(f'Downloading: {url}')
        subprocess.run(cmd, check=True)
        files = sorted(Path(self.s.download_dir).glob('*.info.json'), key=lambda p: p.stat().st_mtime, reverse=True)
        if not files:
            raise RuntimeError('No metadata found after download')
        info_path = files[0]
        with open(info_path, 'r') as f:
            info = json.load(f)
        video_candidates = sorted(Path(self.s.download_dir).glob(f"*{info.get('id','')}*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not video_candidates:
            raise RuntimeError('Downloaded video not found')
        video_path = str(video_candidates[0])
        return { 'video_path': video_path, 'info_path': str(info_path), 'info': info }

    def discover_urls(self, source: str, cookies: str | None = None, limit: int = 20) -> list[str]:
        """Return recent video URLs from a TikTok/Instagram profile or hashtag without downloading.
        Uses a stable desktop User-Agent and TikTok web-new-ui extractor flags.
        """
        ua = (
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
            'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15'
        )
        jcmd = [
            'yt-dlp', '--flat-playlist', '-J', '--user-agent', ua,
            '--extractor-args', 'tiktok:use_web_new_ui=True;skip_dubious=True'
        ]
        if cookies:
            jcmd += ['--cookies', cookies]
        jcmd.append(source)
        logger.info(f'Discovering URLs from: {source}')
        try:
            proc = subprocess.run(jcmd, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f'Discovery failed (exit {e.returncode}). stderr: {e.stderr.strip()}')
            raise
        data = json.loads(proc.stdout or '{}')
        entries = data.get('entries', [])
        urls: list[str] = []
        for e in entries:
            url = e.get('url') or e.get('webpage_url') or e.get('id')
            if not url:
                continue
            # Normalize TikTok short IDs to full URLs if needed
            if isinstance(url, str) and url.startswith('http'):
                urls.append(url)
        return urls[:limit]
