
from django.http import response
from django.shortcuts import render,get_object_or_404,redirect
import requests
from myapp.models import Course,PaidCourse,MofrexUsers,Payments,Questions
from intasend import APIService
from django.http import HttpResponse,JsonResponse
import json
from django.core.mail import send_mail
from dict import settings
import logging



# Create your views here.
from django.shortcuts import render
def index(request):
    courses = Course.objects.all()
    try:
        user_id = request.session.get('user_id')
        paid_courses = PaidCourse.objects.filter(userId=user_id)
            #print(paid_courses.count())
        course_ids = [paid_course.courseId for paid_course in paid_courses]
        
        return render(request, 'index.html', {'courses': courses,"course_ids":course_ids})
    except:
        return render(request, 'index.html', {'courses': courses})

'''
def home(request):
    courses = Course.objects.all()
    user_id = request.session.get('user_id')
    paid_courses = PaidCourse.objects.filter(userId=user_id)
        #print(paid_courses.count())
    course_ids = [paid_course.courseId for paid_course in paid_courses]
    return render(request, 'home.html', {'courses': courses,"course_ids":course_ids})'''

def about(request):
    return render(request, 'about.html')

def allcourses(request):
    # Query all courses from the Course model
    courses = Course.objects.all()
    try:
        user_id = request.session.get('user_id')
        paid_courses = PaidCourse.objects.filter(userId=user_id)
            #print(paid_courses.count())
        course_ids = [paid_course.courseId for paid_course in paid_courses]
        
        return render(request, 'allcourses.html', {'courses': courses,"course_ids":course_ids})
    except:
        return redirect("/login")

    # Pass courses to the template for rendering
    

def contact(request):
    return render(request, 'contact.html')

def course(request,id):
    #store course id
    request.session['course_id'] = id

    try:

    # Get the user ID from the session
        user_id = request.session.get('user_id')

    
        try:
            # Check if the user has paid for the specified course
            paid_course = PaidCourse.objects.get(userId=user_id, courseId=id)

            # If the user has paid, retrieve the course details
            course = Course.objects.get(id=paid_course.courseId)
            questions = Questions.objects.filter(course=id)
            # Create a list to store each question with its choices
            questions_with_choices = []
            for question in questions:
                questions_with_choices.append({
                    'question': question,
                    'choices': question.get_choices()
                })

            context = {
                'questions_with_choices': questions_with_choices,
                'course':course
            }
            return render(request, 'course.html', context)


            
        except PaidCourse.DoesNotExist:
            # If the user has not paid for the course, redirect to the payment URL
            usdprice=Course.objects.get(id=id).price
            request.session['usdprice'] = usdprice
            #print(usdprice)
            #we have estimated 1 usd is 135 ke
            keprice=usdprice*135
            keprice=int(keprice)
            request.session['keprice'] = id
            return render(request,"payment.html",{"usdprice":usdprice,"keprice":keprice})
    except:
        # If user_id is not in session redirect to login
        return redirect('/login') 

def forgot_password(request):
    return render(request, 'forgot_password.html')

def user_login(request):
    return render(request, 'login.html')

def payment(request):
    return render(request, 'payment.html')

def user_register(request):
    return render(request, 'register.html')

def watchlist(request):
    print("watchlist called")
    # Get the user_id from the session
    try:
        #print("hello")
        user_id = request.session.get('user_id')
        #print(user_id)

        if user_id:
            # Retrieve all course_ids associated with the current user_id from PaidCourse
            paid_courses = PaidCourse.objects.filter(userId=user_id)
            print(paid_courses.count())
            course_ids = [paid_course.courseId for paid_course in paid_courses]

            # Retrieve Course objects corresponding to the course_ids
            courses = Course.objects.filter(pk__in=course_ids)

            # Render the watchlist.html template with the filtered courses
            return render(request, 'watchlist.html', {'courses':courses})

        else:
            # Handle case where user_id is not found in the session
            return render(request, 'watchlist.html', {'courses': []})
    except:
        return redirect('/login')

