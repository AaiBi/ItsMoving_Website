import datetime
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from base_app.forms import Mover_Form
from base_app.models import Mover, Moving_Type1, Mover_Moving_Type1, Moving_Type2, Mover_Moving_Type2, Country, \
    RegionOrProvince, Mover_Country, Mover_Region, Quote_Request, Mover_Quote_Request
import random
from user.models import User_Info


def index(request):
    return render(request, 'base_app/index.html')


def mover_inscription(request):
    if request.method == 'GET':
        return render(request, 'base_app/mover/mover_inscription.html', {'form': UserCreationForm()})
    else:
        if request.POST['password'] == request.POST['password1']:
            if User.objects.filter(username=request.POST.get('username')):
                messages.error(request, 'Erreur ! Ce nom d\'utilisateur existe déjà, veuillez utiliser un autre !')
                return redirect('sign_up_user')
            elif User.objects.filter(email=request.POST.get('email')):
                messages.error(request, 'Erreur ! Cet email existe déjà, veuillez utiliser un autre !')
                return redirect('sign_up_user')
            else:
                try:
                    username = request.POST['username']
                    first_name = request.POST['first_name']
                    last_name = request.POST['last_name']
                    email = request.POST['email']
                    password = request.POST['password']

                    # creating the blanck user_info table
                    indicatif = 0
                    phone_number = 0
                    Adresse = "null"
                    country = "null"
                    activated = True
                    profil_picture = "/user/images/profil_image/random_image.png"

                    # Creation of the user account
                    user = User.objects.create_user(username=username, password=password, first_name=first_name,
                                                    last_name=last_name, email=email)

                    user_info = User_Info(indicatif=indicatif, phone_number=phone_number, Adresse=Adresse,
                                          country=country,
                                          activated=activated, profil_picture=profil_picture, user_id=user.id)
                    user.save()
                    user_info.save()

                    return redirect('mover_inscription_step1', new_user_id=user.id)
                except ValueError:
                    return render(request, 'base_app/mover/mover_inscription.html', {'form': UserCreationForm(), 'error': 'Bad data passed in'})
        else:
            return render(request, 'base_app/mover/mover_inscription.html', {'form': UserCreationForm(), 'error': 'Les deux mots de passe ne correspondent pas !'})


def mover_inscription_step1(request, new_user_id):
    if get_object_or_404(User, id=new_user_id):
        user = get_object_or_404(User, id=new_user_id)
        if request.method == 'POST':
            company_name = request.POST['company_name']
            company_phone_number = request.POST['company_phone_number']
            country = request.POST['country']
            City = request.POST['City']
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
                facebook_link = 0
                instagram_link = 0
                twitter_link = 0
                linkedin_link = 0
                logo = "/user/images/profil_image/random_image.png"

                mover = Mover(ref=ref, company_name=company_name, Adresse=Adresse, City=City, country=country,
                              company_phone_number=company_phone_number, Postal_Code=Postal_Code, employee_number=employee_number,
                              TVA_number=TVA_number, website=website, company_statut=company_statut, company_description=
                              company_description, facebook_link=facebook_link, instagram_link=instagram_link, twitter_link=twitter_link,
                              linkedin_link=linkedin_link, logo=logo, user=user)
                mover.save()

                return redirect('mover_inscription_step2', new_user_id=user.id, mover_id=mover.id)
    else:
        messages.error(request, 'Utilisateur non reconnu !')
        return redirect('mover_inscription')
    return render(request, 'base_app/mover/mover_inscription_step1.html')


def mover_inscription_step2(request, new_user_id, mover_id):
    if get_object_or_404(User, id=new_user_id) and get_object_or_404(Mover, id=mover_id):
        user = get_object_or_404(User, id=new_user_id)
        mover_info = get_object_or_404(Mover, id=mover_id)
        moving_type1 = Moving_Type1.objects.all()

        if request.method == 'POST':
            moving_type1_name = request.POST.getlist('moving_type1_name[]')
            if moving_type1_name:
                # Filling Mover_Moving_Type1 table
                for data in moving_type1_name:
                    if Mover_Moving_Type1.objects.filter(moving_type1_name=data, mover=mover_info):
                        messages.error(request, 'Erreur ! Cette sélection existe déjà dans notre base de données !')
                        return redirect('mover_inscription_step1', new_user_id=user.id, mover_id=mover_info.id)
                    else:
                        savedata = Mover_Moving_Type1(moving_type1_name=data, mover=mover_info)
                        savedata.save()
                return redirect('mover_inscription_step3', new_user_id=user.id, mover_id=mover_info.id)
            else:
                messages.error(request, 'Veuillez faire au moins une sélection !')
                return redirect('mover_inscription_step2', new_user_id=user.id, mover_id=mover_info.id)
    else:
        messages.error(request, 'Utilisateur non reconnu !')
        return redirect('mover_inscription')
    return render(request, 'base_app/mover/mover_inscription_step2.html', {'moving_type1': moving_type1})


