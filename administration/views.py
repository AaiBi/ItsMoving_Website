from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404

from base_app.forms import Mover_Form
from base_app.models import Mover, Country, Quote_Request, Moving_Type1, Moving_Type2, Mover_Quote_Request, \
    Quote_Request_Rejected


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
                    return redirect('admin_home')
        else:
            messages.error(request, 'Vous n\'êtes pas autorisé à accéder à cette page !')
            return redirect('admin_login')


@login_required
def admin_home(request):
    return render(request, 'administration/admin_home.html')


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

    if 'search' in request.POST:
        ref = request.POST.get('ref')
        if Quote_Request.objects.filter(ref=ref):
            quote_request = get_object_or_404(Quote_Request, ref=ref)

            if quote_request:
                return render(request, 'administration/devis/devis_home.html', {'quote_request': quote_request})

        else:
            messages.error(request, 'Cette référence n\'existe pas !')
            return render(request, 'administration/devis/devis_home.html')

    return render(request, 'administration/devis/devis_home.html', {'countries': countries, 'quote_requests':
                    quote_requests, 'moving_type1': moving_type1, 'moving_type2': moving_type2, 'mover_quote_requests':
                                                                    mover_quote_requests, 'distributed_requests':
                                                                    distributed_requests,
                                                                    'number_quote_requests_rejected':
                                                                    number_quote_requests_rejected,
                                                                    'quote_requests_rejected':
                                                                    quote_requests_rejected})


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
                                                                          quote_requests_rejected})


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
    number_mover_quote_requests = Mover_Quote_Request.objects.filter(mover_id=mover_pk).count()

    return render(request, 'administration/movers/mover_detail.html', {'mover': mover, 'countries': countries,
                                                                       'moving_type1': moving_type1, 'moving_type2'
                                                                       : moving_type2, 'movers': movers, 'users':
                                                                           users, 'number_mover_quote_requests':
                                                                       number_mover_quote_requests})


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
                messages.error(request, 'Profil désactivé !')
                return redirect('movers_home')

    return render(request, 'administration/movers/mover_active_unactive.html', {'mover': mover, 'countries': countries,
                                                                       'moving_type1': moving_type1, 'moving_type2'
                                                                       : moving_type2, 'movers': movers, 'users':
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
