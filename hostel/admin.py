from django.contrib import admin
from .models import CustomUser, UserProfile, UserRoom, GatePass, Vacancy, RequestBox, Feedback ,AdminSecurity

admin.site.register(CustomUser)
admin.site.register(AdminSecurity)
admin.site.register(UserProfile)
admin.site.register(UserRoom)
admin.site.register(GatePass)
admin.site.register(Vacancy)
admin.site.register(RequestBox)
admin.site.register(Feedback)

