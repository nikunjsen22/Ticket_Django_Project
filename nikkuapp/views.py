# views.py
import json
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .models import CustomUser, Ticket, Notification
from django.contrib.auth.hashers import make_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout


def land(request):
    return render(request, 'landingpage.html')
    
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            if user.role == 'admin':
                return redirect('admin_dashboard')
            elif user.role == 'customer':
                return redirect('customer_tickets')
            else:
                return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    
    return render(request, 'login.html')

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required
def create_ticket(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        priority = request.POST.get('priority')
        
        ticket = Ticket.objects.create(
            title=title,
            description=description,
            priority=priority,
            created_by=request.user
        )
        
        # Create notification for admins
        admins = CustomUser.objects.filter(role='admin')
        for admin in admins:
            Notification.objects.create(
                recipient=admin,
                ticket=ticket,
                notification_type='ticket_created',
                message=f'New ticket created: {ticket.title}'
            )
        
        return redirect('tickets')
    return render(request, 'create_ticket.html')

@login_required
def update_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        priority = request.POST.get('priority')
        status = request.POST.get('status')
        assigned_to_id = request.POST.get('assigned_to')
        
        # Check if assignment changed
        if assigned_to_id and int(assigned_to_id) != (ticket.assigned_to.id if ticket.assigned_to else 0):
            assigned_to = CustomUser.objects.get(id=assigned_to_id)
            ticket.assigned_to = assigned_to
            # Create notification for assigned user
            Notification.objects.create(
                recipient=assigned_to,
                ticket=ticket,
                notification_type='ticket_assigned',
                message=f'You have been assigned to ticket: {ticket.title}'
            )
        
        # Check if status changed
        if status != ticket.status:
            ticket.status = status
            if status == 'resolved':
                # Create notification for ticket creator
                Notification.objects.create(
                    recipient=ticket.created_by,
                    ticket=ticket,
                    notification_type='ticket_resolved',
                    message=f'Your ticket has been resolved: {ticket.title}'
                )
        
        ticket.title = title
        ticket.description = description
        ticket.priority = priority
        ticket.save()
        
        # Create notification for ticket creator about update
        if request.user != ticket.created_by:
            Notification.objects.create(
                recipient=ticket.created_by,
                ticket=ticket,
                notification_type='ticket_updated',
                message=f'Your ticket has been updated: {ticket.title}'
            )
        
        return redirect('tickets')
    
    return render(request, 'update_ticket.html', {'ticket': ticket})

@csrf_exempt
def signup(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            full_name = data.get('full_name')
            email = data.get('email')
            password = data.get('password')
            confirm_password = data.get('confirm_password')
            mobile = data.get('mobile')
            role = data.get('role')

            if not all([full_name, email, password, confirm_password, role]):
                return JsonResponse({'error': 'All fields are required'}, status=400)

            # Mobile is not required
            if mobile is None:
                mobile = ""

            try:
                validate_email(email)
            except ValidationError:
                return JsonResponse({'error': 'Invalid email format'}, status=400)

            if password != confirm_password:
                return JsonResponse({'error': 'Passwords do not match'}, status=400)

            if CustomUser.objects.filter(email=email).exists():
                return JsonResponse({'error': 'Email already exists'}, status=400)

            try:
                hashed_password = make_password(password)
                user = CustomUser(
                    username=email,  # Set username same as email
                    email=email,
                    full_name=full_name,
                    password=hashed_password,
                    mobile=mobile,
                    role=role
                )
                user.save()
                return JsonResponse({'message': 'User registered successfully'}, status=201)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    else:
        # Handle GET request - render the signup page
        return render(request, 'sign-up-page.html')

@login_required
def tickets(request):
    tickets = Ticket.objects.all().order_by('-created_at')
    return render(request, 'tickets.html', {'tickets': tickets})

@login_required
def reports(request):
    # Get date range from request
    date_range = request.GET.get('date_range', 'month')
    
    # Base queryset
    tickets = Ticket.objects.all()
    
    # Apply date filter
    from datetime import datetime, timedelta
    now = datetime.now()
    
    if date_range == 'today':
        tickets = tickets.filter(created_at__date=now.date())
    elif date_range == 'week':
        start_date = now - timedelta(days=now.weekday())
        tickets = tickets.filter(created_at__date__gte=start_date.date())
    elif date_range == 'month':
        tickets = tickets.filter(created_at__month=now.month, created_at__year=now.year)
    elif date_range == 'quarter':
        quarter_start = now.replace(day=1, month=((now.month-1)//3)*3+1)
        tickets = tickets.filter(created_at__gte=quarter_start)
    elif date_range == 'year':
        tickets = tickets.filter(created_at__year=now.year)
    
    # Calculate metrics
    total_tickets = tickets.count()
    
    # Calculate average response time (time between ticket creation and first response)
    response_times = []
    for ticket in tickets:
        if ticket.assigned_to and ticket.updated_at:
            response_time = ticket.updated_at - ticket.created_at
            response_times.append(response_time.total_seconds() / 3600)  # Convert to hours
    
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    # Calculate resolution rate
    resolved_tickets = tickets.filter(status__in=['resolved', 'closed']).count()
    resolution_rate = (resolved_tickets / total_tickets * 100) if total_tickets > 0 else 0
    
    # Get ticket volume over time (last 6 months)
    from django.db.models import Count
    from django.db.models.functions import TruncMonth
    
    # Calculate the date 6 months ago
    six_months_ago = datetime.now() - timedelta(days=180)
    
    monthly_volume = Ticket.objects.filter(
        created_at__gte=six_months_ago
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    # Get priority distribution instead of category
    priority_distribution = tickets.values('priority').annotate(
        count=Count('id')
    ).order_by('-count')
    
    context = {
        'total_tickets': total_tickets,
        'avg_response_time': round(avg_response_time, 1),
        'resolution_rate': round(resolution_rate, 1),
        'monthly_volume': list(monthly_volume),
        'category_distribution': list(priority_distribution),  # Using priority distribution instead
        'date_range': date_range,
    }
    
    return render(request, 'reports.html', context)

@login_required
def customers(request):
    customers = CustomUser.objects.filter(role='customer')
    return render(request, 'customers.html', {'customers': customers})

@login_required
def settings(request):
    return render(request, 'settings.html')

@login_required
def help_center(request):
    return render(request, 'help_center.html')

@login_required
def logout_view(request):
    auth_logout(request)
    return redirect('landing_page')

@login_required
def get_notifications(request):
    notifications = Notification.objects.filter(recipient=request.user, is_read=False)
    return JsonResponse({
        'notifications': list(notifications.values('id', 'notification_type', 'message', 'created_at', 'ticket_id')),
        'unread_count': notifications.count()
    })

@login_required
def mark_notification_read(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id, recipient=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'status': 'success'})
    except Notification.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Notification not found'}, status=404)

@login_required
def mark_all_notifications_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'success'})

@login_required
def admin_dashboard(request):
    # Check if user is admin
    if request.user.role != 'admin':
        return redirect('dashboard')
    
    # Get statistics
    total_users = CustomUser.objects.count()
    active_agents = CustomUser.objects.filter(role='agent', is_active=True).count()
    total_customers = CustomUser.objects.filter(role='customer').count()
    open_tickets = Ticket.objects.filter(status__in=['open', 'in_progress']).count()
    
    # Get agents and customers
    agents = CustomUser.objects.filter(role='agent')
    customers = CustomUser.objects.filter(role='customer')
    
    context = {
        'total_users': total_users,
        'active_agents': active_agents,
        'total_customers': total_customers,
        'open_tickets': open_tickets,
        'agents': agents,
        'customers': customers,
    }
    
    return render(request, 'admin_dashboard.html', context)

@login_required
def customer_tickets(request):
    if request.user.role != 'customer':
        return redirect('dashboard')
    
    tickets = Ticket.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, 'customer_tickets.html', {'tickets': tickets})
