import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from base_app.models import Mover, Moving_Type1, Moving_Type2, Mover_Moving_Type2, Country, \
    Mover_Country, Quote_Request, Mover_Quote_Request, \
    Number_Mover_Quote_Request_PerDay, Number_Distribution_Quote_Request, Movers_Email, Region, Mover_Region, \
    Customers_Notification_Email
import random

#html email
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def index(request):
    return render(request, 'base_app/index.html')


def terms_of_use(request):
    return render(request, 'base_app/terms_of_use.html')


def mover_inscription(request):
    if request.method == 'GET':
        return render(request, 'base_app/mover/mover_inscription.html', {'form': UserCreationForm()})
    else:
        if request.POST['password'] == request.POST['password1']:
            if User.objects.filter(username=request.POST.get('username')):
                messages.error(request, 'Erreur ! Ce nom d\'utilisateur existe déjà, veuillez utiliser un autre !')
                return redirect('mover_inscription')
            elif User.objects.filter(email=request.POST.get('email')):
                messages.error(request, 'Erreur ! Cet email existe déjà, veuillez utiliser un autre !')
                return redirect('mover_inscription')
            else:
                try:
                    username = request.POST['username']
                    first_name = request.POST['first_name']
                    last_name = request.POST['last_name']
                    email = request.POST['email']
                    password = request.POST['password']

                    # Creation of the user account
                    user = User.objects.create_user(username=username, password=password, first_name=first_name,
                                                    last_name=last_name, email=email)
                    user.save()

                    return redirect('mover_inscription_step1', new_user_id=user.id)
                except ValueError:
                    return render(request, 'base_app/mover/mover_inscription.html',
                                  {'form': UserCreationForm(), 'error': 'Bad data passed in'})
        else:
            return render(request, 'base_app/mover/mover_inscription.html',
                          {'form': UserCreationForm(), 'error': 'Les deux mots de passe ne correspondent pas !'})


def mover_inscription_step1(request, new_user_id):
    if get_object_or_404(User, id=new_user_id):
        country = Country.objects.filter(name='Belgique').last()
        regions = Region.objects.filter(country__name='Belgique')
        moving_type1 = Moving_Type1.objects.all()
        user = get_object_or_404(User, id=new_user_id)
        if request.method == 'POST':
            company_name = request.POST['company_name']
            company_phone_number = request.POST['company_phone_number']
            Adresse = request.POST['Adresse']
            Postal_Code = request.POST['Postal_Code']
            employee_number = request.POST['employee_number']
            TVA_number = request.POST['TVA_number']

            if Mover.objects.filter(company_name=request.POST.get('company_name')):
                messages.error(request, 'Erreur ! Ce nom d\'entreprise existe déjà dans notre base de données !')
                return redirect('mover_inscription')
            elif Mover.objects.filter(company_phone_number=request.POST.get('company_phone_number')):
                messages.error(request, 'Erreur ! Ce numéro de téléphone existe déjà dans notre base de données !')
                return redirect('mover_inscription')
            else:
                # Mover table filling
                # creation of the ref
                characters = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
                characters.extend(list('1234567890'))
                size = 10
                ref = ''
                for x in range(size):
                    ref += random.choice(characters)
                ref = ref

                website = 0
                company_statut = 0
                company_description = 0
                logo = "/user/images/profil_image/09.jpg"
                country = Country.objects.filter(id=request.POST['country_id']).last()
                region = Region.objects.filter(id=request.POST['region_id']).last()
                moving_type1 = Moving_Type1.objects.filter(id=request.POST['moving_type1_id']).last()

                mover = Mover(ref=ref, company_name=company_name, Adresse=Adresse, country=country,
                              company_phone_number=company_phone_number, Postal_Code=Postal_Code,
                              employee_number=employee_number, TVA_number=TVA_number, website=website, company_statut=
                              company_statut, company_description=company_description, logo=logo, user=user,
                              moving_type1=moving_type1, region=region)
                mover.save()

                return redirect('mover_inscription_step2', new_user_id=user.id, mover_id=mover.id)
    else:
        messages.error(request, 'Utilisateur non reconnu !')
        return redirect('mover_inscription')
    return render(request, 'base_app/mover/mover_inscription_step1.html', {'country': country, 'moving_type1':
                    moving_type1, 'regions': regions})


def mover_inscription_step2(request, new_user_id, mover_id):
    if get_object_or_404(User, id=new_user_id) and get_object_or_404(Mover, id=mover_id):
        moving_type2 = Moving_Type2.objects.all()
        user = get_object_or_404(User, id=new_user_id)
        mover_info = get_object_or_404(Mover, id=mover_id)

        if request.method == 'POST':
            moving_type2_name = request.POST.getlist('moving_type2_name[]')
            if moving_type2_name:
                # Filling Mover_Moving_Type2 table
                for data in moving_type2_name:
                    if Mover_Moving_Type2.objects.filter(moving_type2_name=data, mover=mover_info):
                        messages.error(request, 'Erreur ! Cette sélection existe déjà dans notre base de données !')
                        return redirect('mover_inscription_step2', new_user_id=user.id, mover_id=mover_info.id)
                    else:
                        if mover_info.moving_type1.name == 'National':
                            # Sending email
                            subject = 'Bienvenu chez ItsMoving'
                            recipient_email = mover_info.user.email
                            recipient_last_name = mover_info.user.last_name
                            email_from = mover_info.user.email

                            # sending html mail
                            html_content = render_to_string("base_app/inscription_email_template.html",
                                                            {'last_name': recipient_last_name,
                                                             'email_from': email_from})
                            text_centent = strip_tags(html_content)
                            email = EmailMultiAlternatives(
                                # subject
                                subject,
                                # content
                                text_centent,
                                # from email
                                settings.EMAIL_HOST_USER,
                                # receiver list
                                [recipient_email]
                            )
                            email.attach_alternative(html_content, "text/html")
                            email.send()

                            # sending email to itsmoving
                            recipient_email = 'contact.itsmoving@gmail.com'
                            subject = 'Inscription d\'un nouveau déménageur'
                            email_from = 'contact.itsmoving@gmail.com'
                            recipient_list = [recipient_email, ]

                            message1 = f'L\'entreprise de déménagement {mover_info.company_name.capitalize()} vient de ' \
                                       f's\'inscrire sur la plateforme et attend d\'être activer. \n'
                            send_mail(subject, message1, email_from, recipient_list)

                            messages.success(request,
                                             'Félicitations, Votre compte a été crée avec succès, il sera activé d\'ici '
                                             '24h !')
                            return redirect('login_user')
                        else:
                            savedata = Mover_Moving_Type2(moving_type2_name=data, mover=mover_info)
                            savedata.save()
                        continue
                return redirect('mover_inscription_step3', new_user_id=user.id, mover_id=mover_info.id)
            else:
                messages.error(request, 'Veuillez faire au moins une sélection !')
                return redirect('mover_inscription_step2', new_user_id=user.id, mover_id=mover_info.id)
    else:
        messages.error(request, 'Utilisateur non reconnu !')
        return redirect('mover_inscription')
    return render(request, 'base_app/mover/mover_inscription_step2.html', {'moving_type2': moving_type2, 'mover_info':
        mover_info})


def mover_inscription_step3(request, new_user_id, mover_id):
    if get_object_or_404(User, id=new_user_id) and get_object_or_404(Mover, id=mover_id):
        countries = Country.objects.all()
        user = get_object_or_404(User, id=new_user_id)
        mover_info = get_object_or_404(Mover, id=mover_id)

        if request.method == 'POST':
            country_name = request.POST.getlist('country_name[]')
            if country_name:
                send_email = False
                # Filling Mover_Moving_Type2 table
                for data in country_name:
                    if Mover_Country.objects.filter(country_name=data, mover=mover_info):
                        messages.error(request, 'Erreur ! Cette sélection existe déjà dans notre base de données !')
                        return redirect('mover_inscription_step3', new_user_id=user.id, mover_id=mover_info.id)
                    else:
                        country_info = Country.objects.filter(name=data).last()
                        savedata = Mover_Country(country_name=data, country=country_info, mover=mover_info)
                        savedata.save()
                        send_email = True

                if send_email:
                    # Sending email
                    subject = 'Bienvenu chez ItsMoving'
                    recipient_email = mover_info.user.email
                    recipient_last_name = mover_info.user.last_name
                    email_from = mover_info.user.email

                    # sending html mail
                    html_content = render_to_string("base_app/inscription_email_template.html",
                                                    {'last_name': recipient_last_name,
                                                     'email_from': email_from})
                    text_centent = strip_tags(html_content)
                    email = EmailMultiAlternatives(
                        # subject
                        subject,
                        # content
                        text_centent,
                        # from email
                        settings.EMAIL_HOST_USER,
                        # receiver list
                        [recipient_email]
                    )
                    email.attach_alternative(html_content, "text/html")
                    email.send()

                    # sending email to itsmoving
                    recipient_email = 'contact.itsmoving@gmail.com'
                    subject = 'Inscription d\'un nouveau déménageur'
                    email_from = 'contact.itsmoving@gmail.com'
                    recipient_list = [recipient_email, ]

                    message1 = f'L\'entreprise de déménagement {mover_info.company_name.capitalize()} vient de ' \
                               f's\'inscrire sur la plateforme et attend d\'être activer. \n'
                    send_mail(subject, message1, email_from, recipient_list)

                messages.success(request,
                                 'Félicitations, l\'inscription est terminée, il ne vous reste qu\'à renseigner'
                                 ' les regions dans lesquelles vous allez intervenir et le nombre de devis maximum que '
                                 'vous souhaitez recevoir par jour !')
                return redirect('login_user')

            else:
                messages.error(request, 'Veuillez faire au moins une sélection !')
                return redirect('mover_inscription_step3', new_user_id=user.id, mover_id=mover_info.id)
    else:
        messages.error(request, 'Utilisateur non reconnu !')
        return redirect('mover_inscription')
    return render(request, 'base_app/mover/mover_inscription_step3.html', {'countries': countries})


def contact_page(request):
    if request.method == "POST":
        full_name = request.POST.get('full_name')

        recipient_email = 'contact.itsmoving@gmail.com'
        subject = request.POST.get('subject')
        email_from = request.POST.get('email')
        #print(email_from)
        message = request.POST.get('message')
        recipient_list = [recipient_email, ]

        message1 = f'Nouveau message de la part de Mr. {full_name.capitalize()}! \n' \
                   f'Email du client : {email_from}\n'\
                   f'Contenu du message: \n{message}'
        send_mail(subject, message1, email_from, recipient_list)

        messages.success(request, f'Votre message à été envoyé avec succès, nous vous contacterons très bientôt !')

    return render(request, 'base_app/contact_page.html', {'title': 'send an email'})


