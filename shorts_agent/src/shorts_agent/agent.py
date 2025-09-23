from __future__ import annotations
import click
from loguru import logger
from .config import Settings
from .downloader import Downloader
from .processor import Processor
try:
    from .subtitles import Subtitler
    SUBS_AVAILABLE = True
except Exception:
    Subtitler = None  # type: ignore
    SUBS_AVAILABLE = False
from .metadata import generate_title, generate_description, generate_hashtags
from .utils import ensure_dirs
from pathlib import Path
import datetime as dt
import csv

@click.group()
def cli():
    pass

@cli.command()
@click.argument('url')
@click.option('--topic', type=click.Choice(['motivation','funny','sports','football']), default='funny')
@click.option('--schedule', is_flag=True, default=False)
@click.option('--cookies', type=click.Path(exists=True, dir_okay=False), default=None, help='Path to cookies.txt (TikTok/Instagram).')
def run(url: str, topic: str, schedule: bool, cookies: str | None):
    s = Settings.from_yaml()
    ensure_dirs(s.download_dir, s.work_dir, s.output_dir, s.log_dir)

    dl = Downloader(s)
    pr = Processor(s)
    st = Subtitler(s) if SUBS_AVAILABLE else None
    from .dedupe import Dedupe
    dd = Dedupe(Path(s.output_dir) / 'hashes')

    item = dl.download(url, cookies=cookies)
    vertical = pr.to_vertical_60s(item['video_path'])

    with_subs = vertical
    if st:
        srt = st.transcribe_to_srt(vertical)
        with_subs = st.burn_in(vertical, srt)

    ph = dd.video_phash(with_subs)
    if dd.is_duplicate(ph):
        logger.error('Duplicate detected. Aborting upload.')
        return
    dd.store_hash(Path(with_subs).stem, ph)

    title = generate_title(topic)
    tags = generate_hashtags(topic)
    desc = generate_description(topic, credit=item['info'].get('uploader'))

    from .uploader import YouTubeUploader
    yt = YouTubeUploader(s.youtube_client_secrets, s.youtube_token)
    publish_at = None
    if schedule:
        now = dt.datetime.now(dt.timezone.utc)
        publish_at = (now + dt.timedelta(hours=2)).isoformat()

    yt.upload(with_subs, title, desc, tags, publish_at)
    logger.info('Done')

@cli.command()
@click.argument('csv_path', type=click.Path(exists=True, dir_okay=False))
@click.option('--topic', type=click.Choice(['motivation','funny','sports','football']), default='funny')
@click.option('--schedule', is_flag=True, default=False)
@click.option('--cookies', type=click.Path(exists=True, dir_okay=False), default=None, help='Path to cookies.txt (TikTok/Instagram).')
def batch(csv_path: str, topic: str, schedule: bool, cookies: str | None):
    """
    CSV columns: url,title_override(optional),description_override(optional)
    """
    s = Settings.from_yaml()
    ensure_dirs(s.download_dir, s.work_dir, s.output_dir, s.log_dir)

    dl = Downloader(s)
    pr = Processor(s)
    st = Subtitler(s) if SUBS_AVAILABLE else None
    from .dedupe import Dedupe
    dd = Dedupe(Path(s.output_dir) / 'hashes')

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = row.get('url')
            if not url:
                continue
            logger.info(f'Processing: {url}')
            item = dl.download(url, cookies=cookies)
            vertical = pr.to_vertical_60s(item['video_path'])

            with_subs = vertical
            if st:
                srt = st.transcribe_to_srt(vertical)
                with_subs = st.burn_in(vertical, srt)

            ph = dd.video_phash(with_subs)
            if dd.is_duplicate(ph):
                logger.warning('Duplicate detected. Skipping upload.')
                continue
            dd.store_hash(Path(with_subs).stem, ph)

            title = row.get('title_override') or generate_title(topic)
            tags = generate_hashtags(topic)
            desc = row.get('description_override') or generate_description(topic, credit=item['info'].get('uploader'))

            from .uploader import YouTubeUploader
            yt = YouTubeUploader(s.youtube_client_secrets, s.youtube_token)
            publish_at = None
            if schedule:
                now = dt.datetime.now(dt.timezone.utc)
                publish_at = (now + dt.timedelta(hours=2)).isoformat()

            yt.upload(with_subs, title, desc, tags, publish_at)
    logger.info('Batch complete')

@cli.command()
@click.argument('source')
@click.option('--cookies', type=click.Path(exists=True, dir_okay=False), default=None)
@click.option('--limit', type=int, default=20)
@click.option('--out', type=click.Path(dir_okay=False), default='discovered_urls.csv')
@click.option('--autobatch', is_flag=True, default=False, help='Immediately process discovered URLs as batch.')
@click.option('--schedule', is_flag=True, default=False)
@click.option('--topic', type=click.Choice(['motivation','funny','sports','football']), default='funny')
def discover(source: str, cookies: str | None, limit: int, out: str, autobatch: bool, schedule: bool, topic: str):
    """
    Discover recent URLs from a TikTok/Instagram profile/hashtag, save to CSV, optionally auto-batch.
    Examples:
      discover https://www.tiktok.com/@someprofile --limit 10
      discover https://www.tiktok.com/tag/funny --autobatch
    """
    s = Settings.from_yaml()
    dl = Downloader(s)
    urls = dl.discover_urls(source, cookies=cookies, limit=limit)
    with open(out, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['url','title_override','description_override'])
        for u in urls:
            writer.writerow([u,'',''])
    logger.info(f'Saved {len(urls)} URLs to {out}')
    if autobatch and urls:
        logger.info('Starting autobatch...')
        batch(out, topic=topic, schedule=schedule, cookies=cookies)

if __name__ == '__main__':
    cli()
