/**
 * checkout.js — Lógica do frontend para a página de checkout.
 *
 * Responsabilidades:
 *  1. Realçar visualmente a opção de endereço selecionada (radio → .is-selected)
 *  2. Realçar visualmente o método de pagamento selecionado
 *  3. Validar o formulário antes do submit:
 *      - endereço selecionado
 *      - método de pagamento selecionado
 *  4. Feedback visual no botão durante envio
 */

(function () {
  'use strict';

  /* ── Helpers ── */
  function qs(selector, root = document) {
    return root.querySelector(selector);
  }
  function qsa(selector, root = document) {
    return Array.from(root.querySelectorAll(selector));
  }

  /* ─────────────────────────────────────────────────────────────────────────
     1. Highlight de opções (endereço e pagamento)
  ───────────────────────────────────────────────────────────────────────── */
  function setupOptionHighlight(radioName, containerSelector) {
    const radios = qsa(`input[name="${radioName}"]`);

    function updateHighlight() {
      radios.forEach((radio) => {
        const option = radio.closest(containerSelector);
        if (!option) return;
        option.classList.toggle('is-selected', radio.checked);
      });
    }

    radios.forEach((radio) => {
      radio.addEventListener('change', updateHighlight);
      // Clique em qualquer parte da opção seleciona o radio
      const option = radio.closest(containerSelector);
      if (option) {
        option.addEventListener('click', () => {
          radio.checked = true;
          updateHighlight();
        });
      }
    });

    // Estado inicial
    updateHighlight();
  }

  /* ─────────────────────────────────────────────────────────────────────────
     2. Inicializar highlights
  ───────────────────────────────────────────────────────────────────────── */
  setupOptionHighlight('address_id', '.address-option');
  setupOptionHighlight('payment_method', '.payment-option');

  /* ─────────────────────────────────────────────────────────────────────────
     3. Validação e submit
  ───────────────────────────────────────────────────────────────────────── */
  const form = qs('#checkout-form');
  if (!form) return;

  const submitBtn = qs('#checkout-submit-btn', form);
  const addressError = qs('#address-validation-error');
  const paymentError = qs('#payment-validation-error');

  function showError(el) {
    if (el) el.classList.add('visible');
  }
  function hideError(el) {
    if (el) el.classList.remove('visible');
  }

  // Esconder erros quando o usuário escolhe uma opção
  qsa('input[name="address_id"]').forEach((r) => {
    r.addEventListener('change', () => hideError(addressError));
  });
  qsa('input[name="payment_method"]').forEach((r) => {
    r.addEventListener('change', () => hideError(paymentError));
  });

  form.addEventListener('submit', function (e) {
    let valid = true;

    // Valida endereço
    const addressChosen = qsa('input[name="address_id"]').some((r) => r.checked);
    if (!addressChosen) {
      showError(addressError);
      valid = false;
    } else {
      hideError(addressError);
    }

    // Valida pagamento
    const paymentChosen = qsa('input[name="payment_method"]').some((r) => r.checked);
    if (!paymentChosen) {
      showError(paymentError);
      valid = false;
    } else {
      hideError(paymentError);
    }

    if (!valid) {
      e.preventDefault();
      // Rola até o primeiro erro
      const firstError = qs('.address-validation-error.visible, .payment-validation-error.visible');
      if (firstError) {
        firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
      return;
    }

    // Feedback visual no botão
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = 'Processando…';
    }
  });
})();
