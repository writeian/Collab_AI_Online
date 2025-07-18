from flask import Blueprint, request, jsonify
from models import db
from datetime import datetime
import json

analytics = Blueprint('analytics', __name__)

class PageView(db.Model):
    """Track page views for analytics."""
    id = db.Column(db.Integer, primary_key=True)
    page = db.Column(db.String(200), nullable=False)
    user_agent = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Relationship
    user = db.relationship('User', backref='page_views')

@analytics.route('/pageview', methods=['POST'])
def track_pageview():
    """Track a page view."""
    try:
        data = request.get_json()
        
        # Get user ID if logged in
        user_id = None
        if 'user_id' in request.session:
            user_id = request.session['user_id']
        
        # Create page view record
        pageview = PageView(
            page=data.get('page', ''),
            user_agent=data.get('user_agent', ''),
            ip_address=request.remote_addr,
            user_id=user_id
        )
        
        db.session.add(pageview)
        db.session.commit()
        
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@analytics.route('/stats', methods=['GET'])
def get_stats():
    """Get basic analytics stats."""
    try:
        # Total page views
        total_views = PageView.query.count()
        
        # Unique visitors (by IP)
        unique_visitors = db.session.query(PageView.ip_address).distinct().count()
        
        # Most visited pages
        popular_pages = db.session.query(
            PageView.page, 
            db.func.count(PageView.page).label('count')
        ).group_by(PageView.page).order_by(db.func.count(PageView.page).desc()).limit(10).all()
        
        # Recent activity (last 7 days)
        from datetime import timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_views = PageView.query.filter(PageView.timestamp >= week_ago).count()
        
        return jsonify({
            'total_page_views': total_views,
            'unique_visitors': unique_visitors,
            'recent_views_7_days': recent_views,
            'popular_pages': [{'page': page, 'count': count} for page, count in popular_pages]
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500 