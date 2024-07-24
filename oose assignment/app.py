from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# Database connection function
def connect_db():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='2005',
        database='shopping_cart'
    )

# Landing Page
@app.route('/')
def index():
    return render_template('index.html')

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return redirect(url_for('store', username=username))
        else:
            return "Invalid login credentials"
    
    return render_template('login.html')

# Signup Page
@app.route('/signup', methods=['GET', 'POST'])
def signup_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        mobile = request.form['mobile']
        
        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password, name, mobile) VALUES (%s, %s, %s, %s)", 
                           (username, password, name, mobile))
            conn.commit()
            conn.close()
            return redirect(url_for('login_page'))
        except mysql.connector.IntegrityError:
            conn.close()
            return "Username already exists"
    
    return render_template('signup.html')

# Store Page
@app.route('/store/<username>', methods=['GET', 'POST'])
def store(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    
    if request.method == 'POST':
        product_id = request.form['product_id']
        quantity = int(request.form['quantity'])
        
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
        product = cursor.fetchone()
        
        if not product:
            return "Product not found!"
        
        cursor.execute("INSERT INTO cart (username, product_id, quantity) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE quantity = quantity + %s", 
                       (username, product_id, quantity, quantity))
        
        conn.commit()
        conn.close()
        return redirect(url_for('store', username=username))
    
    return render_template('store.html', products=products, username=username)

# Add to Cart
@app.route('/add_to_cart/<username>', methods=['POST'])
def add_to_cart(username):
    product_id = request.form['product_id']
    quantity = int(request.form['quantity'])
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
    product = cursor.fetchone()
    
    if not product:
        return "Product not found!"
    
    cursor.execute("INSERT INTO cart (username, product_id, quantity) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE quantity = quantity + %s", 
                   (username, product_id, quantity, quantity))
    
    conn.commit()
    conn.close()
    return redirect(url_for('store', username=username))

# Cart Page
@app.route('/cart/<username>')
def cart(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT p.name, p.price, c.quantity FROM cart c JOIN products p ON c.product_id = p.product_id WHERE c.username = %s", (username,))
    cart_details = cursor.fetchall()
    conn.close()
    return render_template('cart.html', cart=cart_details, username=username)

# Generate Bill
@app.route('/generate_bill/<username>')
def generate_bill(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT p.name, p.price, c.quantity FROM cart c JOIN products p ON c.product_id = p.product_id WHERE c.username = %s", (username,))
    cart_items = cursor.fetchall()
    total_amount = sum(item[1] * item[2] for item in cart_items)
    conn.close()
    return render_template('bill.html', cart_items=cart_items, total_amount=total_amount)

if __name__ == '__main__':
    app.run(debug=True)
