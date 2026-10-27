// Sposta i nodi originali: selezione file, pillola e rimozione restano gestiti da jamovi.
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
            title.textContent = 'Editor';
            title.setAttribute('aria-label', originalTitle);
            if (/\+$/.test(originalTitle)) {
                const badge = document.createElement('sub');
                badge.className = 'mzpj-editor-plus';
                badge.textContent = 'plus';
                badge.setAttribute('aria-hidden', 'true');
                title.appendChild(badge);
            }
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
    if (!label || !button)
        return;
    const origins = [label, body].map(node => node.closest('.silky-layout-cell')).filter(Boolean);
    const host = document.createElement('div');
    const lifecycle = new AbortController();
    const listen = (target, name, handler, capture = false) =>
        target.addEventListener(name, handler, { capture, signal: lifecycle.signal });
    host.className = 'mzpj-service-header';
    host.setAttribute('role', 'group');
    host.setAttribute('aria-label', 'Service script');
    // La rimozione modifica il DOM durante il clic: annulla anche l'attivazione
    // predefinita e gli handler esterni, senza inoltrare il clic a Browse.
    listen(host, 'click', event => {
        const target = event.target;
        const remove = target && target.closest ? target.closest('.jmv-file-selector-remove') : null;
        if (!remove || !host.contains(remove))
            return;
        if (!control || typeof control.setValue !== 'function')
            return;
        event.preventDefault();
        event.stopPropagation();
        dismissTooltip();
        if (!remove.disabled) {
            // scriptFile e' un File singolo: [] e' il valore nativo senza file.
            control.setValue([]);
            // Ripristina il focus dopo la rimozione, senza aprire il suggerimento Service.
            restoringFocus = true;
            try {
                button.focus();
            } finally {
                restoringFocus = false;
            }
        }
    }, true);
    // Conserva il nodo del controllo nativo, ma il nome visibile e' sul pulsante.
    label.removeAttribute('title');
    label.classList.add('mzpj-service-label');
    button.textContent = 'Service…';
    button.setAttribute('aria-label', 'Load a Python service script');
    button.removeAttribute('title');
    host.appendChild(label);
    host.appendChild(body);
    const tooltip = document.createElement('div');
    tooltip.className = 'mzpj-service-tooltip';
    tooltip.id = button.id + '-service-help';
    tooltip.setAttribute('role', 'tooltip');
    tooltip.hidden = true;
    const tooltipTitle = document.createElement('span');
    tooltipTitle.textContent = 'Load a Python service script.';
    const tooltipDetail = document.createElement('span');
    tooltipDetail.textContent = 'Runs before editor code; not shown in the editor.';
    tooltip.append(tooltipTitle, tooltipDetail);
    host.appendChild(tooltip);
    const describedBy = (button.getAttribute('aria-describedby') || '').split(/\s+/).filter(Boolean);
    button.setAttribute('aria-describedby', [...describedBy, tooltip.id].join(' '));
    let activeButton = null;
    let activation = null;
    let keyboardNavigation = false;
    let restoringFocus = false;
    // Il tooltip non intercetta il mouse: uscire dal pulsante lo chiude senza attese.
    const hideTooltip = () => {
        tooltip.hidden = true;
        activeButton = null;
        activation = null;
    };
    const dismissTooltip = () => {
        keyboardNavigation = false;
        hideTooltip();
    };
    const showTooltip = (anchorButton, source) => {
        if (!anchorButton || !anchorButton.isConnected || anchorButton.disabled)
            return;
        activeButton = anchorButton;
        activation = source;
        const removing = anchorButton !== button;
        tooltipTitle.textContent = removing ? 'Remove service script.' : 'Load a Python service script.';
        tooltipDetail.hidden = removing;
        tooltip.hidden = false;
        const anchor = anchorButton.getBoundingClientRect();
        const rect = tooltip.getBoundingClientRect();
        const left = Math.max(8, Math.min(anchor.left, window.innerWidth - rect.width - 8));
        const top = anchor.bottom + 7 + rect.height <= window.innerHeight - 8 ?
            anchor.bottom + 7 : Math.max(8, anchor.top - rect.height - 7);
        tooltip.style.left = left + 'px';
        tooltip.style.top = top + 'px';
    };
    const anchorTarget = event => {
        const node = event.target && event.target.closest ? event.target.closest('button') : null;
        return node && host.contains(node) &&
            (node === button || node.classList.contains('jmv-file-selector-remove')) ? node : null;
    };
    listen(host, 'mouseover', event => {
        const anchor = anchorTarget(event);
        if (anchor && !anchor.contains(event.relatedTarget)) {
            showTooltip(anchor, 'pointer');
        }
    });
    listen(host, 'mouseout', event => {
        const anchor = anchorTarget(event);
        if (anchor && !anchor.contains(event.relatedTarget) && activeButton === anchor &&
                activation === 'pointer')
            hideTooltip();
    });
    listen(host, 'mousedown', event => {
        if (anchorTarget(event))
            dismissTooltip();
    });
    listen(host, 'click', event => {
        if (anchorTarget(event))
            dismissTooltip();
    });
    listen(host, 'focusin', event => {
        const anchor = anchorTarget(event);
        // Solo il focus ottenuto con la tastiera mostra il suggerimento persistente.
        if (anchor && keyboardNavigation && !restoringFocus)
            showTooltip(anchor, 'keyboard');
    });
    listen(host, 'focusout', event => {
        if (anchorTarget(event) === activeButton && activation === 'keyboard')
            hideTooltip();
    });
    listen(host, 'keydown', event => {
        if (anchorTarget(event) && event.key === 'Escape') {
            dismissTooltip();
            event.stopPropagation();
        }
    });
    // La modalita di ingresso riguarda soltanto il pannello del modulo, non il documento intero.
    const focusScope = block || header.parentElement || view;
    listen(focusScope, 'keydown', event => {
        if (event.key === 'Tab')
            keyboardNavigation = true;
    }, true);
    listen(focusScope, 'mousedown', dismissTooltip, true);
    // Il selettore ricrea la pillola: elimina il titolo nativo anche sui nuovi nodi.
    const prepareRemoveButtons = () => {
        body.querySelectorAll('.jmv-file-selector-remove').forEach(remove => {
            remove.setAttribute('title', '');
            const ids = (remove.getAttribute('aria-describedby') || '').split(/\s+/).filter(Boolean);
            if (!ids.includes(tooltip.id))
                remove.setAttribute('aria-describedby', [...ids, tooltip.id].join(' '));
        });
        if (activeButton && (!activeButton.isConnected || activeButton.disabled))
            dismissTooltip();
    };
    prepareRemoveButtons();
    const fileObserver = new MutationObserver(prepareRemoveButtons);
    fileObserver.observe(body, {
        childList: true, subtree: true, attributes: true, attributeFilter: ['disabled']
    });
    listen(view, 'scroll', dismissTooltip, true);
    listen(window, 'resize', dismissTooltip);
    listen(window, 'blur', dismissTooltip);
    const back = header.querySelector('.silky-sp-back-button');
    header.insertBefore(host, back && back.parentElement === header ? back : null);
    header.classList.add('mzpj-editor-header');
    // Le celle rimangono nel modello del layout, ma non occupano piu’ spazio.
    origins.forEach(cell => cell.classList.add('mzpj-service-origin'));
    // I nodi spostati nell'intestazione devono seguire il ciclo di vita del controllo File.
    const dispose = () => {
        hideTooltip();
        fileObserver.disconnect();
        lifecycle.abort();
        host.remove();
    };
    if (control && typeof control.once === 'function')
        control.once('disposing', dispose);
    else if (control && typeof control.on === 'function')
        control.on('disposing', dispose);
    return dispose;

};
