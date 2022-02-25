from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404

from base_app.forms import Mover_Form
from base_app.models import Mover, Country, Quote_Request, Moving_Type1, Moving_Type2, Mover_Quote_Request


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
    return render(request, 'administration/devis/devis_home.html', {'countries': countries, 'quote_requests':
                    quote_requests, 'moving_type1': moving_type1, 'moving_type2': moving_type2, 'mover_quote_requests':
                                                                    mover_quote_requests, 'distributed_requests':
                                                                    distributed_requests})


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

    if request.method == 'GET':
        return render(request, 'administration/devis/devis_detail.html', {'devis': devis, 'countries': countries,
                                                                          'moving_type1': moving_type1, 'moving_type2'
                                                                          : moving_type2, 'movers': movers, 'users':
                                                                          users, 'mover_quote_requests_number':
                                                                          mover_quote_requests_number,
                                                                          'mover_quote_requests': mover_quote_requests})
###################################################  END DEVIS    #####################################################


####################################################   Movers    ######################################################

@login_required
def movers_home(request):
    countries = Country.objects.all()
    moving_type1 = Moving_Type1.objects.all()
    moving_type2 = Moving_Type2.objects.all()
    movers = Mover.objects.all()
    movers_activated = Mover.objects.filter(activated=True)
    movers_unactivated = Mover.objects.filter(activated=False)
    movers_unactivated_count = Mover.objects.filter(activated=False).count()
    users = User.objects.all()

    if request.method == 'GET':
        form = Mover_Form()
        return render(request, 'administration/movers/movers_home.html', {'countries': countries,
                                                                          'moving_type1': moving_type1, 'moving_type2'
                                                                          : moving_type2, 'movers': movers, 'users':
                                                                          users, 'movers_unactivated':
                                                                          movers_unactivated, 'movers_unactivated_count'
                                                                          : movers_unactivated_count, 'form': form,
                                                                          'movers_activated': movers_activated})
    if request.method == 'POST':
        if request.POST.get('mover_id'):
            mover_info = get_object_or_404(Mover, pk=request.POST.get('mover_id'))
            form = Mover_Form(request.POST, instance=mover_info)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profil activé !')
                return redirect('movers_home')


@login_required
def mover_detail(request, mover_pk):
    mover = get_object_or_404(Mover, pk=mover_pk)

    countries = Country.objects.all()
    moving_type1 = Moving_Type1.objects.all()
    moving_type2 = Moving_Type2.objects.all()
    movers = Mover.objects.all()
    users = User.objects.all()

    if request.method == 'GET':
        return render(request, 'administration/movers/mover_detail.html', {'mover': mover, 'countries': countries,
                                                                          'moving_type1': moving_type1, 'moving_type2'
                                                                          : moving_type2, 'movers': movers, 'users':
                                                                          users})

    if request.method == 'POST':
        if request.POST.get('mover_id'):
            mover_info = get_object_or_404(Mover, pk=request.POST.get('mover_id'))
            form = Mover_Form(request.POST, instance=mover_info)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profil activé !')
                return redirect('movers_home')

##################################################   END Movers    ####################################################
