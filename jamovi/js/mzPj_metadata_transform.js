// Inserisce i metadati durante la compilazione, senza leggere file nel browser.
const fs = require('fs');
const path = require('path');
const { Transform } = require('stream');

module.exports = function(file) {
    // jmvtools copia il modulo in build/js prima di eseguire Browserify.
    const isMain = path.basename(file) === 'main.js';
    let contents = '';
    return new Transform({
        transform(chunk, encoding, callback) {
            if (isMain)
                contents += chunk.toString('utf8');
            else
                this.push(chunk);
            callback();
        },
        flush(callback) {
            if (!isMain)
                return callback();
            try {
                const metadata = fs.readFileSync(path.resolve(__dirname, '../0000.yaml'), 'utf8');
                const description = fs.readFileSync(path.resolve(__dirname, '../../DESCRIPTION'), 'utf8');
                const yamlVersion = metadata.match(/^version:\s*['"]?([0-9]+\.[0-9]+\.[0-9]+)['"]?\s*$/m);
                const rVersion = description.match(/^Version:\s*([0-9]+\.[0-9]+\.[0-9]+)\s*$/m);
                if (!yamlVersion || !rVersion || yamlVersion[1] !== rVersion[1])
                    throw new Error('Pj version must match in DESCRIPTION and jamovi/0000.yaml.');
                this.push(contents.replace(/(['"])__MZPJ_MODULE_VERSION__\1/g, JSON.stringify(yamlVersion[1])));
                callback();
            }
            catch (error) {
                callback(error);
            }
        }
    });
};
