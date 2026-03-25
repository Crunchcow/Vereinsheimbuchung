from django.contrib.auth.models import User


def is_verwaltung_or_admin(user: User) -> bool:
    if not user.is_authenticated:
        return False
    return user.is_staff or user.groups.filter(name__in=['Verwaltung', 'Admin']).exists()


def is_admin(user: User) -> bool:
    if not user.is_authenticated:
        return False
    return user.is_superuser or user.groups.filter(name='Admin').exists()
