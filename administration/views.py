import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.mail import send_mail, EmailMultiAlternatives
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from ItsMoving_Website import settings
from administration.models import Movers_Email_Admin
from base_app.forms import Mover_Form
from base_app.models import Mover, Country, Quote_Request, Moving_Type1, Moving_Type2, Mover_Quote_Request, \
    Quote_Request_Rejected, Mover_Country, Region, Mover_Region, Number_Mover_Quote_Request_PerDay, \
    Number_Distribution_Quote_Request, Movers_Email, Customers_Notification_Email


def admin_login(request):
    if request.method == 'GET':
        return render(request, 'administration/admin_login.html', {'form': AuthenticationForm()})
    else:
        if request.POST['username'] == "ibou932" and request.POST['password']:
            user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
            if user is None:
                return render(request, 'user/login_user.html', {'form': AuthenticationForm(),
                                                                'error': 'Votre nom d\'utilisateur et mot de passe '
                                                                         'ne correspondent pas !'})
            else:
                login(request, user)
                if Mover.objects.filter(user_id=request.user.id).last():
                    logout(request)
                    messages.error(request, 'Vous n\'êtes pas autorisé à accéder à cette page !')
                    return redirect('admin_login')
                else:
                    messages.success(request, 'Bienvenue !')
                    return redirect('movers_home')
        else:
            messages.error(request, 'Vous n\'êtes pas autorisé à accéder à cette page !')
            return redirect('admin_login')


@login_required
def admin_logout(request):
    if request.method == 'POST':
        logout(request)
        return redirect('admin_login')


#####################################################   DEVIS    ######################################################

@login_required
def devis_home(request):
    countries = Country.objects.all()
    quote_requests = Quote_Request.objects.all().order_by('-id')
    mover_quote_requests = Mover_Quote_Request.objects.all()
    moving_type1 = Moving_Type1.objects.all()
    moving_type2 = Moving_Type2.objects.all()
    distributed_requests = Mover_Quote_Request.objects.values('quote_request_id').annotate(Count('id')).order_by()
    quote_requests_rejected = Quote_Request_Rejected.objects.filter(mover_quote_request__rejected=True)
    number_quote_requests_rejected = Quote_Request_Rejected.objects.filter(mover_quote_request__rejected=True).count()

    request_not_distributed = []
    for data in quote_requests:
        if not Mover_Quote_Request.objects.filter(quote_request_id=data.id):
            request_not_distributed.append(data.id)

    len_request_not_distributed = len(request_not_distributed)
    if 'search' in request.POST:
        ref = request.POST.get('ref')
        if Quote_Request.objects.filter(ref=ref):
            quote_request = get_object_or_404(Quote_Request, ref=ref)

            if quote_request:
                return render(request, 'administration/devis/devis_home.html', {'quote_request': quote_request})

        else:
            messages.error(request, 'Cette référence n\'existe pas !')
            return render(request, 'administration/devis/devis_home.html')

    if 'distribution' in request.POST:
        # ####################### Automatic distribution for the requests to the movers ####################
        current_date = datetime.datetime.today()
        mover_available = False
        for request in quote_requests:

            # ####################NATIONAL REQUEST DISTRIBUTION START#####################
            if request.moving_type1.name == 'National':

                movers = Mover.objects.filter(activated=True)
                for mover in movers:

                    # we select the movers who deliver in the departure region of the request
                    movers_departure_regions = Mover_Region.objects.filter(region__name=request.region.name,
                                                                           mover_id=mover.id)

                    # we select the movers who deliver in the arrival region of the request
                    movers_arrival_regions = Mover_Region.objects.filter \
                        (region__name=request.Region_Arrival_for_national_moving, mover_id=mover.id)

                    if movers_departure_regions and movers_arrival_regions:
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
                                        moving_type_name_received = request.moving_type1.name
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
                                        recipient_email = request.email
                                        recipient_last_name = request.lastname
                                        email_from = request.email
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
                                        recipient_email = request.email
                                        recipient_last_name = request.lastname
                                        email_from = request.email
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
                            recipient_email = request.email
                            recipient_last_name = request.lastname
                            email_from = request.email
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
                                            moving_type_name_received = request.moving_type1.name
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
                                            recipient_email = request.email
                                            recipient_last_name = request.lastname
                                            email_from = request.email
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
                                            moving_type_name_received = request.moving_type1.name
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
                                            recipient_email = request.email
                                            recipient_last_name = request.lastname
                                            email_from = request.email
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

        return redirect('devis_home')

    return render(
        request, 'administration/devis/devis_home.html', {'countries': countries, 'quote_requests': quote_requests,
                                                          'moving_type1': moving_type1, 'moving_type2': moving_type2,
                                                          'mover_quote_requests': mover_quote_requests,
                                                          'distributed_requests': distributed_requests,
                                                          'number_quote_requests_rejected':
                                                              number_quote_requests_rejected, 'quote_requests_rejected':
                                                              quote_requests_rejected, 'request_not_distributed':
                                                              request_not_distributed, 'len_request_not_distributed':
                                                              len_request_not_distributed
                                                          }
    )


