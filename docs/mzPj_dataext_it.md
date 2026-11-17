# File OMV esterni: data e dataext

Disponibile nella **candidata Pj 1.6.0**, con entrambi i Python, in Pj e Pjp.
Non richiede pandas o un file Service. [Guida inglese](mzPj_dataext.md).

## I due dataset

`data` viene fornito da jamovi: le colonne del dataset corrente in Pj, le sole
variabili selezionate in Pjp. Può provenire da OMV, CSV, SAV o Data Library.
Analisi, tabelle e grafici vanno nei Results. Il normale Save/Save As di jamovi
conserva quel documento con script, analisi e Results.

`dataext` è un **dizionario di colonne separato**, già disponibile e inizialmente
vuoto. Non sostituisce `data`. Ogni analisi ha il proprio dataset esterno.

## Read, Run, preview e Save

Nel riquadro **External OMV files** delle impostazioni:

- **Read…** sceglie un OMV e ne carica dati e metadati supportati in `dataext`,
  senza eseguire lo script dell'editor o il Service. Il dataset aperto in jamovi
  rimane invariato. Successivamente Run esegue lo script per elaborarlo.
- **Save…** sceglie la destinazione e salva l'ultimo `dataext` prodotto con
  successo. Non richiede Prepare o Save nello script, non riesegue Python e
  non include le analisi o i Results del documento.
- **Show preview in Results** mostra o rimuove una tabella HTML compatta: prime
  **10 righe**, **tutte le colonne**, dimensioni totali e scorrimento quando
  serve. Non riesegue Python. Usa esattamente la stessa copia di Save. Il testo
  lungo viene abbreviato nella sola preview; il file mantiene i valori completi.
  Dataset estremamente larghi possono superare il limite di visualizzazione,
  senza impedire il salvataggio completo.

La riga `dataext:` mostra **Empty**, il nome del file letto o **Created in Python**.
Il selettore nativo fornisce una copia di sessione: il percorso originale non
viene promesso o sostituito con quello temporaneo nell'etichetta. Il nome
sorgente non conferma la destinazione scelta con Save. Un dizionario vuoto
disabilita Save; un dataset con colonne ma zero righe può essere salvato.

## Creare dataext dal dataset corrente

Caricare Anderson's Iris Data. In Pjp selezionare le quattro misure e Species.

```python
dataext = mzpjSortRows(data, ['Species', 'Petal.Length'],
                       descending=[False, True])
dataext = mzpjOrderColumns(dataext, ['Species', 'Petal.Length', 'Petal.Width'])
```

Run, eventuale preview, poi Save. Non serve Read. Per una copia Python ordinaria
copiare anche le liste delle colonne:

```python
dataext = {name: list(values) for name, values in data.items()}
```

## Trasformare o combinare dati esterni

Usare prima Read. Con colonne illustrative participant_id, before e after:

```python
dataext = mzpjSortRows(dataext, 'participant_id')
dataext = mzpjWideToLong(dataext, ['before', 'after'],
                        id_columns=['participant_id'],
                        names_to='occasion', values_to='score')
```

Run una volta, controllo e Save. Un altro Run agisce su `dataext` già trasformato:
rileggere l'originale prima di ripetere una trasformazione che richiede le
colonne wide originali. Per combinare i due dataset, con identificativi comuni:

```python
dataext = mzpjMerge(dataext, data, on='participant_id',
                     how='left', validate='many_to_one')
```

La [guida delle trasformazioni](mzPj_datasets_it.md) spiega gli argomenti delle
funzioni. Per aggiungere colonne al dataset **corrente** rimane il meccanismo
Output, assegnandole a `data`. Il salvataggio esterno non usa Output.

## Metadati, errori e durata

Read recupera tipi, etichette, descrizioni, regole dei mancanti e pesi supportati.
L'oggetto esterno funziona come un dizionario e ha anche la proprietà `metadata`,
che contiene i metadati OMV, comprese le specifiche `columns`. Le funzioni
trasportano quelli applicabili. Una nuova mappa ordinaria usa tipi inferiti.
Colonne calcolate, trasformate e Output diventano valori ordinari: non si
ricreano formule, filtri attivi, proprietà delle analisi o Results. Tutte le
righe sono incluse.

Run riusciti mantengono `dataext` nella stessa analisi/sessione. Un errore non
conferma modifiche parziali: preview e Save rimangono sull'ultimo successo.
Una bozza non eseguita non li cambia. Clear cancella editor e Results,
conservando una copia esterna ancora disponibile.

**Salvare i dati esterni prima di chiudere jamovi.** La copia di lavoro è una
cache della sessione, non un dataset allegato al documento dell'analisi. Alla
riapertura rileggere l'OMV esterno o ricreare `dataext` da `data`. Una preview
rimasta nei Results salvati è una visualizzazione storica, non il ripristino
del dataset di lavoro. La UI verifica la disponibilità e non sostituisce
silenziosamente i dati mancanti con `data`.

Il trasferimento tramite dialoghi ha limite **32 MiB compresso**; la lettura
controlla separatamente le voci del dataset decompresse, **256 MiB** di default.
Per percorsi gestiti nello script usare `mzpjReadOmv(path)` e
`mzpjWriteOmv(path, dataset, ...)`, che non aprono dialoghi. La
[guida OMV](mzPj_omv_it.md) descrive metadati e protezione dalla sovrascrittura.

Gli esempi **69** e **70** coprono i due percorsi. Anche gli script API1 ricevono
`dataext` vuoto; popolandolo, la risposta opzionale `omv_export` contiene archivio,
dimensioni e preview ridotta. Il modulo chiamante gestisce salvataggio e stato
fra chiamate. Vedere la [guida API](mzPj_service_api.md).

## Interprete Python

Selezionare **Embedded** o **System** con i radio button **Python interpreter**. Embedded è il Python incluso in jamovi; System è quello installato sul computer. Entrambi supportano questo flusso. La scelta dell’interprete nelle analisi già salvate viene mantenuta. La preview usa un comando esplicito di visualizzazione: non esegue l’editor, anche dopo Save o con una bozza modificata.