def mover_inscription_step3(request, new_user_id, mover_id):
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
                        savedata = Mover_Moving_Type2(moving_type2_name=data, mover=mover_info)
                        savedata.save()
                return redirect('mover_inscription_step4', new_user_id=user.id, mover_id=mover_info.id)
            else:
                messages.error(request, 'Veuillez faire au moins une sélection !')
                return redirect('mover_inscription_step3', new_user_id=user.id, mover_id=mover_info.id)
    else:
        messages.error(request, 'Utilisateur non reconnu !')
        return redirect('mover_inscription')
    return render(request, 'base_app/mover/mover_inscription_step3.html', {'moving_type2': moving_type2})


def mover_inscription_step4(request, new_user_id, mover_id):
    if get_object_or_404(User, id=new_user_id) and get_object_or_404(Mover, id=mover_id):
        countries = Country.objects.all()
        user = get_object_or_404(User, id=new_user_id)
        mover_info = get_object_or_404(Mover, id=mover_id)

        if request.method == 'POST':
            country_name = request.POST.getlist('country_name[]')
            if country_name:
                # Filling Mover_Moving_Type2 table
                for data in country_name:
                    if Mover_Country.objects.filter(country_name=data, mover=mover_info):
                        messages.error(request, 'Erreur ! Cette sélection existe déjà dans notre base de données !')
                        return redirect('mover_inscription_step3', new_user_id=user.id, mover_id=mover_info.id)
                    else:
                        country_info = Country.objects.filter(name=data).last()
                        savedata = Mover_Country(country_name=data, country=country_info, mover=mover_info)
                        savedata.save()

                messages.success(request,
                                 'Félicitations, l\'inscription est terminée, il ne vous reste qu\'à renseigner'
                                 ' les regions dans lesquelles vous allez intervenir !')
                return redirect('login_user')

            else:
                messages.error(request, 'Veuillez faire au moins une sélection !')
                return redirect('mover_inscription_step4', new_user_id=user.id, mover_id=mover_info.id)
    else:
        messages.error(request, 'Utilisateur non reconnu !')
        return redirect('mover_inscription')
    return render(request, 'base_app/mover/mover_inscription_step4.html', {'countries': countries})


def contact_page(request):
    if request.method == "POST":
        try:
            full_name = request.POST.get('full_name')
            phone_number = request.POST.get('phone_number')
            recipient_email = 'sheyp.sarl@gmail.com'
            email = request.POST.get('email')
            subject = request.POST.get('subject')
            message = request.POST.get('message')
            email_from = request.POST.get('email')
            recipient_list = [recipient_email, ]

            # if phone_number.isnumeric():
            #     #Saving the message in the database
            #     message_sent = contact_message(full_name=full_name, email=email, subject=subject, phone_number=phone_number,
            #                              message=message)
            #     message_sent.save()
            #     message1 = f'Nouveau message de la part de {full_name} \n Téléphone: {phone_number} \n Email: {email} \n' \
            #                f'Contenu du message: {message}'
            #     send_mail(subject, message1, email_from, recipient_list)
            #     messages.success(request, f'Votre message à été envoyé avec succès, nous vous contacterons très bientôt !')
            # else:
            #     messages.error(request, f'Le numéro de téléphone ne doit contenir que des chiffres, veuillez reéssayer !')
        except ValueError:
            return render(request, 'user/property_modification.html', {'error': 'Erreur, veuillez reéssayer !'})
    return render(request, 'base_app/contact_page.html')


