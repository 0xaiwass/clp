from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from . import managers
import uuid
#---------------------------------------------------------
class User(AbstractBaseUser):
    phone = models.CharField(max_length=11, unique=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = managers.UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email or self.phone or f"User-{self.pk}"

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    @property
    def superuser_status(self):
        return self.is_superuser
#---------------------------------------------------------
class OTPCode(models.Model):
    phone = models.CharField(max_length=11, unique=True)
    code = models.CharField(max_length=64)
    session_key = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.phone} -- {self.code} -- {self.created_at}"
#---------------------------------------------------------
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    title = models.CharField(max_length=50, verbose_name="نام کامل تحویل‌گیرنده:")
    province = models.CharField(max_length=50, verbose_name="استان:")
    city = models.CharField(max_length=50, verbose_name="شهرستان:")
    street = models.CharField(max_length=50, verbose_name="خیابان/کوی:")
    postal_code = models.CharField(max_length=10, verbose_name="کدپستی:")

    is_default = models.BooleanField(default=False, verbose_name="آدرس پیشفرض:")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        else:
            if not Address.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).exists():
                self.is_default = True
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.user.addresses.count() <= 1:
            raise ValueError('You cannot delete the last address.')

        if self.is_default:
            another_address = Address.objects.filter(user=self.user).exclude(pk=self.pk).first()
            if another_address:
                another_address.is_default = True
                another_address.save()

        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.user} -> {self.title} - {self.city}"













