# Dataset esterno: dizionario di colonne con metadati separati dalle chiavi utente.
import copy


class _PjExternalData(dict):
    def __init__(self, data=None, metadata=None):
        super().__init__({name: list(values) for name, values in (data or {}).items()})
        self._pj_metadata = copy.deepcopy(metadata or {})

    def copy(self):
        return _PjExternalData(self, self._pj_metadata)

    @property
    def metadata(self):
        """OMV column specifications, weights and language for this external dataset."""
        return self._pj_metadata

    def clear(self):
        super().clear()
        self._pj_metadata.clear()


def _pj_external_data(value):
    if isinstance(value, _PjExternalData):
        return value
    if isinstance(value, Mapping) and isinstance(value.get('data'), Mapping):
        return _PjExternalData(value['data'], {k: v for k, v in value.items() if k != 'data'})
    if not isinstance(value, Mapping):
        raise TypeError('dataext must be a dictionary of columns or a document returned by mzpjReadOmv().')
    return _PjExternalData(value)


def _pj_capture_dataext(value):
    value = _pj_external_data(value)
    if not value:
        results.pop('omv_export', None)
        results['dataext_empty'] = True
        return
    # Il writer valida prima tutto il dataset; la preview viene riletta dal file
    # prodotto, cosi' descrive i valori e l'ordine effettivamente salvati.
    metadata = value._pj_metadata
    columns = [c for c in metadata.get('columns', []) if c['name'] in value]
    weights = metadata.get('weights')
    if weights not in value:
        weights = None
    with tempfile.TemporaryDirectory(prefix='mzpj-dataext-') as directory:
        path = os.path.join(directory, 'dataext.omv')
        mzpjWriteOmv(path, value, meta=columns or None, weights=weights,
                     results_language=metadata.get('results_language'))
        if os.path.getsize(path) > 32 * 1024**2:
            raise ValueError('dataext exceeds the 32 MiB dialog transfer limit. Save to an explicit Python path instead.')
        document = mzpjReadOmv(path)
        names = list(document['data'])
        rows = []
        shortened = False
        too_wide = len(names) > 2000
        if not too_wide:
            for i in range(min(10, document['row_count'])):
                row = []
                for name in names:
                    cell = document['data'][name][i]
                    if isinstance(cell, str) and len(cell) > 160:
                        cell = cell[:157] + '...'
                        shortened = True
                    row.append(cell)
                rows.append(row)
        with open(path, 'rb') as stream:
            content = base64.b64encode(stream.read()).decode('ascii')
    results['omv_export'] = {'filename': 'dataext.omv', 'content': content,
                            'row_count': document['row_count'], 'column_count': len(names),
                            'source_name': metadata.get('source_name', ''),
                            'preview': {'columns': [] if too_wide else names, 'rows': rows,
                                        'shortened': shortened, 'too_wide': too_wide}}
    results['dataext_empty'] = False
