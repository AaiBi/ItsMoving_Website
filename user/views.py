from datetime import date
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404

from base_app.forms import Mover_Form
from base_app.models import Mover, Country, Mover_Country, Mover_Region, RegionOrProvince, Moving_Type1, Moving_Type2, \
    Mover_Moving_Type1, Mover_Moving_Type2
from user.forms import EditUserForm, User_Info_Form, EditUserPasswordForm, EditMoverCountryForm, EditMoverRegionForm, \
    EditMoverMovingType1Form, EditMoverMovingType2Form
from user.models import User_Info


def login_user(request):
    if request.method == 'GET':
        return render(request, 'user/login_user.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'user/login_user.html', {'form': AuthenticationForm(), 'error': 'Votre nom d\'utilisateur et mot de passe ne correspondent pas !'})
        else:
            login(request, user)
            return redirect('preview')


def sign_up_user(request):
    if request.method == 'GET':
        return render(request, 'user/sign_up_user.html', {'form': UserCreationForm()})
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
                    user = User.objects.create_user(request.POST['username'], password=request.POST['password1'],
                                                    first_name=request.POST['first_name'], last_name=request.POST['last_name'],
                                                    email=request.POST['email'])
                    # creating the blanck user_info table
                    indicatif = 0
                    phone_number = 0
                    Adresse = "null"
                    country = "null"
                    activated = True
                    profil_picture = "/user/images/profil_image/random_image.png"
                    user_info = User_Info(indicatif=indicatif, phone_number=phone_number, Adresse=Adresse, country=country,
                                          activated=activated, profil_picture=profil_picture, user_id=user.id)
                    user_info.save()

                    user.save()
                    messages.success(request, f'Bienvenue Mr/Mme {user.last_name}, votre compte a été créer avec succès !')
                    return redirect('login_user')
                except ValueError:
                    return render(request, 'user/sign_up_user.html', {'form': UserCreationForm(), 'error': 'Bad data passed in'})
        else:
            return render(request, 'user/sign_up_user.html', {'form': UserCreationForm(), 'error': 'Les deux mots de passe ne correspondent pas !'})


@login_required
def profile(request):
    mover = Mover.objects.filter(user_id=request.user.id).last()
    user_info = get_object_or_404(User_Info, user=request.user)
    return render(request, 'user/profile/profile.html', {'mover': mover, 'user_info': user_info})


@login_required
def reviews(request):
    mover = Mover.objects.filter(user_id=request.user.id).last()
    user_info = get_object_or_404(User_Info, user=request.user)
    return render(request, 'user/profile/reviews.html', {'mover': mover, 'user_info': user_info})


@login_required
def preview(request):
    mover = Mover.objects.filter(user_id=request.user.id).last()
    user_info = get_object_or_404(User_Info, user=request.user)
    form1 = EditUserForm(instance=request.user)
    countries = Country.objects.all()
    regions = RegionOrProvince.objects.all()
    mover_countries = Mover_Country.objects.filter(mover=mover)
    mover_regions = Mover_Region.objects.filter(mover=mover)

    return render(request, 'user/profile/preview.html', {'mover': mover, 'form1': form1, 'user_info': user_info, 'countries':
                                                         countries, 'mover_countries': mover_countries, 'mover_regions':
                                                         mover_regions, 'regions': regions })


@login_required
def statistic(request):
    mover = Mover.objects.filter(user_id=request.user.id).last()
    user_info = get_object_or_404(User_Info, user=request.user)
    return render(request, 'user/profile/statistic.html', {'mover': mover, 'user_info': user_info})


@login_required
def quote_request(request):
    mover = Mover.objects.filter(user_id=request.user.id).last()
    user_info = get_object_or_404(User_Info, user=request.user)
    return render(request, 'user/profile/quote_request.html', {'mover': mover, 'user_info': user_info})


