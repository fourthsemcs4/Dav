import sqlite3
import os

DB_FILE = 'movies.db'

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create movies table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            genre TEXT NOT NULL,
            year INTEGER NOT NULL,
            director TEXT NOT NULL,
            plot TEXT NOT NULL,
            poster_url TEXT NOT NULL,
            initial_rating REAL NOT NULL
        )
    ''')

    # Create reviews table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_id INTEGER NOT NULL,
            reviewer_name TEXT NOT NULL,
            rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
            comment TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (movie_id) REFERENCES movies (id) ON DELETE CASCADE
        )
    ''')

    # Seed data if empty
    cursor.execute('SELECT COUNT(*) FROM movies')
    if cursor.fetchone()[0] == 0:
        movies_seed = [
            (
                "Inception",
                "Sci-Fi",
                2010,
                "Christopher Nolan",
                "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.",
                "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=600&auto=format&fit=crop&q=80",
                8.8
            ),
            (
                "Interstellar",
                "Sci-Fi",
                2014,
                "Christopher Nolan",
                "When Earth becomes uninhabitable, a team of explorers travels through a wormhole in space in an attempt to ensure humanity's survival.",
                "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=600&auto=format&fit=crop&q=80",
                8.7
            ),
            (
                "The Dark Knight",
                "Action",
                2008,
                "Christopher Nolan",
                "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.",
                "https://images.unsplash.com/photo-1478760329108-5c3ed9d495a0?w=600&auto=format&fit=crop&q=80",
                9.0
            ),
            (
                "Pulp Fiction",
                "Crime",
                1994,
                "Quentin Tarantino",
                "The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.",
                "https://images.unsplash.com/photo-1594909122845-11baa439b7bf?w=600&auto=format&fit=crop&q=80",
                8.9
            ),
            (
                "Spirited Away",
                "Fantasy",
                2001,
                "Hayao Miyazaki",
                "During her family's move to the suburbs, a sullen 10-year-old girl wanders into a world ruled by gods, witches, and spirits, and where humans are changed into beasts.",
                "https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?w=600&auto=format&fit=crop&q=80",
                8.6
            ),
            (
                "The Matrix",
                "Sci-Fi",
                1999,
                "Lana Wachowski, Lilly Wachowski",
                "When a beautiful stranger leads computer hacker Neo to a forbidding underworld, he discovers the shocking truth--the life he knows is the elaborate deception of an evil cyber-intelligence.",
                "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=600&auto=format&fit=crop&q=80",
                8.7
            ),
            (
                "La La Land",
                "Romance",
                2016,
                "Damien Chazelle",
                "While navigating their careers in Los Angeles, a pianist and an actress fall in love while attempting to reconcile their aspirations for the future.",
                "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=600&auto=format&fit=crop&q=80",
                8.0
            ),
            (
                "Parasite",
                "Drama",
                2019,
                "Bong Joon Ho",
                "Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan.",
                "https://images.unsplash.com/photo-1508333706533-1ab43ecb1606?w=600&auto=format&fit=crop&q=80",
                8.5
            ),
            (
                "Whiplash",
                "Drama",
                2014,
                "Damien Chazelle",
                "A promising young drummer enrolls at a cut-throat music conservatory where his dreams of greatness are mentored by an instructor who will stop at nothing to realize a student's potential.",
                "https://images.unsplash.com/photo-1511192336575-5a79af67a629?w=600&auto=format&fit=crop&q=80",
                8.5
            ),
            (
                "Spider-Man: Into the Spider-Verse",
                "Animation",
                2018,
                "Bob Persichetti",
                "Teen Miles Morales becomes the Spider-Man of his universe and must join with five spider-powered individuals from other dimensions to stop a threat for all realities.",
                "https://images.unsplash.com/photo-1635805737707-575885ab0820?w=600&auto=format&fit=crop&q=80",
                8.4
            ),
            (
                "Gladiator",
                "Action",
                2000,
                "Ridley Scott",
                "A former Roman General sets out to exact vengeance against the corrupt emperor who murdered his family and sent him into slavery.",
                "https://images.unsplash.com/photo-1558591710-4b4a1ae0f04d?w=600&auto=format&fit=crop&q=80",
                8.5
            ),
            (
                "The Shawshank Redemption",
                "Drama",
                1994,
                "Frank Darabont",
                "Over the course of several years, two convicts form a friendship, seeking consolation and, eventually, redemption through basic compassion.",
                "https://images.unsplash.com/photo-1485846234645-a62644f84728?w=600&auto=format&fit=crop&q=80",
                9.3
            ),
            (
                "The Grand Budapest Hotel",
                "Comedy",
                2014,
                "Wes Anderson",
                "A writer relates his adventures at a renowned European resort hotel between the first and second World Wars with a concierge who is wrongly framed for murder.",
                "https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?w=600&auto=format&fit=crop&q=80",
                8.1
            ),
            (
                "Forrest Gump",
                "Drama",
                1994,
                "Robert Zemeckis",
                "The history of the United States from the 1950s to the '70s unfolds from the perspective of an Alabama man with an IQ of 75, who yearns to be reunited with his childhood sweetheart.",
                "https://images.unsplash.com/photo-1440404653325-ab127d49abc1?w=600&auto=format&fit=crop&q=80",
                8.8
            ),
            (
                "Your Name",
                "Anime",
                2016,
                "Makoto Shinkai",
                "Two strangers find themselves linked in a bizarre way. When a connection is formed, will distance be the only thing to keep them apart?",
                "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=600&auto=format&fit=crop&q=80",
                8.4
            ),
            (
                "Knives Out",
                "Comedy",
                2019,
                "Rian Johnson",
                "A detective investigates the death of the patriarch of an eccentric, combative family.",
                "https://images.unsplash.com/photo-1587840171670-8bdf57865224?w=600&auto=format&fit=crop&q=80",
                7.9
            ),
            (
                "The Lion King",
                "Animation",
                1994,
                "Roger Allers",
                "Lion prince Simba and his father are targeted by his bitter uncle, who wants to ascend the throne himself.",
                "https://images.unsplash.com/photo-1546182990-dffeafbe841d?w=600&auto=format&fit=crop&q=80",
                8.5
            ),
            (
                "Avengers: Endgame",
                "Action",
                2019,
                "Anthony Russo, Joe Russo",
                "After the devastating events of Avengers: Infinity War, the universe is in ruins. With the help of remaining allies, the Avengers assemble once more in order to reverse Thanos' actions.",
                "https://images.unsplash.com/photo-1569003339405-ea396a5a8a90?w=600&auto=format&fit=crop&q=80",
                8.4
            ),
            (
                "Eternal Sunshine of the Spotless Mind",
                "Romance",
                2004,
                "Michel Gondry",
                "When their relationship turns sour, a couple undergoes a medical procedure to have each other erased from their memories.",
                "https://images.unsplash.com/photo-1518156677180-95a2893f3e9f?w=600&auto=format&fit=crop&q=80",
                8.3
            ),
            (
                "Spiderman: No Way Home",
                "Action",
                2021,
                "Jon Watts",
                "With Spider-Man's identity now revealed, Peter asks Doctor Strange for help. When a spell goes wrong, dangerous foes from other worlds start to appear.",
                "https://images.unsplash.com/photo-1608889175123-8ec330b86f84?w=600&auto=format&fit=crop&q=80",
                8.2
            )
        ]

        cursor.executemany('''
            INSERT INTO movies (title, genre, year, director, plot, poster_url, initial_rating)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', movies_seed)

        # Seed some initial reviews for a few movies to make it lively
        initial_reviews = [
            (1, "Alice Smith", 5, "An absolute masterpiece of cinema. The storytelling, acting, and music are mind-blowing!"),
            (1, "Bob Jones", 4, "A bit complex but highly original. Visually spectacular."),
            (2, "Charlie Brown", 5, "No other movie makes me cry like this one. The sound design and space visuals are majestic."),
            (3, "Dana Scully", 5, "Heath Ledger gave the performance of a lifetime. The best superhero movie ever made."),
            (7, "Emma Watson", 4, "A beautiful love letter to Hollywood. Fantastic musical numbers and performances.")
        ]
        cursor.executemany('''
            INSERT INTO reviews (movie_id, reviewer_name, rating, comment)
            VALUES (?, ?, ?, ?)
        ''', initial_reviews)

        conn.commit()

    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully with seeded movie data.")
