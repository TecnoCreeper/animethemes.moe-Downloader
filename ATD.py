# animethemes.moe CLI downloader
# Download modes: - video(with audio) - only audio
# API: https://api-docs.animethemes.moe/

import os
import requests
import sys


# ===== SEARCH QUERY ===== #

def search_query() -> tuple[list[str], dict] :
    print("Anime to search: ")
    userInput = input()
    userInput.strip("")
    userInput.strip("\n")
    matching_anime = []
    response = requests.get(f"https://api.animethemes.moe/search?q={userInput}").json()
    i = len(response["search"]["anime"])
    if i == 0:
        print("ERROR: anime not found")
        sys.exit()
    for index in range(i):
        anime_name = response["search"]["anime"][index]["name"]
        matching_anime.append(anime_name)

    return matching_anime, response

# ===== ===== #



# ===== TRANSFORM MATCHING ANIME LIST IN DICTIONARY ===== #

def get_matching_anime(matching_anime: list) -> dict:
    n = len(matching_anime)
    indexes = [x for x in range(1, n + 1)]
    matching_anime_indexed = dict.fromkeys(indexes, "")
    i = 0
    for item in matching_anime:
        i = i + 1
        matching_anime_indexed.update({i: item})

    return matching_anime_indexed

# ===== ===== #



# ===== MAKE USER CHOOSE ANIME ===== #

def display_anime(matching_anime_indexed: dict, json_response) -> int:
    user_input = None
    while user_input not in matching_anime_indexed.keys():
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Choose the anime (type number):")
        for number, anime_name in matching_anime_indexed.items():
            print(f"{number} - {anime_name}")
        try:
            user_input = int(input())
        except ValueError:
            pass
    
    slug = json_response["search"]["anime"][user_input - 1].get("slug")
    
    return slug


# ===== ===== #



# ===== GET ALL OP / ED WITH ASSOCIATED LINK ===== #

def get_entries(slug: int) -> dict:
    response = requests.get(f"https://api.animethemes.moe/anime/{slug}?include=animethemes.animethemeentries.videos.audio").json()
    raw_entries = []
    for item in response["anime"]["animethemes"]:
        name = item["animethemeentries"][0]["videos"][0].get("filename")
        video_link = item["animethemeentries"][0]["videos"][0].get("link")
        audio_link = item["animethemeentries"][0]["videos"][0]["audio"].get("link")
        temp_list = []
        temp_list.clear()
        temp_list.append(name)
        temp_list.append(video_link)
        temp_list.append(audio_link)
        name_link_tuple = tuple(temp_list)
        raw_entries.append(name_link_tuple)

    entries = tranform_entries(raw_entries)
    
    return entries


# ===== ===== #



# ===== TRANFORM LISTS OF TUPLES raw_entries TO DICTIONARY ===== #

def tranform_entries(raw_entries):
    n = len(raw_entries)
    indexes = [x for x in range(1, n + 1)]
    entries = dict.fromkeys(indexes, {})
    i = 0
    for item in raw_entries:
        i = i + 1
        entries.update({i: {}}) # if i remove this line it stops working and i don't know why -_-
        entries[i].update({"name": item[0]})
        entries[i].update({"video-link": item[1]})
        entries[i].update({"audio-link": item[2]})
    
    return entries

# ===== ===== #



# ===== DISPLAY ===== #
def display_videos(videos):
    user_input = None
    while user_input not in videos.keys():
        os.system('cls' if os.name == 'nt' else 'clear')
        for number, value in videos.items():
            print(f"{number} -")
            for name, link in value.items():
                print(f"{name}: {link}")
            print("=====")
        
        print("Enter which entry you want to download (number):")
        try:
            user_input = int(input())
        except ValueError:
            pass

    video_audio_choice = None
    while video_audio_choice not in (1, 2):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("1 - Video\n2 - Only audio")
        try:
            video_audio_choice = int(input())
        except ValueError:
            pass
    
    if video_audio_choice == 1:
        link_to_download = videos[user_input].get("video-link")
    elif video_audio_choice == 2:
        link_to_download = videos[user_input].get("audio-link")
    

    file_name = videos[user_input].get("name")
    
    return link_to_download, file_name
# ===== ===== #



# ===== DOWNLOAD ===== #

def downloader(link, name):
    extension = link.split(".")[-1]
    r = requests.get(link, stream=True)
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Downloading...")

    with open(f"{name}.{extension}", "wb") as f:
        for chunk in r.iter_content(chunk_size = 1024 * 1024):
            if chunk:
                f.write(chunk)
    
    print("Finished download")

# ===== ===== #



def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    matching_anime, json_response= search_query()
    matching_anime_indexed = get_matching_anime(matching_anime)
    slug = display_anime(matching_anime_indexed, json_response)
    entries = get_entries(slug)
    link_to_download, file_name = display_videos(entries)
    downloader(link_to_download, file_name)

def dev():
    pass

if __name__ == "__main__":
    main()