from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login

from candidats.forms import CustomUserCreationForm, UserUpdateForm, EntrepriseCreateForm, PhotoEntrepriseForm
from employeurs.models import Candidature, Entreprise, Annonce


def home(request):
	user = request.user
	client = getattr(user, 'client_profile', None)

	if client:
		# Récupérer les candidatures validées de ce client
		candidatures_validees = Candidature.objects.filter(client=client, status='validée')

		# Extraire les entreprises liées à ces candidatures acceptées
		entreprises_exclues = Entreprise.objects.filter(
			annonces__candidatures__in=candidatures_validees
		).distinct()

		# Entreprises sans candidatures validées pour ce client
		entreprises = Entreprise.objects.exclude(id__in=entreprises_exclues)
	else:
		entreprises = Entreprise.objects.all()

	return render(request, 'candidats/index.html', {'entreprises': entreprises})


def connexion(request):
	return render(request, 'candidats/connexion.html')


def inscription(request):
	form = CustomUserCreationForm(request.POST or None)
	if request.method == 'POST' and form.is_valid():
		user = form.save()
		login(request, user)
		return redirect('home')
	return render(request, 'candidats/inscription.html', {'form': form})


def account(request):
	user = request.user
	client = getattr(user, 'client_profile', None)

	# Formulaire modification user
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
			# Récupérer la première entreprise de l'user par exemple (ou choisir)
			entreprise = client.entreprises.first()
			if entreprise:
				photo.entreprise = entreprise
				photo.save()
			return redirect('account')

	else:
		u_form = UserUpdateForm(instance=user)
		e_form = EntrepriseCreateForm()
		p_form = PhotoEntrepriseForm()

	# Récupérer candidatures
	candidatures = Candidature.objects.filter(client=client) if client else []
	entreprises = user.entreprises.all() if user.is_authenticated else []
	print("User connecté :", user)
	print("Entreprises trouvées :", user.entreprises.all())

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
		'title': 'Modifier une entreprise'
	})


def entreprise_delete(request, pk):
	entreprise = get_object_or_404(Entreprise, pk=pk, owner=request.user)
	entreprise.delete()
	return redirect('account')


def entreprise_detail(request, entreprise_id):
	entreprise = get_object_or_404(Entreprise, id=entreprise_id)
	annonces = entreprise.annonces.filter(deleted_at__isnull=True)

	client = getattr(request.user, 'client_profile', None) if request.user.is_authenticated else None

	# Récupère les ID des annonces pour lesquelles ce client a déjà postulé
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


@login_required
def postuler(request, annonce_id):
	client = request.user.client_profile
	annonce = get_object_or_404(Annonce, id=annonce_id)

	# Vérifie si déjà une candidature
	if not Candidature.objects.filter(client=client, annonce=annonce).exists():
		Candidature.objects.create(
			client=client,
			annonce=annonce,
			lettre_motivation="Ma lettre automatique",
			cv="cvs/default.pdf"
		)
	return redirect('entreprise_detail', entreprise_id=annonce.entreprise.id)
