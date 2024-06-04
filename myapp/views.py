
from django.http import response
from django.shortcuts import render,get_object_or_404,redirect
import requests
from myapp.models import Course,PaidCourse,MofreyfxUsers,Payments,Modules,Subtopic,Questions,Marks
from intasend import APIService
from django.http import HttpResponse,JsonResponse
import json
from django.core.mail import send_mail
from dict import settings
import logging
import os
from dotenv import load_dotenv
load_dotenv()



# Create your views here.
from django.shortcuts import render
def index(request):
    courses = Course.objects.all().order_by('id')
    courses = courses[:4]
    user_id = request.session.get('user_id')
    if user_id is not None:
        paid_courses = PaidCourse.objects.filter(userId=user_id)
            #print(paid_courses.count())
        course_ids = [paid_course.courseId for paid_course in paid_courses]
        
        return render(request, 'index.html', {'courses': courses,"course_ids":course_ids})
    else:
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
    user_id = request.session.get('user_id')
    if user_id is not None:
        
        paid_courses = PaidCourse.objects.filter(userId=user_id)
            #print(paid_courses.count())
        course_ids = [paid_course.courseId for paid_course in paid_courses]
        
        return render(request, 'allcourses.html', {'courses': courses,"course_ids":course_ids})
    else:
        return redirect("/login")

    # Pass courses to the template for rendering
    

def contact(request):
    return render(request, 'contact.html')

