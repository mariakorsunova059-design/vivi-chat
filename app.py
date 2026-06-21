from flask import Flask, render_template, request, jsonify
import time

app = Flask(__name__)

# Хранилища данных в памяти сервера
# active_users = { username: {"avatar": base64, "last_seen": timestamp} }
active_users = {}
private_messages = [] 
# shared_videos = { "user1-user2": {"url": str, "status": str} }
shared_videos = {}

def get_chat_id(u1, u2):
    return "-".join(sorted([u1, u2]))

@app.route('/')
def index():
    return render_template('index.html')

# Фоновый пинг для автоматического обновления Онлайн-статуса
@app.route('/ping', methods=['POST'])
def ping():
    data = request.json
    username = data.get('username', '').strip()
    avatar = data.get('avatar', '')
    if username:
        if username not in active_users:
            active_users[username] = {"avatar": avatar, "last_seen": time.time()}
        else:
            active_users[username]["last_seen"] = time.time()
            if avatar:  # Если пришла аватарка, обновляем её в памяти
                active_users[username]["avatar"] = avatar
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 400

# Регистрация нового аккаунта
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username', '').strip()
    avatar = data.get('avatar', '')
    
    if not username:
        return jsonify({"status": "error", "message": "Имя не может быть пустым!"}), 400
        
    # Пользователь считается занятым, только если от него был пинг в последние 20 секунд
    if username in active_users and (time.time() - active_users[username]['last_seen'] < 20):
        return jsonify({"status": "error", "message": "Этот юзернейм сейчас занят!"}), 400
        
    active_users[username] = {"avatar": avatar, "last_seen": time.time()}
    return jsonify({"status": "success"}), 200

# Поиск пользователя по юзернейму
@app.route('/search_user', methods=['POST'])
def search_user():
    data = request.json
    username = data.get('username', '').strip()
    if username in active_users:
        is_online = (time.time() - active_users[username]['last_seen']) < 20
        return jsonify({
            "status": "success", 
            "username": username, 
            "avatar": active_users[username]['avatar'],
            "online": is_online,
            "last_seen": active_users[username]['last_seen']
        }), 200
    return jsonify({"status": "error", "message": "Пользователь не найден"}), 404

# Получение переписки и данных плеера видео
@app.route('/get_private_messages', methods=['POST'])
def get_messages():
    data = request.json
    me = data.get('me')
    with_user = data.get('with_user')
    if not me or not with_user:
        return jsonify({"messages": [], "video": {"url": "", "status": ""}})
        
    chat_id = get_chat_id(me, with_user)
    
    chat_history = [
        m for m in private_messages 
        if (m['from'] == me and m['to'] == with_user) or (m['from'] == with_user and m['to'] == me)
    ]
    video_data = shared_videos.get(chat_id, {"url": "", "status": ""})
    return jsonify({"messages": chat_history, "video": video_data})

# Отправка личного сообщения / стикера
@app.route('/send_private_message', methods=['POST'])
def send_message():
    data = request.json
    from_user = data.get('from')
    to_user = data.get('to')
    text = data.get('text', '')
    is_sticker = data.get('is_sticker', False)

    if from_user and to_user:
        avatar_url = active_users.get(from_user, {}).get('avatar', '')
        private_messages.append({
            'from': from_user,
            'to': to_user,
            'text': text,
            'avatar': avatar_url,
            'is_sticker': is_sticker
        })
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 400

# Синхронизация совместного видео
@app.route('/share_video', methods=['POST'])
def share_video():
    data = request.json
    me = data.get('me')
    with_user = data.get('with_user')
    url = data.get('url', '')
    status_text = data.get('status', '')
    
    chat_id = get_chat_id(me, with_user)
    shared_videos[chat_id] = {"url": url, "status": status_text}
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
