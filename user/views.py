from datetime import date
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404

from base_app.forms import Mover_Form
from base_app.models import Mover, Country, Mover_Country, Mover_Region, RegionOrProvince, Moving_Type1, Moving_Type2, \
    Mover_Moving_Type2
from user.forms import EditUserForm, EditUserPasswordForm, EditMoverCountryForm, EditMoverRegionForm, \
    EditMoverMovingType2Form


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
    return render(request, 'user/profile/profile.html', {'mover': mover})


@login_required
def reviews(request):
    mover = Mover.objects.filter(user_id=request.user.id).last()
    return render(request, 'user/profile/reviews.html', {'mover': mover})


@login_required
def preview(request):
    mover = Mover.objects.filter(user_id=request.user.id).last()
    form1 = EditUserForm(instance=request.user)
    countries = Country.objects.all()
    regions = RegionOrProvince.objects.all()
    mover_countries = Mover_Country.objects.filter(mover=mover)
    mover_regions = Mover_Region.objects.filter(mover=mover)

    return render(request, 'user/profile/preview.html', {'mover': mover, 'form1': form1, 'countries':
                                                         countries, 'mover_countries': mover_countries, 'mover_regions':
                                                         mover_regions, 'regions': regions})


@login_required
def statistic(request):
    mover = Mover.objects.filter(user_id=request.user.id).last()
    return render(request, 'user/profile/statistic.html', {'mover': mover})


@login_required
def quote_request(request):
    mover = Mover.objects.filter(user_id=request.user.id).last()
    return render(request, 'user/profile/quote_request.html', {'mover': mover})


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
    #mover_moving_types1_number = Mover_Moving_Type1.objects.filter(mover=mover).count()
    moving_type1 = Moving_Type1.objects.all()
    moving_type2 = Moving_Type2.objects.all()
    #mover_moving_type1 = Mover_Moving_Type1.objects.filter(mover=mover)

    return render(request, 'user/profile/settings.html', {'mover': mover, 'countries': countries,
                                                          'regions': regions, 'mover_countries': mover_countries,
                                                          'mover_regions': mover_regions, 'mover_countries_number':
                                                          mover_countries_number,'mover_moving_types2': mover_moving_types2,
                                                          'moving_type1': moving_type1, 'mover_moving_types2_number':
                                                          mover_moving_types2_number, 'moving_type2': moving_type2})


@login_required
def edit_profile(request):
    mover = Mover.objects.filter(user_id=request.user.id).last()
    form1 = EditUserForm(instance=request.user)
    password_edit_form = EditUserPasswordForm(request.user)
    mover_form = Mover_Form(instance=mover)
    countries = Country.objects.all()
    moving_type1 = Moving_Type1.objects.all()

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
                    ,'error': 'Mauvaises données !'})
        else:
            form1 = EditUserForm(instance=request.user)

    if 'edit_company_logo' in request.POST:
        if request.method == 'POST':
            try:
                mover_form = Mover_Form(request.POST, request.FILES, instance=mover)
                print(request.POST.get('ref'))
                print(request.POST.get('company_name'))
                print(request.POST.get('company_phone_number'))
                print(request.POST.get('Adresse'))
                print(request.POST.get('employee_number'))
                print(request.POST.get('number_max_quote_request'))
                print(request.POST.get('website'))
                print(request.POST.get('TVA_number'))
                print(request.POST.get('Postal_Code'))
                print(request.POST.get('City'))
                print(request.POST.get('company_statut'))
                print(request.POST.get('company_description'))
                print(request.POST.get('facebook_link'))
                print(request.POST.get('instagram_link'))
                print(request.POST.get('twitter_link'))
                print(request.POST.get('linkedin_link'))
                print(request.POST.get('logo'))
                print(request.POST.get('validated'))
                print(request.POST.get('activated'))
                print(request.POST.get('country'))
                if mover_form.is_valid():
                    mover_form.country = get_object_or_404(Country, id=request.POST.get('country'))
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
                                                              moving_type1})


@login_required
def billing(request):
    mover = Mover.objects.filter(user_id=request.user.id).last()
    return render(request, 'user/profile/billing.html', {'mover': mover})


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
    #mover_movingtype1_number = Mover_Moving_Type1.objects.filter(mover=mover).count()

    if request.method == 'GET':
        return render(request, 'user/mover/settings/area_intervention.html',
                      {'mover': mover, 'countries': countries, 'mover_countries': mover_countries,
                       'mover_countries_number': mover_countries_number})

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
    mover = get_object_or_404(Mover, pk=mover_pk)
    mover_country = get_object_or_404(Mover_Country, pk=mover_country_pk)

    if request.method == 'GET':
        form = EditMoverCountryForm(instance=mover_country)
        return render(request, 'user/mover/settings/delete_mover_country.html',
                      {'mover_country': mover_country, 'form': form, 'mover': mover})
    if request.method == 'POST':
        mover_country.delete()
        messages.success(request, 'Suppression effectuée !')
        return redirect('area_intervention')


