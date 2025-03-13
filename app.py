from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SECRET_KEY'] = 'tajny_klic'
db = SQLAlchemy(app)

# Model pro produkty
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(200), nullable=True)

order_product = db.Table(
    'order_product',
    db.Column('order_id', db.Integer, db.ForeignKey('order.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True)
)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    products = db.relationship('Product', secondary='order_product')

# Vytvoření databáze
with app.app_context():
    db.create_all()

# Hlavní stránka - seznam produktů
@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

# Přidání produktu (pro testování)
@app.route('/add_product', methods=['POST'])
def add_product():
    name = request.form['name']
    price = float(request.form['price'])
    image = request.form['image']
    new_product = Product(name=name, price=price, image=image)
    db.session.add(new_product)
    db.session.commit()
    return redirect(url_for('index'))

# Přidání do košíku
@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = []
    session['cart'].append(product_id)
    session.modified = True
    return redirect(url_for('index'))

# Zobrazení košíku
@app.route('/cart')
def cart():
    cart_items = []
    if 'cart' in session:
        cart_items = Product.query.filter(Product.id.in_(session['cart'])).all()
    return render_template('cart.html', cart_items=cart_items)

# Vyprázdnění košíku
@app.route('/clear_cart')
def clear_cart():
    session.pop('cart', None)
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['POST'])
def checkout():
    if 'cart' not in session or not session['cart']:
        flash("Košík je prázdný!", "danger")
        return redirect(url_for('cart'))

    name = request.form['name']
    email = request.form['email']
    address = request.form['address']
    
    cart_items = Product.query.filter(Product.id.in_(session['cart'])).all()
    total_price = sum(item.price for item in cart_items)

    new_order = Order(name=name, email=email, address=address, total_price=total_price, products=cart_items)
    db.session.add(new_order)
    db.session.commit()

    session.pop('cart', None)
    flash("Objednávka byla úspěšně vytvořena!", "success")
    return redirect(url_for('orders'))

# Zobrazení objednávek
@app.route('/orders')
def orders():
    all_orders = Order.query.all()
    return render_template('orders.html', orders=all_orders)

if __name__ == '__main__':
    app.run(debug=True)