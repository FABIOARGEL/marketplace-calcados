"""
Modelos do app users.

CustomUser:
    Extende AbstractUser do Django adicionando o campo `user_type`.
    Distingue entre CLIENTE e VENDEDOR no nível do modelo de usuário.
    Autenticação realizada via e-mail (USERNAME_FIELD = 'email').
    O campo `username` é mantido pelo AbstractUser e preenchido automaticamente
    a partir do e-mail durante o cadastro (transparente ao usuário).

SellerProfile:
    Armazena dados extras do vendedor (nome da loja, CNPJ, descrição).
    Inclui configuração de frete por quilômetro definida pelo vendedor.
    Criado automaticamente via signal quando user_type = SELLER.

Address:
    Endereço de entrega do usuário.
    Um usuário pode ter múltiplos endereços cadastrados.
    O checkout utiliza um dos endereços cadastrados.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """
    Usuário customizado do marketplace.

    Herda todos os campos padrão do AbstractUser e adiciona
    o campo `user_type` para distinguir clientes de vendedores.

    O login é realizado por e-mail (USERNAME_FIELD = 'email').
    O campo `username` permanece no banco de dados por exigência do
    AbstractUser, mas é preenchido automaticamente durante o cadastro
    e não é exposto nos formulários públicos.
    """

    class UserType(models.TextChoices):
        CLIENT = 'CLIENT', _('Cliente')
        SELLER = 'SELLER', _('Vendedor')

    # E-mail obrigatório e único — identificador principal de login
    email = models.EmailField(
        unique=True,
        verbose_name=_('E-mail'),
        help_text=_('Endereço de e-mail único. Utilizado como login.'),
        error_messages={
            'unique': _('Já existe uma conta com este e-mail.'),
        },
    )

    user_type = models.CharField(
        max_length=10,
        choices=UserType.choices,
        default=UserType.CLIENT,
        verbose_name=_('Tipo de usuário'),
        help_text=_('Define se o usuário é um cliente ou vendedor.'),
    )

    # Login por e-mail
    USERNAME_FIELD = 'email'
    # Campos solicitados pelo createsuperuser (além do email e senha)
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = _('Usuário')
        verbose_name_plural = _('Usuários')
        ordering = ['email']

    def __str__(self):
        return f'{self.email} ({self.get_user_type_display()})'

    def save(self, *args, **kwargs):
        """
        Garante que o campo username seja preenchido automaticamente
        a partir do e-mail, mantendo compatibilidade com o AbstractUser.
        O username não é exposto aos usuários finais.
        """
        if not self.username:
            # Gera username a partir da parte local do e-mail
            base = self.email.split('@')[0] if self.email else 'usuario'
            username = base
            counter = 1
            while CustomUser.objects.filter(username=username).exists():
                username = f'{base}{counter}'
                counter += 1
            self.username = username
        super().save(*args, **kwargs)

    @property
    def is_seller(self):
        """Retorna True se o usuário for um vendedor."""
        return self.user_type == self.UserType.SELLER

    @property
    def is_client(self):
        """Retorna True se o usuário for um cliente."""
        return self.user_type == self.UserType.CLIENT

    @property
    def full_name(self):
        """Retorna o nome completo do usuário."""
        return f'{self.first_name} {self.last_name}'.strip() or self.email


class SellerProfile(models.Model):
    """
    Perfil estendido do vendedor.

    Relacionamento 1:1 com CustomUser.
    Armazena dados específicos do vendedor que não pertencem ao usuário base.

    Configuração de frete:
        shipping_rate_per_km: valor em R$ cobrado por quilômetro percorrido.
        shipping_distance_km: distância em km configurada pelo vendedor para
            cálculo do frete de entrega. Representa a distância estimada entre
            a loja e a área de entrega padrão.

    NOTA: O cálculo de frete é simulado. Não há integração com API de mapas
    ou geolocalização nesta versão. A distância é informada pelo vendedor.
    Fórmula: frete = shipping_distance_km × shipping_rate_per_km
    """

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='seller_profile',
        verbose_name=_('Usuário'),
        limit_choices_to={'user_type': CustomUser.UserType.SELLER},
    )
    store_name = models.CharField(
        max_length=150,
        verbose_name=_('Nome da loja'),
    )
    cnpj = models.CharField(
        max_length=18,
        blank=True,
        verbose_name=_('CNPJ'),
        help_text=_('Formato: XX.XXX.XXX/XXXX-XX'),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Descrição da loja'),
    )

    # --- Configuração de frete (definida pelo vendedor) ---
    shipping_rate_per_km = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        verbose_name=_('Valor por km (R$)'),
        help_text=_(
            'Valor em reais cobrado por quilômetro para entrega. '
            'Fórmula: frete = distância × valor/km.'
        ),
    )
    shipping_distance_km = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        verbose_name=_('Distância de entrega (km)'),
        help_text=_(
            'Distância estimada em km informada pelo vendedor para cálculo do frete. '
            'SIMULAÇÃO: não há integração com API de mapas nesta versão.'
        ),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Ativo'),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Criado em'),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Atualizado em'),
    )

    class Meta:
        verbose_name = _('Perfil do vendedor')
        verbose_name_plural = _('Perfis dos vendedores')
        ordering = ['store_name']

    def __str__(self):
        return self.store_name

    def calculate_shipping(self):
        """
        Calcula o valor do frete com base na distância e taxa por km configuradas.

        Retorna:
            Decimal: valor do frete calculado.
                     Retorna 0 se qualquer um dos valores for zero.

        NOTA: Este cálculo é simulado. A distância é informada pelo próprio
        vendedor no perfil da loja. Não há processamento de geolocalização real.
        Fórmula: frete = shipping_distance_km × shipping_rate_per_km
        """
        return self.shipping_distance_km * self.shipping_rate_per_km


class Address(models.Model):
    """
    Endereço de entrega do usuário (RF22, RF23).

    Um usuário pode possuir múltiplos endereços cadastrados.
    O checkout utiliza um dos endereços existentes escolhido pelo comprador.
    """

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='addresses',
        verbose_name=_('Usuário'),
    )
    nickname = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Apelido'),
        help_text=_('Ex: Casa, Trabalho, Apartamento'),
    )
    recipient_name = models.CharField(
        max_length=200,
        verbose_name=_('Nome do destinatário'),
        help_text=_('Nome de quem receberá o pedido neste endereço.'),
    )
    zip_code = models.CharField(
        max_length=9,
        verbose_name=_('CEP'),
        help_text=_('Formato: XXXXX-XXX'),
    )
    street = models.CharField(
        max_length=300,
        verbose_name=_('Rua / Logradouro'),
    )
    number = models.CharField(
        max_length=20,
        verbose_name=_('Número'),
    )
    complement = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Complemento'),
        help_text=_('Ex: Apto 101, Bloco B'),
    )
    neighborhood = models.CharField(
        max_length=150,
        verbose_name=_('Bairro'),
    )
    city = models.CharField(
        max_length=150,
        verbose_name=_('Cidade'),
    )
    state = models.CharField(
        max_length=2,
        verbose_name=_('Estado (UF)'),
        help_text=_('Sigla do estado. Ex: SP, RJ, MG'),
    )
    reference = models.CharField(
        max_length=300,
        blank=True,
        verbose_name=_('Ponto de referência'),
        help_text=_('Ex: Próximo ao mercado, Portão azul'),
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name=_('Endereço padrão'),
        help_text=_('Se marcado, este endereço será pré-selecionado no checkout.'),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Criado em'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Atualizado em'))

    class Meta:
        verbose_name = _('Endereço')
        verbose_name_plural = _('Endereços')
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        label = f' ({self.nickname})' if self.nickname else ''
        return f'{self.street}, {self.number} — {self.city}/{self.state}{label}'

    def full_address(self):
        """Retorna o endereço completo formatado em uma linha."""
        parts = [
            f'{self.street}, {self.number}',
            self.complement,
            self.neighborhood,
            f'{self.city}/{self.state}',
            f'CEP {self.zip_code}',
        ]
        return ' — '.join(p for p in parts if p)
