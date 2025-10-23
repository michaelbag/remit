from django.core.management.base import BaseCommand
from apps.org.models import Employee
from apps.telegram.bot import TelegramBot


class Command(BaseCommand):
    help = 'Test phone number search functionality'

    def add_arguments(self, parser):
        parser.add_argument('phone', type=str, help='Phone number to search for')

    def handle(self, *args, **options):
        phone_number = options['phone']
        bot = TelegramBot()
        
        self.stdout.write(f"Searching for employee with phone: {phone_number}")
        
        # Показываем все сотрудники с номерами телефонов
        employees_with_phones = Employee.objects.filter(phone__isnull=False).exclude(phone='')
        self.stdout.write(f"\nAll employees with phone numbers:")
        for emp in employees_with_phones:
            # Показываем в удобном формате
            if len(emp.phone) == 11 and emp.phone.startswith('7'):
                formatted_phone = f"+{emp.phone[0]} ({emp.phone[1:4]}) {emp.phone[4:7]}-{emp.phone[7:9]}-{emp.phone[9:11]}"
            else:
                formatted_phone = emp.phone
            self.stdout.write(f"  - {emp.name}: {formatted_phone} (raw: {emp.phone})")
        
        # Тестируем нормализацию
        temp_employee = Employee()
        normalized_phone = temp_employee.normalize_phone(phone_number)
        self.stdout.write(f"\nNormalization: {phone_number} -> {normalized_phone}")
        
        # Тестируем поиск
        employee = bot.find_employee_by_phone(phone_number)
        
        if employee:
            self.stdout.write(
                self.style.SUCCESS(f"Found employee: {employee.name} (PK: {employee.pk})")
            )
        else:
            self.stdout.write(
                self.style.ERROR("Employee not found")
            )
