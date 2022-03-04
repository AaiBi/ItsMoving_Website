from datetime import date
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
import random

from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Count, Sum
from django.shortcuts import render, redirect, get_object_or_404
import datetime
from base_app.forms import Mover_Form
from base_app.models import Mover, Country, Mover_Country, Moving_Type1, Moving_Type2, \
    Mover_Moving_Type2, Quote_Request, Mover_Quote_Request, Quote_Request_Rejected, Review
from user.forms import EditUserForm, EditUserPasswordForm, EditMoverCountryForm, \
    EditMoverMovingType2Form, MoverQuoteRequestForm, EditUserPasswordForm1
from user.models import Movers_Password_Recovery_Codes


def login_user(request):
    if request.method == 'GET':
        return render(request, 'user/login_user.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'user/login_user.html', {'form': AuthenticationForm(),
                                                            'error': 'Votre nom d\'utilisateur et mot de passe '
                                                                     'ne correspondent pas !'})
        else:
            login(request, user)
            if Mover.objects.filter(user_id=request.user.id).last():
                return redirect('preview')
            else:
                messages.error(request, 'Profil non disponible !')
                logout(request)
                return redirect('login_user')


def password_change(request):
    if request.method == 'POST':
        if request.POST['email']:

            email = request.POST['email']
            if Mover.objects.filter(user__email=email):
                subject = 'Modification de votre mot de passe'
                recipient_email = email
                email_from = request.POST.get('email')
                recipient_list = [recipient_email, ]
                # creation of the code
                characters = list('AbCdEfGhIjKlMnOpQrStUvWxYz')
                characters.extend(list('1234567890'))
                size = 15
                code = ''
                for x in range(size):
                    code += random.choice(characters)
                code = code
                message = f'Bonjour ! \nCode de modification de votre email: \n{code}'

                # Saving the code
                mover = Mover.objects.filter(user__email=email).last()
                saving_data = Movers_Password_Recovery_Codes(code=code, mover_id=mover.id)
                saving_data.save()

                send_mail(subject, message, email_from, recipient_list, fail_silently=False)
                return redirect('password_recovery', email=email)

            else:
                messages.error(request, 'Cette adresse email n\'existe pas dans notre base de données !')

        else:
            messages.error(request, 'Veuillez entrer votre adresse email !')
    return render(request, 'user/password_change.html')


def password_recovery(request, email):
    if get_object_or_404(Mover, user__email=email):
        mover = get_object_or_404(Mover, user__email=email)

        if request.method == 'POST':
            if request.POST.get('code'):
                code = request.POST.get('code')
                if Movers_Password_Recovery_Codes.objects.filter(code=code, mover_id=mover.id):
                    return redirect('password_edit', email=email, code=code)
                else:
                    messages.error(request, 'Code incorrect !')
            else:
                messages.error(request, 'Veuillez entrer le code que vous avez reçu par mail !')
    else:
        messages.error(request, 'Cet email n\'existe pas !')
        return redirect('password_change')
    return render(request, 'user/password_recovery.html', {'mover': mover})


def password_edit(request, email, code):
    if get_object_or_404(Mover, user__email=email) and get_object_or_404(Movers_Password_Recovery_Codes, code=code):
        mover = get_object_or_404(Mover, user__email=email)
        user = User.objects.filter(email=email).last()
        code = get_object_or_404(Movers_Password_Recovery_Codes, code=code)
        form = EditUserPasswordForm1(user=user)

        if user:
            if request.method == 'POST':
                form = EditUserPasswordForm1(user=user, data=request.POST)
                if form.is_valid():
                    user = form.save()
                    update_session_auth_hash(request, user)
                    messages.success(request, f'Votre mot de passe a été modifié avec succès !')
                    return redirect('login_user')
        else:
            messages.error(request, 'Cet utilisateur n\'existe pas !')

    else:
        messages.error(request, 'Cet email n\'existe pas !')
        return redirect('password_change')
    return render(request, 'user/password_edit.html', {'mover': mover, 'code': code, 'form': form})


