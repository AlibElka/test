from flask import Flask, request, jsonify, send_from_directory
from functools import wraps
import uuid, time, os

app = Flask(__name__, static_folder="static")

# --- In-memory storage ---
users = {
    "user@test.com": {"password": "Test1234!", "name": "Иван Петров"}
}
sessions = {}   # token -> email
events = {
    1: {"id": 1, "title": "Концерт Imagine Dragons", "date": "2025-07-15", "category": "concert", "price": 4500, "seats": 120},
    2: {"id": 2, "title": "Спектакль «Чайка»",      "date": "2025-07-20", "category": "theatre", "price": 2800, "seats": 80},
    3: {"id": 3, "title": "Кино: Дюна 3",            "date": "2025-07-22", "category": "cinema",  "price": 900,  "seats": 200},
    4: {"id": 4, "title": "Джазовый вечер",          "date": "2025-07-28", "category": "concert", "price": 3200, "seats": 60},
    5: {"id": 5, "title": "Балет «Лебединое озеро»", "date": "2025-08-02", "category": "theatre", "price": 5000, "seats": 150},
}
bookings = {}   # booking_id -> booking dict
_booking_counter = 1

def auth_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        token = auth.replace("Bearer ", "").strip()
        if token not in sessions:
            return jsonify({"error": "Unauthorized"}), 401
        request.user_email = sessions[token]
        return f(*args, **kwargs)
    return wrapper

# --- Serve frontend ---
@app.route("/")
def index():
    return send_from_directory("static", "index.html")

# --- Auth ---
@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.json or {}
    email, password, name = data.get("email"), data.get("password"), data.get("name", "")
    if not email or not password:
        return jsonify({"error": "email and password required"}), 400
    if email in users:
        return jsonify({"error": "User already exists"}), 409
    users[email] = {"password": password, "name": name}
    return jsonify({"message": "Registered successfully"}), 201

@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.json or {}
    email, password = data.get("email"), data.get("password")
    user = users.get(email)
    if not user or user["password"] != password:
        return jsonify({"error": "Invalid credentials"}), 401
    token = str(uuid.uuid4())
    sessions[token] = email
    return jsonify({"session_token": token, "name": user["name"]}), 200

@app.route("/api/auth/logout", methods=["POST"])
@auth_required
def logout():
    auth = request.headers.get("Authorization", "")
    token = auth.replace("Bearer ", "").strip()
    sessions.pop(token, None)
    return jsonify({"message": "Logged out"}), 200

# --- Catalog ---
@app.route("/api/events", methods=["GET"])
def get_events():
    category = request.args.get("category")
    date = request.args.get("date")
    result = list(events.values())
    if category:
        result = [e for e in result if e["category"] == category]
    if date:
        result = [e for e in result if e["date"] == date]
    return jsonify(result), 200

@app.route("/api/events/<int:event_id>", methods=["GET"])
def get_event(event_id):
    event = events.get(event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404
    return jsonify(event), 200

# --- Booking ---
@app.route("/api/booking/create", methods=["POST"])
@auth_required
def create_booking():
    global _booking_counter
    data = request.json or {}
    event_id = data.get("event_id")
    event = events.get(event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404
    booking_id = _booking_counter
    _booking_counter += 1
    bookings[booking_id] = {
        "booking_id": booking_id,
        "event_id": event_id,
        "event_title": event["title"],
        "event_date": event["date"],
        "price": event["price"],
        "user_email": request.user_email,
        "status": "pending",
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S")
    }
    return jsonify(bookings[booking_id]), 200

@app.route("/api/booking/<int:booking_id>", methods=["GET"])
@auth_required
def get_booking(booking_id):
    booking = bookings.get(booking_id)
    if not booking:
        return jsonify({"error": "Booking not found"}), 404
    if booking["user_email"] != request.user_email:
        return jsonify({"error": "Forbidden"}), 403
    return jsonify(booking), 200

@app.route("/api/booking/my", methods=["GET"])
@auth_required
def my_bookings():
    user_bookings = [b for b in bookings.values() if b["user_email"] == request.user_email]
    return jsonify(user_bookings), 200

@app.route("/api/booking/<int:booking_id>/cancel", methods=["POST"])
@auth_required
def cancel_booking(booking_id):
    booking = bookings.get(booking_id)
    if not booking:
        return jsonify({"error": "Booking not found"}), 404
    if booking["user_email"] != request.user_email:
        return jsonify({"error": "Forbidden"}), 403
    if booking["status"] == "paid":
        return jsonify({"error": "Cannot cancel a paid booking"}), 409
    booking["status"] = "cancelled"
    return jsonify(booking), 200

# --- Payment ---
@app.route("/api/payment/pay", methods=["POST"])
@auth_required
def pay():
    data = request.json or {}
    booking_id = data.get("booking_id")
    card_token = data.get("card_token", "")
    booking = bookings.get(booking_id)
    if not booking:
        return jsonify({"error": "Booking not found"}), 404
    if booking["status"] == "paid":
        return jsonify({"error": "Booking already paid"}), 409
    if booking["status"] == "cancelled":
        return jsonify({"error": "Booking is cancelled"}), 409
    if card_token == "tok_test_decline":
        booking["status"] = "failed"
        return jsonify({"payment_status": "declined", "booking_status": "failed"}), 402
    booking["status"] = "paid"
    return jsonify({"payment_status": "success", "booking_status": "paid", "booking_id": booking_id}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)