@login_required
def devis_detail(request, quote_request_pk):
    devis = get_object_or_404(Quote_Request, pk=quote_request_pk)
    countries = Country.objects.all()
    moving_type1 = Moving_Type1.objects.all()
    moving_type2 = Moving_Type2.objects.all()
    movers = Mover.objects.all()
    users = User.objects.all()
    mover_quote_requests = Mover_Quote_Request.objects.filter(quote_request_id=quote_request_pk)
    mover_quote_requests_number = Mover_Quote_Request.objects.filter(quote_request_id=quote_request_pk).count()
    number_quote_requests_rejected = Quote_Request_Rejected.objects.filter(mover_quote_request__rejected=True,
                                                                           mover_quote_request__quote_request__id=
                                                                           quote_request_pk).count()
    quote_requests_rejected = Quote_Request_Rejected.objects.filter(mover_quote_request__rejected=True,
                                                                    mover_quote_request__quote_request__id=
                                                                    quote_request_pk)
    regions = Region.objects.all()

    if request.method == 'GET':
        return render(request, 'administration/devis/devis_detail.html', {'devis': devis, 'countries': countries,
                                                                          'moving_type1': moving_type1, 'moving_type2'
                                                                          : moving_type2, 'movers': movers, 'users':
                                                                              users, 'mover_quote_requests_number':
                                                                              mover_quote_requests_number,
                                                                          'mover_quote_requests': mover_quote_requests
            , 'number_quote_requests_rejected':
                                                                              number_quote_requests_rejected,
                                                                          'quote_requests_rejected':
                                                                              quote_requests_rejected, 'regions':
                                                                              regions})


@login_required
def delete_devis(request, quote_request_pk):
    quote_request = get_object_or_404(Quote_Request, pk=quote_request_pk)

    if request.method == 'GET':
        return render(request, 'administration/devis/delete_devis.html',
                      {'quote_request': quote_request})
    if request.method == 'POST':
        quote_request.delete()
        messages.success(request, 'Suppression effectuée !')
        return redirect('devis_home')


###################################################  END DEVIS    #####################################################


####################################################   Movers    ######################################################

@login_required
def movers_home(request):
    countries = Country.objects.all()
    moving_type1 = Moving_Type1.objects.all()
    moving_type2 = Moving_Type2.objects.all()
    movers_activated = Mover.objects.filter(activated=True)
    movers_unactivated = Mover.objects.filter(activated=False)
    movers_unactivated_count = Mover.objects.filter(activated=False).count()
    users = User.objects.all()
    form = Mover_Form()

    if request.method == 'POST':

        if 'search' in request.POST:
            ref = request.POST.get('ref')
            if Mover.objects.filter(ref=ref):
                mover = get_object_or_404(Mover, ref=ref)
                return render(request, 'administration/movers/movers_home.html',
                              {'countries': countries, 'moving_type1': moving_type1, 'moving_type2': moving_type2,
                               'users': users, 'movers_unactivated': movers_unactivated, 'movers_unactivated_count':
                                   movers_unactivated_count, 'movers_activated': movers_activated, 'mover': mover})
            elif Mover.objects.filter(company_name=ref):
                mover = get_object_or_404(Mover, company_name=ref)
                return render(request, 'administration/movers/movers_home.html',
                              {'countries': countries, 'moving_type1': moving_type1, 'moving_type2': moving_type2,
                               'users': users, 'movers_unactivated': movers_unactivated, 'movers_unactivated_count':
                                   movers_unactivated_count, 'movers_activated': movers_activated, 'mover': mover})
            else:
                messages.error(request, 'Ce nom n\'existe pas !')
                return render(request, 'administration/movers/movers_home.html')

        if request.POST.get('mover_id'):
            mover_info = get_object_or_404(Mover, pk=request.POST.get('mover_id'))
            form = Mover_Form(request.POST, instance=mover_info)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profil activé !')
                return redirect('movers_home')

    return render(request, 'administration/movers/movers_home.html', {'countries': countries,
                                                                      'moving_type1': moving_type1, 'moving_type2'
                                                                      : moving_type2, 'users':
                                                                          users, 'movers_unactivated':
                                                                          movers_unactivated, 'movers_unactivated_count'
                                                                      : movers_unactivated_count, 'form': form,
                                                                      'movers_activated': movers_activated})


