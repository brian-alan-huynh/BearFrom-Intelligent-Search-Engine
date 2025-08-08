import os

import requests as req
from dotenv import load_dotenv

load_dotenv()
env = os.dotenv

class NewYorkTimes:
    def __init__(self) -> None:
        self.headers = {
            "User-Agent": f"HuggyPanda/0.1.0 (https://huggypanda.com; {env("EMAIL")})",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Accept-Language": "en-US",
        }

    def get_world_top_stories(self) -> list[dict[str, str]]:
        try:
            res = req.get(
                "https://api.nytimes.com/svc/topstories/v2/world.json",
                headers=self.headers,
                params={ "api-key": env("NEW_YORK_TIMES_API_KEY") },
            )
            
            if res.status_code != 200:
                return []
            
            data = res.json()
            
            world_top_stories = []
            
            for article in data["results"]:
                world_top_stories.append({
                    "title": article["title"],
                    "overview": article["abstract"],
                    "url_to_article": article["url"],
                    "by_author_line": article["byline"],
                    "published_date": article["published_date"],
                    "updated_date": article["updated_date"],
                    "tags": article["des_facet"],
                    "thumbnail_url": article["multimedia"][0]["url"],
                    "thumbnail_caption": article["multimedia"][0]["caption"],
                })
                
            return world_top_stories
            
        except Exception:
            return []
        
    def search_stories(self, query: str) -> list[dict[str, str]]:
        try:
            res = req.get(
                "https://api.nytimes.com/svc/search/v2/articlesearch.json",
                headers=self.headers,
                params={
                    "api-key": env("NEW_YORK_TIMES_API_KEY"),
                    "q": query,
                },
            )
            
            if res.status_code != 200:
                return []
            
            data = res.json()
            
            stories = []
            
            for article in data["response"]["docs"]:
                stories.append({
                    "title": article["headline"]["main"],
                    "overview": article["abstract"],
                    "url_to_article": article["web_url"],
                    "by_author_line": article["byline"]["original"],
                    "published_date": article["pub_date"],
                    "thumbnail_url": article["multimedia"]["default"]["url"],
                    "thumbnail_caption": article["multimedia"]["caption"],
                })
                
            return stories
            
        except Exception:
            return []
