from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, F
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.views.decorators.http import require_POST

from candidats.forms import CustomUserCreationForm, UserUpdateForm, EntrepriseCreateForm, PhotoEntrepriseForm, \
	AnnonceForm
from employeurs.models import *


def home(request):
	user = request.user
	unread_notifications = []
	if user.is_authenticated and hasattr(user, 'notifications'):
		unread_notifications = user.notifications.filter(is_read=False)
	client = getattr(user, 'client_profile', None)
	if client:
		entreprises = Entreprise.objects.annotate(
			total_annonces=Count('annonces', distinct=True),
			annonces_validees=Count(
				'annonces',
				filter=Q(
					annonces__candidatures__client=client,
					annonces__candidatures__status='validée'
				),
				distinct=True
			)
		)
		entreprises_visibles = entreprises.exclude(total_annonces=F('annonces_validees'))
	else:
		entreprises_visibles = Entreprise.objects.all()
	return render(request, 'candidats/index.html', {
		'entreprises': entreprises_visibles,
		'unread_notifications': unread_notifications
	})


def connexion(request):
	return render(request, 'candidats/connexion.html')


def inscription(request):
	form = CustomUserCreationForm(request.POST or None)
	if request.method == 'POST' and form.is_valid():
		user = form.save()
		Client.objects.create(user=user)
		login(request, user)
		return redirect('home')
	return render(request, 'candidats/inscription.html', {'form': form})


def account(request):
	user = request.user
	client = getattr(user, 'client_profile', None)
	if request.method == 'POST':
		u_form = UserUpdateForm(request.POST, instance=user)
		e_form = EntrepriseCreateForm(request.POST)
		p_form = PhotoEntrepriseForm(request.POST, request.FILES)
		if 'update_user' in request.POST and u_form.is_valid():
			u_form.save()
			return redirect('account')
		if 'create_entreprise' in request.POST and e_form.is_valid():
			entreprise = e_form.save(commit=False)
			entreprise.owner = user
			entreprise.save()
			return redirect('account')
		if 'upload_photo' in request.POST and p_form.is_valid():
			photo = p_form.save(commit=False)
			entreprise = client.entreprises.first()
			if entreprise:
				photo.entreprise = entreprise
				photo.save()
			return redirect('account')

	else:
		u_form = UserUpdateForm(instance=user)
		e_form = EntrepriseCreateForm()
		p_form = PhotoEntrepriseForm()
	candidatures = Candidature.objects.filter(client=client) if client else []
	entreprises = user.entreprises.all() if user.is_authenticated else []
	context = {
		'u_form': u_form,
		'e_form': e_form,
		'p_form': p_form,
		'candidatures': candidatures,
		'entreprises': entreprises,
	}
	return render(request, 'candidats/profil.html', context)


@login_required
def entreprise_create(request):
	if request.method == 'POST':
		e_form = EntrepriseCreateForm(request.POST)
		p_form = PhotoEntrepriseForm(request.POST, request.FILES)
		if e_form.is_valid() and p_form.is_valid():
			entreprise = e_form.save(commit=False)
			entreprise.owner = request.user
			entreprise.save()
			photo = p_form.save(commit=False)
			photo.entreprise = entreprise
			photo.save()
			return redirect('account')
	else:
		e_form = EntrepriseCreateForm()
		p_form = PhotoEntrepriseForm()
	return render(request, 'candidats/entreprise_form.html', {
		'form': e_form,
		'p_form': p_form,
		'title': 'Créer une entreprise'
	})


@login_required
def entreprise_update(request, pk):
	entreprise = get_object_or_404(Entreprise, pk=pk, owner=request.user)
	photo_instance = entreprise.photos.first()
	if request.method == 'POST':
		e_form = EntrepriseCreateForm(request.POST, instance=entreprise)
		p_form = PhotoEntrepriseForm(request.POST, request.FILES, instance=photo_instance)
		if e_form.is_valid() and p_form.is_valid():
			entreprise = e_form.save()
			photo = p_form.save(commit=False)
			photo.entreprise = entreprise
			photo.save()
			return redirect('account')
	else:
		e_form = EntrepriseCreateForm(instance=entreprise)
		p_form = PhotoEntrepriseForm(instance=photo_instance)
	return render(request, 'candidats/entreprise_form.html', {
		'form': e_form,
		'p_form': p_form,
		'title': 'Modifier une entreprise'
	})


