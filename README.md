# plateforme_candidature

## introduction
Le but de ce projet est de faire une plateforme de candidature.</br>
Dans ce projet il faudra : 
- une partie administrateur pour :
  - creer une fiche de poste a pourvoir
  - modifier une fiche de poste
  - supprimer une fiche de poste
- une partie client pour :
  - se creer un profil
  - modifier son profil
  - supprimer son profil
  - avoir acces au poste non pourvu
  - deposer une candidature
  - deposer des photos
  - creer une entreprise
  - modifier une entreprise
  - supprimer une entreprise

Les vues minimales sont pour le client : 
- page de connexion
- le dashboard avec les cnadidatures deposees
- la page avec l'enssemble des offres
- la page du profile
- la page contenant le details d'une annonce pour pouvoir postuler

Quant à l'admin, les vues minimales sont : 
- Dashboard avec candidats ayant postulé sur leurs annonces
- Page contenant le détail d’une annonce, d’où ils pourront valider ou invalider les candidatures
- Page du profil (avec photo)
- Notification lorsqu’un candidat postule une de mes annonces (Signals)

## Lancement du projet
Avant de lancer le projet, plusieurs actions sont à realiser. 
### .env
Tout d'abord il faut copier coller le .env.example et le renommer .env afin de mettre les 
valeurs pour la base de donnee
### docker
Ensuite, une fois le .env creer, il faut faire un `docker compose up --build -d` afin de 
lancer le container docker et d'executer le dockerfile pour installer les dependances
python et demarrer les serveur en amont.

