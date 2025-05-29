import os
import json
import re
from plexapi.server import PlexServer

# Plex config (replace with your actual values or set via environment variables)
PLEX_URL = os.environ.get("PLEX_URL", "http://localhost:32400")
PLEX_TOKEN = os.environ.get("PLEX_TOKEN", "your_plex_token_here")
LIBRARY_NAME = os.environ.get("PLEX_LIBRARY", "Movies")

plex = PlexServer(PLEX_URL, PLEX_TOKEN)
movies = plex.library.section(LIBRARY_NAME).all()

movie_data = []

def guess_resolution(filename):
    match = re.search(r'(\d{3,4}p)', filename, re.IGNORECASE)
    return match.group(1).upper() if match else ""

def guess_source(filename):
    sources = ['WEBRip', 'WEBDL', 'BluRay', 'HDRip', 'HDTV', 'DVDRip']
    for source in sources:
        if source.lower() in filename.lower():
            return source
    return "Unknown"

for movie in movies:
    try:
        media = movie.media[0]
        part = media.parts[0]
        file_path = part.file
        folder = os.path.dirname(file_path)
        filename = os.path.basename(file_path)

        resolution = guess_resolution(filename)
        source = guess_source(filename)
        video_codec = getattr(media, 'videoCodec', "")
        container = getattr(media, 'container', "")
        year = movie.year or ""
        imdb_id = movie.guid.split("://")[-1].split("?")[0] if "imdb" in movie.guid else ""

        clean_title = re.sub(r'[\\/*?:"<>|]', '', movie.title).strip()
        new_folder = f"{clean_title} ({year})"
        new_filename = f"{clean_title} ({year}) {source}-{resolution}.{container}"

        movie_entry = {
            "title": movie.title,
            "year": year,
            "imdb_id": imdb_id,
            "current_path": file_path,
            "current_folder": os.path.basename(folder),
            "suggested_folder": new_folder,
            "suggested_filename": new_filename,
            "video_codec": video_codec,
            "container": container,
            "resolution": resolution,
            "source": source,
            "status": "rename"  # default action
        }

        movie_data.append(movie_entry)

    except Exception as e:
        print(f"Failed to process movie: {movie.title}. Error: {e}")

# Save JSON to file
with open("plex_movie_index.json", "w", encoding="utf-8") as f:
    json.dump(movie_data, f, indent=2)

print("Index generated in plex_movie_index.json")
