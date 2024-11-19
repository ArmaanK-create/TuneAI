from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Sample song database
songs_db = [
    {"name": "Shape of You", "artist": "Ed Sheeran", "genre": "Pop"},
    {"name": "Blinding Lights", "artist": "The Weeknd", "genre": "Pop"},
    {"name": "Levitating", "artist": "Dua Lipa", "genre": "Pop"},
    {"name": "Watermelon Sugar", "artist": "Harry Styles", "genre": "Pop"},
    {"name": "Smells Like Teen Spirit", "artist": "Nirvana", "genre": "Rock"},
    {"name": "Sweet Child O' Mine", "artist": "Guns N' Roses", "genre": "Rock"},
    {"name": "Bohemian Rhapsody", "artist": "Queen", "genre": "Rock"},
]

@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json()
    song_name = data.get("song", "").lower()

    # Find the song in the database
    song = next((s for s in songs_db if s["name"].lower() == song_name), None)

    if not song:
        return jsonify({"message": "Song not found!", "recommendations": []}), 404

    # Find similar songs (same genre)
    recommendations = [s for s in songs_db if s["genre"] == song["genre"] and s["name"] != song["name"]]

    return jsonify({"message": f"Recommendations for {song['name']}:", "recommendations": recommendations}), 200

if __name__ == "__main__":
    app.run(debug=True)


