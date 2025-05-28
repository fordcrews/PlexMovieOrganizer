# plex_movie_organizer.py
# Rebuilds the script to organize and rename movie files based on Plex metadata.

from plexapi.server import PlexServer
import os
import shutil
from pathlib import Path
import re

# CONFIGURE THESE
PLEX_URL = 'http://localhost:32400'
PLEX_TOKEN = 'YOUR_PLEX_TOKEN'
MOVIE_LIBRARY_NAME = 'Movies'
DESTINATION_ROOT = '/mnt/media/movies'  # Final destination folder
LEFTOVER_DIR = '/mnt/media/leftovers'  # For orphaned junk

# Ensure destination and leftovers exist
os.makedirs(DESTINATION_ROOT, exist_ok=True)
os.makedirs(LEFTOVER_DIR, exist_ok=True)

# Connect to Plex
plex = PlexServer(PLEX_URL, PLEX_TOKEN)
movie_library = plex.library.section(MOVIE_LIBRARY_NAME)

def safe_filename(name):
    return re.sub(r'[\\/:*?"<>|]', '', name)

for movie in movie_library.all():
    try:
        if not movie.locations:
            continue

        file_path = Path(movie.locations[0])
        if not file_path.exists():
            continue

        title = safe_filename(movie.title)
        year = movie.year if movie.year else '0000'
        ext = file_path.suffix

        dest_dir = Path(DESTINATION_ROOT) / f"{title} ({year})"
        dest_dir.mkdir(parents=True, exist_ok=True)

        dest_path = dest_dir / f"{title} ({year}){ext}"
        print(f"Moving {file_path} -> {dest_path}")
        
        shutil.move(str(file_path), str(dest_path))

        # Clean up original folder if empty
        if file_path.parent != dest_dir and not any(file_path.parent.iterdir()):
            shutil.move(str(file_path.parent), LEFTOVER_DIR)

    except Exception as e:
        print(f"Failed on {movie.title}: {e}")
# PlexMovieOrganizer
