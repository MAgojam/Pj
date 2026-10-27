/* jamovi/js/main.js - Pj (Python for jamovi): editor Ace in modalità Python, toolbar/menu di configurazione e autocompletamento */

const ace = require('brace');

require('brace/mode/python');
require('brace/ext/language_tools');

require('./css');
const Suggest = require('./suggest');
const initEditorFiles = require('./mzPj_editor_files');
const runEditor = require('./mzPj_editor_run');
const placeServiceHeader = require('./mzPj_service_header');
const SuggestIcons = require('./suggesticons');
// Sostituito dal compilatore leggendo 0000.yaml e verificando DESCRIPTION.
const moduleVersion = '__MZPJ_MODULE_VERSION__';

function arrayEquals(a, b) {
    return Array.isArray(a) &&
        Array.isArray(b) &&
        a.length === b.length &&
        a.every((val, index) => val === b[index]);
}

// ────────────────────────────────────────────────────────────────────
// STILE VARIABLE SUPPLIER (solo Pjp: Pj non ha VariableSupplier in
// pj.u.yaml, quindi qui è un no-op sicuro). Le variabili selezionate
// diventano il dizionario `data` nel codice Python - le classi pj-vs-*
// sono definite in jamovi/js/css.js.
// ────────────────────────────────────────────────────────────────────
function hasValue(val) {
    return Array.isArray(val) && val.length > 0 && val[0] !== '';
}

function styleVariableSupplier(ui) {
    let field = ui.vars;
    if (field && field.el) {
        let filled = hasValue(field.value());
        field.el.classList.add('pj-vs-target');
        field.el.classList.toggle('pj-vs-filled', filled);
        field.el.classList.toggle('pj-vs-empty', ! filled);
    }

    let sourceList = document.querySelector('jmv-selectgrid.silky-variable-supplier');
    if (sourceList)
        sourceList.classList.add('pj-vs-source');

    document.querySelectorAll('button.jmv-variable-transfer').forEach((btn) => {
        btn.classList.add('pj-vs-transfer-btn');
    });
}

// ────────────────────────────────────────────────────────────────────
// ACCORDION "Variables" (solo Pjp): CustomControl al posto del
// CollapseBox nativo (pjpAccordion in pjp.a.yaml/pjp.u.yaml). Lo stato
// aperto/chiuso e' l'opzione Bool nascosta pjpAccordion, quindi viene
// persistito con l'analisi. Su Pj (senza questo CustomControl)
// ui.pjpAccordion e' undefined, quindi tutto qui sotto e' un no-op.
// ────────────────────────────────────────────────────────────────────
function findAccordionContent(ui) {
    let header = ui.pjpAccordion && ui.pjpAccordion.el;
    let target = ui.vars && ui.vars.el;
    if ( ! header || ! target)
        return null;

    // Trova l'antenato comune tra header e target (approccio robusto,
    // indipendente da quanti livelli di wrapper jamovi frappone tra un
    // controllo dichiarato in yaml e il suo nodo DOM effettivo): risale
    // da target finche' non incontra un nodo che e' anche antenato
    // dell'header. Il nodo immediatamente precedente su quel ramo e' il
    // contenitore "fratello" da mostrare/nascondere.
    let headerAncestors = new Set();
    for (let node = header; node; node = node.parentElement)
        headerAncestors.add(node);

    let node = target;
    let prev = null;
    while (node && ! headerAncestors.has(node)) {
        prev = node;
        node = node.parentElement;
    }

    return prev;
}

function applyAccordionState(ui) {
    let header = ui.pjpAccordion && ui.pjpAccordion.el;
    if ( ! header)
        return;

    let expanded = header._pjExpanded !== false;
    header.classList.toggle('pj-accordion-expanded', expanded);

    let content = findAccordionContent(ui);
    if (content) {
        content.classList.add('pj-accordion-content');
        content.classList.toggle('pj-accordion-expanded', expanded);
    }
}

