// Ogni richiesta resta associata alla sessione che l’ha avviata.
module.exports = async function(ui) {

            const session = this.currentSession;
            const request = this.runRequest = (this.runRequest || 0) + 1;
            let script = session.getDocument().getValue();
            script = script.replace(/[\r\u200B-\u200D\uFEFF]/g, '');

            let columns = [ ];
            try {
                if (window.name === 'Pj-Pj')
                    columns = await this.getColumnNames();
            } catch (error) {
                if (session === this.currentSession && request === this.runRequest)
                    this.showEditorMessage('Unable to read dataset columns. Please try again.');
                return;
            }
            if (session !== this.currentSession || request !== this.runRequest)
                return;
            this.showEditorMessage('');

            ui.view.model.options.beginEdit();
            try {

            ui.figWidth.setValue(this.$figWidth.value);
            ui.figHeight.setValue(this.$figHeight.value);
            ui.output.setValue(this.$output.value);
            ui.python.setValue(this.$python.value);
            ui.editorCleared.setValue(false);

            if (window.name === 'Pj-Pj') {
                let match = script.match(/^\s*\#\s*\((.*)\)/);
                if (match !== null) {
                    let content = match[1];
                    let vars = content.split(',');
                    vars = vars.map(s => s.trim());
                    vars = vars.filter(v => columns.includes(v));
                    ui.vars.setValue(vars);
                    ui.code.setValue(script);
                    session.allColumns = false;
                }
                else {
                    ui.vars.setValue(columns);
                    ui.code.setValue(script);
                    session.allColumns = true;
                }
            }
            else {
                ui.code.setValue(script);
            }

            // Inverte l'opzione per rieseguire l'analisi anche senza altre modifiche.
            ui.toggle.setValue( ! ui.toggle.value());

            } finally {
                ui.view.model.options.endEdit();
            }

            this.editor.focus();
};
