import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.timezone import now
from datetime import timedelta
from .models import Book
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.http import HttpResponseNotAllowed, JsonResponse

User = get_user_model()  # Use the custom user model

# ----------SIGNUP VIEW --------------------

from django.shortcuts import render, redirect
from django.db import IntegrityError
from .models import CustomUser

def signup_view(request):
    error_message = None
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        semester = request.POST.get('semester')
        admission_number = request.POST.get('admission_number')
        department_name = request.POST.get('department_name')
        phone_number = request.POST.get('phone')

        try:
            # Create the user
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                role=role,
                semester=semester,
                admission_number=admission_number,
                department_name=department_name,
                phone_number=phone_number
            )
            user.save()
            return redirect('login_view')  # Redirect to login page after signup
        except IntegrityError:
            error_message = "Admission Number or Email already exists. Please try another."

    return render(request, 'signup.html', {'error_message': error_message})


# ----------Login VIEW --------------------
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from .models import CustomUser

User = get_user_model()

def login_view(request):
    error_message = None

    if request.method == "POST":
        role = request.POST.get('role')
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')

        # Attempt to find the user by username or email based on the input
        try:
            if '@' in username_or_email:
                # If the input contains '@', assume it's an email
                user = CustomUser.objects.get(email=username_or_email, role=role)
            else:
                # Otherwise, treat it as a username
                user = CustomUser.objects.get(username=username_or_email, role=role)

            # Check the password
            if user.check_password(password):
                login(request, user)  # Log the user in
                return redirect('home')  # Redirect to the home page
            else:
                error_message = "Invalid password. Please try again."
        except CustomUser.DoesNotExist:
            error_message = "No user found with the provided username/email and role."

    return render(request, 'login.html', {'error_message': error_message})

# ----------HOME VIEW --------------------
from django.shortcuts import render
from .models import Book, StudyMaterial

def home(request):
    query = request.GET.get('q', '').strip()  # Trim extra spaces
    filter_by = request.GET.get('filter_by', 'textbook_name')  # Default filter: textbook_name

    books = Book.objects.none()  # Default to empty queryset
    materials = StudyMaterial.objects.none()  # Default to empty queryset

    if query:  # Only filter when a query is provided
        if filter_by == 'textbook_name':
            books = Book.objects.filter(textbook_name__icontains=query)
            materials = StudyMaterial.objects.filter(subject__icontains=query)
        elif filter_by == 'author_name':
            books = Book.objects.filter(author_name__icontains=query)

        elif filter_by == 'subject':
            books = Book.objects.filter(subject__icontains=query)
            materials = StudyMaterial.objects.filter(subject__icontains=query)
        elif filter_by == 'semester':
            books = Book.objects.filter(semester=query)  # Assuming semester is a number
            materials = StudyMaterial.objects.filter(semester=query)

    context = {
        'books': books,
        'materials': materials,
        'query': query,
        'filter_by': filter_by,
    }
    return render(request, 'home.html', context)

# ----------Donation Dashboard VIEW --------------------

def donate_view(request):
    return render(request, 'donation_dashboard.html')  


# ----------Donate TextBook View ---------
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Book

@login_required
def donate_textbook(request):
    if request.method == "POST":
        textbook_name = request.POST.get('textbook_name')
        author_name = request.POST.get('author_name')
        subject = request.POST.get('subject')
        semester = request.POST.get('semester')
        feedback = request.POST.get('feedback', None)
        rating = request.POST.get('rating', None)
        image = request.FILES.get('image')

        if not all([textbook_name, author_name, subject, semester, image]):
            messages.error(request, "Please fill in all required fields.")
            return redirect('donate_textbook')

        # Create a new Book instance
        Book.objects.create(
            user=request.user,
            textbook_name=textbook_name,
            author_name=author_name,
            subject=subject,
            semester=semester,
            feedback=feedback,
            rating=rating,
            image=image
        )

        messages.success(request, "Thank you for donating your textbook!")
        return redirect("home")  # Redirect to the home page after donation

    return render(request, 'donate_textbook.html')

# ----------Book View ---------


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Book, DonationRequest
from datetime import datetime, timedelta

def get_next_working_days():
    """
    Returns the next 3 working days (Monday to Friday) as a list of strings in 'YYYY-MM-DD' format.
    """
    working_days = []
    current_date = datetime.today()
    while len(working_days) < 3:
        current_date += timedelta(days=1)
        if current_date.weekday() < 5:  # Monday to Friday
            working_days.append(current_date.strftime('%Y-%m-%d'))
    return working_days

