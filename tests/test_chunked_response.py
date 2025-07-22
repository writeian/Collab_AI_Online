import os
import sys
import tempfile
from app import create_app, db
from models import User, Chat, Message

app = create_app()
app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

with app.app_context():
    db.drop_all()
    db.create_all()
    # Create test user and chat
    user = User(username='testuser', email='test@example.com', password_hash='x', display_name='Test User')
    db.session.add(user)
    db.session.commit()
    chat = Chat(title='Test Chat', room_id=1, created_by=user.id)
    db.session.add(chat)
    db.session.commit()
    # Re-query chat to ensure it's attached to the session
    chat = Chat.query.get(chat.id)
    # Create a truncated assistant message
    msg = Message(chat_id=chat.id, role='assistant', content='This is a truncated response...', is_truncated=True)
    db.session.add(msg)
    db.session.commit()
    msg_id = msg.id

    client = app.test_client()

    # POST to continue endpoint (double-checking the route)
    response = client.post(f'/chat/{chat.id}/continue/{msg_id}')
    print('POST /chat/continue response status:', response.status_code)
    # Check messages in DB
    messages = Message.query.filter_by(chat_id=chat.id).order_by(Message.timestamp).all()
    print('Messages in chat:')
    for m in messages:
        print(f'ID: {m.id}, parent: {m.parent_message_id}, truncated: {m.is_truncated}, content: {m.content[:40]}') 