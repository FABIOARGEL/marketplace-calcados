# config/__init__.py
# Pacote de configuração do projeto Django — Marketplace de Calçados

import sys

# Compatibilidade Django 4.2 com Python 3.14+ (copy(super()) em BaseContext.__copy__)
if sys.version_info >= (3, 13):
    from django.template import context as _template_context

    def _base_context_copy(self):
        duplicate = self.__class__.__new__(self.__class__)
        duplicate.dicts = self.dicts[:]
        return duplicate

    _template_context.BaseContext.__copy__ = _base_context_copy
