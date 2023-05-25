from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from .serializers import (
    UserSerializer,
    PasswordResetSerializer,
    PasswordChangeSerializer,
)
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes

# This will use to generate Email with token
# from django.core.mail import send_mail

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
        if user := serializer.save():
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
    """
    Handle the password reset request. The function generates a password reset token for the user.

    Arguments:
    request: Django request object, should contain the user's email.

    Returns:
    200 HTTP response with a message stating that the password reset token has been generated, if the email was valid and associated with a user.
    400 HTTP response with an error message stating that no user was found with this email address, if the email was invalid or not associated with a user.
    """
    serializer = PasswordResetSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)
    email = serializer.validated_data["email"]
    if user := User.objects.filter(email=email).first():
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        return Response(
            {"detail": "Password reset token has been generated."},
            status=200,
        )
    else:
        return Response(
            {"detail": "No user found with this email address."},
            status=400,
        )


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def password_change(request):
    """
    Handle the password change request. The function validates the token and changes the user's password if the new password and new password confirmation match.

    Arguments:
    request: Django request object, should contain the user's email, the password reset token, the new password, and the new password confirmation.

    Returns:
    200 HTTP response with a message stating that the password has been reset, if the token, email, new password and new password confirmation were valid.
    400 HTTP response with an error message, if the token or email was invalid, or the new password and new password confirmation did not match.
    """
    serializer = PasswordChangeSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)
    email = serializer.validated_data["email"]
    token = serializer.validated_data["token"]
    new_password = serializer.validated_data["new_password"]
    confirm_new_password = serializer.validated_data["confirm_new_password"]

    user = User.objects.filter(email=email).first()

    if user and default_token_generator.check_token(user, token):
        if new_password == confirm_new_password:
            user.set_password(new_password)
            user.save()
            return Response({"detail": "Password has been reset."}, status=200)
        else:
            return Response(
                {"detail": "New password and confirm new password do not match."},
                status=400,
            )
    else:
        return Response({"detail": "Invalid token or email."}, status=400)
