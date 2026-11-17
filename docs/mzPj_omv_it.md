# File OMV: lettura e scrittura del dataset

Funzioni della candidata successiva a Pj 1.5.0: **non presenti nei pacchetti
1.5.0 pubblicati**. Sono disponibili automaticamente in Pj, Pjp e nel servizio
Python per altri moduli, senza caricare un file Service. Usano solo la libreria
standard, con entrambi gli interpreti e senza rete.
[Guida inglese di riferimento](mzPj_omv.md).

## Lettura

```python
documento = mzpjReadOmv(path='source.omv', labels=True, max_bytes=256 * 1024**2)
```

- `path`: stringa o `pathlib.Path` accessibile al Python scelto. La funzione non apre dialoghi; il pulsante Read carica direttamente `dataext`, senza chiamate nello script.
- `labels=True`: restituisce le etichette delle categorie; `False`: i codici interi memorizzati.
- `max_bytes`: limite positivo in byte per le voci decompresse del dataset, 256 MiB per default. Si può aumentare esplicitamente per un dataset grande e affidabile. Non vengono caricate le risorse delle analisi.

Il risultato è un dizionario con `data` (nome colonna → lista di valori),
`columns` (metadati delle colonne), `row_count`, `weights`, `results_language`,
`archive_version` ed `entries` (nomi delle voci ZIP).

I mancanti di sistema diventano `None`. Le regole personalizzate per i mancanti
restano nei metadati: i valori cui si applicano non vengono eliminati né sostituiti.
Si leggono tutte le righe, anche quelle escluse da filtri attivi. Le colonne filtro
restituiscono booleani. La lettura non carica il documento nell'interfaccia jamovi,
non esegue script e non ripristina le analisi. Versioni future non supportate,
dati troncati o voci ZIP duplicate producono un errore.

## Scrittura

```python
esito = mzpjWriteOmv(percorso, data, meta=None, weights=None,
                    results_language=None, overwrite=False, html=None)
```

| Argomento | Significato |
| --- | --- |
| `percorso` | Destinazione con estensione `.omv`; la cartella deve già esistere. |
| `data` | Dizionario non vuoto di colonne con uguale numero di righe, oppure documento completo restituito da `mzpjReadOmv`; l'ordine è quello del dizionario. |
| `meta` | Dizionario `{nome: specifica}` oppure lista `columns` restituita dalla lettura. Non deve descrivere colonne assenti da `data`. |
| `weights` | Nome di una colonna numerica da impostare come peso; non esegue calcoli pesati. |
| `results_language` | Lingua del nuovo documento; `None` eredita la lingua del documento letto o usa `'en'` per un dizionario ordinario. |
| `overwrite` | Booleano, default `False`: protegge i file esistenti, anche se creati da un altro processo durante la scrittura. |
| `html` | Testo facoltativo per `index.html`; non crea analisi o Results nativi. Normalmente lasciare `None`. |

L'esito contiene `path`, `row_count`, `column_count`. Si scrive prima un archivio
temporaneo completo nella cartella di destinazione. Un errore di validazione non
sostituisce un file esistente; errori di permessi, disco o filesystem vengono riportati.

Senza metadati: numeri interi → Integer/Continuous; frazionari → Decimal/Continuous;
testi → Text/Nominal con livelli ordinati; booleani → Integer/Nominal con etichette
TRUE/FALSE. `None`, NaN numerici e testo vuoto rappresentano mancanti. Infiniti,
tipi incompatibili mescolati e interi non rappresentabili senza perdita di precisione
sono rifiutati. Per identificativi numerici troppo grandi usare testi.

Nei metadati si impostano `dataType` (`Integer`, `Decimal`, `Text`), `measureType`
(`Continuous`, `Nominal`, `Ordinal`, `ID`), `description`, `missingValues`
(es. `['== 99']`), `width`, `importName`, `trimLevels`, `id` e `levels`.
I livelli accettano liste di etichette, tuple `(codice, etichetta)` con eventuale
testo di importazione e flag pinned, oppure dizionari `{codice: etichetta}`.
Le categorie Text richiedono codici consecutivi da zero. I tipi ID numerici
espliciti vengono mantenuti; negli altri casi gli ID sono testuali. ID delle
colonne positivi e univoci vengono mantenuti; se incompleti o duplicati sono rigenerati.

**Si crea una copia dei dati, non un Save/Save As del documento.** Le colonne
Computed, Recoded, Filter e Output diventano normali colonne Data con i valori
correnti. Non si ricreano formule, trasformazioni, filtri attivi, appartenenza
alle analisi, script o Results. Tutte le righe sono incluse. I metadati originali
di ruolo e formula sono accettati ma rimossi nella copia, evitando dipendenze
inesistenti. Si conservano etichette, descrizioni e regole dei mancanti.
Questo comportamento è distinto dal problema del salvataggio dei Results Svg.

## Esempio con metadati originali

Read e Save nelle impostazioni lavorano sul `dataext` separato, senza chiamate
Python obbligatorie. La preview facoltativa mostra la stessa copia salvata.
Vedere la [guida dataext](mzPj_dataext_it.md). Gli esempi seguenti usano invece
percorsi espliciti Python, senza aprire dialoghi.

```python
from pathlib import Path

documento = mzpjReadOmv(Path.home() / 'originale.omv')
nomi = ['score', 'group']
dati = {nome: documento['data'][nome] for nome in nomi}
metadati = [col for col in documento['columns'] if col['name'] in nomi]
mzpjWriteOmv(Path.home() / 'copia.omv', dati, meta=metadati)
```

Nell'editor `data` contiene valori, non tutti i metadati originali: occorre
fornirli con `meta`, oppure ricavarli leggendo l'OMV. In Pj sono disponibili tutte
le colonne ricevute; in Pjp solo quelle selezionate. Il file creato contiene solo
quelle passate alla funzione. La scrittura non aggiunge colonne al dataset aperto:
per quello utilizzare Output. Esempio completo: `68_omv_dataset_snapshot.py`.

Gli stessi helper sono disponibili nel ponte `mzPjRunPython()` senza modificare
API1 o il contratto dei risultati. Il modulo chiamante sceglie i percorsi e gestisce
gli errori. I percorsi vengono risolti dall'interprete selezionato: nel Flatpak
Linux il Python embedded vede la sandbox, System Python l'host. Non si attiva il
selettore file di jamovi e non si concedono nuovi permessi. Preferire percorsi
assoluti e non sostituire con questi helper il documento OMV attualmente aperto.
