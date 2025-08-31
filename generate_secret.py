from django.core.management.utils import get_random_secret_key

secret_key = get_random_secret_key()
print(f"SECRET_KEY = '{secret_key}'")
