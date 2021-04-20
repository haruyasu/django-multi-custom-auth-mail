from django.db import models
from accounts.models import CustomUser


class User(models.Model):
    account_core = models.OneToOneField(
        CustomUser, verbose_name='アカウント', on_delete=models.CASCADE)
    address = models.CharField('住所', max_length=100, null=True, blank=True)

    def __str__(self):
        return self.account_core.first_name


class Staff(models.Model):
    account_core = models.OneToOneField(
        CustomUser, verbose_name='アカウント', on_delete=models.CASCADE)
    tel = models.CharField('電話番号', max_length=100, null=True, blank=True)

    def __str__(self):
        return self.account_core.first_name
