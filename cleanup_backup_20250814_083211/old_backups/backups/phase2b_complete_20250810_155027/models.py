from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# SQLAlchemy instance is created here so it can be imported by app.py
# without causing circular-import issues.
db = SQLAlchemy()

class User(db.Model):
    """A registered user of the application."""
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Registration questions (optional fields)
    full_name = db.Column(db.String(100), nullable=True)
    institution = db.Column(db.String(200), nullable=True)
    department = db.Column(db.String(200), nullable=True)
    research_area = db.Column(db.String(200), nullable=True)
    role = db.Column(db.String(50), nullable=True)  # Student, Professor, Researcher, etc.
    primary_use_case = db.Column(db.String(100), nullable=True)
    team_size = db.Column(db.String(50), nullable=True)
    heard_from = db.Column(db.String(100), nullable=True)
    receive_updates = db.Column(db.Boolean, default=False, nullable=True)
    contact_for_research = db.Column(db.Boolean, default=False, nullable=True)
    
    # Password reset fields
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    owned_rooms = db.relationship('Room', backref='owner', lazy=True, foreign_keys='Room.owner_id')
    room_memberships = db.relationship('RoomMember', backref='user', lazy=True)
    google_auth = db.relationship('GoogleAuth', backref='user', uselist=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"<User {self.username}>"

class GoogleAuth(db.Model):
    """Stores Google OAuth tokens for Docs API access."""
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text, nullable=True)
    token_expiry = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<GoogleAuth user_id={self.user_id}>"

class Room(db.Model):
    """A collaborative learning space where users can create and share chats."""
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    goals = db.Column(db.Text, nullable=True)  # Learning goals for the room
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships
    chats = db.relationship('Chat', backref='room', lazy=True, cascade='all, delete-orphan')
    members = db.relationship('RoomMember', backref='room', lazy=True, cascade='all, delete-orphan')
    custom_prompts = db.relationship('CustomPrompt', backref='room', lazy=True, cascade='all, delete-orphan')
    achievements = db.relationship('Achievement', backref='room', lazy=True, cascade='all, delete-orphan')
    user_mode_usage = db.relationship('UserModeUsage', backref='room', lazy=True, cascade='all, delete-orphan')
    prompt_records = db.relationship('PromptRecord', backref='room', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Room {self.id} {self.name!r}>"

class RoomMember(db.Model):
    """Represents a user's membership in a room."""
    
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    accepted_at = db.Column(db.DateTime, nullable=True)  # When user first accessed the room
    can_create_chats = db.Column(db.Boolean, default=True, nullable=False)
    can_invite_members = db.Column(db.Boolean, default=False, nullable=False)
    
    __table_args__ = (db.UniqueConstraint('room_id', 'user_id', name='unique_room_user'),)
    
    def __repr__(self):
        return f"<RoomMember room_id={self.room_id} user_id={self.user_id}>"

class Chat(db.Model):
    """A conversation within a room that can be accessed by all room members."""
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    mode = db.Column(
        db.String(32),          # Dynamic modes based on room goals
        default='explore',
        nullable=False
    )
    
    # Relationships
    messages = db.relationship('Message', backref='chat', lazy=True, cascade='all, delete-orphan')
    prompt_records = db.relationship('PromptRecord', backref='chat', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='chat', lazy=True, cascade='all, delete-orphan')
    creator = db.relationship('User', backref='created_chats', foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<Chat {self.id} {self.title!r}>"

class Message(db.Model):
    """A single turn in the conversation (user or assistant)."""
    
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # null for assistant messages
    role = db.Column(db.String(20), nullable=False)  # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    parent_message_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=True, default=None)
    is_truncated = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relationship
    user = db.relationship('User', backref='messages')
    
    def __repr__(self):
        return f"<Message {self.id} role={self.role}>"

class Comment(db.Model):
    """Comments on specific dialogue items in a chat."""
    
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    dialogue_number = db.Column(db.Integer, nullable=False)  # Which prompt/response (1, 2, 3, etc.)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='comments')
    
    def __repr__(self):
        return f"<Comment {self.id} on dialogue {self.dialogue_number}>"

class CustomPrompt(db.Model):
    """Custom system instructions created by instructors for specific modes and rooms."""
    
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=True)  # null for global prompts
    mode_key = db.Column(db.String(50), nullable=False)
    label = db.Column(db.String(100), nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships
    creator = db.relationship('User', backref='custom_prompts', foreign_keys=[created_by])
    
    __table_args__ = (db.UniqueConstraint('room_id', 'mode_key', name='unique_room_mode'),)
    
    def __repr__(self):
        return f"<CustomPrompt {self.mode_key} for room {self.room_id}>"

class PromptRecord(db.Model):
    """Records student prompts for dashboard analytics."""
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    mode = db.Column(db.String(32), nullable=False)  # The mode when the prompt was sent
    prompt_content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='prompt_records')
    
    def __repr__(self):
        return f"<PromptRecord {self.id} mode={self.mode}>"

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
    
    def __repr__(self):
        return f"<PageView {self.id} page={self.page}>"

class UserModeUsage(db.Model):
    """Track which modes each user has used in each room for achievements."""
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    mode = db.Column(db.String(32), nullable=False)  # The mode that was used
    first_used_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_used_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    usage_count = db.Column(db.Integer, default=1, nullable=False)  # How many times this mode was used
    
    # Relationships
    user = db.relationship('User', backref='mode_usage')
    
    __table_args__ = (db.UniqueConstraint('user_id', 'room_id', 'mode', name='unique_user_room_mode'),)
    
    def __repr__(self):
        return f"<UserModeUsage user_id={self.user_id} room_id={self.room_id} mode={self.mode}>"

class Achievement(db.Model):
    """Track user achievements/milestones in rooms."""
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    achievement_type = db.Column(db.String(50), nullable=False)  # 'first_steps', 'explorer', 'collaborator', etc.
    earned_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='achievements')
    
    __table_args__ = (db.UniqueConstraint('user_id', 'room_id', 'achievement_type', name='unique_user_room_achievement'),)
    
    def __repr__(self):
        return f"<Achievement {self.achievement_type} for user {self.user_id} in room {self.room_id}>"

