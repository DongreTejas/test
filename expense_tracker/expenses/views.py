from django.shortcuts import render,redirect,HttpResponse,get_object_or_404
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth import login,logout
from .middlewares import auth,guest
from expenses.models import Expense
from .forms import MyForm,UserRegistrationForm
from django.db.models import Sum,F
from django.utils.timezone import timedelta
from django.utils import timezone
@guest
def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'authentication/register.html', {'form': form})
@guest
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data = request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request,user)
            return redirect('dashboard')
    else:
        initial_data = {'username':'', 'password':''}
        form = AuthenticationForm(initial = initial_data)
    return render(request, 'authentication/login.html' ,{'form':form})
@auth # Only logged-in users can access
def dashboard_view(request):
    if request.method == 'POST':
        form = MyForm(request.POST)
        if form.is_valid():
            expense_id = request.POST.get('expense_id')
            delete_expense = request.POST.get('delete_expense')
            if delete_expense:
                # Delete the expense
                expense = get_object_or_404(Expense, id=delete_expense, user=request.user)
                expense.delete()
                return redirect('dashboard')
            elif expense_id:
                # Update existing expense
                expense = get_object_or_404(Expense, id=expense_id, user=request.user)
                expense.category = form.cleaned_data['category']
                expense.cost = form.cleaned_data['cost']
                expense.description = form.cleaned_data['description']
                expense.created_at = form.cleaned_data['created_at']
                expense.save()
            else:
                # Create new expense
                expense = Expense(
                    user=request.user,
                    category=form.cleaned_data['category'],
                    cost=form.cleaned_data['cost'],
                    description=form.cleaned_data['description'],
                    created_at=form.cleaned_data['created_at']
                )
                expense.save()
        return redirect('dashboard')
    else:
        form = MyForm()

    expenses = Expense.objects.filter(user=request.user).order_by(F('created_at').desc())
    total_expenses = expenses.aggregate(Sum('cost'))['cost__sum'] or 0
    total_expense_count = expenses.count()

    return render(request, 'dashboard.html', {'form': MyForm(), 'expenses': expenses, 'total_expenses': total_expenses, 'total_expense_count': total_expense_count })

def analytics_view(request):
    expenses = Expense.objects.filter(user=request.user)
    category_costs = expenses.values('category').annotate(total_cost=Sum('cost'))

    now = timezone.now().date()
    seven_days_ago = now - timedelta(days=6)
    last_7_days_expenses = expenses.filter(created_at__date__gte=seven_days_ago)

    # Initialize a dictionary for the last 7 days with 0 values
    daily_cost_dict = {seven_days_ago + timedelta(days=i): 0 for i in range(7)}

    # Query to get expenses summed by date
    daily_expenses = last_7_days_expenses.values('created_at__date').annotate(total_cost=Sum('cost')).order_by('created_at')

    # Update dictionary with actual expense values
    for daily in daily_expenses:
        daily_cost_dict[daily['created_at__date']] = daily['total_cost']

    # Create a list from the dictionary to pass to the template
    daily_costs = [{'date': date, 'total_cost': cost} for date, cost in daily_cost_dict.items()]

    context = {
        'expenses': expenses,
        'category_costs': category_costs,
        'daily_costs': daily_costs,
    }
    return render(request, 'analytics.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')