@login_required
def reviews(request):
    mover = Mover.objects.filter(user_id=request.user.id).last()
    number_quote_request = Mover_Quote_Request.objects.filter(mover_id=mover.id, treated=False, rejected=False).count()
    reviews = Review.objects.filter(mover_quote_request__mover_id=mover.id).order_by('-id')

    return render(request, 'user/profile/reviews.html', {'mover': mover, 'number_quote_request': number_quote_request,
                                                         'reviews': reviews})


@login_required
def preview(request):
    mover = Mover.objects.filter(user_id=request.user.id).last()
    form1 = EditUserForm(instance=request.user)
    countries = Country.objects.all()
    mover_countries = Mover_Country.objects.filter(mover=mover)
    number_quote_request = Mover_Quote_Request.objects.filter(mover_id=mover.id, treated=False, rejected=False).count()
    number_quote_request1 = Mover_Quote_Request.objects.filter(mover_id=mover.id).count()
    reviews = Review.objects.filter(mover_quote_request__mover_id=mover.id)
    total_reviews = Review.objects.filter(mover_quote_request__mover_id=mover.id).count()

    #percentage speed
    speed_reviews_sum = Review.objects.filter(mover_quote_request__mover_id=mover.id).aggregate(TOTAL=Sum('speed'))['TOTAL']
    total_possible = total_reviews * 5
    if speed_reviews_sum and speed_reviews_sum != 0:
        speed_percentage = speed_reviews_sum / total_possible
        speed_percentage = speed_percentage * 100
    else:
        speed_percentage = 0

    #percentage organisation
    organisation_reviews_sum = \
        Review.objects.filter(mover_quote_request__mover_id=mover.id).aggregate(TOTAL=Sum('organisation'))['TOTAL']
    if organisation_reviews_sum and organisation_reviews_sum != 0:
        organisation_percentage = organisation_reviews_sum / total_possible
        organisation_percentage = organisation_percentage * 100
    else:
        organisation_percentage = 0

    #reliability organisation
    reliability_reviews_sum = \
    Review.objects.filter(mover_quote_request__mover_id=mover.id).aggregate(TOTAL=Sum('reliability'))['TOTAL']
    if reliability_reviews_sum and reliability_reviews_sum != 0:
        reliability_percentage = reliability_reviews_sum / total_possible
        reliability_percentage = reliability_percentage * 100
    else:
        reliability_percentage = 0

    #quality organisation
    quality_reviews_sum = \
        Review.objects.filter(mover_quote_request__mover_id=mover.id).aggregate(TOTAL=Sum('quality'))['TOTAL']
    if quality_reviews_sum and quality_reviews_sum != 0:
        quality_percentage = quality_reviews_sum / total_possible
        quality_percentage = quality_percentage * 100
    else:
        quality_percentage = 0

    #general review
    total_sum = speed_percentage + organisation_percentage + reliability_percentage + quality_percentage
    total_sum = (total_sum / 400) * 100

    return render(request, 'user/profile/preview.html', {'mover': mover, 'form1': form1, 'countries':
        countries, 'mover_countries': mover_countries, 'number_quote_request': number_quote_request,
                                                         'number_quote_request1': number_quote_request1, 'reviews':
                                                         reviews, 'speed_reviews_sum': speed_reviews_sum,
                                                         'organisation_percentage': organisation_percentage,
                                                         'reliability_percentage': reliability_percentage,
                                                         'quality_percentage': quality_percentage,
                                                         'speed_percentage': speed_percentage, 'total_reviews':
                                                         total_reviews, 'total_sum': total_sum})


