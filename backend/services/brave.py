import os

import requests as req
from dotenv import load_dotenv

from .wiki import get_wiki_result, get_wiki_infobox_result, get_wiki_see_also

load_dotenv()
env = os.getenv

class Brave:
    def __init__(self):
        self.search_headers = {
            "X-Subscription-Token": env("BRAVE_SEARCH_API_KEY"),
            "User-Agent": f"HuggyPanda/0.1.0 (https://huggypanda.com; {env("EMAIL")})",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Accept-Language": "en-US",
        }
        
        self.suggest_headers = {
            "X-Subscription-Token": env("BRAVE_SUGGEST_API_KEY"),
            "User-Agent": f"HuggyPanda/0.1.0 (https://huggypanda.com; {env("EMAIL")})",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Accept-Language": "en-US",
        }
        
    def _get_url(self, search_type: str) -> str:
        return f"https://api.search.brave.com/res/v1/{search_type}/search"
            
    def get_web_results(self, query: str, safesearch: str): # fetch the safesearch preferences by calling s3 method in the route logic
        try:
            res = req.get(
                self._get_url("web"),
                headers=self.search_headers,
                params={
                    "q": query,
                    "safesearch": safesearch,
                    "units": "imperial",
                    "extra_snippets": True,
                },
            )
            
            if res.status_code != 200:
                return {
                    "success": False,
                    "response": "Failed to get web results",
                }
            
            data = res.json()
            
            search_results = {}
            blended_results = {}
            extra_snippets = []
            
            search_results["og_query"] = data["query"]["original"]
            search_results["corrected_query"] = data["query"]["altered"] if data["query"]["altered"] else ""

            # News results
            if data["news"]:
                news_res_filtered = []
                
                for news_res in data["news"]["results"]:
                    news_res_filtered.append({
                        "title": news_res["title"],
                        "url": news_res["url"],
                        "snippet": news_res["description"],
                        "created_date": news_res["page_age"],
                        "site_name": news_res["profile"]["name"],
                        "is_family_friendly": news_res["family_friendly"],
                        "favicon": (
                            news_res["meta_url"]["favicon"] 
                            if news_res["meta_url"]["favicon"] 
                            else news_res["profile"]["img"]
                        ),
                        "site_homepage": news_res["meta_url"]["hostname"],
                        "url_path_from_homepage_to_result": news_res["meta_url"]["path"],
                        "is_breaking_news": news_res["breaking"],
                        "is_live": news_res["is_live"],
                        "thumbnail": news_res["thumbnail"]["original"],
                        "age": news_res["age"],
                    })
                    
                    extra_snippets + news_res["extra_snippets"]
                
                search_results["news_cluster"] = news_res_filtered
                    
            else:
                search_results["news_cluster"] = []
            
            # Video results
            if data["videos"]:
                video_res_filtered = []
                
                for video_res in data["videos"]["results"]:
                    video_res_filtered.append({
                        "url": video_res["url"],
                        "title": video_res["title"],
                        "snippet": video_res["description"],
                        "age": video_res["age"],
                        "created_date": video_res["page_age"],
                        "duration": video_res["video"]["duration"],
                        "creator": video_res["video"]["creator"] if video_res["video"]["creator"] else "",
                        "publisher": video_res["video"]["publisher"],
                        "site_homepage": video_res["meta_url"]["hostname"],
                        "favicon": video_res["meta_url"]["favicon"],
                        "url_path_from_homepage_to_result": video_res["meta_url"]["path"],
                        "embed_video_url": f"https://www.youtube.com/embed/{video_res["url"].split("=")[-1]}",
                    })
                
                search_results["video_cluster"] = video_res_filtered
                
            else:
                search_results["video_cluster"] = []

            # Web results
            web_res_filtered = []
            
            for web_res in data["web"]["results"]:
                title = web_res["title"]
                url = web_res["url"]
                site_name = web_res["profile"]["name"]
                
                if site_name == "Wikipedia":
                    shaved_title = title.replace(" - Wikipedia", "")
                    
                    blended_results["wiki"] = get_wiki_result(shaved_title)
                    blended_results["wiki_infobox"] = get_wiki_infobox_result(url)
                    blended_results["wiki_see_also"] = get_wiki_see_also(shaved_title)
                
                if site_name == "Tripadivsor":
                    pass
                
                web_res_filtered.append({
                    "title": title,
                    "url": url,
                    "snippet": web_res["description"],
                    "created_date": web_res["page_age"] if web_res["page_age"] else "",
                    "site_name": site_name,
                    "favicon": (
                        web_res["meta_url"]["favicon"] 
                        if web_res["meta_url"]["favicon"] 
                        else web_res["profile"]["img"]
                    ),
                    "is_family_friendly": web_res["family_friendly"],
                    "is_live": web_res["is_live"],
                    "deep_results": (
                        [
                            { "title": deep_res["title"], "url": deep_res["url"] }
                            for deep_res in web_res["deep_results"]["button"]
                        ]
                        if web_res["deep_results"]
                        else ""
                    ),
                    "site_homepage": web_res["meta_url"]["hostname"],
                    "url_path_from_homepage_to_result": web_res["meta_url"]["path"],
                    "age": web_res["age"] if web_res["age"] else "",
                    "thumbnail": web_res["thumbnail"]["original"] if web_res["thumbnail"] else "",
                })
                
                extra_snippets + web_res["extra_snippets"]
            
            search_results["web_results"] = web_res_filtered
            
            return {
                "success": True,
                "response": { search_results, blended_results, extra_snippets },
            }
        
        except Exception as e:
            return {
                "success": False,
                "response": f"Failed to get web results ({e})",
            }

    def get_suggest_results(self, query: str) -> dict[str, bool | list[str]]:
        try:
            res = req.get(
                self._get_url("suggest"),
                headers=self.suggest_headers,
                params={
                    "q": query,
                    "count": 20,
                },
            )

            if res.status_code != 200:
                return {
                    "success": False,
                    "response": "Failed to get suggest results",
                }
            
            data = res.json()
            
            suggested_queries = [
                query_obj["query"]
                for query_obj in data["results"]
            ]

            return {
                "success": True,
                "response": suggested_queries,
            }
        
        except Exception as e:
            return {
                "success": False,
                "response": f"Failed to get suggest results ({e})",
            }
