// Caricamento passivo, bozza e salvataggio condivisi da Pj e Pjp.
module.exports = function(ui, $contents) {
        this.$filename = $contents.querySelector('#editor-filename');
        this.$fileInput = $contents.querySelector('#editor-file');
        this.$message = $contents.querySelector('#editor-message');
        this.$replace = $contents.querySelector('#editor-replace');
        this.pendingScript = null;
        this.showEditorMessage = (message) => {
            this.$message.textContent = message;
            this.$message.hidden = !message;
        };
        this.refreshEditorFilename = () => {
            const state = this.currentSession.pjState;
            const modified = this.currentSession.getValue() !== state.baseline;
            this.$filename.textContent = (state.filename || 'Untitled') + (modified ? ' *' : '');
            this.$filename.title = state.filename || 'Untitled';
        };
        this.persistEditor = () => {
            const session = this.currentSession;
            session.pjState.draft = session.getValue();
            session.pjState.hasDraft = true;
            ui.editorState.setValue(Object.assign({}, session.pjState));
            this.refreshEditorFilename();
        };
        this.replaceEditorScript = () => {
            const pending = this.pendingScript;
            this.pendingScript = null;
            this.$replace.hidden = true;
            if (!pending || pending.session !== this.currentSession)
                return;
            this.currentSession.pjState.filename = pending.filename;
            this.currentSession.pjState.baseline = pending.code;
            this.currentSession.setValue(pending.code);
            this.persistEditor();
            this.editor.gotoLine(1, 0, false);
            this.editor.focus();
        };
        $contents.querySelector('#load-script').addEventListener('click', () => {
            this.showEditorMessage('');
            this.$fileInput.click();
        });
        this.$fileInput.addEventListener('change', () => {
            const file = this.$fileInput.files[0];
            this.$fileInput.value = '';
            if (!file)
                return;
            if (!/\.py$/i.test(file.name)) {
                this.showEditorMessage('Choose a Python script (.py).');
                return;
            }
            const session = this.currentSession;
            const request = this.fileRequest = (this.fileRequest || 0) + 1;
            const reader = new FileReader();
            reader.onerror = () => {
                if (session === this.currentSession && request === this.fileRequest)
                    this.showEditorMessage('Unable to read the selected script.');
            };
            reader.onload = () => {
                if (session !== this.currentSession || request !== this.fileRequest)
                    return;
                this.pendingScript = {
                    session, filename: file.name,
                    code: String(reader.result).replace(/^\uFEFF/, '').replace(/\r\n?/g, '\n')
                };
                if (session.getValue().trim()) {
                    this.$replace.hidden = false;
                    $contents.querySelector('#cancel-script').focus();
                }
                else
                    this.replaceEditorScript();
            };
            reader.readAsText(file, 'UTF-8');
        });
        $contents.querySelector('#replace-script').addEventListener('click', () => this.replaceEditorScript());
        $contents.querySelector('#cancel-script').addEventListener('click', () => {
            this.pendingScript = null;
            this.$replace.hidden = true;
            this.editor.focus();
        });
        $contents.querySelector('#save-script').addEventListener('click', () => {
            ui.view.model.options.beginEdit();
            try {
                this.persistEditor();
                ui.saveEditorScript.setValue(true);
            } finally {
                ui.view.model.options.endEdit();
            }
        });
        $contents.querySelector('#clear-script').addEventListener('click', () => {
            const session = this.currentSession;
            if (!session)
                return;
            // Invalida Run e letture ancora in attesa prima di svuotare la bozza.
            this.runRequest = (this.runRequest || 0) + 1;
            this.fileRequest = (this.fileRequest || 0) + 1;
            this.pendingScript = null;
            this.$replace.hidden = true;
            this.showEditorMessage('');
            ui.view.model.options.beginEdit();
            try {
                session.pjState = { draft: '', hasDraft: true, filename: '', baseline: '' };
                session.allColumns = false;
                session.setValue('');
                this.persistEditor();
                ui.code.setValue('');
                ui.editorCleared.setValue(true);
                ui.toggle.setValue(!ui.toggle.value());
            } finally {
                ui.view.model.options.endEdit();
            }
            this.editor.gotoLine(1, 0, false);
            this.editor.focus();
        });
};