class RubricCriterion(db.Model):
    """Rubric criteria for assessing learning step progress."""
    
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    step_key = db.Column(db.String(32), nullable=False)  # 'explore', 'focus', 'context', etc.
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    weight = db.Column(db.Float, default=1.0, nullable=False)
    order = db.Column(db.Integer, nullable=False)
    
    # Relationships
    room = db.relationship('Room', backref='rubric_criteria')
    levels = db.relationship('RubricLevel', backref='criterion', lazy=True, cascade='all, delete-orphan')
    
    __table_args__ = (db.UniqueConstraint('room_id', 'step_key', 'name', name='unique_room_step_criterion'),)
    
    def __repr__(self):
        return f"<RubricCriterion {self.name} for {self.step_key} in room {self.room_id}>"

class RubricLevel(db.Model):
    """Individual levels within a rubric criterion."""
    
    id = db.Column(db.Integer, primary_key=True)
    criterion_id = db.Column(db.Integer, db.ForeignKey('rubric_criterion.id'), nullable=False)
    level = db.Column(db.String(50), nullable=False)  # 'Emerging', 'Developing', 'Proficient', 'Exemplary'
    score = db.Column(db.Integer, nullable=False)  # 1, 2, 3, 4
    description = db.Column(db.Text, nullable=False)
    examples = db.Column(db.Text, nullable=True)  # JSON array of examples
    
    def __repr__(self):
        return f"<RubricLevel {self.level} (score {self.score}) for criterion {self.criterion_id}>"

class RoomRubric(db.Model):
    """Overall rubric configuration for a learning step in a room."""
    
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    step_key = db.Column(db.String(32), nullable=False)
    progression_threshold = db.Column(db.Float, default=2.5, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    room = db.relationship('Room', backref='room_rubrics')
    
    __table_args__ = (db.UniqueConstraint('room_id', 'step_key', name='unique_room_step_rubric'),)
    
    def __repr__(self):
        return f"<RoomRubric for {self.step_key} in room {self.room_id}>"