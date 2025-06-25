import sqlite3

class UserService:
    def get_all(self):
        with sqlite3.connect("db.sqlite") as conn:
            return conn.execute("SELECT id, name FROM users").fetchall()

    def create(self, name):
        with sqlite3.connect("db.sqlite") as conn:
            conn.execute("INSERT INTO users (name) VALUES (?)", (name,))
            conn.commit()

    def update(self, user_id, name):
        with sqlite3.connect("db.sqlite") as conn:
            conn.execute("UPDATE users SET name = ? WHERE id = ?", (name, user_id))
            conn.commit()

    def delete(self, user_id):
        with sqlite3.connect("db.sqlite") as conn:
            conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
