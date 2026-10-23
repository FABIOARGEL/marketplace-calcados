/**
 * search.js — Lógica de busca no catálogo e no header.
 *
 * Funcionalidades:
 *  - Validação do campo antes de submeter (não envia query vazia)
 *  - Foco automático no campo de busca do catálogo
 *  - Sincronização do campo do header com o termo atual da URL
 *  - Debounce opcional para busca futura em tempo real
 */

(function () {
    'use strict';

    /* --------------------------------------------------------
       Helpers
    -------------------------------------------------------- */

    /**
     * Retorna o valor do parâmetro `q` da query string atual.
     * @returns {string}
     */
    function getQueryParam() {
        return new URLSearchParams(window.location.search).get('q') || '';
    }

    /**
     * Impede o submit quando o campo está vazio.
     * @param {HTMLFormElement} form
     */
    function preventEmptySearch(form) {
        if (!form) return;

        form.addEventListener('submit', function (event) {
            const input = form.querySelector('input[name="q"]');
            if (!input) return;

            const value = input.value.trim();

            if (value === '') {
                // Se já estava sem busca, não recarrega a página
                event.preventDefault();
                input.focus();
                return;
            }

            // Normaliza espaços extras
            input.value = value;
        });
    }

    /* --------------------------------------------------------
       Header — formulários de busca rápida
    -------------------------------------------------------- */

    const headerForm = document.getElementById('header-search-form');
    const mobileForm = document.getElementById('mobile-search-form');

    preventEmptySearch(headerForm);
    preventEmptySearch(mobileForm);

    // Pré-preenche os campos do header com o termo atual da URL
    const currentQuery = getQueryParam();

    if (currentQuery) {
        const headerInput = document.getElementById('header-q');
        const mobileInput = document.getElementById('mobile-q');

        if (headerInput) headerInput.value = currentQuery;
        if (mobileInput) mobileInput.value = currentQuery;
    }

    /* --------------------------------------------------------
       Catálogo — formulário de busca principal
    -------------------------------------------------------- */

    const catalogForm = document.getElementById('catalog-search-form');
    preventEmptySearch(catalogForm);

    // Foca no campo de busca do catálogo apenas quando o usuário
    // chegou por uma busca (preserva UX em navegação normal)
    const catalogInput = document.getElementById('catalog-q');

    if (catalogInput && currentQuery) {
        // Posiciona cursor ao final do texto existente
        const len = catalogInput.value.length;
        catalogInput.setSelectionRange(len, len);
        catalogInput.focus({ preventScroll: true });
    }

    /* --------------------------------------------------------
       Acessibilidade — anuncia contagem de resultados
    -------------------------------------------------------- */

    const emptyState = document.getElementById('catalog-empty-state');

    if (emptyState) {
        // aria-live="polite" já está no elemento; o anúncio acontece
        // automaticamente quando o conteúdo é inserido no DOM.
        // Este bloco existe para futuras melhorias de SPA/AJAX.
    }
}());
