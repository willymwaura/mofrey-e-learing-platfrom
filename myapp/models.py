
from django.db import models
from django.utils.timezone import now
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

#users model
class MofreyfxUsers (models.Model):
    email=models.EmailField()
    password=models.CharField(max_length=10)
    username=models.CharField(max_length=20,default='username')
    phone=models.CharField(max_length=20,default='0112345678')

    def __str__(self):
        return self.email

#course model
class Course(models.Model):
    name = models.CharField(max_length=255)
    image_url = models.URLField(max_length=200)
    video_url = models.URLField(max_length=200)
    notes = models.TextField(blank=True)
    price = models.FloatField()
    duration=models.FloatField()
    date=models.DateTimeField(default=now,blank=False)

    def __str__(self):
        return self.name
    
#model for paid courses
class PaidCourse(models.Model):
    userId= models.IntegerField()
    courseId = models.IntegerField()
    date=models.DateTimeField(default=now,blank=False)

    def __str__(self):
        return f'{self.userId} - {self.courseId}'
    

class Payments(models.Model):
    email=models.EmailField(default="email@gmail.com")
    courseId = models.IntegerField()
    userId = models.IntegerField()
    amountkes = models.FloatField(default=0.0)
    amountusd = models.FloatField(default=0.0)
    mpesa_number = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20,default='initialized')
    payment_method = models.CharField(max_length=20,default='mpesa')

class Questions(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    question_text = models.TextField()
    choice1 = models.CharField(max_length=255)
    choice2 = models.CharField(max_length=255)
    choice3 = models.CharField(max_length=255,blank=True)
    choice4 = models.CharField(max_length=255,blank=True)
    choice5 = models.CharField(max_length=255,blank=True)
    correct_answer = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    def get_choices(self):
        choices = []
        for i in range(1, 6):  # Assuming choices are 'choice1' to 'choice5'
            choice_text = getattr(self, f'choice{i}')
            if choice_text:
                choices.append(choice_text)
        return choices

    def __str__(self):
        return f'{self.course.name} - {self.question_text}'





