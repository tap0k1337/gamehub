from app import db, app, User, Service, Review, Order

if __name__ == '__main__':
    with app.app_context():
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
