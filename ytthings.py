from typing import List
import discord
from discord.utils import get
import oembed
import urlextract
extractor = urlextract.URLExtract()
consumer = oembed.OEmbedConsumer()
endpoint = oembed.OEmbedEndpoint('https://www.youtube.com/oembed/', ['*.youtube.com/*', 'youtu.be/*', 'youtube.com/*'])
consumer.addEndpoint(endpoint)

def get_links_from_string(string: str) -> List[str]:
    return extractor.find_urls(string)

def get_youtube_links_from_list(links: List[str]) -> List[str]:
    return [link for link in links if 'youtu' in link]

def convert_youtube_links_to_format(links: List[str]) -> List[str]:
    return [link.replace('youtu.be/', 'youtube.com/watch?v=') for link in links]

def get_channel_link_from_link(link: str) -> str:
    response = consumer.embed(link)
    return response.getData()['author_url']

if __name__ == "__main__":
    x = get_links_from_string('@Kalm https://www.youtube.com/watch?v=VVXaOcwZJYY')
    print(x)
    y = get_youtube_links_from_list(x)
    print(y)
    z = convert_youtube_links_to_format(y)
    print(z)
    for link in z:
        print(get_channel_link_from_link(link))