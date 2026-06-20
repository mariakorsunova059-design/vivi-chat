from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Хранилище данных в памяти сервера
active_users = {} # {username: avatar_base64}
private_messages = [] # Список всех ЛС: [{"from":..., "to":..., "text":..., "is_sticker":...}]

@app.route('/')
def index():
    return render_template('index.html')

# Вход и сохранение аватарки на сервере
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username', '').strip()
    avatar = data.get('avatar', '')
    
    if not username:
        return jsonify({"status": "error", "message": "Имя не может быть пустым!"}), 400
        
    if username in active_users:
        return jsonify({"status": "error", "message": "Этот юзернейм уже занят!"}), 400
        
    active_users[username] = avatar
    return jsonify({"status": "success"}), 200

# Поиск пользователя по юзернейму
@app.route('/search_user', methods=['POST'])
def search_user():
    data = request.json
    username = data.get('username', '').strip()
    if username in active_users:
        return jsonify({"status": "success", "username": username, "avatar": active_users[username]}), 200
    return jsonify({"status": "error", "message": "Пользователь не найден"}), 404

# Получение ЛС между двумя пользователями
@app.route('/get_private_messages', methods=['POST'])
def get_messages():
    data = request.json
    me = data.get('me')
    with_user = data.get('with_user')
    
    # Фильтруем только те сообщения, которые были между мной и этим собеседником
    chat_history = [
        m for m in private_messages 
        if (m['from'] == me and m['to'] == with_user) or (m['from'] == with_user and m['to'] == me)
    ]
    return jsonify(chat_history)

# Отправка личного сообщения
@app.route('/send_private_message', methods=['POST'])
def send_message():
    data = request.json
    from_user = data.get('from')
    to_user = data.get('to')
    text = data.get('text', '')
    is_sticker = data.get('is_sticker', False)

    if from_user and to_user:
        private_messages.append({
            'from': from_user,
            'to': to_user,
            'text': text,
            'avatar': active_users.get(from_user, ''),
            'is_sticker': is_sticker
        })
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
