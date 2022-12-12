""" animethemes.moe CLI downloader

Download modes: - video(with audio) - only audio
API: https://api-docs.animethemes.moe/
"""

import os
import sys
import requests

REQUEST_TIMEOUT = 60


def search_query() -> dict[int, dict[str, str]]:
    """Receive user input;  return the corresponding search results, and the full response."""
    print("Anime to search: ")
    user_input = input()
    response = requests.get(
        f"https://api.animethemes.moe/search?q={user_input}", timeout=REQUEST_TIMEOUT
    ).json()
    matching_anime = {
        i: {key: entry[key] for key in ("name", "slug")}
        for i, entry in enumerate(response["search"]["anime"])
    }
    if not matching_anime:
        print("ERROR: anime not found")
        sys.exit()
    return matching_anime


def display_anime(matching_anime_indexed: dict[int, dict[str, str]]) -> str:
    """Receive user input to select an entry from the search results; return its URL slug."""
    user_input = None
    while user_input not in matching_anime_indexed.keys():
        os.system("cls" if os.name == "nt" else "clear")
        print("Choose the anime (type number):")
        for number, anime in matching_anime_indexed.items():
            print(f"{number} - {anime['name']}")
        try:
            user_input = int(input())
        except ValueError:
            pass
    slug = matching_anime_indexed[user_input]["slug"]
    return slug


# ===== GET ALL OP / ED WITH ASSOCIATED LINK ===== #
def get_entries(slug: int) -> dict:
    response = requests.get(
        f"https://api.animethemes.moe/anime/{slug}?include=animethemes.animethemeentries.videos.audio"
    ).json()
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
        entries.update(
            {i: {}}
        )  # if i remove this line it stops working and i don't know why -_-
        entries[i].update({"name": item[0]})
        entries[i].update({"video-link": item[1]})
        entries[i].update({"audio-link": item[2]})

    return entries


# ===== ===== #


# ===== DISPLAY ===== #
def display_videos(videos):
    user_input = None
    while user_input not in videos.keys():
        os.system("cls" if os.name == "nt" else "clear")
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
        os.system("cls" if os.name == "nt" else "clear")
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
    os.system("cls" if os.name == "nt" else "clear")
    print("Downloading...")

    with open(f"{name}.{extension}", "wb") as f:
        for chunk in r.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)

    print("Finished download")


# ===== ===== #


def main():
    os.system("cls" if os.name == "nt" else "clear")
    matching_anime = search_query()
    slug = display_anime(matching_anime)
    entries = get_entries(slug)
    link_to_download, file_name = display_videos(entries)
    downloader(link_to_download, file_name)


def dev():
    pass


if __name__ == "__main__":
    main()