def devis_page1(request):
    moving_type1 = Moving_Type1.objects.all()
    moving_type2 = Moving_Type2.objects.all()
    country = Country.objects.filter(name='Belgique').last()
    if request.method == 'POST':
        moving_type1_id = request.POST.get('moving_type1_id')
        moving_type2_id = request.POST.get('moving_type2_id')
        country_id = request.POST.get('country_id')
        if moving_type1_id and moving_type2_id and country_id:
            return redirect('devis_page2', moving_type1_id=moving_type1_id, moving_type2_id=moving_type2_id,
                            country_id=country_id)
        else:
            messages.error(request, 'Veuillez renseigner tous les champs !')
            return redirect('devis_page1')
    return render(request, 'base_app/devis/devis_page1.html',
                  {'moving_type1': moving_type1, 'moving_type2': moving_type2,
                   'country': country})


def devis_page2(request, moving_type1_id, moving_type2_id, country_id):
    moving_type1 = get_object_or_404(Moving_Type1, pk=moving_type1_id)
    moving_type2 = get_object_or_404(Moving_Type2, pk=moving_type2_id)
    country = get_object_or_404(Country, pk=country_id)
    regions = Region.objects.all()
    if request.method == 'POST':
        region_id = request.POST.get('region_id')
        Adresse_Departure = request.POST.get('Adresse_Departure')
        Postal_Code_Departure = request.POST.get('Postal_Code_Departure')
        Residence_Number_or_Name_Departure = request.POST.get('Residence_Number_or_Name_Departure')
        Residence_Departure = request.POST.get('Residence_Departure')
        Number_Room_Departure = request.POST.get('Number_Room_Departure')

        if region_id and Adresse_Departure and Postal_Code_Departure and Residence_Number_or_Name_Departure and Residence_Departure \
                and Number_Room_Departure:
            return redirect('devis_page3', moving_type1_id=moving_type1.id, moving_type2_id=moving_type2.id,
                            country_id=country.id, region_id=region_id, Adresse_Departure=Adresse_Departure,
                            Postal_Code_Departure=Postal_Code_Departure
                            , Residence_Number_or_Name_Departure=Residence_Number_or_Name_Departure,
                            Number_Room_Departure=
                            Number_Room_Departure, Residence_Departure=Residence_Departure)
        else:
            messages.error(request, 'Veuillez renseigner tous les champs !')
            return redirect('devis_page2')
    return render(request, 'base_app/devis/devis_page2.html', {'regions': regions})


def devis_page3(request, moving_type1_id, moving_type2_id, country_id, region_id, Adresse_Departure,
                Postal_Code_Departure, Residence_Number_or_Name_Departure, Number_Room_Departure, Residence_Departure):
    moving_type1 = get_object_or_404(Moving_Type1, pk=moving_type1_id)
    moving_type2 = get_object_or_404(Moving_Type2, pk=moving_type2_id)
    country = get_object_or_404(Country, pk=country_id)
    regions = Region.objects.all()

    countries = Country.objects.all()
    if request.method == 'POST':
        City_Arrival_for_international_moving = request.POST.get('City_Arrival_for_international_moving')
        Region_Arrival_for_national_moving = request.POST.get('Region_Arrival_for_national_moving')
        Country_Arrival = request.POST.get('Country_Arrival')
        Adresse_Arrival = request.POST.get('Adresse_Arrival')
        Postal_Code_Arrival = request.POST.get('Postal_Code_Arrival')
        Residence_Number_or_Name_Arrival = request.POST.get('Residence_Number_or_Name_Arrival')
        Residence_Arrival = request.POST.get('Residence_Arrival')

        if City_Arrival_for_international_moving and Adresse_Arrival and Postal_Code_Arrival and \
                Residence_Number_or_Name_Arrival and Residence_Arrival:
            return redirect('devis_page4', moving_type1_id=moving_type1.id, moving_type2_id=moving_type2.id,
                            country_id=country.id,
                            region_id=region_id, Adresse_Departure=Adresse_Departure,
                            Postal_Code_Departure=Postal_Code_Departure
                            , Residence_Number_or_Name_Departure=Residence_Number_or_Name_Departure,
                            Number_Room_Departure=Number_Room_Departure, Residence_Departure=Residence_Departure,
                            Country_Arrival=Country_Arrival,
                            City_Arrival_for_international_moving=City_Arrival_for_international_moving
                            , Adresse_Arrival=Adresse_Arrival, Postal_Code_Arrival=Postal_Code_Arrival,
                            Residence_Number_or_Name_Arrival=
                            Residence_Number_or_Name_Arrival, Residence_Arrival=Residence_Arrival,
                            Region_Arrival_for_national_moving=Region_Arrival_for_national_moving)
        else:
            messages.error(request, 'Veuillez faire au moins une sélection !')
            return redirect('devis_page3')
    return render(request, 'base_app/devis/devis_page3.html',
                  {'region_id': region_id, 'Adresse_Departure': Adresse_Departure,
                   'Postal_Code_Departure': Postal_Code_Departure, 'countries': countries,
                   'Residence_Number_or_Name_Departure': Residence_Number_or_Name_Departure,
                   'Number_Room_Departure': Number_Room_Departure, 'Residence_Departure':
                       Residence_Departure, 'moving_type1_id': moving_type1_id, 'regions': regions})


def devis_page4(request, moving_type1_id, moving_type2_id, country_id, region_id, Adresse_Departure,
                Postal_Code_Departure, Region_Arrival_for_national_moving,
                Residence_Number_or_Name_Departure, Number_Room_Departure, Residence_Departure, Country_Arrival,
                City_Arrival_for_international_moving, Adresse_Arrival,
                Postal_Code_Arrival, Residence_Number_or_Name_Arrival, Residence_Arrival):
    moving_type1 = get_object_or_404(Moving_Type1, pk=moving_type1_id)
    moving_type2 = get_object_or_404(Moving_Type2, pk=moving_type2_id)
    country = get_object_or_404(Country, pk=country_id)

    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')

        if firstname and lastname and email and phone_number:
            return redirect('devis_page5', moving_type1_id=moving_type1.id, moving_type2_id=moving_type2.id,
                            country_id=country.id,
                            region_id=region_id, Adresse_Departure=Adresse_Departure,
                            Postal_Code_Departure=Postal_Code_Departure
                            , Residence_Number_or_Name_Departure=Residence_Number_or_Name_Departure,
                            Number_Room_Departure=
                            Number_Room_Departure, Residence_Departure=Residence_Departure, Country_Arrival=
                            Country_Arrival, City_Arrival_for_international_moving=City_Arrival_for_international_moving
                            , Adresse_Arrival=Adresse_Arrival,
                            Postal_Code_Arrival=Postal_Code_Arrival, Residence_Number_or_Name_Arrival=
                            Residence_Number_or_Name_Arrival, Residence_Arrival=Residence_Arrival, firstname=firstname,
                            lastname=lastname, email=email, phone_number=phone_number,
                            Region_Arrival_for_national_moving=Region_Arrival_for_national_moving)
        else:
            messages.error(request, 'Veuillez faire au moins une sélection !')
            return redirect('devis_page4')
    return render(request, 'base_app/devis/devis_page4.html',
                  {'region_id': region_id, 'Adresse_Departure': Adresse_Departure,
                   'Postal_Code_Departure': Postal_Code_Departure,
                   'Residence_Number_or_Name_Departure': Residence_Number_or_Name_Departure, 'Country_Arrival':
                       Country_Arrival, 'City_Arrival_for_international_moving': City_Arrival_for_international_moving,
                   'Adresse_Arrival': Adresse_Arrival,
                   'Postal_Code_Arrival': Postal_Code_Arrival, 'Residence_Number_or_Name_Arrival':
                       Residence_Number_or_Name_Arrival, 'Residence_Arrival': Residence_Arrival,
                   'Residence_Departure': Residence_Departure, 'Number_Room_Departure':
                       Number_Room_Departure, 'Region_Arrival_for_national_moving': Region_Arrival_for_national_moving})