@login_required
def statistic(request):
    mover = Mover.objects.filter(user_id=request.user.id).last()
    current_date = datetime.date.today()
    number_quote_request = Mover_Quote_Request.objects.filter(mover_id=mover.id, treated=False, rejected=False).count()
    number_quote_request_received_this_month = Mover_Quote_Request.objects.filter(mover_id=mover.id, created__month=
    current_date.month).count()
    number_quote_request_treated_this_month = Mover_Quote_Request.objects.filter(mover_id=mover.id, created__month=
    current_date.month, treated=True).count()
    number_quote_request_rejected_this_month = Mover_Quote_Request.objects.filter(mover_id=mover.id, created__month=
    current_date.month, rejected=True).count()
    number_quote_request_treated = Mover_Quote_Request.objects.filter(mover_id=mover.id, treated=True).count()
    number_quote_request_rejected = Mover_Quote_Request.objects.filter(mover_id=mover.id, rejected=True).count()
    if number_quote_request_treated or number_quote_request_rejected:
        treated = number_quote_request_treated / (number_quote_request_treated + number_quote_request_rejected)
        treated = treated * 100
        rejected = number_quote_request_rejected / (number_quote_request_treated + number_quote_request_rejected)
        rejected = rejected * 100
    else:
        treated = 0
        rejected = 0

    return render(request, 'user/profile/statistic.html', {'mover': mover, 'number_quote_request': number_quote_request,
                                                           'treated': treated, 'rejected': rejected,
                                                           'number_quote_request_received_this_month':
                                                               number_quote_request_received_this_month,
                                                           'number_quote_request_treated_this_month':
                                                               number_quote_request_treated_this_month,
                                                           'number_quote_request_rejected_this_month':
                                                               number_quote_request_rejected_this_month})


@login_required
def quote_request(request):
    mover = Mover.objects.filter(user_id=request.user.id).last()
    mover_quote_requests = Mover_Quote_Request.objects.filter(mover_id=mover.id, treated=False, rejected=False)
    number_quote_request = Mover_Quote_Request.objects.filter(mover_id=mover.id, treated=False, rejected=False).count()

    if 'search' in request.POST:
        ref = request.POST.get('ref')
        if Quote_Request.objects.filter(ref=ref):
            quote_request = get_object_or_404(Quote_Request, ref=ref)
            mover_quote_request = Mover_Quote_Request.objects.filter(quote_request_id=quote_request.id, mover_id=mover.
                                                                     id).last()
            if mover_quote_request:
                return render(request, 'user/profile/quote_request.html', {'mover': mover, 'mover_quote_request':
                    mover_quote_request, 'number_quote_request': number_quote_request,
                                                                           'quote_request': quote_request})
            else:
                messages.error(request, 'Cette demande de devis ne vous est pas destinée !')
                return render(request, 'user/profile/quote_request.html')

        else:
            messages.error(request, 'Cette référence n\'existe pas !')
            return render(request, 'user/profile/quote_request.html')

    return render(request, 'user/profile/quote_request.html', {'mover': mover, 'mover_quote_requests':
        mover_quote_requests, 'number_quote_request': number_quote_request})


@login_required
def settings(request):
    mover = Mover.objects.filter(user_id=request.user.id).last()
    countries = Country.objects.all()
    mover_countries = Mover_Country.objects.filter(mover=mover)
    mover_countries_number = Mover_Country.objects.filter(mover=mover).count()
    mover_moving_types2 = Mover_Moving_Type2.objects.filter(mover=mover)
    mover_moving_types2_number = Mover_Moving_Type2.objects.filter(mover=mover).count()
    number_quote_request = Mover_Quote_Request.objects.filter(mover_id=mover.id, treated=False, rejected=False).count()
    moving_type1 = Moving_Type1.objects.all()
    moving_type2 = Moving_Type2.objects.all()

    return render(request, 'user/profile/settings.html', {'mover': mover, 'countries': countries,
                                                          'mover_countries': mover_countries, 'mover_countries_number':
                                                              mover_countries_number,
                                                          'mover_moving_types2': mover_moving_types2,
                                                          'moving_type1': moving_type1, 'mover_moving_types2_number':
                                                              mover_moving_types2_number, 'moving_type2': moving_type2,
                                                          'number_quote_request': number_quote_request})


