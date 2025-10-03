#!/usr/bin/env python3
from flask import Flask, jsonify, session
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, Article, User
import os

# Flask app configuration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'  # using SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_secret')  # needed for sessions

# Initialize database and migrations
db.init_app(app)
migrate = Migrate(app, db)

# Enable CORS so React frontend can send cookies
CORS(app, supports_credentials=True)

# Route: Get an article
@app.route('/articles/<int:id>', methods=['GET'])
def get_article(id):
    # Initialize session['page_views'] to 0 if this is the first request
    session['page_views'] = session['page_views'] if 'page_views' in session else 0

    # Increment page_views for every request
    session['page_views'] += 1

    # Paywall: block access if more than 3 page views
    if session['page_views'] > 3:
        return jsonify({'message': 'Maximum pageview limit reached'}), 401

    # Fetch the article from the database using SQLAlchemy 2.0 preferred method
    article = db.session.get(Article, id)
    if not article:
        return jsonify({'message': 'Article not found'}), 404

    # Return article JSON
    return jsonify(article.to_dict()), 200

# Route: Clear session
@app.route('/clear', methods=['GET'])
def clear_session():
    session.clear()
    return jsonify({'message': 'session cleared'}), 200


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
