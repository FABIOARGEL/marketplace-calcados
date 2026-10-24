/**
 * filters.js — Interacao do painel de filtros do catalogo.
 *
 * Responsabilidades:
 *  - Toggle da sidebar no mobile (abre/fecha)
 *  - Accordion por grupo de filtro (abre/fecha secao)
 *  - Submissao automatica ao mudar radio/checkbox de filtros
 *  - Restaura estado visual dos filtros ao carregar a pagina
 */

(function () {
  'use strict';

  /* ============================================================
     1. Toggle da sidebar (mobile)
  ============================================================ */
  const toggleBtn = document.getElementById('filters-toggle-btn');
  const sidebar = document.getElementById('catalog-sidebar');

  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', function () {
      const isOpen = sidebar.classList.toggle('is-open');
      toggleBtn.setAttribute('aria-expanded', String(isOpen));
    });
  }

  /* ============================================================
     2. Accordion por grupo de filtros
  ============================================================ */
  const groupToggles = document.querySelectorAll('.filter-group__toggle');

  groupToggles.forEach(function (btn) {
    const targetId = btn.getAttribute('aria-controls');
    const optionsEl = targetId ? document.getElementById(targetId) : null;

    if (!optionsEl) return;

    btn.addEventListener('click', function () {
      const expanded = btn.getAttribute('aria-expanded') === 'true';
      const nowExpanded = !expanded;

      btn.setAttribute('aria-expanded', String(nowExpanded));

      if (nowExpanded) {
        optionsEl.classList.remove('is-collapsed');
      } else {
        optionsEl.classList.add('is-collapsed');
      }
    });
  });

  /* ============================================================
     3. Auto-submit ao mudar radio (categoria, marca)
        Checkboxes de tamanho precisam do botao "Filtrar"
        para nao recarregar a cada clique multiplo.
        Aqui deixamos apenas radios com auto-submit.
  ============================================================ */
  const filterForm = document.getElementById('catalog-filter-form');

  if (filterForm) {
    const radioInputs = filterForm.querySelectorAll('input[type="radio"]');

    radioInputs.forEach(function (radio) {
      radio.addEventListener('change', function () {
        // Pequeno delay para a animacao de selecao ser visivel
        setTimeout(function () {
          filterForm.submit();
        }, 150);
      });
    });
  }

  /* ============================================================
     4. Fechar sidebar ao clicar fora (mobile)
  ============================================================ */
  document.addEventListener('click', function (e) {
    if (!sidebar || !toggleBtn) return;

    // Se nao esta aberto, ignora
    if (!sidebar.classList.contains('is-open')) return;

    // Se o clique foi dentro da sidebar ou no botao toggle, ignora
    if (sidebar.contains(e.target) || toggleBtn.contains(e.target)) return;

    sidebar.classList.remove('is-open');
    toggleBtn.setAttribute('aria-expanded', 'false');
  });

  /* ============================================================
     5. Feedback visual: marca o botao de filtrar quando
        algum checkbox de tamanho e alterado
  ============================================================ */
  if (filterForm) {
    const sizeCheckboxes = filterForm.querySelectorAll('input[type="checkbox"][name="tamanho"]');
    const submitBtn = document.getElementById('filter-submit-btn');

    sizeCheckboxes.forEach(function (cb) {
      cb.addEventListener('change', function () {
        if (!submitBtn) return;
        // Pulsa o botao de filtrar para indicar que ha mudanca pendente
        submitBtn.classList.add('filter-form__submit--pulse');
        setTimeout(function () {
          submitBtn.classList.remove('filter-form__submit--pulse');
        }, 600);
      });
    });
  }

})();
