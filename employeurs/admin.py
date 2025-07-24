from django.contrib import admin
from .models import (
    Entreprise, PhotosEntreprise, Annonce, Notification,
    Candidature, CandidatureHistorique, Client
)

@admin.action(description="Marquer comme validée")
def marquer_comme_validee(modeladmin, request, queryset):
    queryset.update(status='validée')

@admin.register(Entreprise)
class EntrepriseAdmin(admin.ModelAdmin):
    list_display = ['name', 'siret_number', 'owner', 'created_at']
    search_fields = ['name', 'siret_number', 'adress', 'owner__username']
    list_filter = ['created_at']

@admin.register(PhotosEntreprise)
class PhotosEntrepriseAdmin(admin.ModelAdmin):
    list_display = ['legend', 'entreprise', 'uploaded_at']
    search_fields = ['legend', 'entreprise__name']
    list_filter = ['uploaded_at']

@admin.register(Annonce)
class AnnonceAdmin(admin.ModelAdmin):
    list_display = ['title', 'entreprise', 'created_at', 'updated_at']
    search_fields = ['title', 'description', 'entreprise__name']
    list_filter = ['entreprise', 'created_at']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'created_at', 'is_read']
    search_fields = ['user__username', 'message']
    list_filter = ['is_read', 'created_at']

@admin.register(Candidature)
class CandidatureAdmin(admin.ModelAdmin):
    list_display = ['client', 'annonce', 'status', 'date_postulation']
    search_fields = ['client__user__username', 'annonce__title', 'status']
    list_filter = ['status', 'date_postulation']
    actions = [marquer_comme_validee]

@admin.register(CandidatureHistorique)
class CandidatureHistoriqueAdmin(admin.ModelAdmin):
    list_display = ['candidature', 'action', 'user', 'date_action']
    search_fields = ['candidature__id', 'action', 'user__username']
    list_filter = ['action', 'date_action']

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['user']
    search_fields = ['user__username', 'user__email']
