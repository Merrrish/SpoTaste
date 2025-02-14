from flask import Flask, render_template, request, redirect, session, url_for
from spotify_data.fetch_data import get_top_tracks, get_top_artists, get_recently_played_tracks, get_user_info, get_user_stats, get_followed_artists_count, get_recent_stats, get_top_genres_visual, get_user_playlists
from spotify_data.auth import get_spotify_auth_url, get_token, authenticate_spotify
from dotenv import load_dotenv
import os

load_dotenv()

secret_key = os.getenv('SECRET_KEY')

app = Flask(__name__)
app.secret_key = secret_key

@app.route('/')
def login():
    if 'token_info' in session:
        return redirect('https://spotaste-production.up.railway.app/statistics')
    return render_template('login.html')

@app.route('/auth')
def auth():
    auth_url = get_spotify_auth_url()
    return redirect(auth_url)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        print("Error: No authorization code received!")
        return "Error: No authorization code received!", 400
    try:
        token_info = get_token(code)
        if not token_info:
            print("Error: Unable to fetch token from Spotify!")
            return "Error: Unable to fetch token from Spotify!", 500
        session['token_info'] = token_info
        print("Access token received and saved in session.")
    except Exception as e:
        print(f"Error during token exchange: {e}")
        return f"Error during token exchange: {e}", 500
    print("Redirecting to /statistics")
    return redirect(url_for('statistics'))

@app.route('/statistics')
def statistics():
    sp = authenticate_spotify()
    if not sp:
        return "Error: Authentication failed", 400
    user_name, user_image_url = get_user_info()
    followed_artists_count = get_followed_artists_count()
    user_stats = get_user_stats()
    stats = get_recent_stats()
    genres = get_top_genres_visual()
    if request.args.get('fragment') == 'true':
        return render_template('partials/statistics.html', stats=stats, genres=genres)
    return render_template('layout.html', data_type='tracks', user_name=user_name, user_image_url=user_image_url, user_stats=user_stats, followed_artists_count=followed_artists_count, stats=stats, genres=genres)

@app.route('/top-artists')
def top_artists():
    sp = authenticate_spotify()
    if not sp:
        return "Error: Authentication failed", 400
    time_period = request.args.get('time_period', 'short_term')
    artists = get_top_artists(time_period)
    user_name, user_image_url = get_user_info()
    followed_artists_count = get_followed_artists_count()
    user_stats = get_user_stats()
    if request.args.get('fragment') == 'true':
        return render_template('partials/top_artists.html', artists=artists)
    return render_template('layout.html', data_type='artists', user_name=user_name, user_image_url=user_image_url, followed_artists_count=followed_artists_count, user_stats=user_stats, artists=artists, time_period=time_period)

@app.route('/top-tracks')
def toptracks():
    sp = authenticate_spotify()
    if not sp:
        return "Error: Authentication failed", 400
    time_period = request.args.get('time_period', 'short_term')
    tracks = get_top_tracks(time_period)
    user_name, user_image_url = get_user_info()
    followed_artists_count = get_followed_artists_count()
    user_stats = get_user_stats()
    if request.args.get('fragment') == 'true':
        return render_template('partials/top_tracks.html', tracks=tracks)
    return render_template('layout.html', data_type='tracks', user_name=user_name, user_image_url=user_image_url, followed_artists_count=followed_artists_count, user_stats=user_stats, tracks=tracks, time_period=time_period)

@app.route('/playlists')
def playlists():
    sp = authenticate_spotify()
    if not sp:
        return "Error: Authentication failed", 400
    playlists = get_user_playlists()
    user_name, user_image_url = get_user_info()
    followed_artists_count = get_followed_artists_count()
    user_stats = get_user_stats()
    if request.args.get('fragment') == 'true':
        return render_template('partials/playlists.html', playlists=playlists)
    return render_template('layout.html', data_type='tracks', user_name=user_name, user_image_url=user_image_url, followed_artists_count=followed_artists_count, user_stats=user_stats, playlists=playlists)

@app.route('/recentlyplayed')
def recentlyplayed():
    sp = authenticate_spotify()
    if not sp:
        return "Error: Authentication failed", 400
    tracks = get_recently_played_tracks()
    user_name, user_image_url = get_user_info()
    followed_artists_count = get_followed_artists_count()
    user_stats = get_user_stats()
    if request.args.get('fragment') == 'true':
        return render_template('partials/recentlyplayed.html', tracks=tracks)
    return render_template('layout.html', data_type='tracks', user_name=user_name, user_image_url=user_image_url, followed_artists_count=followed_artists_count, user_stats=user_stats, tracks=tracks)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
