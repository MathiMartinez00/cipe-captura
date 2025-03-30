import logging
import json
import csv
from api.models import City, ComplaintType, Complaint
from api.serializers import ComplaintSerializerRead
from app.constants import SCIENTIFIC_AREA, POSITION, FIRST_CAT_SCIENTIFIC_AREA
from app.forms import RegistrationForm, RegistrationEditForm, UserRegistrationForm
from app.models import Institution, Scientist, Affiliation
from app.utils import get_location_info_from_coordinates, load_countries_iso2
from django.db.models import Count, Max, Sum
from django.forms.models import model_to_dict
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout


logger = logging.getLogger(__name__)
countries_iso2 = load_countries_iso2()


def __get_data_map(scientific_area='', position=''):
    query = {'approved': True}
    if scientific_area != '':
        query['scientific_area'] = scientific_area
    if position != '':
        query['position'] = position
    scientist_objs = Scientist.objects.filter(**query)
    scientists = []
    institutions = []
    countries = set()
    cities = set()
    num_male_scientists, num_female_scientists = 0, 0
    min_age_male, max_age_male, min_age_female, max_age_female = 100, -1, 100, -1
    for scientist_obj in scientist_objs:
        scientist_institution = Affiliation.objects.select_related().get(scientist=scientist_obj, current=True).institution
        institution_country_iso3166 = ''
        if countries_iso2.get(scientist_institution.country.lower()):
            institution_country_iso3166 = countries_iso2.get(scientist_institution.country.lower())
        else:
            print(f"could not find {scientist_institution.country.lower()}")
        scientists.append(
            {'name': str(scientist_obj),
             'first_name': scientist_obj.first_name,
             'last_name': scientist_obj.last_name,
             'sex': scientist_obj.sex,
             'scientific_area': scientist_obj.get_scientific_area_display(),
             'position':  scientist_obj.get_position_display(),
             'twitter_handler': scientist_obj.twitter_handler if scientist_obj.twitter_handler != '' or None else None,
             'facebook_profile': scientist_obj.facebook_profile if scientist_obj.facebook_profile != '' or None else None,
             'gscholar_profile': scientist_obj.gscholar_profile if scientist_obj.gscholar_profile != '' or None else None,
             'scopus_profile': scientist_obj.scopus_profile if scientist_obj.scopus_profile != '' or None else None,
             'linkedin_profile': scientist_obj.linkedin_profile if scientist_obj.linkedin_profile != '' or None else None,
             'researchgate_profile': scientist_obj.researchgate_profile if scientist_obj.researchgate_profile != '' or None else None,
             'academia_profile': scientist_obj.academia_profile if scientist_obj.academia_profile != '' or None else None,
             'institutional_website': scientist_obj.institutional_website if scientist_obj.institutional_website != '' or None else None,
             'personal_website': scientist_obj.personal_website if scientist_obj.personal_website != '' or None else None,
             'orcid_profile': scientist_obj.orcid_profile if scientist_obj.orcid_profile != '' or None else None,
             'becal_fellow': scientist_obj.has_becal_scholarship,
             'institution_name': scientist_institution.name,
             'institution_latitude': scientist_institution.latitude,
             'institution_longitude': scientist_institution.longitude,
             'institution_country': scientist_institution.country,
             'institution_country_iso2': institution_country_iso3166,
             'institution_city': scientist_institution.city
             },
        )
        institutions.append(scientist_institution.name)
        countries.add(scientist_institution.country)
        cities.add(scientist_institution.city)
        if scientist_obj.sex == 'femenino':
            num_female_scientists += 1
            if scientist_obj.rough_age > max_age_female:
                max_age_female = scientist_obj.rough_age
            if scientist_obj.rough_age < min_age_female:
                min_age_female = scientist_obj.rough_age
        elif scientist_obj.sex == 'masculino':
            num_male_scientists += 1
            if scientist_obj.rough_age > max_age_male:
                max_age_male = scientist_obj.rough_age
            if scientist_obj.rough_age < min_age_male:
                min_age_male = scientist_obj.rough_age
        if scientist_obj.first_name == 'prueba':
            print(scientists[-1])
    num_scientists = len(scientists)
    num_institutions = len(set(institutions))
    num_countries = len(countries)
    num_cities = len(cities)
    return scientists, num_scientists, num_institutions, num_countries, num_male_scientists, num_female_scientists, \
        max_age_male, max_age_female, min_age_male, min_age_female, num_cities


