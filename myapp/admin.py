
from django.contrib import admin
from . models import MofrexUsers,Course,PaidCourse,Payments,Questions

# Register your models here.
admin.site.register(MofrexUsers)
admin.site.register(Course)
admin.site.register(PaidCourse)
admin.site.register(Questions)
admin.site.register(Payments)