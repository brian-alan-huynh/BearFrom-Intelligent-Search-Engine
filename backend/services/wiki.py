import os
import re

import requests as req
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
env = os.getenv

class Wiki:
    def __init__(self) -> None:
        self.headers = {
            "User-Agent": f"HuggyPanda/0.1.0 (https://huggypanda.com; {env("EMAIL")})",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Accept-Language": "en-US",
        }

    def get_wiki_result(title: str) -> dict[str, str]:
        try:
            res = req.get(
                "https://en.wikipedia.org/w/api.php",
                headers = self.headers,
                params={
                    "action": "query",
                    "props": "extracts|pageimages",
                    "titles": title,
                    "explaintext": True,
                    "format": "json",
                    "pithumbsize": 700,
                },
            )
            
            if res.status_code != 200:
                return {
                    "success": False,
                    "response": "Failed to get Wiki results",
                }
            
            res_data = res.json()
            
            res_page_data_key = res_data["query"]["pages"].keys()
            data = res_data["query"]["pages"][res_page_data_key[0]]
            
            return {
                "success": True,
                "response": {
                    "title": data["title"],
                    "snippet": data["extract"].split("==")[0].replace("\n", " "),
                    "thumbnail": data["thumbnail"]["source"],
                },
            }
            
        except Exception as e:
            return {
                "success": False,
                "response": f"Failed to get Wiki results ({e})",
            }
            
    def _filter_infobox_coords(coord: str) -> str:
        coord_split = coord.split('/')[-1]

        decimal_coord = ''

        for val in coord_split:
            if val == '.' or val == ' ':
                decimal_coord += val
                continue
            elif (
                val == 'N' or
                val == 'S' or
                val == 'E' or
                val == 'W'
            ):
                decimal_coord += '°' + val
                continue

            try:
                int(val)
                decimal_coord += val
            except:
                continue

        decimal_coord_split = decimal_coord.strip().split(' ')

        for i in range(len(decimal_coord_split)):
            if 'S' in decimal_coord_split[i] or 'W' in decimal_coord_split[i]:
                decimal_coord_split[i] = '-' + decimal_coord_split[i]

        return ' '.join(decimal_coord_split)
    
    def get_wiki_infobox_result(url: str) -> dict[str, str | dict[str, str]]:
        try:
            infoboxes = pd.read_html(url, attrs={"class": "infobox"})
            
            if infoboxes:
                infobox = infoboxes[0]
                infobox_keys = list(infobox.keys())
                infobox_len = len(infobox) - 1

                filtered_wiki_infobox = {}

                for i in range(infobox_len):
                    first_col_row = infobox[infobox_keys[0]][i]
                    second_col_row = infobox[infobox_keys[1]][i]

                    if (
                        pd.isna(first_col_row) or
                        pd.isna(second_col_row) or
                        any(x in first_col_row for x in ["Dependencies", "Subsidaries", "Subordinated", "Latitude", "Longitude"])
                    ):
                        continue

                    if "Coordinates" in first_col_row:
                        filtered_wiki_infobox["Coordinates"] = _filter_infobox_coords(second_col_row)
                        continue

                    if (
                        len(first_col_row) > 45 or
                        len(second_col_row) > 45 or
                        first_col_row == second_col_row
                    ):
                        continue

                    if "Capital and largest city" in first_col_row:
                        first_col_row = "Capital and largest city"

                    if "Assembly members" in first_col_row:
                        first_col_row = "Assembly members"

                    first_col_row = (
                        first_col_row.replace("•", "")
                        .replace("  ", " ")
                        .strip()
                    )

                    second_col_row = (
                        second_col_row.replace("•", "")
                        .replace("\xa0", " ")
                        .replace("′", "")
                    )

                    first_col_row = re.sub(r"\[.*?\]", "", first_col_row)
                    first_col_row = re.sub(r"\{.*?\}", "", first_col_row)

                    if first_col_row.strip() == "":
                        continue

                    second_col_row = re.sub(r"\[.*?\]", " ", second_col_row)
                    second_col_row = re.sub(r"\{.*?\}", " ", second_col_row)

                    if second_col_row.strip() == "":
                        continue

                    second_col_row = re.sub(r"(?<!\s)\(", " (", second_col_row)
                    second_col_row = re.sub(r"\)(?!\s)", ") ", second_col_row)

                    second_col_row = (
                        second_col_row.replace("Nasdaq", " Nasdaq")
                        .replace("S&P", " S&P")
                        .replace("DJIA", " DJIA")
                        .replace("Euro", " Euro")
                        .replace("DAX", " DAX")
                    )

                    second_col_row_chars = list(second_col_row)
                    i = 1

                    while i < len(second_col_row_chars):
                        prev_char = second_col_row_chars[i - 1]
                        curr_char = second_col_row_chars[i]

                        if (
                            (
                                (prev_char.islower() and curr_char.isupper()) or
                                (
                                    prev_char.isalpha() and 
                                    curr_char.isnumeric() and
                                    prev_char != "m" and
                                    prev_char != "i"
                                )
                            )
                            and
                            (
                                i < 2 or
                                second_col_row_chars[i - 2] != " "
                            )
                        ):
                            second_col_row_chars.insert(i, " ")
                            i += 1

                        i += 1

                    second_col_row = (
                        "".join(second_col_row_chars)
                        .strip()
                        # Run replace twice to ensure that all extra spaces are removed
                        .replace("  ", " ")
                        .replace("  ", " ")
                    )

                    filtered_wiki_infobox[first_col_row] = second_col_row
                
                return {
                    "success": True,
                    "response": filtered_wiki_infobox,
                }
                
            else:
                return {
                    "success": False,
                    "response": "Failed to get Wiki Infobox results",
                }
        
        except Exception as e:
            return {
                "success": False,
                "response": f"Failed to get Wiki Infobox results ({e})",
            }
            
    def get_wiki_see_also(title: str) -> list[dict[str, str]]:
        res = req.get(
            "https://en.wikipedia.org/w/index.php",
            headers=self.headers,
            params={
                "title": title,
                "action": "raw",
            }
        )
        
        if res.status_code != 200:
            return {
                "success": False,
                "response": "Failed to get Wiki See Also results",
            }
        
        page_text = response.text
        page_text_lines = page_text.splitlines()

        see_also_items = []
        collecting = False

        for i in range(len(page_text_lines) - 1, -1, -1):
            line = page_text_lines[i].strip()

            # Start collecting after reaching '== References ==' or '== Notes =='
            if not collecting and re.match(r'^==\s*References\s*==$', line, re.IGNORECASE):
                collecting = True
                continue
            elif not collecting and re.match(r'^==\s*Notes\s*==$', line, re.IGNORECASE):
                collecting = True
                continue

            if collecting and re.match(r'^==\s*See also\s*==$', line, re.IGNORECASE):
                break

            if collecting:
                if line.startswith('{{') or line.startswith('}}'):
                    continue

                match = re.match(r'^\*\s*\[\[(.*?)\]\]', line)

                if match:
                    see_also_items.insert(0, match.group(1))

        see_also_items_data = []
        
        for i in range(len(see_also_items)):
            item = see_also_items[i]
            
            if '|' in item:
                item = item.split('|')[-1]
            
            wiki_result = get_wiki_result(item)
            
            if not wiki_result["success"]:
                see_also_items_data.append({ "title": item })
                continue
            
            see_also_items_data.append({
                "title": wiki_result["response"]["title"],
                "thumbnail": wiki_result["response"]["thumbnail"],
            })

        return see_also_items_data