@login_required
def moving_type(request):
    mover = Mover.objects.filter(user_id=request.user.id).last()
    # mover_moving_types1 = Mover_Moving_Type1.objects.filter(mover=mover)
    # mover_moving_types1_number = Mover_Moving_Type1.objects.filter(mover=mover).count()
    moving_type1 = Moving_Type1.objects.all()
    if request.method == 'GET':
        return render(request, 'user/mover/settings/moving_type.html',
                      {'mover': mover, 'moving_type1': moving_type1})

    if 'add_moving_type1' in request.POST:
        if request.method == 'POST':
            moving_type1_name = request.POST.getlist('moving_type1_name[]')
            if request.POST.getlist('moving_type1_name[]'):
                for data in moving_type1_name:
                    # if Mover_Moving_Type1.objects.filter(moving_type1_name=data, mover=mover):
                    #     messages.error(request, 'Erreur ! Cette sélection existe déjà dans notre base de données !')
                    #     return redirect('moving_type')
                    # else:
                    #     savedata = Mover_Moving_Type1(moving_type1_name=data, mover=mover)
                    #     savedata.save()
                    #     messages.success(request, 'Nouveau type de déménagement ajouté avec succès !')
                    continue
                return redirect('moving_type')
            else:
                messages.error(request, 'Veuillez faire au moins une sélection !')
                return redirect('moving_type')


@login_required
def delete_mover_moving_type1(request, moving_type_pk, mover_pk):
    mover = get_object_or_404(Mover, pk=mover_pk)
    #mover_moving_tytpe = get_object_or_404(Mover_Moving_Type1, pk=moving_type_pk)

    if request.method == 'GET':
        #form = EditMoverMovingType1Form(instance=mover_moving_tytpe)
        return render(request, 'user/mover/settings/delete_mover_moving_type1.html',
                      { 'mover': mover})
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
    if request.method == 'GET':
        return render(request, 'user/mover/settings/customer_type.html',
                      {'mover': mover, 'mover_moving_types2': mover_moving_types2, 'moving_type2': moving_type2,
                       'mover_moving_types2_number': mover_moving_types2_number})

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

    if request.method == 'GET':
        form = EditMoverMovingType2Form(instance=mover_moving_type2)
        return render(request, 'user/mover/settings/delete_mover_moving_type2.html',
                      {'mover_moving_type2': mover_moving_type2, 'form': form, 'mover': mover})
    if request.method == 'POST':
        mover_moving_type2.delete()
        messages.success(request, 'Suppression effectuée !')
        return redirect('customer_type')


@login_required
def modify_country_departure(request, mover_country_pk):
    mover_country = get_object_or_404(Mover_Country, pk=mover_country_pk)
    form = EditMoverCountryForm(instance=mover_country)

    if request.method == 'POST':
        form = EditMoverCountryForm(request.POST, instance=mover_country)
        if form.is_valid():
            form.save()
            messages.success(request, 'Modification effectuée !')
            return redirect('area_intervention')

    return render(request, 'user/mover/settings/modify_country_departure.html', {'mover_country': mover_country,
                                                                                 'form': form})


@login_required
def modify_country_arrival(request, mover_country_pk):
    mover_country = get_object_or_404(Mover_Country, pk=mover_country_pk)
    form = EditMoverCountryForm(instance=mover_country)

    if request.method == 'POST':
        form = EditMoverCountryForm(request.POST, instance=mover_country)
        if form.is_valid():
            form.save()
            messages.success(request, 'Modification effectuée !')
            return redirect('area_intervention')

    return render(request, 'user/mover/settings/modify_country_arrival.html', {'mover_country': mover_country,
                                                                                 'form': form})


@login_required
def quote_request_settings(request):
    mover = Mover.objects.filter(user_id=request.user.id).last()
    form = Mover_Form(instance=mover)

    if request.method == 'POST':
        form = Mover_Form(request.POST, instance=mover)
        print(request.POST.get('ref'))
        print(request.POST.get('company_name'))
        print(request.POST.get('company_phone_number'))
        print(request.POST.get('Adresse'))
        print(request.POST.get('employee_number'))
        print(request.POST.get('number_max_quote_request'))
        print(request.POST.get('website'))
        print(request.POST.get('TVA_number'))
        print(request.POST.get('Postal_Code'))
        print(request.POST.get('City'))
        print(request.POST.get('company_statut'))
        print(request.POST.get('company_description'))
        print(request.POST.get('facebook_link'))
        print(request.POST.get('instagram_link'))
        print(request.POST.get('twitter_link'))
        print(request.POST.get('linkedin_link'))
        print(request.POST.get('logo'))
        print(request.POST.get('validated'))
        print(request.POST.get('activated'))
        print(request.POST.get('country'))
        if form.is_valid():
            form = form.save(commit=False)
            form.country = get_object_or_404(Country, id=request.POST.get('country'))
            form.save()
            messages.success(request, 'Modification effectuée !')
            return redirect('quote_request_settings')

    return render(request, 'user/mover/settings/quote_request_settings.html', {'mover': mover, 'form': form})

#################################################  SETTINGS END    #####################################################
@login_required
def delete_mover_region(request, mover_region_pk, mover_pk):
    mover = get_object_or_404(Mover, pk=mover_pk)
    mover_region = get_object_or_404(Mover_Region, pk=mover_region_pk)

    if request.method == 'GET':
        form = EditMoverRegionForm(instance=mover_region)
        return render(request, 'user/mover/settings/delete_mover_region.html',
                      {'mover_region': mover_region, 'form': form, 'mover': mover})
    if request.method == 'POST':
        mover_region.delete()
        messages.success(request, 'Suppression effectuée !')
        return redirect('settings')