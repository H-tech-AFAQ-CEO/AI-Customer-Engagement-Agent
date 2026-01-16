from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import requests
import json
import os
from datetime import datetime
import schedule
import time
import threading
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory storage for demo purposes
chats = []
crm_logs = []
social_posts = []
analytics = {
    'total_chats': 247,
    'avg_resolution': '4.2m',
    'fallback_rate': 3.8,
    'social_posts': 42
}

# AI Configuration
ai_config = {
    'model': 'gpt4',
    'timeout': 30,
    'max_length': 10,
    'analytics_enabled': True
}

# Training data
training_data = {
    'brand_voice': 'Friendly, professional, and solution-focused. Use clear language and avoid jargon.',
    'intents': {
        'order_status': 'Thank you for your inquiry. I can help you check your order status.',
        'product_info': 'I\'d be happy to provide information about our products.',
        'refund': 'I understand you\'re requesting a refund. Let me assist you with that.',
        'technical': 'For technical support, please provide more details about the issue.'
    }
}

@app.route('/')
def index():
    return render_template('index.html', analytics=analytics, training=training_data, config=ai_config)

@app.route('/social')
def social():
    return render_template('social.html', posts=social_posts, analytics=analytics)

@app.route('/chat')
def chat():
    return render_template('chat.html', chats=chats, analytics=analytics)

@app.route('/crm')
def crm():
    return render_template('crm.html', logs=crm_logs, analytics=analytics)

@app.route('/analytics')
def analytics_page():
    return render_template('analytics.html', analytics=analytics)

@app.route('/training')
def training():
    return render_template('training.html', training=training_data, analytics=analytics)

@app.route('/config')
def config():
    return render_template('config.html', config=ai_config, analytics=analytics)

@app.route('/publish_post', methods=['POST'])
def publish_post():
    data = request.json
    platform = data.get('platform')
    message = data.get('message')
    schedule_time = data.get('schedule_time')
    auto_post = data.get('auto_post')

    if not message:
        return jsonify({'error': 'Message is required'}), 400

    # Mock publishing
    post = {
        'id': len(social_posts) + 1,
        'platform': platform,
        'message': message,
        'scheduled': schedule_time,
        'auto': auto_post,
        'timestamp': datetime.now().isoformat()
    }
    social_posts.append(post)

    # Update analytics
    analytics['social_posts'] += 1

    # Add to CRM logs
    crm_logs.append({
        'message': f'Social post scheduled for {platform}',
        'timestamp': datetime.now().isoformat()
    })

    return jsonify({'success': True, 'post_id': post['id']})

@app.route('/send_chat', methods=['POST'])
def send_chat():
    data = request.json
    message = data.get('message')

    if not message:
        return jsonify({'error': 'Message is required'}), 400

    # Add user message
    user_msg = {
        'type': 'user',
        'message': message,
        'timestamp': datetime.now().isoformat()
    }
    chats.append(user_msg)

    # Generate AI response (mock)
    ai_response = generate_ai_response(message)
    bot_msg = {
        'type': 'bot',
        'message': ai_response,
        'timestamp': datetime.now().isoformat()
    }
    chats.append(bot_msg)

    # Update analytics
    analytics['total_chats'] += 1

    return jsonify({'response': ai_response})

@app.route('/handoff', methods=['POST'])
def handoff():
    crm_logs.append({
        'message': 'Chat handed off to human agent',
        'timestamp': datetime.now().isoformat()
    })
    return jsonify({'success': True})

@app.route('/sync_crm', methods=['POST'])
def sync_crm():
    data = request.json
    endpoint = data.get('endpoint')
    api_key = data.get('api_key')

    if not endpoint or not api_key:
        return jsonify({'error': 'Endpoint and API key required'}), 400

    # Mock CRM sync
    crm_logs.append({
        'message': 'Manual CRM sync completed',
        'timestamp': datetime.now().isoformat()
    })

    return jsonify({'success': True})

@app.route('/update_training', methods=['POST'])
def update_training():
    data = request.json
    training_data['brand_voice'] = data.get('brand_voice', training_data['brand_voice'])
    intent = data.get('intent')
    template = data.get('template')
    if intent and template:
        training_data['intents'][intent] = template

    crm_logs.append({
        'message': 'AI training model updated',
        'timestamp': datetime.now().isoformat()
    })

    return jsonify({'success': True})

@app.route('/save_config', methods=['POST'])
def save_config():
    data = request.json
    ai_config.update({
        'model': data.get('model', ai_config['model']),
        'timeout': int(data.get('timeout', ai_config['timeout'])),
        'max_length': int(data.get('max_length', ai_config['max_length'])),
        'analytics_enabled': data.get('analytics_enabled', ai_config['analytics_enabled'])
    })

    return jsonify({'success': True})

@app.route('/refresh_stats', methods=['POST'])
def refresh_stats():
    import random
    analytics['total_chats'] += random.randint(0, 10)
    analytics['fallback_rate'] = max(0, analytics['fallback_rate'] - 0.1)

    crm_logs.append({
        'message': 'Analytics refreshed',
        'timestamp': datetime.now().isoformat()
    })

    return jsonify(analytics)

def generate_ai_response(user_message):
    # Simple mock AI response based on keywords
    message_lower = user_message.lower()
    if 'order' in message_lower:
        return training_data['intents']['order_status']
    elif 'product' in message_lower:
        return training_data['intents']['product_info']
    elif 'refund' in message_lower:
        return training_data['intents']['refund']
    elif 'technical' in message_lower or 'help' in message_lower:
        return training_data['intents']['technical']
    else:
        return "Thank you for your message. How can I assist you today?"

# Background scheduler for auto-posts
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)

scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

if __name__ == '__main__':
    socketio.run(app, debug=True)