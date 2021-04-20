from django.views import View
from accounts.forms import SignupUserForm, SignupStaffForm
from django.shortcuts import render, redirect
from allauth.account import views
from django.views.generic.edit import FormView

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import BadHeaderError, send_mail, EmailMessage
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.http import Http404, HttpResponseBadRequest, HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse

User = get_user_model()


class SignupCompleteView(View):
    def get(self, request, *args, **kwargs):
        # 有効期限1日
        timeout_seconds = getattr(
            settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*60*24)
        # tokenが正しければ本登録
        token = kwargs.get('token')
        try:
            user_pk = loads(token, max_age=timeout_seconds)

        # 期限切れの場合
        except SignatureExpired:
            return HttpResponseBadRequest()

        # tokenが間違っている場合
        except BadSignature:
            return HttpResponseBadRequest()

        # tokenは問題ない場合
        else:
            try:
                user = User.objects.get(pk=user_pk)
            # ユーザーが存在しない場合
            except User.DoesNotExist:
                return HttpResponseBadRequest()
            else:
                if not user.is_active:
                    # 問題なければ本登録
                    user.is_active = True
                    user.save()

        return render(request, 'accounts/signup_complete.html')


class SignupDoneView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'accounts/signup_done.html')

    def post(self, request, *args, **kwargs):
        user = User()
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.address = request.POST.get('address')
        user.set_password(request.POST.get('password'))
        user.is_active = False
        user.save()

        domain = 'localhost:8000'
        context = {
            'protocol': self.request.scheme,
            'domain': domain,
            'token': dumps(user.pk),
            'user': user,
        }

        subject = render_to_string(
            'accounts/mail_template/signup_subject.txt', context)
        message = render_to_string(
            'accounts/mail_template/signup_message.txt', context)

        try:
            user.email_user(subject, message)
        except BadHeaderError:
            return HttpResponse("無効なヘッダが検出されました。")

        return JsonResponse({'data': 'data'})


class SignupConfirmView(View):
    def post(self, request, *args, **kwargs):
        form = SignupUserForm(request.POST or None)

        email = form.data['email']
        User.objects.filter(email=email, is_active=False).delete()

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            address = form.cleaned_data['address']
            password = form.cleaned_data['password1']

            return render(request, 'accounts/signup_confirm.html', {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'address': address,
                'password': password,
            })

        return render(request, 'accounts/signup.html', {
            'form': form,
        })


class SignupView(views.SignupView):
    template_name = 'accounts/signup.html'
    form_class = SignupUserForm

    def get_context_data(self, **kwargs):
        context = super(SignupView, self).get_context_data(**kwargs)
        return context

class StaffSignupView(views.SignupView):
    template_name = 'accounts/staff_signup.html'
    form_class = SignupStaffForm

    def dispatch(self, request, *args, **kwargs):
        response = super(FormView, self).dispatch(request, *args, **kwargs)
        return response

    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect('/')
        form = SignupStaffForm(request.POST or None)
        return render(request, 'accounts/staff_signup.html', {
            'form': form
        })


class LoginView(views.LoginView):
    template_name = 'accounts/login.html'


class LogoutView(views.LogoutView):
    template_name = 'accounts/logout.html'

    def post(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            self.logout()
        return redirect('/')

