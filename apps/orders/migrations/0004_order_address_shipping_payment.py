# Migration gerada manualmente para refletir as decisões de negócio:
# 1. FK shipping_address em Order (endereço de entrega selecionado no checkout)
# 2. subtotal em Order (valor dos produtos sem frete)
# 3. shipping_cost em Order (frete simulado, baseado em distância × taxa/km do vendedor)
# 4. payment_method em Order (método de pagamento SIMULADO)
# 5. payment_status em Order (status do pagamento SIMULADO)
#
# NOTA: O pagamento é apenas simulado para fins acadêmicos.
# Não há processamento financeiro real no sistema.

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_initial'),
        ('users', '0002_email_unique_address_shipping'),
    ]

    operations = [
        # 1. Adicionar FK para o endereço de entrega
        migrations.AddField(
            model_name='order',
            name='shipping_address',
            field=models.ForeignKey(
                blank=True,
                help_text='Endereço selecionado pelo cliente no checkout.',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='orders',
                to='users.address',
                verbose_name='Endereço de entrega',
            ),
        ),
        # 2. Adicionar subtotal (valor dos produtos sem frete)
        migrations.AddField(
            model_name='order',
            name='subtotal',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text='Valor dos produtos sem frete, calculado no momento do checkout.',
                max_digits=10,
                verbose_name='Subtotal',
            ),
        ),
        # 3. Adicionar shipping_cost (frete calculado — SIMULADO)
        migrations.AddField(
            model_name='order',
            name='shipping_cost',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text='Valor do frete calculado no checkout. SIMULADO: baseado na distância configurada pelo vendedor × taxa/km. Não há integração com API de logística real.',
                max_digits=10,
                verbose_name='Frete',
            ),
        ),
        # 4. Adicionar payment_method (SIMULADO — sem processamento real)
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(
                blank=True,
                choices=[
                    ('CREDIT_CARD_SIM', 'Cartão de Crédito (Simulado)'),
                    ('DEBIT_CARD_SIM', 'Cartão de Débito (Simulado)'),
                    ('PIX_SIM', 'PIX (Simulado)'),
                    ('BOLETO_SIM', 'Boleto Bancário (Simulado)'),
                ],
                help_text='SIMULADO — Nenhuma cobrança real é realizada. Campo para fins acadêmicos e de demonstração.',
                max_length=20,
                verbose_name='Método de pagamento',
            ),
        ),
        # 5. Adicionar payment_status (SIMULADO — sem processamento real)
        migrations.AddField(
            model_name='order',
            name='payment_status',
            field=models.CharField(
                choices=[
                    ('PENDING', 'Pagamento Pendente'),
                    ('APPROVED', 'Pagamento Aprovado (Simulado)'),
                    ('CANCELLED', 'Pagamento Cancelado'),
                ],
                default='PENDING',
                help_text='SIMULADO — Representa apenas o status fictício do pagamento. Nenhuma transação financeira real é processada.',
                max_length=20,
                verbose_name='Status do pagamento',
            ),
        ),
        # 6. Atualizar total — ajustar help_text para refletir subtotal + frete
        migrations.AlterField(
            model_name='order',
            name='total',
            field=models.DecimalField(
                decimal_places=2,
                help_text='Subtotal + frete, calculado no momento da finalização do pedido.',
                max_digits=10,
                verbose_name='Total',
            ),
        ),
    ]
