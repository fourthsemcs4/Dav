// App State
let moviesState = [];
let selectedMovieId = null;
let currentGenre = "";
let currentSearch = "";
let searchTimeout = null;

// DOM Elements
const elements = {
    movieGrid: document.getElementById('movie-grid-container'),
    searchInput: document.getElementById('search-input'),
    clearSearchBtn: document.getElementById('clear-search-btn'),
    genreTabsList: document.getElementById('genre-tabs-list'),
    catalogTitle: document.getElementById('catalog-title'),
    resultsCount: document.getElementById('results-count-text'),
    modal: document.getElementById('movie-detail-modal'),
    closeModalBtn: document.getElementById('close-modal-btn'),
    
    // Stats elements
    statMovies: document.getElementById('val-total-movies'),
    statReviews: document.getElementById('val-total-reviews'),
    statAvgRating: document.getElementById('val-avg-rating'),
    statTopMovie: document.getElementById('val-top-movie'),
    
    // Modal content elements
    modalPoster: document.getElementById('modal-movie-poster'),
    modalTitle: document.getElementById('modal-movie-title'),
    modalGenre: document.getElementById('modal-movie-genre'),
    modalYear: document.getElementById('modal-movie-year'),
    modalDirector: document.getElementById('modal-movie-director'),
    modalStars: document.getElementById('modal-movie-stars'),
    modalRatingVal: document.getElementById('modal-movie-rating-val'),
    modalRatingCount: document.getElementById('modal-movie-rating-count'),
    modalPlot: document.getElementById('modal-movie-plot'),
    
    // Modal tabs & panels
    tabReviewsBtn: document.getElementById('btn-tab-reviews'),
    tabAddReviewBtn: document.getElementById('btn-tab-add-review'),
    reviewsListTab: document.getElementById('modal-reviews-list-tab'),
    addReviewTab: document.getElementById('modal-add-review-tab'),
    reviewsList: document.getElementById('modal-reviews-list'),
    reviewForm: document.getElementById('movie-review-form'),
    starSelector: document.getElementById('star-rating-selector'),
    starHint: document.getElementById('star-rating-hint'),
    
    toastContainer: document.getElementById('toast-container')
};

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
    initApp();
    setupEventListeners();
});

function initApp() {
    fetchStats();
    fetchGenres();
    fetchMovies();
}

// Setup Global Event Listeners
function setupEventListeners() {
    // Search input with debounce (250ms)
    elements.searchInput.addEventListener('input', (e) => {
        currentSearch = e.target.value;
        elements.clearSearchBtn.style.display = currentSearch ? 'flex' : 'none';
        
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            fetchMovies();
        }, 250);
    });

    // Clear search
    elements.clearSearchBtn.addEventListener('click', () => {
        elements.searchInput.value = "";
        currentSearch = "";
        elements.clearSearchBtn.style.display = 'none';
        fetchMovies();
    });

    // Modal Close
    elements.closeModalBtn.addEventListener('click', closeModal);
    elements.modal.addEventListener('click', (e) => {
        if (e.target === elements.modal) closeModal();
    });

    // ESC key to close modal
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && elements.modal.classList.contains('active')) {
            closeModal();
        }
    });

    // Modal Details Tabs
    elements.tabReviewsBtn.addEventListener('click', () => switchModalTab('reviews'));
    elements.tabAddReviewBtn.addEventListener('click', () => switchModalTab('form'));

    // Star Selector Radio Hints
    elements.starSelector.addEventListener('change', (e) => {
        const rating = e.target.value;
        const hints = {
            '1': 'Terrible - 1 Star',
            '2': 'Mediocre - 2 Stars',
            '3': 'Good - 3 Stars',
            '4': 'Great - 4 Stars',
            '5': 'Masterpiece - 5 Stars'
        };
        elements.starHint.textContent = hints[rating] || 'Select a rating';
        elements.starHint.style.color = 'var(--star-active)';
    });

    // Review Form Submit
    elements.reviewForm.addEventListener('submit', handleReviewSubmit);
    
    // Logo Click to reset filters
    document.getElementById('brand-logo').addEventListener('click', () => {
        currentGenre = "";
        currentSearch = "";
        elements.searchInput.value = "";
        elements.clearSearchBtn.style.display = 'none';
        
        // Reset active tab class
        document.querySelectorAll('.genre-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.genre === "");
        });
        
        fetchMovies();
    });
}

// Fetch stats panel data
async function fetchStats() {
    try {
        const res = await fetch('/api/stats');
        const stats = await res.json();
        elements.statMovies.textContent = stats.total_movies;
        elements.statReviews.textContent = stats.total_reviews;
        elements.statAvgRating.textContent = stats.global_avg_rating > 0 ? `${stats.global_avg_rating} ★` : '0.0 ★';
        elements.statTopMovie.textContent = stats.highest_rated_movie;
        
        // Make the Top Rated card clickable to open reviews directly
        const topRatedCard = document.getElementById('stat-top-movie');
        if (stats.highest_rated_id) {
            topRatedCard.style.cursor = 'pointer';
            topRatedCard.onclick = () => openMovieDetail(stats.highest_rated_id);
        } else {
            topRatedCard.style.cursor = 'default';
            topRatedCard.onclick = null;
        }
    } catch (err) {
        console.error('Error fetching stats:', err);
    }
}


