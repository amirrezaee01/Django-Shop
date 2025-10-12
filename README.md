# Django Shop – Online Shop Backend

A **backend e-commerce platform** built with **Python and Django**, designed to manage products, carts, and orders.  
This project demonstrates backend development skills, including **Django models, CRUD operations, REST API readiness, and Docker setup** for easy development and deployment.

## Features

- User registration, login, and logout
- Product management (CRUD)
- Cart and order system
- REST API-ready architecture
- Dockerized development environment for consistent setup
- SQLite database (default for development)

## Tech Stack

- Backend: Python 3.8+, Django 4.x
- Database: SQLite (development)
- Docker: for containerized development
- Frontend: HTML, CSS (for testing endpoints/templates)
- Version Control: Git & GitHub

## Installation (Docker)

# Clone the repository
git clone https://github.com/amirrezaee01/Django-Shop.git
cd Django-Shop

# Make sure Docker is installed and running

# Build Docker images
docker-compose build

# Start containers (run the app)
docker-compose up

# Apply migrations inside the Django container
docker-compose exec backend python manage.py migrate

# Create a superuser inside the container (for admin access)
docker-compose exec backend python manage.py createsuperuser

# The app is now running at http://127.0.0.1:8000/