@login_required
def settings(request):
    mover = Mover.objects.filter(user_id=request.user.id).last()
    user_info = get_object_or_404(User_Info, user=request.user)
    countries = Country.objects.all()
    regions = RegionOrProvince.objects.all()
    mover_countries = Mover_Country.objects.filter(mover=mover)
    mover_countries_number = Mover_Country.objects.filter(mover=mover).count()
    mover_regions = Mover_Region.objects.filter(mover=mover)
    mover_moving_types2 = Mover_Moving_Type2.objects.filter(mover=mover)
    mover_moving_types2_number = Mover_Moving_Type2.objects.filter(mover=mover).count()
    mover_moving_types1 = Mover_Moving_Type1.objects.filter(mover=mover)
    mover_moving_types1_number = Mover_Moving_Type1.objects.filter(mover=mover).count()
    moving_type1 = Moving_Type1.objects.all()
    moving_type2 = Moving_Type2.objects.all()

    if 'add_country' in request.POST:
        if request.method == 'POST':
            country_name = request.POST.getlist('country_name[]')
            if request.POST.getlist('country_name[]'):
                for data in country_name:
                    if Mover_Country.objects.filter(country_name=data, mover=mover):
                        messages.error(request, 'Erreur ! Cette sélection existe déjà dans notre base de données !')
                        return redirect('settings')
                    else:
                        country = Country.objects.filter(name=data).last()
                        savedata = Mover_Country(country_name=data, country=country, mover=mover)
                        savedata.save()
                        messages.success(request, 'Nouveau pays ajouté avec succès !')
                return redirect('settings')
            else:
                messages.error(request, 'Veuillez faire au moins une sélection !')
                return redirect('settings')

    if 'add_region' in request.POST:
        if request.method == 'POST':
            region_name = request.POST.get('region_name')
            if request.POST.get('region_name'):
                if Mover_Region.objects.filter(region_name=region_name, mover=mover):
                    messages.error(request, 'Erreur ! Cette sélection existe déjà dans notre base de données !')
                    return redirect('settings')
                else:
                    region = RegionOrProvince.objects.filter(name=region_name).last()
                    for country in countries:
                        if region.country_id == country.id:
                            country = Country.objects.filter(id=country.id).last()
                            mover = get_object_or_404(Mover, id=mover.id)
                            savedata = Mover_Region(region_name=region_name, region=region, country=country, mover=mover)
                            savedata.save()
                    messages.success(request, 'Nouvelle region ajoutée avec succès !')
                return redirect('settings')
            else:
                messages.error(request, 'Veuillez faire au moins une sélection !')
                return redirect('settings')

    if 'add_moving_type1' in request.POST:
        if request.method == 'POST':
            moving_type1_name = request.POST.getlist('moving_type1_name[]')
            if request.POST.getlist('moving_type1_name[]'):
                for data in moving_type1_name:
                    if Mover_Moving_Type1.objects.filter(moving_type1_name=data, mover=mover):
                        messages.error(request, 'Erreur ! Cette sélection existe déjà dans notre base de données !')
                        return redirect('settings')
                    else:
                        savedata = Mover_Moving_Type1(moving_type1_name=data, mover=mover)
                        savedata.save()
                        messages.success(request, 'Nouveau type de déménagement ajouté avec succès !')
                return redirect('settings')
            else:
                messages.error(request, 'Veuillez faire au moins une sélection !')
                return redirect('settings')

    if 'add_moving_type2' in request.POST:
        if request.method == 'POST':
            moving_type2_name = request.POST.getlist('moving_type2_name[]')
            if request.POST.getlist('moving_type2_name[]'):
                for data in moving_type2_name:
                    if Mover_Moving_Type2.objects.filter(moving_type2_name=data, mover=mover):
                        messages.error(request, 'Erreur ! Cette sélection existe déjà dans notre base de données !')
                        return redirect('settings')
                    else:
                        savedata = Mover_Moving_Type2(moving_type2_name=data, mover=mover)
                        savedata.save()
                        messages.success(request, 'Nouveau type de déménagement ajouté avec succès !')
                return redirect('settings')
            else:
                messages.error(request, 'Veuillez faire au moins une sélection !')
                return redirect('settings')

    return render(request, 'user/profile/settings.html', {'mover': mover, 'user_info': user_info, 'countries': countries,
                                                          'regions': regions, 'mover_countries': mover_countries,
                                                          'mover_regions': mover_regions, 'mover_countries_number':
                                                          mover_countries_number, 'mover_moving_types1':
                                                          mover_moving_types1, 'mover_moving_types2': mover_moving_types2,
                                                          'moving_type1': moving_type1, 'mover_moving_types1_number':
                                                          mover_moving_types1_number, 'mover_moving_types2_number':
                                                          mover_moving_types2_number, 'moving_type2': moving_type2})


