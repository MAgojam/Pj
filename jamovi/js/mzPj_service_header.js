// Sposta i nodi originali: Browse, pillola e rimozione restano gestiti da jamovi.
module.exports = function(ui) {
    const view = ui.view && ui.view.el;
    if (!view)
        return;
    const block = view.closest ? view.closest('.jmv-options-block') : null;
    const header = (block || document).querySelector('.silky-options-header');
    if (!header)
        return;
    const title = header.querySelector('.silky-options-title');
    if (title && !title.querySelector('.mzpj-title-icon')) {
        const originalTitle = title.textContent.trim();
        if (/^Pj\s+Editor(?:\s*\+)?$/.test(originalTitle)) {
            title.textContent = originalTitle.replace(/^Pj\s+/, '');
            title.setAttribute('aria-label', originalTitle);
        }
        title.classList.add('mzpj-icon-title');
        const icon = document.createElement('span');
        icon.className = 'mzpj-title-icon';
        icon.setAttribute('aria-hidden', 'true');
        // SVG incorporato: nessuna richiesta di file e nessuna azione al clic.
        icon.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="38" height="38" viewBox="0 0 64 64" aria-hidden="true" focusable="false">
  <g fill="none" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5">
    <path d="M10 25 4 32 10 39" stroke="#3e6da9"/>
    <path d="M54 25 60 32 54 39" stroke="#eca038"/>
  </g>
  <path d="M18 45V19c0-7 5-10 13-10h5c7 0 11 4 11 11v2c0 7-4 10-12 10h-8v13a4.5 4.5 0 0 1-9 0Z" fill="#3e6da9"/>
  <path d="M39 37h9v6c0 10-6 15-15 15h-7c-6 0-10-3-10-8v-2c0-4 3-7 8-7h9v8h-6c-1 0-2 1-2 2h8c4 0 6-3 6-8Z" fill="#ffd343"/>
  <circle cx="38" cy="17" r="2" fill="#fff"/>
  <circle cx="37.5" cy="17" r="0.9" fill="#1e293b"/>
  <circle cx="22" cy="48" r="1.8" fill="#1e293b"/>
  <circle cx="43.5" cy="32" r="3" fill="#ffd343"/>
</svg>`;
        title.insertBefore(icon, title.firstChild || null);
    }
    const control = ui.scriptFile;
    const body = control && control.body && control.body.nodeType === 1 ? control.body :
        view.querySelector('.jmv-file-selector');
    if (!body || header.contains(body))
        return;
    const button = body.querySelector('.jmv-file-selector-button');
    const label = control && control.label && control.label.nodeType === 1 ? control.label :
        Array.from(view.querySelectorAll('label')).find(label => button && label.htmlFor === button.id);
    if (!label)
        return;
    const origins = [label, body].map(node => node.closest('.silky-layout-cell')).filter(Boolean);
    const host = document.createElement('div');
    host.className = 'mzpj-service-header';
    host.setAttribute('role', 'group');
    host.setAttribute('aria-label', 'Service script');
    // La rimozione modifica il DOM durante il clic: annulla anche l'attivazione
    // predefinita e gli handler esterni, senza inoltrare il clic a Browse.
    host.addEventListener('click', event => {
        const target = event.target;
        const remove = target && target.closest ? target.closest('.jmv-file-selector-remove') : null;
        if (!remove || !host.contains(remove))
            return;
        if (!control || typeof control.setValue !== 'function')
            return;
        event.preventDefault();
        event.stopPropagation();
        if (!remove.disabled) {
            // scriptFile e' un File singolo: [] e' il valore nativo senza file.
            control.setValue([]);
            if (button)
                button.focus();
        }
    }, true);
    label.title = label.textContent;
    host.appendChild(label);
    host.appendChild(body);
    const back = header.querySelector('.silky-sp-back-button');
    header.insertBefore(host, back && back.parentElement === header ? back : null);
    header.classList.add('mzpj-editor-header');
    // Le celle rimangono nel modello del layout, ma non occupano piu’ spazio.
    origins.forEach(cell => cell.classList.add('mzpj-service-origin'));
};
