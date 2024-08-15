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

        number_of_objects = 10
        if options['complaint_count']:
            number_of_objects = options['complaint_count']
        for i in range(number_of_objects):
            Complaint.objects.create(
                complaint_type=random.choice(complaint_types),
                description=fake.paragraph(nb_sentences=random.randint(1, 3), variable_nb_sentences=False),
                city=random.choice(cities),
                latitude=random.uniform(-25.28994, -26.28994),
                longitude=random.uniform(-57.77053, -54.77053),
                altitude=0,
                accuracy=0,
                road_type=random.choice(road_types),
            )

        self.stdout.write("Generated random data successfully")
