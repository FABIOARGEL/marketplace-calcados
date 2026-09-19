"""
Backend de autenticação por e-mail para o marketplace de calçados.

O Django usa por padrão o campo `username` para autenticação.
Este backend substitui esse comportamento, permitindo que o usuário
faça login com seu e-mail e senha.

Registro em settings.py:
    AUTHENTICATION_BACKENDS = [
        'apps.users.backends.EmailBackend',
        'django.contrib.auth.backends.ModelBackend',
    ]

O ModelBackend é mantido como fallback para que o painel admin
continue funcionando com superusuários criados via createsuperuser.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailBackend(ModelBackend):
    """
    Backend de autenticação por e-mail.

    Autentica o usuário usando e-mail e senha em vez de username e senha.
    Case-insensitive para o e-mail (normalizado para minúsculas).
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Autentica usando e-mail como identificador.

        Args:
            request: objeto HttpRequest atual.
            username: aceita e-mail no campo username do formulário padrão.
            password: senha do usuário.

        Returns:
            CustomUser autenticado ou None se as credenciais forem inválidas.
        """
        User = get_user_model()

        if username is None or password is None:
            return None

        try:
            # Busca pelo e-mail (case-insensitive)
            user = User.objects.get(email__iexact=username)
        except User.DoesNotExist:
            # Executa verificação de senha mesmo sem usuário para evitar
            # ataques de timing (timing attack mitigation)
            User().set_password(password)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None
