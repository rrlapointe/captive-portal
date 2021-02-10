# pylint: disable=too-few-public-methods

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Layout, Submit
from django.core.exceptions import ValidationError
from django import forms
from macaddress.formfields import MACAddressField

from . import models
from .util import calculate_guest_password

class AuthorizationForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.layout = Layout(
			HTML(
				'<p>This form is for registering devices that are incompatible with the captive portal. '
				'Once you enter a device\'s MAC address here, the device will be able to use the Wi-Fi for 6 months.</p>'
			),
			'mac_address',
			Submit('submit', 'Register'),
		)

	class Meta:
		model = models.Authorization
		fields = ('mac_address',)

class AuthorizeGuestForm(forms.Form):
	def clean_guest_password(self):
		if self.cleaned_data['guest_password'] != calculate_guest_password():
			raise ValidationError('Incorrect guest password')
		return self.cleaned_data['guest_password']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.layout = Layout(
			'mac',
			'guest_password',
			Submit('submit', 'Log in as guest'),
		)

	mac = MACAddressField(widget=forms.HiddenInput())
	guest_password = forms.CharField(max_length=128,
		label="Guest password", help_text="Ask a member for the guest password.")
