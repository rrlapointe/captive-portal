from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.http import urlencode
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import CreateView
from macaddress import format_mac
from netaddr import mac_unix_expanded

from . import models, forms
from .util import authorize, calculate_guest_password

class LoginRequiredMixin: # pylint: disable=too-few-public-methods
	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		if not request.user.is_active:
			logout(request)
		return super().dispatch(request, *args, **kwargs)

class AuthorizationCreateView(LoginRequiredMixin, CreateView):
	template_name = 'crispy.html'
	form_class = forms.AuthorizationForm
	success_url = reverse_lazy('ui:home')

	def get_context_data(self, **kwargs):
		kwargs['msg'] = 'Register IoT device'
		return super().get_context_data(**kwargs)

	def form_valid(self, form):
		minutes = settings.AUTHENTICATED_USERS_AUTHORIZATION_MINUTES
		form.instance.user = self.request.user
		form.instance.authorized_until = timezone.now() + timedelta(minutes=minutes)
		messages.success(self.request, 'Device registered')
		response = super().form_valid(form)
		authorize(format_mac(form.instance.mac_address, mac_unix_expanded), minutes)
		return response

@login_required
@require_GET
def account_profile(request):
	return render(request, 'registration/profile.html', {'user': request.user})

@login_required
@require_GET
def homepage(request):
	context = {}
	return render(request, 'home.html', context)

@require_GET
@transaction.atomic
def landing(request):
	try:
		mac = request.GET['id']
	except KeyError:
		if request.META['REMOTE_ADDR'] == settings.REVERSE_PROXY_IP:
			return HttpResponseRedirect(reverse('ui:home'))
		return HttpResponseRedirect(settings.PORTAL_TRIGGER_REDIRECT)

	if request.user.is_authenticated:
		minutes = settings.AUTHENTICATED_USERS_AUTHORIZATION_MINUTES
		try:
			pk = models.Authorization.objects.create(
				user=request.user,
				mac_address=mac,
				authorized_until=timezone.now() + timedelta(minutes=minutes)
			).pk
		except ValidationError:
			return HttpResponseBadRequest()
		authorize(format_mac(models.Authorization.objects.get(pk=pk).mac_address, mac_unix_expanded), minutes)
		return HttpResponseRedirect(settings.AUTHENTICATED_USERS_SUCCESS_REDIRECT)
	guest_form = forms.AuthorizeGuestForm()
	guest_form.initial['mac'] = mac
	guest_form.helper.form_action = reverse('authorize_guest')
	return render(request, 'landing.html', {'mac': mac, 'guest_form': guest_form})

@require_POST
@transaction.atomic
def authorize_guest(request):
	form = forms.AuthorizeGuestForm(request.POST)
	if not form.is_valid():
		for field in form.errors:
			messages.error(request, form.errors[field])
		if 'mac' not in form.cleaned_data:
			return HttpResponseBadRequest()
		return HttpResponseRedirect(reverse('landing1') + '?' + urlencode({'id': form.cleaned_data['mac']}))
	mac = format_mac(form.cleaned_data['mac'], mac_unix_expanded)
	minutes = settings.GUESTS_AUTHORIZATION_MINUTES
	models.Authorization.objects.create(
		user=None,
		mac_address=mac,
		authorized_until=timezone.now() + timedelta(minutes=minutes)
	)
	authorize(mac, minutes)
	return HttpResponseRedirect(settings.GUESTS_SUCCESS_REDIRECT)

@login_required
@require_GET
def guest_password(request):
	return render(request, 'guest_password.html', {'guest_password': calculate_guest_password()})

@login_required
@require_GET
def authorizations_list(request):
	now = timezone.now()
	context = {}
	context['title'] = 'Access Log'
	context['authorizations'] = models.Authorization.objects.exclude(
		authorized_until__lte=now, timestamp__lte=(now - timedelta(days=7)))
	return render(request, 'authorizations_list.html', context)

@login_required
@require_GET
def my_devices(request):
	context = {}
	context['title'] = 'My Devices'
	context['authorizations'] = models.Authorization.objects.filter(user=request.user)
	return render(request, 'authorizations_list.html', context)
