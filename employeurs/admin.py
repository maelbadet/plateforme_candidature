import csv

from django.contrib import admin
from django import forms
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import path
from .models import (
    Entreprise, PhotosEntreprise, Annonce, Notification,
    Candidature, CandidatureHistorique, Client
)

@admin.action(description="Marquer comme validée")
def marquer_comme_validee(modeladmin, request, queryset):
    queryset.update(status='validée')

class CsvImportForm(forms.Form):
    csv_file = forms.FileField()

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
    list_display = ('id', 'client', 'annonce', 'status', 'date_postulation')
    search_fields = ['client__user__username', 'annonce__title', 'status']
    list_filter = ['status', 'date_postulation']
    actions = [marquer_comme_validee]
    change_list_template = "admin/candidature_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export_csv/', self.admin_site.admin_view(self.export_csv)),
            path('import_csv/', self.admin_site.admin_view(self.import_csv)),
        ]
        return custom_urls + urls

    def export_csv(self, request):
        return redirect('export_candidatures')

    def import_csv(self, request):
        if request.method == "POST":
            form = CsvImportForm(request.POST, request.FILES)
            if form.is_valid():
                file = form.cleaned_data['csv_file']
                decoded = file.read().decode('utf-8').splitlines()
                reader = csv.DictReader(decoded)
                for row in reader:
                    try:
                        client = Client.objects.get(user__username=row['Client'])
                        annonce = Annonce.objects.get(title=row['Annonce'])
                        Candidature.objects.create(
                            client=client,
                            annonce=annonce,
                            lettre_motivation=row.get('Lettre', ''),
                            cv='default.pdf',
                            status=row['Status']
                        )
                    except Exception as e:
                        messages.error(request, f"Erreur ligne {row}: {e}")
                self.message_user(request, "Importation réussie !", messages.SUCCESS)
                return HttpResponseRedirect("../")
        else:
            form = CsvImportForm()
        return render(request, "admin/csv_form.html", {"form": form})

@admin.register(CandidatureHistorique)
class CandidatureHistoriqueAdmin(admin.ModelAdmin):
    list_display = ['candidature', 'action', 'user', 'date_action']
    search_fields = ['candidature__id', 'action', 'user__username']
    list_filter = ['action', 'date_action']

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['user']
    search_fields = ['user__username', 'user__email']