from django.db import models
from django.contrib.auth.models import User

class Entreprise(models.Model):
    name = models.CharField(max_length=60)
    siret_number = models.CharField(max_length=14)
    adress = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='entreprises')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class PhotosEntreprise(models.Model):
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='photos_entreprise/')
    legend = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo {self.legend} - {self.entreprise.name}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username} - Read: {self.is_read}"


class Annonce(models.Model):
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='annonces')
    title = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title


class Client(models.Model):
    # Il faut définir ce modèle, car Candidatures fait référence à Client.
    # S'il s'agit d'un User avec un profil Client, on pourrait aussi envisager un OneToOneField vers User
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    # Ajoute ici d'autres champs spécifiques au client si besoin

    def __str__(self):
        return self.user.username


class Candidature(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='candidatures')
    annonce = models.ForeignKey(Annonce, on_delete=models.CASCADE, related_name='candidatures')
    lettre_motivation = models.TextField()
    cv = models.FileField(upload_to='cvs/')
    status = models.CharField(max_length=20, choices=[
        ('en attente', 'En attente'),
        ('validée', 'Validée'),
        ('refusée', 'Refusée'),
    ], default='en attente')
    date_postulation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Candidature {self.id} - {self.status}"


class CandidatureHistorique(models.Model):
    candidature = models.ForeignKey(Candidature, on_delete=models.CASCADE, related_name='historiques')
    action = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='actions_candidature')
    date_action = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} on {self.candidature} by {self.user}"
