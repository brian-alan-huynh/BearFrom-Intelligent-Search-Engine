import os
from datetime import datetime

import requests as req
from dotenv import load_dotenv

load_dotenv()
env = os.getenv

class Tripadvisor:
    def __init__(self):
        self.headers = {
            "User-Agent": f"HuggyPanda/0.1.0 (https://huggypanda.com; {env("EMAIL")})",
            "Referer": "https://huggypanda.com",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Accept-Language": "en-US",
        }
        
    def _query_for_hotels_in_city(self, title: str) -> str:
        location = ""
        split_title = title.split(" ")

        for i in range(len(split_title)):
            if ":" in split_title[i]:
                location = " ".join(split_title[:i+1])
                break
            elif "(" in split_title[i] or "-" in split_title[i]:
                location = " ".join(split_title[:i])
                break

        location = location.replace(",", "").replace(":", "")
        
        return location + " hotels"

    def _query_places(self, query: str, place_type: str) -> list[dict[str, str]]:
        try:
            res = req.get(
                "https://api.content.tripadvisor.com/api/v1/location/search",
                headers=self.headers,
                params={
                    "key": env("TRIPADVISOR_API_KEY"),
                    "searchQuery": query,
                    "category": place_type,
                    "language": "en",
                },
            )
            
            if res.status_code != 200:
                raise Exception("Failed to get Tripadvisor Details results")
            
            data = res.json()
        
            places_results = []
            
            for place in data["data"]:
                places_results.append({
                    "name": place["name"],
                    "city": place["address_obj"]["city"],
                    "address": place["address_obj"]["address_string"],
                    "location_id": place["location_id"],
                })
            
            return places_results
        
        except Exception as e:
            raise Exception(f"Failed to get Tripadvisor Details results ({e})")
    
    def _get_place_details(
        self,
        places_results: list[dict[str, str]]
    ) -> list[dict[str, str] | list[dict[str, str] | list[str]]]:
        
        try:
            places_details_results = []
            
            for place in places_results:
                location_id = place["location_id"]
            
                res = req.get(
                    f"https://api.content.tripadvisor.com/api/v1/location/{location_id}/details",
                    headers=self.headers,
                    params={
                        "key": env("TRIPADVISOR_API_KEY"),
                        "language": "en",
                    },
                )
                
                if res.status_code != 200:
                    raise Exception("Failed to get Tripadvisor Details results")
                    
                data = res.json()
                
                places_details_results.append({
                    "rating": data["rating"],
                    "rating_image": data["rating_image_url"],
                    "rank": data["ranking_data"]["ranking_string"],
                    "num_reviews": data["num_reviews"],
                    "review_rating_count": data["review_rating_count"],
                    "summary_rating": [
                        {
                            "category": data["subratings"][k]["localized_name"],
                            "rating_image": data["subratings"][k]["rating_image_url"],
                            "rating": data["subratings"][k]["value"],
                        }
                        for k in data["subratings"].keys()
                    ],
                    "description": data["description"],
                    "price_level": data["price_level"],
                    "url_to_listing": data["web_url"],
                    "phone_num": data["phone"] if data["phone"] else "",
                    "url_to_lister": data["website"] if data["website"] else "",
                    "email": data["email"] if data["email"] else "",
                    "awards": [
                        {
                            "name": award["display_name"],
                            "year": award["year"],
                            "image": award["images"]["small"],
                        }
                        for award in data["awards"]
                    ] if data["awards"] else [],
                    "photo_count": data["photo_count"],
                    "url_to_photos": data["see_all_photos"],
                    "opening_hours": data["hours"]["weekday_text"] if data["hours"]["weekday_text"] else {},
                    "features": data["features"] if data["features"] else [],
                    "amenities": data["amenities"] if data["amenities"] else [],
                    "cuisine": [
                        cuisine["localized_name"]
                        for cuisine in data["cuisine"]
                    ] if data["cuisine"] else []
                })
        
            return places_details_results
        
        except Exception as e:
            raise Exception(f"Failed to get Tripadvisor Details results ({e})")
        
    def _get_place_images(
        self,
        places_results: list[dict[str, str]]
    ) -> list[dict[str, list[str]]]:
        
        try:
            places_images_results = []
            
            for place in places_results:
                location_id = place["location_id"]
                    
                res = req.get(
                    f"https://api.content.tripadvisor.com/api/v1/location/{location_id}/photos",
                    headers=self.headers,
                    params={
                        "key": env("TRIPADVISOR_API_KEY"),
                        "language": "en",
                        "limit": 5,
                    },
                )
                
                if res.status_code != 200:
                    raise Exception("Failed to get Tripadvisor Image results")
                
                data = res.json()
                
                place_images = []
                
                for image_data in data["data"]:
                    place_images.append({
                        "image": image_data["images"]["original"]["url"],
                        "date": (datetime.fromisoformat(image_data["published_date"]
                                                        .replace("Z", "+00:00"))
                                .strftime(r"%Y-%m-%d"))
                    })
                
                places_images_results.append(place_images)
                
            return places_images_results
            
        except Exception as e:
            raise Exception(f"Failed to get Tripadvisor Image results ({e})")
        
    def _get_place_reviews(
        self,
        places_results: list[dict[str, str]]
    ) -> list[dict[str, str | list[str | dict[str, str]], dict[str, str]]]:
        
        try:
            places_reviews_results = []
            
            for place in places_results:
                location_id = place["location_id"]
                
                res = req.get(
                    f"https://api.content.tripadvisor.com/api/v1/location/{location_id}/reviews",
                    headers=self.headers,
                    params={
                        "key": env("TRIPADVISOR_API_KEY"),
                        "language": "en",
                        "limit": 5,
                    },
                )
                
                if res.status_code != 200:
                    raise Exception("Failed to get Tripadvisor Review results")
                
                data = res.json()
                
                place_reviews = []
                
                for review_data in data["data"]:
                    place_reviews.append({
                        "rating": review_data["rating"],
                        "rating_image": review_data["rating_image_url"],
                        "url_to_review": review_data["url"],
                        "title": review_data["title"],
                        "review_snippet": review_data["text"],
                        "review_date": review_data["published_date"],
                        "travel_date": review_data["travel_date"],
                        "trip_type": review_data["trip_type"],
                        "reviewer_username": review_data["user"]["username"],
                        "reviewer_location": review_data["user"]["user_location"]["name"],
                        "reviewer_pfp": review_data["user"]["avatar"]["original"],
                        "summary_rating": [
                            {
                                "category": data["subratings"][k]["localized_name"],
                                "rating_image": data["subratings"][k]["rating_image_url"],
                                "rating": data["subratings"][k]["value"],
                            }
                            for k in data["subratings"].keys()
                        ],
                        "owner_response_snippet": review_data["owner_response"]["title"],
                        "owner_response_title": review_data["owner_response"]["text"],
                        "owner_response_name": review_data["owner_response"]["author"],
                        "owner_response_date": review_data["owner_response"]["published_date"],
                    })
                    
                places_reviews_results.append(place_reviews)
            
            return places_reviews_results
        
        except Exception as e:
            raise Exception(f"Failed to get Tripadvisor Review results ({e})") 

    def get_place_results(
        self,
        query: str,
        eatery_search: bool = False,
        from_title: bool = False
    ) -> dict[str, bool | dict[str, str]]:
        
        if from_title:
            query = self._query_for_hotels_in_city(query)
        
        place_type = "restaurants" if eatery_search else "hotels"
        
        places = self._query_places(query, place_type) # [{}, {}, {}]
        details = self._get_place_details(places) # [{}, {}, {}]
        images = self._get_place_images(places) # [[{}, {}, {}], [{}, {}, {}], [{}, {}, {}]]
        reviews = self._get_place_reviews(places) # [[{}, {}, {}], [{}, {}, {}], [{}, {}, {}]]
        
        place_results = []
        
        for i in range(len(places)):
            concat_place = places[i] | details[i]
            concat_place["images"] = images[i]
            concat_place["reviews"] = reviews[i]
            
            place_results.append(concat_place)
        
        return place_results

