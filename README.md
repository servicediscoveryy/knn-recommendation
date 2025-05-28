 ## 🧠 What is a Recommendation System?

A **recommendation system** is like a smart assistant. It watches what a user is doing — like searching, clicking, or booking — and then **suggests the best services** that the user might like next.

Just like Netflix suggests movies based on what you’ve watched before — we are doing the same here, but for **services** like salons, mechanics, etc.

---

## 🌱 Why Do We Need It?

Without a recommendation system:

- Users have to manually search and scroll to find what they need.
- They might miss better or cheaper services near them.
- Businesses may not reach the right customers.

With a recommendation system:

- 🎯 Users get **personalized suggestions**.
- 🔍 They discover services that match their **interests, habits, and location**.
- 💼 Service providers get more visibility.

---

## ⚙️ How It Works (In Simple Terms)

Here’s how the system thinks:

### 1. **Understand the Services**
We collect data about each service:
- Its **category** (e.g., plumber, tutor, mechanic)
- Its **tags** (keywords like “affordable”, “experienced”)
- Its **location**, **price**, and **popularity**

This helps the system understand what each service is about.

---

### 2. **Understand the User**
We track what the user does:
- Do they **view** a service?
- Do they **book** one?
- Do they **add it to cart** or **review** it?

Each action has a **weight**. For example:
- Booking = high interest
- Just viewing = low interest

This helps us build a **user profile** — a picture of what kind of services the user likes.

---

### 3. **Find a Match**
Once we know:
- What the user likes
- What each service offers

We use a smart algorithm (called **KNN**) to find the **most similar services** to what the user prefers.

---

### 4. **Show Recommendations**
We then show the top 5–10 best matching services for that user.

If we don’t know anything about the user (they’re new), we show the **most popular** services instead.

---

## 📦 How This Is Built (Simplified Tech View)

- 🧾 **MongoDB** – stores users, services, and their actions
- 🧠 **Python + Machine Learning** – builds the brain (recommendation logic)
- 🌐 **Flask API** – provides endpoints like `/recommend`, `/train`
- 🐳 **Docker** – makes the app portable and easy to deploy
- 🚀 **Render** – hosts the app on the internet

---

## 📊 Real-World Example

Imagine a user named Priya:
- She searched for beauty salons
- Viewed 3 and booked 1
- Gave a good review

Now the system understands:
- She likes beauty services
- In a specific area
- In a certain price range

It will now show **similar salons** near her with good prices and good reviews.

Great question! Here’s a super simple guide on **how to use your service recommendation system**, whether you’re a developer, tester, or just curious.

---

## 🚀 How to Use This Recommendation System

Whether you're testing it locally or deploying on a platform like Render, here’s a full step-by-step guide:

---

### 🖥️ 1. Run Locally (Developer)

#### ✅ Prerequisites
- Python installed
- MongoDB Atlas connection URI
- Docker (if using Docker)
- All code cloned from GitHub

---

#### Option 1: Without Docker (Directly)

```bash
# Step 1: Install dependencies
pip install -r requirements.txt

# Step 2: Set MongoDB URI
# Create a file named `.env` and add this:
MONGODB_URI=mongodb+srv://your-user:password@yourcluster.mongodb.net/

# Step 3: Run the app
python app.py
```

Now visit [http://localhost:5000](http://localhost:5000)

---

#### Option 2: With Docker

```bash
# Step 1: Build Docker image
docker build -t recommender-app .

# Step 2: Run the app
docker run -p 10000:10000 -e MONGODB_URI="your-mongo-uri" recommender-app
```

Visit [http://localhost:10000](http://localhost:10000)

---

### 🌐 2. Use the API Routes

Here’s how to interact with the system using a browser or tools like **Postman** or **curl**:

---

#### 🔁 `/train`
Trains the model on current service and category data.

**Example:**
```
GET http://localhost:10000/train
```

Response:
```json
{ "message": "Model trained successfully." }
```

---

#### 👤 `/recommend/<user_id>`
Returns personalized services for a specific user.

**Example:**
```
GET http://localhost:10000/recommend/67dd5c5d726e64ceb0b30617
```

Response:
```json
[
  { "_id": "serviceId1", "title": "Beauty Salon A", ... },
  { "_id": "serviceId2", "title": "Spa B", ... },
  ...
]
```

---

#### 📊 `/evaluate`
Evaluates model performance using sample users (Precision@K).

**Example:**
```
GET http://localhost:10000/evaluate
```

Response:
```json
{ "average_precision": 0.75 }
```


You can now test `/train`, `/recommend`, and `/evaluate` on the internet 🚀
