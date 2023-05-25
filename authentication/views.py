from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from .serializers import UserSerializer, PasswordResetSerializer
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.core.mail import send_mail

User = get_user_model()


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def user_create(request):
    """
    Create a new user. It's an idempotent operation,
    if the user already exists then the request will fail.
    Required fields are: username, email, first_name, last_name, and password.

    Arguments:
    request: Django request object, should contain the user data.

    Returns:
    201 HTTP response with user data and tokens, if the operation was successful.
    400 HTTP response with error details, if the operation was unsuccessful.
    """
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        if user:
            json = serializer.data
            refresh = RefreshToken.for_user(user)
            json["refresh"] = str(refresh)
            json["access"] = str(refresh.access_token)
            return Response(json, status=201)
    return Response(serializer.errors, status=400)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def user_login(request):
    """
    Authenticate a user. Users can authenticate with either username or email.

    Arguments:
    request: Django request object, should contain username/email and password.

    Returns:
    200 HTTP response with refresh and access tokens, if the credentials were valid.
    400 HTTP response with error details, if the credentials were invalid.
    """
    username = request.data.get("username")
    password = request.data.get("password")

    if username is None or password is None:
        return Response(
            {"error": "Please provide both username/email and password"}, status=400
        )

    user = User.objects.filter(email=username).first()

    if user is None:
        user = User.objects.filter(username=username).first()

    if user is None:
        return Response({"error": "Invalid login credentials"}, status=400)

    if not user.check_password(password):
        return Response({"error": "Invalid login credentials"}, status=400)

    refresh = RefreshToken.for_user(user)
    data = {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }
    return Response(data, status=200)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def password_reset(request):
    serializer = PasswordResetSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data["email"]
        users = User.objects.filter(email=email)
        if users:
            for user in users:
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                current_site = get_current_site(request)
                mail_subject = "Reset your password"
                message = render_to_string(
                    "password_reset_email.html",
                    {
                        "user": user,
                        "domain": current_site.domain,
                        "uid": uid,
                        "token": token,
                    },
                )
                send_mail(
                    mail_subject,
                    message,
                    "admin@mywebsite.com",
                    [email],
                )
            return Response(
                {"detail": "Password reset e-mail has been sent."},
                status=200,
            )
        else:
            return Response(
                {"detail": "No user found with this email address."},
                status=400,
            )
    else:
        return Response(serializer.errors, status=400)
