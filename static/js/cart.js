/**
 * cart.js
 *
 * Funcionalidades interativas da página do carrinho:
 *  - Botões +/− para alterar quantidade com feedback visual
 *  - Revelar/ocultar botão "Atualizar" apenas quando valor muda
 *  - Recalcular subtotal do item visualmente antes de enviar
 *  - Atualizar total geral no resumo
 *  - Confirmação antes de remover um item
 */

(function () {
  "use strict";

  /* ─── Helpers ─────────────────────────────────────────────── */

  /**
   * Formata número no padrão brasileiro: 1.234,56
   * @param {number} value
   * @returns {string}
   */
  function formatBRL(value) {
    return value
      .toFixed(2)
      .replace(".", ",")
      .replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  }

  /**
   * Recalcula o subtotal de um item e atualiza o DOM.
   * @param {HTMLElement} article  — article.cart-item
   */
  function recalcItem(article) {
    const input = article.querySelector(".cart-item__qty-input");
    const subtotalEl = article.querySelector(".subtotal-value");
    if (!input || !subtotalEl) return;

    const qty = parseInt(input.value, 10) || 0;
    const unitPrice = parseFloat(
      article.querySelector(".cart-item__subtotal").dataset.unitPrice
    );
    subtotalEl.textContent = formatBRL(qty * unitPrice);
  }

  /**
   * Recalcula o total geral somando todos os subtotais visíveis.
   */
  function recalcTotal() {
    let total = 0;
    document.querySelectorAll(".cart-item__subtotal").forEach((el) => {
      const input = el
        .closest(".cart-item")
        ?.querySelector(".cart-item__qty-input");
      if (!input) return;
      const qty = parseInt(input.value, 10) || 0;
      const unitPrice = parseFloat(el.dataset.unitPrice);
      total += qty * unitPrice;
    });

    const totalEl = document.getElementById("total-value");
    const summaryEl = document.getElementById("summary-subtotal");
    if (totalEl) totalEl.textContent = formatBRL(total);
    if (summaryEl) summaryEl.textContent = "R$\u00a0" + formatBRL(total);
  }

  /**
   * Exibe ou oculta o botão "Atualizar" de um item.
   * @param {HTMLElement} article
   * @param {HTMLInputElement} input
   */
  function toggleUpdateBtn(article, input) {
    const btn = article.querySelector(".cart-item__btn-update");
    if (!btn) return;
    const original = parseInt(input.dataset.original, 10);
    const current = parseInt(input.value, 10);
    btn.hidden = current === original || current < 1;
  }

  /* ─── Controles de quantidade ──────────────────────────────── */

  document.querySelectorAll(".cart-item__qty-form").forEach((form) => {
    const article = form.closest(".cart-item");
    const input = form.querySelector(".cart-item__qty-input");
    if (!input || !article) return;

    /* Botões +/− */
    form.querySelectorAll(".qty-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        let val = parseInt(input.value, 10) || 1;
        if (btn.dataset.action === "inc") {
          val = Math.min(val + 1, parseInt(input.max, 10) || 99);
        } else {
          val = Math.max(val - 1, 1);
        }
        input.value = val;
        recalcItem(article);
        recalcTotal();
        toggleUpdateBtn(article, input);
      });
    });

    /* Digitação direta */
    input.addEventListener("input", () => {
      recalcItem(article);
      recalcTotal();
      toggleUpdateBtn(article, input);
    });

    /* Garante min=1 ao sair do campo */
    input.addEventListener("blur", () => {
      if (!input.value || parseInt(input.value, 10) < 1) {
        input.value = 1;
        recalcItem(article);
        recalcTotal();
        toggleUpdateBtn(article, input);
      }
    });
  });

  /* ─── Confirmação de remoção ───────────────────────────────── */

  document.querySelectorAll(".cart-item__remove-form").forEach((form) => {
    form.addEventListener("submit", (e) => {
      const name = form.dataset.itemName || "este item";
      const confirmed = window.confirm(
        `Remover "${name}" do carrinho?\n\nEsta ação não pode ser desfeita.`
      );
      if (!confirmed) {
        e.preventDefault();
      }
    });
  });

  /* ─── Animação de saída no envio do form de remoção ─────────── */

  document.querySelectorAll(".cart-item__remove-form").forEach((form) => {
    form.addEventListener("submit", (e) => {
      /* A confirmação já aconteceu acima; se chegamos aqui, foi confirmado */
      const article = form.closest(".cart-item");
      if (article) {
        article.style.transition = "opacity 0.25s ease, transform 0.25s ease";
        article.style.opacity = "0";
        article.style.transform = "translateX(20px)";
      }
    });
  });

  /* ─── Feedback visual ao submeter form de update ──────────────── */

  document.querySelectorAll(".cart-item__qty-form").forEach((form) => {
    form.addEventListener("submit", () => {
      const btn = form.querySelector(".cart-item__btn-update");
      if (btn) {
        btn.textContent = "Salvando…";
        btn.disabled = true;
      }
    });
  });
})();
