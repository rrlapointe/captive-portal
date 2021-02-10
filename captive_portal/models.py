from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from macaddress.fields import MACAddressField
import timeago

class Authorization(models.Model):
	user = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, null=True)
	mac_address = MACAddressField(verbose_name='MAC address',
		help_text='A device\'s MAC address can be found on a sticker attached to the device.')
	timestamp = models.DateTimeField(auto_now_add=True)
	authorized_until = models.DateTimeField()

	class Meta:
		ordering = '-timestamp', '-authorized_until'

	def __str__(self):
		if self.user is None:
			return f'Guest authorization for {self.mac_address}'
		return f'Authorization for {self.user} {self.mac_address}'

	@property
	def timeago(self):
		return timeago.format(self.timestamp, timezone.now())

	@property
	def timeago_authorized_until(self):
		return timeago.format(self.authorized_until, timezone.now())
