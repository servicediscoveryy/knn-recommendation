import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
import pymongo
from bson.objectid import ObjectId
from collections import defaultdict
import math
from dotenv import load_dotenv
import os
load_dotenv()
MONGO_URI = "mongodb+srv://servicediscovery:%40Service2025@cluster0.pjqjt.mongodb.net"

# Mock MongoDB connection (replace with your actual connection)
client = pymongo.MongoClient(MONGO_URI)
db = client["servicediscovery"]

# Interaction weights
INTERACTION_WEIGHTS = {
    "book": 1.0,
    "review": 0.8,
    "cart": 0.6,
    "view": 0.4,
    "search": 0.2,
}


class ServiceRecommender:
    def __init__(self):
        self.db = db
        self.user_profiles = {}
        self.service_vectors = {}
        self.knn_model = None
        self.vectorizer = TfidfVectorizer()
        self.scaler = MinMaxScaler()
        self.category_map = {}
        self.location_map = {}

    def load_data(self):
        """Load data from MongoDB and preprocess"""
        # Get all categories and create mapping
        categories = db.categories.find()
        self.category_map = {str(cat["_id"]): idx for idx, cat in enumerate(categories)}

        print(self.category_map)

        # Get all services
        services = db.services.find()
        service_data = []

        # Create feature vectors for services
        for service in services:
            service_id = str(service["_id"])

            # Basic features
            features = {
                "category": self.category_map.get(str(service["category"]), -1),
                "tags": " ".join(service.get("tags", [])),
                "location": service["location"],
                "views": service.get("views", 0),
                "price": service.get("price", 0),
            }

            service_data.append((service_id, features))
        print(service_data)
        return service_data

    def preprocess_services(self, service_data):
        """Convert service data into feature vectors"""
        # Process tags with TF-IDF
        tags = [data["tags"] for _, data in service_data]
        tags_tfidf = self.vectorizer.fit_transform(tags)

        # Process locations (create unique mapping)
        all_locations = list(set(data["location"] for _, data in service_data))
        self.location_map = {loc: idx for idx, loc in enumerate(all_locations)}

        # Create final vectors
        vectors = []
        service_ids = []

        for service_id, data in service_data:
            # One-hot encode category
            category_vec = np.zeros(len(self.category_map))
            if data["category"] != -1:
                category_vec[data["category"]] = 1

            # Get location index
            location_idx = self.location_map.get(data["location"], -1)

            # Combine all features
            vector = np.concatenate(
                [
                    category_vec,
                    tags_tfidf[service_data.index((service_id, data))].toarray()[0],
                    np.array([location_idx, data["views"], data["price"]]),
                ]
            )

            vectors.append(vector)
            service_ids.append(service_id)

        # Normalize numerical features
        vectors = self.scaler.fit_transform(vectors)

        # Store in dictionary
        self.service_vectors = {sid: vec for sid, vec in zip(service_ids, vectors)}

        print(vectors[0], service_ids[0])

        return vectors, service_ids

    def build_user_profile(self, user_id):
        """Create a weighted user profile based on interactions"""
        interactions = list(db.userinteractions.find({"userId": ObjectId(user_id)}))
        if not interactions:
            return None

        # Initialize profile components
        category_weights = defaultdict(float)
        tag_weights = defaultdict(float)
        location_weights = defaultdict(float)
        total_weight = 0.0

        # Process each interaction
        for interaction in interactions:
            service = db.services.find_one({"_id": interaction["serviceId"]})
            if not service:
                continue

            weight = INTERACTION_WEIGHTS.get(interaction["actionType"], 0.1)
            total_weight += weight

            # Update category preference
            category_id = str(service["category"])
            category_weights[category_id] += weight

            # Update tag preferences
            for tag in service.get("tags", []):
                tag_weights[tag] += weight

            # Update location preference
            location = service["location"]
            location_weights[location] += weight

        if total_weight == 0:
            return None

        # Normalize weights
        category_vec = np.zeros(len(self.category_map))
        for cat_id, weight in category_weights.items():
            idx = self.category_map.get(cat_id, -1)
            if idx != -1:
                category_vec[idx] = weight / total_weight

        # Get top tags (normalized)
        top_tags = sorted(tag_weights.items(), key=lambda x: x[1], reverse=True)[:10]
        tags_vec = np.zeros(len(self.vectorizer.vocabulary_))
        for tag, weight in top_tags:
            if tag in self.vectorizer.vocabulary_:
                idx = self.vectorizer.vocabulary_[tag]
                tags_vec[idx] = weight / total_weight

        # Get preferred location
        preferred_location = max(location_weights.items(), key=lambda x: x[1])[0]
        location_idx = self.location_map.get(preferred_location, -1)

        # Create final user vector
        user_vec = np.concatenate(
            [
                category_vec,
                tags_vec,
                np.array([location_idx, 0, 0]),  # Placeholder for views and price
            ]
        )

        # Store user profile
        self.user_profiles[user_id] = user_vec
        return user_vec

    def train_knn(self, n_neighbors=5):
        """Train KNN model on service vectors"""
        vectors = list(self.service_vectors.values())
        service_ids = list(self.service_vectors.keys())

        if len(vectors) == 0:
            raise ValueError("No service vectors available")

        self.knn_model = NearestNeighbors(n_neighbors=n_neighbors, metric="cosine")
        self.knn_model.fit(vectors)
        return self.knn_model

    def recommend_services(self, user_id, n_recommendations=5):
        """Generate recommendations for a user"""
        # Build user profile if not exists
        if user_id not in self.user_profiles:
            user_profile = self.build_user_profile(user_id)
            if user_profile is None:
                # Fallback to popular services
                return self.get_popular_services(n_recommendations)

        user_vec = self.user_profiles[user_id]

        # Find nearest neighbors
        distances, indices = self.knn_model.kneighbors(
            [user_vec], n_neighbors=n_recommendations
        )

        # Get recommended service IDs
        all_service_ids = list(self.service_vectors.keys())
        recommended_ids = [all_service_ids[idx] for idx in indices[0]]

        # Get full service details
        recommended_services = []
        for service_id in recommended_ids:
            service = db.services.find_one({"_id": ObjectId(service_id)})
            if service:
                recommended_services.append(service)

        return recommended_services

    def get_popular_services(self, limit=5):
        """Fallback method when user has no interactions"""
        return list(db.services.find().sort("views", -1).limit(limit))

    def evaluate_model(self, test_users, k=5):
        """Evaluate recommendations using Precision@K"""
        precisions = []

        for user_id in test_users:
            interactions = list(db.userinteractions.find({"userId": ObjectId(user_id)}))
            true_services = set([str(inter["serviceId"]) for inter in interactions])

            if not true_services:
                continue

            recommendations = self.recommend_services(user_id, n_recommendations=k)
            recommended_ids = [str(service["_id"]) for service in recommendations]

            # Calculate Precision@K
            hits = sum([1 for rec_id in recommended_ids if rec_id in true_services])
            precision = hits / k
            precisions.append(precision)

        if precisions:
            avg_precision = sum(precisions) / len(precisions)
        else:
            avg_precision = 0.0

        print(f"Average Precision@{k}: {avg_precision:.4f}")
        return avg_precision


# # Example usage
# if __name__ == "__main__":
#     recommender = ServiceRecommender()

#     # Load and preprocess data
#     service_data = recommender.load_data()
#     vectors, service_ids = recommender.preprocess_services(service_data)

#     # Train KNN model
#     recommender.train_knn(n_neighbors=10)

#     # Generate recommendations for a user
#     user_id = "67dd5c5d726e64ceb0b30617"  # Replace with actual user ID
#     recommendations = recommender.recommend_services(user_id)

#     print("Recommended Services:")
#     for idx, service in enumerate(recommendations, 1):
#         print(f"{idx}. {service['title']} (Category: {service['category']})")

#     # ✅ Evaluate the model
#     test_user_ids = [
#         user["_id"] for user in db.users.find().limit(10)
#     ]  # Example: get first 10 users
#     recommender.evaluate_model(test_user_ids, k=5)
