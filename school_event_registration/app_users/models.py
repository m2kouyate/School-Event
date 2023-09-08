from django.contrib.auth.models import User
from django.db import models


def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.id, filename)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to=user_directory_path, null=True, blank=True,
                                        default='default/img.png')
    about = models.TextField(max_length=1000, blank=True, default='')

    def __str__(self):
        return f'{self.user}'

    def delete(self, *args, **kwargs):
        user = self.user
        super().delete(*args, **kwargs)
        user.delete()

