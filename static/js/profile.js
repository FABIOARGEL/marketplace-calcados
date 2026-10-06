/**
 * profile.js — Preview de frete em tempo real.
 *
 * Recalcula o frete estimado sempre que o usuário altera os campos
 * shipping_distance_km ou shipping_rate_per_km no formulário do vendedor.
 * Usa apenas data-* e addEventListener — sem eventos inline.
 */

document.addEventListener('DOMContentLoaded', () => {
    const distanceInput = document.getElementById('id_shipping_distance_km');
    const rateInput = document.getElementById('id_shipping_rate_per_km');
    const previewValue = document.getElementById('shipping-preview-value');

    if (!distanceInput || !rateInput || !previewValue) {
        // Campos não presentes (usuário cliente) — nada a fazer.
        return;
    }

    /**
     * Calcula e exibe o frete estimado.
     * Fórmula: frete = distância × taxa
     */
    function updateShippingPreview() {
        const distance = parseFloat(distanceInput.value) || 0;
        const rate = parseFloat(rateInput.value) || 0;
        const total = distance * rate;

        previewValue.style.opacity = '0.4';

        setTimeout(() => {
            if (total > 0) {
                previewValue.textContent = total.toLocaleString('pt-BR', {
                    style: 'currency',
                    currency: 'BRL',
                });
            } else {
                previewValue.textContent = '—';
            }
            previewValue.style.opacity = '1';
        }, 120);
    }

    distanceInput.addEventListener('input', updateShippingPreview);
    rateInput.addEventListener('input', updateShippingPreview);

    // Calcula na carga inicial caso os campos já venham preenchidos.
    updateShippingPreview();
});
