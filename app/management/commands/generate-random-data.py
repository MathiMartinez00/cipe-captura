from django.core.management.base import BaseCommand
from api.models import Complaint, ComplaintType, City, RoadType
from faker import Faker
import random


class Command(BaseCommand):
    help = "Generate random data"

    def add_arguments(self, parser):
        parser.add_argument('--complaint-count', help="Number of complaints to generate", type=int)

    def handle(self, *args, **options):
        fake = Faker()

        cities = list()

        cities.append(City.objects.create(name='Asuncion'))
        cities.append(City.objects.create(name='Capiata'))
        cities.append(City.objects.create(name='Lambare'))

        complaint_types = list()

        complaint_types.append(ComplaintType.objects.create(name='Bache', code='BCH'))
        complaint_types.append(ComplaintType.objects.create(name='Basura', code='BSR'))

        road_types = list()

        road_types.append(RoadType.objects.create(name='Asfalto'))
        road_types.append(RoadType.objects.create(name='Empedrado'))

        for i in range(options.get('complaint-count', 10)):
            Complaint.objects.create(
                complaint_type=random.choice(complaint_types),
                description=fake.paragraph(nb_sentences=random.randint(1, 3), variable_nb_sentences=False),
                city=random.choice(cities),
                latitude=random.uniform(-25.17, -26.17),
                longitude=random.uniform(-57.36, -56.36),
                altitude=0,
                accuracy=0,
                road_type=random.choice(road_types),
            )

        self.stdout.write("Generated random data successfully")