def devis_page1(request):
    moving_type1 = Moving_Type1.objects.all()
    moving_type2 = Moving_Type2.objects.all()
    country = Country.objects.all()
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
    if request.method == 'POST':
        City_Departure = request.POST.get('City_Departure')
        Adresse_Departure = request.POST.get('Adresse_Departure')
        Postal_Code_Departure = request.POST.get('Postal_Code_Departure')
        Residence_Number_or_Name_Departure = request.POST.get('Residence_Number_or_Name_Departure')
        Residence_Departure = request.POST.get('Residence_Departure')
        Number_Room_Departure = request.POST.get('Number_Room_Departure')

        if City_Departure and Adresse_Departure and Postal_Code_Departure and Residence_Number_or_Name_Departure and Residence_Departure \
                and Number_Room_Departure:
            return redirect('devis_page3', moving_type1_id=moving_type1.id, moving_type2_id=moving_type2.id,
                            country_id=country.id,
                            City_Departure=City_Departure, Adresse_Departure=Adresse_Departure,
                            Postal_Code_Departure=Postal_Code_Departure
                            , Residence_Number_or_Name_Departure=Residence_Number_or_Name_Departure,
                            Number_Room_Departure=
                            Number_Room_Departure, Residence_Departure=Residence_Departure)
        else:
            messages.error(request, 'Veuillez renseigner tous les champs !')
            return redirect('devis_page2')
    return render(request, 'base_app/devis/devis_page2.html')


def devis_page3(request, moving_type1_id, moving_type2_id, country_id, City_Departure, Adresse_Departure,
                Postal_Code_Departure,
                Residence_Number_or_Name_Departure, Number_Room_Departure, Residence_Departure):
    moving_type1 = get_object_or_404(Moving_Type1, pk=moving_type1_id)
    moving_type2 = get_object_or_404(Moving_Type2, pk=moving_type2_id)
    country = get_object_or_404(Country, pk=country_id)
    countries = Country.objects.all()
    if request.method == 'POST':
        if request.POST.get('Country_Arrival'):
            Country_Arrival = request.POST.get('Country_Arrival')
        else:
            Country_Arrival = 0

        City_Arrival = request.POST.get('City_Arrival')
        Adresse_Arrival = request.POST.get('Adresse_Arrival')
        Postal_Code_Arrival = request.POST.get('Postal_Code_Arrival')
        Residence_Number_or_Name_Arrival = request.POST.get('Residence_Number_or_Name_Arrival')
        Residence_Arrival = request.POST.get('Residence_Arrival')

        if City_Arrival and Adresse_Arrival and Postal_Code_Arrival and Residence_Number_or_Name_Arrival and Residence_Arrival:
            return redirect('devis_page4', moving_type1_id=moving_type1.id, moving_type2_id=moving_type2.id,
                            country_id=country.id,
                            City_Departure=City_Departure, Adresse_Departure=Adresse_Departure,
                            Postal_Code_Departure=Postal_Code_Departure
                            , Residence_Number_or_Name_Departure=Residence_Number_or_Name_Departure,
                            Number_Room_Departure=Number_Room_Departure, Residence_Departure=Residence_Departure,
                            Country_Arrival=Country_Arrival, City_Arrival=City_Arrival
                            , Adresse_Arrival=Adresse_Arrival, Postal_Code_Arrival=Postal_Code_Arrival,
                            Residence_Number_or_Name_Arrival=
                            Residence_Number_or_Name_Arrival, Residence_Arrival=Residence_Arrival)
        else:
            messages.error(request, 'Veuillez faire au moins une sélection !')
            return redirect('devis_page3')
    return render(request, 'base_app/devis/devis_page3.html',
                  {'City_Departure': City_Departure, 'Adresse_Departure': Adresse_Departure,
                   'Postal_Code_Departure': Postal_Code_Departure, 'countries': countries,
                   'Residence_Number_or_Name_Departure': Residence_Number_or_Name_Departure,
                   'Number_Room_Departure': Number_Room_Departure, 'Residence_Departure':
                       Residence_Departure, 'moving_type1_id': moving_type1_id})


