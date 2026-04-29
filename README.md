# Real Time E-Commerce Recommendation System (End-to-End ML pipeline)
This project implements a production style, end-to-end machine learning system for real-time product recommendations in an e-commerce setting.

The system simulates how modern large scale platforms (Amazon, Walmart, etc.) deliver personalized recommendations by combining:

- User interaction tracking (events)
- Candidate generation
- Machine learning-based ranking
- Event-driven data pipelines
- Training and inference workflows

When a user interacts with an e-commerce application (e.g., views or clicks a product), the system must:

1. Retrieve a set of relevant candidate products
2. Rank them using a machine learning model
3. Return personalized recommendations in real time
4. Capture user behavior for future learning

This project simulates that entire lifecycle.

The system follows a multi-stage recommendation architecture:

User → Backend → Candidate Generation → ML Ranking → Response  
        │  
        └── Events → Streaming → Training Pipeline → Model Update


# Machine Learning Approach
The recommendation system is implemented as a multi-stage pipeline:

1. Candidate Generation
   - Retrieves a subset of products using category, popularity, and similarity heuristics

2. Ranking Model
   - Predicts relevance of a product given:
     - user features
     - product features
     - contextual signals

3. Model Types
   - Baseline: Gradient Boosting / XGBoost
   - Advanced: PyTorch-based neural ranking model

4. Evaluation Metrics
   - Recall@K
   - Mean Reciprocal Rank (MRR)
   - AUC (for classification)


# Data Pipeline
Synthetic data is generated to simulate realistic e-commerce behavior.

### Tables

- `products` → catalog metadata
- `users` → user profiles
- `events` → behavioral interactions

### Event Types

- view
- click
- add_to_cart
- purchase

### Key Feature

User interactions are biased toward preferred categories to simulate real-world behavior patterns.         


# Training Pipeline
The training pipeline performs:

1. Data extraction from PostgreSQL
2. Feature engineering:
   - user preferences
   - product attributes
   - interaction features
3. Label generation (positive/negative samples)
4. Model training
5. Evaluation and metric tracking
6. Model artifact export

Frameworks used:
- PyTorch
- scikit-learn
- pandas


# Inference Pipeline
During real-time inference:

1. User sends request via API
2. Backend retrieves candidate products
3. ML service scores candidates
4. Top-K results are returned
5. Event is logged for future learning

Latency considerations:
- candidate filtering
- caching (Redis)
- lightweight feature computation


# Event Driven Architecture
User actions are captured and streamed using Kafka/Redpanda.

Events include:
- product views
- clicks
- add-to-cart
- purchases

Consumers:
- feature update service
- training data builder
- analytics pipeline

This enables continuous learning and system improvement.


# Tech Stack
### Backend
- Node.js (Express)

### Machine Learning
- Python
- PyTorch
- scikit-learn

### Data
- PostgreSQL
- Redis

### Streaming
- Kafka / Redpanda

### DevOps
- Docker
- Docker Compose
- GitHub Actions (CI/CD)

### Others
- pandas, numpy


# Setup Instructions
### 1. Clone the repository
git clone <your-repo-url>
cd realtime-recsys

### 2. Set up PostgreSQL
- Create database: recsys
- Run schema: infra/init-db/init.sql

### 3. Generate synthetic data
cd training-pipeline
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/generate_synthetic_data.py

### 4. Verify data
SELECT COUNT(*) FROM products;
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM events;