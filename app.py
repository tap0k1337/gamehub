from flask import Flask, flash, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func
import json
import logging

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gamehub.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'secret'

db = SQLAlchemy(app)

# === Модель пользователя ===
class User(db.Model):
    __tablename__ = 'users'
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(200), nullable=False)
    role          = db.Column(db.String(20), default='customer')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# === Модель сервиса ===
class Service(db.Model):
    __tablename__ = 'services'
    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(100), nullable=False)
    price       = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    category    = db.Column(db.String(20), nullable=False, default='service')
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user        = db.relationship('User', backref='services')

# === Модель отзыва ===
class Review(db.Model):
    __tablename__ = 'reviews'
    id         = db.Column(db.Integer, primary_key=True)
    rating     = db.Column(db.Integer, nullable=False)
    comment    = db.Column(db.Text)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'),    nullable=False)
    service    = db.relationship('Service', backref='reviews')
    user       = db.relationship('User')

# === Модель заказа ===
class Order(db.Model):
    __tablename__ = 'orders'
    id         = db.Column(db.Integer, primary_key=True)
    buyer_id   = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    items      = db.Column(db.Text, nullable=False)  # JSON-строка [{id,title,price,quantity}, …]
    status     = db.Column(db.String(20), nullable=False, default='pending') 
    created_at = db.Column(db.DateTime, server_default=func.now())

    buyer = db.relationship('User', backref='orders')

# === Главная и регистрация ===
@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role     = request.form.get('role', 'customer')
        if username == 'admin':
            error = 'Регистрация логином "admin" запрещена'
        else:
            existing = User.query.filter_by(username=username).first()
            if existing:
                error = 'Пользователь уже существует'
            else:
                user = User(username=username, role=role)
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                session['user_id'] = user.id
                session['username'] = user.username
                session['role'] = user.role
                if user.role == 'admin':
                    return redirect(url_for('admin_panel'))
                elif user.role == 'seller':
                    return redirect(url_for('my_services'))
                else:
                    return redirect(url_for('index'))
    return render_template('index.html', error=error)

# === О товарах ===
@app.route('/about')
def about():
    return render_template('about.html')

# === Вход ===
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user     = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id']  = user.id
            session['username'] = user.username
            session['role']     = user.role
            if user.role == 'admin':
                return redirect(url_for('admin_panel'))
            elif user.role == 'seller':
                return redirect(url_for('my_services'))
            else:
                return redirect(url_for('index'))
        error = 'Неверный логин или пароль'
    return render_template('login.html', error=error)

# === Выход ===
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# === Каталог ===
@app.route('/catalog')
def catalog():
    selected_category = request.args.get('category', 'all')
    if selected_category == 'all':
        services = Service.query.all()
    else:
        services = Service.query.filter_by(category=selected_category).all()
    review_stats = {}
    for s in services:
        ratings = [r.rating for r in s.reviews]
        avg = round(sum(ratings)/len(ratings),1) if ratings else None
        review_stats[s.id] = {'avg': avg, 'count': len(ratings)}
    return render_template('catalog.html', services=services, review_stats=review_stats, selected_category=selected_category)

