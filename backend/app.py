from flask import Flask, jsonify, request
import psycopg2
import os
from datetime import datetime

app = Flask(__name__)

# Конфигурация БД
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'db'),
    'database': os.getenv('DB_NAME', 'mydb'),
    'user': os.getenv('DB_USER', 'user'),
    'password': os.getenv('DB_PASSWORD', 'password')
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

@app.route('/')
def hello():
    return jsonify({
        'message': 'Добро пожаловать в Docker приложение!',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/users', methods=['GET'])
def get_users():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT id, name, email FROM users;')
        users = cur.fetchall()
        cur.close()
        conn.close()
        
        return jsonify([{
            'id': user[0],
            'name': user[1],
            'email': user[2]
        } for user in users])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id;',
            (data['name'], data['email'])
        )
        user_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'id': user_id, 'message': 'Пользователь создан'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