def __get_complaints_statistics():
    complaint_list = list()
    complaints = Complaint.objects.all()
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
        complaint_types_ordered = sorted(complaint_types_dict.items(), key=lambda x: x[1], reverse=True)
        statistics = {
            'complaint_count': complaint_count,
            'max_cities': {
                'count': cities_ordered[0][1],
                'city': cities.get(pk=cities_ordered[0][0])
            },
            'max_complaint_types': {
                'count': complaint_types_ordered[0][1],
                'complaint_type': complaint_types.get(pk=complaint_types_ordered[0][0])
            },
        }
        return statistics
    return dict()


def index(request, *args, **kwargs):
    complaints = Complaint.objects.all()
    serializer = ComplaintSerializerRead(complaints, many=True)
    complaints_stats = __get_complaints_statistics()
    context = {
        'complaints': json.dumps(serializer.data),
        'complaints_stats':complaints_stats
    }
    return render(request, 'index.html', context)


def __get_institution_extra_information(inst_dict):
    geocode_result, address, postal_code, city, region, country = get_location_info_from_coordinates(inst_dict['latitude'],
                                                                                                     inst_dict['longitude'])
    inst_dict['address'] = address
    inst_dict['city'] = city
    inst_dict['region'] = region
    inst_dict['country'] = country
    inst_dict['postal_code'] = postal_code

    return geocode_result, inst_dict


def __create_update_institution(inst_dict):
    # Get institution country and city
    try:
        inst_obj = Institution.objects.get(latitude=inst_dict['latitude'], longitude=inst_dict['longitude'])
        if inst_obj.country == '':
            success, inst_dict = __get_institution_extra_information(inst_dict)
            if success:
                inst_obj, updated = Institution.objects.update_or_create(latitude=inst_dict['latitude'],
                                                                         longitude=inst_dict['longitude'],
                                                                         defaults=inst_dict)
            else:
                raise Exception(f"Could not information of institution")
    except Institution.DoesNotExist:
        _, inst_dict = __get_institution_extra_information(inst_dict)
        inst_obj = Institution(**inst_dict)
        inst_obj.save()
        logger.info(f"Institution {inst_dict} created!")
    return inst_obj


def registration(request):
    msg = ''
    registration_error = -1
    created = False
    form = RegistrationForm(request.POST or None, request.FILES or None)
    if request.method == "POST":
        if form.is_valid():
            complaint = Complaint.objects.create(
                complaint_type=form.cleaned_data['complaint_type'],
                description=form.cleaned_data['description'],
                city=form.cleaned_data['city'],
                latitude=form.cleaned_data['location_lat'],
                longitude=form.cleaned_data['location_lng'],
                road_type=form.cleaned_data['road_type'],
                photo=form.cleaned_data['photo'],
                altitude=0,
                accuracy=0,
                captura_id=None,
            )
            msg=f"Denuncia realizada correctamente."
            logger.info(f"Complaint {complaint} created!")
            registration_error = 0
            created = True
        else:
            msg = "Datos inválidos, favor compruebe los errores"
            logger.info(f"Registration Error: The form is not valid. Form details {form}")
            registration_error = 1
    context = {
        'form': form,
        'msg': msg,
        'edit': 0,
        'institution': json.dumps(None),
        'registration_result': registration_error
    }
    if created:
        logger.info(f"Complaint created!")
    return render(request, 'register.html', context)


def success_registration(request):
    return render(request, 'success.html')


