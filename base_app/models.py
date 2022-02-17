from django.contrib.auth.models import User
from django.db import models


class Gender(models.Model):
    name = models.CharField(max_length=300)

    def __str__(self):
        return self.name


class Country(models.Model):
    name = models.CharField(max_length=300)

    def __str__(self):
        return self.name


class RegionOrProvince(models.Model):
    name = models.CharField(max_length=300)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Moving_Type1(models.Model): #can be national opr international
    name = models.CharField(max_length=300)

    def __str__(self):
        return self.name


class Moving_Type2(models.Model): #can be 'particulier' or 'professionnel'
    name = models.CharField(max_length=300)

    def __str__(self):
        return self.name


class Mover(models.Model):
    ref = models.CharField(max_length=30, default="")
    company_name = models.CharField(max_length=300)
    Adresse = models.CharField(max_length=300, default="")
    City = models.CharField(max_length=300, default="")
    country = models.CharField(max_length=300, default="")
    company_phone_number = models.CharField(max_length=50)
    Postal_Code = models.IntegerField(default=0)
    employee_number = models.IntegerField(default=0)
    TVA_number = models.CharField(max_length=30, default="")
    company_description = models.TextField(default="")
    website = models.CharField(max_length=300, default="")
    company_statut = models.CharField(max_length=300, default="")
    facebook_link = models.CharField(max_length=500, default="")
    instagram_link = models.CharField(max_length=500, default="")
    twitter_link = models.CharField(max_length=500, default="")
    linkedin_link = models.CharField(max_length=500, default="")
    number_max_quote_request = models.IntegerField(default=0)
    logo = models.ImageField(upload_to='base_app/images/', blank=True, default="")
    validated = models.BooleanField(default=False)
    activated = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default="")

    def __str__(self):
        return self.company_name


class Mover_Images(models.Model):
    image = models.ImageField(upload_to='base_app/images/', blank=True)
    mover = models.ForeignKey(Mover, on_delete=models.CASCADE, default="")


class Mover_Moving_Type1(models.Model):
    moving_type1_name = models.CharField(max_length=300, default="")
    mover = models.ForeignKey(Mover, on_delete=models.CASCADE)


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
    region_name = models.CharField(max_length=300)
    region = models.ForeignKey(RegionOrProvince, on_delete=models.CASCADE, default="")
    country = models.ForeignKey(Country, on_delete=models.CASCADE, default="")
    mover = models.ForeignKey(Mover, on_delete=models.CASCADE)


class Quote_Request(models.Model):
    ref = models.CharField(max_length=30)

    City_Departure = models.CharField(max_length=300)
    Postal_Code_Departure = models.IntegerField()
    Adresse_Departure = models.CharField(max_length=300)
    Residence_Number_or_Name_Departure = models.CharField(max_length=300)
    Country_Arrival = models.CharField(max_length=300, default="")
    City_Arrival = models.CharField(max_length=300)
    Adresse_Arrival = models.CharField(max_length=300)
    Residence_Number_or_Name_Arrival = models.CharField(max_length=300)
    Postal_Code_Arrival = models.IntegerField()
    Residence_Departure = models.CharField(max_length=300)
    Number_Room_Departure = models.IntegerField()
    Residence_Arrival = models.CharField(max_length=300)
    packing_service = models.BooleanField(default=False)
    packaging_materials = models.BooleanField(default=False)
    furniture_assembly_disassembly = models.BooleanField(default=False)
    furniture_storage = models.BooleanField(default=False)
    firstname = models.CharField(max_length=300, default="")
    lastname = models.CharField(max_length=300, default="")
    email = models.EmailField(default="")
    phone_number = models.CharField(max_length=30, default="")
    Additional_informations = models.CharField(max_length=300)
    moving_date = models.DateTimeField(auto_now_add=False)
    moving_date1 = models.DateTimeField(auto_now_add=False)
    moving_date2 = models.DateTimeField(auto_now_add=False)
    created = models.DateTimeField(auto_now_add=True)

    moving_type1 = models.ForeignKey(Moving_Type1, on_delete=models.CASCADE)
    moving_type2 = models.ForeignKey(Moving_Type2, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, default="")

    def __str__(self):
        return self.ref


class Mover_Quote_Request(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    quote_request = models.ForeignKey(Quote_Request, on_delete=models.CASCADE)
    mover = models.ForeignKey(Mover, on_delete=models.CASCADE)


class Number_Mover_Quote_Request_Per_Day(models.Model):
    number_quote_received_the_same_day = models.IntegerField()
    reception_date_quote_request = models.DateTimeField(auto_now_add=True)
    mover = models.ForeignKey(Mover, on_delete=models.CASCADE)