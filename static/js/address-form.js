/**
 * address-form.js
 *
 * Autocomplete de CEP via API ViaCEP (https://viacep.com.br/).
 * Preenche automaticamente: logradouro, bairro, cidade e UF.
 *
 * Dispara no evento `blur` do campo CEP apos detectar 8 digitos numericos.
 * Nao usa jQuery nem bibliotecas externas — apenas Fetch API nativa.
 */

(function () {
  "use strict";

  // Seletores
  const cepInput          = document.getElementById("id_addr_zip_code");
  const streetInput       = document.getElementById("id_addr_street");
  const neighborhoodInput = document.getElementById("id_addr_neighborhood");
  const cityInput         = document.getElementById("id_addr_city");
  const stateInput        = document.getElementById("id_addr_state");

  // Saida antecipada se a pagina nao contiver o formulario de endereco
  if (!cepInput) return;

  // ── Helpers ──────────────────────────────────────────────────────────────

  function stripCep(value) {
    return value.replace(/\D/g, "");
  }

  function formatCep(digits) {
    return digits.length === 8 ? `${digits.slice(0, 5)}-${digits.slice(5)}` : digits;
  }

  function setLoading(active) {
    if (active) {
      cepInput.setAttribute("data-loading", "true");
      cepInput.style.opacity = "0.6";
      cepInput.style.cursor  = "wait";
    } else {
      cepInput.removeAttribute("data-loading");
      cepInput.style.opacity = "";
      cepInput.style.cursor  = "";
    }
  }

  function setCepFeedback(type, message) {
    // Remove feedback anterior
    const existing = cepInput.parentElement.querySelector(".cep-feedback");
    if (existing) existing.remove();
    cepInput.classList.remove("form-input--error", "form-input--success");

    if (!message) return;

    cepInput.classList.add(type === "error" ? "form-input--error" : "form-input--success");

    const el = document.createElement("p");
    el.className = `cep-feedback cep-feedback--${type}`;
    el.setAttribute("role", "alert");
    el.textContent = message;
    cepInput.insertAdjacentElement("afterend", el);
  }

  function fillFields(data) {
    const map = [
      [streetInput,       data.logradouro],
      [neighborhoodInput, data.bairro],
      [cityInput,         data.localidade],
      [stateInput,        data.uf],
    ];

    map.forEach(([el, value]) => {
      if (el) el.value = value || "";
    });

    // Foca no proximo campo em branco relevante
    const focusTarget = streetInput && !streetInput.value ? streetInput
                      : neighborhoodInput && !neighborhoodInput.value ? neighborhoodInput
                      : null;
    if (focusTarget) focusTarget.focus();
  }

  function clearAddressFields() {
    [streetInput, neighborhoodInput, cityInput, stateInput].forEach(el => {
      if (el) el.value = "";
    });
  }

  // ── Mascara automatica XXXXX-XXX enquanto digita ─────────────────────────
  cepInput.addEventListener("input", function () {
    const digits = stripCep(this.value);
    this.value = digits.length <= 5 ? digits : formatCep(digits.slice(0, 8));
  });

  // ── Autocomplete ao sair do campo (blur) ──────────────────────────────────
  cepInput.addEventListener("blur", async function () {
    const digits = stripCep(this.value);

    if (digits.length === 0) return;

    if (digits.length < 8) {
      setCepFeedback("error", "CEP incompleto. Digite os 8 digitos.");
      return;
    }

    // Garante formatacao correta no campo
    this.value = formatCep(digits);
    setCepFeedback(null, null);
    setLoading(true);

    try {
      const controller = new AbortController();
      const timeout    = setTimeout(() => controller.abort(), 8000);

      const response = await fetch(
        `https://viacep.com.br/ws/${digits}/json/`,
        { signal: controller.signal }
      );
      clearTimeout(timeout);

      if (!response.ok) throw new Error("Resposta invalida da API.");

      const data = await response.json();

      if (data.erro) {
        clearAddressFields();
        setCepFeedback("error", "CEP nao encontrado. Verifique o numero digitado.");
        return;
      }

      clearAddressFields();
      fillFields(data);
      setCepFeedback("success", "Endereco preenchido automaticamente.");

    } catch (err) {
      const isTimeout = err.name === "AbortError";
      setCepFeedback(
        "error",
        isTimeout
          ? "Tempo esgotado ao consultar o CEP. Preencha manualmente."
          : "Nao foi possivel consultar o CEP. Preencha manualmente."
      );
    } finally {
      setLoading(false);
    }
  });

})();
