import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import session, redirect
from dotenv import load_dotenv
import os

# Загружаем переменные из .env
load_dotenv()

# Используем переменные из .env
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
SCOPES = os.getenv('SCOPES')

sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPES,
    show_dialog=True  # Показываем окно авторизации
)

def authenticate_spotify():
    """Возвращает объект клиента Spotify, если токен сохранен в сессии."""
    token_info = session.get('token_info')
    if token_info:
        token = token_info.get('access_token')  # Используем .get(), чтобы избежать ошибки, если токен не найден
        if token:
            return spotipy.Spotify(auth=token)
        else:
            print("Error: Access token is missing!")
    else:
        print("Error: No token info found in session!")
    return redirect('/login')  # Если токен отсутствует, перенаправляем на страницу входа

def get_spotify_auth_url():
    """Возвращает URL для аутентификации пользователя через Spotify."""
    return sp_oauth.get_authorize_url()

def get_token(code):
    """Получает токен доступа на основе кода аутентификации."""
    try:
        print(f"Attempting to get token for code: {code}")
        token_info = sp_oauth.get_access_token(code)
        print(f"Token info received: {token_info}")
        return token_info
    except Exception as e:
        print(f"Error retrieving token: {e}")
        return None