def entreprise_delete(request, pk):
	entreprise = get_object_or_404(Entreprise, pk=pk, owner=request.user)
	entreprise.delete()
	return redirect('account')


def entreprise_detail(request, entreprise_id):
	entreprise = get_object_or_404(Entreprise, id=entreprise_id)
	client = getattr(request.user, 'client_profile', None) if request.user.is_authenticated else None
	annonces = entreprise.annonces.filter(deleted_at__isnull=True)
	annonces = annonces.exclude(
		candidatures__status='validée'
	).distinct()
	annonces_deja_postulees = []
	if client:
		annonces_deja_postulees = Candidature.objects.filter(
			client=client,
			annonce__in=annonces
		).values_list('annonce_id', flat=True)
	context = {
		'entreprise': entreprise,
		'annonces': annonces,
		'client': client,
		'annonces_deja_postulees': annonces_deja_postulees,
	}
	return render(request, 'candidats/entreprise_detail.html', context)


from django.core.files.storage import FileSystemStorage


@login_required
def postuler(request, annonce_id):
	client = request.user.client_profile
	annonce = get_object_or_404(Annonce, id=annonce_id)

	if request.method == "POST" and not Candidature.objects.filter(client=client, annonce=annonce).exists():
		lettre = request.POST.get("lettre_motivation", "")
		cv_file = request.FILES.get("cv")

		if cv_file:
			fs = FileSystemStorage()
			filename = fs.save(f"cvs/{cv_file.name}", cv_file)
		else:
			filename = "cvs/default.pdf"

		candidature = Candidature.objects.create(
			client=client,
			annonce=annonce,
			lettre_motivation=lettre,
			cv=filename
		)

		Notification.objects.create(
			user=annonce.entreprise.owner,
			message=f"{request.user.username} a postulé à l'annonce '{annonce.title}'",
			candidature=candidature
		)

		CandidatureHistorique.objects.create(
			candidature=candidature,
			action="Candidature envoyée",
			user=request.user
		)

	return redirect('entreprise_detail', entreprise_id=annonce.entreprise.id)


@login_required
def profil_candidat(request, pk):
	client = get_object_or_404(Client, pk=pk)

	entreprises = request.user.entreprises.all()

	if not entreprises.exists():
		return render(request, "errors/403.html", {"message": "Accès refusé. pas d'entreprise."})

	a_postule_chez_lui = Candidature.objects.filter(
		client=client,
		annonce__entreprise__owner=request.user
	).exists()

	if not a_postule_chez_lui:
		return render(request, "errors/403.html", {"message": "Ce candidat n'a pas postulé à vos offres."})

	# Liste des candidatures du client liées à ses entreprises
	candidatures = Candidature.objects.filter(
		client=client,
		annonce__entreprise__owner=request.user
	)

	return render(request, "employeurs/profil_candidat.html", {
		"client": client,
		"candidatures": candidatures
	})


@require_POST
@login_required
def changer_statut_candidature(request, candidature_id):
	candidature = get_object_or_404(Candidature, pk=candidature_id)

	# Vérifie que la candidature appartient bien à une entreprise de l'utilisateur connecté
	if candidature.annonce.entreprise.owner != request.user:
		return render(request, "errors/403.html", {"message": "Accès interdit à cette candidature."})

	decision = request.POST.get("decision")

	if decision == "valider":
		candidature.status = "validée"
		messages.success(request, "Candidature acceptée.")
	elif decision == "refuser":
		candidature.status = "refusée"
		messages.warning(request, "Candidature refusée.")
	else:
		messages.error(request, "Action non valide.")
		return redirect("profil_candidat", pk=candidature.client.pk)

	candidature.save()
	return redirect("profil_candidat", pk=candidature.client.pk)
