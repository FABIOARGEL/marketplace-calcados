/**
 * product-form.js
 *
 * Funcionalidades do formulário de cadastro de produto:
 *   1. Adicionar/remover linhas de estoque dinamicamente (inline formset)
 *   2. Preview de imagens antes do upload
 *   3. Highlight de drag-and-drop na zona de upload
 */

(function () {
    'use strict';

    // ----------------------------------------------------------------
    // 1. Estoque — adicionar/remover linhas dinamicamente
    // ----------------------------------------------------------------

    /**
     * Gerencia o formset de estoque inline.
     * Lê o TOTAL_FORM_COUNT do management form e incrementa ao adicionar linhas.
     */
    function initStockFormset() {
        const tableBody = document.getElementById('stock-formset-body');
        const addBtn = document.getElementById('btn-add-stock-row');
        const totalFormsInput = document.getElementById('id_stock-TOTAL_FORMS');
        const emptyRow = document.getElementById('stock-empty-row');

        if (!tableBody || !addBtn || !totalFormsInput || !emptyRow) return;

        addBtn.addEventListener('click', function () {
            const formCount = parseInt(totalFormsInput.value, 10);
            // Clona a linha template e substitui o prefixo __prefix__
            const newRowHtml = emptyRow.innerHTML.replace(/__prefix__/g, formCount);

            const tr = document.createElement('tr');
            tr.classList.add('stock-row');
            tr.setAttribute('data-form-index', formCount);
            tr.innerHTML = newRowHtml;

            tableBody.appendChild(tr);
            totalFormsInput.value = formCount + 1;

            // Foca no input de tamanho da nova linha
            const sizeInput = tr.querySelector('.form-input--size');
            if (sizeInput) sizeInput.focus();
        });

        // Delegação de evento para o checkbox de deletar
        tableBody.addEventListener('change', function (e) {
            const checkbox = e.target;
            if (!checkbox.matches('input[type="checkbox"][id*="-DELETE"]')) return;

            const row = checkbox.closest('tr');
            if (!row) return;

            if (checkbox.checked) {
                row.classList.add('stock-row--deleted');
            } else {
                row.classList.remove('stock-row--deleted');
            }
        });
    }

    // ----------------------------------------------------------------
    // 2. Preview de imagens antes do upload
    // ----------------------------------------------------------------

    /**
     * Gera previews em miniatura quando o usuário seleciona imagens
     * em qualquer input[type=file] do formset de imagens.
     */
    function initImagePreviews() {
        const previewContainer = document.getElementById('image-previews-container');
        if (!previewContainer) return;

        // Delegação no formset — captura mudanças em qualquer file input
        const imageFormsetContainer = document.getElementById('image-formset-container');
        if (!imageFormsetContainer) return;

        imageFormsetContainer.addEventListener('change', function (e) {
            const input = e.target;
            if (!input.matches('input[type="file"]')) return;

            const files = input.files;
            if (!files || !files.length) return;

            Array.from(files).forEach(function (file) {
                if (!file.type.startsWith('image/')) return;

                const reader = new FileReader();
                reader.onload = function (evt) {
                    const preview = document.createElement('div');
                    preview.classList.add('image-preview');

                    const img = document.createElement('img');
                    img.src = evt.target.result;
                    img.alt = file.name;

                    const removeBtn = document.createElement('button');
                    removeBtn.type = 'button';
                    removeBtn.classList.add('image-preview__remove');
                    removeBtn.textContent = '×';
                    removeBtn.setAttribute('aria-label', 'Remover preview de ' + file.name);

                    removeBtn.addEventListener('click', function () {
                        preview.remove();
                        // Limpa o input de arquivo associado
                        input.value = '';
                    });

                    preview.appendChild(img);
                    preview.appendChild(removeBtn);
                    previewContainer.appendChild(preview);
                };
                reader.readAsDataURL(file);
            });
        });
    }

    // ----------------------------------------------------------------
    // 3. Drag-and-drop highlight na zona de upload
    // ----------------------------------------------------------------

    function initDragAndDrop() {
        const uploadZone = document.getElementById('image-upload-zone');
        if (!uploadZone) return;

        const fileInput = uploadZone.querySelector('input[type="file"]');

        // Clique na zona abre o seletor de arquivos
        uploadZone.addEventListener('click', function () {
            if (fileInput) fileInput.click();
        });

        ['dragenter', 'dragover'].forEach(function (eventName) {
            uploadZone.addEventListener(eventName, function (e) {
                e.preventDefault();
                e.stopPropagation();
                uploadZone.classList.add('image-upload-zone--dragover');
            });
        });

        ['dragleave', 'drop'].forEach(function (eventName) {
            uploadZone.addEventListener(eventName, function (e) {
                e.preventDefault();
                e.stopPropagation();
                uploadZone.classList.remove('image-upload-zone--dragover');
            });
        });

        uploadZone.addEventListener('drop', function (e) {
            const dt = e.dataTransfer;
            if (!dt || !fileInput) return;

            // Dispara evento change no input para acionar o preview
            const newFiles = dt.files;
            if (!newFiles.length) return;

            // DataTransfer é somente-leitura em alguns browsers;
            // apenas exibe os previews via FileReader sem anexar ao input
            const previewContainer = document.getElementById('image-previews-container');
            if (!previewContainer) return;

            Array.from(newFiles).forEach(function (file) {
                if (!file.type.startsWith('image/')) return;
                const reader = new FileReader();
                reader.onload = function (evt) {
                    const preview = document.createElement('div');
                    preview.classList.add('image-preview');

                    const img = document.createElement('img');
                    img.src = evt.target.result;
                    img.alt = file.name;

                    preview.appendChild(img);
                    previewContainer.appendChild(preview);
                };
                reader.readAsDataURL(file);
            });
        });
    }

    // ----------------------------------------------------------------
    // Inicialização
    // ----------------------------------------------------------------
    document.addEventListener('DOMContentLoaded', function () {
        initStockFormset();
        initImagePreviews();
        initDragAndDrop();
    });

}());