@login_required
def edit_profile(request):
    mover = Mover.objects.filter(user_id=request.user.id).last()
    form1 = EditUserForm(instance=request.user)
    password_edit_form = EditUserPasswordForm(request.user)
    mover_form = Mover_Form(instance=mover)
    countries = Country.objects.all()
    moving_type1 = Moving_Type1.objects.all()
    number_quote_request = Mover_Quote_Request.objects.filter(mover_id=mover.id, treated=False, rejected=False).count()

    if 'edit_user' in request.POST:
        if request.method == 'POST':
            try:
                form1 = EditUserForm(request.POST, instance=request.user)
                if form1.is_valid():
                    form1.save()
                    messages.success(request, 'Modification effectué avec succès !')
                    return redirect('edit_profile')
            except ValueError:
                return render(request, 'user/profile/edit_profile.html', {'mover': mover, 'form1': form1,
                                                                          'error': 'Mauvaises données !'})
        else:
            form1 = EditUserForm(instance=request.user)

    if 'username_edit' in request.POST:
        if request.method == 'POST':
            try:
                form1 = EditUserForm(request.POST, instance=request.user)
                if form1.is_valid():
                    form1.save()
                    messages.success(request, 'Modification effectué avec succès !')
                    return redirect('edit_profile')
            except ValueError:
                return render(request, 'user/profile/edit_profile.html', {'mover': mover, 'form1': form1
                    , 'error': 'Mauvaises données !'})
        else:
            form1 = EditUserForm(instance=request.user)

    if 'edit_company_logo' in request.POST:
        if request.method == 'POST':
            try:
                mover_form = Mover_Form(request.POST, request.FILES, instance=mover)

                if mover_form.is_valid():
                    mover_form.country = get_object_or_404(Country, id=request.POST.get('country'))
                    mover_form.moving_type1 = get_object_or_404(Moving_Type1, id=request.POST.get('moving_type1'))
                    mover_form.save()
                    messages.success(request, 'Votre logo a été modifié avec succès !')
                    return redirect('edit_profile')
            except ValueError:
                return render(request, 'user/profile/edit_profile.html', {'mover': mover, 'mover_form': mover_form,
                                                                          'error': 'Mauvaises données !'})
        else:
            mover_form = Mover_Form(instance=mover)

    if 'edit_mover_info' in request.POST:
        if request.method == 'POST':
            try:
                mover_form = Mover_Form(request.POST, instance=mover)
                if mover_form.is_valid():
                    mover_form.country = get_object_or_404(Country, id=request.POST.get('country'))
                    mover_form.moving_type1 = get_object_or_404(Moving_Type1, id=request.POST.get('moving_type1'))
                    mover_form.save()
                    messages.success(request, 'Modification effectué avec succès !')
                    return redirect('edit_profile')
            except ValueError:
                return render(request, 'user/profile/edit_profile.html', {'mover': mover, 'mover_form': mover_form,
                                                                          'countries': countries, 'moving_type1':
                                                                              moving_type1,
                                                                          'error': 'Mauvaises données !'})
        else:
            mover_form = Mover_Form(instance=mover)

    if 'social_media_link_form' in request.POST:
        if request.method == 'POST':
            # print(request.POST.get('ref'))
            # print(request.POST.get('company_name'))
            # print(request.POST.get('company_phone_number'))
            # print(request.POST.get('Adresse'))
            # print(request.POST.get('employee_number'))
            # print(request.POST.get('number_max_quote_request'))
            # print(request.POST.get('website'))
            # print(request.POST.get('TVA_number'))
            # print(request.POST.get('Postal_Code'))
            # print(request.POST.get('City'))
            # print(request.POST.get('company_statut'))
            # print(request.POST.get('company_description'))
            # print(request.POST.get('logo'))
            # print(request.POST.get('validated'))
            # print(request.POST.get('activated'))
            # print(request.POST.get('country'))
            try:
                mover_form = Mover_Form(request.POST, instance=mover)
                if mover_form.is_valid():
                    mover_form.save()
                    messages.success(request, 'Modification effectué avec succès !')
                    return redirect('edit_profile')
            except ValueError:
                return render(request, 'user/profile/edit_profile.html', {'mover': mover, 'mover_form': mover_form,
                                                                          'error': 'Mauvaises données !'})
        else:
            mover_form = Mover_Form(instance=mover)

    if 'password_edit' in request.POST:
        if request.method == 'POST':
            password_edit_form = EditUserPasswordForm(request.user, request.POST)
            if password_edit_form.is_valid():
                print("bien")
                user = password_edit_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, f'Votre mot de passe a été modifié avec succès !')
                return redirect('edit_profile')
        else:
            password_edit_form = EditUserPasswordForm(request.user)

    return render(request, 'user/profile/edit_profile.html', {'mover': mover, 'form1': form1
        , 'password_edit_form': password_edit_form, 'mover_form':
                                                                  mover_form, 'countries': countries, 'moving_type1':
                                                                  moving_type1, 'number_quote_request':
                                                                  number_quote_request})