def devis_page4(request, moving_type1_id, moving_type2_id, country_id, City_Departure, Adresse_Departure,
                Postal_Code_Departure,
                Residence_Number_or_Name_Departure, Number_Room_Departure, Residence_Departure, Country_Arrival,
                City_Arrival, Adresse_Arrival,
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
                            City_Departure=City_Departure, Adresse_Departure=Adresse_Departure,
                            Postal_Code_Departure=Postal_Code_Departure
                            , Residence_Number_or_Name_Departure=Residence_Number_or_Name_Departure,
                            Number_Room_Departure=
                            Number_Room_Departure, Residence_Departure=Residence_Departure, Country_Arrival=
                            Country_Arrival, City_Arrival=City_Arrival, Adresse_Arrival=Adresse_Arrival,
                            Postal_Code_Arrival=Postal_Code_Arrival, Residence_Number_or_Name_Arrival=
                            Residence_Number_or_Name_Arrival, Residence_Arrival=Residence_Arrival, firstname=firstname,
                            lastname=
                            lastname, email=email, phone_number=phone_number)
        else:
            messages.error(request, 'Veuillez faire au moins une sélection !')
            return redirect('devis_page4')
    return render(request, 'base_app/devis/devis_page4.html',
                  {'City_Departure': City_Departure, 'Adresse_Departure': Adresse_Departure,
                   'Postal_Code_Departure': Postal_Code_Departure,
                   'Residence_Number_or_Name_Departure': Residence_Number_or_Name_Departure, 'Country_Arrival':
                       Country_Arrival, 'City_Arrival': City_Arrival, 'Adresse_Arrival': Adresse_Arrival,
                   'Postal_Code_Arrival': Postal_Code_Arrival, 'Residence_Number_or_Name_Arrival':
                       Residence_Number_or_Name_Arrival, 'Residence_Arrival': Residence_Arrival,
                   'Residence_Departure': Residence_Departure, 'Number_Room_Departure':
                       Number_Room_Departure})