function initAccordionHeader(ui) {
    let header = ui.pjpAccordion && ui.pjpAccordion.el;
    // guard: non ricostruire il markup se gia' inizializzato (puo' essere
    // chiamata sia da 'creating' che da 'loaded'/'update' come ridondanza,
    // visto che il binding per naming-convention (pjpAccordion_creating) su
    // alcune installazioni jamovi Desktop locali risulta inaffidabile)
    if ( ! header || header.dataset.pjInit)
        return;
    header.dataset.pjInit = '1';
    header._pjExpanded = true; // stato iniziale: aperto (CustomControl non
    // e' associato ad alcuna opzione - vedi customcontrol.ts - quindi lo
    // stato si tiene qui, non su un'opzione persistita)

    header.classList.add('pj-accordion-header');
    header.setAttribute('role', 'button');
    header.tabIndex = 0;

    header.innerHTML = `
        <span class="pj-accordion-icon-container">
            <svg class="pj-plus-minus-icon" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2">
                <line class="horizontal" x1="4" y1="8" x2="12" y2="8"></line>
                <line class="vertical" x1="8" y1="4" x2="8" y2="12"></line>
            </svg>
        </span>
        <span class="pj-accordion-title">Variables</span>`;

    let toggle = () => {
        header._pjExpanded = ! header._pjExpanded;
        applyAccordionState(ui);
    };

    header.addEventListener('click', toggle);
    header.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            toggle();
        }
    });

    applyAccordionState(ui);
}


