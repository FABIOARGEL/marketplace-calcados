# Migration gerada manualmente para refletir as decisões de negócio:
# 1. email único em CustomUser (login por e-mail)
# 2. ordering de CustomUser alterado de ['username'] para ['email']
# 3. shipping_rate_per_km e shipping_distance_km em SellerProfile (frete simulado)
# 4. Novo modelo Address (múltiplos endereços por usuário)

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        # 1. Tornar email único no CustomUser (requisito de login por e-mail)
        migrations.AlterField(
            model_name='customuser',
            name='email',
            field=models.EmailField(
                error_messages={'unique': 'Já existe uma conta com este e-mail.'},
                help_text='Endereço de e-mail único. Utilizado como login.',
                max_length=254,
                unique=True,
                verbose_name='E-mail',
            ),
        ),
        # 2. Alterar ordering de CustomUser para email
        migrations.AlterModelOptions(
            name='customuser',
            options={
                'ordering': ['email'],
                'verbose_name': 'Usuário',
                'verbose_name_plural': 'Usuários',
            },
        ),
        # 3. Adicionar shipping_rate_per_km ao SellerProfile
        migrations.AddField(
            model_name='sellerprofile',
            name='shipping_rate_per_km',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text='Valor em reais cobrado por quilômetro para entrega. Fórmula: frete = distância × valor/km.',
                max_digits=6,
                verbose_name='Valor por km (R$)',
            ),
        ),
        # 4. Adicionar shipping_distance_km ao SellerProfile
        migrations.AddField(
            model_name='sellerprofile',
            name='shipping_distance_km',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text='Distância estimada em km informada pelo vendedor para cálculo do frete. SIMULAÇÃO: não há integração com API de mapas nesta versão.',
                max_digits=8,
                verbose_name='Distância de entrega (km)',
            ),
        ),
        # 5. Criar o modelo Address (múltiplos endereços por usuário)
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nickname', models.CharField(blank=True, help_text='Ex: Casa, Trabalho, Apartamento', max_length=100, verbose_name='Apelido')),
                ('recipient_name', models.CharField(help_text='Nome de quem receberá o pedido neste endereço.', max_length=200, verbose_name='Nome do destinatário')),
                ('zip_code', models.CharField(help_text='Formato: XXXXX-XXX', max_length=9, verbose_name='CEP')),
                ('street', models.CharField(max_length=300, verbose_name='Rua / Logradouro')),
                ('number', models.CharField(max_length=20, verbose_name='Número')),
                ('complement', models.CharField(blank=True, help_text='Ex: Apto 101, Bloco B', max_length=100, verbose_name='Complemento')),
                ('neighborhood', models.CharField(max_length=150, verbose_name='Bairro')),
                ('city', models.CharField(max_length=150, verbose_name='Cidade')),
                ('state', models.CharField(help_text='Sigla do estado. Ex: SP, RJ, MG', max_length=2, verbose_name='Estado (UF)')),
                ('reference', models.CharField(blank=True, help_text='Ex: Próximo ao mercado, Portão azul', max_length=300, verbose_name='Ponto de referência')),
                ('is_default', models.BooleanField(default=False, help_text='Se marcado, este endereço será pré-selecionado no checkout.', verbose_name='Endereço padrão')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='addresses',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Usuário',
                )),
            ],
            options={
                'verbose_name': 'Endereço',
                'verbose_name_plural': 'Endereços',
                'ordering': ['-is_default', '-created_at'],
            },
        ),
    ]
