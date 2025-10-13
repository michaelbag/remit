from django.core.management.base import BaseCommand
from apps.org.models import Employee


class Command(BaseCommand):
    help = 'Normalize phone numbers for all employees'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        employees_with_phones = Employee.objects.filter(phone__isnull=False).exclude(phone='')
        
        self.stdout.write(f"Found {employees_with_phones.count()} employees with phone numbers")
        
        updated_count = 0
        
        for employee in employees_with_phones:
            old_phone = employee.phone
            new_phone = employee.normalize_phone(old_phone)
            
            if old_phone != new_phone:
                if dry_run:
                    self.stdout.write(
                        f"Would update {employee.name}: {old_phone} -> {new_phone}"
                    )
                else:
                    employee.phone = new_phone
                    employee.save()
                    self.stdout.write(
                        f"Updated {employee.name}: {old_phone} -> {new_phone}"
                    )
                updated_count += 1
            else:
                self.stdout.write(f"No change needed for {employee.name}: {old_phone}")
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f"DRY RUN: Would update {updated_count} phone numbers")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Successfully updated {updated_count} phone numbers")
            )