const events = {
    loaded(ui) {

        this.editSessions = { };

        let $contents = ui.view.el;
        $contents.style.display = 'flex';
        $contents.style.flexDirection = 'column';

        $contents.insertAdjacentHTML('beforeend', `
            <div id="editor-box">
                <div id="toolbar">
                    <div id="editor-heading"><button type="button" id="clear-script" title="Clear editor and results" aria-label="Clear editor and results">Clear</button><span>Python editor</span><span id="editor-filename"></span></div>
                    <div id="editor-actions">
                        <div id="script-actions" role="group" aria-labelledby="scripts-label">
                            <span id="scripts-label">Scripts</span>
                            <button type="button" id="load-script" title="Load a Python script into the editor">Load</button>
                            <button type="button" id="save-script" title="Save the editor code as a Python script">Save</button>
                        </div>
                        <div id="config-container">
                            <button type="button" id="config" title="Settings" aria-label="Settings" aria-expanded="false" aria-controls="menu">
                                <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round">
                                    <path d="M4 6h16M4 12h16M4 18h16"/>
                                    <circle cx="9" cy="6" r="2.2"/><circle cx="16" cy="12" r="2.2"/><circle cx="8" cy="18" r="2.2"/>
                                </svg>
                            </button>
                        </div>
                        <button type="button" id="run" title="Run" aria-label="Run">
                            <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" fill="currentColor"><path d="M8 5.5a1 1 0 0 1 1.5-.86l10 6a1 1 0 0 1 0 1.72l-10 6A1 1 0 0 1 8 17.5Z"/></svg>
                        </button>
                    </div>
                </div>
                <input type="file" id="editor-file" accept=".py" hidden>
                <div id="editor-message" role="status" hidden></div>
                <div id="editor-replace" hidden>
                    <span>Replace the current editor code?</span>
                    <button type="button" id="replace-script">Replace</button>
                    <button type="button" id="cancel-script">Cancel</button>
                </div>
                <div id="editor"></div>
                <div id="info">Ctrl + Shift + Enter to run</div>
            </div>`);

        let $config = $contents.querySelector('#config');
        
        $config.insertAdjacentHTML('afterend', `
            <div id="menu" inert aria-hidden="true">
                <label id="code-label"><span>Python Code</span><span id="pj-module-version"></span></label>
                <div id="python-setting" class="pj-setting-row">
                    <label id="python-label" for="python-version">Python Version</label>
                    <select id="python-version">
                        <option value="bundled">jamovi Python</option>
                        <option value="external">System Python</option>
                    </select>
                </div>
                <div id="output-setting" class="pj-setting-row">
                    <label id="output-label" for="output">Output</label>
                    <select id="output">
                        <option value="noEcho">Show output only</option>
                        <option value="echo">Show code and output</option>
                        <option value="pyinfo">Show Python info</option>
                    </select>
                </div>
                <div id="figure-size">
                    <div id="figure-size-title">Figure size (px)</div>
                    <div id="figure-size-row">
                        <label for="figure-width">Width</label>
                        <input id="figure-width" placeholder="Default" title="Images: leave both fields blank to fit within 800 × 600 px without enlarging. Set one dimension to preserve proportions, or both for an exact size.">
                        <label for="figure-height">Height</label>
                        <input id="figure-height" placeholder="Default" title="Images: leave both fields blank to fit within 800 × 600 px without enlarging. Set one dimension to preserve proportions, or both for an exact size.">
                    </div>
                </div>
            </div>`);

        this.$editor = $contents.querySelector('#editor');
        $contents.querySelector('#pj-module-version').textContent = 'Pj v' + moduleVersion;
        this.$run = $contents.querySelector('#run');
        this.$config = $config;
        this.$menu = $contents.querySelector('#menu');

        this.$run.addEventListener('click', () => this.run(ui));

        initEditorFiles.call(this, ui, $contents);

        this.$output = $contents.querySelector('#output');
        this.$output.addEventListener('change', (event) => {
            ui.output.setValue(this.$output.value);
        });

        this.$python = $contents.querySelector('#python-version');
        this.$python.addEventListener('change', (event) => {
            ui.python.setValue(this.$python.value);
        });

        this.$figWidth = $contents.querySelector('#figure-width');
        this.$figHeight = $contents.querySelector('#figure-height');

        // Popup trascinabile: mousedown su etichette/aree vuote (non sui
        // controlli stessi, altrimenti si romperebbe il click su
        // select/input/button) passa da position:absolute a position:fixed,
        // mantenendo la posizione visuale corrente, poi segue il mouse.
        let dragState = null;

        this.$menu.addEventListener('mousedown', (event) => {
            let tag = event.target.tagName;
            if (tag === 'SELECT' || tag === 'INPUT' || tag === 'OPTION' || tag === 'BUTTON')
                return;

            let rect = this.$menu.getBoundingClientRect();
            dragState = {
                startX: event.clientX,
                startY: event.clientY,
                startLeft: rect.left,
                startTop: rect.top
            };
            this.$menu.style.position = 'fixed';
            this.$menu.style.left = dragState.startLeft + 'px';
            this.$menu.style.top = dragState.startTop + 'px';
            this.$menu.style.right = 'auto';
            event.preventDefault();
        });

        document.addEventListener('mousemove', (event) => {
            if ( ! dragState)
                return;
            let dx = event.clientX - dragState.startX;
            let dy = event.clientY - dragState.startY;
            this.$menu.style.left = (dragState.startLeft + dx) + 'px';
            this.$menu.style.top = (dragState.startTop + dy) + 'px';
        });

        document.addEventListener('mouseup', () => {
            dragState = null;
        });

        this.$menu.querySelectorAll('input').forEach(el => el.addEventListener('keyup', (event) => {
            if (event.keyCode == 13)
                this.run(ui);
        }));

        $config.addEventListener('click', () => this.toggleMenu(ui));

        if (navigator.platform === 'MacIntel') {
            let $info = $contents.querySelector('#info');
            $info.textContent = '\u2318 + Shift + Enter to run';
        }

        this.editor = ace.edit('editor');

        this.editor.$blockScrolling = Infinity; // Disattiva l'avviso di scorrimento di Ace.
        this.editor.setShowPrintMargin(false);
        this.editor.setHighlightActiveLine(false);
        this.editor.focus();

        this.editor.setOptions({
            enableBasicAutocompletion: true,
        });

        this.editor.commands.on('afterExec', (event) => {
            let editor = event.editor;
            if (event.command.name == 'insertstring') {
                let position = editor.getCursorPosition();
                let line = editor.getSession().getDocument().getLine(position.row);
                let before = line.substring(0, position.column);
                // Avvia l'autocompletamento dopo lettere/underscore/punto (es. "np.", "stats.", "data['..."):
                // copre sia i moduli importati sia l'accesso al dataset
                if (/^[\w.]$/.test(event.args) && /[A-Za-z0-9_\.]{3}$/.test(before))
                    editor.execCommand('startAutocomplete');
            }
            else if (event.command.name == 'backspace' &&
                editor.completer &&
                editor.completer.activated)
                    editor.execCommand('startAutocomplete');
            else if (event.command.name === 'startAutocomplete')
                SuggestIcons.add(event.editor);
        });

        this.editor.commands.on('exec', (event) => {
            if (event.command.name === 'indent') {
                let editor = event.editor;
                let position = editor.getCursorPosition();
                let line = editor.getSession().getDocument().getLine(position.row);
                let before = line.substring(0, position.column);
                // Solo dopo identificatore/punto: cosi' Tab indenta normalmente dopo un ':'
                // di fine blocco (if/for/def...), come atteso in Python
                if (/[A-Za-z0-9_\.]$/.test(before)) {
                    editor.execCommand('startAutocomplete');
                    event.preventDefault();
                }
            }
            else if (event.command.name === 'paste') {
                // Elimina i caratteri invisibili che possono comparire nel testo incollato.
                event.args.text = event.args.text.replace(/[\r\u200B-\u200D\uFEFF]/g, '');
            }
        });

        // Rimuove i completatori predefiniti di Ace.
        this.editor.completers.splice(0, this.editor.completers.length);

        // Aggiunge il completatore Python del modulo.
        this.editor.completers.push(new Suggest(() => {
            return this.getColumnNames();
        }));

        this.getColumnNames = () => {
            return this.requestData('columns', {  })
                .then((data) => {
                    return data.columns.map(col => col.name);
                }).then((names) => {
                    // Esclude le colonne filtro iniziali di jamovi.
                    let index = 0;
                    for (;index < names.length; index++) {
                        let name = names[index];
                        if (/^Filter [1-9][0-9]*$/.exec(name) ||
                            /^F[1-9][0-9]* \([1-9][0-9]*\)$/.exec(name))
                                continue; // Colonna filtro.
                        else
                            break; // Prima colonna diversa da un filtro.
                    }
                    return names.slice(index);
                });
        };

        this.toggleMenu = (ui) => {
            if ( ! this.$menu.classList.contains('visible'))
                this.showMenu(ui);
            else
                this.hideMenu(ui);
        };

        this.showMenu = (ui) => {
            this.$menu.removeAttribute('inert');
            this.$menu.setAttribute('aria-hidden', 'false');
            this.$menu.classList.add('visible');
            this.$config.setAttribute('aria-expanded', 'true');
        };

        this.hideMenu = (ui) => {
            if (this.$menu.contains(document.activeElement))
                this.$config.focus();
            this.$menu.setAttribute('inert', '');
            this.$menu.setAttribute('aria-hidden', 'true');
            this.$menu.classList.remove('visible');
            this.$config.setAttribute('aria-expanded', 'false');

            ui.view.model.options.beginEdit();
            ui.figWidth.setValue(this.$figWidth.value);
            ui.figHeight.setValue(this.$figHeight.value);
            ui.output.setValue(this.$output.value);
            ui.python.setValue(this.$python.value);
            ui.view.model.options.endEdit();
        };

        this.run = (ui) => runEditor.call(this, ui);

        this.$editor.addEventListener('keydown', (event) => {

            if (event.keyCode === 13 && (event.metaKey || event.ctrlKey) && event.shiftKey) {
                // ctrl+shift+enter
                this.run(ui);
                event.stopPropagation();
            }
            else if (event.keyCode === 65 && event.metaKey) {
                // ctrl+a
                this.$editor.select();
            }
            else if (event.keyCode === 67 && (event.metaKey || event.ctrlKey) && event.shiftKey)             {
                // ctrl+shift+c
                this.editor.toggleCommentLines();
            }
            else if (event.keyCode === 191 && (event.metaKey || event.ctrlKey)) {
                // ctrl+/
                this.editor.toggleCommentLines();
            }
        });

        styleVariableSupplier(ui);
        initAccordionHeader(ui);

        placeServiceHeader(ui);
    },

    onDataChanged(ui, event) {
        if (!this.currentSession || !this.currentSession.allColumns)
            return;
        if (event.dataType !== 'columns')
            return;
        const session = this.currentSession;
        this.getColumnNames().then((columns) => {
            if (session !== this.currentSession)
                return;
            let old = ui.vars.value();
            if ( ! arrayEquals(old, columns))
                ui.vars.setValue(columns);
        }, () => this.showEditorMessage('Unable to refresh dataset columns.'));
        styleVariableSupplier(ui);
    },

    onChange_vars(ui, event) {
        styleVariableSupplier(ui);
    },

    pjpAccordion_creating(ui, event) {
        initAccordionHeader(ui);
    },

    update(ui, event) {

        let id = event.id;
        if (this.currentAnalysisId !== id) {
            this.runRequest = (this.runRequest || 0) + 1;
            this.fileRequest = (this.fileRequest || 0) + 1;
        }
        this.currentAnalysisId = id;
        this.currentSession = this.editSessions[id];

        if (this.currentSession === undefined) {

            const stored = ui.editorState.value() || {};
            const code = stored.hasDraft ? stored.draft : ui.code.value();
            const session = ace.createEditSession(code, 'ace/mode/python');
            session.pjState = {
                draft: code, hasDraft: !!stored.hasDraft,
                filename: stored.filename || '',
                baseline: stored.hasDraft ? stored.baseline : code
            };
            this.currentSession = session;
            this.editSessions[id] = session;
            session.on('change', () => {
                if (session === this.currentSession)
                    this.persistEditor();
            });
        }

        this.editor.setSession(this.currentSession);
        this.refreshEditorFilename();
        if (this.pendingScript && this.pendingScript.session !== this.currentSession) {
            this.pendingScript = null;
            this.$replace.hidden = true;
        }

        this.$figWidth.value = ui.figWidth.value();
        this.$figHeight.value = ui.figHeight.value();
        this.$output.value = ui.output.value();
        this.$python.value = ui.python.value();
        styleVariableSupplier(ui);
        initAccordionHeader(ui);
        applyAccordionState(ui);
        placeServiceHeader(ui);
    },
};


module.exports = events;
