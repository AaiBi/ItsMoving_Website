from datetime import date
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
import datetime
from base_app.forms import Mover_Form
from base_app.models import Mover, Country, Mover_Country, Mover_Region, RegionOrProvince, Moving_Type1, Moving_Type2, \
    Mover_Moving_Type2, Quote_Request, Mover_Quote_Request, Quote_Request_Rejected
from user.forms import EditUserForm, EditUserPasswordForm, EditMoverCountryForm, EditMoverRegionForm, \
    EditMoverMovingType2Form, MoverQuoteRequestForm


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


@login_required
def profile(request):
    mover = Mover.objects.filter(user_id=request.user.id).last()
    number_quote_request = Mover_Quote_Request.objects.filter(mover_id=mover.id, treated=False, rejected=False).count()

    return render(request, 'user/profile/profile.html', {'mover': mover, 'number_quote_request': number_quote_request})


@login_required
def reviews(request):
    mover = Mover.objects.filter(user_id=request.user.id).last()
    number_quote_request = Mover_Quote_Request.objects.filter(mover_id=mover.id, treated=False, rejected=False).count()

    return render(request, 'user/profile/reviews.html', {'mover': mover, 'number_quote_request': number_quote_request})


@login_required
def preview(request):
    mover = Mover.objects.filter(user_id=request.user.id).last()
    form1 = EditUserForm(instance=request.user)
    countries = Country.objects.all()
    regions = RegionOrProvince.objects.all()
    mover_countries = Mover_Country.objects.filter(mover=mover)
    mover_regions = Mover_Region.objects.filter(mover=mover)
    number_quote_request = Mover_Quote_Request.objects.filter(mover_id=mover.id, treated=False, rejected=False).count()
    number_quote_request1 = Mover_Quote_Request.objects.filter(mover_id=mover.id).count()

    return render(request, 'user/profile/preview.html', {'mover': mover, 'form1': form1, 'countries':
        countries, 'mover_countries': mover_countries, 'mover_regions': mover_regions, 'regions': regions,
                                                         'number_quote_request': number_quote_request,
                                                         'number_quote_request1': number_quote_request1})


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
    regions = RegionOrProvince.objects.all()
    mover_countries = Mover_Country.objects.filter(mover=mover)
    mover_countries_number = Mover_Country.objects.filter(mover=mover).count()
    mover_regions = Mover_Region.objects.filter(mover=mover)
    mover_moving_types2 = Mover_Moving_Type2.objects.filter(mover=mover)
    mover_moving_types2_number = Mover_Moving_Type2.objects.filter(mover=mover).count()
    # mover_moving_types1_number = Mover_Moving_Type1.objects.filter(mover=mover).count()
    number_quote_request = Mover_Quote_Request.objects.filter(mover_id=mover.id, treated=False, rejected=False).count()
    moving_type1 = Moving_Type1.objects.all()
    moving_type2 = Moving_Type2.objects.all()
    # mover_moving_type1 = Mover_Moving_Type1.objects.filter(mover=mover)

    return render(request, 'user/profile/settings.html', {'mover': mover, 'countries': countries,
                                                          'regions': regions, 'mover_countries': mover_countries,
                                                          'mover_regions': mover_regions, 'mover_countries_number':
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
@login_required
def delete_mover_region(request, mover_region_pk, mover_pk):
    mover = get_object_or_404(Mover, pk=mover_pk)
    mover_region = get_object_or_404(Mover_Region, pk=mover_region_pk)
    number_quote_request = Mover_Quote_Request.objects.filter(mover_id=mover.id, treated=False, rejected=False).count()

    if request.method == 'GET':
        form = EditMoverRegionForm(instance=mover_region)
        return render(request, 'user/mover/settings/delete_mover_region.html',
                      {'mover_region': mover_region, 'form': form, 'mover': mover, 'number_quote_request':
                          number_quote_request})
    if request.method == 'POST':
        mover_region.delete()
        messages.success(request, 'Suppression effectuée !')
        return redirect('settings')


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
