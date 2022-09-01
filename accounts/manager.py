from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """
    Creates and saves a User with the given email and password.
    """
    use_in_migrations: bool = True

    def create_user(self, email, password=None, **extra_fields):
        try:
            if not email:
                raise ValueError('Email must be provided')
            email = self.normalize_email(email)
            user = self.model(email=email, **extra_fields)
            user.set_password(password)
            user.save(using=self._db)
            return user
        except Exception as e:
            print(e)
            raise Exception('Error creating user')

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active',  True)

        if extra_fields.get('is_staff') != True:
            raise ValueError('Super user must be havee True status')

        return self.create_user(email, password, **extra_fields)
