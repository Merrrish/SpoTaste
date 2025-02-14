import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import session, redirect
from dotenv import load_dotenv
import os
from collections import Counter
from datetime import datetime, timedelta

load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
SCOPES = os.getenv('SCOPES')

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID, 
                                               client_secret=CLIENT_SECRET, 
                                               redirect_uri=REDIRECT_URI, 
                                               scope=SCOPES))

def get_user_info():
    """Получаем информацию о пользователе (имя и изображение профиля)."""
    user_info = sp.current_user()
    user_name = user_info['display_name']  # Имя пользователя
    user_image_url = user_info['images'][0]['url'] if user_info['images'] else None  # Ссылка на изображение профиля
    return user_name, user_image_url

def get_user_stats():
    """
    Возвращает информацию о пользователе:
    - количество подписчиков
    - количество подписок
    - количество плейлистов
    """
    user_profile = sp.current_user()  # Получаем профиль пользователя
    playlists = sp.current_user_playlists()  # Получаем плейлисты пользователя

    followers = user_profile.get('followers', {}).get('total', 0)  # Подписчики
    playlists_count = playlists['total']  # Количество плейлистов

    # Spotify API не предоставляет прямых данных о подписках, поэтому укажем "N/A"
    subscriptions = "N/A"

    return {
        "followers": followers,
        "subscriptions": subscriptions,
        "playlists": playlists_count
    }

def get_followed_artists_count():
    """
    Возвращает количество артистов, на которых подписан пользователь.
    """
    response = sp.current_user_followed_artists(limit=1)  # Запрос только одного артиста
    total_count = response.get('artists', {}).get('total', 0)  # Общее количество подписок
    return total_count

def get_top_tracks(time_period):
    top_tracks = sp.current_user_top_tracks(time_range=time_period, limit=10)
    track_info = []
    for track in top_tracks['items']:
        track_info.append({
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'cover': track['album']['images'][0]['url'] if track['album']['images'] else None,
            'duration': f"{track['duration_ms'] // 60000}:{(track['duration_ms'] // 1000) % 60:02}"
        })
    return track_info


def get_top_artists(time_period):
    """
    Получает топ-артистов пользователя через Spotify API.

    :param time_period: Период времени (short_term, medium_term, long_term).
    :return: Список данных об артистах.
    """
    top_artists = sp.current_user_top_artists(time_range=time_period, limit=10)
    artist_info = []
    for artist in top_artists['items']:
        artist_info.append({
            'name': artist['name'],
            'image': artist['images'][0]['url'] if artist['images'] else None
        })
    return artist_info



def get_top_genres_visual(time_period="long_term"):
    """
    Получает топ жанров пользователя за указанный период.
    Возвращает список жанров и их частот.
    """
    if time_period not in ["short_term", "medium_term", "long_term"]:
        time_period = "long_term"  # Используем long_term как стандартный
    
    top_artists = sp.current_user_top_artists(time_range=time_period, limit=50)
    
    # Собираем жанры
    genres = []
    for artist in top_artists['items']:
        genres.extend(artist['genres'])
    
    # Подсчет популярности жанров
    genre_count = Counter(genres)
    top_genres = genre_count.most_common(5)
    
    return top_genres

def get_recently_played_tracks(limit=10):
    # Получаем последние прослушанные треки
    results = sp.current_user_recently_played(limit=limit)
    tracks = []
    for item in results['items']:
        track_name = item['track']['name']
        artist_name = item['track']['artists'][0]['name']
        duration_ms = item['track']['duration_ms']  # Длительность в миллисекундах
        duration = str(int(duration_ms / 60000)) + ":" + str(int((duration_ms % 60000) / 1000)).zfill(2)
        cover_url = item['track']['album']['images'][0]['url']  # Обложка трека
        tracks.append({
            'track_name': track_name,
            'artist_name': artist_name,
            'duration': duration,
            'cover_url': cover_url
        })
    
    return tracks

def get_recent_stats():
    """
    Получает статистику прослушивания за последние 24 часа и 7 дней:
    - Количество треков
    - Количество минут
    """
    now = datetime.utcnow()
    last_24_hours = now - timedelta(hours=24)
    last_7_days = now - timedelta(days=7)
    
    results = sp.current_user_recently_played(limit=50)  # Получаем максимум 50 треков
    tracks_24h = 0
    minutes_24h = 0
    tracks_7d = 0
    minutes_7d = 0

    for item in results['items']:
        # Попробуем сначала с миллисекундами, если не получится - без них
        try:
            played_at = datetime.strptime(item['played_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            played_at = datetime.strptime(item['played_at'], "%Y-%m-%dT%H:%M:%SZ")
        
        track_duration_ms = item['track']['duration_ms']

        # Треки и время за последние 24 часа
        if played_at > last_24_hours:
            tracks_24h += 1
            minutes_24h += track_duration_ms / 60000  # Переводим миллисекунды в минуты

        # Треки и время за последние 7 дней
        if played_at > last_7_days:
            tracks_7d += 1
            minutes_7d += track_duration_ms / 60000  # Переводим миллисекунды в минуты

    return {
        "tracks_24h": tracks_24h,
        "minutes_24h": round(minutes_24h, 2),
        "tracks_7d": tracks_7d,
        "minutes_7d": round(minutes_7d, 2),
    }

    
def get_user_playlists():
    """
    Получает плейлисты пользователя через Spotify API.
    :return: Список данных о плейлистах.
    """
    playlists = sp.current_user_playlists(limit=10)
    playlist_info = []
    for playlist in playlists['items']:
        playlist_info.append({
            'name': playlist['name'],
            'image': playlist['images'][0]['url'] if playlist['images'] else None,
            'track_count': playlist['tracks']['total']
        })
    return playlist_info

def get_total_listening_time(tracks):
    """Вычисляет общее время прослушивания в минутах."""
    total_time_ms = sum(track['duration_ms'] for track in tracks)
    total_time_minutes = total_time_ms / 1000 / 60  # Переводим миллисекунды в минуты
    return total_time_minutes
