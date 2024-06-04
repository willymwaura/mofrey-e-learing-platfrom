
from django.contrib import admin
from . models import MofreyfxUsers,Course,PaidCourse,Payments,Episodes,Subtopic,Questions,Marks

# Register your models here.
admin.site.register(MofreyfxUsers)
admin.site.register(Course)
admin.site.register(PaidCourse)

admin.site.register(Payments)
admin.site.register(Episodes)
admin.site.register(Subtopic)
admin.site.register(Questions)
admin.site.register(Marks)