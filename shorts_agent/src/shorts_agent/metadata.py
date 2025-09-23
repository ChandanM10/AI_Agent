from loguru import logger
import random

TOPIC_TAGS = {
    'motivation': ['motivation','success','mindset','discipline','habits','goals'],
    'funny': [
        'funny','lol','meme','comedy','fails','relatable','prank','skit','movieclips',
        'reels','tiktok','viralvideo','laugh','humor','trend'
    ],
    'sports': ['sports','workout','fitness','training','athlete','grind'],
    'football': [
        'football','soccer','futbol','goals','skills','highlights','dribbles','freekick',
        'messi','lionelmessi','barcelona','psg','intermiami','argentina','ronaldo','cr7',
        'neymar','mbappe','pedri','gavi','xavi','barca','laliga','ucl','uefachampionsleague'
    ]
}

def generate_title(topic: str) -> str:
    if topic == 'motivation':
        return 'Stop Scrolling. Start Building.'
    if topic == 'funny':
        options = [
            "This Made Me Cry Laughing",
            "Funniest 60 Seconds Today",
            "I Wasn't Ready For This",
            "Try Not To Laugh: 60s"
        ]
        return random.choice(options)
    if topic == 'sports':
        return "You Won't Skip Leg Day Again"
    if topic == 'football':
        return 'Insane Messi Skill Move'
    return 'This Blew My Mind'

def generate_hashtags(topic: str) -> list[str]:
    base = ['shorts','viral','fyp'] + TOPIC_TAGS.get(topic, [])
    # ensure football-specific virals are prioritized when topic is football
    if topic == 'football':
        preferred = ['footballshorts','messishorts','soccer','ucl','barcelona','intermiami','argentina','ronaldo','cr7','pedri','futbol','goal','skills']
        base = preferred + base
    return [f"#{t}" for t in base][:15]

def generate_description(topic: str, credit: str | None = None) -> str:
    keywords = ', '.join(TOPIC_TAGS.get(topic, ['trending']))
    if topic == 'football':
        desc = (
            "60 seconds of elite football highlights — skills, goals, and clutch plays. "
            f"Keywords: {keywords}."
        )
    elif topic == 'funny':
        desc = (
            "60 seconds of the funniest viral reels & movie moments. "
            "Daily laughs, pranks, and comedy cuts. "
            f"Keywords: {keywords}."
        )
    else:
        desc = f"60 seconds, {topic}. Keywords: {keywords}."
    if credit:
        desc += f"\nCredits: {credit}"
    return desc
