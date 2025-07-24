import psycopg2
from decouple import config

with open('.env', 'rb') as f:
    content = f.read()
    print(content)

try:
    connection = psycopg2.connect(
        dbname=config('DJANGO_DATABASE'),
        user=config('DJANGO_USER'),
        password=config('DJANGO_PASSWORD'),
        host=config('DJANGO_HOST'),
        port=config('DJANGO_PORT'),
    )
    print("✅ Connexion à la base réussie !")
    connection.close()
except Exception as e:
    print("❌ Échec de la connexion :", e)