from myapp.custom_fuctions import get_module_ids_ordered_by_subtopics_and_date ,give_unclocked_ids_list
def course(request,id):
    #store course id
    request.session['course_id'] = id
    user_id = request.session.get('user_id')
    if user_id is not None:

    
        try:
            # Check if the user has paid for the specified course
            print("start")
            paid_course = PaidCourse.objects.get(userId=user_id, courseId=id) 
            

            # If the user has paid, retrieve the course details
            course = Course.objects.get(id=paid_course.courseId)
            #getting the subtopics of the course 
            subtopics=Subtopic.objects.filter(course=id).order_by('date')
            print("fetched subtopics")

            course_modules_list=get_module_ids_ordered_by_subtopics_and_date(id)
            print(course_modules_list)
            #replace this code with a fuction
            '''
            try:
                latest_mark = Marks.objects.filter(status=True).latest('date')
                latest_module_id = latest_mark.moduleId

                position = course_modules_list.index(latest_module_id)
                modules_to_view=position+2
            except:
                modules_to_view=1
            print(modules_to_view)
            unlocked_module_ids = course_modules_list[:modules_to_view]
            print(unlocked_module_ids) '''
            unlocked_module_ids=give_unclocked_ids_list(course_modules_list,user_id)
            
            

            context={
                    'course':course,
                    'subtopics':subtopics,
                    'unlocked_module_ids':unlocked_module_ids
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
            print(keprice)
            
            request.session['keprice'] = keprice
            return render(request,"payment.html",{"usdprice":usdprice,"keprice":keprice})
    else:
        # If user_id is not in session redirect to login
        return redirect('/login')

def forgot_password(request):
    return render(request, 'forgot_password.html')

def user_login(request):
    return render(request, 'login.html')

def payment(request,id):
    user_id=request.session.get('user_id')
    request.session['course_id'] = id

    if user_id is not None:

        usdprice=Course.objects.get(id=id).price
        request.session['usdprice'] = usdprice
            #print(usdprice)
            #we have estimated 1 usd is 135 ke
        keprice=usdprice*135
        keprice=int(keprice)
        print(keprice)
            
        request.session['keprice'] = keprice
        return render(request,"payment.html",{"usdprice":usdprice,"keprice":keprice})
    else:
        return redirect("/login")

def user_register(request):
    return render(request, 'register.html')

def watchlist(request):
    print("watchlist called")
    # Get the user_id from the session
    user_id = request.session.get('user_id')
    if user_id is not None:
        
        #print(user_id)

        if user_id:
            # Retrieve all course_ids associated with the current user_id from PaidCourse
            paid_courses = PaidCourse.objects.filter(userId=user_id)
            #print(paid_courses.count())
            course_ids = [paid_course.courseId for paid_course in paid_courses]

            # Retrieve Course objects corresponding to the course_ids
            courses = Course.objects.filter(pk__in=course_ids)

            # Render the watchlist.html template with the filtered courses
            return render(request, 'watchlist.html', {'courses':courses})

        else:
            # Handle case where user_id is not found in the session
            return render(request, 'watchlist.html', {'courses': []})
    else:
        return redirect('/login')

def gallery(request):
    return render (request,'gallery.html')

def create_account(request):

    password1= request.POST.get('password', False)
    password2 = request.POST.get('confirm_password', False)
    email = request.POST.get('email', False)
    phone = request.POST.get('phone', False)
    username = request.POST.get('username', False)
    firstname = request.POST.get('firstname', False)
    secondname = request.POST.get('secondname', False)


    if  password1 != password2:
        message="the two passwords are diffrent."
        return render(request, "register.html", {"message": message})

        # Check if email and password are provided
    if not email or not password1:
        message="Email and password are required."
        return render(request, "register.html", {"message": message})

        # Check if user already exists
    if MofreyfxUsers.objects.filter(email=email).exists():
        
        message="User with this email already exists.."
        return render(request, "register.html", {"message": message})

        # Create user
    user = MofreyfxUsers.objects.create(email=email, password=password1,phone=phone,username=username,firstname=firstname,secondname=secondname)
    try:
        
        subject = 'Thank you'
        message = '''Thank you for signing up,
            Your Account is now active,
            To login, use:
            https://mofreydigiversity.com '''
  
        from_email = settings.EMAIL_HOST_USER   
        recipient_list = [email]
        print("sending email")
        try:
            send_mail(subject, message, from_email, recipient_list)
            return redirect("/login")
        except:
            return redirect("/login")
    
    except Exception as e:
        logging.error(f"Failed to send email. Error message: {str(e)}")
        return redirect("/register")
    

        # Respond with success message
    

def auth_login(request):
    email = request.POST.get('email',False)
    password = request.POST.get('password',False)

        # Check if an email and password are provided
    if not email or not password:
        
        message= "Email and password are required."
        return render(request, "login.html", {"message": message})

    try:
            # Check if user exists
        user = MofreyfxUsers.objects.get(email=email,password=password)
    except MofreyfxUsers.DoesNotExist:
        
        message= "User does not exist.You need to sign up please."
        return render(request, "login.html", {"message": message})

        # Check if password is correct
    if user.password != password:
        
        message= "You provided an incorrect password."
        return render(request, "login.html", {"message": message})

        # If everything is correct, respond with user details
    # Store the user ID in the session
    request.session['user_id'] = user.id
    print(user.id)
    return redirect('index')

def mpesa_checkout(request):
     #getting user id from session
    user_id=request.session.get('user_id')
    if user_id is not None:
        

        #getting saf number from form
        phone = request.POST.get('phone', False)
        #email of the user
        email = MofreyfxUsers.objects.get(id=user_id).email
        #cost of course
        amountkes = request.session.get('keprice')
        print(amountkes)
        courseid = request.session.get('course_id')
        #print(amount)
        if phone.startswith('0'):
                phone = '254' + phone[1:]
                print(phone)
                
        payment_instance=Payments.objects.create(mpesa_number=phone,email=email,amountkes=amountkes,courseId=courseid,userId=user_id)
        payment_instance.save()
        

        try:
                # Initialize the APIService
            token =os.getenv('token')
            publishable_key = os.getenv('publishable_key')
            service = APIService(token=token, publishable_key=publishable_key, test=False)

                # Trigger M-Pesa STK Push
            response = service.collect.mpesa_stk_push(phone_number=phone, email=email, amount=amountkes, narrative="mpesa payment")
            print(response)
            
            
            

                # Return the response from the M-Pesa STK Push
            return render(request,"loading.html")

        except Exception as e:
                # Return an error if there's an exception
            return render(request,"index.html",{"error": "try again later "})
    else:
        return redirect('/login')



def CardPayments(request):
    #getting user id from session
    user_id=request.session.get('user_id')
    if user_id is not None:
       

        #getting saf number from form
        #phone = request.POST.get('phone', False)
        #email of the user
        email = MofreyfxUsers.objects.get(id=user_id).email
        #cost of course
        amountusd = request.session.get('usdprice')
        courseid = request.session.get('course_id')
        
        
                
        payment_instance=Payments.objects.create(email=email,amountusd=amountusd,courseId=courseid,userId=user_id)
        payment_instance.save()
        

        
        try:
            publishable_key = os.getenv('publishable_key')
            
            token = os.getenv('token')
            
            service = APIService(token=token, publishable_key=publishable_key, test=False)

            response = service.collect.checkout(email=email, amount=amountusd, currency="USD", comment="Service Fees", redirect_url="https://mofreydigiversity.com/loading")
            url=response.get("url")
            print(url)
            
            return redirect(url)

        except:
            return redirect("/index")
    else:
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
        account = data["account"]  # Get the account information from data

        # Initialize phone and email variables with None
        phone = None
        email = None

        try:
            int_account = int(account)  # Try converting account to an integer
            phone = (int_account)    # Convert the integer to a character (assuming this is intended for phone number processing)
            print(phone)
        except ValueError:
            # If account is not an integer, treat it as an email
            email = account
            print(email)

        if phone is not None:
            # Process payments based on phone number
            try:
                payment_instance = Payments.objects.filter(mpesa_number=phone).latest('id')
                payment_instance.payment_status = 'completed'
                payment_instance.save()

                user_id = payment_instance.userId
                course_id = payment_instance.courseId

                paid_course_instance = PaidCourse.objects.create(userId=user_id, courseId=course_id)
                course_bought=Course.objects.get(id=course_id)
                email=MofreyfxUsers.objects.get(id=user_id).email
                subject = f"Thank you for buying {course_bought.course_name}"
            
                # Construct the message body with the course link
                message = f'''To view your purchased   courses, click the link below:
                
        https://mofreydigiversity.com/allcourses'''
        
                from_email = settings.EMAIL_HOST_USER
                recipient_list = [email]
                print("sending email")
                try:
                    send_mail(subject, message, from_email, recipient_list)
                    return JsonResponse({'message':'mpesa payment complete'})
                except:
                    return JsonResponse({'message':'mpesa payment complete'})
                

            except Payments.DoesNotExist:
                return JsonResponse({"message": "No payment found for this phone number."})

        elif email is not None:
            # Process payments based on email
            try:
                payment_instance = Payments.objects.filter(email=email).latest('id')
                payment_instance.payment_status = 'completed'
                payment_instance.payment_method = 'card'
                payment_instance.save()

                user_id = payment_instance.userId
                course_id = payment_instance.courseId

                paid_course_instance = PaidCourse.objects.create(userId=user_id, courseId=course_id)
                course_bought=Course.objects.get(id=course_id)
                subject = f"Thank you for purchasing {course_bought.course_name}"
            
                # Construct the message body with the course link
                message = f'''To view your purchased   courses, click the link below:
                    
            https://mofreydigiversity.com/allcourses/'''
        
                from_email = settings.EMAIL_HOST_USER   
                recipient_list = [email]
                print("sending email")
                try:
                    send_mail(subject, message, from_email, recipient_list)
                    return JsonResponse({'message':'mpesa payment complete'})
                except:
                    return JsonResponse({'message':'mpesa payment complete'})
                

            except Payments.DoesNotExist:
                return JsonResponse({"message": "No payment found for this email."})

        else:
            return JsonResponse({"message": "No email or phone provided."})

        
    else:
        return JsonResponse({"message": "Transaction state is not complete."})

def user_profile(request):
    print("starting")
    print("getting id")
    user_id=request.session.get('user_id')
    print(user_id)
    if user_id is not None:
    
       
        user_logged=MofreyfxUsers.objects.get(id=user_id)
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
    else:
        return redirect("/login")
    
    
def reset_password(request):
    email = request.POST.get('email',False)
    print(email)
    try:
        
        password=MofreyfxUsers.objects.get(email=email).password
        subject = 'Your password'
        message = '''Your password is {}.
        You can login now to Mofrey Markets.
        URL: https://mofreydigiversity.com/login.'''.format(password) 
        from_email = settings.EMAIL_HOST_USER   
        recipient_list = [email]
        print("sending email")
        send_mail(subject, message, from_email, recipient_list)
        print('email sent ')
        message="your password has been sent to your email"
        return render(request,"forgot_password.html",{"message":message})
    except Exception as e:
        logging.error(f"Failed to send email. Error message: {str(e)}")
        message='use the correct email'
        return render(request,"forgot_password.html",{"message":message})
    





def submit_quiz(request):
    if request.method == 'POST':
        # Initialize a list to store question responses
        question_responses = []

        # Iterate over the submitted POST data to capture question IDs and selected choices
        for key in request.POST:
            if key.startswith('question_') and key.endswith('_choice'):
                question_id = key.split('_')[1]  # Extract the question ID from the key
                selected_choice = request.POST[key]  # Get the selected choice ID

                # Append the question ID and selected choice ID as a tuple to question_responses
                question_responses.append((question_id, selected_choice))

        # Retrieve the IDs of questions that were part of the quiz
        question_ids = [question_id for question_id, selected_choice in question_responses]

        # Fetch only the relevant questions from the database based on the question IDs
        relevant_questions = Questions.objects.filter(id__in=question_ids)

        # Process each question response and calculate the score
        score = 0
        total_questions = len(question_responses)  # Total number of questions based on responses

        answer_details = []

        for question_id, selected_choice in question_responses:
            question = relevant_questions.get(id=question_id)

            # Determine if the selected choice is correct
            if selected_choice == str(question.correct_answer):
                score += 1

            # Retrieve the text of the correct choice
            correct_choice_text = getattr(question, f'choice{question.correct_answer}')

            # Append question details to answer_details list
            answer_details.append({
                'question_text': question.question_text,
                'selected_choice': selected_choice,
                'correct_choice': correct_choice_text
            })

        # Calculate percentage and failed questions
        percentage = int((score / total_questions) * 100)
        course_id=request.session.get("course_id")
        user_id=request.session.get("user_id")
        module_id=request.session.get("module_id")
        print("module id is ",module_id)
        if percentage >= 75:
            try:
                # Try to get an existing Marks object with the same userId and moduleId
                marks_obj = Marks.objects.get(userId=user_id, moduleId=module_id)
                
                # If the new percentage is higher, update the marks field
                if percentage > marks_obj.marks:
                    marks_obj.marks = percentage
                    marks_obj.save()
            except Marks.DoesNotExist:
                # If no Marks object exists, create a new one
                Marks.objects.create(userId=user_id, moduleId=module_id, marks=percentage, status=True)
        failed_questions = total_questions - score

        course_modules_list=get_module_ids_ordered_by_subtopics_and_date(course_id)
        print(course_modules_list)
        unlocked_module_ids=give_unclocked_ids_list(course_modules_list,user_id)
        position=course_modules_list.index(module_id)
        next_position=position+1

        #get the number of elements in course module list
        number_of_modules=len(course_modules_list)
        if next_position >= number_of_modules:
            next_module_id=None
        else:
            next_module_id=course_modules_list[next_position]


        # Prepare response data including questions and quiz results
        response_data = {
            'score': score,
            'total_questions': total_questions,
            'percentage': percentage,
            'failed_questions': failed_questions,
            'answer_details': answer_details,
            'module_id':module_id,
            'next_module_id':next_module_id,
            'unlocked_module_ids':unlocked_module_ids

        }

        # Render results.html with response_data
        return render(request, "results.html", {'data': response_data})

    # Handle other HTTP methods (e.g., GET) gracefully
    return JsonResponse({'error': 'Invalid request'}, status=400)




def logout(request):
    user_id=request.session.get('user_id')
    if user_id is  not None:
        del request.session['user_id']
        return redirect("/index")
    else:
        return redirect("/index")

    
def terms(request):
    return render (request,"terms.html")

from myapp.custom_fuctions import get_module_ids_ordered_by_subtopics_and_date
def module(request,id):
    request.session['module_id'] = id
    user_id = request.session.get('user_id')
    course_id=request.session.get('course_id')
    if user_id is not None:

    
        try:
            course_modules_list=get_module_ids_ordered_by_subtopics_and_date(course_id)
            print(course_modules_list)
            unlocked_module_ids=give_unclocked_ids_list(course_modules_list,user_id)
            if id not in unlocked_module_ids:
                return render(request,"module_error.html")

            else:
                pass
            print("module view running")
            
            module = Modules.objects.get(id=id)
            
            questions = Questions.objects.filter(module=id,course=course_id)
                # Create a list to store each question with its choices
            
            questions_with_choices = []
            for question in questions:
                    questions_with_choices.append({
                        'question': question,
                        'choices': question.get_choices()
                    })

            context = {
                    'questions_with_choices': questions_with_choices,
                    'module':module
                }
            return render(request, 'module.html', context)
            
        except :
            print("module view running")
            
            module = Modules.objects.get(id=id)
            
            questions = Questions.objects.filter(module=id,course=course_id)
                # Create a list to store each question with its choices
            
           

            context = {
                   
                    'module':module
                }
            return render(request, 'module.html', context)
    else:
        # If user_id is not in session redirect to login
        return redirect('/login')
    

import weasyprint
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from .models import Course, Marks, MofreyfxUsers

def download_certificate(request):
    # Check if user is logged in
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect("/login")

    # Check if user has finished all modules of the course
    course_id = request.session.get('course_id')
    course_modules_list = get_module_ids_ordered_by_subtopics_and_date(course_id)
    unlocked_module_ids = give_unclocked_ids_list(course_modules_list, user_id)
    last_course_module_id = unlocked_module_ids[-1]

    try:
        try:
            marks = Marks.objects.get(moduleId=last_course_module_id,userId=user_id).marks
        except:
            marks = Marks.objects.filter(moduleId=last_course_module_id,userId=user_id).latest('date')
            
    except Marks.DoesNotExist:
        marks = None

    if marks is None:
        return render(request,"cert_error.html")

    # Fetch course and user details
    course = Course.objects.get(id=course_id)
    course_name = course.course_name
    loggedin_user = MofreyfxUsers.objects.get(id=user_id)
    username = loggedin_user.username

    # Prepare data for rendering certificate template
    data = {
        'course_name': course_name,
        'username': username
    }

    # Render HTML template to string
    html_content = render_to_string('certificate.html', data)

    # Generate PDF from HTML content using WeasyPrint
    pdf_content = generate_pdf(html_content)

    # Return PDF as attachment
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="certificate.pdf"'
    return response

def generate_pdf(html_content):
    # Generate PDF from HTML content using WeasyPrint
    pdf = weasyprint.HTML(string=html_content).write_pdf()
    return pdf

def faqs(request):
    return render(request,'faqs.html')

def booking (request):
    phone = request.POST.get('phone',False)
    classbooked = request.POST.get('classbooked',False)
    name = request.POST.get('name',False)
    message = request.POST.get('message',False)
    sender=settings.EMAIL_HOST_USER
    recipients = ['mentorship@mofreyfx.com']
    subject="Thank you for booking "  + classbooked
    print(subject)
    message=f'{name} booked {classbooked}.\n\nPhone: {phone}\nMessage: {message}'
    
    

    try:
        send_mail(subject, message, sender, recipients)

        print('Your message has been sent successfully.')
        return redirect('/index')  # Redirect to a success page or some other page
    except Exception as e:
        print('An error occurred: {e}')
        return redirect('/index')
    
def loading(request):
    return render (request,"loading.html")