def map_scientists(request):
    scientists, _, _, _, _, _, _, _, _, _, _ = __get_data_map()
    value_scientific_areas = []
    value_positions = []
    exists_becal_scholar = False
    for scientist in scientists:
        if scientist['scientific_area'] not in value_scientific_areas:
            value_scientific_areas.append(scientist['scientific_area'])
        if scientist['position'] not in value_positions:
            value_positions.append(scientist['position'])
        if not exists_becal_scholar and scientist.get('becal_fellow'):
            exists_becal_scholar = True
    scientific_areas = []
    for value_scientific_area in value_scientific_areas:
        for scientific_area in SCIENTIFIC_AREA:
            if scientific_area[1] == value_scientific_area:
                scientific_areas.append(scientific_area)
                break
    positions = []
    for value_position in value_positions:
        for position in POSITION:
            if position[1] == value_position:
                positions.append(position)

    cities = City.objects.all()
    complaint_types = ComplaintType.objects.all()
    complaints = Complaint.objects.all()
    serializer = ComplaintSerializerRead(complaints, many=True)
    context = {
        'scientists': json.dumps(scientists),
        'scientific_areas': scientific_areas,
        'cities': cities,
        'complaint_types': complaint_types,
        'complaints': json.dumps(serializer.data),
        'positions': positions,
        'exists_becal_scholar': exists_becal_scholar
    }
    return render(request, 'map.html', context)


def filter_map(request):
    if request.method == 'POST':
        position = request.POST.get('position')
        scientific_area = request.POST.get('scientific_area')
        becal = request.POST.get('becal')
        scientists, _, _, _, _, _, _, _, _, _, _ = __get_data_map(scientific_area, position)
        response_data = {
            'scientists': scientists,
        }
        complaints = Complaint.objects.all()
        if position:
            complaints = complaints.filter(complaint_type_id=position)
        if scientific_area:
            complaints = complaints.filter(city_id=scientific_area)
        serializer = ComplaintSerializerRead(complaints, many=True)
        response_data['scientists'] = serializer.data
        return HttpResponse(json.dumps(response_data), content_type='application/json')
    else:
        return HttpResponse(
            json.dumps({"msg": "Cannot recognize the method type"}),
            content_type="application/json"
        )


def edit_scientist(request, **kwargs):
    scientist_slug = kwargs.get('scientist_slug')
    scientist_obj = Scientist.objects.get(slug=scientist_slug)
    registration_error = -1
    msg = ''
    institution = None
    if request.method == "POST":
        form = RegistrationEditForm(request.POST or None)
        if form.is_valid():
            data = form.cleaned_data.copy()
            if data['location_lat'] != '' and data['location_lng'] != '' and data['location_name'] != '':
                institution = {
                    'latitude': data['location_lat'],
                    'longitude': data['location_lng'],
                    'name': data['location_name']
                }
                # update scientist affiliation
                affiliation = Affiliation.objects.get(scientist=scientist_obj, current=True)
                if affiliation.institution.name != data['location_name'] or \
                   affiliation.institution.longitude != data['location_lng'] or \
                   affiliation.institution.latitude != data['location_lat']:
                    # Save institution data
                    inst_obj = __create_update_institution(institution)
                    # Create/Update affiliation
                    affiliation_obj, created = Affiliation.objects.get_or_create(scientist=scientist_obj,
                                                                                 institution=inst_obj,
                                                                                 defaults={'scientist': scientist_obj,
                                                                                           'institution': inst_obj})
                    if created:
                        logger.info(f"Affiliation {affiliation_obj} was created!")
                # Remove institution data from form object
                del data['location_lat']
                del data['location_lng']
                del data['location_name']
                data['approved'] = False
                # Update scientist
                Scientist.objects.filter(ci=form.cleaned_data['ci'], email=form.cleaned_data['email']).\
                    update(**data)
                msg = f"Actualización de datos exitosa! Luego de su aprobación, los nuevos datos podrán ser " \
                      f"visualizados en el mapa de investigadores."
                registration_error = 0
                institution = {
                    'latitude': form.cleaned_data['location_lat'],
                    'longitude': form.cleaned_data['location_lng'],
                    'name': form.cleaned_data['location_name']
                }
            else:
                msg = f"Datos de registro incompletos, favor indique una institución"
                logger.info(f"Scientist update error: Missing institution. Form details {form}")
                registration_error = 1
        else:
            msg = "Datos inválidos, favor compruebe los errores"
            logger.info(f"Scientist update error: The form is not valid. Form details {form}")
            registration_error = 1
        form = RegistrationEditForm(initial=form.cleaned_data)
    else:
        existing_data = model_to_dict(scientist_obj)
        keys_to_remove = ['phone_number', 'communication_channel', 'approved', 'slug']
        for key_to_remove in keys_to_remove:
            del existing_data[key_to_remove]
        # add location data
        scientist_affiliation = Affiliation.objects.get(scientist=scientist_obj, current=True)
        institution = {
            'latitude': scientist_affiliation.institution.latitude,
            'longitude': scientist_affiliation.institution.longitude,
            'name': scientist_affiliation.institution.name
        }
        existing_data['location_name'] = institution['name']
        existing_data['location_lat'] = institution['latitude']
        existing_data['location_lng'] = institution['longitude']
        form = RegistrationEditForm(initial=existing_data)
    context = {
        'form': form,
        'institution': json.dumps(institution),
        'edit': 1,
        'msg': msg,
        'registration_result': registration_error
    }
    return render(request, 'register.html', context)


