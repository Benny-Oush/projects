import sqlite3
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
import pages.page_generator as pg

def create_db():
    with sqlite3.connect('tasks.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                task TEXT NOT NULL,
                completed BOOLEAN NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
def add_task(task):
    with sqlite3.connect('tasks.db') as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO tasks (task) VALUES (?)', (task,))
        conn.commit()
def get_all_tasks():
    with sqlite3.connect('tasks.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, task, case when completed=1 then "Complete" else "Pending" end as status, created_at FROM tasks')
        return cursor.fetchall()
def edit_task(id, task):
    with sqlite3.connect('tasks.db') as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE tasks SET task = ? WHERE id = ?', (task, id))
        conn.commit()
def complete_task(id):
    with sqlite3.connect('tasks.db') as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE tasks SET completed = 1 WHERE id = ?', (id,))
        conn.commit()
def delete_task(id):
    with sqlite3.connect('tasks.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tasks WHERE id = ?', (id,))
        conn.commit()


class MyHandler(BaseHTTPRequestHandler):
    def generate_homepage(self, edit_id=None):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        return self.wfile.write(pg.create_page(get_all_tasks(), edit_id).encode())
    def do_GET(self):
        try:
            path = self.path
            if path == '/style.css':
                with open('pages/style.css', 'r') as f:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/css')
                    self.end_headers()
                    return self.wfile.write(f.read().encode())
            elif path == '/':
                return self.generate_homepage()
            elif path.startswith('/complete'):
                id = path.split('=')[1]
                complete_task(id)
                self.send_response(303)
                self.send_header('Location', '/')
                self.end_headers()
            elif path.startswith('/edit'):
                id = path.split('=')[1]
                self.generate_homepage(id)
            elif path.startswith('/delete'):
                id = path.split('=')[1]
                delete_task(id)
                self.send_response(303)
                self.send_header('Location', '/')
                self.end_headers()
            else:
                self.send_response(404)
                self.wfile.write(b'404 Page Not Found')
        except Exception as e:
            print(e)
            self.send_response(500)
            self.wfile.write(b'500 Internal Server Error')
    def do_POST(self):
        try:
            path = self.path
            if path == '/':
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                fields = parse_qs(post_data.decode())
                task = fields.get('task', [None])[0]
                edit_id = fields.get('edit_id', [None])[0]
                if edit_id == '0':
                    add_task(task)
                else:
                    edit_task(edit_id, task)
                self.generate_homepage()
            else:
                self.send_response(404)
                self.wfile.write(b'404 Page Not Found')
        except Exception as e:
            print(e)
            self.send_response(500)
            self.wfile.write(b'500 Internal Server Error')
        
if __name__ == '__main__':
    create_db()
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, MyHandler)
    print('server running on port 8080')
    httpd.serve_forever()