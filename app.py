# app.py

from flask import Flask, jsonify
from recommendation_engine import ServiceRecommender
from bson import ObjectId

app = Flask(__name__)
recommender = ServiceRecommender()


@app.route("/train", methods=["POST"])
def train():
    try:
        service_data = recommender.load_data()
        recommender.preprocess_services(service_data)
        recommender.train_knn(n_neighbors=10)
        return jsonify({"message": "Model trained successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/recommend/<user_id>", methods=["GET"])
def recommend(user_id):
    try:
        recommendations = recommender.recommend_services(user_id)
        result = [
            {
                "id": str(service["_id"]),
                "title": service.get("title"),
                "category": str(service.get("category")),
            }
            for service in recommendations
        ]
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/evaluate", methods=["GET"])
def evaluate():
    try:
        test_user_ids = [
            str(user["_id"]) for user in recommender.db.users.find().limit(10)
        ]
        score = recommender.evaluate_model(test_user_ids, k=5)
        return jsonify({"precision@5": score})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
