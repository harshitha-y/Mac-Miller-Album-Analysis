import os
import time
import base64
import json
import re
from dotenv import load_dotenv
from requests import get, post, HTTPError
import lyricsgenius
from langdetect import detect, LangDetectException

# Load environment variables from a .env file
load_dotenv()

# Spotify Credentials
SPOTIFY_CLIENT_ID = os.getenv("CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# Genius Credentials
GENIUS_API_TOKEN = os.getenv("GENIUS_API_TOKEN")

# Initialize the Genius API client with a longer timeout
genius = lyricsgenius.Genius(GENIUS_API_TOKEN, 
                             remove_section_headers=False, # Keep [Chorus], etc.
                             skip_non_songs=True, 
                             excluded_terms=["(Remix)", "(Live)"],
                             verbose=False,
                             timeout=15) # Increased timeout for slow pages

def get_spotify_token():
    """Obtains an access token from the Spotify API."""
    auth_string = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    url = "https://accounts.spotify.com/api/token"
    headers = {"Authorization": "Basic " + auth_base64}
    data = {"grant_type": "client_credentials"}
    
    try:
        result = post(url, headers=headers, data=data)
        result.raise_for_status()
        return result.json().get("access_token")
    except HTTPError as http_err:
        print(f"Spotify HTTP error (token): {http_err}")
    return None

def search_for_artist(token, artist_name):
    """Searches for an artist on Spotify to get their ID."""
    url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": artist_name, "type": "artist", "limit": 1}

    try:
        result = get(url, headers=headers, params=params)
        result.raise_for_status()
        artists = result.json().get("artists", {}).get("items", [])
        return artists[0] if artists else None
    except HTTPError as http_err:
        print(f"Spotify HTTP error (artist search): {http_err}")
    return None

def get_artist_albums(token, artist_id):
    """Gets all official albums for a given artist from Spotify."""
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"include_groups": "album", "limit": 50}
    
    try:
        result = get(url, headers=headers, params=params)
        result.raise_for_status()
        return result.json().get("items", [])
    except HTTPError as http_err:
        print(f"Spotify HTTP error (albums): {http_err}")
    return []

def get_album_tracks(token, album_id):
    """Gets all tracks for a given album from Spotify."""
    url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"limit": 50}
    
    try:
        result = get(url, headers=headers, params=params)
        result.raise_for_status()
        return result.json().get("items", [])
    except HTTPError as http_err:
        print(f"Spotify HTTP error (tracks): {http_err}")
    return []

def get_lyrics(artist_name, track_title):
    """
    Fetches lyrics using the lyricsgenius library and performs initial cleaning.
    Includes a retry mechanism for robustness.
    """
    for attempt in range(2): # Try up to 2 times
        try:
            song = genius.search_song(track_title, artist_name)
            if song and song.lyrics:
                raw_lyrics = song.lyrics
                #remove metadata
                start_pos = raw_lyrics.find('[')
                
                if start_pos != -1:
                    # If a bracket is found, take everything from that point onward
                    lyrics_body = raw_lyrics[start_pos:]
                    return lyrics_body.strip()
                else:
                    # If no brackets are found, it might be a poem or malformed.
                    # remove the common "Lyrics" header.
                    lyrics_body = re.sub(r'^.*Lyrics', '', raw_lyrics, flags=re.IGNORECASE | re.DOTALL).strip()
                    return lyrics_body
            
            return "Lyrics not found."
        except Exception as e:
            print(f"  -> Attempt {attempt + 1} failed for '{track_title}': {e}")
            time.sleep(1) # Wait a second before retrying
    
    return "Error fetching lyrics after multiple attempts."


def detect_language(text):
    """Detects the language of a given text."""
    try:
        if not text or len(text.split()) < 5: # Check for very short/empty strings
            return "unknown"
        return detect(text)
    except LangDetectException:
        return "unknown"

# --- Main execution ---
if __name__ == "__main__":
    all_tracks_data = []
    ARTIST_NAME_TO_SEARCH = "Mac Miller"
    
    spotify_token = get_spotify_token()
    if spotify_token:
        artist = search_for_artist(spotify_token, ARTIST_NAME_TO_SEARCH)
        
        if artist:
            print(f"Found artist: {artist['name']} (Spotify ID: {artist['id']})")
            albums = get_artist_albums(spotify_token, artist['id'])
            
            target_album_name = "Swimming"
            target_album = next((a for a in albums if a['name'] == target_album_name), None)

            if target_album:
                print(f"--- Processing Album: {target_album['name']} ---")
                tracks = get_album_tracks(spotify_token, target_album['id'])
                
                if tracks:
                    for track in tracks:
                        track_name = track['name']
                        print(f"Fetching data for track: {track_name}...")
                        
                        lyrics = get_lyrics(artist['name'], track_name)
                        
                        language = detect_language(lyrics)
                        if language != 'en' and language != 'unknown':
                            print(f"  -> Warning: Detected language is '{language}' for track '{track_name}'")

                        all_tracks_data.append({
                            'artist': artist['name'],
                            'album': target_album['name'],
                            'track_title': track_name,
                            'lyrics': lyrics,
                            'language': language
                        })
    
    if all_tracks_data:
        jsonl_file = "Swimming.jsonl"
        
        if os.path.exists(jsonl_file):
            os.remove(jsonl_file)
            print(f"Removed existing file: {jsonl_file}")

        print(f"\nCreating new file and writing {len(all_tracks_data)} tracks to {jsonl_file}...")
        
        with open(jsonl_file, 'w', encoding='utf-8') as f:
            for record in all_tracks_data:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
            
        print("Done!")
