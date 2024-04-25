
from django.http import response
from django.shortcuts import render,get_object_or_404,redirect
import requests
from myapp.models import Course,PaidCourse,MofreyfxUsers,Payments,Questions
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

def course(request,id):
    #store course id
    request.session['course_id'] = id
    user_id = request.session.get('user_id')
    if user_id is not None:

    
        try:
            # Check if the user has paid for the specified course
            paid_courses = PaidCourse.objects.filter(userId=user_id, courseId=id).order_by('-date')  
            if paid_courses.exists():
                paid_course = paid_courses.last()

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
            else:
                return redirect("/index")


            
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
    user = MofreyfxUsers.objects.create(email=email, password=password1,phone=phone,username=username)
    try:
        
        subject = 'Thank you'
        message = '''Thank you for signing up,
            Your Account is now active,
            To login, use:
            https://mofrey.up.railway.app.'''
  
        from_email = settings.EMAIL_HOST_USER   
        recipient_list = [email]
        print("sending email")
        send_mail(subject, message, from_email, recipient_list)
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
            token = "ISSecretKey_live_0bcbeaa2-f210-476b-9bfa-28fae2ee5c0a"
            publishable_key = "ISPubKey_live_ee33ed45-3f7e-46ce-a6a4-d91fae6de1de"
            service = APIService(token=token, publishable_key=publishable_key, test=False)

                # Trigger M-Pesa STK Push
            response = service.collect.mpesa_stk_push(phone_number=phone, email=email, amount=amountkes, narrative="mpesa payment")
            print(response)
            #pass the course details in email
            
            course_bought=Course.objects.get(id=courseid)
            subject = f"Thank you for buying {course_bought.name}"
        
            # Construct the message body with the course link
            message = f'''To view your purchased   courses, click the link below:
            
    https://mofrey.up.railway.app/allcourses'''
    
            from_email = settings.EMAIL_HOST_USER   
            recipient_list = [email]
            print("sending email")
            send_mail(subject, message, from_email, recipient_list)

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
            publishable_key = "ISPubKey_live_ee33ed45-3f7e-46ce-a6a4-d91fae6de1de"
            service = APIService(token="ISSecretKey_live_0bcbeaa2-f210-476b-9bfa-28fae2ee5c0a", publishable_key=publishable_key, test=False)

            response = service.collect.checkout(email=email, amount=amountusd, currency="USD", comment="Service Fees", redirect_url="http://example.com/thank-you")
            url=response.get("url")
            course_bought=Course.objects.get(id=courseid)
            subject = f"Thank you for purchasing {course_bought.name}"
        
            # Construct the message body with the course link
            message = f'''To view your purchased   courses, click the link below:
                
        https://mofrey.up.railway.app/allcourses/'''
    
            from_email = settings.EMAIL_HOST_USER   
            recipient_list = [email]
            print("sending email")
            send_mail(subject, message, from_email, recipient_list)
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
        URL: https://mofrey.up.railway.app/login.'''.format(password) 
        from_email = settings.EMAIL_HOST_USER   
        recipient_list = [email]
        print("sending email")
        send_mail(subject, message, from_email, recipient_list)
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
        failed_questions = total_questions - score

        # Prepare response data including questions and quiz results
        response_data = {
            'score': score,
            'total_questions': total_questions,
            'percentage': percentage,
            'failed_questions': failed_questions,
            'answer_details': answer_details
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
  