@login_required
def edit_profile(request):
    mover = Mover.objects.filter(user_id=request.user.id).last()
    user_info = get_object_or_404(User_Info, user=request.user)
    form1 = EditUserForm(instance=request.user)
    form2 = User_Info_Form(instance=user_info)
    password_edit_form = EditUserPasswordForm(request.user)
    mover_form = Mover_Form(instance=mover)

    if 'edit_user' in request.POST:
        if request.method == 'POST':
            try:
                form1 = EditUserForm(request.POST, instance=request.user)
                if form1.is_valid():
                    form1.save()
                    messages.success(request, 'Modification effectué avec succès !')
                    return redirect('edit_profile')
            except ValueError:
                return render(request, 'user/profile/edit_profile.html', {'mover': mover, 'form1': form1, 'user_info':
                    user_info,'error': 'Mauvaises données !'})
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
                return render(request, 'user/profile/edit_profile.html', {'mover': mover, 'form1': form1, 'user_info':
                    user_info,'error': 'Mauvaises données !'})
        else:
            form1 = EditUserForm(instance=request.user)

    if 'edit_user_info' in request.POST:
        if request.method == 'POST':
            try:
                form2 = User_Info_Form(request.POST, instance=user_info)
                if form2.is_valid():
                    form2.save()
                    messages.success(request, 'Modification effectué avec succès !')
                    return redirect('edit_profile')
            except ValueError:
                return render(request, 'user/profile/edit_profile.html', {'mover': mover, 'form2': form2, 'user_info':
                    user_info, 'error': 'Mauvaises données !'})
        else:
            form2 = User_Info_Form(instance=user_info)

    if 'edit_user_image' in request.POST:
        if request.method == 'POST':
            try:
                form2 = User_Info_Form(request.POST, request.FILES, instance=user_info)
                if form2.is_valid():
                    form2.save()
                    messages.success(request, 'Votre photo de profile a été modifié avec succès !')
                    return redirect('edit_profile')
            except ValueError:
                return render(request, 'user/profile/edit_profile.html', {'mover': mover, 'form2': form2, 'user_info':
                    user_info,'error': 'Mauvaises données !'})
        else:
            form2 = User_Info_Form(instance=user_info)

    if 'edit_company_logo' in request.POST:
        if request.method == 'POST':
            try:
                mover_form = Mover_Form(request.POST, request.FILES, instance=mover)
                if mover_form.is_valid():
                    mover_form.save()
                    messages.success(request, 'Votre logo a été modifié avec succès !')
                    return redirect('edit_profile')
            except ValueError:
                return render(request, 'user/profile/edit_profile.html', {'mover': mover, 'mover_form': mover_form, 'user_info':
                    user_info,'error': 'Mauvaises données !'})
        else:
            mover_form = User_Info_Form(instance=mover)

    if 'edit_mover_info' in request.POST:
        if request.method == 'POST':
            try:
                mover_form = Mover_Form(request.POST, instance=mover)
                if mover_form.is_valid():
                    mover_form.save()
                    messages.success(request, 'Modification effectué avec succès !')
                    return redirect('edit_profile')
            except ValueError:
                return render(request, 'user/profile/edit_profile.html', {'mover': mover, 'mover_form': mover_form, 'user_info':
                    user_info,'error': 'Mauvaises données !'})
        else:
            mover_form = Mover_Form(instance=mover)

    if 'social_media_link_form' in request.POST:
        if request.method == 'POST':
            try:
                mover_form = Mover_Form(request.POST, instance=mover)
                if mover_form.is_valid():
                    mover_form.save()
                    messages.success(request, 'Modification effectué avec succès !')
                    return redirect('edit_profile')
            except ValueError:
                return render(request, 'user/profile/edit_profile.html', {'mover': mover, 'mover_form': mover_form, 'user_info':
                    user_info,'error': 'Mauvaises données !'})
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

    return render(request, 'user/profile/edit_profile.html', {'mover': mover, 'form2': form2, 'form1': form1, 'user_info':
                                                                user_info, 'password_edit_form': password_edit_form, 'mover_form':
                                                              mover_form})


@login_required
def billing(request):
    mover = Mover.objects.filter(user_id=request.user.id).last()
    user_info = get_object_or_404(User_Info, user=request.user)
    return render(request, 'user/profile/billing.html', {'mover': mover, 'user_info': user_info})


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
        return redirect('settings')


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


@login_required
def delete_mover_moving_type1(request, moving_type_pk, mover_pk):
    mover = get_object_or_404(Mover, pk=mover_pk)
    mover_moving_tytpe = get_object_or_404(Mover_Moving_Type1, pk=moving_type_pk)

    if request.method == 'GET':
        form = EditMoverMovingType1Form(instance=mover_moving_tytpe)
        return render(request, 'user/mover/settings/delete_mover_moving_type1.html',
                      {'mover_moving_tytpe': mover_moving_tytpe, 'form': form, 'mover': mover})
    if request.method == 'POST':
        mover_moving_tytpe.delete()
        messages.success(request, 'Suppression effectuée !')
        return redirect('settings')


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
        return redirect('settings')