# === Отзывы ===
@app.route('/review/<int:service_id>', methods=['GET','POST'])
def review(service_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    service = Service.query.get_or_404(service_id)
    if request.method == 'POST':
        rating  = int(request.form['rating'])
        comment = request.form['comment']
        new_review = Review(rating=rating, comment=comment,
                            service_id=service_id, user_id=session['user_id'])
        db.session.add(new_review)
        db.session.commit()
        return redirect(url_for('catalog'))
    return render_template('review.html', service=service)

# === Корзина ===
@app.route('/cart')
def cart():
    return render_template('cart.html')

# === Оформление заказа ===
@app.route('/checkout', methods=['POST'])
def checkout():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    cart_json = request.form.get('cart_data')
    if not cart_json:
        return "Корзина пуста", 400
    order = Order(buyer_id=session['user_id'], items=cart_json)
    db.session.add(order)
    db.session.commit()
    return redirect(url_for('checkout_success', order_id=order.id))

# === Страница успеха оформления ===
@app.route('/checkout_success/<int:order_id>')
def checkout_success(order_id):
    return render_template('checkout_success.html', order_id=order_id)

# === Фейковая оплата картой с формой ===
@app.route('/pay/<int:order_id>', methods=['GET','POST'])
def pay(order_id):
    order = Order.query.get_or_404(order_id)
    if request.method == 'POST':
        # Эмулируем оплату
        order.status = 'paid'
        db.session.commit()
        # Уведомляем продавцов
        items = json.loads(order.items)
        seller_usernames = set()
        for it in items:
            service_id = it.get('id')
            svc = Service.query.get(service_id) if service_id else None
            if svc and svc.user_id != order.buyer_id:
                seller_usernames.add(svc.user.username)
        for username in seller_usernames:
            logging.info(f"[FAKE MAIL] продавец '{username}': заказ #{order_id} оплачен")
        flash(f"Заказ #{order_id} успешно оплачен!", "success")
        return redirect(url_for('track', order_id=order_id))
    # GET: показываем форму оплаты
    return render_template('payment.html', order_id=order_id)

# === Трекер заказа ===
@app.route('/track/<int:order_id>')
def track(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('track.html', order_id=order.id, status=order.status)

# ===== Новое: Профиль покупателя (список его заказов) =====
@app.route('/profile')
def profile():
    if 'user_id' not in session or session.get('role') != 'customer':
        return redirect(url_for('login'))
    orders = Order.query.filter_by(buyer_id=session['user_id']).order_by(Order.created_at.desc()).all()
    return render_template('profile.html', orders=orders)

# === Добавление услуги ===
@app.route('/add', methods=['GET','POST'])
def add_service():
    if 'user_id' not in session or session.get('role') != 'seller':
        return redirect(url_for('login'))
    if request.method == 'POST':
        new_service = Service(
            title=request.form['title'],
            price=int(request.form['price']),
            description=request.form['description'],
            category=request.form.get('category', 'service'),
            user_id=session['user_id']
        )
        db.session.add(new_service)
        db.session.commit()
        return redirect(url_for('my_services'))
    return render_template('add.html')

# === Мои услуги ===
@app.route('/my-services')
def my_services():
    if 'user_id' not in session or session.get('role') != 'seller':
        return redirect(url_for('login'))
    services = Service.query.filter_by(user_id=session['user_id']).all()
    return render_template('my_services.html', services=services)

# ===== Новое: Список заказов для продавца =====
@app.route('/seller-orders')
def seller_orders():
    if 'user_id' not in session or session.get('role') != 'seller':
        return redirect(url_for('login'))
    # Берём все заказы, в items которых есть хотя бы одна услуга этого продавца
    all_orders = Order.query.filter(Order.status != 'pending').order_by(Order.created_at.desc()).all()
    seller_id = session['user_id']
    seller_orders = []
    for order in all_orders:
        items = json.loads(order.items)
        # Проверяем, содержится ли среди items услуга этого продавца
        for it in items:
            svc = Service.query.get(it.get('id'))
            if svc and svc.user_id == seller_id:
                seller_orders.append(order)
                break
    return render_template('seller_orders.html', orders=seller_orders)

# ===== Новое: Обновление статуса заказа продавцом =====
@app.route('/seller-orders/<int:order_id>/update', methods=['POST'])
def update_seller_order(order_id):
    if 'user_id' not in session or session.get('role') != 'seller':
        return redirect(url_for('login'))
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    if new_status in ('in_progress', 'completed'):
        order.status = new_status
        db.session.commit()
    return redirect(url_for('seller_orders'))

# === Админ-панель ===
@app.route('/admin-panel')
def admin_panel():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    users    = User.query.all()
    services = Service.query.all()
    return render_template('admin_panel.html', users=users, services=services)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
