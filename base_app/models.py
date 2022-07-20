from django.contrib.auth.models import User
from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=300)

    def __str__(self):
        return self.name


class Region(models.Model):
    name = models.CharField(max_length=300)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Moving_Type1(models.Model):  # can be national opr international
    name = models.CharField(max_length=300)

    def __str__(self):
        return self.name


class Moving_Type2(models.Model):  # can be 'particulier' or 'professionnel'
    name = models.CharField(max_length=300)

    def __str__(self):
        return self.name


class Mover(models.Model):
    ref = models.CharField(max_length=30, default="")
    company_name = models.CharField(max_length=300)
    company_phone_number = models.CharField(max_length=50)
    Adresse = models.CharField(max_length=300, default="")
    employee_number = models.IntegerField(default=0)
    number_max_quote_request = models.IntegerField(default=0)
    website = models.CharField(max_length=300, default="")
    TVA_number = models.CharField(max_length=30, default="")
    Postal_Code = models.IntegerField(default=0)
    company_statut = models.CharField(max_length=300, default="")
    company_description = models.TextField(default="")
    logo = models.ImageField(upload_to='user/images/profil_image/', blank=True, default="")
    pause = models.BooleanField(default=False)
    activated = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default="")
    country = models.ForeignKey(Country, on_delete=models.CASCADE, default="")
    region = models.ForeignKey(Region, on_delete=models.CASCADE, default="")
    moving_type1 = models.ForeignKey(Moving_Type1, on_delete=models.CASCADE, default="")

    def __str__(self):
        return self.company_name


class Mover_Images(models.Model):
    image = models.ImageField(upload_to='base_app/images/', blank=True)
    mover = models.ForeignKey(Mover, on_delete=models.CASCADE, default="")


class Mover_Moving_Type2(models.Model):
    moving_type2_name = models.CharField(max_length=300, default="")
    mover = models.ForeignKey(Mover, on_delete=models.CASCADE)


class Mover_Country(models.Model):
    country_name = models.CharField(max_length=300)
    departure = models.BooleanField(default=False)
    arrival = models.BooleanField(default=False)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, default="")
    mover = models.ForeignKey(Mover, on_delete=models.CASCADE)


class Mover_Region(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE, default="")
    mover = models.ForeignKey(Mover, on_delete=models.CASCADE)


class Quote_Request(models.Model):
    ref = models.CharField(max_length=30)
    Adresse_Departure = models.CharField(max_length=300)
    Postal_Code_Departure = models.IntegerField()
    Residence_Number_or_Name_Departure = models.CharField(max_length=300)
    Residence_Departure = models.CharField(max_length=300)
    Number_Room_Departure = models.IntegerField()
    Country_Arrival = models.CharField(max_length=300, default="")

    City_Arrival_for_international_moving = models.CharField(max_length=300, default="")
    Region_Arrival_for_national_moving = models.CharField(max_length=300, default="")

    Adresse_Arrival = models.CharField(max_length=300)
    Residence_Number_or_Name_Arrival = models.CharField(max_length=300)
    Postal_Code_Arrival = models.IntegerField()
    Residence_Arrival = models.CharField(max_length=300)
    packing_service = models.BooleanField(default=False)
    packaging_materials = models.BooleanField(default=False)
    furniture_assembly_disassembly = models.BooleanField(default=False)
    furniture_storage = models.BooleanField(default=False)
    Additional_informations = models.CharField(max_length=300)
    firstname = models.CharField(max_length=300, default="")
    lastname = models.CharField(max_length=300, default="")
    email = models.EmailField(default="")
    phone_number = models.CharField(max_length=30, default="")
    created = models.DateTimeField(auto_now_add=True)
    distributed = models.BooleanField(default=False)
    moving_date = models.DateTimeField(auto_now_add=False)
    moving_date1 = models.DateTimeField(auto_now_add=False)
    moving_date2 = models.DateTimeField(auto_now_add=False)
    moving_type1 = models.ForeignKey(Moving_Type1, on_delete=models.CASCADE)
    moving_type2 = models.ForeignKey(Moving_Type2, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, default="")
    region = models.ForeignKey(Region, on_delete=models.CASCADE, default="")

    def __str__(self):
        return self.ref


class Mover_Quote_Request(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    quote_request = models.ForeignKey(Quote_Request, on_delete=models.CASCADE)
    treated = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    paid = models.CharField(max_length=20, default='Non payé') #can be 'Non payé' or 'Payé' or 'Vérification en cours...'
    mover = models.ForeignKey(Mover, on_delete=models.CASCADE)


class Quote_Request_Rejected(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    reason = models.TextField()
    mover_quote_request = models.ForeignKey(Mover_Quote_Request, on_delete=models.CASCADE, default="")


class Number_Mover_Quote_Request_PerDay(models.Model):
    number_quote_received_the_same_day = models.IntegerField()
    reception_date_quote_request = models.DateTimeField(auto_now_add=True)
    mover = models.ForeignKey(Mover, on_delete=models.CASCADE)


class Number_Distribution_Quote_Request(models.Model):
    number_distribution = models.IntegerField()
    number_max_distribution = models.IntegerField(default=5)
    created = models.DateTimeField(auto_now_add=True)
    quote_request = models.ForeignKey(Quote_Request, on_delete=models.CASCADE)


class Review(models.Model):
    speed = models.IntegerField(default=0)
    organisation = models.IntegerField(default=0)
    reliability = models.IntegerField(default=0)
    quality = models.IntegerField(default=0)
    message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    mover_quote_request = models.ForeignKey(Mover_Quote_Request, on_delete=models.CASCADE)


class Movers_Email(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    quote_request = models.ForeignKey(Quote_Request, on_delete=models.CASCADE, default="")
    mover = models.ForeignKey(Mover, on_delete=models.CASCADE, default="")


class Customers_Notification_Email(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    moving_possibility = models.BooleanField(default=False) # If True: movers available for the region or country
    quote_request = models.ForeignKey(Quote_Request, on_delete=models.CASCADE)
    mover = models.ForeignKey(Mover, on_delete=models.CASCADE)
