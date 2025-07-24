from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include
from candidats import views

urlpatterns = [
	path("", views.home, name="home"),
	path('admin/', admin.site.urls),
	path('connexion/', LoginView.as_view(template_name='candidats/connexion.html'), name='connexion'),
	path('deconnexion/', LogoutView.as_view(next_page='connexion'), name='deconnexion'),
	path('accounts/profile', views.account, name='account'),
	path('entreprise/creer/', views.entreprise_create, name='entreprise_create'),
	path('entreprise/<int:pk>/modifier/', views.entreprise_update, name='entreprise_update'),
	path('entreprise/<int:pk>/supprimer/', views.entreprise_delete, name='entreprise_delete'),
	path('inscription/', views.inscription, name='inscription'),
	path('entreprise/<int:entreprise_id>/', views.entreprise_detail, name='entreprise_detail'),
	path('postuler/<int:annonce_id>/', views.postuler, name='postuler'),
]