def user_registration(request):
    context = {
        'action_url_name': 'user_registration',
        'is_create_mode': True,
    }
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            User.objects.create_user(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            return redirect('index')

        context['form'] = form
        return render(request, 'user-registration.html', {'form': form})

    form = UserRegistrationForm()
    context['form'] = form

    return render(request, 'user-registration.html', context)


def user_login(request):
    context = {
        'action_url_name': 'user_login',
        'is_create_mode': False,
    }
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                return redirect('index')

        context['form'] = form
        return render(request, 'user-registration.html', context)

    form = UserRegistrationForm()
    context['form'] = form

    return render(request, 'user-registration.html', context)


def user_logout(request):
    logout(request)
    return redirect('index')


def view_api_key(request):
    if request.user.is_authenticated:
        return render(request, 'user-info.html')

    return redirect('index')


def __get_complaint_stats():
    complaint_list = list()
    complaints = Complaint.objects.all()
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
    return dict()

def graphs_page(request):
    complaint_stats = __get_complaint_stats()
    complaint_types = ComplaintType.objects.all()
    cities = City.objects.all()
    return render(request, 'graphs.html', { 'stats': complaint_stats, 'complaint_types': complaint_types, 'cities': cities })

def complaints_per_city_csv_report(request):
    complaint_stats = __get_complaint_stats()
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="complaints_per_city.csv"'},
    )

    writer = csv.writer(response)
    writer.writerow(["city", "complaint_count"])
    writer.writerows([[complaints_per_city['city'], complaints_per_city['count']] for complaints_per_city in complaint_stats['complaints_per_city']])

    return response

def complaints_per_city_json_report(request):
    complaint_stats = __get_complaint_stats()
    return JsonResponse(complaint_stats['complaints_per_city'], safe=False)

def complaints_per_complaint_type_csv_report(request):
    complaint_stats = __get_complaint_stats()
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="complaints_per_complaint_type.csv"'},
    )

    writer = csv.writer(response)
    writer.writerow(["city", "complaint_count"])
    writer.writerows([[complaints_per_complaint_type['complaint_type'], complaints_per_complaint_type['count']] for complaints_per_complaint_type in complaint_stats['complaints_per_complaint_type']])

    return response

def complaints_per_complaint_type_json_report(request):
    complaint_stats = __get_complaint_stats()
    return JsonResponse(complaint_stats['complaints_per_complaint_type'], safe=False)