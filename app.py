import os
import json
import smtplib
import requests
from flask import Flask, render_template, request, jsonify
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- Initialize Flask ---
# We explicitly tell Flask where the templates are
app = Flask(__name__, template_folder='templates', static_folder='static')

# Vercel needs the 'app' object to be available at the top level
# This variable name is used by Vercel's Python builder
app = app 

# --- Email Configuration ---
# REMEMBER: You must set these or use environment variables in Vercel
EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS', 'your_email@gmail.com')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', 'your_app_password')
RECIPIENT_EMAIL = os.environ.get('RECIPIENT_EMAIL', 'your_email@gmail.com')

# --- Gemini API Configuration ---
API_KEY = os.environ.get('API_KEY', '')

# --- Web Page Routes ---
@app.route('/')
def index():
    return render_template('rm_fashion_website.html')

@app.route('/product')
def product():
    return render_template('product_page.html')

@app.route('/cart')
def cart():
    return render_template('cart.html')
    
@app.route('/outfit_builder')
def outfit_builder():
    return render_template('outfit_builder.html')

@app.route('/order_success')
def order_success():
    return render_template('order_success.html')

@app.route('/track_order')
def track_order():
    return render_template('track_order.html')

@app.route('/checkout')
def checkout():
    return render_template('checkout.html')

# --- API Routes ---

@app.route('/process_order', methods=['POST'])
def process_order():
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        customer = data.get('customer')
        items = data.get('items')
        total = data.get('total')

        if not all([order_id, customer, items, total]):
            return jsonify({"error": "Missing order details"}), 400
        
        subject = f"Order Placed #{order_id} - RM Fashion"
        body = f"New Order: {order_id}\n\nCustomer: {customer.get('name')}\nItems:\n{items}\nTotal: ₹{total}"
        
        # Simple check to prevent crash if email isn't configured
        if "your_email" in EMAIL_ADDRESS:
            return jsonify({"message": "Order processed (Email not configured)"}), 200

        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAIL, msg.as_string())
        
        return jsonify({"message": "Order email sent."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/payment_confirmed', methods=['POST'])
def handle_payment_confirmed():
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        if not order_id:
            return jsonify({"error": "Missing order ID"}), 400
        # Notification logic here...
        return jsonify({"message": "Payment notification sent."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate_looks', methods=['POST'])
def handle_generate_looks():
    try:
        data = request.get_json()
        prompt = data.get('prompt')
        if not prompt or not API_KEY:
            return jsonify({"error": "AI not available"}), 400
        
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
        payload = { "contents": [{"parts": [{"text": prompt}]}], "generationConfig": { "responseMimeType": "application/json" } }
        response = requests.post(api_url, json=payload)
        result = response.json()

        if result.get("candidates"):
            looks = json.loads(result["candidates"][0]["content"]["parts"][0]["text"])
            return jsonify({"looks": looks}), 200
        return jsonify({"error": "AI failed"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Do not use app.run() here for Vercel

