from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from englishcode_ai_chatbot_rest.base_models import BaseModel


class UserManager(BaseUserManager):
    def _create_user(self, email, full_name, password=None, is_staff=True, is_superuser=False, **extra_fields):
        if not email:
            raise ValueError("You have not provided a valid e-mail address")

        user = self.model(
            email=self.normalize_email(email),
            full_name=full_name,
            is_staff=is_staff,
            is_superuser=is_superuser,
            **extra_fields
        )

        user.set_password(password)
        user.save()
        return user

    def create_user(self, email, full_name, password=None, **extra_fields):
        return self._create_user(
            email,
            full_name,
            password,
            True,
            False,
            **extra_fields)

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        return self._create_user(
            email,
            full_name,
            password,
            True,
            True,
            **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.CharField('Email',max_length=60, blank=True, null=True, unique=True)
    full_name = models.CharField('Full Name', max_length=70, blank=True, null=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(auto_now=True, auto_now_add=False)
    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return f'{self.email} - {self.full_name}'


class Assistant(BaseModel):
    assistant_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    model = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    starter_message = models.TextField()

    def __str__(self):
        return self.name


class Thread(BaseModel):
    thread_id = models.CharField(max_length=50, unique=True)
    assistant_fk = models.ForeignKey(Assistant, on_delete=models.CASCADE)
    user_fk = models.ForeignKey(User, on_delete=models.CASCADE)


class Message(BaseModel):
    message_id = models.CharField(max_length=50, unique=True)
    role = models.CharField(max_length=50)  # 'user' or 'chatbot'
    # content = models.TextField()
    # is_context_message = models.BooleanField(default=False)
    thread_fk = models.ForeignKey(Thread, on_delete=models.CASCADE)


"""
class AIResponse(models.Model):
    message = models.OneToOneField(Message, on_delete=models.CASCADE)
    response_content = models.TextField()
    response_time = models.DateTimeField(auto_now_add=True)
    # Otros campos según sea necesario
"""
