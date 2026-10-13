// JSON produce letterali stringa validi anche in Python, inclusi apici e controlli.
const pythonString = value => JSON.stringify(String(value));
const keywords = new Set(('False None True and as assert async await break class continue def del ' +
    'elif else except finally for from global if import in is lambda nonlocal not or pass raise ' +
    'return try while with yield').split(' '));

function context(before) {
    let quote = null;
    let escaped = false;
    for (let i = 0; i < before.length; i++) {
        const char = before[i];
        if (quote) {
            if (escaped)
                escaped = false;
            else if (char === '\\')
                escaped = true;
            else if (before.slice(i, i + quote.length) === quote) {
                i += quote.length - 1;
                quote = null;
            }
        } else if (char === '#')
            return 'comment';
        else if (char === "'" || char === '"') {
            quote = before.slice(i, i + 3) === char.repeat(3) ? char.repeat(3) : char;
            i += quote.length - 1;
        }
    }
    return quote ? 'string' : '';
}

function variables(names) {
    const entries = [];
    names = Array.isArray(names) ? names.filter(name => typeof name === 'string') : [];
    for (const name of names) {
        const literal = pythonString(name);
        for (const value of [literal, 'data[' + literal + ']'])
            entries.push({ name: value, value, meta: 'variable', type: 'var' });
        if (/^[A-Za-z_][A-Za-z0-9_]*$/.test(name) && !keywords.has(name))
            entries.push({ name, value: name, meta: 'variable', type: 'var' });
    }
    return entries;
}

module.exports = { pythonString, context, variables };
