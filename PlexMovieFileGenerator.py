import os
import json
from plexapi.server import PlexServer

# Plex config (replace with your actual values or set via environment variables)
PLEX_URL = os.environ.get("PLEX_URL", "http://localhost:32400")
PLEX_TOKEN = os.environ.get("PLEX_TOKEN", "your_plex_token_here")
LIBRARY_NAME = os.environ.get("PLEX_LIBRARY", "Movies")

plex = PlexServer(PLEX_URL, PLEX_TOKEN)
movies = plex.library.section(LIBRARY_NAME).all()

movie_data = []

for movie in movies:
    try:
        media = movie.media[0]
        part = media.parts[0]
        file_path = part.file
        folder = os.path.dirname(file_path)
        filename = os.path.basename(file_path)

        resolution = media.videoResolution or ""
        source = media.videoSource or ""
        video_codec = media.videoCodec or ""
        container = media.container or ""
        year = movie.year or ""
        imdb_id = movie.guid.split("://")[-1].split("?")[0] if "imdb" in movie.guid else ""

        new_folder = f"{movie.title} ({year})"
        new_filename = f"{movie.title} ({year}) {source}-{resolution}.{container}"

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
