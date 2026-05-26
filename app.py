from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3
import os
from database import get_db_connection, init_db

app = Flask(__name__, static_folder='static')
CORS(app)  # Enable CORS for external access if needed

# Initialize DB on startup
init_db()

# Serve static frontend files
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/styles.css')
def serve_styles():
    return send_from_directory(app.static_folder, 'styles.css')

@app.route('/app.js')
def serve_js():
    return send_from_directory(app.static_folder, 'app.js')


# API: Get all movies with search/genre filters and aggregated ratings
@app.route('/api/movies', methods=['GET'])
def get_movies():
    genre_filter = request.args.get('genre')
    search_filter = request.args.get('search')

    conn = get_db_connection()
    cursor = conn.cursor()

    query = '''
        SELECT m.id, m.title, m.genre, m.year, m.director, m.plot, m.poster_url, m.initial_rating,
               COALESCE(SUM(r.rating), 0) as total_user_rating,
               COUNT(r.id) as review_count
        FROM movies m
        LEFT JOIN reviews r ON m.id = r.movie_id
    '''
    
    conditions = []
    params = []
    
    if genre_filter:
        conditions.append("m.genre = ?")
        params.append(genre_filter)
        
    if search_filter:
        conditions.append("(m.title LIKE ? OR m.director LIKE ?)")
        search_like = f"%{search_filter}%"
        params.append(search_like)
        params.append(search_like)
        
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
        
    query += " GROUP BY m.id ORDER BY m.title ASC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    movies = []
    for row in rows:
        # Calculate weighted average: (initial_rating_out_of_5 + sum_of_user_ratings) / (1 + count_of_user_ratings)
        initial_rating_stars = row['initial_rating'] / 2.0
        review_count = row['review_count']
        total_user_rating = row['total_user_rating']
        
        weighted_rating = (initial_rating_stars + total_user_rating) / (1.0 + review_count)
        
        movies.append({
            'id': row['id'],
            'title': row['title'],
            'genre': row['genre'],
            'year': row['year'],
            'director': row['director'],
            'plot': row['plot'],
            'poster_url': row['poster_url'],
            'rating': round(weighted_rating, 2),
            'review_count': review_count
        })
        
    conn.close()
    return jsonify(movies)