def devis_page5(request, moving_type1_id, moving_type2_id, country_id, region_id, Adresse_Departure,
                Postal_Code_Departure, Region_Arrival_for_national_moving,
                Residence_Number_or_Name_Departure, Number_Room_Departure, Residence_Departure, Country_Arrival,
                City_Arrival_for_international_moving, Adresse_Arrival,
                Postal_Code_Arrival, Residence_Number_or_Name_Arrival, Residence_Arrival, firstname, lastname, email,
                phone_number):

    moving_type1 = get_object_or_404(Moving_Type1, pk=moving_type1_id)
    moving_type2 = get_object_or_404(Moving_Type2, pk=moving_type2_id)
    country_departure_request = get_object_or_404(Country, pk=country_id)
    region = get_object_or_404(Region, pk=region_id)

    if moving_type1_id == 1:
        Region_Arrival_for_national_moving = get_object_or_404(Region, id=Region_Arrival_for_national_moving)
        Region_Arrival_for_national_moving = Region_Arrival_for_national_moving.name
    else:
        Region_Arrival_for_national_moving = 0
    current_date = datetime.datetime.today()
    global mover_available

    if request.method == 'POST':
        furniture_assembly_disassembly = request.POST.get('furniture_assembly_disassembly')
        furniture_storage = request.POST.get('furniture_storage')
        packing_service = request.POST.get('packing_service')
        packaging_materials = request.POST.get('packaging_materials')
        Additional_informations = request.POST.get('Additional_informations')
        # moving_date2 = request.POST.get('moving_date2')

        # creation of the ref
        characters = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        characters.extend(list('1234567890'))
        size = 10
        ref = ''
        for x in range(size):
            ref += random.choice(characters)
        ref = ref

        if request.POST.get('furniture_assembly_disassembly'):
            furniture_assembly_disassembly = True
        else:
            furniture_assembly_disassembly = False

        if request.POST.get('furniture_storage'):
            furniture_storage = True
        else:
            furniture_storage = False

        if request.POST.get('packaging_materials'):
            packaging_materials = True
        else:
            packaging_materials = False

        if request.POST.get('packing_service'):
            packing_service = True
        else:
            packing_service = False

        if request.POST.get('moving_date1') and request.POST.get('moving_date1') and request.POST.get('moving_date'):

            messages.error(request, 'Vous choisir deux dates pour la partie #Je flexible# ou une date pour la partie'
                                    '#Date de déménagement# et non les deux à la fois !')
            render(request, 'base_app/devis/devis_page5.html')

        else:

            if request.POST.get('moving_date'):
                moving_date = request.POST.get('moving_date')

                moving_date1 = "1000-10-10"
                moving_date2 = "1000-10-10"

                if Country_Arrival == "0":
                    country_arrival_name = ""
                else:
                    country_arrival_info = Country.objects.filter(id=Country_Arrival).last()
                    country_arrival_name = country_arrival_info.name

                savedata = Quote_Request(ref=ref, region=region,
                                         Postal_Code_Departure=Postal_Code_Departure,
                                         Adresse_Departure=Adresse_Departure, Residence_Number_or_Name_Departure=
                                         Residence_Number_or_Name_Departure, Country_Arrival=country_arrival_name,
                                         City_Arrival_for_international_moving=City_Arrival_for_international_moving,
                                         Adresse_Arrival=Adresse_Arrival,
                                         Residence_Number_or_Name_Arrival=Residence_Number_or_Name_Arrival,
                                         Postal_Code_Arrival=
                                         Postal_Code_Arrival, Residence_Departure=Residence_Departure,
                                         Number_Room_Departure=
                                         Number_Room_Departure, Residence_Arrival=Residence_Arrival,
                                         packing_service=packing_service,
                                         packaging_materials=packaging_materials, furniture_assembly_disassembly=
                                         furniture_assembly_disassembly, furniture_storage=furniture_storage,
                                         firstname=firstname, lastname=lastname, email=email, phone_number=phone_number,
                                         Additional_informations=
                                         Additional_informations, moving_date=moving_date, moving_date1=moving_date1,
                                         moving_date2=
                                         moving_date2, moving_type1=moving_type1, moving_type2=moving_type2, country=
                                         country_departure_request, Region_Arrival_for_national_moving=
                                         Region_Arrival_for_national_moving)
                savedata.save()

                ######################## Automatic distribution for the requests to the movers ####################
                requests = Quote_Request.objects.all().order_by('-id')

                mover_available = False
                for request in requests:

                    # ####################NATIONAL REQUEST DISTRIBUTION START#####################
                    if request.moving_type1.name == 'National':

                        movers = Mover.objects.filter(activated=True)
                        for mover in movers:

                            # we select the movers who deliver in the departure region of the request
                            movers_departure_regions = Mover_Region.objects.filter(region__name=request.region.name,
                                                                                   mover_id=mover.id)

                            # we select the movers who deliver in the arrival region of the request
                            movers_arrival_regions = Mover_Region.objects.filter\
                                (region__name=request.Region_Arrival_for_national_moving, mover_id=mover.id)

                            if movers_departure_regions and movers_arrival_regions:
                                print(mover.company_name)
                                mover_available = True

                                max_request_day = Number_Mover_Quote_Request_PerDay.objects.filter(
                                    mover_id=mover.id,
                                    reception_date_quote_request__date=current_date.date()).last()

                                # We check if the mover has received a request today
                                if max_request_day:

                                    if max_request_day.number_quote_received_the_same_day < mover. \
                                            number_max_quote_request:

                                        # we prevent the mover to receive the same request twice
                                        quote_request_info = Quote_Request.objects.filter(
                                            id=request.id).last()
                                        mover_info = Mover.objects.filter(id=mover.id).last()
                                        number_distribution_request = Number_Distribution_Quote_Request.objects.filter \
                                            (quote_request=quote_request_info.id).last()

                                        if not Mover_Quote_Request.objects.filter(quote_request=quote_request_info,
                                                                                  mover=mover_info):
                                            number = max_request_day.number_quote_received_the_same_day + 1
                                            savedata1 = Number_Mover_Quote_Request_PerDay(
                                                number_quote_received_the_same_day=number, mover=mover_info)

                                            savedata2 = Mover_Quote_Request(quote_request=quote_request_info,
                                                                            mover=mover_info)

                                            # we verify if the request hasn't been distributed more than 5 times
                                            if number_distribution_request:

                                                if number_distribution_request.number_distribution < number_distribution_request. \
                                                        number_max_distribution:
                                                    number_distribution = number_distribution_request.number_distribution + 1
                                                    savedata3 = Number_Distribution_Quote_Request(
                                                        number_distribution=
                                                        number_distribution,
                                                        quote_request=
                                                        quote_request_info)
                                                    savedata3.save()

                                            else:
                                                number_distribution = 1
                                                savedata3 = Number_Distribution_Quote_Request(number_distribution=
                                                                                              number_distribution,
                                                                                              quote_request=
                                                                                              quote_request_info)
                                                savedata3.save()

                                            savedata1.save()
                                            savedata2.save()

                                            # Sending email to the Mover
                                            if not Movers_Email.objects.filter(quote_request__id=
                                                                               savedata2.quote_request.id,
                                                                               mover__id=savedata2.mover.id):
                                                # Sending email
                                                subject = 'ItsMoving - Nouvelle demande de devis'
                                                recipient_email = mover_info.user.email
                                                recipient_last_name = mover_info.user.last_name
                                                company_name = mover_info.company_name
                                                moving_type_name_received = moving_type1.name
                                                email_from = mover_info.user.email
                                                message = f'Une nouvelle demande de devis {moving_type_name_received} ' \
                                                          f'est disponible, Veuillez vous connecter à votre compte afin ' \
                                                          f'de consulter les détails.'

                                                # sending html mail
                                                html_content = render_to_string(
                                                    "base_app/quote_request_notification_email_template.html",
                                                    {'last_name': recipient_last_name,
                                                     'company_name': company_name,
                                                     'message': message,
                                                     'email_from': email_from})
                                                text_centent = strip_tags(html_content)
                                                email = EmailMultiAlternatives(
                                                    # subject
                                                    subject,
                                                    # content
                                                    text_centent,
                                                    # from email
                                                    settings.EMAIL_HOST_USER,
                                                    # receiver list
                                                    [recipient_email]
                                                )
                                                email.attach_alternative(html_content, "text/html")
                                                email.send()

                                                save_mover_email = Movers_Email(quote_request_id=
                                                                                savedata2.quote_request.id,
                                                                                mover_id=
                                                                                savedata2.mover.id)
                                                save_mover_email.save()

                                            if not Customers_Notification_Email.objects.filter(
                                                quote_request__ref=request.ref
                                            ):
                                                save_client_notification_email = Customers_Notification_Email(
                                                    moving_possibility=True, quote_request_id=request.id,
                                                    mover_id=mover.id
                                                )
                                                save_client_notification_email.save()

                                                # We send an email to the customer
                                                subject = 'ItsMoving - Accusé de reception'
                                                recipient_email = savedata.email
                                                recipient_last_name = savedata.lastname
                                                email_from = savedata.email
                                                message = f'Votre demande de devis a bien été reçu, vous aurez un ' \
                                                          f'retour de 5 de nos professionnels dans les heures à venir.'

                                                # sending html mail
                                                html_content = render_to_string(
                                                    "base_app/quote_request_notification_email_template.html",
                                                    {'last_name': recipient_last_name, 'message': message,
                                                     'email_from': email_from})
                                                text_centent = strip_tags(html_content)
                                                email = EmailMultiAlternatives(
                                                    # subject
                                                    subject,
                                                    # content
                                                    text_centent,
                                                    # from email
                                                    settings.EMAIL_HOST_USER,
                                                    # receiver list
                                                    [recipient_email]
                                                )
                                                email.attach_alternative(html_content, "text/html")
                                                email.send()

                                                # we modify the quote to mark the email as sent
                                                edit_quote_request_email_sent = Quote_Request(
                                                    ref=request.ref, country_id=request.country.id, id=request.id,
                                                    created=
                                                    request.created, Adresse_Departure=request.Adresse_Departure,
                                                    Postal_Code_Departure=request.Postal_Code_Departure,
                                                    Residence_Number_or_Name_Departure=request.Residence_Number_or_Name_Departure,
                                                    Residence_Departure=request.Residence_Departure,
                                                    Number_Room_Departure=request.
                                                        Number_Room_Departure, Country_Arrival=request.Country_Arrival,
                                                    City_Arrival_for_international_moving=request.
                                                        City_Arrival_for_international_moving,
                                                    Adresse_Arrival=request.Adresse_Arrival,
                                                    Region_Arrival_for_national_moving=request.Region_Arrival_for_national_moving,
                                                    Residence_Number_or_Name_Arrival=request.Residence_Number_or_Name_Arrival,
                                                    Postal_Code_Arrival=request.Postal_Code_Arrival,
                                                    Residence_Arrival=request.
                                                        Residence_Arrival, packing_service=request.packing_service,
                                                    packaging_materials
                                                    =request.packaging_materials,
                                                    furniture_assembly_disassembly=request.
                                                        furniture_assembly_disassembly,
                                                    furniture_storage=request.furniture_storage,
                                                    Additional_informations=request.Additional_informations,
                                                    firstname=request.
                                                        firstname, lastname=request.lastname, email=request.email,
                                                    region_id=request.
                                                        region.id, phone_number=request.phone_number,
                                                    distributed=request.distributed,
                                                    moving_date=request.moving_date, moving_date1=request.moving_date1,
                                                    moving_date2=request.moving_date2,
                                                    moving_type1_id=request.moving_type1.id,
                                                    moving_type2_id=request.moving_type2.id
                                                )

                                                edit_quote_request_email_sent.save()

                                else:
                                    quote_request_info = Quote_Request.objects.filter(id=request.id).last()
                                    mover_info = Mover.objects.filter(id=mover.id).last()
                                    number_distribution_request = Number_Distribution_Quote_Request.objects.filter \
                                        (quote_request=quote_request_info.id).last()

                                    # the request have to be saved maximum 5 time to 5 differents movers
                                    for i in range(5):

                                        # we prevent the mover to receive the same request twice
                                        if not Mover_Quote_Request.objects.filter(quote_request=quote_request_info,
                                                                                  mover=mover_info):

                                            savedata1 = Number_Mover_Quote_Request_PerDay(
                                                number_quote_received_the_same_day=1,
                                                mover=mover_info)

                                            savedata2 = Mover_Quote_Request(quote_request=
                                                                            quote_request_info,
                                                                            mover=mover_info)

                                            # we verify if the request hasn't been distributed more than 5 times
                                            if number_distribution_request:

                                                if number_distribution_request.number_distribution < number_distribution_request. \
                                                        number_max_distribution:
                                                    number_distribution = number_distribution_request.number_distribution + 1
                                                    savedata3 = Number_Distribution_Quote_Request(
                                                        number_distribution=
                                                        number_distribution,
                                                        quote_request=
                                                        quote_request_info)
                                                    savedata3.save()

                                            else:
                                                number_distribution = 1
                                                savedata3 = Number_Distribution_Quote_Request(number_distribution=
                                                                                              number_distribution,
                                                                                              quote_request=
                                                                                              quote_request_info)
                                                savedata3.save()

                                            savedata1.save()
                                            savedata2.save()

                                            # Sending email to the Mover
                                            if not Movers_Email.objects.filter(quote_request__id=
                                                                               savedata2.quote_request.id,
                                                                               mover__id=savedata2.mover.id):
                                                # Sending email
                                                subject = 'ItsMoving - Nouvelle demande de devis'
                                                recipient_email = mover_info.user.email
                                                recipient_last_name = mover_info.user.last_name
                                                company_name = mover_info.company_name
                                                moving_type_name_received = moving_type1.name
                                                email_from = mover_info.user.email
                                                message = f'Une nouvelle demande de devis {moving_type_name_received} ' \
                                                          f'est disponible, Veuillez vous connecter à votre compte afin ' \
                                                          f'de consulter les détails.'

                                                # sending html mail
                                                html_content = render_to_string(
                                                    "base_app/quote_request_notification_email_template.html",
                                                    {'last_name': recipient_last_name,
                                                     'company_name': company_name,
                                                     'message': message,
                                                     'email_from': email_from})
                                                text_centent = strip_tags(html_content)
                                                email = EmailMultiAlternatives(
                                                    # subject
                                                    subject,
                                                    # content
                                                    text_centent,
                                                    # from email
                                                    settings.EMAIL_HOST_USER,
                                                    # receiver list
                                                    [recipient_email]
                                                )
                                                email.attach_alternative(html_content, "text/html")
                                                email.send()

                                                save_mover_email = Movers_Email(quote_request_id=
                                                                                savedata2.quote_request.id,
                                                                                mover_id=
                                                                                savedata2.mover.id)
                                                save_mover_email.save()

                                            if not Customers_Notification_Email.objects.filter(
                                                    quote_request__ref=request.ref
                                            ):
                                                save_client_notification_email = Customers_Notification_Email(
                                                    moving_possibility=True, quote_request_id=request.id,
                                                    mover_id=mover.id
                                                )
                                                save_client_notification_email.save()

                                                # We send an email to the customer
                                                subject = 'ItsMoving - Accusé de reception'
                                                recipient_email = savedata.email
                                                recipient_last_name = savedata.lastname
                                                email_from = savedata.email
                                                message = f'Votre demande de devis a bien été reçu, vous aurez un ' \
                                                          f'retour de 5 de nos professionnels dans les heures à venir.'

                                                # sending html mail
                                                html_content = render_to_string(
                                                    "base_app/quote_request_notification_email_template.html",
                                                    {'last_name': recipient_last_name, 'message': message,
                                                     'email_from': email_from})
                                                text_centent = strip_tags(html_content)
                                                email = EmailMultiAlternatives(
                                                    # subject
                                                    subject,
                                                    # content
                                                    text_centent,
                                                    # from email
                                                    settings.EMAIL_HOST_USER,
                                                    # receiver list
                                                    [recipient_email]
                                                )
                                                email.attach_alternative(html_content, "text/html")
                                                email.send()

                                                # we modify the quote to mark the email as sent
                                                edit_quote_request_email_sent = Quote_Request(
                                                    ref=request.ref, country_id=request.country.id, id=request.id,
                                                    created=
                                                    request.created, Adresse_Departure=request.Adresse_Departure,
                                                    Postal_Code_Departure=request.Postal_Code_Departure,
                                                    Residence_Number_or_Name_Departure=request.Residence_Number_or_Name_Departure,
                                                    Residence_Departure=request.Residence_Departure,
                                                    Number_Room_Departure=request.
                                                        Number_Room_Departure, Country_Arrival=request.Country_Arrival,
                                                    City_Arrival_for_international_moving=request.
                                                        City_Arrival_for_international_moving,
                                                    Adresse_Arrival=request.Adresse_Arrival,
                                                    Region_Arrival_for_national_moving=request.Region_Arrival_for_national_moving,
                                                    Residence_Number_or_Name_Arrival=request.Residence_Number_or_Name_Arrival,
                                                    Postal_Code_Arrival=request.Postal_Code_Arrival,
                                                    Residence_Arrival=request.
                                                        Residence_Arrival, packing_service=request.packing_service,
                                                    packaging_materials
                                                    =request.packaging_materials,
                                                    furniture_assembly_disassembly=request.
                                                        furniture_assembly_disassembly,
                                                    furniture_storage=request.furniture_storage,
                                                    Additional_informations=request.Additional_informations,
                                                    firstname=request.
                                                        firstname, lastname=request.lastname, email=request.email,
                                                    region_id=request.
                                                        region.id, phone_number=request.phone_number,
                                                    distributed=request.distributed,
                                                    moving_date=request.moving_date, moving_date1=request.moving_date1,
                                                    moving_date2=request.moving_date2,
                                                    moving_type1_id=request.moving_type1.id,
                                                    moving_type2_id=request.moving_type2.id
                                                )

                                                edit_quote_request_email_sent.save()

                            if not mover_available:
                                if not Customers_Notification_Email.objects.filter(
                                    quote_request__email=request.email, quote_request__ref=request.ref
                                ):
                                    save_client_notification_email = Customers_Notification_Email(
                                        moving_possibility=False, quote_request_id=request.id, mover_id=mover.id
                                    )
                                    save_client_notification_email.save()

                                    # We send an email to the customer
                                    subject = 'ItsMoving - Accusé de reception'
                                    recipient_email = savedata.email
                                    recipient_last_name = savedata.lastname
                                    email_from = savedata.email
                                    message = f''

                                    # sending html mail
                                    html_content = render_to_string(
                                        "base_app/quote_request_client_notification_email_template.html",
                                        {'last_name': recipient_last_name, 'message': message,
                                         'email_from': email_from})
                                    text_centent = strip_tags(html_content)
                                    email = EmailMultiAlternatives(
                                        # subject
                                        subject,
                                        # content
                                        text_centent,
                                        # from email
                                        settings.EMAIL_HOST_USER,
                                        # receiver list
                                        [recipient_email]
                                    )
                                    email.attach_alternative(html_content, "text/html")
                                    email.send()

                                    # we modify the quote to mark the email as sent
                                    edit_quote_request_email_sent = Quote_Request(
                                        ref=request.ref, country_id=request.country.id, id=request.id, created=
                                        request.created, Adresse_Departure=request.Adresse_Departure,
                                        Postal_Code_Departure=request.Postal_Code_Departure,
                                        Residence_Number_or_Name_Departure=request.Residence_Number_or_Name_Departure,
                                        Residence_Departure=request.Residence_Departure, Number_Room_Departure=request.
                                        Number_Room_Departure, Country_Arrival=request.Country_Arrival,
                                        City_Arrival_for_international_moving=request.
                                        City_Arrival_for_international_moving, Adresse_Arrival=request.Adresse_Arrival,
                                        Region_Arrival_for_national_moving=request.Region_Arrival_for_national_moving,
                                        Residence_Number_or_Name_Arrival=request.Residence_Number_or_Name_Arrival,
                                        Postal_Code_Arrival=request.Postal_Code_Arrival, Residence_Arrival=request.
                                        Residence_Arrival, packing_service=request.packing_service, packaging_materials
                                        =request.packaging_materials, furniture_assembly_disassembly=request.
                                        furniture_assembly_disassembly, furniture_storage=request.furniture_storage,
                                        Additional_informations=request.Additional_informations, firstname=request.
                                        firstname, lastname=request.lastname, email=request.email, region_id=request.
                                        region.id, phone_number=request.phone_number, distributed=request.distributed,
                                        moving_date=request.moving_date, moving_date1=request.moving_date1,
                                        moving_date2=request.moving_date2, moving_type1_id=request.moving_type1.id,
                                        moving_type2_id=request.moving_type2.id
                                    )

                                    edit_quote_request_email_sent.save()

                    ####################END NATIONAL REQUEST DISTRIBUTION START###################

                    #####################INTERNATIONAL REQUEST DISTRIBUTION START#####################
                    elif request.moving_type1.name == 'International':

                        movers = Mover.objects.filter(moving_type1__name='International', activated=True)
                        for mover in movers:

                            # we select the mover who work in the country of destination of the request
                            mover_countries = Mover_Country.objects.filter(mover_id=mover.id)
                            for mover_country in mover_countries:
                                if request.Country_Arrival == mover_country.country_name:

                                    max_request_day = Number_Mover_Quote_Request_PerDay.objects.filter(
                                        mover_id=mover.id,
                                        reception_date_quote_request__date=current_date.date()).last()

                                    # We check if the mover has received a request today
                                    if max_request_day:

                                        if max_request_day.number_quote_received_the_same_day < mover. \
                                                number_max_quote_request:

                                            # we prevent the mover to receive the same request twice
                                            quote_request_info = Quote_Request.objects.filter(
                                                id=request.id).last()
                                            mover_info = Mover.objects.filter(id=mover.id).last()
                                            number_distribution_request = Number_Distribution_Quote_Request.objects.filter \
                                                (quote_request=quote_request_info.id).last()

                                            if not Mover_Quote_Request.objects.filter(quote_request=quote_request_info,
                                                                                  mover=mover_info):
                                                number = max_request_day.number_quote_received_the_same_day + 1
                                                savedata1 = Number_Mover_Quote_Request_PerDay(
                                                    number_quote_received_the_same_day=number, mover=mover_info)

                                                savedata2 = Mover_Quote_Request(quote_request=quote_request_info,
                                                                                mover=mover_info)

                                                # we verify if the request hasn't been distributed more than 5 times
                                                if number_distribution_request:

                                                    if number_distribution_request.number_distribution < number_distribution_request. \
                                                            number_max_distribution:

                                                        number_distribution = number_distribution_request.number_distribution + 1
                                                        savedata3 = Number_Distribution_Quote_Request(
                                                            number_distribution=
                                                            number_distribution,
                                                            quote_request=
                                                            quote_request_info)
                                                        savedata3.save()

                                                else:
                                                    number_distribution = 1
                                                    savedata3 = Number_Distribution_Quote_Request(number_distribution=
                                                                                                  number_distribution,
                                                                                                  quote_request=
                                                                                                  quote_request_info)
                                                    savedata3.save()

                                                savedata1.save()
                                                savedata2.save()

                                                # Sending email to the Mover
                                                if not Movers_Email.objects.filter(quote_request__id=
                                                                               savedata2.quote_request.id,
                                                                               mover__id=savedata2.mover.id):
                                                    # Sending email
                                                    subject = 'ItsMoving - Nouvelle demande de devis'
                                                    recipient_email = mover_info.user.email
                                                    recipient_last_name = mover_info.user.last_name
                                                    company_name = mover_info.company_name
                                                    moving_type_name_received = moving_type1.name
                                                    email_from = mover_info.user.email
                                                    message = f'Une nouvelle demande de devis {moving_type_name_received} ' \
                                                              f'est disponible, Veuillez vous connecter à votre compte afin ' \
                                                              f'de consulter les détails.'

                                                    # sending html mail
                                                    html_content = render_to_string(
                                                        "base_app/quote_request_notification_email_template.html",
                                                        {'last_name': recipient_last_name,
                                                         'company_name': company_name,
                                                         'message': message,
                                                         'email_from': email_from})
                                                    text_centent = strip_tags(html_content)
                                                    email = EmailMultiAlternatives(
                                                        # subject
                                                        subject,
                                                        # content
                                                        text_centent,
                                                        # from email
                                                        settings.EMAIL_HOST_USER,
                                                        # receiver list
                                                        [recipient_email]
                                                    )
                                                    email.attach_alternative(html_content, "text/html")
                                                    email.send()

                                                    save_mover_email = Movers_Email(quote_request_id=
                                                                                    savedata2.quote_request.id,
                                                                                    mover_id=
                                                                                    savedata2.mover.id)
                                                    save_mover_email.save()

                                                if not Customers_Notification_Email.objects.filter(
                                                        quote_request__ref=request.ref
                                                ):
                                                    save_client_notification_email = Customers_Notification_Email(
                                                        moving_possibility=True, quote_request_id=request.id,
                                                        mover_id=mover.id
                                                    )
                                                    save_client_notification_email.save()

                                                    # We send an email to the customer
                                                    subject = 'ItsMoving - Accusé de reception'
                                                    recipient_email = savedata.email
                                                    recipient_last_name = savedata.lastname
                                                    email_from = savedata.email
                                                    message = f'Votre demande de devis a bien été reçu, vous aurez un ' \
                                                              f'retour de 5 de nos professionnels dans les heures à venir.'

                                                    # sending html mail
                                                    html_content = render_to_string(
                                                        "base_app/quote_request_notification_email_template.html",
                                                        {'last_name': recipient_last_name, 'message': message,
                                                         'email_from': email_from})
                                                    text_centent = strip_tags(html_content)
                                                    email = EmailMultiAlternatives(
                                                        # subject
                                                        subject,
                                                        # content
                                                        text_centent,
                                                        # from email
                                                        settings.EMAIL_HOST_USER,
                                                        # receiver list
                                                        [recipient_email]
                                                    )
                                                    email.attach_alternative(html_content, "text/html")
                                                    email.send()

                                                    # we modify the quote to mark the email as sent
                                                    edit_quote_request_email_sent = Quote_Request(
                                                        ref=request.ref, country_id=request.country.id, id=request.id,
                                                        created=
                                                        request.created, Adresse_Departure=request.Adresse_Departure,
                                                        Postal_Code_Departure=request.Postal_Code_Departure,
                                                        Residence_Number_or_Name_Departure=request.Residence_Number_or_Name_Departure,
                                                        Residence_Departure=request.Residence_Departure,
                                                        Number_Room_Departure=request.
                                                            Number_Room_Departure,
                                                        Country_Arrival=request.Country_Arrival,
                                                        City_Arrival_for_international_moving=request.
                                                            City_Arrival_for_international_moving,
                                                        Adresse_Arrival=request.Adresse_Arrival,
                                                        Region_Arrival_for_national_moving=request.Region_Arrival_for_national_moving,
                                                        Residence_Number_or_Name_Arrival=request.Residence_Number_or_Name_Arrival,
                                                        Postal_Code_Arrival=request.Postal_Code_Arrival,
                                                        Residence_Arrival=request.
                                                            Residence_Arrival, packing_service=request.packing_service,
                                                        packaging_materials
                                                        =request.packaging_materials,
                                                        furniture_assembly_disassembly=request.
                                                            furniture_assembly_disassembly,
                                                        furniture_storage=request.furniture_storage,
                                                        Additional_informations=request.Additional_informations,
                                                        firstname=request.
                                                            firstname, lastname=request.lastname, email=request.email,
                                                        region_id=request.
                                                            region.id, phone_number=request.phone_number,
                                                        distributed=request.distributed,
                                                        moving_date=request.moving_date,
                                                        moving_date1=request.moving_date1,
                                                        moving_date2=request.moving_date2,
                                                        moving_type1_id=request.moving_type1.id,
                                                        moving_type2_id=request.moving_type2.id
                                                    )

                                                    edit_quote_request_email_sent.save()

                                    else:
                                        quote_request_info = Quote_Request.objects.filter(id=request.id).last()
                                        mover_info = Mover.objects.filter(id=mover.id).last()
                                        number_distribution_request = Number_Distribution_Quote_Request.objects.filter \
                                            (quote_request=quote_request_info.id).last()

                                        # the request have to be saved maximum 5 time to 5 differents movers
                                        for i in range(5):

                                            # we prevent the mover to receive the same request twice
                                            if not Mover_Quote_Request.objects.filter(quote_request=quote_request_info,
                                                                                  mover=mover_info):

                                                savedata1 = Number_Mover_Quote_Request_PerDay(
                                                    number_quote_received_the_same_day=1,
                                                    mover=mover_info)

                                                savedata2 = Mover_Quote_Request(quote_request=
                                                                                quote_request_info,
                                                                                mover=mover_info)

                                                # we verify if the request hasn't been distributed more than 5 times
                                                if number_distribution_request:

                                                    if number_distribution_request.number_distribution < number_distribution_request. \
                                                            number_max_distribution:

                                                        number_distribution = number_distribution_request.number_distribution + 1
                                                        savedata3 = Number_Distribution_Quote_Request(
                                                            number_distribution=
                                                            number_distribution,
                                                            quote_request=
                                                            quote_request_info)
                                                        savedata3.save()

                                                else:
                                                    number_distribution = 1
                                                    savedata3 = Number_Distribution_Quote_Request(number_distribution=
                                                                                                  number_distribution,
                                                                                                  quote_request=
                                                                                                  quote_request_info)
                                                    savedata3.save()

                                                savedata1.save()
                                                savedata2.save()

                                                # Sending email to the Mover
                                                if not Movers_Email.objects.filter(quote_request__id=
                                                                               savedata2.quote_request.id,
                                                                               mover__id=savedata2.mover.id):
                                                    # Sending email
                                                    subject = 'ItsMoving - Nouvelle demande de devis'
                                                    recipient_email = mover_info.user.email
                                                    recipient_last_name = mover_info.user.last_name
                                                    company_name = mover_info.company_name
                                                    moving_type_name_received = moving_type1.name
                                                    email_from = mover_info.user.email
                                                    message = f'Une nouvelle demande de devis {moving_type_name_received} ' \
                                                              f'est disponible, Veuillez vous connecter à votre compte afin ' \
                                                              f'de consulter les détails.'

                                                    # sending html mail
                                                    html_content = render_to_string(
                                                        "base_app/quote_request_notification_email_template.html",
                                                        {'last_name': recipient_last_name,
                                                         'company_name': company_name,
                                                         'message': message,
                                                         'email_from': email_from})
                                                    text_centent = strip_tags(html_content)
                                                    email = EmailMultiAlternatives(
                                                        # subject
                                                        subject,
                                                        # content
                                                        text_centent,
                                                        # from email
                                                        settings.EMAIL_HOST_USER,
                                                        # receiver list
                                                        [recipient_email]
                                                    )
                                                    email.attach_alternative(html_content, "text/html")
                                                    email.send()

                                                    save_mover_email = Movers_Email(quote_request_id=
                                                                                    savedata2.quote_request.id,
                                                                                    mover_id=
                                                                                    savedata2.mover.id)
                                                    save_mover_email.save()

                                                if not Customers_Notification_Email.objects.filter(
                                                        quote_request__ref=request.ref
                                                ):
                                                    save_client_notification_email = Customers_Notification_Email(
                                                        moving_possibility=True, quote_request_id=request.id,
                                                        mover_id=mover.id
                                                    )
                                                    save_client_notification_email.save()

                                                    # We send an email to the customer
                                                    subject = 'ItsMoving - Accusé de reception'
                                                    recipient_email = savedata.email
                                                    recipient_last_name = savedata.lastname
                                                    email_from = savedata.email
                                                    message = f'Votre demande de devis a bien été reçu, vous aurez un ' \
                                                              f'retour de 5 de nos professionnels dans les heures à venir.'

                                                    # sending html mail
                                                    html_content = render_to_string(
                                                        "base_app/quote_request_notification_email_template.html",
                                                        {'last_name': recipient_last_name, 'message': message,
                                                         'email_from': email_from})
                                                    text_centent = strip_tags(html_content)
                                                    email = EmailMultiAlternatives(
                                                        # subject
                                                        subject,
                                                        # content
                                                        text_centent,
                                                        # from email
                                                        settings.EMAIL_HOST_USER,
                                                        # receiver list
                                                        [recipient_email]
                                                    )
                                                    email.attach_alternative(html_content, "text/html")
                                                    email.send()

                                                    # we modify the quote to mark the email as sent
                                                    edit_quote_request_email_sent = Quote_Request(
                                                        ref=request.ref, country_id=request.country.id, id=request.id,
                                                        created=
                                                        request.created, Adresse_Departure=request.Adresse_Departure,
                                                        Postal_Code_Departure=request.Postal_Code_Departure,
                                                        Residence_Number_or_Name_Departure=request.Residence_Number_or_Name_Departure,
                                                        Residence_Departure=request.Residence_Departure,
                                                        Number_Room_Departure=request.
                                                            Number_Room_Departure,
                                                        Country_Arrival=request.Country_Arrival,
                                                        City_Arrival_for_international_moving=request.
                                                            City_Arrival_for_international_moving,
                                                        Adresse_Arrival=request.Adresse_Arrival,
                                                        Region_Arrival_for_national_moving=request.Region_Arrival_for_national_moving,
                                                        Residence_Number_or_Name_Arrival=request.Residence_Number_or_Name_Arrival,
                                                        Postal_Code_Arrival=request.Postal_Code_Arrival,
                                                        Residence_Arrival=request.
                                                            Residence_Arrival, packing_service=request.packing_service,
                                                        packaging_materials
                                                        =request.packaging_materials,
                                                        furniture_assembly_disassembly=request.
                                                            furniture_assembly_disassembly,
                                                        furniture_storage=request.furniture_storage,
                                                        Additional_informations=request.Additional_informations,
                                                        firstname=request.
                                                            firstname, lastname=request.lastname, email=request.email,
                                                        region_id=request.
                                                            region.id, phone_number=request.phone_number,
                                                        distributed=request.distributed,
                                                        moving_date=request.moving_date,
                                                        moving_date1=request.moving_date1,
                                                        moving_date2=request.moving_date2,
                                                        moving_type1_id=request.moving_type1.id,
                                                        moving_type2_id=request.moving_type2.id
                                                    )

                                                    edit_quote_request_email_sent.save()

                    ####################END INTERNATIONAL REQUEST DISTRIBUTION START###################

                return redirect('devis_page6')

            elif request.POST.get('moving_date1') and request.POST.get('moving_date1'):
                moving_date = "1000-10-10"
                moving_date1 = request.POST.get('moving_date1')
                moving_date2 = request.POST.get('moving_date2')

                if Country_Arrival == "0":
                    country_arrival_name = ""
                else:
                    country_arrival_info = Country.objects.filter(id=Country_Arrival).last()
                    country_arrival_name = country_arrival_info.name

                savedata = Quote_Request(ref=ref, region=region,
                                         Postal_Code_Departure=Postal_Code_Departure,
                                         Adresse_Departure=Adresse_Departure, Residence_Number_or_Name_Departure=
                                         Residence_Number_or_Name_Departure, Country_Arrival=country_arrival_name,
                                         City_Arrival_for_international_moving=City_Arrival_for_international_moving,
                                         Adresse_Arrival=Adresse_Arrival,
                                         Residence_Number_or_Name_Arrival=Residence_Number_or_Name_Arrival,
                                         Postal_Code_Arrival=
                                         Postal_Code_Arrival, Residence_Departure=Residence_Departure,
                                         Number_Room_Departure=
                                         Number_Room_Departure, Residence_Arrival=Residence_Arrival,
                                         packing_service=packing_service,
                                         packaging_materials=packaging_materials, furniture_assembly_disassembly=
                                         furniture_assembly_disassembly, furniture_storage=furniture_storage,
                                         firstname=firstname, lastname=lastname, email=email, phone_number=phone_number,
                                         Additional_informations=
                                         Additional_informations, moving_date=moving_date, moving_date1=moving_date1,
                                         moving_date2=
                                         moving_date2, moving_type1=moving_type1, moving_type2=moving_type2, country=
                                         country_departure_request, Region_Arrival_for_national_moving=
                                         Region_Arrival_for_national_moving)
                savedata.save()

                ######################## Automatic distribution for the requests to the movers ####################
                requests = Quote_Request.objects.all().order_by('-id')

                mover_available = False
                for request in requests:

                    # ####################NATIONAL REQUEST DISTRIBUTION START#####################
                    if request.moving_type1.name == 'National':

                        movers = Mover.objects.filter(activated=True)
                        for mover in movers:

                            # we select the movers who deliver in the departure region of the request
                            movers_departure_regions = Mover_Region.objects.filter(region__name=request.region.name,
                                                                                   mover_id=mover.id)

                            # we select the movers who deliver in the arrival region of the request
                            movers_arrival_regions = Mover_Region.objects.filter\
                                (region__name=request.Region_Arrival_for_national_moving, mover_id=mover.id)

                            if movers_departure_regions and movers_arrival_regions:
                                print(mover.company_name)
                                mover_available = True

                                max_request_day = Number_Mover_Quote_Request_PerDay.objects.filter(
                                    mover_id=mover.id,
                                    reception_date_quote_request__date=current_date.date()).last()

                                # We check if the mover has received a request today
                                if max_request_day:

                                    if max_request_day.number_quote_received_the_same_day < mover. \
                                            number_max_quote_request:

                                        # we prevent the mover to receive the same request twice
                                        quote_request_info = Quote_Request.objects.filter(
                                            id=request.id).last()
                                        mover_info = Mover.objects.filter(id=mover.id).last()
                                        number_distribution_request = Number_Distribution_Quote_Request.objects.filter \
                                            (quote_request=quote_request_info.id).last()

                                        if not Mover_Quote_Request.objects.filter(quote_request=quote_request_info,
                                                                                  mover=mover_info):
                                            number = max_request_day.number_quote_received_the_same_day + 1
                                            savedata1 = Number_Mover_Quote_Request_PerDay(
                                                number_quote_received_the_same_day=number, mover=mover_info)

                                            savedata2 = Mover_Quote_Request(quote_request=quote_request_info,
                                                                            mover=mover_info)

                                            # we verify if the request hasn't been distributed more than 5 times
                                            if number_distribution_request:

                                                if number_distribution_request.number_distribution < number_distribution_request. \
                                                        number_max_distribution:
                                                    number_distribution = number_distribution_request.number_distribution + 1
                                                    savedata3 = Number_Distribution_Quote_Request(
                                                        number_distribution=
                                                        number_distribution,
                                                        quote_request=
                                                        quote_request_info)
                                                    savedata3.save()

                                            else:
                                                number_distribution = 1
                                                savedata3 = Number_Distribution_Quote_Request(number_distribution=
                                                                                              number_distribution,
                                                                                              quote_request=
                                                                                              quote_request_info)
                                                savedata3.save()

                                            savedata1.save()
                                            savedata2.save()

                                            # Sending email to the Mover
                                            if not Movers_Email.objects.filter(quote_request__id=
                                                                               savedata2.quote_request.id,
                                                                               mover__id=savedata2.mover.id):
                                                # Sending email
                                                subject = 'ItsMoving - Nouvelle demande de devis'
                                                recipient_email = mover_info.user.email
                                                recipient_last_name = mover_info.user.last_name
                                                company_name = mover_info.company_name
                                                moving_type_name_received = moving_type1.name
                                                email_from = mover_info.user.email
                                                message = f'Une nouvelle demande de devis {moving_type_name_received} ' \
                                                          f'est disponible, Veuillez vous connecter à votre compte afin ' \
                                                          f'de consulter les détails.'

                                                # sending html mail
                                                html_content = render_to_string(
                                                    "base_app/quote_request_notification_email_template.html",
                                                    {'last_name': recipient_last_name,
                                                     'company_name': company_name,
                                                     'message': message,
                                                     'email_from': email_from})
                                                text_centent = strip_tags(html_content)
                                                email = EmailMultiAlternatives(
                                                    # subject
                                                    subject,
                                                    # content
                                                    text_centent,
                                                    # from email
                                                    settings.EMAIL_HOST_USER,
                                                    # receiver list
                                                    [recipient_email]
                                                )
                                                email.attach_alternative(html_content, "text/html")
                                                email.send()

                                                save_mover_email = Movers_Email(quote_request_id=
                                                                                savedata2.quote_request.id,
                                                                                mover_id=
                                                                                savedata2.mover.id)
                                                save_mover_email.save()

                                            if not Customers_Notification_Email.objects.filter(
                                                quote_request__ref=request.ref
                                            ):
                                                save_client_notification_email = Customers_Notification_Email(
                                                    moving_possibility=True, quote_request_id=request.id,
                                                    mover_id=mover.id
                                                )
                                                save_client_notification_email.save()

                                                # We send an email to the customer
                                                subject = 'ItsMoving - Accusé de reception'
                                                recipient_email = savedata.email
                                                recipient_last_name = savedata.lastname
                                                email_from = savedata.email
                                                message = f'Votre demande de devis a bien été reçu, vous aurez un ' \
                                                          f'retour de 5 de nos professionnels dans les heures à venir.'

                                                # sending html mail
                                                html_content = render_to_string(
                                                    "base_app/quote_request_notification_email_template.html",
                                                    {'last_name': recipient_last_name, 'message': message,
                                                     'email_from': email_from})
                                                text_centent = strip_tags(html_content)
                                                email = EmailMultiAlternatives(
                                                    # subject
                                                    subject,
                                                    # content
                                                    text_centent,
                                                    # from email
                                                    settings.EMAIL_HOST_USER,
                                                    # receiver list
                                                    [recipient_email]
                                                )
                                                email.attach_alternative(html_content, "text/html")
                                                email.send()

                                                # we modify the quote to mark the email as sent
                                                edit_quote_request_email_sent = Quote_Request(
                                                    ref=request.ref, country_id=request.country.id, id=request.id,
                                                    created=
                                                    request.created, Adresse_Departure=request.Adresse_Departure,
                                                    Postal_Code_Departure=request.Postal_Code_Departure,
                                                    Residence_Number_or_Name_Departure=request.Residence_Number_or_Name_Departure,
                                                    Residence_Departure=request.Residence_Departure,
                                                    Number_Room_Departure=request.
                                                        Number_Room_Departure, Country_Arrival=request.Country_Arrival,
                                                    City_Arrival_for_international_moving=request.
                                                        City_Arrival_for_international_moving,
                                                    Adresse_Arrival=request.Adresse_Arrival,
                                                    Region_Arrival_for_national_moving=request.Region_Arrival_for_national_moving,
                                                    Residence_Number_or_Name_Arrival=request.Residence_Number_or_Name_Arrival,
                                                    Postal_Code_Arrival=request.Postal_Code_Arrival,
                                                    Residence_Arrival=request.
                                                        Residence_Arrival, packing_service=request.packing_service,
                                                    packaging_materials
                                                    =request.packaging_materials,
                                                    furniture_assembly_disassembly=request.
                                                        furniture_assembly_disassembly,
                                                    furniture_storage=request.furniture_storage,
                                                    Additional_informations=request.Additional_informations,
                                                    firstname=request.
                                                        firstname, lastname=request.lastname, email=request.email,
                                                    region_id=request.
                                                        region.id, phone_number=request.phone_number,
                                                    distributed=request.distributed,
                                                    moving_date=request.moving_date, moving_date1=request.moving_date1,
                                                    moving_date2=request.moving_date2,
                                                    moving_type1_id=request.moving_type1.id,
                                                    moving_type2_id=request.moving_type2.id
                                                )

                                                edit_quote_request_email_sent.save()

                                else:
                                    quote_request_info = Quote_Request.objects.filter(id=request.id).last()
                                    mover_info = Mover.objects.filter(id=mover.id).last()
                                    number_distribution_request = Number_Distribution_Quote_Request.objects.filter \
                                        (quote_request=quote_request_info.id).last()

                                    # the request have to be saved maximum 5 time to 5 differents movers
                                    for i in range(5):

                                        # we prevent the mover to receive the same request twice
                                        if not Mover_Quote_Request.objects.filter(quote_request=quote_request_info,
                                                                                  mover=mover_info):

                                            savedata1 = Number_Mover_Quote_Request_PerDay(
                                                number_quote_received_the_same_day=1,
                                                mover=mover_info)

                                            savedata2 = Mover_Quote_Request(quote_request=
                                                                            quote_request_info,
                                                                            mover=mover_info)

                                            # we verify if the request hasn't been distributed more than 5 times
                                            if number_distribution_request:

                                                if number_distribution_request.number_distribution < number_distribution_request. \
                                                        number_max_distribution:
                                                    number_distribution = number_distribution_request.number_distribution + 1
                                                    savedata3 = Number_Distribution_Quote_Request(
                                                        number_distribution=
                                                        number_distribution,
                                                        quote_request=
                                                        quote_request_info)
                                                    savedata3.save()

                                            else:
                                                number_distribution = 1
                                                savedata3 = Number_Distribution_Quote_Request(number_distribution=
                                                                                              number_distribution,
                                                                                              quote_request=
                                                                                              quote_request_info)
                                                savedata3.save()

                                            savedata1.save()
                                            savedata2.save()

                                            # Sending email to the Mover
                                            if not Movers_Email.objects.filter(quote_request__id=
                                                                               savedata2.quote_request.id,
                                                                               mover__id=savedata2.mover.id):
                                                # Sending email
                                                subject = 'ItsMoving - Nouvelle demande de devis'
                                                recipient_email = mover_info.user.email
                                                recipient_last_name = mover_info.user.last_name
                                                company_name = mover_info.company_name
                                                moving_type_name_received = moving_type1.name
                                                email_from = mover_info.user.email
                                                message = f'Une nouvelle demande de devis {moving_type_name_received} ' \
                                                          f'est disponible, Veuillez vous connecter à votre compte afin ' \
                                                          f'de consulter les détails.'

                                                # sending html mail
                                                html_content = render_to_string(
                                                    "base_app/quote_request_notification_email_template.html",
                                                    {'last_name': recipient_last_name,
                                                     'company_name': company_name,
                                                     'message': message,
                                                     'email_from': email_from})
                                                text_centent = strip_tags(html_content)
                                                email = EmailMultiAlternatives(
                                                    # subject
                                                    subject,
                                                    # content
                                                    text_centent,
                                                    # from email
                                                    settings.EMAIL_HOST_USER,
                                                    # receiver list
                                                    [recipient_email]
                                                )
                                                email.attach_alternative(html_content, "text/html")
                                                email.send()

                                                save_mover_email = Movers_Email(quote_request_id=
                                                                                savedata2.quote_request.id,
                                                                                mover_id=
                                                                                savedata2.mover.id)
                                                save_mover_email.save()

                                            if not Customers_Notification_Email.objects.filter(
                                                    quote_request__ref=request.ref
                                            ):
                                                save_client_notification_email = Customers_Notification_Email(
                                                    moving_possibility=True, quote_request_id=request.id,
                                                    mover_id=mover.id
                                                )
                                                save_client_notification_email.save()

                                                # We send an email to the customer
                                                subject = 'ItsMoving - Accusé de reception'
                                                recipient_email = savedata.email
                                                recipient_last_name = savedata.lastname
                                                email_from = savedata.email
                                                message = f'Votre demande de devis a bien été reçu, vous aurez un ' \
                                                          f'retour de 5 de nos professionnels dans les heures à venir.'

                                                # sending html mail
                                                html_content = render_to_string(
                                                    "base_app/quote_request_notification_email_template.html",
                                                    {'last_name': recipient_last_name, 'message': message,
                                                     'email_from': email_from})
                                                text_centent = strip_tags(html_content)
                                                email = EmailMultiAlternatives(
                                                    # subject
                                                    subject,
                                                    # content
                                                    text_centent,
                                                    # from email
                                                    settings.EMAIL_HOST_USER,
                                                    # receiver list
                                                    [recipient_email]
                                                )
                                                email.attach_alternative(html_content, "text/html")
                                                email.send()

                                                # we modify the quote to mark the email as sent
                                                edit_quote_request_email_sent = Quote_Request(
                                                    ref=request.ref, country_id=request.country.id, id=request.id,
                                                    created=
                                                    request.created, Adresse_Departure=request.Adresse_Departure,
                                                    Postal_Code_Departure=request.Postal_Code_Departure,
                                                    Residence_Number_or_Name_Departure=request.Residence_Number_or_Name_Departure,
                                                    Residence_Departure=request.Residence_Departure,
                                                    Number_Room_Departure=request.
                                                        Number_Room_Departure, Country_Arrival=request.Country_Arrival,
                                                    City_Arrival_for_international_moving=request.
                                                        City_Arrival_for_international_moving,
                                                    Adresse_Arrival=request.Adresse_Arrival,
                                                    Region_Arrival_for_national_moving=request.Region_Arrival_for_national_moving,
                                                    Residence_Number_or_Name_Arrival=request.Residence_Number_or_Name_Arrival,
                                                    Postal_Code_Arrival=request.Postal_Code_Arrival,
                                                    Residence_Arrival=request.
                                                        Residence_Arrival, packing_service=request.packing_service,
                                                    packaging_materials
                                                    =request.packaging_materials,
                                                    furniture_assembly_disassembly=request.
                                                        furniture_assembly_disassembly,
                                                    furniture_storage=request.furniture_storage,
                                                    Additional_informations=request.Additional_informations,
                                                    firstname=request.
                                                        firstname, lastname=request.lastname, email=request.email,
                                                    region_id=request.
                                                        region.id, phone_number=request.phone_number,
                                                    distributed=request.distributed,
                                                    moving_date=request.moving_date, moving_date1=request.moving_date1,
                                                    moving_date2=request.moving_date2,
                                                    moving_type1_id=request.moving_type1.id,
                                                    moving_type2_id=request.moving_type2.id
                                                )

                                                edit_quote_request_email_sent.save()

                            if not mover_available:
                                if not Customers_Notification_Email.objects.filter(
                                    quote_request__email=request.email, quote_request__ref=request.ref
                                ):
                                    save_client_notification_email = Customers_Notification_Email(
                                        moving_possibility=False, quote_request_id=request.id, mover_id=mover.id
                                    )
                                    save_client_notification_email.save()

                                    # We send an email to the customer
                                    subject = 'ItsMoving - Accusé de reception'
                                    recipient_email = savedata.email
                                    recipient_last_name = savedata.lastname
                                    email_from = savedata.email
                                    message = f'{request.ref} - Mover : {mover.company_name}'

                                    # sending html mail
                                    html_content = render_to_string(
                                        "base_app/quote_request_client_notification_email_template.html",
                                        {'last_name': recipient_last_name, 'message': message,
                                         'email_from': email_from})
                                    text_centent = strip_tags(html_content)
                                    email = EmailMultiAlternatives(
                                        # subject
                                        subject,
                                        # content
                                        text_centent,
                                        # from email
                                        settings.EMAIL_HOST_USER,
                                        # receiver list
                                        [recipient_email]
                                    )
                                    email.attach_alternative(html_content, "text/html")
                                    email.send()

                                    # we modify the quote to mark the email as sent
                                    edit_quote_request_email_sent = Quote_Request(
                                        ref=request.ref, country_id=request.country.id, id=request.id, created=
                                        request.created, Adresse_Departure=request.Adresse_Departure,
                                        Postal_Code_Departure=request.Postal_Code_Departure,
                                        Residence_Number_or_Name_Departure=request.Residence_Number_or_Name_Departure,
                                        Residence_Departure=request.Residence_Departure, Number_Room_Departure=request.
                                        Number_Room_Departure, Country_Arrival=request.Country_Arrival,
                                        City_Arrival_for_international_moving=request.
                                        City_Arrival_for_international_moving, Adresse_Arrival=request.Adresse_Arrival,
                                        Region_Arrival_for_national_moving=request.Region_Arrival_for_national_moving,
                                        Residence_Number_or_Name_Arrival=request.Residence_Number_or_Name_Arrival,
                                        Postal_Code_Arrival=request.Postal_Code_Arrival, Residence_Arrival=request.
                                        Residence_Arrival, packing_service=request.packing_service, packaging_materials
                                        =request.packaging_materials, furniture_assembly_disassembly=request.
                                        furniture_assembly_disassembly, furniture_storage=request.furniture_storage,
                                        Additional_informations=request.Additional_informations, firstname=request.
                                        firstname, lastname=request.lastname, email=request.email, region_id=request.
                                        region.id, phone_number=request.phone_number, distributed=request.distributed,
                                        moving_date=request.moving_date, moving_date1=request.moving_date1,
                                        moving_date2=request.moving_date2, moving_type1_id=request.moving_type1.id,
                                        moving_type2_id=request.moving_type2.id
                                    )

                                    edit_quote_request_email_sent.save()

                    # ###################END NATIONAL REQUEST DISTRIBUTION START###################

                    # ####################INTERNATIONAL REQUEST DISTRIBUTION START#####################
                    elif request.moving_type1.name == 'International':

                        movers = Mover.objects.filter(moving_type1__name='International', activated=True)
                        for mover in movers:

                            # we select the mover who work in the country of destination of the request
                            mover_countries = Mover_Country.objects.filter(mover_id=mover.id)
                            for mover_country in mover_countries:
                                if request.Country_Arrival == mover_country.country_name:

                                    max_request_day = Number_Mover_Quote_Request_PerDay.objects.filter(
                                        mover_id=mover.id,
                                        reception_date_quote_request__date=current_date.date()).last()

                                    # We check if the mover has received a request today
                                    if max_request_day:

                                        if max_request_day.number_quote_received_the_same_day < mover. \
                                                number_max_quote_request:

                                            # we prevent the mover to receive the same request twice
                                            quote_request_info = Quote_Request.objects.filter(
                                                id=request.id).last()
                                            mover_info = Mover.objects.filter(id=mover.id).last()
                                            number_distribution_request = Number_Distribution_Quote_Request.objects.filter \
                                                (quote_request=quote_request_info.id).last()

                                            if not Mover_Quote_Request.objects.filter(quote_request=quote_request_info,
                                                                                  mover=mover_info):
                                                number = max_request_day.number_quote_received_the_same_day + 1
                                                savedata1 = Number_Mover_Quote_Request_PerDay(
                                                    number_quote_received_the_same_day=number, mover=mover_info)

                                                savedata2 = Mover_Quote_Request(quote_request=quote_request_info,
                                                                                mover=mover_info)

                                                # we verify if the request hasn't been distributed more than 5 times
                                                if number_distribution_request:

                                                    if number_distribution_request.number_distribution < number_distribution_request. \
                                                            number_max_distribution:

                                                        number_distribution = number_distribution_request.number_distribution + 1
                                                        savedata3 = Number_Distribution_Quote_Request(
                                                            number_distribution=
                                                            number_distribution,
                                                            quote_request=
                                                            quote_request_info)
                                                        savedata3.save()

                                                else:
                                                    number_distribution = 1
                                                    savedata3 = Number_Distribution_Quote_Request(number_distribution=
                                                                                                  number_distribution,
                                                                                                  quote_request=
                                                                                                  quote_request_info)
                                                    savedata3.save()

                                                savedata1.save()
                                                savedata2.save()

                                                # Sending email to the Mover
                                                if not Movers_Email.objects.filter(quote_request__id=
                                                                               savedata2.quote_request.id,
                                                                               mover__id=savedata2.mover.id):
                                                    # Sending email
                                                    subject = 'ItsMoving - Nouvelle demande de devis'
                                                    recipient_email = mover_info.user.email
                                                    recipient_last_name = mover_info.user.last_name
                                                    company_name = mover_info.company_name
                                                    moving_type_name_received = moving_type1.name
                                                    email_from = mover_info.user.email
                                                    message = f'Une nouvelle demande de devis {moving_type_name_received} ' \
                                                              f'est disponible, Veuillez vous connecter à votre compte afin ' \
                                                              f'de consulter les détails.'

                                                    # sending html mail
                                                    html_content = render_to_string(
                                                        "base_app/quote_request_notification_email_template.html",
                                                        {'last_name': recipient_last_name,
                                                         'company_name': company_name,
                                                         'message': message,
                                                         'email_from': email_from})
                                                    text_centent = strip_tags(html_content)
                                                    email = EmailMultiAlternatives(
                                                        # subject
                                                        subject,
                                                        # content
                                                        text_centent,
                                                        # from email
                                                        settings.EMAIL_HOST_USER,
                                                        # receiver list
                                                        [recipient_email]
                                                    )
                                                    email.attach_alternative(html_content, "text/html")
                                                    email.send()

                                                    save_mover_email = Movers_Email(quote_request_id=
                                                                                    savedata2.quote_request.id,
                                                                                    mover_id=
                                                                                    savedata2.mover.id)
                                                    save_mover_email.save()

                                                if not Customers_Notification_Email.objects.filter(
                                                        quote_request__ref=request.ref
                                                ):
                                                    save_client_notification_email = Customers_Notification_Email(
                                                        moving_possibility=True, quote_request_id=request.id,
                                                        mover_id=mover.id
                                                    )
                                                    save_client_notification_email.save()

                                                    # We send an email to the customer
                                                    subject = 'ItsMoving - Accusé de reception'
                                                    recipient_email = savedata.email
                                                    recipient_last_name = savedata.lastname
                                                    email_from = savedata.email
                                                    message = f'Votre demande de devis a bien été reçu, vous aurez un ' \
                                                              f'retour de 5 de nos professionnels dans les heures à venir.'

                                                    # sending html mail
                                                    html_content = render_to_string(
                                                        "base_app/quote_request_notification_email_template.html",
                                                        {'last_name': recipient_last_name, 'message': message,
                                                         'email_from': email_from})
                                                    text_centent = strip_tags(html_content)
                                                    email = EmailMultiAlternatives(
                                                        # subject
                                                        subject,
                                                        # content
                                                        text_centent,
                                                        # from email
                                                        settings.EMAIL_HOST_USER,
                                                        # receiver list
                                                        [recipient_email]
                                                    )
                                                    email.attach_alternative(html_content, "text/html")
                                                    email.send()

                                                    # we modify the quote to mark the email as sent
                                                    edit_quote_request_email_sent = Quote_Request(
                                                        ref=request.ref, country_id=request.country.id, id=request.id,
                                                        created=
                                                        request.created, Adresse_Departure=request.Adresse_Departure,
                                                        Postal_Code_Departure=request.Postal_Code_Departure,
                                                        Residence_Number_or_Name_Departure=request.Residence_Number_or_Name_Departure,
                                                        Residence_Departure=request.Residence_Departure,
                                                        Number_Room_Departure=request.
                                                            Number_Room_Departure,
                                                        Country_Arrival=request.Country_Arrival,
                                                        City_Arrival_for_international_moving=request.
                                                            City_Arrival_for_international_moving,
                                                        Adresse_Arrival=request.Adresse_Arrival,
                                                        Region_Arrival_for_national_moving=request.Region_Arrival_for_national_moving,
                                                        Residence_Number_or_Name_Arrival=request.Residence_Number_or_Name_Arrival,
                                                        Postal_Code_Arrival=request.Postal_Code_Arrival,
                                                        Residence_Arrival=request.
                                                            Residence_Arrival, packing_service=request.packing_service,
                                                        packaging_materials
                                                        =request.packaging_materials,
                                                        furniture_assembly_disassembly=request.
                                                            furniture_assembly_disassembly,
                                                        furniture_storage=request.furniture_storage,
                                                        Additional_informations=request.Additional_informations,
                                                        firstname=request.
                                                            firstname, lastname=request.lastname, email=request.email,
                                                        region_id=request.
                                                            region.id, phone_number=request.phone_number,
                                                        distributed=request.distributed,
                                                        moving_date=request.moving_date,
                                                        moving_date1=request.moving_date1,
                                                        moving_date2=request.moving_date2,
                                                        moving_type1_id=request.moving_type1.id,
                                                        moving_type2_id=request.moving_type2.id
                                                    )

                                                    edit_quote_request_email_sent.save()

                                    else:
                                        quote_request_info = Quote_Request.objects.filter(id=request.id).last()
                                        mover_info = Mover.objects.filter(id=mover.id).last()
                                        number_distribution_request = Number_Distribution_Quote_Request.objects.filter \
                                            (quote_request=quote_request_info.id).last()

                                        # the request have to be saved maximum 5 time to 5 differents movers
                                        for i in range(5):

                                            # we prevent the mover to receive the same request twice
                                            if not Mover_Quote_Request.objects.filter(quote_request=quote_request_info,
                                                                                  mover=mover_info):

                                                savedata1 = Number_Mover_Quote_Request_PerDay(
                                                    number_quote_received_the_same_day=1,
                                                    mover=mover_info)

                                                savedata2 = Mover_Quote_Request(quote_request=
                                                                                quote_request_info,
                                                                                mover=mover_info)

                                                # we verify if the request hasn't been distributed more than 5 times
                                                if number_distribution_request:

                                                    if number_distribution_request.number_distribution < number_distribution_request. \
                                                            number_max_distribution:

                                                        number_distribution = number_distribution_request.number_distribution + 1
                                                        savedata3 = Number_Distribution_Quote_Request(
                                                            number_distribution=
                                                            number_distribution,
                                                            quote_request=
                                                            quote_request_info)
                                                        savedata3.save()

                                                else:
                                                    number_distribution = 1
                                                    savedata3 = Number_Distribution_Quote_Request(number_distribution=
                                                                                                  number_distribution,
                                                                                                  quote_request=
                                                                                                  quote_request_info)
                                                    savedata3.save()

                                                savedata1.save()
                                                savedata2.save()

                                                # Sending email to the Mover
                                                if not Movers_Email.objects.filter(quote_request__id=
                                                                               savedata2.quote_request.id,
                                                                               mover__id=savedata2.mover.id):
                                                    # Sending email
                                                    subject = 'ItsMoving - Nouvelle demande de devis'
                                                    recipient_email = mover_info.user.email
                                                    recipient_last_name = mover_info.user.last_name
                                                    company_name = mover_info.company_name
                                                    moving_type_name_received = moving_type1.name
                                                    email_from = mover_info.user.email
                                                    message = f'Une nouvelle demande de devis {moving_type_name_received} ' \
                                                              f'est disponible, Veuillez vous connecter à votre compte afin ' \
                                                              f'de consulter les détails.'

                                                    # sending html mail
                                                    html_content = render_to_string(
                                                        "base_app/quote_request_notification_email_template.html",
                                                        {'last_name': recipient_last_name,
                                                         'company_name': company_name,
                                                         'message': message,
                                                         'email_from': email_from})
                                                    text_centent = strip_tags(html_content)
                                                    email = EmailMultiAlternatives(
                                                        # subject
                                                        subject,
                                                        # content
                                                        text_centent,
                                                        # from email
                                                        settings.EMAIL_HOST_USER,
                                                        # receiver list
                                                        [recipient_email]
                                                    )
                                                    email.attach_alternative(html_content, "text/html")
                                                    email.send()

                                                    save_mover_email = Movers_Email(quote_request_id=
                                                                                    savedata2.quote_request.id,
                                                                                    mover_id=
                                                                                    savedata2.mover.id)
                                                    save_mover_email.save()

                                                if not Customers_Notification_Email.objects.filter(
                                                        quote_request__ref=request.ref
                                                ):
                                                    save_client_notification_email = Customers_Notification_Email(
                                                        moving_possibility=True, quote_request_id=request.id,
                                                        mover_id=mover.id
                                                    )
                                                    save_client_notification_email.save()

                                                    # We send an email to the customer
                                                    subject = 'ItsMoving - Accusé de reception'
                                                    recipient_email = savedata.email
                                                    recipient_last_name = savedata.lastname
                                                    email_from = savedata.email
                                                    message = f'Votre demande de devis a bien été reçu, vous aurez un ' \
                                                              f'retour de 5 de nos professionnels dans les heures à venir.'

                                                    # sending html mail
                                                    html_content = render_to_string(
                                                        "base_app/quote_request_notification_email_template.html",
                                                        {'last_name': recipient_last_name, 'message': message,
                                                         'email_from': email_from})
                                                    text_centent = strip_tags(html_content)
                                                    email = EmailMultiAlternatives(
                                                        # subject
                                                        subject,
                                                        # content
                                                        text_centent,
                                                        # from email
                                                        settings.EMAIL_HOST_USER,
                                                        # receiver list
                                                        [recipient_email]
                                                    )
                                                    email.attach_alternative(html_content, "text/html")
                                                    email.send()

                                                    # we modify the quote to mark the email as sent
                                                    edit_quote_request_email_sent = Quote_Request(
                                                        ref=request.ref, country_id=request.country.id, id=request.id,
                                                        created=
                                                        request.created, Adresse_Departure=request.Adresse_Departure,
                                                        Postal_Code_Departure=request.Postal_Code_Departure,
                                                        Residence_Number_or_Name_Departure=request.Residence_Number_or_Name_Departure,
                                                        Residence_Departure=request.Residence_Departure,
                                                        Number_Room_Departure=request.
                                                            Number_Room_Departure,
                                                        Country_Arrival=request.Country_Arrival,
                                                        City_Arrival_for_international_moving=request.
                                                            City_Arrival_for_international_moving,
                                                        Adresse_Arrival=request.Adresse_Arrival,
                                                        Region_Arrival_for_national_moving=request.Region_Arrival_for_national_moving,
                                                        Residence_Number_or_Name_Arrival=request.Residence_Number_or_Name_Arrival,
                                                        Postal_Code_Arrival=request.Postal_Code_Arrival,
                                                        Residence_Arrival=request.
                                                            Residence_Arrival, packing_service=request.packing_service,
                                                        packaging_materials
                                                        =request.packaging_materials,
                                                        furniture_assembly_disassembly=request.
                                                            furniture_assembly_disassembly,
                                                        furniture_storage=request.furniture_storage,
                                                        Additional_informations=request.Additional_informations,
                                                        firstname=request.
                                                            firstname, lastname=request.lastname, email=request.email,
                                                        region_id=request.
                                                            region.id, phone_number=request.phone_number,
                                                        distributed=request.distributed,
                                                        moving_date=request.moving_date,
                                                        moving_date1=request.moving_date1,
                                                        moving_date2=request.moving_date2,
                                                        moving_type1_id=request.moving_type1.id,
                                                        moving_type2_id=request.moving_type2.id
                                                    )

                                                    edit_quote_request_email_sent.save()

            #      ####################END INTERNATIONAL REQUEST DISTRIBUTION START###################

                return redirect('devis_page6')

            else:
                messages.error(request, 'Veuillez choisir une date de déménagement !')
                render(request, 'base_app/devis/devis_page5.html')

    return render(request, 'base_app/devis/devis_page5.html')


def devis_page6(request):
    return render(request, 'base_app/devis/devis_page6.html')


def article1_international_moving(request):
    return render(request, 'base_app/article1_international_moving.html')


def article2_belgium_moving(request):
    return render(request, 'base_app/article2_belgium_moving.html')