@login_required
def mover_detail(request, mover_pk):
    mover = get_object_or_404(Mover, pk=mover_pk)
    countries = Country.objects.all()
    moving_type1 = Moving_Type1.objects.all()
    moving_type2 = Moving_Type2.objects.all()
    movers = Mover.objects.all()
    users = User.objects.all()
    movers_country = Mover_Country.objects.filter(mover_id=mover_pk)
    number_mover_quote_requests = Mover_Quote_Request.objects.filter(mover_id=mover_pk).count()

    return render(request, 'administration/movers/mover_detail.html', {'mover': mover, 'countries': countries,
                                                                       'moving_type1': moving_type1, 'moving_type2'
                                                                       : moving_type2, 'movers': movers, 'users':
                                                                           users, 'number_mover_quote_requests':
                                                                           number_mover_quote_requests,
                                                                       'movers_country':
                                                                           movers_country})


@login_required
def mover_active_unactive(request, mover_pk):
    mover = get_object_or_404(Mover, pk=mover_pk)
    countries = Country.objects.all()
    moving_type1 = Moving_Type1.objects.all()
    moving_type2 = Moving_Type2.objects.all()
    movers = Mover.objects.all()
    users = User.objects.all()
    form = Mover_Form(request.POST)

    if request.method == 'POST':
        mover_info = get_object_or_404(Mover, pk=mover_pk)
        form = Mover_Form(request.POST, instance=mover_info)
        form.country = Country.objects.filter(id=request.POST.get('country_id'))
        moving_type1 = Moving_Type1.objects.filter(id=request.POST.get('moving_type1_id'))

        if request.POST.get('activated') == 'True':
            if form.is_valid():
                form.save()
                messages.success(request, 'Profil activé !')
                return redirect('movers_home')

        if request.POST.get('activated') == 'False':
            if form.is_valid():
                form.save()
                messages.success(request, 'Profil désactivé !')
                return redirect('movers_home')

    return render(request, 'administration/movers/mover_active_unactive.html', {'mover': mover, 'countries': countries,
                                                                                'moving_type1': moving_type1,
                                                                                'moving_type2'
                                                                                : moving_type2, 'movers': movers,
                                                                                'users':
                                                                                    users, 'form': form})


@login_required
def mover_devis(request, mover_pk):
    mover = get_object_or_404(Mover, pk=mover_pk)
    mover_quote_requests = Mover_Quote_Request.objects.filter(mover_id=mover_pk)
    number_mover_quote_requests = Mover_Quote_Request.objects.filter(mover_id=mover_pk).count()

    if 'search' in request.POST:
        ref = request.POST.get('ref')
        if Quote_Request.objects.filter(ref=ref):
            quote_request = get_object_or_404(Quote_Request, ref=ref)
            mover_quote_request = Mover_Quote_Request.objects.filter(quote_request_id=quote_request.id, mover_id=mover.
                                                                     id).last()
            if mover_quote_request:
                return render(request, 'administration/movers/mover_devis.html', {'mover': mover, 'mover_quote_request':
                    mover_quote_request, 'number_mover_quote_requests': number_mover_quote_requests})
            else:
                messages.error(request, 'Cette demande de devis ne vous est pas destinée !')
                return render(request, 'administration/movers/mover_devis.html')

        else:
            messages.error(request, 'Cette référence n\'existe pas !')
            return render(request, 'administration/movers/mover_devis.html')

    return render(request, 'administration/movers/mover_devis.html', {'mover': mover, 'mover_quote_requests':
        mover_quote_requests,
                                                                      'number_mover_quote_requests':
                                                                          number_mover_quote_requests})


##################################################   END Movers    ####################################################


################################################### FACTURATION  ######################################################
################################################### FACTURATION  ######################################################

