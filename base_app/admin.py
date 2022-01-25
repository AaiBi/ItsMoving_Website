from django.contrib import admin
from base_app.models import Mover, Moving_Type1, Moving_Type2, RegionOrProvince, Country, Mover_Moving_Type1, \
    Mover_Moving_Type2, Mover_Country, Mover_Region

admin.site.register(Moving_Type1)
admin.site.register(Moving_Type2)
admin.site.register(Mover)
admin.site.register(Mover_Moving_Type1)
admin.site.register(Mover_Moving_Type2)
admin.site.register(RegionOrProvince)
admin.site.register(Country)
admin.site.register(Mover_Country)
admin.site.register(Mover_Region)
