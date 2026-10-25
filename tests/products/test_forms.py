"""
Testes unitários para os formulários do app products.

Cobre:
    ProductForm:
        - Formulário válido com todos os campos obrigatórios
        - Preço zero é rejeitado (clean_price)
        - Preço negativo é rejeitado (clean_price)
        - Preço positivo válido é aceito
        - Nome vazio é rejeitado
        - Descrição vazia é rejeitada
        - Marca vazia é rejeitada
        - Categoria é opcional
        - Preço com casas decimais é aceito

Executável via:
    python manage.py test tests.products
    python manage.py test tests.products.test_forms
"""

from decimal import Decimal

from django.test import TestCase

from apps.products.forms import ProductForm
from apps.products.models import Category


class ProductFormValidoTest(TestCase):
    """Testa cenários onde o ProductForm deve ser considerado válido."""

    def setUp(self):
        self.category = Category.objects.create(
            name='Sandalia',
            slug='sandalia',
        )
        self.dados_validos = {
            'name': 'Havaianas Top',
            'description': 'Sandalia classica brasileira para uso casual.',
            'brand': 'Havaianas',
            'price': '59.90',
            'category': self.category.pk,
        }

    def test_form_valido_com_todos_os_campos(self):
        """Formulário com todos os campos preenchidos corretamente é válido."""
        form = ProductForm(data=self.dados_validos)
        self.assertTrue(form.is_valid(), f'Formulário deveria ser válido. Erros: {form.errors}')

    def test_form_valido_sem_categoria(self):
        """Categoria é opcional: formulário sem categoria deve ser válido."""
        dados = {**self.dados_validos}
        dados.pop('category')
        form = ProductForm(data=dados)
        self.assertTrue(
            form.is_valid(),
            f'Formulário sem categoria deveria ser válido. Erros: {form.errors}',
        )

    def test_form_preco_decimal_valido(self):
        """Preço com casas decimais (ex: 1299.99) deve ser aceito."""
        dados = {**self.dados_validos, 'price': '1299.99'}
        form = ProductForm(data=dados)
        self.assertTrue(form.is_valid(), f'Preço decimal deveria ser válido. Erros: {form.errors}')

    def test_form_preco_inteiro_valido(self):
        """Preço sem casas decimais (ex: 100) deve ser aceito."""
        dados = {**self.dados_validos, 'price': '100'}
        form = ProductForm(data=dados)
        self.assertTrue(form.is_valid(), f'Preço inteiro deveria ser válido. Erros: {form.errors}')

    def test_form_preco_minimo_valido(self):
        """Preço de R$ 0,01 (mínimo positivo) deve ser aceito."""
        dados = {**self.dados_validos, 'price': '0.01'}
        form = ProductForm(data=dados)
        self.assertTrue(form.is_valid(), f'Preço 0.01 deveria ser válido. Erros: {form.errors}')

    def test_form_cleaned_data_preco_e_decimal(self):
        """O cleaned_data['price'] deve ser do tipo Decimal, não float."""
        form = ProductForm(data=self.dados_validos)
        form.is_valid()
        self.assertIsInstance(
            form.cleaned_data['price'],
            Decimal,
            'O preço limpo deve ser Decimal, nunca float.',
        )