@login_required
def facturation_home(request):
    movers = Mover.objects.all()
    users = User.objects.all()
    mover_quote_requests_not_paid = Mover_Quote_Request.objects.filter(rejected=False, paid="Non payé").values('mover') \
        .order_by('mover').annotate(count=Count('mover'))
    mover_quote_requests_paid = Mover_Quote_Request.objects.filter(rejected=False, paid="Payé").values('mover') \
        .order_by('mover').annotate(count=Count('mover'))
    number_quote_request_unpaid = Mover_Quote_Request.objects.filter(rejected=False, paid="Non payé").count()

    if request.method == 'POST':
        number_payment = int(request.POST.get('number_payment'))
        mover_id = request.POST.get('mover_id')
        mover = Mover.objects.filter(id=mover_id).last()
        mover_quote_requests = Mover_Quote_Request.objects.filter(mover_id=mover_id, paid='Non payé', rejected=False) \
            [:number_payment]

        # modifing the mover quote request table to paid='Paye' as paid
        # we validated the number of quote request paid as paid
        for mover_quote_request in mover_quote_requests:
            save_data1 = Mover_Quote_Request(id=mover_quote_request.id, created=mover_quote_request.created,
                                             quote_request_id=mover_quote_request.quote_request.id,
                                             treated=mover_quote_request.treated, rejected=
                                             mover_quote_request.rejected, paid="Payé", mover_id=mover_id)
            save_data1.save()
            messages.success(request, f'Paiement pour {number_payment} demande de devis ont été validés par succès pour'
                                      f'{mover.company_name} !')

    return render(request, 'administration/facturation/facturation_home.html', {'number_quote_request_unpaid':
                                                                                    number_quote_request_unpaid,
                                                                                'movers': movers, 'users': users,
                                                                                'mover_quote_requests_not_paid':
                                                                                    mover_quote_requests_not_paid,
                                                                                'mover_quote_requests_paid':
                                                                                    mover_quote_requests_paid})


@login_required
def list_payments_not_done(request, mover_pk):
    mover = get_object_or_404(Mover, pk=mover_pk)
    mover_quote_request_unpaids = Mover_Quote_Request.objects.filter(mover=mover, rejected=False,
                                                                     paid="Non payé").order_by('-id')
    return render(request, 'administration/facturation/list_payments_not_done.html', {'mover': mover,
                                                                                      'mover_quote_request_unpaids':
                                                                                          mover_quote_request_unpaids})


@login_required
def list_payments_done(request, mover_pk):
    mover = get_object_or_404(Mover, pk=mover_pk)
    mover_quote_request_paids = Mover_Quote_Request.objects.filter(mover=mover, rejected=False, paid="Payé").order_by(
        '-id')
    return render(request, 'administration/facturation/list_payments_done.html', {'mover': mover,
                                                                                  'mover_quote_request_paids':
                                                                                      mover_quote_request_paids})


@login_required
def group_email_for_paiement(request):
    today = datetime.date.today()
    last_month = today.month - 1
    movers = Mover.objects.all()
    users = User.objects.all()
    mover_quote_requests = Mover_Quote_Request.objects.filter(rejected=False, paid="Non payé", created__month=
    today.month)

    if request.method == 'POST':
        for mover_quote_request in mover_quote_requests:

            # we check if the mover didnt receive the same email the same day
            if not Movers_Email_Admin.objects.filter(mover_id=mover_quote_request.mover.id, created__date=today):
                # sending the emails to the movers
                number_quote_request_unpaid = Mover_Quote_Request.objects.filter(rejected=False, paid="Non payé",
                                                                                 mover_id=mover_quote_request.mover.id,
                                                                                 created__month=today.month).count()

                subject = 'Rappel pour demandes de devis reçu non payé!'
                recipient_email = mover_quote_request.mover.user.email
                email_from = mover_quote_request.mover.user.email
                recipient_list = [recipient_email, ]
                message = f'Bonjour Mr/Mme {mover_quote_request.mover.user.last_name}!\n ' \
                          f'Vous avez actuellement {number_quote_request_unpaid} demande(s) de devis non payé, ' \
                          f'veuillez accédez à votre compte utilisateur dans l\'onglet \'Facture\' pour plus de ' \
                          f'détails et éventuellement faire le paiement.\n' \
                          f'Après la date limite (le 20 de ce mois), votre compte risque d\'être suspendu!' \
                          f'\nMerci !\n' \
                          f'Lien de connexion : http://127.0.0.1:8000/user/login/'
                send_mail(subject, message, email_from, recipient_list, fail_silently=False)

                save_rappel_email = Movers_Email_Admin(quote_request_id=mover_quote_request.quote_request.id,
                                                       mover_id=mover_quote_request.mover.id)
                save_rappel_email.save()

    return render(request, 'administration/facturation/group_email_for_paiement.html', {'movers': movers})

################################################# END FACTURATION  ####################################################
################################################# END FACTURATION  ####################################################