@login_required
def billing(request):
    mover = Mover.objects.filter(user_id=request.user.id).last()
    number_quote_request = Mover_Quote_Request.objects.filter(mover_id=mover.id, treated=False, rejected=False).count()

    return render(request, 'user/profile/billing.html', {'mover': mover, 'number_quote_request': number_quote_request})


@login_required
def logout_user(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login_user')


@login_required
def user_password_change(request):
    if request.method == 'POST':
        form = EditUserPasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, f'Votre mot de passe a été modifié avec succès !')
            return redirect('preview')
    else:
        form = EditUserPasswordForm(request.user)
    return render(request, 'user/profile/user_password_change.html', {'form': form})


#################################################  SETTINGS START  #####################################################

@login_required
def area_intervention(request):
    mover = Mover.objects.filter(user_id=request.user.id).last()
    countries = Country.objects.all()
    mover_countries = Mover_Country.objects.filter(mover=mover)
    mover_countries_number = Mover_Country.objects.filter(mover=mover).count()
    number_quote_request = Mover_Quote_Request.objects.filter(mover_id=mover.id, treated=False, rejected=False).count()
    # mover_movingtype1_number = Mover_Moving_Type1.objects.filter(mover=mover).count()

    if request.method == 'GET':
        return render(request, 'user/mover/settings/area_intervention.html',
                      {'mover': mover, 'countries': countries, 'mover_countries': mover_countries,
                       'mover_countries_number': mover_countries_number, 'number_quote_request': number_quote_request})

    if 'add_country' in request.POST:
        if request.method == 'POST':
            country_name = request.POST.getlist('country_name[]')
            if request.POST.getlist('country_name[]'):
                for data in country_name:
                    if Mover_Country.objects.filter(country_name=data, mover=mover):
                        messages.error(request, 'Erreur ! Cette sélection existe déjà dans notre base de données !')
                        return redirect('area_intervention')
                    else:
                        country = Country.objects.filter(name=data).last()
                        savedata = Mover_Country(country_name=data, country=country, mover=mover)
                        savedata.save()
                        messages.success(request, 'Nouveau pays ajouté avec succès !')
                return redirect('area_intervention')
            else:
                messages.error(request, 'Veuillez faire au moins une sélection !')
                return redirect('area_intervention')


@login_required
def delete_mover_country(request, mover_country_pk, mover_pk):
    number_quote_request = Mover_Quote_Request.objects.filter(mover_id=mover_pk, treated=False, rejected=False).count()
    mover = get_object_or_404(Mover, pk=mover_pk)
    mover_country = get_object_or_404(Mover_Country, pk=mover_country_pk)

    if request.method == 'GET':
        form = EditMoverCountryForm(instance=mover_country)
        return render(request, 'user/mover/settings/delete_mover_country.html',
                      {'mover_country': mover_country, 'form': form, 'mover': mover, 'number_quote_request':
                          number_quote_request})
    if request.method == 'POST':
        mover_country.delete()
        messages.success(request, 'Suppression effectuée !')
        return redirect('area_intervention')


@login_required
def delete_mover_moving_type1(request, moving_type_pk, mover_pk):
    mover = get_object_or_404(Mover, pk=mover_pk)
    number_quote_request = Mover_Quote_Request.objects.filter(mover_id=mover.id, treated=False, rejected=False).count()
    # mover_moving_tytpe = get_object_or_404(Mover_Moving_Type1, pk=moving_type_pk)

    if request.method == 'GET':
        # form = EditMoverMovingType1Form(instance=mover_moving_tytpe)
        return render(request, 'user/mover/settings/delete_mover_moving_type1.html',
                      {'mover': mover, 'number_quote_request': number_quote_request})
    # if request.method == 'POST':
    #     mover_moving_tytpe.delete()
    #     messages.success(request, 'Suppression effectuée !')
    #     return redirect('moving_type')


