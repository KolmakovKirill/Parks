from django.db import models
from django.contrib.auth.models import User

class UserData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userdata')
    ssid = models.CharField(max_length=100, blank=True)
    data = models.JSONField(default=dict, blank=True)  

    def __str__(self):
        return f"Data for {self.user.username}"

class ESP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ssid = models.CharField(max_length=50)
    ip_address = models.GenericIPAddressField(protocol='IPv4')  # Добавлено поле IP

    def __str__(self):
        return f"{self.ssid} ({self.ip_address})"

class LightZone(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    zone_number = models.PositiveSmallIntegerField()
    is_on = models.BooleanField(default=False)
    esp = models.ForeignKey(ESP, on_delete=models.CASCADE, default=0)  # Привязка к ESP

    class Meta:
        unique_together = ('user', 'zone_number')

    def __str__(self):
        return f"Zone {self.zone_number} ({'ON' if self.is_on else 'OFF'})"

class SystemLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    zone_number = models.PositiveSmallIntegerField()
    action = models.CharField(max_length=10, choices=(('on', 'Включение'), ('off', 'Выключение')))

    def __str__(self):
        return f"{self.timestamp}: Пользователь {self.user.username} -> Зона {self.zone_number} [{self.action}]"

