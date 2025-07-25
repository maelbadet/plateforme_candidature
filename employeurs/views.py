import csv

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import now

from candidats.forms import AnnonceForm
from employeurs.models import Candidature, Entreprise, Annonce, Notification


def export_candidatures_csv(request):
	today = now().date()
	candidatures = Candidature.objects.filter(date_postulation__date=today)

	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = f'attachment; filename="candidatures_{today}.csv"'

	writer = csv.writer(response)
	writer.writerow(['ID', 'Client', 'Annonce', 'Status', 'Date'])

	for c in candidatures:
		writer.writerow([
			c.id,
			c.client.user.username,
			c.annonce.title,
			c.status,
			c.date_postulation,
		])

	return response


@login_required
def mes_annonces(request, entreprise_id):
	entreprise = get_object_or_404(Entreprise, id=entreprise_id, owner=request.user)
	annonces = entreprise.annonces.filter(deleted_at__isnull=True)
	return render(request, 'employeurs/mes_annonces.html', {
		'entreprise': entreprise,
		'annonces': annonces,
	})


@login_required
def creer_annonce(request, entreprise_id):
	entreprise = get_object_or_404(Entreprise, id=entreprise_id, owner=request.user)

	if request.method == 'POST':
		form = AnnonceForm(request.POST)
		if form.is_valid():
			annonce = form.save(commit=False)
			annonce.entreprise = entreprise
			annonce.save()
			return redirect('mes_annonces', entreprise_id=entreprise.id)
	else:
		form = AnnonceForm()

	return render(request, 'employeurs/creer_annonce.html', {'form': form, 'entreprise': entreprise})


@login_required
def modifier_annonce(request, entreprise_id, annonce_id):
	entreprise = get_object_or_404(Entreprise, id=entreprise_id, owner=request.user)
	annonce = get_object_or_404(Annonce, id=annonce_id, entreprise=entreprise)

	if request.method == 'POST':
		form = AnnonceForm(request.POST, instance=annonce)
		if form.is_valid():
			form.save()
			return redirect('mes_annonces', entreprise_id=entreprise.id)
	else:
		form = AnnonceForm(instance=annonce)

	return render(request, 'employeurs/modifier_annonce.html', {
		'form': form,
		'entreprise': entreprise,
		'annonce': annonce
	})


@login_required
def supprimer_annonce(request, entreprise_id, annonce_id):
	entreprise = get_object_or_404(Entreprise, id=entreprise_id, owner=request.user)
	annonce = get_object_or_404(Annonce, id=annonce_id, entreprise=entreprise)

	if request.method == 'POST':
		annonce.delete()
		return redirect('mes_annonces', entreprise_id=entreprise.id)

	return render(request, 'employeurs/supprimer_annonce.html', {
		'entreprise': entreprise,
		'annonce': annonce
	})


@login_required
def notifications(request):
	user = request.user
	if user.is_authenticated:
		notifications = user.notifications.filter(is_read=False)
	else:
		notifications = 0

	return render(request, 'employeurs/notifications_list.html', {
		'notifications': notifications
	})


@login_required
def lire_notification(request, notification_id):
	notification = get_object_or_404(Notification, id=notification_id, user=request.user)
	notification.is_read = True
	notification.save()

	entreprise_id = notification.candidature.annonce.entreprise.id
	return redirect('entreprise_detail', entreprise_id=entreprise_id)


def check_notifications(request):
	if request.user.is_authenticated:
		count = request.user.notifications.filter(is_read=False).count()
	else:
		count = 0
	return JsonResponse({'unread_count': count})
