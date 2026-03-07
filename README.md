# PolyLRC

[![Python](https://img.shields.io/badge/python-3.13-blue)](https://www.python.org/)  
[![FastAPI](https://img.shields.io/badge/FastAPI-0.101.0-green)](https://fastapi.tiangolo.com/)  
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

Minimal prediction market platform built with **FastAPI**, **PostgreSQL**, and **Redis** for a computer science final project.  
Phases 1–4 are implemented: user authentication, wallet management, and market creation.

---

## Features Implemented (Phases 1–4)

### 1. User Management
- User registration and login
- JWT-based authentication (access + refresh tokens)
- Password hashing using bcrypt
- Role-based system (admin / user)
- `/users/me` endpoint for retrieving authenticated user profile

### 2. Wallets
- Wallet model with transaction registry
- Faucet on registration (initial credit)
- Credit and debit helper functions
- Balance calculated dynamically (no balance column)

### 3. Markets
- Market creation with multiple outcomes
- Market states: `PRE`, `OPEN`, `CLOSED`, `RESOLUTION`
- Open/close timestamps
- Markets only mutable if `PRE`
- Market listing and detail endpoints
- Market descriptions in Markdown (stored as plain text)

### 4. Infrastructure
- FastAPI backend
- PostgreSQL database
- Alembic migrations for schema versioning
- Redis caching
- Docker + docker-compose support
- Environment-based configuration
- Health check endpoints (`GET /health`, `GET /health/db`)