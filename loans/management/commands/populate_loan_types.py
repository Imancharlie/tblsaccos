from django.core.management.base import BaseCommand
from loans.models import LoanType

class Command(BaseCommand):
    help = 'Populate loan types with initial data'

    def handle(self, *args, **options):
        loan_types_data = [
            {
                'name': 'chap_chap',
                'max_amount': 1000000,
                'interest_rate': 10.0,
                'max_period': 1,
                'processing_fee': 0,
                'collateral_required': 'Hakuna dhamana inayohitajika'
            },
            {
                'name': 'sikukuu',
                'max_amount': 1000000,
                'interest_rate': 10.0,
                'max_period': 6,
                'processing_fee': 0,
                'collateral_required': 'Hakuna dhamana inayohitajika'
            },
            {
                'name': 'elimu',
                'max_amount': 3000000,
                'interest_rate': 14.5,
                'max_period': 6,
                'processing_fee': 0,
                'collateral_required': 'Akiba na Udhamini'
            },
            {
                'name': 'vyombo',
                'max_amount': 2000000,
                'interest_rate': 18.5,
                'max_period': 6,
                'processing_fee': 0,
                'collateral_required': 'Akiba na Udhamini'
            },
            {
                'name': 'wanawake',
                'max_amount': 10000000,
                'interest_rate': 1.0,  # 1% per month
                'max_period': 6,
                'processing_fee': 0,
                'collateral_required': 'Akiba na Udhamini'
            },
            {
                'name': 'dharura',
                'max_amount': 3000000,
                'interest_rate': 18.5,
                'max_period': 12,
                'processing_fee': 0,
                'collateral_required': 'Udhamini tu'
            },
            {
                'name': 'kupumlia',
                'max_amount': 5000000,
                'interest_rate': 18.5,
                'max_period': 12,
                'processing_fee': 0,
                'collateral_required': 'Udhamini tu'
            },
            {
                'name': 'bima',
                'max_amount': 2000000,
                'interest_rate': 18.5,
                'max_period': 12,
                'processing_fee': 0,
                'collateral_required': 'Akiba na Udhamini'
            },
            {
                'name': 'maendeleo',
                'max_amount': 70000000,
                'interest_rate': 18.5,
                'max_period': 60,
                'processing_fee': 0,
                'collateral_required': 'Akiba, Mali na Udhamini'
            }
        ]

        created_count = 0
        updated_count = 0

        for loan_type_data in loan_types_data:
            loan_type, created = LoanType.objects.update_or_create(
                name=loan_type_data['name'],
                defaults={
                    'max_amount': loan_type_data['max_amount'],
                    'interest_rate': loan_type_data['interest_rate'],
                    'max_period': loan_type_data['max_period'],
                    'processing_fee': loan_type_data['processing_fee'],
                    'collateral_required': loan_type_data['collateral_required'],
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created loan type: {loan_type.get_name_display()}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated loan type: {loan_type.get_name_display()}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed {len(loan_types_data)} loan types. '
                f'Created: {created_count}, Updated: {updated_count}'
            )
        )





