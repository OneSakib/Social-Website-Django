from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Q
from django.shortcuts import render, HttpResponse, HttpResponseRedirect, get_object_or_404
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.mail import send_mail, BadHeaderError
from .forms import LoginForm, PasswordChange, UserRegistrationForm, UserEditForm, ProfileEditForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Profile
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from common.decorators import ajax_required
from .models import Contact
from django.views.decorators.csrf import csrf_protect, csrf_exempt, ensure_csrf_cookie
from actions.utils import create_action
from actions.models import Action


# Create your views here.
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, 'Successfully Login')
                    return render(request, 'account/register_done.html')
                else:
                    messages.error(request, 'Disabled Account')
                    return HttpResponse("Disabled Account")
            else:
                messages.error(request, 'Invalid Login ')
                return HttpResponse('Invalid Login')
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})


@login_required(login_url='account:login')
def dashboard(request):
    # Display all actions by default
    actions = Action.objects.exclude(user=request.user)

    following_ids = request.user.following.values_list('id', flat=True)
    if following_ids:
        actions = actions.filter(user_id__in=following_ids)
    actions = actions.select_related('user', 'user__profile').prefetch_related('target')[:10]
    # for action in actions:
    #     print(action.target)
    return render(request, 'account/dashboard.html', {'section': 'dashboard', 'actions': actions})


@login_required
def password_change(request):
    if request.method == 'POST':
        form = PasswordChange(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Successfully Password Changed')
            return render(request, 'account/password_change_done.html')
    else:
        form = PasswordChange(request.user)

    return render(request, 'account/password_change.html', {'form': form})


def password_change_done(request):
    messages.success(request, 'Password Changed Done')
    return render(request, 'account/password_change_done.html')


def password_reset_request(request):
    if request.method == 'POST':
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            assoicated_users = User.objects.filter(Q(email=data))

            if assoicated_users.exists():
                for user in assoicated_users:
                    subject = "Password Reset Form "
                    email_template_name = 'password_reset_email.txt'
                    c = {
                        "email": user.email,
                        "domain": '127.0.0.1:8000',
                        "site_name": "Website",
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        "token": default_token_generator.make_token(user),
                        "protocol": 'http'
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, 'malikgovind348@gmail.com', [user.email], fail_silently=False)
                        messages.success(request, 'Email successfully send your email id check and reset password')

                    except BaseException:
                        messages.error(request, 'invalid Url Header')
                        return HttpResponse('Invalid Header found')
                    messages.success(request, "Password Reset Done")
                    return HttpResponseRedirect('/password_reset/done')

    password_reset_form = PasswordResetForm()
    return render(request, 'account/password_reset.html', context={'form': password_reset_form})


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(
                user_form.cleaned_data['password']
            )
            new_user.save()
            Profile.objects.create(user=new_user)
            create_action(new_user, 'has Created an account')

            messages.success(request, "Register Successfully You can login now ")
            return HttpResponseRedirect(reverse('account:login'))
    else:
        user_form = UserRegistrationForm()
    return render(request, 'account/register.html', {'user_form': user_form})


@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your Profile Successfully Modify')
            return HttpResponseRedirect(reverse('account:dashboard'))
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    return render(request, 'account/edit.html', {'user_form': user_form, 'profile_form': profile_form})


@login_required
def user_list(request):
    users = User.objects.filter(is_active=True)
    return render(request, 'account/user/list.html', {'section': 'people', 'users': users})


@login_required
def user_detail(request, username):
    user = get_object_or_404(User, username=username, is_active=True)
    return render(request, 'account/user/detail.html', {'section': 'people', 'user': user})


# @ajax_required
# @require_POST
# @require_POST
# @login_required

@csrf_exempt
def user_follow(request):
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    if user_id and action:
        try:
            user = User.objects.get(id=user_id)
            if action == 'follow':
                Contact.objects.get_or_create(user_from=request.user, user_to=user)
                create_action(request.user, 'is following', user)
            else:
                Contact.objects.filter(user_from=request.user, user_to=user).delete()
            return JsonResponse({'status': 'ok'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'ok'})