def gallery(request):
    return render (request,'gallery.html')

def create_account(request):

    password1= request.POST.get('password', False)
    password2 = request.POST.get('confirm_password', False)
    email = request.POST.get('email', False)
    phone = request.POST.get('phone', False)
    username = request.POST.get('username', False)


    if  password1 != password2:
        message="the two passwords are diffrent."
        return render(request, "register.html", {"message": message})

        # Check if email and password are provided
    if not email or not password1:
        message="Email and password are required."
        return render(request, "register.html", {"message": message})

        # Check if user already exists
    if MofrexUsers.objects.filter(email=email).exists():
        
        message="User with this email already exists.."
        return render(request, "register.html", {"message": message})

        # Create user
    user = MofrexUsers.objects.create(email=email, password=password1,phone=phone,username=username)
    

        # Respond with success message
    return render(request, "login.html")

def auth_login(request):
    email = request.POST.get('email',False)
    password = request.POST.get('password',False)

        # Check if an email and password are provided
    if not email or not password:
        
        message= "Email and password are required."
        return render(request, "login.html", {"message": message})

    try:
            # Check if user exists
        user = MofrexUsers.objects.get(email=email,password=password)
    except MofrexUsers.DoesNotExist:
        
        message= "User does not exist.You need to sign up please."
        return render(request, "login.html", {"message": message})

        # Check if password is correct
    if user.password != password:
        
        message= "You provided an incorrect password."
        return render(request, "login.html", {"message": message})

        # If everything is correct, respond with user details
    # Store the user ID in the session
    request.session['user_id'] = user.id
    return redirect('index')

def mpesa_checkout(request):
    try:
        #getting user id from session
        user_id=request.session.get('user_id')

        #getting saf number from form
        phone = request.POST.get('phone', False)
        #email of the user
        email = MofrexUsers.objects.get(id=user_id).email
        #cost of course
        amountkes = request.session.get('keprice')
        courseid = request.session.get('course_id')
        #print(amount)
        if phone.startswith('0'):
                phone = '254' + phone[1:]
                print(phone)
                
        payment_instance=Payments.objects.create(mpesa_number=phone,email=email,amountkes=amountkes,courseId=courseid,userId=user_id)
        payment_instance.save()
        

        try:
                # Initialize the APIService
            token = "ISSecretKey_live_0bcbeaa2-f210-476b-9bfa-28fae2ee5c0a"
            publishable_key = "ISPubKey_live_ee33ed45-3f7e-46ce-a6a4-d91fae6de1de"
            service = APIService(token=token, publishable_key=publishable_key, test=False)

                # Trigger M-Pesa STK Push
            response = service.collect.mpesa_stk_push(phone_number=phone, email=email, amount=amountkes, narrative="mpesa payment")
            print(response)

                # Return the response from the M-Pesa STK Push
            return render(request,"loading.html")

        except Exception as e:
                # Return an error if there's an exception
            return render(request,"index.html",{"error": "try again later "})
    except:
        return redirect('/login')



