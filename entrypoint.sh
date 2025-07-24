#!/bin/sh

# Attendre que PostgreSQL soit prêt
echo "🕒 Attente que la base de données soit prête..."
while ! nc -z db 5432; do
  sleep 1
done
echo "✅ Base de données prête !"

# Commandes Django
python manage.py makemigrations
python manage.py migrate
python manage.py create_superuser_if_none_exists
python manage.py runserver 0.0.0.0:8000