@login_required
def book_detail(request, pk):
    """
    Displays the details of a book and handles the request submission.
    """
    book = get_object_or_404(Book, pk=pk)
    donor_name = book.user.get_full_name() if book.user else "Anonymous"
    dates = get_next_working_days()

    if request.method == "POST":
        # Get data from the form
        place = request.POST.get('place')
        time = request.POST.get('time')
        date = request.POST.get('date')

        # Validate form inputs
        if not place or not time or not date:
            messages.error(request, "Please fill in all fields.")
        elif date not in dates:
            messages.error(request, "Invalid date selected. Please choose a valid working day.")
        else:
            try:
                # Convert 12-hour format time (e.g., '10:50 AM') to 24-hour format
                time_24_hour = datetime.strptime(time, "%I:%M %p").time()

                # Create a new DonationRequest
                DonationRequest.objects.create(
                    book=book,
                    receiver=request.user,
                    donor=book.user,
                    donation_place=place,
                    donation_time=time_24_hour,
                    donation_date=date,
                    status="Pending",
                )

                messages.success(request, "Your request has been sent to the donor.")
                return redirect('book_detail', pk=pk)  # Redirect to the same page
            except ValueError:
                messages.error(request, "Invalid time format. Please enter the time in 'HH:MM AM/PM' format.")
            except Exception as e:
                messages.error(request, f"An error occurred: {e}")

    context = {
        'book': book,
        'donor_name': donor_name,
        'feedback': book.feedback,
        'rating': book.rating,
        'dates': dates,
    }
    return render(request, 'book_detail.html', context)


# ----------Notification View ---------


# ----------Request View ---------

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import DonationRequest, Notification

@login_required
def manage_requests(request):
    """
    Handles book requests for the logged-in donor and displays notifications.
    Allows the donor to accept or reject requests.
    """
    if request.method == "POST":
        # Get the request ID and action from the form
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')

        # Fetch the DonationRequest by ID
        donation_request = get_object_or_404(DonationRequest, id=request_id, donor=request.user, status="Pending")

        if action == "accept":
            donation_request.status = "Accepted"
            donation_request.save()

            # Create a notification for the receiver
            Notification.objects.create(
                receiver=donation_request.receiver,
                donor=donation_request.donor,
                book=donation_request.book,
                donation_request=donation_request,
                status="Accepted",
                message=(
                    f"Your request for '{donation_request.book.textbook_name}' "
                    f"has been accepted by {donation_request.donor.username}."
                ),
            )
            messages.success(request, f"You have accepted the request for {donation_request.book.textbook_name}.")

        elif action == "reject":
            donation_request.status = "Rejected"
            donation_request.save()

            # Create a notification for the receiver
            Notification.objects.create(
                receiver=donation_request.receiver,
                donor=donation_request.donor,
                book=donation_request.book,
                donation_request=donation_request,
                status="Rejected",
                message=(
                    f"Your request for '{donation_request.book.textbook_name}' "
                    f"has been rejected by {donation_request.donor.username}."
                ),
            )
            messages.warning(request, f"You have rejected the request for {donation_request.book.textbook_name}.")
        else:
            messages.error(request, "Invalid action. Please try again.")

        return redirect("manage_requests")  # Redirect to refresh the page

    # Fetch pending requests for the logged-in donor
    donation_requests = DonationRequest.objects.filter(donor=request.user, status="Pending").select_related("book", "receiver")

    # Fetch notifications for the logged-in donor
    notifications = Notification.objects.filter(donor=request.user).order_by("-created_at")

    context = {
        "donation_requests": donation_requests,  # Update variable name to match the template
        "notifications": notifications,  # Pass notifications to the template
    }
    return render(request, "manage_requests.html", context)

# ----------Userdashborad View ---------

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Book

def dashboard(request):
    user = request.user
    shared_books = Book.objects.filter(user=user)
    return render(request, 'dashboard.html', {'user': user, 'shared_books': shared_books})

@csrf_exempt
def update_profile(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user = request.user
        user.phone_number = data.get('phone')
        user.semester = data.get('semester')
        user.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)
# ----------SM detail View ---------

from django.shortcuts import render, get_object_or_404
from .models import StudyMaterial