@login_required
def customer_type(request):
    mover = Mover.objects.filter(user_id=request.user.id).last()
    mover_moving_types2 = Mover_Moving_Type2.objects.filter(mover=mover)
    mover_moving_types2_number = Mover_Moving_Type2.objects.filter(mover=mover).count()
    moving_type2 = Moving_Type2.objects.all()
    number_quote_request = Mover_Quote_Request.objects.filter(mover_id=mover.id, treated=False, rejected=False).count()

    if request.method == 'GET':
        return render(request, 'user/mover/settings/customer_type.html',
                      {'mover': mover, 'mover_moving_types2': mover_moving_types2, 'moving_type2': moving_type2,
                       'mover_moving_types2_number': mover_moving_types2_number, 'number_quote_request':
                           number_quote_request})

    if 'add_moving_type2' in request.POST:
        if request.method == 'POST':
            moving_type2_name = request.POST.getlist('moving_type2_name[]')
            if request.POST.getlist('moving_type2_name[]'):
                for data in moving_type2_name:
                    if Mover_Moving_Type2.objects.filter(moving_type2_name=data, mover=mover):
                        messages.error(request, 'Erreur ! Cette sélection existe déjà dans notre base de données !')
                        return redirect('customer_type')
                    else:
                        savedata = Mover_Moving_Type2(moving_type2_name=data, mover=mover)
                        savedata.save()
                        messages.success(request, 'Nouveau type de déménagement ajouté avec succès !')
                return redirect('customer_type')
            else:
                messages.error(request, 'Veuillez faire au moins une sélection !')
                return redirect('customer_type')


@login_required
def delete_mover_moving_type2(request, moving_type_pk, mover_pk):
    mover = get_object_or_404(Mover, pk=mover_pk)
    mover_moving_type2 = get_object_or_404(Mover_Moving_Type2, pk=moving_type_pk)
    number_quote_request = Mover_Quote_Request.objects.filter(mover_id=mover.id, treated=False, rejected=False).count()

    if request.method == 'GET':
        form = EditMoverMovingType2Form(instance=mover_moving_type2)
        return render(request, 'user/mover/settings/delete_mover_moving_type2.html',
                      {'mover_moving_type2': mover_moving_type2, 'form': form, 'mover': mover, 'number_quote_request':
                          number_quote_request})
    if request.method == 'POST':
        mover_moving_type2.delete()
        messages.success(request, 'Suppression effectuée !')
        return redirect('customer_type')


@login_required
def quote_request_settings(request):
    mover = Mover.objects.filter(user_id=request.user.id).last()
    form = Mover_Form(instance=mover)
    number_quote_request = Mover_Quote_Request.objects.filter(mover_id=mover.id, treated=False, rejected=False).count()

    if request.method == 'POST':
        form = Mover_Form(request.POST, instance=mover)
        if form.is_valid():
            form = form.save(commit=False)
            form.country = get_object_or_404(Country, id=request.POST.get('country'))
            form.moving_type1 = get_object_or_404(Moving_Type1, id=request.POST.get('moving_type1'))
            form.save()
            messages.success(request, 'Modification effectuée !')
            return redirect('quote_request_settings')

    return render(request, 'user/mover/settings/quote_request_settings.html', {'mover': mover, 'form': form,
                                                                               'number_quote_request':
                                                                                   number_quote_request})


#################################################  SETTINGS END    #####################################################


################################################# QUOTE REQUEST    ####################################################

@login_required
def mover_quote_request_detail(request, mover_request_pk):
    if get_object_or_404(Mover_Quote_Request, pk=mover_request_pk):
        mover_quote_request = get_object_or_404(Mover_Quote_Request, pk=mover_request_pk)

        return render(request, 'user/quote_request/mover_quote_request_detail.html', {'mover_quote_request':
                                                                                          mover_quote_request})
    else:
        messages.error(request, 'Cette requête n\'existe pas !')
        return redirect('quote_request')