// Fetch and render genre buttons
async function fetchGenres() {
    try {
        const res = await fetch('/api/genres');
        const genres = await res.json();
        
        // Clear all except "All Genres"
        elements.genreTabsList.innerHTML = `<button class="genre-tab active" data-genre="">All Genres</button>`;
        
        genres.forEach(genre => {
            const btn = document.createElement('button');
            btn.className = 'genre-tab';
            btn.dataset.genre = genre;
            btn.textContent = genre;
            elements.genreTabsList.appendChild(btn);
        });

        // Add event listeners to tabs
        elements.genreTabsList.addEventListener('click', (e) => {
            const tab = e.target.closest('.genre-tab');
            if (!tab) return;

            document.querySelectorAll('.genre-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            currentGenre = tab.dataset.genre;
            fetchMovies();
        });
    } catch (err) {
        console.error('Error fetching genres:', err);
    }
}

// Fetch movies grid
async function fetchMovies() {
    elements.movieGrid.innerHTML = `
        <div class="loading-spinner">
            <div class="spinner"></div>
            <p>Filtering cinema library...</p>
        </div>
    `;

    try {
        let url = '/api/movies';
        const params = [];
        if (currentGenre) params.push(`genre=${encodeURIComponent(currentGenre)}`);
        if (currentSearch) params.push(`search=${encodeURIComponent(currentSearch)}`);
        
        if (params.length > 0) {
            url += '?' + params.join('&');
        }

        const res = await fetch(url);
        moviesState = await res.json();
        
        renderMovieGrid();
    } catch (err) {
        console.error('Error fetching movies:', err);
        elements.movieGrid.innerHTML = `
            <div class="empty-state">
                <i class="fa-solid fa-triangle-exclamation"></i>
                <p>Failed to connect to backend api.</p>
            </div>
        `;
    }
}

// Render catalog layout
function renderMovieGrid() {
    elements.resultsCount.textContent = `${moviesState.length} title${moviesState.length === 1 ? '' : 's'} found`;
    
    if (currentGenre) {
        elements.catalogTitle.textContent = `${currentGenre} Masterpieces`;
    } else if (currentSearch) {
        elements.catalogTitle.textContent = 'Search Results';
    } else {
        elements.catalogTitle.textContent = 'All Masterpieces';
    }

    if (moviesState.length === 0) {
        elements.movieGrid.innerHTML = `
            <div class="empty-state">
                <i class="fa-solid fa-clapperboard"></i>
                <p>No movies match your current search criteria.</p>
            </div>
        `;
        return;
    }

    elements.movieGrid.innerHTML = "";
    moviesState.forEach(movie => {
        const card = document.createElement('div');
        card.className = 'movie-card';
        card.innerHTML = `
            <div class="card-poster-wrapper">
                <span class="card-genre-badge">${movie.genre}</span>
                <img src="${movie.poster_url}" alt="${movie.title}" loading="lazy">
            </div>
            <div class="card-body">
                <h3 class="card-title">${movie.title}</h3>
                <div class="card-meta">
                    <span>${movie.year}</span>
                    <span>By ${movie.director.split(',')[0]}</span>
                </div>
                <div class="card-rating-row">
                    <i class="fa-solid fa-star star-icon"></i>
                    <span class="card-rating-val">${movie.rating.toFixed(1)}</span>
                    <span class="card-reviews-count">(${movie.review_count} rev)</span>
                </div>
            </div>
        `;
        
        card.addEventListener('click', () => openMovieDetail(movie.id));
        elements.movieGrid.appendChild(card);
    });
}

// Open modal with detailed information
async function openMovieDetail(movieId) {
    selectedMovieId = movieId;
    switchModalTab('reviews');
    elements.reviewForm.reset();
    elements.starHint.textContent = 'Select a rating';
    elements.starHint.style.color = 'var(--text-secondary)';

    // Open immediately with loading indicator
    elements.modal.classList.add('active');
    document.body.style.overflow = 'hidden'; // Stop background scrolling

    try {
        const res = await fetch(`/api/movies/${movieId}`);
        const movie = await res.json();

        // Populate Modal Fields
        elements.modalPoster.src = movie.poster_url;
        elements.modalPoster.alt = movie.title;
        elements.modalTitle.textContent = movie.title;
        elements.modalGenre.textContent = movie.genre;
        elements.modalYear.textContent = movie.year;
        elements.modalDirector.textContent = movie.director;
        elements.modalPlot.textContent = movie.plot;
        elements.modalRatingVal.textContent = movie.rating.toFixed(1);
        elements.modalRatingCount.textContent = `(${movie.review_count} review${movie.review_count === 1 ? '' : 's'})`;

        // Render stars in header
        renderStarsHTML(elements.modalStars, movie.rating);
        
        // Render user reviews list
        renderReviewsList(movie.reviews);
    } catch (err) {
        console.error('Error fetching movie details:', err);
        showToast('Error fetching movie details', 'error');
        closeModal();
    }
}

// Close Modal helper
function closeModal() {
    elements.modal.classList.remove('active');
    document.body.style.overflow = 'auto'; // Re-enable background scrolling
    selectedMovieId = null;
}

// Switch between reviews list tab and submit form tab
function switchModalTab(tab) {
    if (tab === 'reviews') {
        elements.tabReviewsBtn.classList.add('active');
        elements.tabAddReviewBtn.classList.remove('active');
        elements.reviewsListTab.classList.add('active');
        elements.addReviewTab.classList.remove('active');
    } else {
        elements.tabReviewsBtn.classList.remove('active');
        elements.tabAddReviewBtn.classList.add('active');
        elements.reviewsListTab.classList.remove('active');
        elements.addReviewTab.classList.add('active');
    }
}

// Helper to draw visual stars (supports half stars)
function renderStarsHTML(container, rating) {
    container.innerHTML = "";
    const fullStars = Math.floor(rating);
    const hasHalf = rating % 1 >= 0.3 && rating % 1 <= 0.7;
    const roundedStars = rating % 1 > 0.7 ? fullStars + 1 : fullStars;

    for (let i = 1; i <= 5; i++) {
        const star = document.createElement('i');
        if (i <= roundedStars) {
            star.className = 'fa-solid fa-star';
        } else if (i === fullStars + 1 && hasHalf) {
            star.className = 'fa-solid fa-star-half-stroke';
        } else {
            star.className = 'fa-regular fa-star';
        }
        container.appendChild(star);
    }
}

// Render reviews inside details pane
function renderReviewsList(reviews) {
    if (!reviews || reviews.length === 0) {
        elements.reviewsList.innerHTML = `
            <div class="no-reviews">
                <i class="fa-regular fa-comments" style="font-size: 1.5rem; margin-bottom: 0.5rem; display: block;"></i>
                <p>No community reviews yet. Be the first to share your thoughts!</p>
            </div>
        `;
        return;
    }

    elements.reviewsList.innerHTML = "";
    reviews.forEach(review => {
        const reviewItem = document.createElement('div');
        reviewItem.className = 'review-item';
        
        // Format relative date or neat local string
        const reviewDate = new Date(review.created_at).toLocaleDateString(undefined, {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        });

        let starsHTML = '';
        for (let i = 1; i <= 5; i++) {
            starsHTML += `<i class="${i <= review.rating ? 'fa-solid' : 'fa-regular'} fa-star"></i>`;
        }

        reviewItem.innerHTML = `
            <div class="review-header">
                <span class="reviewer-name">${review.reviewer_name}</span>
                <span class="review-date">${reviewDate}</span>
            </div>
            <div class="review-stars">${starsHTML}</div>
            <p class="review-comment">${review.comment}</p>
        `;
        elements.reviewsList.appendChild(reviewItem);
    });
}

// Handle Form Submission of a review
async function handleReviewSubmit(e) {
    e.preventDefault();

    const name = document.getElementById('reviewer-name-input').value.trim();
    const comment = document.getElementById('review-comment-input').value.trim();
    const checkedRating = document.querySelector('input[name="star-rating"]:checked');

    if (!name || !comment) {
        showToast('All fields are required', 'error');
        return;
    }

    if (!checkedRating) {
        showToast('Please select a star rating', 'error');
        return;
    }

    const rating = parseInt(checkedRating.value, 10);

    try {
        const res = await fetch(`/api/movies/${selectedMovieId}/reviews`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                reviewer_name: name,
                rating: rating,
                comment: comment
            })
        });

        const data = await res.json();
        
        if (res.ok) {
            showToast('Review submitted successfully!', 'success');
            
            // Reload movie detail (to pull in new review item + updated rating)
            openMovieDetail(selectedMovieId);
            
            // Reload global elements in background
            fetchMovies();
            fetchStats();
        } else {
            showToast(data.error || 'Failed to submit review', 'error');
        }
    } catch (err) {
        console.error('Error submitting review:', err);
        showToast('Connection error. Failed to send review.', 'error');
    }
}

// Non-intrusive notification toast
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = type === 'success' 
        ? '<i class="fa-solid fa-circle-check"></i>' 
        : '<i class="fa-solid fa-circle-exclamation"></i>';
        
    toast.innerHTML = `${icon} <span>${message}</span>`;
    elements.toastContainer.appendChild(toast);

    // Fade and delete
    setTimeout(() => {
        toast.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        setTimeout(() => toast.remove(), 500);
    }, 3000);
}
