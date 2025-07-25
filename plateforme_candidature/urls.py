from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include
from candidats import views
from employeurs import views as employeurs_views
from plateforme_candidature import settings

urlpatterns = [
	path("", views.home, name="home"),
	path('admin/', admin.site.urls),
	path('connexion/', LoginView.as_view(template_name='candidats/connexion.html'), name='connexion'),
	path('deconnexion/', LogoutView.as_view(next_page='connexion'), name='deconnexion'),
	path('accounts/profile', views.account, name='account'),
	path('profil-candidat/<int:pk>/', views.profil_candidat, name='profil_candidat'),
	path('candidature/<int:candidature_id>/changer-statut/', views.changer_statut_candidature,
	     name='changer_statut_candidature'),
	path('entreprise/<int:entreprise_id>/annonces/', employeurs_views.mes_annonces, name='mes_annonces'),
	path('entreprise/<int:entreprise_id>/annonces/creer/', employeurs_views.creer_annonce, name='creer_annonce'),
	path('entreprise/<int:entreprise_id>/annonces/<int:annonce_id>/modifier/', employeurs_views.modifier_annonce,
	     name='modifier_annonce'),
	path('entreprise/<int:entreprise_id>/annonces/<int:annonce_id>/supprimer/', employeurs_views.supprimer_annonce,
	     name='supprimer_annonce'),
	path('notifications/', employeurs_views.notifications, name='notifications'),
	# urls.py
	path('notification/<int:notification_id>/lire/', employeurs_views.lire_notification, name='lire_notification'),
	path('entreprise/creer/', views.entreprise_create, name='entreprise_create'),
	path('entreprise/<int:pk>/modifier/', views.entreprise_update, name='entreprise_update'),
	path('entreprise/<int:pk>/supprimer/', views.entreprise_delete, name='entreprise_delete'),
	path('inscription/', views.inscription, name='inscription'),
	path('entreprise/<int:entreprise_id>/', views.entreprise_detail, name='entreprise_detail'),
	path('postuler/<int:annonce_id>/', views.postuler, name='postuler'),
	path('api/export-candidatures/', employeurs_views.export_candidatures_csv, name='export_candidatures'),
	path('api/check-notifications/', employeurs_views.check_notifications, name='check_notifications'),

]
if settings.DEBUG:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