def CardPayments(request):
    try:
        #getting user id from session
        user_id=request.session.get('user_id')

        #getting saf number from form
        #phone = request.POST.get('phone', False)
        #email of the user
        email = MofrexUsers.objects.get(id=user_id).email
        #cost of course
        amountusd = request.session.get('usdprice')
        courseid = request.session.get('course_id')
        
        
                
        payment_instance=Payments.objects.create(email=email,amountusd=amountusd,courseId=courseid,userId=user_id)
        payment_instance.save()
        

        
        try:
            publishable_key = "ISPubKey_live_ee33ed45-3f7e-46ce-a6a4-d91fae6de1de"
            service = APIService(token="ISSecretKey_live_0bcbeaa2-f210-476b-9bfa-28fae2ee5c0a", publishable_key=publishable_key, test=False)

            response = service.collect.checkout(phone_number=254112100378,email=email, amount=amountusd, currency="USD", comment="Service Fees", redirect_url="http://example.com/thank-you")
            url=response.get("url")
            return redirect(url)

        except:
            return redirect("/index")
    except:
        return redirect("/login")
    
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  
def PaymentCallback(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data in the request."}, status=400)
    print(data)
    

        # Check if transaction state is complete
    if data["state"] == "COMPLETE":
        try:
                # Get or create credit balance for the account
            account = data["account"]
            try:
               int_account= int(account)
               phone=chr(int_account)
            except:
                email=account

            if phone:
                payment_instance= Payments.objects.filter(mpesa_number=phone).latest('id')
                payment_instance.payment_status='completed'
                payment_instance.save()
                user_id=payment_instance.userId
                course_id=payment_instance.courseId
                paid_course_instance=PaidCourse.objects.create(userId=user_id,courseId=course_id)
                paid_course_instance.save()
            if email:
                payment_instance= Payments.objects.filter(email=email).latest('id')
                payment_instance.payment_status='completed'
                payment_instance.payment_method='card'
                payment_instance.save()
                user_id=payment_instance.userId
                course_id=payment_instance.courseId
                paid_course_instance=PaidCourse.objects.create(userId=user_id,courseId=course_id)
                paid_course_instance.save()
            else:
                return JsonResponse({"message": "NO EMAIL OR PHONE."})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Transaction state is not complete."})

def user_profile(request):
    
    print("starting")
    print("getting id")
    user_id=request.session.get('user_id')
    print(user_id)
    user_logged=MofrexUsers.objects.get(id=user_id)
    email = user_logged.email
    password = user_logged.password
    username = user_logged.username
    phone = user_logged.phone
    print(phone)
    user_data = {
            'email': email,
            'password': password,
            'username': username,
            'phone': phone
        }
    
    return render(request, "profile.html", {'user_data': user_data})
    
    
def reset_password(request):
    email = request.POST.get('email',False)
    print(email)
    try:
        
        password=MofrexUsers.objects.get(email=email).password
        subject = 'your password'
        message = "your password is" + password + 'you can login now to mofrey markets.'   
        from_email = settings.EMAIL_HOST_USER   
        recipient_list = [email]
        print("sending email")
        send_mail(subject, message, from_email, recipient_list)
        message="your passord has been sent to your email"
        return render(request,"forgot_password.html",{"message":message})
    except Exception as e:
        logging.error(f"Failed to send email. Error message: {str(e)}")
        message='use the correct email'
        return render(request,"forgot_password.html",{"message":message})
    

def submit_quiz(request):
    if request.method == 'POST':
        score = 0
        total_questions = len(request.POST) // 2  # Each question has 2 form inputs (choice and answer)
        answer_details = []  # List to store details about each question's answer

        for i in range(1, total_questions + 1):
            question_id = request.POST.get(f'question_{i}_answer')
            selected_choice = request.POST.get(f'question_{i}_choice')

            if question_id and selected_choice:
                question = Questions.objects.get(id=question_id)
                correct_answer_index = question.correct_answer - 1  # Convert to zero-based index
                correct_choice_text = getattr(question, f'choice{question.correct_answer}')

                if selected_choice == str(question.correct_answer):
                    score += 1

                # Store question details and correct choice text in answer_details list
                answer_details.append({
                    'question_text': question.question_text,
                    'selected_choice': selected_choice,
                    'correct_choice': correct_choice_text
                })

        response_data = {
            'score': score,
            'total_questions': total_questions,
            'answer_details': answer_details  # Include answer details in the response
        }

        # Print every question with the correct answer text
        for detail in answer_details:
            print(f"Question: {detail['question_text']}")
            print(f"Correct Answer: {detail['correct_choice']}")
            print()  # Print a blank line for better readability

        return JsonResponse(response_data)

    return JsonResponse({'error': 'Invalid request'}, status=400)

    

  