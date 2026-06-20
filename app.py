from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Хранилище сообщений и занятых ников (в памяти сервера)
messages = []
active_users = set()

@app.route('/')
def index():
    return render_template('index.html')

# Регистрация и проверка уникальности ника
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username', '').strip()
    
    if not username:
        return jsonify({"status": "error", "message": "Имя не может быть пустым!"}), 400
        
    if username in active_users:
        return jsonify({"status": "error", "message": "Этот юзернейм уже занят кем-то другим!"}), 400
        
    active_users.add(username)
    return jsonify({"status": "success"}), 200

# Получение сообщений
@app.route('/get_messages', methods=['GET'])
def get_messages():
    return jsonify(messages)

# Отправка сообщения (или стикера)
@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    username = data.get('username')
    text = data.get('text', '')
    avatar = data.get('avatar', '') # Получаем аватарку в виде текста (Base64)
    is_sticker = data.get('is_sticker', False)

    if username:
        messages.append({
            'username': username,
            'text': text,
            'avatar': avatar,
            'is_sticker': is_sticker
        })
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