# API: Get a single movie and its reviews
@app.route('/api/movies/<int:movie_id>', methods=['GET'])
def get_movie_detail(movie_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get movie details
    cursor.execute('''
        SELECT m.id, m.title, m.genre, m.year, m.director, m.plot, m.poster_url, m.initial_rating,
               COALESCE(SUM(r.rating), 0) as total_user_rating,
               COUNT(r.id) as review_count
        FROM movies m
        LEFT JOIN reviews r ON m.id = r.movie_id
        WHERE m.id = ?
        GROUP BY m.id
    ''', (movie_id,))
    
    movie_row = cursor.fetchone()
    if not movie_row:
        conn.close()
        return jsonify({'error': 'Movie not found'}), 404
        
    # Get reviews for this movie
    cursor.execute('''
        SELECT id, reviewer_name, rating, comment, created_at
        FROM reviews
        WHERE movie_id = ?
        ORDER BY created_at DESC
    ''', (movie_id,))
    
    review_rows = cursor.fetchall()
    
    reviews = []
    for r in review_rows:
        reviews.append({
            'id': r['id'],
            'reviewer_name': r['reviewer_name'],
            'rating': r['rating'],
            'comment': r['comment'],
            'created_at': r['created_at']
        })
        
    initial_rating_stars = movie_row['initial_rating'] / 2.0
    review_count = movie_row['review_count']
    total_user_rating = movie_row['total_user_rating']
    weighted_rating = (initial_rating_stars + total_user_rating) / (1.0 + review_count)
    
    movie_detail = {
        'id': movie_row['id'],
        'title': movie_row['title'],
        'genre': movie_row['genre'],
        'year': movie_row['year'],
        'director': movie_row['director'],
        'plot': movie_row['plot'],
        'poster_url': movie_row['poster_url'],
        'rating': round(weighted_rating, 2),
        'review_count': review_count,
        'reviews': reviews
    }
    
    conn.close()
    return jsonify(movie_detail)

# API: Post a review for a movie
@app.route('/api/movies/<int:movie_id>/reviews', methods=['POST'])
def add_review(movie_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body is empty'}), 400
        
    reviewer_name = data.get('reviewer_name', '').strip()
    rating_val = data.get('rating')
    comment = data.get('comment', '').strip()
    
    if not reviewer_name:
        return jsonify({'error': 'Reviewer name is required'}), 400
    if rating_val is None or not isinstance(rating_val, int) or rating_val < 1 or rating_val > 5:
        return jsonify({'error': 'Rating must be an integer between 1 and 5'}), 400
    if not comment:
        return jsonify({'error': 'Comment is required'}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Verify movie exists
    cursor.execute('SELECT id FROM movies WHERE id = ?', (movie_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Movie not found'}), 404
        
    # Insert review
    cursor.execute('''
        INSERT INTO reviews (movie_id, reviewer_name, rating, comment)
        VALUES (?, ?, ?, ?)
    ''', (movie_id, reviewer_name, rating_val, comment))
    
    conn.commit()
    
    # Recalculate rating to return updated state
    cursor.execute('''
        SELECT m.initial_rating, COALESCE(SUM(r.rating), 0) as total_user_rating, COUNT(r.id) as review_count
        FROM movies m
        LEFT JOIN reviews r ON m.id = r.movie_id
        WHERE m.id = ?
        GROUP BY m.id
    ''', (movie_id,))
    
    row = cursor.fetchone()
    
    initial_rating_stars = row['initial_rating'] / 2.0
    review_count = row['review_count']
    total_user_rating = row['total_user_rating']
    weighted_rating = (initial_rating_stars + total_user_rating) / (1.0 + review_count)
    
    conn.close()
    
    return jsonify({
        'message': 'Review added successfully',
        'updated_rating': round(weighted_rating, 2),
        'review_count': review_count
    }), 201

# API: Get list of unique genres
@app.route('/api/genres', methods=['GET'])
def get_genres():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT genre FROM movies ORDER BY genre ASC')
    genres = [row['genre'] for row in cursor.fetchall()]
    conn.close()
    return jsonify(genres)

# API: Get overall statistics
@app.route('/api/stats', methods=['GET'])
def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total movies
    cursor.execute('SELECT COUNT(*) FROM movies')
    total_movies = cursor.fetchone()[0]
    
    # Total reviews
    cursor.execute('SELECT COUNT(*) FROM reviews')
    total_reviews = cursor.fetchone()[0]
    
    # Overall average rating from reviews (out of 5 stars)
    cursor.execute('SELECT AVG(rating) FROM reviews')
    avg_row = cursor.fetchone()[0]
    global_avg_rating = round(avg_row, 2) if avg_row else 0.0
    
    # Highest rated movie (based on our weighted average formula)
    cursor.execute('''
        SELECT m.id, m.title, m.initial_rating,
               COALESCE(SUM(r.rating), 0) as total_user_rating,
               COUNT(r.id) as review_count
        FROM movies m
        LEFT JOIN reviews r ON m.id = r.movie_id
        GROUP BY m.id
    ''')
    rows = cursor.fetchall()
    
    highest_rated_title = "N/A"
    highest_rated_id = None
    highest_rating = -1.0
    
    for row in rows:
        initial_rating_stars = row['initial_rating'] / 2.0
        review_count = row['review_count']
        total_user_rating = row['total_user_rating']
        weighted_rating = (initial_rating_stars + total_user_rating) / (1.0 + review_count)
        
        if weighted_rating > highest_rating:
            highest_rating = weighted_rating
            highest_rated_title = row['title']
            highest_rated_id = row['id']
            
    conn.close()
    
    return jsonify({
        'total_movies': total_movies,
        'total_reviews': total_reviews,
        'global_avg_rating': global_avg_rating,
        'highest_rated_movie': f"{highest_rated_title} ({round(highest_rating, 2)} ★)" if total_movies > 0 else "N/A",
        'highest_rated_id': highest_rated_id
    })




if __name__ == '__main__':
    # Make sure static directory exists
    os.makedirs('static', exist_ok=True)
    app.run(debug=True, port=5000)
