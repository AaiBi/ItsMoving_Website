from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from base_app.forms import Mover_Form
from base_app.models import Mover, Moving_Type1, Mover_Moving_Type1, Moving_Type2, Mover_Moving_Type2, Country, \
    RegionOrProvince, Mover_Country, Mover_Region
import random


def index(request):
    return render(request, 'base_app/index.html')


def mover_inscription(request):

    # creation of the ref
    characters = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    characters.extend(list('1234567890'))
    size = 10
    ref = ''
    for x in range(size):
        ref += random.choice(characters)
    ref = ref

    if request.method == 'POST':
        form = Mover_Form(request.POST)
        if request.user.is_authenticated:
            if form.is_valid():
                form = form.save(commit=False)
                if Mover.objects.filter(company_name=request.POST.get('company_name')):
                    messages.error(request, 'Erreur ! Ce nom d\'entreprise existe déjà dans notre base de données !')
                    return redirect('mover_inscription')
                elif Mover.objects.filter(company_email=request.POST.get('company_email')):
                    messages.error(request, 'Erreur ! Cet email existe déjà dans notre base de données !')
                    return redirect('mover_inscription')
                elif Mover.objects.filter(company_phone_number=request.POST.get('company_phone_number')):
                    messages.error(request, 'Erreur ! Cet email existe déjà dans notre base de données !')
                    return redirect('mover_inscription')
                else:
                    form.user = get_object_or_404(User, id=request.user.id)
                    form.save()
                    messages.success(request, 'Informations ajoutées avec succès !')
                    return redirect('mover_inscription_step1', mover_pk=form.id)
        else:
            messages.error(request, 'Veuillez vous connectez d\'abord, si vous n\'en avez pas veuillez en créer !')
            return redirect('login_user')
    return render(request, 'base_app/mover/mover_inscription.html', {'ref': ref})


def mover_inscription_step1(request, mover_pk):
    mover_information = get_object_or_404(Mover, pk=mover_pk)
    moving_type1 = Moving_Type1.objects.all()
    if request.method == 'POST':
        mover_id = request.POST.get('mover_id')
        moving_type1_name = request.POST.getlist('moving_type1_name[]')
        if request.POST.getlist('moving_type1_name[]'):
            for data in moving_type1_name:
                if Mover_Moving_Type1.objects.filter(moving_type1_name=data, mover=mover_information):
                    messages.error(request, 'Erreur ! Cette sélection existe déjà dans notre base de données !')
                    return redirect('mover_inscription_step1', mover_pk=mover_id)
                else:
                    mover = get_object_or_404(Mover, id=request.POST.get('mover_id'))
                    savedata = Mover_Moving_Type1(moving_type1_name=data, mover=mover)
                    savedata.save()
                    messages.success(request, 'Informations ajoutées avec succès !')
            return redirect('mover_inscription_step2', mover_pk=mover_id)
        else:
            messages.error(request, 'Veuillez faire au moins une sélection !')
            return redirect('mover_inscription_step1', mover_pk=mover_id)

    return render(request, 'base_app/mover/mover_inscription_step1.html', {'mover_information': mover_information,
                                                                           'moving_type1': moving_type1})


def mover_inscription_step2(request, mover_pk):
    mover_information = get_object_or_404(Mover, pk=mover_pk)
    moving_type2 = Moving_Type2.objects.all()
    if request.method == 'POST':
        mover_id = request.POST.get('mover_id')
        moving_type2_name = request.POST.getlist('moving_type2_name[]')
        if request.POST.getlist('moving_type2_name[]'):
            for data in moving_type2_name:
                if Mover_Moving_Type2.objects.filter(moving_type2_name=data, mover=mover_information):
                    messages.error(request, 'Erreur ! Cette sélection existe déjà dans notre base de données !')
                    return redirect('mover_inscription_step2', mover_pk=mover_id)
                else:
                    mover = get_object_or_404(Mover, id=request.POST.get('mover_id'))
                    savedata = Mover_Moving_Type2(moving_type2_name=data, mover=mover)
                    savedata.save()
                    messages.success(request, 'Informations ajoutées avec succès !')
            return redirect('mover_inscription_step3', mover_pk=mover_id)
        else:
            messages.error(request, 'Veuillez faire au moins une sélection !')
            return redirect('mover_inscription_step2', mover_pk=mover_id)
    return render(request, 'base_app/mover/mover_inscription_step2.html', {'mover_information': mover_information,
                                                                           'moving_type2': moving_type2})


def mover_inscription_step3(request, mover_pk):
    mover_information = get_object_or_404(Mover, pk=mover_pk)
    countries = Country.objects.all()
    if request.method == 'POST':
        country_name = request.POST.getlist('country_name[]')
        mover_id = request.POST.get('mover_id')
        if request.POST.getlist('country_name[]'):
            for data in country_name:
                if Mover_Country.objects.filter(country_name=data, mover=mover_information):
                    messages.error(request, 'Erreur ! Cette sélection existe déjà dans notre base de données !')
                    return redirect('mover_inscription_step3', mover_pk=mover_id)
                else:
                    country = Country.objects.filter(name=data).last()
                    mover = get_object_or_404(Mover, id=request.POST.get('mover_id'))
                    savedata = Mover_Country(country_name=data, country=country, mover=mover)
                    savedata.save()
                    messages.success(request, 'Informations ajoutées avec succès !')
            return redirect('mover_inscription_step4', mover_pk=mover_id)
        else:
            messages.error(request, 'Veuillez faire au moins une sélection !')
            return redirect('mover_inscription_step3', mover_pk=mover_id)
    return render(request, 'base_app/mover/mover_inscription_step3.html', {'mover_information': mover_information,
                                                                           'countries': countries})


def mover_inscription_step4(request, mover_pk):
    mover_information = get_object_or_404(Mover, pk=mover_pk)
    countries = Country.objects.all()
    regions = RegionOrProvince.objects.all()
    mover_countries = Mover_Country.objects.filter(mover=mover_information)

    if request.method == 'POST':
        mover_id = request.POST.get('mover_id')
        region_name = request.POST.getlist('region_name[]')
        if request.POST.getlist('region_name[]'):
            for data in region_name:
                if Mover_Region.objects.filter(region_name=data, mover=mover_information):
                    messages.error(request, 'Erreur ! Cette sélection existe déjà dans notre base de données !')
                    return redirect('mover_inscription_step4', mover_pk=mover_id)
                else:
                    region = RegionOrProvince.objects.filter(name=data).last()
                    for country in countries:
                        if country.id == region.country_id:
                            country = Country.objects.filter(id=country.id).last()
                            mover = get_object_or_404(Mover, id=request.POST.get('mover_id'))
                            savedata = Mover_Region(region_name=data, region=region, country=country, mover=mover)
                            savedata.save()
                            messages.success(request,
                                                 'Felicitations, l\'inscription est presque terminée, il ne vous reste qu\'à renseigner'
                                                 ' les provinces ou les communes dans lesquelles vous intervenez !')
            return redirect('preview')
        else:
            messages.error(request, 'Veuillez faire au moins une sélection !')
            return redirect('mover_inscription_step4', mover_pk=mover_id)
    return render(request, 'base_app/mover/mover_inscription_step4.html', {'mover_information': mover_information,
                            'countries': countries, 'regions': regions, 'mover_countries': mover_countries})


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
    return render(request, 'base_app/devis/devis_page1.html')


def article1_international_moving(request):
    return render(request, 'base_app/article1_international_moving.html')


def article2_belgium_moving(request):
    return render(request, 'base_app/article2_belgium_moving.html')