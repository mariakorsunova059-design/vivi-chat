from flask import Flask, render_template_string
from flask_socketio import SocketIO, emit
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tg_style_secret_key_2026'
socketio = SocketIO(app, cors_allowed_origins="*")

# Палитра приятных цветов для аватарок (как в Telegram)
AVATAR_COLORS = ["#1abc9c", "#2ecc71", "#3498db", "#9b59b6", "#34495e", "#16a085", "#27ae60", "#2980b9", "#8e44ad", "#f1c40f", "#e67e22", "#e74c3c"]

HTML_PAGE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>вивиok мессенджер</title>
    <script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #e7ebf0; display: flex; justify-content: center; align-items: center; height: 100vh; }
        
        /* Окно авторизации */
        #auth-container { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 360px; text-align: center; }
        #auth-container h2 { margin-bottom: 20px; color: #2481cc; }
        .auth-input { width: 100%; padding: 12px; margin-bottom: 15px; border: 1px solid #dae1e8; border-radius: 8px; font-size: 15px; outline: none; }
        .auth-btn { width: 100%; padding: 12px; background: #2481cc; color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; }
        .auth-btn:hover { background: #2074b6; }

        /* Окно чата */
        #chat-container { display: none; width: 450px; height: 85vh; background: white; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); flex-direction: column; overflow: hidden; }
        .brand-title { background: #527fa6; color: white; padding: 15px; font-size: 18px; font-weight: bold; text-align: center; }
        
        #chat-window { flex-grow: 1; padding: 15px; overflow-y: auto; background: #f4f4f5; display: flex; flex-direction: column; gap: 10px; }
        
        /* Стили сообщения в стиле ТГ */
        .msg-row { display: flex; gap: 10px; align-items: flex-start; max-width: 85%; }
        .avatar { width: 38px; height: 38px; border-radius: 50%; color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px; flex-shrink: 0; text-transform: uppercase; }
        .msg-content { background: white; padding: 8px 12px; border-radius: 12px; box-shadow: 0 1px 2px rgba(0,0,0,0.07); position: relative; display: flex; flex-direction: column; }
        .msg-name { font-weight: bold; color: #3a6d99; font-size: 13px; margin-bottom: 2px; cursor: pointer; }
        .msg-username { color: #707579; font-weight: normal; font-size: 12px; margin-left: 5px; }
        .msg-text { color: #000; font-size: 15px; word-break: break-word; }

        /* Поле ввода */
        .input-box { padding: 10px 15px; display: flex; gap: 10px; background: white; border-top: 1px solid #e6e6e6; align-items: center; }
        #text-input { flex-grow: 1; padding: 10px 15px; border: 1px solid #dae1e8; border-radius: 20px; font-size: 15px; outline: none; background: #f1f5f9; }
        #send-btn { background: none; border: none; color: #2481cc; font-weight: bold; font-size: 16px; cursor: pointer; padding: 5px 10px; }
        #send-btn:hover { color: #2074b6; }
    </style>
</head>
<body>

    <div id="auth-container">
        <h2>вивиok</h2>
        <p style="color: #707579; margin-bottom: 20px; font-size: 14px;">Введите ваши данные для входа в мессенджер</p>
        <input type="text" id="auth-name" class="auth-input" placeholder="Ваше имя (например, Иван)">
        <input type="text" id="auth-username" class="auth-input" placeholder="Юзернейм (например, ivan_99)">
        <button class="auth-btn" onclick="login()">Войти в чат</button>
    </div>

    <div id="chat-container">
        <div class="brand-title">вивиok мессенджер</div>
        <div id="chat-window"></div>
        <div class="input-box">
            <input type="text" id="text-input" placeholder="Написать сообщение..." onkeypress="checkEnter(event)">
            <button id="send-btn" onclick="send()">Отправить</button>
        </div>
    </div>

    <script>
        const socket = io();
        let myName = "";
        let myUsername = "";
        let myColor = "";

        function login() {
            const nameInput = document.getElementById('auth-name').value.trim();
            let usernameInput = document.getElementById('auth-username').value.trim();

            if (!nameInput || !usernameInput) {
                alert("Пожалуйста, заполните оба поля!");
                return;
            }

            // Убираем лишнюю @, если пользователь её сам ввел, и добавляем красиво
            usernameInput = usernameInput.replace(/^@/, '');
            
            myName = nameInput;
            myUsername = "@" + usernameInput;

            # Запрашиваем у сервера случайный цвет для нашей аватарки
            socket.emit('get_avatar_color', {}, function(color) {
                myColor = color;
                // Скрываем форму входа, показываем чат
                document.getElementById('auth-container').style.display = 'none';
                document.getElementById('chat-container').style.display = 'flex';
            });
        }

        socket.on('msg_to_all', function(data) {
            const chatWindow = document.getElementById('chat-window');
            
            // Создаем строку сообщения
            const msgRow = document.createElement('div');
            msgRow.className = 'msg-row';

            // Получаем первую букву имени для аватарки
            const initial = data.name.charAt(0);

            msgRow.innerHTML = `
                <div class="avatar" style="background-color: ${data.color};">${initial}</div>
                <div class="msg-content">
                    <div class="msg-name">${data.name}<span class="msg-username">${data.username}</span></div>
                    <div class="msg-text">${data.text}</div>
                </div>
            `;

            chatWindow.appendChild(msgRow);
            chatWindow.scrollTop = chatWindow.scrollHeight;
        });

        function send() {
            const textInput = document.getElementById('text-input');
            const text = textInput.value.trim();
            if(text) {
                socket.emit('msg_from_client', {
                    name: myName,
                    username: myUsername,
                    text: text,
                    color: myColor
                });
                textInput.value = '';
            }
        }

        function checkEnter(e) { if(e.key === 'Enter') send(); }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@socketio.on('get_avatar_color')
def handle_avatar_color(data):
    # Возвращаем клиенту случайный цвет из палитры ТГ
    return random.choice(AVATAR_COLORS)

@socketio.on('msg_from_client')
def handle_msg(data):
    emit('msg_to_all', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
