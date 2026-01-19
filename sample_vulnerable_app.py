"""
취약한 Flask 애플리케이션 (데모용)
의도적으로 여러 보안 취약점을 포함하고 있습니다.
"""

from flask import Flask, request, render_template_string
import sqlite3
import os
import subprocess

app = Flask(__name__)

# 취약점 1: 하드코딩된 비밀번호 및 시크릿 키
SECRET_KEY = "hardcoded-secret-key-123456"
DATABASE_PASSWORD = "admin123"
API_KEY = "sk-1234567890abcdef"

# 취약점 2: SQL Injection 취약점
@app.route('/user')
def get_user():
    user_id = request.args.get('id')
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # 사용자 입력을 직접 쿼리에 삽입 (SQL Injection 취약)
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    cursor.execute(query)
    
    result = cursor.fetchall()
    conn.close()
    return str(result)

# 취약점 3: Command Injection 취약점
@app.route('/ping')
def ping_server():
    host = request.args.get('host')
    
    # 사용자 입력을 직접 shell 명령어로 실행 (Command Injection 취약)
    result = os.system(f"ping -c 1 {host}")
    return f"Ping result: {result}"

# 취약점 4: Path Traversal 취약점
@app.route('/file')
def read_file():
    filename = request.args.get('name')
    
    # 경로 검증 없이 파일 읽기 (Path Traversal 취약)
    with open(f"/var/www/files/{filename}", 'r') as f:
        content = f.read()
    return content

# 취약점 5: Server-Side Template Injection (SSTI)
@app.route('/template')
def render_template():
    name = request.args.get('name')
    
    # 사용자 입력을 직접 템플릿에 삽입 (SSTI 취약)
    template = f"<h1>Hello {name}!</h1>"
    return render_template_string(template)

# 취약점 6: Weak Cryptography
def encrypt_password(password):
    import hashlib
    # MD5 사용 (취약한 해시 알고리즘)
    return hashlib.md5(password.encode()).hexdigest()

# 취약점 7: Insecure Deserialization
@app.route('/load')
def load_data():
    import pickle
    data = request.args.get('data')
    
    # 신뢰할 수 없는 데이터를 pickle로 역직렬화 (RCE 가능)
    obj = pickle.loads(data.encode())
    return str(obj)

# 취약점 8: Debug Mode 활성화 (프로덕션 환경에서 위험)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
