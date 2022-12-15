"""animethemes.moe CLI downloader

Download modes: - video(with audio) - only audio
API: https://api-docs.animethemes.moe/
"""

import os
import sys
import requests

REQUEST_TIMEOUT = 60
CHUNK_SIZE = 1024 * 1024


def search_query() -> dict[int, dict[str, str]]:
    """Receive user input;  return the corresponding search results, and the full response."""
    print("==========\nAnime to search:\n")
    user_input = input()
    response = requests.get(
        f"https://api.animethemes.moe/search?q={user_input}", timeout=REQUEST_TIMEOUT
    ).json()
    matching_anime = {
        i: {key: entry[key] for key in ("name", "slug")}
        for i, entry in enumerate(response["search"]["anime"], start=1)
    }
    if not matching_anime:
        print("==========\nERROR: anime not found")
        sys.exit()
    return matching_anime


def display_anime(matching_anime_indexed: dict[int, dict[str, str]]) -> str:
    """Receive user input to select an entry from the search results; return its URL slug."""
    user_input = None
    while user_input not in matching_anime_indexed.keys():
        os.system("cls" if os.name == "nt" else "clear")
        print("==========\nChoose the anime:\n")
        for number, anime in matching_anime_indexed.items():
            print(f"{number} - {anime['name']}")
        print("")
        try:
            user_input = int(input())
        except ValueError:
            pass

    slug = matching_anime_indexed[user_input]["slug"]
    return slug


def get_entries(slug: str) -> dict:
    """Return the OPs/EDs associated to the given URL slug."""
    # Currently, only return one version of each OP/ED (the highest quality available?)
    response = requests.get(
        f"https://api.animethemes.moe/anime/{slug}?include=animethemes.animethemeentries.videos.audio",
        timeout=REQUEST_TIMEOUT,
    ).json()
    entries = {
        i: {
            "name": entry["animethemeentries"][0]["videos"][0]["filename"],
            "video-link": entry["animethemeentries"][0]["videos"][0]["link"],
            "audio-link": entry["animethemeentries"][0]["videos"][0]["audio"]["link"],
        }
        for i, entry in enumerate(response["anime"]["animethemes"], start=1)
    }
    return entries


def display_videos(videos: dict[int, dict[str, str]]) -> tuple[str, str]:
    """Receive user input to select an entry and choose between video and audio; return the URL."""
    user_input = None
    while user_input not in videos.keys():
        os.system("cls" if os.name == "nt" else "clear")
        print("==========")
        for number, entry in videos.items():
            print(f"{number} - {entry['name']}")
            for name, link in entry.items():
                if name != "name":
                    print(f"{name}: {link}")
            print("")
        print("\nEnter which entry you want to download:\n")
        try:
            user_input = int(input())
        except ValueError:
            pass

    file_name = videos[user_input].get("name")
    video_audio_choice = None
    while video_audio_choice not in (1, 2):
        os.system("cls" if os.name == "nt" else "clear")
        print(f"==========\n{file_name}\n")
        print("1 - Video\n2 - Only audio\n")
        try:
            video_audio_choice = int(input())
        except ValueError:
            pass

    link_to_download = videos[user_input][
        "video-link" if video_audio_choice == 1 else "audio-link"
    ]

    return link_to_download, file_name


def downloader(link: str, name: str) -> None:
    """Download the selected link."""
    extension = link.split(".")[-1]
    response = requests.get(link, stream=True, timeout=REQUEST_TIMEOUT)
    os.system("cls" if os.name == "nt" else "clear")
    total_length = int(response.headers.get("content-length"))
    downloaded = 0
    with open(f"{name}.{extension}", "wb") as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                done = downloaded / total_length
                sys.stdout.write(f"\rDownloading... {done:>7.2%}")

    print("\nDownload completed!")


def main() -> None:
    """Run the CLI."""
    os.system("cls" if os.name == "nt" else "clear")
    matching_anime = search_query()
    slug = display_anime(matching_anime)
    entries = get_entries(slug)
    link_to_download, file_name = display_videos(entries)
    downloader(link_to_download, file_name)


if __name__ == "__main__":
    main()
