const funcs = require('./funcs');
const contextService = require('./mzPj_editor_context');

module.exports = function(columnSource) {
    this.identifierRegexps = [/[A-Za-z0-9_\.]/];
    this.getCompletions = (editor, session, pos, prefix, callback) => {
        const line = session.getDocument().getLine(pos.row);
        const before = line.substring(0, Math.max(0, pos.column - prefix.length));
        // Ace riconosce anche stringhe multilinea iniziate nelle righe precedenti.
        const token = session.getTokenAt ? session.getTokenAt(pos.row, Math.max(0, pos.column - prefix.length)) : null;
        if (contextService.context(before) || (token && /(?:string|comment)/.test(token.type))) {
            callback(null, []);
            return;
        }
        const base = funcs.filter(entry => entry.value.toLowerCase().startsWith(prefix.toLowerCase()));
        const finish = names => {
            const entries = base.concat(contextService.variables(names));
            callback(null, entries.map((entry, index) => Object.assign({}, entry, {
                completer: this,
                score: entries.length - index + (entry.value.startsWith(prefix) ? 1000 : 0)
            })));
        };
        // Una richiesta rifiutata mantiene disponibili i suggerimenti statici.
        Promise.resolve().then(() => columnSource()).then(finish, () => finish([]));
    };
    this.insertMatch = (editor, entry) => {
        if (entry.type === 'func') {
            editor.completer.insertMatch({value: entry.value.replace('()', '') + '()'});
            const pos = editor.getCursorPosition();
            if (pos.column > 0) {
                pos.column -= 1;
                editor.moveCursorToPosition(pos);
            }
        } else
            editor.completer.insertMatch({value: entry.value});
    };
};
