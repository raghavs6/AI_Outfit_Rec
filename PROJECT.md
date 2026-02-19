1. Project Vision

Build a full-stack AI-powered mobile application that:
	•	Allows users to upload images of their clothing items
	•	Extracts visual features using computer vision
	•	Generates compatible outfits from their own closet
	•	Learns user preferences via swipe feedback
	•	Scales toward real-time, high-performance recommendation systems
    -   

This project is designed to develop strong skills in:
	•	Backend engineering
	•	API design
	•	Database modeling
	•	Machine learning systems
	•	Performance optimization
	

⸻

2. High-Level Goals

Product Goals
	•	Seamless closet upload experience
	•	Personalized outfit recommendations
	•	Inspiration-based matching (Pinterest/Instagram style)
	•	Real-time generation and ranking

Technical Goals
	•	Build a scalable REST API backend
	•	Design proper relational data models
	•	Implement image ingestion pipeline
	•	Integrate embedding-based retrieval
	•	Develop ranking logic
	•	Optimize for low latency
	•	(Advanced) Explore GPU-accelerated scoring

⸻

3. System Architecture (Planned)

Mobile App (React Native / Flutter)
↓
FastAPI Backend (REST API)
↓
PostgreSQL Database
↓
Image Storage (Local → S3)
↓
ML Pipeline
	•	Embedding extraction
	•	Similarity search
	•	Ranking model
↓
Outfit Generation Engine

⸻

4. Core Components

4.1 Backend (FastAPI)

Responsibilities:
	•	User management
	•	Closet item storage
	•	Image upload + validation
	•	Static file serving
	•	Recommendation endpoints
	•	Feedback capture

Key Concepts:
	•	REST APIs
	•	CRUD operations
	•	Dependency injection
	•	Data validation
	•	Error handling
	•	Session management

⸻

4.2 Database (PostgreSQL)

Tables (Planned):

Users
	•	id (UUID, primary key)
	•	created_at

Items
	•	id (UUID)
	•	user_id (foreign key)
	•	category (top/bottom/shoes)
	•	image_url
	•	embedding (vector)
	•	created_at

Swipes
	•	id
	•	user_id
	•	item_ids
	•	liked (boolean)
	•	timestamp

Concepts:
	•	Primary keys
	•	Foreign keys
	•	Indexing
	•	Query optimization

⸻

4.3 Image Pipeline

Stage 1:
	•	Upload via multipart/form-data
	•	Save to disk
	•	Serve via static route

Stage 2:
	•	Background removal
	•	Cropping
	•	Color extraction

Stage 3:
	•	Embedding extraction (vision model)

⸻

4.4 ML System Design

Embedding-Based Retrieval
	•	Extract vector representation per item
	•	Store vectors in database
	•	Use similarity search (cosine distance)

Outfit Generation
	•	Combine Top × Bottom × Shoes
	•	Filter invalid combinations
	•	Score compatibility

Ranking
	•	Learn from swipe feedback
	•	Improve relevance over time

⸻

5. Performance Goals

Short-Term:
	•	<200ms API responses
	•	Efficient DB queries
	•	Minimal blocking I/O

Mid-Term:
	•	Batch embedding extraction
	•	Vector indexing
	•	Cached pair compatibility



⸻

6. Learning Objectives

This project will teach:

Backend Engineering
	•	API architecture
	•	Error handling
	•	Authentication
	•	Modular design

Databases
	•	Schema design
	•	Migrations
	•	Query performance

ML Systems
	•	Data pipelines
	•	Model integration
	•	Retrieval systems
	•	Ranking systems

Systems Engineering
	•	Latency optimization
	•	Resource management
	•	Profiling
	•	Scalability planning

⸻

7. Development Phases

Phase 1 – Backend Foundations
	•	FastAPI setup
	•	Guest users
	•	Image upload
	•	Static serving

Phase 2 – Persistent Storage
	•	PostgreSQL integration
	•	SQLAlchemy models
	•	Migrations

Phase 3 – ML Integration
	•	Embedding extraction
	•	Similarity search
	•	Recommendation endpoint

Phase 4 – Feedback Loop
	•	Swipe capture
	•	Ranking adjustments

Phase 5 – Performance Optimization
	•	Caching
	•	Parallel scoring
	•	Profiling

Phase 6 – Advanced Systems
	•	Vector DB optimization
	•	GPU acceleration
	•	Low-latency inference

⸻

8. Tech Stack

Languages:
	•	Python
	•	SQL
	•	(Planned) C++, CUDA

Backend:
	•	FastAPI
	•	Uvicorn

Database:
	•	PostgreSQL
	•	SQLAlchemy
	•	(Planned) pgvector / FAISS

ML:
	•	Computer Vision Models
	•	Embedding Extraction
	•	Ranking Models

Infrastructure:
	•	Docker
	•	Git
	•	Linux

Mobile:
	•	React Native / Flutter

⸻
⸻

10. Long-Term Vision

Transform into:
	•	A production-ready ML recommendation system
	•	A portfolio-grade ML systems project
	•	A demonstration of scalable backend + AI integration
	•	A foundation for GPU-accelerated combinatorial ranking