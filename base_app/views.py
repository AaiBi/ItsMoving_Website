import datetime
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from base_app.models import Mover, Moving_Type1, Moving_Type2, Mover_Moving_Type2, Country, \
    Mover_Country, Quote_Request, Mover_Quote_Request, \
    Number_Mover_Quote_Request_PerDay, Number_Distribution_Quote_Request
import random


def index(request):
    return render(request, 'base_app/index.html')


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
        moving_type1 = Moving_Type1.objects.all()
        user = get_object_or_404(User, id=new_user_id)
        if request.method == 'POST':
            company_name = request.POST['company_name']
            company_phone_number = request.POST['company_phone_number']
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
                logo = "/user/images/profil_image/09.jpg"
                country = Country.objects.filter(id=request.POST['country_id']).last()
                moving_type1 = Moving_Type1.objects.filter(id=request.POST['moving_type1_id']).last()

                mover = Mover(ref=ref, company_name=company_name, Adresse=Adresse, City=City, country=country,
                              company_phone_number=company_phone_number, Postal_Code=Postal_Code,
                              employee_number=employee_number, TVA_number=TVA_number, website=website, company_statut=
                              company_statut, company_description=company_description, logo=logo, user=user,
                              moving_type1=moving_type1)
                mover.save()

                return redirect('mover_inscription_step2', new_user_id=user.id, mover_id=mover.id)
    else:
        messages.error(request, 'Utilisateur non reconnu !')
        return redirect('mover_inscription')
    return render(request, 'base_app/mover/mover_inscription_step1.html', {'country': country, 'moving_type1':
        moving_type1})


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
                            #Sending email
                            subject = 'Bienvenue chez ItsMoving'
                            recipient_email = mover_info.user.email
                            email_from = mover_info.user.email
                            recipient_list = [recipient_email, ]

                            message = 'Félicitations !\nVotre compte a été crée avec succès, il sera activer d\'ici ' \
                                      '24h !'
                            send_mail(subject, message, email_from, recipient_list, fail_silently=False)

                            messages.success(request,
                                             'Félicitations, l\'inscription est terminée, il ne vous reste qu\'à '
                                             'renseigner les regions dans lesquelles vous allez intervenir !')
                            return redirect('login_user')
                        else:
                            # Sending email
                            subject = 'Bienvenue chez ItsMoving'
                            recipient_email = mover_info.user.email
                            email_from = mover_info.user.email
                            recipient_list = [recipient_email, ]

                            message = 'Félicitations !\nVotre compte a été crée avec succès, il sera activer d\'ici ' \
                                      '24h !'
                            send_mail(subject, message, email_from, recipient_list, fail_silently=False)

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
                return redirect('mover_inscription_step3', new_user_id=user.id, mover_id=mover_info.id)
    else:
        messages.error(request, 'Utilisateur non reconnu !')
        return redirect('mover_inscription')
    return render(request, 'base_app/mover/mover_inscription_step3.html', {'countries': countries})


