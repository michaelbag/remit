from django.core.management.base import BaseCommand
from apps.telegram.models import TelegramBroadcast


class Command(BaseCommand):
    help = 'Fill empty code fields in TelegramBroadcast with sequential codes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Get all broadcasts ordered by creation time
        broadcasts = TelegramBroadcast.objects.all().order_by('created')
        
        # Filter only those without codes
        broadcasts_without_codes = broadcasts.filter(code__isnull=True) | broadcasts.filter(code='')
        
        if not broadcasts_without_codes.exists():
            self.stdout.write(
                self.style.SUCCESS('All broadcasts already have codes assigned!')
            )
            return
        
        self.stdout.write(f'Found {broadcasts_without_codes.count()} broadcasts without codes')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No changes will be made'))
            for broadcast in broadcasts_without_codes:
                self.stdout.write(f'  Would update: {broadcast.title}')
            return
        
        # Update codes
        updated_count = 0
        for i, broadcast in enumerate(broadcasts_without_codes, 1):
            # Generate 9-digit code with leading zeros
            code = f'{i:09d}'
            broadcast.code = code
            broadcast.save()
            updated_count += 1
            self.stdout.write(f'Updated: {broadcast.title} -> Code: {code}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_count} broadcasts with codes!')
        )
