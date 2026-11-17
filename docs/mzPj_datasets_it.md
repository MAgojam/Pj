# Funzioni di trasformazione dei dataset

Per Read, Save, dataext, metadati e preview facoltativa vedere la [guida ai dataset esterni](mzPj_dataext_it.md).

## Funzioni

| Funzione | Argomenti e comportamento |
| --- | --- |
| `mzpjSortRows(dataset, by, descending=False, missing='last')` | `by`: un nome o lista di nomi. `descending`: booleano unico o uno per chiave. Ordinamento stabile; i pari mantengono l'ordine iniziale. `missing='first'`/`'last'` è indipendente dalla direzione. Le etichette si ordinano come testi, non secondo i livelli ordinali. |
| `mzpjOrderColumns(dataset, columns, keep_others=True)` | Porta in testa le colonne richieste, nell'ordine indicato. Con `False` conserva solo quelle. |
| `mzpjCombineColumns(dataset, columns, name, sep=' ', drop=False, missing='skip')` | Unisce i valori in una nuova colonna testuale. `name` non deve esistere. `drop=True` elimina dalla copia le colonne usate. `'skip'` omette le componenti mancanti; tutte mancanti danno `None`. `'propagate'` dà `None` se ne manca anche una. |
| `mzpjWideToLong(dataset, columns, id_columns=None, names_to='variable', values_to='value')` | Impila le colonne scelte. Per default le altre sono identificativi; una lista esplicita conserva solo quegli identificativi. Ordine: riga originaria, poi colonna. Non aggrega o converte i valori. |
| `mzpjLongToWide(dataset, id_columns, names_from='variable', values_from='value', fill=None)` | Pivot di una colonna di valori; mantiene solo identificativi e valori pivotati. I nomi devono essere testi non vuoti. Coppie identificativo/nome duplicate generano errore: aggregare prima in modo esplicito. Le combinazioni assenti usano `fill`. Ordine di prima comparsa. |
| `mzpjMerge(dataset, other, on, how='left', suffixes=('_left', '_right'), validate='one_to_one', max_rows=1000000)` | Join con una o più chiavi comuni. `how`: `'left'`, `'right'`, `'inner'`, `'outer'`. Le colonne non chiave omonime ricevono i suffissi. `validate`: `'one_to_one'`, `'one_to_many'`, `'many_to_one'`, `'many_to_many'`. Chiavi mancanti e nomi finali duplicati sono rifiutati. Il limite di righe evita espansioni involontarie ed è aumentabile esplicitamente. |

Le chiavi devono essere scalari. Tipi non confrontabili nell'ordinamento generano
errore. Per mancanti si intendono `None` e NaN numerici: le regole personalizzate
memorizzate nei metadati non vengono valutate dalle trasformazioni.
Un'impilatura con tipi incompatibili non viene convertita silenziosamente:
la scrittura OMV la rifiuta. Le chiavi categoriali dei due dataset devono usare
codifiche/etichette compatibili. Sono preparazioni dati, non stime statistiche.

