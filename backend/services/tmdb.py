import os

import requests as req
from dotenv import load_dotenv

load_dotenv()
env = os.getenv

class TMDB:
    def __init__(self) -> None:
        self.headers = {
            "Authorization": f"Bearer {env("TMDB_API_KEY")}",
            "User-Agent": f"HuggyPanda/0.1.0 (https://huggypanda.com; {env("EMAIL")})",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Accept-Language": "en-US",
        }
        
    def get_content_summary(self, title: str) -> dict[str, str | int | float | list[dict[str, str]]]:
        try:
            res = req.get(
                "https://api.themoviedb.org/3/search/multi",
                headers=self.headers,
                params={
                    "query": title,
                    "include_adult": True,
                    "page": 1,
                },
            )
            
            if res.status_code != 200:
                return {}
            
            content_data = res.json()
            data = content_data["results"][0]
            
            if data["media_type"] == "movie" or data["media_type"] == "tv":
                return {
                    "is_adult": data["adult"],
                    "backdrop_url": (
                        f"https://image.tmdb.org/t/p/original{data["backdrop_path"]}"
                        if data["backdrop_path"] else ""
                    ),
                    "title": data["title"],
                    "og_title": data["original_title"],
                    "description": data["overview"],
                    "poster_url": (
                        f"https://image.tmdb.org/t/p/original{data["poster_path"]}"
                        if data["poster_path"] else ""
                    ),
                    "og_language": data["original_language"],
                    "release_date": data["release_date"],
                    "user_score_rating": round(data["vote_average"], 1),
                    "num_users_voted": data["vote_count"],
                    "_type": data["media_type"],
                    "_id": data["id"],
                }

            else:
                return {
                    "is_adult": data["adult"],
                    "name": data["name"],
                    "og_name": data["original_name"],
                    "pfp_url": (
                        f"https://image.tmdb.org/t/p/original{data["profile_path"]}"
                        if data["profile_path"] else ""
                    ),
                    "known_for_movies_and_tv": [
                        {
                            "title": content["title"],
                            "og_title": content["original_title"],
                            "poster_url": (
                                f"https://image.tmdb.org/t/p/original{data["poster_path"]}"
                                if data["poster_path"] else ""
                            ),
                            "release_date": content["release_date"],
                        }
                        for content in data["known_for"]
                    ],
                    "_type": data["media_type"],
                    "_id": data["id"],
                }

        except Exception:
            return {}
        
    def get_content_details(self, id: int, type: str) -> dict[str, str | list[str]]:
        try:
            req_url = None
            
            if type == "movie":
                req_url = f"https://api.themoviedb.org/3/movie/{id}"
            elif type == "tv":
                req_url = f"https://api.themoviedb.org/3/tv/{id}"
            else:
                req_url = f"https://api.themoviedb.org/3/person/{id}"
            
            res = req.get(
                req_url,
                headers=self.headers,
            )
            
            if res.status_code != 200:
                return {}
            
            data = res.json()
            
            if type == "movie":
                return {
                    "budget": f"${data["budget"]}",
                    "genres": [
                        genre["name"]
                        for genre in data["genres"]
                    ],
                    "url_to_website": data["homepage"],
                    "revenue": f"${data["revenue"]}",
                    "runtime": f"{data["runtime"]} min.",
                    "status": data["status"],
                    "tagline": data["tagline"],
                    "profit": f"${data["revenue"] - data["budget"]}",
                }
                
            elif type == "tv":
                return {
                    "creators": [
                        {
                            "name": creator["name"],
                            "og_name": creator["original_name"],
                            "pfp_url": (
                                f"https://image.tmdb.org/t/p/original{data["profile_path"]}"
                                if data["profile_path"] else ""
                            ),
                        }
                        for creator in data["created_by"]
                    ],
                    "genres": [
                        genre["name"]
                        for genre in data["genres"]
                    ],
                    "url_to_website": data["homepage"],
                    "num_episodes": data["number_of_episodes"],
                    "num_seasons": data["number_of_seasons"],
                    "status": data["status"],
                    "tagline": data["tagline"],
                    "show_type": data["type"],
                }
                
            else:
                return {
                    "biography": data["biography"][:len(data["biography"]) // 2] + "...",
                    "birthday": data["birthday"],
                    "deathday": data["deathday"] if data["deathday"] else "Still alive",
                    "url_to_website": data["homepage"],
                    "place_of_birth": data["place_of_birth"],
                }
        
        except:
            return {}
        
    def get_content_images(self, id: int, type: str) -> list[str]:
        try:
            req_url = None
            
            if type == "movie":
                req_url = f"https://api.themoviedb.org/3/movie/{id}/images"
            elif type == "tv":
                req_url = f"https://api.themoviedb.org/3/tv/{id}/images"
            else:
                req_url = f"https://api.themoviedb.org/3/person/{id}/images"
            
            res = req.get(
                req_url,
                headers=self.headers,
            )
            
            if res.status_code != 200:
                return []
            
            data = res.json()
            
            images = []
            
            for i, image in enumerate(data["backdrops"]):
                if i > 3:
                    break
                
                images.append(f"https://image.tmdb.org/t/p/original{image["file_path"]}")
            
            return images
        
        except Exception:
            return []
    
    def get_content_reviews(self, id: int, type: str) -> list[dict[str, str]]:
        try:
            req_url = None
            
            if type == "movie":
                req_url = f"https://api.themoviedb.org/3/movie/{id}/reviews"
            elif type == "tv":
                req_url = f"https://api.themoviedb.org/3/tv/{id}/reviews"
            else:
                return []
            
            res = req.get(
                req_url,
                headers=self.headers,
            )
            
            if res.status_code != 200:
                return []
            
            data = res.json()
            
            reviews = []
            
            for i, review in enumerate(data["results"]):
                if i > 3:
                    break
                
                reviews.append({
                    "reviewer_username": review["author_details"]["username"],
                    "review_snippet": review["content"][:len(review["content"]) // 2] + "...",
                    "review_date": review["updated_at"],
                    "url_to_review": review["url"],
                })
                
            return reviews
        
        except Exception:
            return []
        
    def get_tmdb_results(self, title: str) -> dict[str, str | dict[str, str]]:
        title = title.split("(")[0].strip()
        
        content_summary = get_content_summary(title)
        content_details = get_content_details(content_summary["_id"], content_summary["_type"])
        content_images = get_content_images(content_summary["_id"], content_summary["_type"])
        content_reviews = get_content_reviews(content_summary["_id"], content_summary["_type"])
        
        content_info = {}
        
        content_info = content_summary | content_details
        content_info["images"] = content_images
        content_info["reviews"] = content_reviews
        content_info["content_type"] = content_summary["_type"]
        
        return content_info
        
