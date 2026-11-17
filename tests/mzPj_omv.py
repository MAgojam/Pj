# Verifica lettura e scrittura .omv: archivi nello stile del writer di jamovi, round trip e errori.
import json
import math
import struct
import tempfile
import unittest
import zipfile
from unittest.mock import patch
from pathlib import Path

ns = {}
exec((Path(__file__).resolve().parents[1] / 'inst/python/mzPj_omv.py').read_text(encoding='utf-8'), ns)
read = ns['mzpjReadOmv']
write = ns['mzpjWriteOmv']
MISSING = -2147483648


def jamovi_style_archive(path, fields, columns, xdata=None, manifest=None, row_count=None, weights=None):
    """Costruisce un archivio come fa jamovi/server/formatio/omv.py (scrittura, versione 11.0).

    columns: per ogni campo la lista di valori grezzi (interi, double, oppure testi per le ID).
    """
    if row_count is None:
        row_count = len(columns[0]) if columns else 0
    data_bin = bytearray()
    strings = bytearray()
    for field, values in zip(fields, columns):
        if field.get('dataType') == 'Decimal':
            for value in values:
                data_bin += struct.pack('<d', value)
        elif field.get('dataType') == 'Text' and field.get('measureType') == 'ID':
            for value in values:
                if value != '':
                    encoded = value.encode('utf-8')
                    data_bin += struct.pack('<i', len(strings))
                    strings += encoded + bytes(1)
                else:
                    data_bin += struct.pack('<i', MISSING)
        else:
            for value in values:
                data_bin += struct.pack('<i', value)
    if manifest is None:
        manifest = ('Manifest-Version: 1.0\nData-Archive-Version: 1.0.2\n'
                    'jamovi-Archive-Version: 11.0\nCreated-By: jamovi 28.17.0.0\n')
    metadata = {
        'document': {'resultsLanguage': 'en'},
        'dataSet': {'rowCount': row_count, 'columnCount': len(fields), 'removedRows': [], 'addedRows': [],
                    'fields': fields, 'transforms': [], 'weights': weights},
    }
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('meta', manifest)
        archive.writestr('index.html', '<html></html>')
        archive.writestr('metadata.json', json.dumps(metadata))
        if xdata is not None:
            archive.writestr('xdata.json', json.dumps(xdata))
        archive.writestr('data.bin', bytes(data_bin))
        if strings:
            archive.writestr('strings.bin', bytes(strings))
        archive.writestr('01 Descriptives/analysis', b'\x08\x01')


def field(name, column_id, data_type, measure, column_type='Data', **extra):
    result = {
        'name': name, 'id': column_id, 'columnType': column_type, 'dataType': data_type,
        'measureType': measure, 'formula': '', 'formulaMessage': '', 'parentId': 0, 'width': 100,
        'type': {'Decimal': 'number'}.get(data_type, 'string' if measure == 'ID' and data_type == 'Text' else 'integer'),
        'importName': name, 'description': '', 'transform': 0, 'edits': [], 'missingValues': []}
    result.update(extra)
    return result


class OmvTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = str(Path(self.directory.name) / 'test.omv')

    def test_reads_archive_written_like_jamovi(self):
        fields = [
            field('who', 1, 'Text', 'ID'),
            field('age', 2, 'Integer', 'Continuous'),
            field('score', 3, 'Decimal', 'Continuous', description='A score'),
            field('grp', 4, 'Integer', 'Nominal', trimLevels=True),
            field('city', 5, 'Text', 'Nominal', trimLevels=True, missingValues=["== 'n/a'"]),
            field('Filter 1', 6, 'Integer', 'Nominal', column_type='Filter', width=78, filterNo=0, active=True),
        ]
        columns = [['p1', 'p\u00e8', '', 'p4'], [30, 41, MISSING, 25], [1.5, math.nan, 3.25, -0.5],
                   [0, 1, 1, 0], [1, 0, MISSING, 1], [1, 1, 0, 1]]
        six = lambda v, label: [v, label, label, False, False, False]
        xdata = {'grp': {'labels': [six(0, 'ctl'), six(1, 'trt')]},
                 'city': {'labels': [six(0, 'Roma'), six(1, 'Genova')]},
                 'Filter 1': {'labels': [six(0, '0'), six(1, '1')]}}
        jamovi_style_archive(self.path, fields, columns, xdata)
        result = read(self.path)
        self.assertEqual(result['row_count'], 4)
        self.assertEqual(result['archive_version'], (11, 0))
        self.assertEqual(list(result['data']), ['who', 'age', 'score', 'grp', 'city', 'Filter 1'])
        self.assertEqual(result['data']['who'], ['p1', 'p\u00e8', None, 'p4'])
        self.assertEqual(result['data']['age'], [30, 41, None, 25])
        self.assertEqual(result['data']['score'], [1.5, None, 3.25, -0.5])
        self.assertEqual(result['data']['grp'], ['ctl', 'trt', 'trt', 'ctl'])
        self.assertEqual(result['data']['city'], ['Genova', 'Roma', None, 'Genova'])
        self.assertEqual(result['data']['Filter 1'], [True, True, False, True])
        self.assertIn('01 Descriptives/analysis', result['entries'])
        columns_meta = {c['name']: c for c in result['columns']}
        self.assertEqual(columns_meta['score']['description'], 'A score')
        self.assertEqual(columns_meta['city']['missingValues'], ["== 'n/a'"])
        self.assertEqual(columns_meta['grp']['levels'][1], (1, 'trt', 'trt', False))
        self.assertEqual(columns_meta['Filter 1']['filterNo'], 0)
        # Codici grezzi.
        raw = read(self.path, labels=False)['data']
        self.assertEqual(raw['grp'], [0, 1, 1, 0])
        self.assertEqual(raw['city'], [1, 0, None, 1])

    def test_old_files_and_missing_xdata(self):
        fields = [{'name': 'a', 'id': 1, 'measureType': 'Continuous', 'type': 'number'},
                  {'name': 'b', 'id': 2, 'measureType': 'Nominal', 'type': 'integer'},
                  {'name': 'c', 'id': 3, 'measureType': 'Ordinal', 'type': 'integer'}]
        columns = [[0.5, 2.0], [7, 3], [MISSING, 2]]
        # Il builder scrive i dati per dataType; poi il dataType si toglie dal JSON come nei file vecchi.
        fields_with_types = [dict(fields[0], dataType='Decimal'), dict(fields[1], dataType='Integer'),
                             dict(fields[2], dataType='Integer')]
        jamovi_style_archive(self.path, fields_with_types, columns, xdata=None)
        with zipfile.ZipFile(self.path) as source:
            entries = {name: source.read(name) for name in source.namelist()}
        metadata = json.loads(entries['metadata.json'])
        for item in metadata['dataSet']['fields']:
            del item['dataType']
        entries['metadata.json'] = json.dumps(metadata).encode('utf-8')
        with zipfile.ZipFile(self.path, 'w') as target:
            for name, content in entries.items():
                target.writestr(name, content)
        result = read(self.path)
        columns_meta = {c['name']: c for c in result['columns']}
        self.assertEqual((columns_meta['a']['dataType'], columns_meta['a']['measureType']), ('Decimal', 'Continuous'))
        self.assertEqual((columns_meta['b']['dataType'], columns_meta['b']['measureType']), ('Integer', 'Nominal'))
        # xdata.json assente: livelli ricostruiti dai valori, nell'ordine di comparsa.
        self.assertEqual(columns_meta['b']['levels'], [(7, '7', '7', False), (3, '3', '3', False)])
        self.assertEqual(result['data']['b'], ['7', '3'])
        self.assertEqual(result['data']['c'], [None, '2'])
        self.assertEqual(result['data']['a'], [0.5, 2.0])

    def test_legacy_nominal_text_measure(self):
        fields = [{'name': 't', 'id': 1, 'measureType': 'NominalText', 'type': 'integer'}]
        jamovi_style_archive(self.path, [dict(fields[0], dataType='Integer')], [[0, 1, 0]],
                             {'t': {'labels': [[0, 'x'], [1, 'y']]}})
        with zipfile.ZipFile(self.path) as source:
            entries = {name: source.read(name) for name in source.namelist()}
        metadata = json.loads(entries['metadata.json'])
        del metadata['dataSet']['fields'][0]['dataType']
        entries['metadata.json'] = json.dumps(metadata).encode('utf-8')
        with zipfile.ZipFile(self.path, 'w') as target:
            for name, content in entries.items():
                target.writestr(name, content)
        result = read(self.path)
        self.assertEqual(result['columns'][0]['dataType'], 'Text')
        self.assertEqual(result['data']['t'], ['x', 'y', 'x'])

    def test_round_trip_inferred_types(self):
        data = {
            'n': [1, 2, None, 4],
            'x': [0.5, None, float('nan'), 2.25],
            'text': ['b', 'a', None, ''],
            'flag': [True, False, None, True],
            'whole': [1.0, 2.0, 3.0, None],
            'empty': [None, None, None, None],
        }
        summary = write(self.path, data)
        self.assertEqual(summary, {'path': self.path, 'row_count': 4, 'column_count': 6})
        result = read(self.path)
        self.assertEqual(result['data']['n'], [1, 2, None, 4])
        self.assertEqual(result['data']['x'], [0.5, None, None, 2.25])
        self.assertEqual(result['data']['text'], ['b', 'a', None, None])
        self.assertEqual(result['data']['flag'], ['TRUE', 'FALSE', None, 'TRUE'])
        self.assertEqual(result['data']['whole'], [1, 2, 3, None])
        self.assertEqual(result['data']['empty'], [None] * 4)
        kinds = {c['name']: (c['dataType'], c['measureType']) for c in result['columns']}
        self.assertEqual(kinds['n'], ('Integer', 'Continuous'))
        self.assertEqual(kinds['x'], ('Decimal', 'Continuous'))
        self.assertEqual(kinds['text'], ('Text', 'Nominal'))
        self.assertEqual(kinds['flag'], ('Integer', 'Nominal'))
        self.assertEqual(kinds['whole'], ('Integer', 'Continuous'))
        levels = {c['name']: c.get('levels') for c in result['columns']}
        self.assertEqual([item[:2] for item in levels['text']], [(0, 'a'), (1, 'b')])
        self.assertEqual([item[:2] for item in levels['flag']], [(1, 'TRUE'), (0, 'FALSE')])

    def test_archive_structure_matches_jamovi_writer(self):
        write(self.path, {'who': ['p1', 'p2', None, 'p\u00e8'], 'v': [1.5, 2.5, 3.5, 4.5], 'k': [3, 1, 2, 1]},
              {'who': {'measureType': 'ID'}, 'k': {'measureType': 'Ordinal'}})
        with zipfile.ZipFile(self.path) as archive:
            self.assertEqual(archive.namelist(), ['meta', 'metadata.json', 'xdata.json', 'data.bin', 'strings.bin'])
            manifest = archive.read('meta').decode('utf-8').splitlines()
            self.assertEqual(manifest[:3], ['Manifest-Version: 1.0', 'Data-Archive-Version: 1.0.2',
                                            'jamovi-Archive-Version: 11.0'])
            metadata = json.loads(archive.read('metadata.json'))
            xdata = json.loads(archive.read('xdata.json'))
            data_bin = archive.read('data.bin')
            strings = archive.read('strings.bin')
        dataset = metadata['dataSet']
        self.assertEqual(metadata['document'], {'resultsLanguage': 'en'})
        self.assertEqual(set(dataset), {'rowCount', 'columnCount', 'removedRows', 'addedRows', 'fields',
                                        'transforms', 'weights'})
        self.assertEqual(dataset['columnCount'], 3)
        # Chiavi dei campi come nel writer di jamovi per una colonna Data.
        base = {'name', 'id', 'columnType', 'dataType', 'measureType', 'formula', 'formulaMessage', 'parentId',
                'width', 'type', 'importName', 'description', 'transform', 'edits', 'missingValues'}
        by_name = {f['name']: f for f in dataset['fields']}
        self.assertEqual(set(by_name['who']), base)
        self.assertEqual(set(by_name['v']), base)
        self.assertEqual(set(by_name['k']), base | {'trimLevels'})
        self.assertEqual([f['id'] for f in dataset['fields']], [1, 2, 3])
        self.assertEqual((by_name['who']['type'], by_name['v']['type'], by_name['k']['type']),
                         ('string', 'number', 'integer'))
        # data.bin: 4 byte per riga per ID e intere, 8 per decimali.
        self.assertEqual(len(data_bin), 4 * 4 + 8 * 4 + 4 * 4)
        # Indici di stringa sequenziali (richiesto anche da jmvReadWrite) e -2147483648 per il mancante.
        offsets = struct.unpack_from('<4i', data_bin, 0)
        self.assertEqual(offsets, (0, 3, MISSING, 6))
        self.assertEqual(strings, b'p1\x00p2\x00p\xc3\xa8\x00')
        # Etichette a quattro elementi come jmvReadWrite; solo colonne con livelli.
        self.assertEqual(list(xdata), ['k'])
        self.assertEqual(xdata['k']['labels'], [[1, '1', '1', False], [2, '2', '2', False], [3, '3', '3', False]])

    def test_meta_levels_and_round_trip_of_read_metadata(self):
        data = {'likert': [1, 3, 2, None, 3], 'size': ['M', 'S', 'L', 'M', None]}
        meta = {'likert': {'measureType': 'Ordinal', 'description': 'Agreement',
                           'levels': [(1, 'Disagree'), (2, 'Neutral'), (3, 'Agree')], 'missingValues': ['== 99']},
                'size': {'measureType': 'Ordinal', 'levels': ['S', 'M', 'L']}}
        write(self.path, data, meta)
        first = read(self.path)
        self.assertEqual(first['data']['likert'], ['Disagree', 'Agree', 'Neutral', None, 'Agree'])
        self.assertEqual(first['data']['size'], ['M', 'S', 'L', 'M', None])
        by_name = {c['name']: c for c in first['columns']}
        self.assertEqual(by_name['size']['levels'][0][:2], (0, 'S'))
        self.assertEqual(by_name['likert']['missingValues'], ['== 99'])
        # Riscrittura con i metadati letti e i dati con etichette: stesso contenuto.
        second_path = str(Path(self.directory.name) / 'second.omv')
        write(second_path, first['data'], first['columns'])
        second = read(second_path)
        self.assertEqual(second['data'], first['data'])
        self.assertEqual(second['columns'], first['columns'])
        # Riscrittura con i codici grezzi.
        third_path = str(Path(self.directory.name) / 'third.omv')
        write(third_path, read(self.path, labels=False)['data'], first['columns'])
        self.assertEqual(read(third_path)['data'], first['data'])

    def test_weights_filter_and_html(self):
        data = {'w': [1.0, 2.5, 1.0], 'keep': [True, False, True]}
        meta = {'keep': {'columnType': 'Filter', 'filterNo': 0, 'active': True, 'formula': 'w < 2'}}
        write(self.path, data, meta, weights='w', html='<html>x</html>', results_language='it')
        result = read(self.path)
        self.assertEqual(result['weights'], 'w')
        self.assertEqual(result['results_language'], 'it')
        self.assertEqual(read(self.path, labels=False)['data']['keep'], [1, 0, 1])
        self.assertEqual(result['columns'][1]['formula'], '')
        self.assertEqual(result['columns'][1]['columnType'], 'Data')
        with zipfile.ZipFile(self.path) as archive:
            self.assertEqual(archive.read('index.html'), b'<html>x</html>')

    def test_empty_table_and_unicode_names(self):
        write(self.path, {'\u00e9t\u00e9': []})
        result = read(self.path)
        self.assertEqual(result['row_count'], 0)
        self.assertEqual(result['data'], {'\u00e9t\u00e9': []})

    def test_overwrite_and_atomic_failure(self):
        write(self.path, {'a': [1]})
        with self.assertRaises(FileExistsError):
            write(self.path, {'a': [2]})
        before = Path(self.path).read_bytes()
        with self.assertRaises(TypeError):
            write(self.path, {'a': [1, 'x']}, overwrite=True)
        self.assertEqual(Path(self.path).read_bytes(), before)
        write(self.path, {'a': [2]}, overwrite=True)
        self.assertEqual(read(self.path)['data']['a'], [2])
        self.assertEqual([p.name for p in Path(self.directory.name).iterdir()], ['test.omv'])

    def test_write_errors(self):
        bad = Path(self.directory.name)
        with self.assertRaises(ValueError): write(str(bad / 'x.csv'), {'a': [1]})
        with self.assertRaises(FileNotFoundError): write(str(bad / 'no' / 'x.omv'), {'a': [1]})
        with self.assertRaises(TypeError): write(self.path, [])
        with self.assertRaises(TypeError): write(self.path, {})
        with self.assertRaises(ValueError): write(self.path, {'a': [1], 'b': [1, 2]})
        with self.assertRaises(TypeError): write(self.path, {'a': 'text'})
        with self.assertRaises(TypeError): write(self.path, {'a': [1, 'x']})
        with self.assertRaises(TypeError): write(self.path, {'a': [True, 1]})
        with self.assertRaises(TypeError): write(self.path, {'a': [object()]})
        with self.assertRaises(ValueError): write(self.path, {'a': [math.inf]})
        with self.assertRaises(ValueError): write(self.path, {'a': ['x\x00y']})
        with self.assertRaises(ValueError): write(self.path, {'a': [1]}, {'b': {}})
        with self.assertRaises(ValueError): write(self.path, {'a': [1]}, {'a': {'color': 'red'}})
        with self.assertRaises(ValueError): write(self.path, {'a': [1]}, {'a': {'measureType': 'Other'}})
        with self.assertRaises(ValueError): write(self.path, {'a': [1.5]}, {'a': {'dataType': 'Integer'}})
        with self.assertRaises(ValueError): write(self.path, {'a': [1.5]}, {'a': {'measureType': 'Nominal'}})
        with self.assertRaises(ValueError): write(self.path, {'a': [1]}, {'a': {'levels': ['x']}})
        with self.assertRaises(ValueError): write(self.path, {'a': ['x', 'y']}, {'a': {'levels': ['x']}})
        with self.assertRaises(ValueError): write(self.path, {'a': ['x']}, {'a': {'levels': [(1, 'x')]}})
        with self.assertRaises(ValueError): write(self.path, {'a': [5]}, {'a': {'measureType': 'Nominal', 'levels': [(1, 'x')]}})
        with self.assertRaises(ValueError): write(self.path, {'a': [1]}, {'a': {'columnType': 'Unknown'}})
        with self.assertRaises(ValueError): write(self.path, {'a': ['x']}, weights='a')
        with self.assertRaises(ValueError): write(self.path, {'a': [2 ** 40]}, {'a': {'dataType': 'Integer'}})
        with self.assertRaises(TypeError): write(self.path, {'a': [1]}, {'a': {'description': 5}})
        with self.assertRaises(TypeError): write(self.path, {'a': [1]}, {'a': {'missingValues': [5]}})
        self.assertFalse(Path(self.path).exists())

    def test_large_integers_become_decimal_and_ids_from_integers(self):
        write(self.path, {'big': [2 ** 40, 1], 'code': [10, 20]}, {'code': {'measureType': 'ID'}})
        result = read(self.path)
        kinds = {c['name']: (c['dataType'], c['measureType']) for c in result['columns']}
        self.assertEqual(kinds['big'], ('Decimal', 'Continuous'))
        self.assertEqual(result['data']['big'], [float(2 ** 40), 1.0])
        self.assertEqual(kinds['code'], ('Text', 'ID'))
        self.assertEqual(result['data']['code'], ['10', '20'])

    def test_snapshot_of_derived_columns(self):
        for role in ('Computed', 'Recoded', 'Output', 'Filter'):
            with self.subTest(role=role):
                path = Path(self.directory.name) / (role + '.omv')
                spec = {'columnType': role, 'formula': 'missing_input + 1',
                        'transform': 42, 'parentId': 9, 'outputAnalysisId': 7}
                write(path, {'x': [1, 2]}, {'x': spec})
                result = read(path)
                self.assertEqual(result['data']['x'], [1, 2])
                field = result['columns'][0]
                self.assertEqual((field['columnType'], field['formula'], field['transform'], field['parentId']),
                                 ('Data', '', 0, 0))
                with zipfile.ZipFile(path) as archive:
                    self.assertEqual(json.loads(archive.read('metadata.json'))['dataSet']['transforms'], [])
                    self.assertFalse(any(n.endswith('/analysis') for n in archive.namelist()))

    def test_numeric_id_types_are_preserved(self):
        for kind, values in [('Integer', [1, None, 3]), ('Decimal', [1.5, None, 3.25])]:
            with self.subTest(kind=kind):
                path = Path(self.directory.name) / (kind + '.omv')
                write(path, {'id': values}, {'id': {'dataType': kind, 'measureType': 'ID'}})
                result = read(path)
                self.assertEqual(result['columns'][0]['dataType'], kind)
                self.assertEqual(result['columns'][0]['measureType'], 'ID')
                self.assertEqual(result['data']['id'], values)

    def test_nan_boolean_and_integer_precision(self):
        write(self.path, {'flag': [True, math.nan, False]})
        self.assertEqual(read(self.path, labels=False)['data']['flag'], [1, None, 0])
        for spec in (None, {'x': {'dataType': 'Decimal'}}):
            with self.assertRaises(ValueError):
                write(Path(self.directory.name) / 'large.omv', {'x': [2**53 + 1]}, spec)

    def test_boolean_arguments_and_archive_limit(self):
        for flag in ('False', 1, None):
            with self.assertRaises(TypeError): write(self.path, {'x': [1]}, overwrite=flag)
        write(self.path, {'x': [1]})
        with self.assertRaises(TypeError): read(self.path, labels='False')
        with self.assertRaises(ValueError): read(self.path, max_bytes=10)
        self.assertEqual(read(self.path, max_bytes=1024**2)['data'], {'x': [1]})

    def test_no_overwrite_race(self):
        original_commit = ns['os'].rename if ns['os'].name == 'nt' else ns['os'].link
        def race(source, target):
            Path(target).write_bytes(b'another process')
            return original_commit(source, target)
        method = 'rename' if ns['os'].name == 'nt' else 'link'
        with patch.object(ns['os'], method, side_effect=race):
            with self.assertRaises(FileExistsError): write(self.path, {'x': [1]})
        self.assertEqual(Path(self.path).read_bytes(), b'another process')
        self.assertEqual(len(list(Path(self.directory.name).iterdir())), 1)

    def test_read_errors(self):
        not_zip = Path(self.directory.name) / 'bad.omv'
        not_zip.write_bytes(b'not a zip')
        with self.assertRaises(ValueError): read(str(not_zip))
        with self.assertRaises(FileNotFoundError): read(str(Path(self.directory.name) / 'missing.omv'))
        fields = [field('a', 1, 'Integer', 'Continuous')]
        jamovi_style_archive(self.path, fields, [[1, 2]], manifest='jamovi-Archive-Version: 13.0\n')
        with self.assertRaisesRegex(ValueError, 'newer version'): read(self.path)
        jamovi_style_archive(self.path, fields, [[1, 2]], manifest='Manifest-Version: 1.0\n')
        with self.assertRaisesRegex(ValueError, 'manifest is corrupt'): read(self.path)
        jamovi_style_archive(self.path, fields, [[1, 2]], row_count=5)
        with self.assertRaisesRegex(ValueError, 'shorter'): read(self.path)
        with zipfile.ZipFile(self.path, 'w') as archive:
            archive.writestr('meta', 'jamovi-Archive-Version: 11.0\n')
        with self.assertRaisesRegex(ValueError, 'metadata.json'): read(self.path)
        with zipfile.ZipFile(self.path, 'w') as archive:
            archive.writestr('meta', 'jamovi-Archive-Version: 11.0\n')
            archive.writestr('metadata.json', '{not json')
        with self.assertRaisesRegex(ValueError, 'not valid JSON'): read(self.path)
        with zipfile.ZipFile(self.path, 'w') as archive:
            archive.writestr('META-INF/MANIFEST.MF', 'jamovi-Archive-Version: 5.0\r\n')
            archive.writestr('metadata.json', json.dumps({'dataSet': {'rowCount': 1, 'fields': [
                {'name': 'a', 'id': 1, 'dataType': 'Integer', 'measureType': 'Continuous'}]}}))
            archive.writestr('data.bin', struct.pack('<i', 7))
        self.assertEqual(read(self.path)['data'], {'a': [7]})
        self.assertEqual(read(self.path)['archive_version'], (5, 0))


if __name__ == '__main__':
    unittest.main()