@login_required
def mover_request_treated(request, mover_request_pk):
    mover_quote_request = get_object_or_404(Mover_Quote_Request, pk=mover_request_pk)
    form = MoverQuoteRequestForm(instance=mover_quote_request)

    if request.method == 'POST':
        form = MoverQuoteRequestForm(request.POST, instance=mover_quote_request)
        if form.is_valid():
            # Sending email
            company_name = mover_quote_request.mover.company_name
            customer_lastname = mover_quote_request.quote_request.lastname

            subject = f'Comment s\'est passé votre déménagement avec {company_name} ?'
            recipient_email = mover_quote_request.quote_request.email
            email_from = mover_quote_request.quote_request.email
            recipient_list = [recipient_email, ]
            mover_quote_request_id = mover_quote_request.id
            message = f'Bonjour Mr/Mme {customer_lastname}!\n Nous avions besoin de votre avis à propos de votre dernier' \
                      f' déménagement.\n' \
                      f'Cliquer sur ce lien pour nous donner votre avis et nous aider à améliorer nos services: \n' \
                      f'http://127.0.0.1:8000/user/reviews/{mover_quote_request_id}'
            send_mail(subject, message, email_from, recipient_list, fail_silently=False)

            form.save()
            messages.success(request, 'Vous aviez valider que cette demande a été traitée avec succès !')
            return redirect('quote_request')

    return render(request, 'user/quote_request/mover_request_treated.html', {'mover_quote_request': mover_quote_request,
                                                                             'form': form})


@login_required
def mover_request_rejected(request, mover_request_pk):
    mover_quote_request = get_object_or_404(Mover_Quote_Request, pk=mover_request_pk)
    form = MoverQuoteRequestForm(instance=mover_quote_request)

    if request.method == 'POST':
        form = MoverQuoteRequestForm(request.POST, instance=mover_quote_request)
        reason = request.POST.get('reason')
        if form.is_valid():
            if reason != "":
                if Quote_Request_Rejected.objects.filter(mover_quote_request_id=mover_request_pk):
                    messages.error(request, 'Erreur ! Vous ne pouvez pas rejeter une demande deux fois !')
                    return redirect('mover_request_rejected', mover_request_pk=mover_request_pk)
                else:
                    savedata = Quote_Request_Rejected(reason=reason, mover_quote_request=mover_quote_request)
                    form.save()
                    savedata.save()
                    messages.success(request, 'Demande rejetée avec succès !')
                    return redirect('quote_request')

            else:
                messages.error(request, 'Veuillez sélectionner une raison !')
                return redirect('mover_request_rejected', mover_request_pk=mover_request_pk)

    return render(request, 'user/quote_request/mover_request_rejected.html', {'mover_quote_request':
                                                                                  mover_quote_request})


@login_required
def treated_quote_request(request):
    mover = Mover.objects.filter(user_id=request.user.id).last()
    mover_quote_requests = Mover_Quote_Request.objects.filter(mover_id=mover.id, treated=True, rejected=False)
    number_quote_request = Mover_Quote_Request.objects.filter(mover_id=mover.id, treated=False, rejected=False).count()

    return render(request, 'user/quote_request/treated_quote_request.html', {'mover': mover,
                                                                             'mover_quote_requests':
                                                                                 mover_quote_requests,
                                                                             'number_quote_request': number_quote_request})


################################################ END  QUOTE REQUEST  ##################################################


################################################## REVIEWS  ####################################################

def review_request(request, mover_request_pk):
    mover_quote_request = get_object_or_404(Mover_Quote_Request, pk=mover_request_pk)

    if request.method == 'POST':
        speed = request.POST.getlist('speed[]')
        reliability = request.POST.getlist('reliability[]')
        organisation = request.POST.getlist('organisation[]')
        quality = request.POST.getlist('quality[]')
        message = request.POST.get('message')
        speed = len(speed)
        reliability = len(reliability)
        organisation = len(organisation)
        quality = len(quality)

        if speed and reliability and organisation and quality and message:
            if Review.objects.filter(mover_quote_request_id=mover_request_pk):
                messages.error(request, 'Vous aviez déjà donner une note à ce déménagement !')
            else:
                savedata = Review(speed=speed, organisation=organisation, reliability=reliability, quality=quality,
                                  message=message, mover_quote_request_id=mover_request_pk)
                savedata.save()
                messages.success(request, 'Nous vous remercions d\'avoir partager votre avis avec nous, Merci !')
                return redirect('review_request')
        else:
            messages.error(request, 'Veuillez renseigner tous les champs !')
            return redirect('review_request')

    return render(request, 'user/mover/reviews/review_request.html', {'mover_quote_request': mover_quote_request})

################################################ END REVIEWS  ##################################################
