
from django.db import models
from django.utils.timezone import now
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

#users model
class MofreyfxUsers (models.Model):
    email=models.EmailField()
    password=models.CharField(max_length=10)
    username=models.CharField(max_length=20)
    phone=models.CharField(max_length=20)
    firstname=models.CharField(max_length=20,default='firstname')
    secondname=models.CharField(max_length=20,default='secondname')

    def __str__(self):
        return f'{self.email} :{self.username}'

#course model
class Course(models.Model):
    course_name = models.CharField(max_length=255)
    image_url = models.URLField(max_length=200)
    trailer_url = models.URLField(max_length=200)
    intro_notes = models.TextField(blank=True)
    price = models.FloatField()
    duration=models.FloatField()
    date=models.DateTimeField(default=now,blank=False)

    def __str__(self):
        return self.course_name
    
#model for paid courses
class PaidCourse(models.Model):
    userId= models.IntegerField()
    courseId = models.IntegerField()
    date=models.DateTimeField(default=now,blank=False)

    def __str__(self):
        return f'{self.userId} - {self.courseId}'
    

class Payments(models.Model):
    email=models.EmailField()
    courseId = models.IntegerField()
    userId = models.IntegerField()
    amountkes = models.FloatField(default=0.0)
    amountusd = models.FloatField(default=0.0)
    mpesa_number = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20,default='initialized')
    payment_method = models.CharField(max_length=20,default='mpesa')

    def __str__(self):
        return f'{self.userId} :{self.payment_status} :{self.payment_method}'

class Subtopic(models.Model):
    subtopic= models.CharField(max_length=255)
    course = models.ForeignKey(Course,on_delete=models.CASCADE,default=0)
    date=models.DateTimeField(default=now,blank=False)

    def __str__(self):
        return f'{self.course} :{self.subtopic}'

class Modules(models.Model):
    module_name = models.CharField(max_length=255)
    thumbnail_url = models.URLField(max_length=200)
    video_url = models.URLField(max_length=200)
    module_notes = models.TextField(blank=True)
    module_number = models.IntegerField()
    course = models.ForeignKey(Course,on_delete=models.CASCADE)
    subtopic = models.ForeignKey(Subtopic, on_delete=models.CASCADE,default=0)
    date=models.DateTimeField(default=now,blank=False)
    def __str__(self):
        return f'{self.course} :{self.subtopic} :{self.module_name}'


  
    

class Questions(models.Model):
    course = models.ForeignKey(Course,on_delete=models.CASCADE,default=0)
    module = models.ForeignKey(Modules,on_delete=models.CASCADE)
    question_image_url=models.URLField(default='https://me.com')
    question_text = models.TextField()
    choice1 = models.CharField(max_length=255,blank=True)
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
        return f'{self.module} - {self.question_text}' 
    

class Marks(models.Model):
    userId = models.IntegerField()
    moduleId=models.IntegerField()
    marks=models.IntegerField(default=0)
    date=models.DateTimeField(default=now,blank=False)
    status=models.BooleanField(default=False)
    def __str__(self):
        return f'{self.userId} :{self.moduleId}'