def study_material_detail(request, material_id):
    # Fetch the specific study material by its ID or return a 404 error if not found
    material = get_object_or_404(StudyMaterial, pk=material_id)
    
    # Fetch uploader name if you have an uploader field (if it's a ForeignKey to User, for example)
    uploader_name = material.uploader.username if hasattr(material, 'uploader') and material.uploader else "Unknown"  # Modify based on your actual model structure

    context = {
        'material': material,
        'uploader_name': uploader_name,
    }
    return render(request, 'study_material_detail.html', context)



def alumni_chat_view(request):
    return render(request, 'home.html')  # Replace 'home.html' with your actual template

def receive_view(request):
    return render(request, 'home.html')  # Replace 'home.html' with your actual template

# ----------Donate SM View ---------

from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import StudyMaterial
from django.core.exceptions import ValidationError

def donate_study_material(request):
    if request.method == 'POST':
        # Handle form submission
        subject = request.POST.get('subject')
        module = request.POST.get('module')
        semester = request.POST.get('semester')
        description = request.POST.get('description')  # New field
        file = request.FILES.get('file')

        # Validate that all required fields are provided
        if not subject or not module or not semester or not description or not file:
            return HttpResponse("All fields are required.", status=400)

        # Validate that semester is a valid number (1-8)
        try:
            semester = int(semester)
            if semester < 1 or semester > 8:
                return HttpResponse("Semester must be between 1 and 8.", status=400)
        except ValueError:
            return HttpResponse("Semester must be a valid number.", status=400)

        # Check if file is of an allowed type
        allowed_file_types = ['.pdf', '.ppt', '.pptx', '.docx', '.txt']
        if not any(file.name.endswith(ext) for ext in allowed_file_types):
            return HttpResponse(f"Invalid file type. Only the following types are allowed: {', '.join(allowed_file_types)}.", status=400)

        # Save the study material
        try:
            study_material = StudyMaterial(
                subject=subject,
                module=module,
                semester=semester,
                description=description,  # Save description
                file=file
            )
            study_material.save()
            return redirect("home")  # Redirect to the home page after successful donation
        except ValidationError as e:
            return HttpResponse(f"Error: {e}", status=400)

    # Render the form
    return render(request, 'donate_study_material.html')

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Textbook

def sell_books(request):
    if request.method == "POST":
        textbook_name = request.POST.get("textbook_name")
        author_name = request.POST.get("author_name")
        subject = request.POST.get("subject")
        semester = request.POST.get("semester")
        price = request.POST.get("price")
        feedback = request.POST.get("feedback")
        rating = request.POST.get("rating")
        image = request.FILES.get("image")

        try:
            textbook = Textbook(
                name=textbook_name,
                author=author_name,
                subject=subject,
                semester=semester,
                price=price,
                feedback=feedback,
                rating=rating,
                image=image,
            )
            textbook.save()
            messages.success(request, "Your textbook has been successfully donated!")
            return redirect("home")  # Replace with your actual URL name
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

    return render(request, "sell_book.html")



# import requests
# from django.http import JsonResponse
# from django.shortcuts import render
# from django.conf import settings

# # OCR endpoint URL
# API_URL = 'https://api.ocr.space/parse/image'

# def ocr_view(request):
#     if request.method == 'POST':
#         file = request.FILES.get('file')
#         if not file:
#             return JsonResponse({'error': 'No file provided.'}, status=400)

#         # Prepare the payload for the OCR API
#         payload = {
#             'apikey': settings.OCR_API_KEY,  # Securely fetch API key from settings
#             'language': 'eng',  # Change to required language code if needed
#         }

#         files = {
#             'file': (file.name, file, file.content_type)
#         }

#         try:
#             # Send the request to OCR API
#             response = requests.post(API_URL, data=payload, files=files)
#             response.raise_for_status()  # Raise error for HTTP issues
#             result = response.json()

#             # Extract text from the API response
#             if 'ParsedResults' in result and result['ParsedResults']:
#                 extracted_text = result['ParsedResults'][0].get('ParsedText', '')
#                 return JsonResponse({'extracted_text': extracted_text})
#             else:
#                 return JsonResponse({'error': 'Text extraction failed.'}, status=400)
#         except requests.exceptions.RequestException as e:
#             return JsonResponse({'error': f'OCR API request failed: {str(e)}'}, status=500)

#     return render(request, 'ocr/upload.html')

# def upload(request):
#     return render(request, 'upload.html')