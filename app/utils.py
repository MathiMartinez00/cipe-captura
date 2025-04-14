import csv
import googlemaps
import logging
import urllib.request
import json
from django.conf import settings
from urllib.parse import urlencode
from api.models import Complaint, ComplaintType, City
from django.http import HttpResponse, JsonResponse

gmaps = googlemaps.Client(key=f"{settings.GOOGLE_MAPS_API_KEY}")
logger = logging.getLogger(__name__)


def load_countries_iso2():
    iso_data = {}
    with open('data/iso3166-1.csv', 'r', encoding='utf-8-sig') as f:
        iso_file = csv.DictReader(f)
        for line in iso_file:
            iso_data[line['nombre'].lower()] = line['iso2'].lower()
    return iso_data

def get_location_info_from_coordinates(latitude, longitude, language='es'):
    address, postal_code, city, region, country = '', '', '', '', ''
    logger.info(f"Going to look for information about the location with latitude {latitude} and "
                f"longitude {longitude}")
    mydict = {'format': 'jsonv2', 'lat': str(latitude), 'lon': str(longitude)}
    urlencode(mydict)
    query = urlencode(mydict)
    try:
        #look up OSM's API
        content = urllib.request.urlopen("https://nominatim.openstreetmap.org/reverse?"+query).read() 
        json_result=json.loads(content.decode(), parse_float=float)
        if 'address' in json_result:
            if 'road' in json_result['address']:
                address = json_result['address']['road']
            if 'postcode' in json_result['address']:
                postal_code = json_result['address']['postcode']
            if 'city' in json_result['address']:
                city = json_result['address']['city']
            if 'state' in json_result['address']:
                region = json_result['address']['state']
            elif 'region' in json_result['address']:
                region = json_result['address']['region']
            if 'country' in json_result['address']:
                country = json_result['address']['country']
        return True, address, postal_code, city, region, country
    except Exception as e:
        logger.error(f"Error when doing reverse geo-coding {e}")
        return False, address, postal_code, city, region, country

def get_location_info_from_name(location_name, language='es'):
    address, postal_code, city, region, country = '', '', '', '', ''
    latitude, longitude = 0.0, 0.0
    logger.info(f"Going to look for information of location {location_name}")
    mydict = {'q': location_name, 'format': 'json', 'limit': '1', 'addressdetails': '[1]'}
    urlencode(mydict)
    query = urlencode(mydict)
    try:
        #look up OSM's API
        content = urllib.request.urlopen("https://nominatim.openstreetmap.org/search.php?"+query).read()
        json_result=json.loads(content)
        if 'address' in json_result[0]:
            if 'road' in json_result[0]['address']:
                address = json_result[0]['address']['road']
            if 'postcode' in json_result[0]['address']:
                postal_code = json_result[0]['address']['postcode']
            if 'city' in json_result[0]['address']:
                city = json_result[0]['address']['city']
            if 'state' in json_result[0]['address']:
                region = json_result[0]['address']['state']
            elif 'region' in json_result[0]['address']:
                region = json_result[0]['address']['region']
            if 'country' in json_result[0]['address']:
                country = json_result[0]['address']['country']
        if 'lat' in json_result[0]:
            latitude = json_result[0]['lat']
        if 'lon' in json_result[0]:
            longitude = json_result[0]['lon']
        return True, address, postal_code, city, region, country, latitude, longitude
    except Exception as e:
        logger.error(f"Error when doing geo-coding {e}")
        return False, address, postal_code, city, region, country, latitude, longitude

class ComplaintsStatsReporter:
    def __init__(self, start_date=None, end_date=None):
        self.start_date = start_date
        self.end_date = end_date

    def get_complaints_stats(self):
        complaint_list = list()
        complaints = Complaint.objects.all()
        if self.start_date and self.end_date:
            complaints = complaints.filter(created_at__date__gte=self.start_date, created_at__date__lte=self.end_date)
        cities_dict = dict()
        cities = City.objects.all()
        complaint_types = ComplaintType.objects.all()
        complaint_types_dict = dict()
        if complaints and complaint_types and cities:
            for complaint_type in complaint_types:
                complaint_types_dict[complaint_type.id] = 0
            for city in cities:
                cities_dict[city.id] = 0
            for complaint in complaints:
                complaint_list.append(complaint)
                cities_dict[complaint.city.id] += 1
                complaint_types_dict[complaint.complaint_type.id] += 1
            complaint_count = len(complaint_list)
            cities_ordered = sorted(cities_dict.items(), key=lambda x: x[1], reverse=True)
            complaints_per_city = [{'count': city[1], 'city': cities.get(pk=city[0]).name} for city in cities_ordered]
            complaint_types_ordered = sorted(complaint_types_dict.items(), key=lambda x: x[1], reverse=True)
            complaints_per_complaint_type = [{'count': complaint_type[1], 'complaint_type': complaint_types.get(pk=complaint_type[0]).name} for complaint_type in complaint_types_ordered]
            statistics = {
                'complaint_count': complaint_count,
                'complaints_per_city': complaints_per_city,
                'complaints_per_complaint_type': complaints_per_complaint_type,
            }
            return statistics
        
    def generate_complaints_per_city_csv_report(self):
        complaint_stats = self.get_complaints_stats()
        if complaint_stats:
            response = HttpResponse(
                content_type="text/csv",
                headers={"Content-Disposition": 'attachment; filename="complaints_per_city.csv"'},
            )

            writer = csv.writer(response)
            writer.writerow(["city", "complaint_count"])
            writer.writerows([[complaints_per_city['city'], complaints_per_city['count']] for complaints_per_city in complaint_stats['complaints_per_city']])

            return response
        
        return JsonResponse(data={'error': 'No complaint data found'}, status=404)
    
    def generate_complaints_per_city_json_report(self):
        complaint_stats = self.get_complaints_stats()
        if complaint_stats:
            return JsonResponse(complaint_stats['complaints_per_city'], safe=False)
        
        return JsonResponse(data={'error': 'No complaint data found'}, status=404)
    
    def generate_complaints_per_complaint_count_csv_report(self):
        complaint_stats = self.get_complaints_stats()
        if complaint_stats:
            response = HttpResponse(
                content_type="text/csv",
                headers={"Content-Disposition": 'attachment; filename="complaints_per_complaint_type.csv"'},
            )

            writer = csv.writer(response)
            writer.writerow(["city", "complaint_count"])
            writer.writerows([[complaints_per_complaint_type['complaint_type'], complaints_per_complaint_type['count']] for complaints_per_complaint_type in complaint_stats['complaints_per_complaint_type']])

            return response
        
        return JsonResponse(data={'error': 'No complaint data found'}, status=404)

    def generate_complaints_per_complaint_count_json_report(self):
        complaint_stats = self.get_complaints_stats()
        if complaint_stats:
            return JsonResponse(complaint_stats['complaints_per_complaint_type'], safe=False)
        
        return JsonResponse(data={'error': 'No complaint data found'}, status=404)
    
    def get_error_response(self):
        return JsonResponse(data={'error': 'Invalid format'}, status=400)