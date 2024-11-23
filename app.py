from flask import Flask, request, redirect, session, url_for, jsonify, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)
app.secret_key = "571315fdf3b14eb29f4db416a6c0f288"  
app.config['SESSION_COOKIE_NAME'] = 'TuneAI Cookie'

SPOTIPY_CLIENT_ID = "f7a4c65ebaa948ac9b95ba20bbc172f6"
SPOTIPY_CLIENT_SECRET = "571315fdf3b14eb29f4db416a6c0f288"
SPOTIPY_REDIRECT_URI = "http://127.0.0.1:5000/callback"


sp_oauth = SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope="user-library-read user-top-read"
)


def get_token():
    token_info = session.get('token_info', None)
    if not token_info:
        print("No token info found in session.")
        return None


    if sp_oauth.is_token_expired(token_info):
        print("Access token expired. Refreshing...")
        try:
            token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
            session['token_info'] = token_info  
            print("New token acquired:", token_info['access_token'])
        except Exception as e:
            print("Failed to refresh token:", e)
            return None

    return token_info['access_token']

# Routes
@app.route('/')
def index():
    return render_template('index.html') 

@app.route('/login')
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url) 

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        print("Authorization code missing in callback.")
        return jsonify({"error": "Authorization code missing"}), 400

    try:
        token_info = sp_oauth.get_access_token(code)
        print("Token Info from Spotify:", token_info)  # Debug
        if not token_info:
            print("Token Info is None.")
            return jsonify({"error": "Failed to fetch token info from Spotify"}), 500

        session['token_info'] = token_info  
        print("Session Contents after setting token_info in /callback:", dict(session))  # Debug
    except Exception as e:
        print(f"Exception during token exchange: {e}")
        return jsonify({"error": "Failed to fetch token."}), 500

    return redirect(url_for('recommend_ui'))


@app.route('/recommend-ui')
def recommend_ui():
    return render_template('recommend.html')  

@app.route('/recommend', methods=['POST'])
def recommend():
    access_token = get_token()
    if not access_token:
        return jsonify({"error": "Not authenticated. Please log in again."}), 401

    sp = spotipy.Spotify(auth=access_token)

   
    data = request.get_json()
    song_name = data.get('song')

    if not song_name:
        return jsonify({"error": "No song provided."}), 400

    # Search for the song on Spotify
    results = sp.search(q=song_name, type='track', limit=1)
    if not results['tracks']['items']:
        return jsonify({"error": "Song not found on Spotify."}), 404

    seed_track = results['tracks']['items'][0]['id']

    # Get recommendations based on the seed track
    recommendations = sp.recommendations(seed_tracks=[seed_track], limit=10)

    recommended_tracks = [
        {"name": track['name'], "artist": track['artists'][0]['name']}
        for track in recommendations['tracks']
    ]
    return jsonify({"recommendations": recommended_tracks}), 200

# Main execution
if __name__ == "__main__":
    app.run(debug=True)

