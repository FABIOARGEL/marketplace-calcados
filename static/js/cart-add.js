/**
 * cart-add.js — Lógica client-side da página de detalhe do produto.
 *
 * Funcionalidades:
 *  1. Galeria: troca a imagem principal ao clicar em miniatura
 *  2. Quantity stepper: botões +/− com validação de min/max
 *  3. Seleção de tamanho: exibe estoque disponível e ajusta max do input
 *  4. Validação do formulário antes de enviar
 *  5. Feedback visual ao submeter (loading state no botão)
 *  6. Atualiza o indicador de itens do carrinho no header
 */

(function () {
    'use strict';

    /* --------------------------------------------------------
       1. Galeria de imagens
    -------------------------------------------------------- */
    const mainImg = document.getElementById('gallery-main-img');
    const thumbBtns = document.querySelectorAll('.detail-gallery__thumb');

    thumbBtns.forEach(function (btn) {
        btn.addEventListener('click', function () {
            // Atualiza imagem principal
            if (mainImg) {
                mainImg.src = btn.dataset.src;
                mainImg.alt = btn.dataset.alt;

                // Animação de fade
                mainImg.style.opacity = '0';
                requestAnimationFrame(function () {
                    mainImg.style.transition = 'opacity 200ms ease';
                    mainImg.style.opacity = '1';
                });
            }

            // Marca miniatura ativa
            thumbBtns.forEach(function (t) {
                t.classList.remove('detail-gallery__thumb--active');
                t.setAttribute('aria-pressed', 'false');
            });
            btn.classList.add('detail-gallery__thumb--active');
            btn.setAttribute('aria-pressed', 'true');
        });

        // Acessibilidade: ativa com Enter/Espaço
        btn.setAttribute('aria-pressed', btn.classList.contains('detail-gallery__thumb--active') ? 'true' : 'false');
    });

    /* --------------------------------------------------------
       2. Quantity stepper
    -------------------------------------------------------- */
    const qtyInput = document.getElementById('quantity-input');
    const btnDecrease = document.getElementById('qty-decrease');
    const btnIncrease = document.getElementById('qty-increase');

    function clampQty(value, min, max) {
        return Math.min(Math.max(parseInt(value, 10) || min, min), max);
    }

    function updateStepperButtons() {
        if (!qtyInput) return;
        const val = parseInt(qtyInput.value, 10);
        const min = parseInt(qtyInput.min, 10) || 1;
        const max = parseInt(qtyInput.max, 10) || 99;

        if (btnDecrease) btnDecrease.disabled = val <= min;
        if (btnIncrease) btnIncrease.disabled = val >= max;
    }

    if (btnDecrease) {
        btnDecrease.addEventListener('click', function () {
            if (!qtyInput) return;
            const min = parseInt(qtyInput.min, 10) || 1;
            const max = parseInt(qtyInput.max, 10) || 99;
            qtyInput.value = clampQty(parseInt(qtyInput.value, 10) - 1, min, max);
            updateStepperButtons();
        });
    }

    if (btnIncrease) {
        btnIncrease.addEventListener('click', function () {
            if (!qtyInput) return;
            const min = parseInt(qtyInput.min, 10) || 1;
            const max = parseInt(qtyInput.max, 10) || 99;
            qtyInput.value = clampQty(parseInt(qtyInput.value, 10) + 1, min, max);
            updateStepperButtons();
        });
    }

    if (qtyInput) {
        qtyInput.addEventListener('input', updateStepperButtons);
        updateStepperButtons();
    }

    /* --------------------------------------------------------
       3. Seleção de tamanho → exibe estoque disponível
    -------------------------------------------------------- */
    const sizeSelect = document.getElementById('size-select');
    const stockInfo = document.getElementById('stock-available');
    const sizeHint = document.getElementById('size-hint');

    function onSizeChange() {
        if (!sizeSelect || !qtyInput) return;

        const selected = sizeSelect.options[sizeSelect.selectedIndex];
        const stockQty = selected ? parseInt(selected.dataset.stock || '0', 10) : 0;

        // Atualiza max do input de quantidade
        qtyInput.max = stockQty > 0 ? stockQty : 1;

        // Clamp qty atual se necessário
        if (parseInt(qtyInput.value, 10) > stockQty) {
            qtyInput.value = stockQty > 0 ? stockQty : 1;
        }

        // Exibe disponibilidade
        if (stockInfo) {
            if (selected && selected.value) {
                stockInfo.textContent = stockQty > 0
                    ? `${stockQty} unidade${stockQty !== 1 ? 's' : ''} disponíve${stockQty !== 1 ? 'is' : 'l'}`
                    : 'Esgotado';
                stockInfo.className = 'cart-add-form__stock-info ' +
                    (stockQty > 0 ? 'cart-add-form__stock-info--ok' : 'cart-add-form__stock-info--empty');
            } else {
                stockInfo.textContent = '';
                stockInfo.className = 'cart-add-form__stock-info';
            }
        }

        // Limpa hint de obrigatório após seleção
        if (sizeHint && selected && selected.value) {
            sizeHint.textContent = '';
        }

        updateStepperButtons();
    }

    if (sizeSelect) {
        sizeSelect.addEventListener('change', onSizeChange);
    }

    /* --------------------------------------------------------
       4. Validação e 5. Loading state no formulário
    -------------------------------------------------------- */
    const cartForm = document.getElementById('cart-add-form');
    const submitBtn = document.getElementById('btn-add-to-cart');

    if (cartForm) {
        cartForm.addEventListener('submit', function (event) {
            // Valida tamanho selecionado
            if (sizeSelect && !sizeSelect.value) {
                event.preventDefault();
                if (sizeHint) {
                    sizeHint.textContent = 'Selecione um tamanho antes de continuar.';
                }
                sizeSelect.focus();
                return;
            }

            // Valida quantidade
            const qty = parseInt(qtyInput ? qtyInput.value : '1', 10);
            if (isNaN(qty) || qty < 1) {
                event.preventDefault();
                if (qtyInput) {
                    qtyInput.value = 1;
                    qtyInput.focus();
                }
                return;
            }

            // Loading state
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = '⏳ Adicionando…';
                submitBtn.setAttribute('aria-busy', 'true');
            }
        });
    }

    /* --------------------------------------------------------
       6. Atualiza indicador de carrinho no header (badge)
    -------------------------------------------------------- */

    /**
     * Após sucesso Django redireciona para /carrinho/ com mensagem.
     * Para atualizar o badge sem recarregar, usamos um fetch simples
     * ao endpoint de detalhes do carrinho para obter a contagem.
     *
     * Nota: isso só executa se existir um elemento com id="cart-count"
     * no header — a implementação do badge fica em cart_detail.html/header.
     */
    function refreshCartBadge() {
        const badge = document.getElementById('cart-count');
        if (!badge) return;

        fetch('/carrinho/', {
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            credentials: 'same-origin',
        })
        .then(function (res) { return res.text(); })
        .then(function (html) {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const newBadge = doc.getElementById('cart-count');
            if (newBadge) badge.textContent = newBadge.textContent;
        })
        .catch(function () { /* silencia — badge atualiza no próximo carregamento */ });
    }

    if (cartForm) {
        cartForm.addEventListener('submit', refreshCartBadge);
    }

}());
