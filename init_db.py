from app import db, app, User, Service, Review, Order
import os

DB_PATH = os.path.join(app.instance_path, 'gamehub.db')

if __name__ == '__main__':
    with app.app_context():
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
            print("🗑 Старый файл базы удалён")
        db.create_all()
        print("✅ Таблицы успешно созданы.")

        # Создание администратора, если его нет
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', role='admin')
            admin.set_password('admin')
            db.session.add(admin)
            db.session.commit()
            print("🔐 Админ создан: логин = admin, пароль = admin")
        else:
            print("⚠️ Админ уже существует")