def devis_page5(request, moving_type1_id, moving_type2_id, country_id, City_Departure, Adresse_Departure,
                Postal_Code_Departure,
                Residence_Number_or_Name_Departure, Number_Room_Departure, Residence_Departure, Country_Arrival,
                City_Arrival, Adresse_Arrival,
                Postal_Code_Arrival, Residence_Number_or_Name_Arrival, Residence_Arrival, firstname, lastname, email,
                phone_number):
    moving_type1 = get_object_or_404(Moving_Type1, pk=moving_type1_id)
    moving_type2 = get_object_or_404(Moving_Type2, pk=moving_type2_id)
    country_departure_request = get_object_or_404(Country, pk=country_id)
    current_date = datetime.datetime.today()

    if request.method == 'POST':
        furniture_assembly_disassembly = request.POST.get('furniture_assembly_disassembly')
        furniture_storage = request.POST.get('furniture_storage')
        packing_service = request.POST.get('packing_service')
        packaging_materials = request.POST.get('packaging_materials')
        Additional_informations = request.POST.get('Additional_informations')
        #moving_date2 = request.POST.get('moving_date2')

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

        if request.POST.get('moving_date'):
            moving_date = request.POST.get('moving_date')
            moving_date1 = "1000-10-10"
            moving_date2 = "1000-10-10"

            if Country_Arrival == "0":
                country_arrival_name = ""
            else:
                country_arrival_info = Country.objects.filter(id=Country_Arrival).last()
                country_arrival_name = country_arrival_info.name

            savedata = Quote_Request(ref=ref, City_Departure=City_Departure, Postal_Code_Departure=Postal_Code_Departure,
                                     Adresse_Departure=Adresse_Departure, Residence_Number_or_Name_Departure=
                                     Residence_Number_or_Name_Departure, Country_Arrival=country_arrival_name,
                                     City_Arrival=City_Arrival, Adresse_Arrival=Adresse_Arrival,
                                     Residence_Number_or_Name_Arrival=Residence_Number_or_Name_Arrival, Postal_Code_Arrival=
                                     Postal_Code_Arrival, Residence_Departure=Residence_Departure, Number_Room_Departure=
                                     Number_Room_Departure, Residence_Arrival=Residence_Arrival, packing_service=packing_service,
                                     packaging_materials=packaging_materials, furniture_assembly_disassembly=
                                     furniture_assembly_disassembly, furniture_storage=furniture_storage, firstname=firstname,
                                     lastname=lastname, email=email, phone_number=phone_number, Additional_informations=
                                     Additional_informations, moving_date=moving_date, moving_date1=moving_date1, moving_date2=
                                     moving_date2, moving_type1=moving_type1, moving_type2=moving_type2, country=
                                     country_departure_request)

            # Automatic distribution of the quote request to the movers
            if moving_type1.name == "National":
                moving_type1_national = Moving_Type1.objects.filter(name="National")
                movers_countries = Mover_Country.objects.all()
                countries = Country.objects.all()
                movers = Mover.objects.all()

                for mover in movers:
                    for mover_country in movers_countries:
                        if mover_country.mover_id == mover.id:

                            for country in countries:
                                if country.id == mover_country.country_id:

                                    # we select only the movers that one of the departure countries are the same to the
                                    # departure country of the request
                                    if mover_country.country_name == country_departure_request.name \
                                            and mover_country.departure == True:
                                        movers_quotes_requests = Mover_Quote_Request.objects.filter(mover_id=mover.id)

                                        if movers_quotes_requests:
                                            for mover_request in movers_quotes_requests:

                                                #we verify if the mover didnt reach his max quote request of the day
                                                if mover_request.created.date() == current_date.date():

                                                    number_quote_request_received = Mover_Quote_Request.objects.filter(
                                                        mover_id=mover.id).count()

                                                    if number_quote_request_received < mover.number_max_quote_request:
                                                        print(number_quote_request_received)
                                                        print(mover.company_name)

                                                        #number_request_received_per_day


            #savedata.save()
            return redirect('devis_page6')

        elif request.POST.get('moving_date1') and request.POST.get('moving_date1'):
            moving_date = "1000-10-10"
            moving_date1 = request.POST.get('moving_date1')
            moving_date2 = request.POST.get('moving_date2')

            country_arrival_info = Country.objects.filter(id=Country_Arrival).last()

            savedata = Quote_Request(ref=ref, City_Departure=City_Departure,
                                     Postal_Code_Departure=Postal_Code_Departure,
                                     Adresse_Departure=Adresse_Departure, Residence_Number_or_Name_Departure=
                                     Residence_Number_or_Name_Departure, Country_Arrival=country_arrival_info.name,
                                     City_Arrival=City_Arrival, Adresse_Arrival=Adresse_Arrival,
                                     Residence_Number_or_Name_Arrival=Residence_Number_or_Name_Arrival,
                                     Postal_Code_Arrival=
                                     Postal_Code_Arrival, Residence_Departure=Residence_Departure,
                                     Number_Room_Departure=
                                     Number_Room_Departure, Residence_Arrival=Residence_Arrival,
                                     packing_service=packing_service,
                                     packaging_materials=packaging_materials, furniture_assembly_disassembly=
                                     furniture_assembly_disassembly, furniture_storage=furniture_storage,
                                     firstname=firstname,
                                     lastname=lastname, email=email, phone_number=phone_number, Additional_informations=
                                     Additional_informations, moving_date=moving_date, moving_date1=moving_date1,
                                     moving_date2=
                                     moving_date2, moving_type1=moving_type1, moving_type2=moving_type2,
                                     country=country_departure_request)
            savedata.save()
            return redirect('devis_page6')

        else:
            messages.error(request, 'Veuillez choisir une date de déménagement !')
            return redirect('devis_page5', moving_type1_id=moving_type1.id, moving_type2_id=moving_type2.id,
                            country_id=country_departure_request.id,
                            City_Departure=City_Departure, Adresse_Departure=Adresse_Departure,
                            Postal_Code_Departure=Postal_Code_Departure
                            , Residence_Number_or_Name_Departure=Residence_Number_or_Name_Departure,
                            Number_Room_Departure=
                            Number_Room_Departure, Residence_Departure=Residence_Departure, City_Arrival=City_Arrival
                            , Adresse_Arrival=Adresse_Arrival, Postal_Code_Arrival=Postal_Code_Arrival,
                            Residence_Number_or_Name_Arrival=
                            Residence_Number_or_Name_Arrival, Residence_Arrival=Residence_Arrival, firstname=firstname,
                            lastname=lastname, email=email, phone_number=phone_number)

    return render(request, 'base_app/devis/devis_page5.html')


def devis_page6(request):
    return render(request, 'base_app/devis/devis_page6.html')


def article1_international_moving(request):
    return render(request, 'base_app/article1_international_moving.html')


def article2_belgium_moving(request):
    return render(request, 'base_app/article2_belgium_moving.html')
