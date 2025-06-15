from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from apyori import apriori
from collections import defaultdict

app = Flask(__name__)

# MongoDB connection
client = MongoClient("mongodb+srv://servicediscovery:%40Service2025@cluster0.pjqjt.mongodb.net")
db = client["servicediscovery"]
bookings_collection = db["bookings"]
services_collection = db["services"]

# Step 1: Fetch bookings from MongoDB
print("Fetching bookings from MongoDB...")
bookings_raw = list(bookings_collection.find({}))
print(f"Total bookings fetched: {len(bookings_raw)}")

# Step 2: Group services by orderId
order_transactions = defaultdict(list)

for booking in bookings_raw:
    try:
        order_id = booking.get("orderId")
        service_id = booking.get("serviceId")

        if not order_id or not service_id:
            continue

        service = services_collection.find_one({"_id": ObjectId(service_id)})
        if not service or not service.get("title"):
            continue

        service_title = service["title"].strip().lower()

        if service_title not in order_transactions[order_id]:
            order_transactions[order_id].append(service_title)
    except Exception as e:
        print(f"Error processing booking: {e}")

# Step 3: Prepare transactions
unique_transactions = list(order_transactions.values())
print(f"Total unique transactions for training: {len(unique_transactions)}")

# Step 4: Run Apriori
min_support = 0.2
min_confidence = 0.3
print(f"Running Apriori with min_support={min_support}, min_confidence={min_confidence}...")
results = apriori(unique_transactions, min_support=min_support, min_confidence=min_confidence)

# Step 5: Build bidirectional recommendation dictionary
recommendation_dict = defaultdict(list)

for rule in results:
    for stat in rule.ordered_statistics:
        base_items = list(stat.items_base)
        add_items = list(stat.items_add)
        if len(base_items) == 1 and len(add_items) == 1:
            base = base_items[0]
            add = add_items[0]
            confidence = round(stat.confidence, 2)

            if (add, confidence) not in recommendation_dict[base]:
                recommendation_dict[base].append((add, confidence))

            # Reverse direction
            if (base, confidence) not in recommendation_dict[add]:
                recommendation_dict[add].append((base, confidence))

# Step 6: Recommendation function
def get_recommendations(service_name):
    service_name = service_name.lower().strip()
    if service_name in recommendation_dict:
        sorted_recs = sorted(recommendation_dict[service_name], key=lambda x: x[1], reverse=True)
        return [item for item, _ in sorted_recs]
    else:
        return []

# Step 7: Flask route
@app.route("/recommendations", methods=["GET"])
def recommendations():
    service_query = request.args.get("service", "").strip()
    if not service_query:
        return jsonify({"error": "Missing `service` query parameter"}), 400

    recommended = get_recommendations(service_query)
    return jsonify({
        "service": service_query,
        "recommendations": recommended
    })

# Step 8: Run the server
if __name__ == "__main__":
    print("📡 Server starting at http://localhost:5000")
    app.run(host="0.0.0.0", port=5000)