def contact_page(request):
    if request.method == "POST":
        full_name = request.POST.get('full_name')

        recipient_email = 'sheyp.sarl@gmail.com'

        email_from = request.POST.get('email')
        message = request.POST.get('message')
        recipient_list = [recipient_email, ]

        message1 = f'Nouveau message de la part de {full_name} \n Email: {email_from} \n' \
                   f'Contenu du message: {message}'
        send_mail(full_name, message1, email_from, recipient_list, fail_silently=False)

        messages.success(request, f'Votre message à été envoyé avec succès, nous vous contacterons très bientôt !')

    return render(request, 'base_app/contact_page.html')


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

                savedata = Quote_Request(ref=ref, City_Departure=City_Departure,
                                         Postal_Code_Departure=Postal_Code_Departure,
                                         Adresse_Departure=Adresse_Departure, Residence_Number_or_Name_Departure=
                                         Residence_Number_or_Name_Departure, Country_Arrival=country_arrival_name,
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
                                         moving_date2, moving_type1=moving_type1, moving_type2=moving_type2, country=
                                         country_departure_request)
                savedata.save()

                ######################## Automatic distribution for the requests to the movers ####################
                requests = Quote_Request.objects.all().order_by('-id')

                for request in requests:

                    #####################NATIONAL REQUEST DISTRIBUTION START#####################
                    if request.moving_type1.name == 'National':

                        movers = Mover.objects.filter(activated=True)
                        for mover in movers:

                            max_request_day = Number_Mover_Quote_Request_PerDay.objects.filter(mover_id=mover.id,
                                                        reception_date_quote_request__date=current_date.date()).last()

                            # We check if the mover has received a request today
                            if max_request_day:

                                print(mover.company_name, ' recieved ', max_request_day.number_quote_received_the_same_day,
                                      ' today ')
                                if max_request_day.number_quote_received_the_same_day < mover.number_max_quote_request:

                                    # we prevent the mover to receive the same request twice
                                    quote_request_info = Quote_Request.objects.filter(id=request.id).last()
                                    mover_info = Mover.objects.filter(id=mover.id).last()
                                    number_distribution_request = Number_Distribution_Quote_Request.objects.filter \
                                        (quote_request=quote_request_info.id).last()

                                    if Mover_Quote_Request.objects.filter(quote_request=quote_request_info,
                                                                          mover=mover_info):
                                        print(mover.company_name, " cant receive the same request more than "
                                                                  "one time")
                                    else:
                                        number = max_request_day.number_quote_received_the_same_day + 1
                                        savedata1 = Number_Mover_Quote_Request_PerDay(
                                            number_quote_received_the_same_day=number, mover=mover_info)

                                        savedata = Mover_Quote_Request(quote_request=quote_request_info, mover=
                                        mover_info)

                                        # we verify if the request hasn't been distributed more than 5 times
                                        if number_distribution_request:

                                            if number_distribution_request.number_distribution < number_distribution_request. \
                                                    number_max_distribution:

                                                number_distribution = number_distribution_request.number_distribution + 1
                                                savedata2 = Number_Distribution_Quote_Request(number_distribution=
                                                                                              number_distribution,
                                                                                              quote_request=
                                                                                              quote_request_info)
                                                savedata2.save()

                                            else:
                                                print(request.ref, ' a atteint le maximum de 5 distributions')

                                        else:
                                            number_distribution = 1
                                            savedata2 = Number_Distribution_Quote_Request(number_distribution=
                                                                                          number_distribution,
                                                                                          quote_request=
                                                                                          quote_request_info)
                                            savedata2.save()

                                        savedata.save()
                                        savedata1.save()

                                        # Sending email to the Mover
                                        subject = 'ItsMoving - Nouvelle demande de devis'
                                        recipient_email = mover_info.user.email
                                        email_from = mover_info.user.email
                                        recipient_list = [recipient_email, ]
                                        message = f'Bonjour {mover_info.company_name}!\nVous venez de recevoir une ' \
                                                  f'nouvelle demande de devis, veuillez accéder à votre compte pour ' \
                                                  f'plus de détails. Merci !'
                                        send_mail(subject, message, email_from, recipient_list, fail_silently=False)

                                        # Sending email to the client
                                        subject = 'ItsMoving - Demande de devis reçu'
                                        recipient_email = email
                                        email_from = email
                                        recipient_list = [recipient_email, ]
                                        message = f'Bonjour Mr/Mme {lastname}!\nVotre demande de devis a bien été reçu,' \
                                                  f' vous aurez un retour très bientôt, Merci !'
                                        send_mail(subject, message, email_from, recipient_list, fail_silently=False)

                                else:
                                    print(mover.company_name, " max atteint pour ajourdhui !")

                            else:
                                quote_request_info = Quote_Request.objects.filter(id=request.id).last()
                                mover_info = Mover.objects.filter(id=mover.id).last()
                                number_distribution_request = Number_Distribution_Quote_Request.objects.filter \
                                    (quote_request=quote_request_info.id).last()

                                # the request have to be saved maximum 5 time to 5 differents movers
                                for i in range(5):

                                    # we prevent the mover to receive the same request twice
                                    if Mover_Quote_Request.objects.filter(quote_request=quote_request_info,
                                                                          mover=mover_info):
                                        print("you cant receive the same request more than "
                                              "one time")
                                    else:

                                        savedata1 = Number_Mover_Quote_Request_PerDay(number_quote_received_the_same_day=1,
                                                                                      mover=mover_info)

                                        savedata = Mover_Quote_Request(quote_request=
                                                                       quote_request_info,
                                                                       mover=mover_info)

                                        # we verify if the request hasn't been distributed more than 5 times
                                        if number_distribution_request:

                                            if number_distribution_request.number_distribution < number_distribution_request. \
                                                    number_max_distribution:

                                                number_distribution = number_distribution_request.number_distribution + 1
                                                savedata2 = Number_Distribution_Quote_Request(number_distribution=
                                                                                              number_distribution,
                                                                                              quote_request=
                                                                                              quote_request_info)
                                                savedata2.save()

                                            else:
                                                print(request.ref, ' a atteint le maximum de 5 distributions')

                                        else:
                                            number_distribution = 1
                                            savedata2 = Number_Distribution_Quote_Request(number_distribution=
                                                                                          number_distribution,
                                                                                          quote_request=
                                                                                          quote_request_info)
                                            savedata2.save()

                                        savedata.save()
                                        savedata1.save()

                                        # Sending email to the Mover
                                        subject = 'ItsMoving - Nouvelle demande de devis'
                                        recipient_email = mover_info.user.email
                                        email_from = mover_info.user.email
                                        recipient_list = [recipient_email, ]
                                        message = f'Bonjour {mover_info.company_name}!\nVous venez de recevoir une ' \
                                                  f'nouvelle demande de devis, veuillez accéder à votre compte pour ' \
                                                  f'plus de détails. Merci !'
                                        send_mail(subject, message, email_from, recipient_list, fail_silently=False)

                                        # Sending email
                                        subject = 'ItsMoving - Demande de devis reçu'
                                        recipient_email = email
                                        email_from = email
                                        recipient_list = [recipient_email, ]
                                        message = f'Bonjour Mr/Mme {lastname}!\nVotre demande de devis a bien été reçu,' \
                                                  f' vous aurez un retour très bientôt, Merci !'
                                        send_mail(subject, message, email_from, recipient_list, fail_silently=False)
                                        print("email sent")

                    ####################END NATIONAL REQUEST DISTRIBUTION START###################

                    #####################INTERNATIONAL REQUEST DISTRIBUTION START#####################
                    elif request.moving_type1.name == 'International':

                        movers = Mover.objects.filter(moving_type1__name='International', activated=True)
                        for mover in movers:

                            # we select the mover who work in the country of the request
                            mover_countries = Mover_Country.objects.filter(mover_id=mover.id)
                            for mover_country in mover_countries:
                                if request.Country_Arrival == mover_country.country_name:

                                    max_request_day = Number_Mover_Quote_Request_PerDay.objects.filter(
                                        mover_id=mover.id,
                                        reception_date_quote_request__date=current_date.date()).last()

                                    # We check if the mover has received a request today
                                    if max_request_day:

                                        print(mover.company_name, ' recieved ',
                                              max_request_day.number_quote_received_the_same_day,
                                              ' today ')
                                        if max_request_day.number_quote_received_the_same_day < mover. \
                                                number_max_quote_request:

                                            # we prevent the mover to receive the same request twice
                                            quote_request_info = Quote_Request.objects.filter(
                                                id=request.id).last()
                                            mover_info = Mover.objects.filter(id=mover.id).last()
                                            number_distribution_request = Number_Distribution_Quote_Request.objects.filter \
                                                (quote_request=quote_request_info.id).last()

                                            if Mover_Quote_Request.objects.filter(quote_request=quote_request_info,
                                                                                  mover=mover_info):
                                                print(mover.company_name,
                                                      " cant receive the same request more than "
                                                      "one time")
                                            else:
                                                number = max_request_day.number_quote_received_the_same_day + 1
                                                savedata1 = Number_Mover_Quote_Request_PerDay(
                                                    number_quote_received_the_same_day=number, mover=mover_info)

                                                savedata = Mover_Quote_Request(quote_request=quote_request_info,
                                                                               mover=mover_info)

                                                # we verify if the request hasn't been distributed more than 5 times
                                                if number_distribution_request:

                                                    if number_distribution_request.number_distribution < number_distribution_request. \
                                                            number_max_distribution:

                                                        number_distribution = number_distribution_request.number_distribution + 1
                                                        savedata2 = Number_Distribution_Quote_Request(number_distribution=
                                                                                                      number_distribution,
                                                                                                      quote_request=
                                                                                                      quote_request_info)
                                                        savedata2.save()

                                                    else:
                                                        print(request.ref, ' a atteint le maximum de 5 distributions')

                                                else:
                                                    number_distribution = 1
                                                    savedata2 = Number_Distribution_Quote_Request(number_distribution=
                                                                                                  number_distribution,
                                                                                                  quote_request=
                                                                                                  quote_request_info)
                                                    savedata2.save()

                                                savedata.save()
                                                savedata1.save()

                                                # Sending email to the Mover
                                                subject = 'ItsMoving - Nouvelle demande de devis'
                                                recipient_email = mover_info.user.email
                                                email_from = mover_info.user.email
                                                recipient_list = [recipient_email, ]
                                                message = f'Bonjour {mover_info.company_name}!\nVous venez de recevoir une ' \
                                                          f'nouvelle demande de devis, veuillez accéder à votre compte pour ' \
                                                          f'plus de détails. Merci !'
                                                send_mail(subject, message, email_from, recipient_list,
                                                          fail_silently=False)

                                                # Sending email to the client
                                                subject = 'ItsMoving - Demande de devis reçu'
                                                recipient_email = email
                                                email_from = email
                                                recipient_list = [recipient_email, ]
                                                message = f'Bonjour Mr/Mme {lastname}!\nVotre demande de devis a bien été reçu,' \
                                                          f' vous aurez un retour très bientôt, Merci !'
                                                send_mail(subject, message, email_from, recipient_list,
                                                          fail_silently=False)

                                        else:
                                            print(mover.company_name, " max atteint pour ajourdhui !")

                                    else:
                                        quote_request_info = Quote_Request.objects.filter(id=request.id).last()
                                        mover_info = Mover.objects.filter(id=mover.id).last()
                                        number_distribution_request = Number_Distribution_Quote_Request.objects.filter \
                                            (quote_request=quote_request_info.id).last()

                                        # the request have to be saved maximum 5 time to 5 differents movers
                                        for i in range(5):

                                            # we prevent the mover to receive the same request twice
                                            if Mover_Quote_Request.objects.filter(quote_request=quote_request_info,
                                                                                  mover=mover_info):
                                                print("you cant receive the same request more than "
                                                      "one time")
                                            else:

                                                savedata1 = Number_Mover_Quote_Request_PerDay(
                                                    number_quote_received_the_same_day=1,
                                                    mover=mover_info)

                                                savedata = Mover_Quote_Request(quote_request=
                                                                               quote_request_info,
                                                                               mover=mover_info)

                                                # we verify if the request hasn't been distributed more than 5 times
                                                if number_distribution_request:

                                                    if number_distribution_request.number_distribution < number_distribution_request. \
                                                            number_max_distribution:

                                                        number_distribution = number_distribution_request.number_distribution + 1
                                                        savedata2 = Number_Distribution_Quote_Request(number_distribution=
                                                                                                      number_distribution,
                                                                                                      quote_request=
                                                                                                      quote_request_info)
                                                        savedata2.save()

                                                    else:
                                                        print(request.ref, ' a atteint le maximum de 5 distributions')

                                                else:
                                                    number_distribution = 1
                                                    savedata2 = Number_Distribution_Quote_Request(number_distribution=
                                                                                                  number_distribution,
                                                                                                  quote_request=
                                                                                                  quote_request_info)
                                                    savedata2.save()

                                                savedata.save()
                                                savedata1.save()

                                                # Sending email to the Mover
                                                subject = 'ItsMoving - Nouvelle demande de devis'
                                                recipient_email = mover_info.user.email
                                                email_from = mover_info.user.email
                                                recipient_list = [recipient_email, ]
                                                message = f'Bonjour {mover_info.company_name}!\nVous venez de recevoir une ' \
                                                          f'nouvelle demande de devis, veuillez accéder à votre compte pour ' \
                                                          f'plus de détails. Merci !'
                                                send_mail(subject, message, email_from, recipient_list,
                                                          fail_silently=False)

                                                # Sending email to the client
                                                subject = 'ItsMoving - Demande de devis reçu'
                                                recipient_email = email
                                                email_from = email
                                                recipient_list = [recipient_email, ]
                                                message = f'Bonjour Mr/Mme {lastname}!\nVotre demande de devis a bien été reçu,' \
                                                          f' vous aurez un retour très bientôt, Merci !'
                                                send_mail(subject, message, email_from, recipient_list,
                                                          fail_silently=False)
                                                print("email sent")



                                else:
                                    print(request.Country_Arrival, ' fait pas partie de la liste de destination de ',
                                          mover_country.country.name)
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

                savedata = Quote_Request(ref=ref, City_Departure=City_Departure,
                                         Postal_Code_Departure=Postal_Code_Departure,
                                         Adresse_Departure=Adresse_Departure, Residence_Number_or_Name_Departure=
                                         Residence_Number_or_Name_Departure, Country_Arrival=country_arrival_name,
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

                ######################## Automatic distribution for the requests to the movers ####################
                requests = Quote_Request.objects.all().order_by('-id')

                for request in requests:

                    #####################NATIONAL REQUEST DISTRIBUTION START#####################
                    if request.moving_type1.name == 'National':
                        print('National')
                        movers = Mover.objects.all()
                        for mover in movers:

                            max_request_day = Number_Mover_Quote_Request_PerDay.objects.filter(mover_id=mover.id,
                                                                                               reception_date_quote_request__date=current_date.date()).last()

                            # We check if the mover has received a request today
                            if max_request_day:

                                print(mover.company_name, ' recieved ', max_request_day.number_quote_received_the_same_day,
                                      ' today ')
                                if max_request_day.number_quote_received_the_same_day < mover.number_max_quote_request:

                                    # we prevent the mover to receive the same request twice
                                    quote_request_info = Quote_Request.objects.filter(id=request.id).last()
                                    mover_info = Mover.objects.filter(id=mover.id).last()
                                    number_distribution_request = Number_Distribution_Quote_Request.objects.filter \
                                        (quote_request=quote_request_info.id).last()

                                    if Mover_Quote_Request.objects.filter(quote_request=quote_request_info,
                                                                          mover=mover_info):
                                        print(mover.company_name, " cant receive the same request more than "
                                                                  "one time")
                                    else:
                                        number = max_request_day.number_quote_received_the_same_day + 1
                                        savedata1 = Number_Mover_Quote_Request_PerDay(
                                            number_quote_received_the_same_day=number, mover=mover_info)

                                        savedata = Mover_Quote_Request(quote_request=quote_request_info, mover=
                                        mover_info)

                                        # we verify if the request hasn't been distributed more than 5 times
                                        if number_distribution_request:

                                            if number_distribution_request.number_distribution < number_distribution_request. \
                                                    number_max_distribution:

                                                number_distribution = number_distribution_request.number_distribution + 1
                                                savedata2 = Number_Distribution_Quote_Request(number_distribution=
                                                                                              number_distribution,
                                                                                              quote_request=
                                                                                              quote_request_info)
                                                savedata2.save()

                                            else:
                                                print(request.ref, ' a atteint le maximum de 5 distributions')

                                        else:
                                            number_distribution = 1
                                            savedata2 = Number_Distribution_Quote_Request(number_distribution=
                                                                                          number_distribution,
                                                                                          quote_request=
                                                                                          quote_request_info)
                                            savedata2.save()

                                        savedata.save()
                                        savedata1.save()

                                        # Sending email to the Mover
                                        subject = 'ItsMoving - Nouvelle demande de devis'
                                        recipient_email = mover_info.user.email
                                        email_from = mover_info.user.email
                                        recipient_list = [recipient_email, ]
                                        message = f'Bonjour {mover_info.company_name}!\nVous venez de recevoir une ' \
                                                  f'nouvelle demande de devis, veuillez accéder à votre compte pour ' \
                                                  f'plus de détails. Merci !'
                                        send_mail(subject, message, email_from, recipient_list, fail_silently=False)

                                        # Sending email to the client
                                        subject = 'ItsMoving - Demande de devis reçu'
                                        recipient_email = email
                                        email_from = email
                                        recipient_list = [recipient_email, ]
                                        message = f'Bonjour Mr/Mme {lastname}!\nVotre demande de devis a bien été reçu,' \
                                                  f' vous aurez un retour très bientôt, Merci !'
                                        send_mail(subject, message, email_from, recipient_list,
                                                  fail_silently=False)

                                else:
                                    print(mover.company_name, " max atteint pour ajourdhui !")

                            else:
                                quote_request_info = Quote_Request.objects.filter(id=request.id).last()
                                mover_info = Mover.objects.filter(id=mover.id).last()
                                number_distribution_request = Number_Distribution_Quote_Request.objects.filter \
                                    (quote_request=quote_request_info.id).last()

                                # the request have to be saved maximum 5 time to 5 differents movers
                                for i in range(5):

                                    # we prevent the mover to receive the same request twice
                                    if Mover_Quote_Request.objects.filter(quote_request=quote_request_info,
                                                                          mover=mover_info):
                                        print("you cant receive the same request more than "
                                              "one time")
                                    else:

                                        savedata1 = Number_Mover_Quote_Request_PerDay(number_quote_received_the_same_day=1,
                                                                                      mover=mover_info)

                                        savedata = Mover_Quote_Request(quote_request=
                                                                       quote_request_info,
                                                                       mover=mover_info)

                                        # we verify if the request hasn't been distributed more than 5 times
                                        if number_distribution_request:

                                            if number_distribution_request.number_distribution < number_distribution_request. \
                                                    number_max_distribution:

                                                number_distribution = number_distribution_request.number_distribution + 1
                                                savedata2 = Number_Distribution_Quote_Request(number_distribution=
                                                                                              number_distribution,
                                                                                              quote_request=
                                                                                              quote_request_info)
                                                savedata2.save()

                                            else:
                                                print(request.ref, ' a atteint le maximum de 5 distributions')

                                        else:
                                            number_distribution = 1
                                            savedata2 = Number_Distribution_Quote_Request(number_distribution=
                                                                                          number_distribution,
                                                                                          quote_request=
                                                                                          quote_request_info)
                                            savedata2.save()

                                        savedata.save()
                                        savedata1.save()

                                        # Sending email to the Mover
                                        subject = 'ItsMoving - Nouvelle demande de devis'
                                        recipient_email = mover_info.user.email
                                        email_from = mover_info.user.email
                                        recipient_list = [recipient_email, ]
                                        message = f'Bonjour {mover_info.company_name}!\nVous venez de recevoir une ' \
                                                  f'nouvelle demande de devis, veuillez accéder à votre compte pour ' \
                                                  f'plus de détails. Merci !'
                                        send_mail(subject, message, email_from, recipient_list, fail_silently=False)

                                        # Sending email to the client
                                        subject = 'ItsMoving - Demande de devis reçu'
                                        recipient_email = email
                                        email_from = email
                                        recipient_list = [recipient_email, ]
                                        message = f'Bonjour Mr/Mme {lastname}!\nVotre demande de devis a bien été reçu,' \
                                                  f' vous aurez un retour très bientôt, Merci !'
                                        send_mail(subject, message, email_from, recipient_list,
                                                  fail_silently=False)
                                        print("email sent")

                    ####################END NATIONAL REQUEST DISTRIBUTION START###################

                    #####################INTERNATIONAL REQUEST DISTRIBUTION START#####################
                    elif request.moving_type1.name == 'International':

                        movers = Mover.objects.filter(moving_type1__name='International')
                        for mover in movers:

                            # we select the mover who work in the country of the request
                            mover_countries = Mover_Country.objects.filter(mover_id=mover.id)
                            for mover_country in mover_countries:
                                if request.Country_Arrival == mover_country.country_name:

                                    max_request_day = Number_Mover_Quote_Request_PerDay.objects.filter(
                                        mover_id=mover.id,
                                        reception_date_quote_request__date=current_date.date()).last()

                                    # We check if the mover has received a request today
                                    if max_request_day:

                                        print(mover.company_name, ' recieved ',
                                              max_request_day.number_quote_received_the_same_day,
                                              ' today ')
                                        if max_request_day.number_quote_received_the_same_day < mover. \
                                                number_max_quote_request:

                                            # we prevent the mover to receive the same request twice
                                            quote_request_info = Quote_Request.objects.filter(
                                                id=request.id).last()
                                            mover_info = Mover.objects.filter(id=mover.id).last()
                                            number_distribution_request = Number_Distribution_Quote_Request.objects.filter \
                                                (quote_request=quote_request_info.id).last()

                                            if Mover_Quote_Request.objects.filter(quote_request=quote_request_info,
                                                                                  mover=mover_info):
                                                print(mover.company_name,
                                                      " cant receive the same request more than "
                                                      "one time")
                                            else:
                                                number = max_request_day.number_quote_received_the_same_day + 1
                                                savedata1 = Number_Mover_Quote_Request_PerDay(
                                                    number_quote_received_the_same_day=number, mover=mover_info)

                                                savedata = Mover_Quote_Request(quote_request=quote_request_info,
                                                                               mover=mover_info)

                                                # we verify if the request hasn't been distributed more than 5 times
                                                if number_distribution_request:

                                                    if number_distribution_request.number_distribution < number_distribution_request. \
                                                            number_max_distribution:

                                                        number_distribution = number_distribution_request.number_distribution + 1
                                                        savedata2 = Number_Distribution_Quote_Request(number_distribution=
                                                                                                      number_distribution,
                                                                                                      quote_request=
                                                                                                      quote_request_info)
                                                        savedata2.save()

                                                    else:
                                                        print(request.ref, ' a atteint le maximum de 5 distributions')

                                                else:
                                                    number_distribution = 1
                                                    savedata2 = Number_Distribution_Quote_Request(number_distribution=
                                                                                                  number_distribution,
                                                                                                  quote_request=
                                                                                                  quote_request_info)
                                                    savedata2.save()

                                                savedata.save()
                                                savedata1.save()

                                                # Sending email to the Mover
                                                subject = 'ItsMoving - Nouvelle demande de devis'
                                                recipient_email = mover_info.user.email
                                                email_from = mover_info.user.email
                                                recipient_list = [recipient_email, ]
                                                message = f'Bonjour {mover_info.company_name}!\nVous venez de recevoir une ' \
                                                          f'nouvelle demande de devis, veuillez accéder à votre compte pour ' \
                                                          f'plus de détails. Merci !'
                                                send_mail(subject, message, email_from, recipient_list,
                                                          fail_silently=False)

                                                # Sending email to the client
                                                subject = 'ItsMoving - Demande de devis reçu'
                                                recipient_email = email
                                                email_from = email
                                                recipient_list = [recipient_email, ]
                                                message = f'Bonjour Mr/Mme {lastname}!\nVotre demande de devis a bien été reçu,' \
                                                          f' vous aurez un retour très bientôt, Merci !'
                                                send_mail(subject, message, email_from, recipient_list,
                                                          fail_silently=False)
                                                print("email sent")

                                        else:
                                            print(mover.company_name, " max atteint pour ajourdhui !")

                                    else:
                                        quote_request_info = Quote_Request.objects.filter(id=request.id).last()
                                        mover_info = Mover.objects.filter(id=mover.id).last()
                                        number_distribution_request = Number_Distribution_Quote_Request.objects.filter \
                                            (quote_request=quote_request_info.id).last()

                                        # the request have to be saved maximum 5 time to 5 differents movers
                                        for i in range(5):

                                            # we prevent the mover to receive the same request twice
                                            if Mover_Quote_Request.objects.filter(quote_request=quote_request_info,
                                                                                  mover=mover_info):
                                                print("you cant receive the same request more than "
                                                      "one time")
                                            else:

                                                savedata1 = Number_Mover_Quote_Request_PerDay(
                                                    number_quote_received_the_same_day=1,
                                                    mover=mover_info)

                                                savedata = Mover_Quote_Request(quote_request=
                                                                               quote_request_info,
                                                                               mover=mover_info)

                                                # we verify if the request hasn't been distributed more than 5 times
                                                if number_distribution_request:

                                                    if number_distribution_request.number_distribution < number_distribution_request. \
                                                            number_max_distribution:

                                                        number_distribution = number_distribution_request.number_distribution + 1
                                                        savedata2 = Number_Distribution_Quote_Request(number_distribution=
                                                                                                      number_distribution,
                                                                                                      quote_request=
                                                                                                      quote_request_info)
                                                        savedata2.save()

                                                    else:
                                                        print(request.ref, ' a atteint le maximum de 5 distributions')

                                                else:
                                                    number_distribution = 1
                                                    savedata2 = Number_Distribution_Quote_Request(number_distribution=
                                                                                                  number_distribution,
                                                                                                  quote_request=
                                                                                                  quote_request_info)
                                                    savedata2.save()

                                                savedata.save()
                                                savedata1.save()

                                                # Sending email to the Mover
                                                subject = 'ItsMoving - Nouvelle demande de devis'
                                                recipient_email = mover_info.user.email
                                                email_from = mover_info.user.email
                                                recipient_list = [recipient_email, ]
                                                message = f'Bonjour {mover_info.company_name}!\nVous venez de recevoir une ' \
                                                          f'nouvelle demande de devis, veuillez accéder à votre compte pour ' \
                                                          f'plus de détails. Merci !'
                                                send_mail(subject, message, email_from, recipient_list,
                                                          fail_silently=False)

                                                # Sending email to the client
                                                subject = 'ItsMoving - Demande de devis reçu'
                                                recipient_email = email
                                                email_from = email
                                                recipient_list = [recipient_email, ]
                                                message = f'Bonjour Mr/Mme {lastname}!\nVotre demande de devis a bien été reçu,' \
                                                          f' vous aurez un retour très bientôt, Merci !'
                                                send_mail(subject, message, email_from, recipient_list,
                                                          fail_silently=False)
                                                print("email sent")

                                else:
                                    print(request.Country_Arrival, ' fait pas partie de la liste de destination de ',
                                          mover.company_name)
                    ####################END INTERNATIONAL REQUEST DISTRIBUTION START###################

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
