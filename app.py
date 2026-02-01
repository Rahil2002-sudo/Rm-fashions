from flask import Flask, render_template, request, redirect, url_for
# With this:
if __name__ == '__main__':
    from models import db, Product
else:
    from .models import db, Product

app = Flask(__name__)
app.config.from_pyfile('config.py')
db.init_app(app)

# Create database tables before first request
# Use application context instead


# Homepage - show all products
@app.route('/')
def home():
    products = Product.query.all()
    return render_template('index.html', products=products)

# Product detail page
@app.route('/product/<int:id>')
def product_detail(id):
    product = Product.query.get(id)
    return render_template('product.html', product=product)

# Add to cart functionality
@app.route('/cart', methods=['POST'])
def add_to_cart():
    product_id = request.form.get('product_id')
    # In a real app, we'd add to a shopping cart here
    return redirect(url_for('checkout'))

# Checkout page
@app.route('/checkout')
def checkout():
    return render_template('checkout.html')
with app.app_context():
    db.create_all()
# Run the application
if __name__ == '__main__':
    app.run(debug=True)