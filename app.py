from flask import Flask, jsonify, request, session
from flask_cors import CORS
import json
import requests

app = Flask(__name__)
CORS(app)
app.secret_key = 'baxaoptom-secret-key'

# 📁 Fayl yo‘llari
PRODUCTS_FILE = 'products.json'
ORDERS_FILE = 'orders.json'
SETTINGS_FILE = 'settings.json'

# 🔐 Telegram sozlamalari
BOT_TOKEN = "8409191752:AAEgPddZfKIGrFHOSfBnY6OfQTCk3aRHMzo"
CHAT_ID = "5167278754"  # Dostonbek — Azamov.B

# -------------------- Login --------------------
@app.route('/login', methods=['POST'])
def login():
    creds = request.get_json()
    username = creds.get('username')
    password = creds.get('password')

    if username == 'admin' and password == 'baxa123':
        session['admin'] = True
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "fail"})

# -------------------- Buyurtmalar --------------------
@app.route('/order', methods=['POST'])
def receive_order():
    order = request.get_json()
    name = order.get('name')
    price = order.get('price')
    phone = order.get('phone')

    # 📝 Buyurtmani saqlash
    try:
        with open(ORDERS_FILE, 'r+', encoding='utf-8') as f:
            orders = json.load(f)
            orders.append(order)
            f.seek(0)
            json.dump(orders, f, indent=2, ensure_ascii=False)
    except:
        return jsonify({"status": "error", "message": "Buyurtma saqlanmadi"})

    # 📩 Telegramga xabar yuborish
    text = f"🛒 Yangi buyurtma:\n📦 {name}\n💰 {price} so‘m\n📞 {phone}"
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={
            "chat_id": CHAT_ID,
            "text": text
        })
        return jsonify({"status": "sent"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# -------------------- Mahsulotlar --------------------
@app.route('/products', methods=['GET'])
def get_products():
    with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
        products = json.load(f)
    return jsonify(products)

@app.route('/products/add', methods=['POST'])
def add_product():
    new_product = request.get_json()
    with open(PRODUCTS_FILE, 'r+', encoding='utf-8') as f:
        products = json.load(f)
        products.append(new_product)
        f.seek(0)
        json.dump(products, f, indent=2, ensure_ascii=False)
    return jsonify({"status": "added"})

@app.route('/products/delete/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    with open(PRODUCTS_FILE, 'r+', encoding='utf-8') as f:
        products = json.load(f)
        products = [p for p in products if p['id'] != product_id]
        f.seek(0)
        f.truncate()
        json.dump(products, f, indent=2, ensure_ascii=False)
    return jsonify({"status": "deleted"})

@app.route('/products/update/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    updated = request.get_json()
    with open(PRODUCTS_FILE, 'r+', encoding='utf-8') as f:
        products = json.load(f)
        for p in products:
            if p['id'] == product_id:
                p.update(updated)
        f.seek(0)
        f.truncate()
        json.dump(products, f, indent=2, ensure_ascii=False)
    return jsonify({"status": "updated"})

# -------------------- Sozlamalar --------------------
@app.route('/settings', methods=['GET'])
def get_settings():
    with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
        settings = json.load(f)
    return jsonify(settings)

@app.route('/settings/update', methods=['POST'])
def update_settings():
    new_settings = request.get_json()
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(new_settings, f, indent=2, ensure_ascii=False)
    return jsonify({"status": "updated"})

# -------------------- Server --------------------
if __name__ == '__main__':
    app.run(debug=True)