class ProductFormPrecoInvalidoTest(TestCase):
    """Testa as validações de preço no ProductForm (clean_price)."""

    def setUp(self):
        self.category = Category.objects.create(
            name='Bota',
            slug='bota',
        )
        self.dados_base = {
            'name': 'Bota Couro',
            'description': 'Bota de couro genuino para o inverno.',
            'brand': 'Democrata',
            'category': self.category.pk,
        }

    def test_preco_zero_invalido(self):
        """Preço igual a zero deve gerar erro de validação."""
        dados = {**self.dados_base, 'price': '0'}
        form = ProductForm(data=dados)
        self.assertFalse(form.is_valid(), 'Preço zero deve tornar o formulário inválido.')
        self.assertIn('price', form.errors, 'Erro deve ser no campo price.')

    def test_preco_negativo_invalido(self):
        """Preço negativo deve gerar erro de validação."""
        dados = {**self.dados_base, 'price': '-10.00'}
        form = ProductForm(data=dados)
        self.assertFalse(form.is_valid(), 'Preço negativo deve tornar o formulário inválido.')
        self.assertIn('price', form.errors, 'Erro deve ser no campo price.')

    def test_preco_vazio_invalido(self):
        """Campo preço vazio deve gerar erro de validação."""
        dados = {**self.dados_base, 'price': ''}
        form = ProductForm(data=dados)
        self.assertFalse(form.is_valid(), 'Preço vazio deve tornar o formulário inválido.')
        self.assertIn('price', form.errors, 'Erro deve ser no campo price.')

    def test_preco_texto_invalido(self):
        """Valor não numérico no preço deve gerar erro de validação."""
        dados = {**self.dados_base, 'price': 'abc'}
        form = ProductForm(data=dados)
        self.assertFalse(form.is_valid(), 'Texto no preço deve tornar o formulário inválido.')
        self.assertIn('price', form.errors, 'Erro deve ser no campo price.')

    def test_mensagem_erro_preco_zero(self):
        """Mensagem de erro para preço zero deve ser informativa."""
        dados = {**self.dados_base, 'price': '0'}
        form = ProductForm(data=dados)
        form.is_valid()
        mensagem_erro = str(form.errors['price'])
        self.assertIn(
            'maior que zero',
            mensagem_erro,
            'Mensagem de erro deve mencionar que o preço deve ser maior que zero.',
        )


class ProductFormCamposObrigatoriosTest(TestCase):
    """Testa que campos obrigatórios do ProductForm são validados corretamente."""

    def setUp(self):
        self.category = Category.objects.create(
            name='Tenis Corrida',
            slug='tenis-corrida',
        )
        self.dados_completos = {
            'name': 'Mizuno Wave Prophecy',
            'description': 'Tenis de alta performance para corridas de longa distancia.',
            'brand': 'Mizuno',
            'price': '799.90',
            'category': self.category.pk,
        }

    def test_nome_vazio_invalido(self):
        """Nome vazio deve gerar erro de validação no campo name."""
        dados = {**self.dados_completos, 'name': ''}
        form = ProductForm(data=dados)
        self.assertFalse(form.is_valid(), 'Nome vazio deve tornar o formulário inválido.')
        self.assertIn('name', form.errors, 'Erro deve ser no campo name.')

    def test_descricao_vazia_invalida(self):
        """Descrição vazia deve gerar erro de validação no campo description."""
        dados = {**self.dados_completos, 'description': ''}
        form = ProductForm(data=dados)
        self.assertFalse(form.is_valid(), 'Descrição vazia deve tornar o formulário inválido.')
        self.assertIn('description', form.errors, 'Erro deve ser no campo description.')

    def test_marca_vazia_invalida(self):
        """Marca vazia deve gerar erro de validação no campo brand."""
        dados = {**self.dados_completos, 'brand': ''}
        form = ProductForm(data=dados)
        self.assertFalse(form.is_valid(), 'Marca vazia deve tornar o formulário inválido.')
        self.assertIn('brand', form.errors, 'Erro deve ser no campo brand.')

    def test_nome_com_comprimento_maximo(self):
        """Nome com exatamente 200 caracteres deve ser aceito."""
        dados = {**self.dados_completos, 'name': 'A' * 200}
        form = ProductForm(data=dados)
        self.assertTrue(
            form.is_valid(),
            f'Nome com 200 chars deveria ser válido. Erros: {form.errors}',
        )

    def test_nome_excedendo_limite_invalido(self):
        """Nome com mais de 200 caracteres deve ser rejeitado."""
        dados = {**self.dados_completos, 'name': 'A' * 201}
        form = ProductForm(data=dados)
        self.assertFalse(
            form.is_valid(),
            'Nome com 201 chars deve tornar o formulário inválido.',
        )
        self.assertIn('name', form.errors, 'Erro deve ser no campo name.')
