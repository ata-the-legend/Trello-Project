from uuid import uuid4
from django.db.models.query import QuerySet
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.core.mail import send_mail
from django.utils import timezone
from trello.apps.core.models import SoftQuerySet
from trello.apps.dashboards.models import Board


class UserManager(BaseUserManager):

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email, and password.
        """
        # query_set = QuerySet

        if extra_fields.get('avatar', True) is None:
            del extra_fields['avatar']

        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self,  email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)
    
    def get_queryset(self) -> QuerySet:
        return SoftQuerySet(model=self.model, using=self._db, hints=self._hints).all().filter(is_active=True)
    

class HardManager(UserManager):
    def get_queryset(self):
        return SoftQuerySet(model=self.model, using=self._db, hints=self._hints).all()


class User(AbstractBaseUser, PermissionsMixin):

    id = models.UUIDField(editable=False, primary_key=True, default=uuid4)    
    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    email = models.EmailField(
        _("email address"), 
        unique=True, 
        error_messages={
            "unique": _("A user with that email already exists."),
        },
    )
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
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    avatar = models.ImageField(
        _("avatar"), 
        upload_to='uploads/avatars/', 
        default='uploads/avatars/default.jpg', 
        blank=False, 
        null=False,
        )
    mobile = models.CharField(
        _("mobile number"),
        max_length=11,
        error_messages={
            "unique": _("A user with that email already exists."),
        }, 
        unique=True, 
        blank=True, 
        null=True
    )

    objects = UserManager()
    original_objects = HardManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def validate_unique(self, exclude=None):
        if (
            User.original_objects.filter(email=self.email).exists()
        ):
            raise ValidationError(
                    message={
                        "email": _("A user with that email already exists."),
                    }
                )
        super().validate_unique(exclude=None)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def archive(self):
        self.is_active = False
        self.save()

    def restore(self):
        self.is_active= True
        self.save()

    def membered_workspaces(self):
        return self.member_work_spaces.all()

    def owened_workspases(self):
        return self.owner_work_spaces.all()

    def tasked_boards(self):
        return set(Board.objects.filter(board_Tasklists__in= self.assigned_tasks.all().values('status')))

    def active_tasks(self):
        return self.assigned_tasks.all()
        # return Task.objects.filter(assigned_to=self)
        # return self.assigned_tasks.filter(is_active=True).all()\
        #     .filter(status__is_active=True, status__board__is_active=True, status__board__work_space__is_active=True)

    def tasks_has_deadline(self):
        return self.assigned_tasks.exclude(end_date__lt= timezone.now()) 

    def activities_on_board(self, other):
        return self.doer_activity.all().filter(task__status__board=other)

    def teammates_in_workspace(self, other):
        if other.owner == self:
            return User.objects.filter(id__in = self.owened_workspases().filter(id=other.id).values('members'))
        else:
            return User.objects.filter(id__in = self.membered_workspaces().filter(id=other.id).values('members')).exclude(id=self.id) \
                  | User.objects.filter(id__in = self.membered_workspaces().filter(id=other.id).values('owner'))
        
    def __str__(self):
        return self.get_full_name()
    


class RecycleManager(UserManager):
    def get_queryset(self):
        return SoftQuerySet(model=self.model, using=self._db, hints=self._hints).all().filter(is_active=False)


class UserRecycle(User):

    objects = RecycleManager()

    class Meta:
        verbose_name = _("UserRecycle")
        verbose_name_plural = _("UsersRecycle")
        proxy = True

