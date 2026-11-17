// Riutilizza il selettore File nativo; nessun percorso del browser viene inventato.
module.exports = function(ui, menu) {
    if (!menu) return;
    const panel = menu.querySelector('#omv-files');
    const control = ui.omvFile;
    if (!control || !control.body || !panel)
        return;
    const refresh = () => {
        let info = {};
        try { info = JSON.parse((ui.dataextInfo.value() || {}).json || '{}'); } catch (_) { /* Stato iniziale vuoto. */ }
        panel.querySelector('#dataext-name').textContent = info.name || 'Empty';
        panel.querySelector('#dataext-dimensions').textContent = info.ready && Number.isInteger(info.rows) && Number.isInteger(info.columns)
            ? `${info.rows} rows · ${info.columns} columns` : '';
        panel.querySelector('#save-omv').disabled = !info.ready;
        panel.querySelector('#preview-dataext').checked = !!ui.previewDataext.value();
    };
    refresh();
    if (panel.dataset.initialized === 'true') return;
    panel.dataset.initialized = 'true';
    // Gli aggiornamenti provenienti dal backend arrivano alle Options native,
    // anche quando l'utente rimane nella stessa analisi e non scatta update().
    for (const name of ['dataextInfo', 'previewDataext'])
        ui.view.model.options.getOption(name).on('valuechanged', refresh);
    const body = control.body;
    panel.querySelector('#save-omv').setAttribute('aria-label', 'Save dataext as an external OMV');
    const label = control.label;
    const origins = [body, label].filter(Boolean).map(node => node.closest('.silky-layout-cell')).filter(Boolean);
    if (label) label.hidden = true;
    const button = body.querySelector('.jmv-file-selector-button');
    if (button) {
        button.textContent = 'Read…';
        button.setAttribute('aria-label', 'Read an external OMV into dataext');
    }
    panel.querySelector('.mzpj-omv-input').appendChild(body);
    origins.forEach(cell => { cell.style.display = 'none'; });
    panel.querySelector('#save-omv').addEventListener('click', () => ui.saveOmvFile.setValue(true));
    panel.querySelector('#preview-dataext').addEventListener('change', event => {
        // Stato e comando viaggiano insieme: nessuna deduzione dalle altre opzioni.
        const options = ui.view.model.options;
        options.beginEdit();
        try {
            ui.previewDataext.setValue(event.target.checked);
            ui.previewDataextRequest.setValue(true);
        } finally {
            options.endEdit();
        }
    });
};
