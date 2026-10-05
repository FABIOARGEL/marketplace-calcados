"""
Signals do app users.

Cria automaticamente um SellerProfile quando um usuário do tipo SELLER
é criado no sistema. Isso garante que todo vendedor tenha um perfil
associado desde o momento do cadastro.

O signal é registrado em apps.py via UsersConfig.ready().
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CustomUser, SellerProfile


@receiver(post_save, sender=CustomUser)
def create_seller_profile(sender, instance, created, **kwargs):
    """
    Cria SellerProfile automaticamente ao criar um usuário SELLER.

    Args:
        sender: classe CustomUser.
        instance: instância do usuário recém-salvo.
        created: True se o usuário acabou de ser criado.
    """
    if created and instance.user_type == CustomUser.UserType.SELLER:
        SellerProfile.objects.create(
            user=instance,
            store_name=f'Loja de {instance.first_name}',
        )
