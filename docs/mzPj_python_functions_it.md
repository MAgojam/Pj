# Manuale delle funzioni Python di Pj

[Versione inglese di riferimento](mzPj_python_functions.md). Aggiornato il 28 ottobre 2026.

Questo manuale spiega le funzioni aggiunte da Pj, distinte dal linguaggio Python.
Firme e default sono estratti dal sorgente corrente. **Chart.js, Plotly, Svg
nativo D3, helper dati/metanalisi e Output da Pj richiedono Pj 1.4.0 o successivo;
non sono presenti nei precedenti pacchetti 1.3.x.**
Le funzioni mzpj non richiedono import nell’editor Pj/Pjp. Rispettare maiuscole e
minuscole. Dopo `*` gli argomenti vanno passati per nome. None indica default
documentato oppure assenza di un valore opzionale, non zero. I dieci helper D3
generali non richiedono librerie scientifiche Python opzionali; quelli numerici
per dati/metanalisi richiedono NumPy/SciPy nell’interprete selezionato. Pj include
alcune librerie pure Python, non pandas o matplotlib. Controllare Settings →
Show Python info per l’interprete effettivo. Su macOS Pj individua la cartella
Resources/lib/pythonX.Y dell’app embedded per importare le librerie già incluse.
Il Python System mantiene le proprie librerie e percorsi.

## Dati, file e colonne prodotte

`data` è un dizionario di liste-colonna, non un DataFrame automatico. Pjp riceve
soltanto le variabili selezionate nella sua UI; Pj normalmente riceve le colonne
di input del dataset. I propri Output sono esclusi dagli input automatici di
Pj. I mancanti del dataset diventano None; le categorie diventano etichette
visualizzate. Usare i nomi esatti. Gli helper restituiscono valori senza
modificare gli input. L’assegnazione a `data['nuovo_nome']` richiede una colonna
Output nativa nei due editor. Non è una modalità per sovrascrivere gli input.
Restituire gli stessi nuovi nomi aggiorna le colonne; ometterli in un’esecuzione
riuscita rimuove gli Output di quell’analisi. Non sono formule persistenti di
Compute/Transform.

**Service…** carica un file eseguito prima del codice dell’editor, nello stesso
ambiente di esecuzione. Non è mostrato nell’editor. **Scripts → Load** sostituisce
il testo dell’editor; **Save** lo salva; **Run** esegue. Load da solo non esegue.
Conservare sul proprio computer il file di servizio per modificarlo/riselezionarlo.
Ogni Run avvia un nuovo processo Python: le variabili non persistono tra Run.
Gli script hanno i permessi del processo selezionato; non sono espressioni
statistiche eseguite in un ambiente ristretto.

## Scegliere risultati ed esportazione

ShowTable produce tabelle native, ShowText testo Markdown, ShowImage immagini PNG.
Usare `render='html'` quando servono colori, scorrimento o accordion nelle tabelle.
Con D3, `result_type='svg'` fornisce l’esportazione nativa della figura mantenendo
le interazioni supportate in Results. Con Chart/Plotly, `static=True` produce
invece una sola fotografia statica per PDF/DOCX/ODT; False mantiene HTML
interattivo senza catture. Le dimensioni del popup sono default; quelle esplicite
degli helper prevalgono. I controlli interattivi non rieseguono Python e non
aggiornano automaticamente altre tabelle native.
L’esportazione LaTeX degli Svg client ha un limite jamovi documentato: il successo
in Word/PDF non certifica LaTeX. Un risultato eccessivo genera un errore informativo
di dimensione: ridurre punti/righe o separare i risultati, non la precisione dei calcoli.

## Guide dettagliate di riferimento

- [Tabelle native/HTML, colori, annotazioni ed esempi](PYTHON_RESULTS_GUIDE.md)
- [Parametri e convenzioni D3](mzPj_d3_plots.md), [esploratori collegati](mzPj_linked_d3.md), [Svg/esportazione](mzPj_d3_export.md)
- [Chart.js, legenda e modalità statica](mzPj_chartjs.md), [Plotly](mzPj_plotly.md)
- [Preparazione dati: mancanti, gruppi, MAD e Output](mzPj_data_preparation.md)
- [Misure metanalitiche e limiti](mzPj_meta_analysis.md)
- [Librerie incluse e import](mzPj_bundled_libraries.md), [limiti dimensionali](mzPj_output_size.md)

## Riferimento delle funzioni

Le funzioni Show aggiungono risultati; non restituiscono modelli stimati. Usare
nomi `name` stabili e distinti per più risultati. Le firme mostrano i default
effettivi e le tabelle spiegano ogni argomento. I dizionari complessi di stile e
configurazione seguono gli schemi delle guide collegate, non codice arbitrario.


### mzpjShowImage


Aggiunge un risultato Image PNG nativo.


```python
mzpjShowImage(png_data, name=None, title=None)
```


| Argomento | Significato |
|---|---|

| `png_data` | Byte PNG, stream binario aperto o rappresentazione PNG supportata. Per un file usare with open(path, "rb"); non accetta qualunque formato immagine. |

| `name` | Chiave univoca del risultato per questa esecuzione; None la genera. Per mzpjUseLibrary indica il nome della libreria nel catalogo. |

| `title` | Titolo visibile; None usa quello predefinito della funzione. |



### mzpjShowHtml


Aggiunge un risultato HTML. Grafici JS arbitrari non acquisiscono automaticamente l’esportazione nativa Office.


```python
mzpjShowHtml(content, name=None, title=None)
```


| Argomento | Significato |
|---|---|

| `content` | Testo da presentare: Markdown per ShowText, HTML per ShowHtml. Eseguire l’escape dei dati prima di inserirli in HTML. |

| `name` | Chiave univoca del risultato per questa esecuzione; None la genera. Per mzpjUseLibrary indica il nome della libreria nel catalogo. |

| `title` | Titolo visibile; None usa quello predefinito della funzione. |



### mzpjShowText


Aggiunge testo Markdown tramite Text jamovi.


```python
mzpjShowText(content, name=None)
```


| Argomento | Significato |
|---|---|

| `content` | Testo da presentare: Markdown per ShowText, HTML per ShowHtml. Eseguire l’escape dei dati prima di inserirli in HTML. |

| `name` | Chiave univoca del risultato per questa esecuzione; None la genera. Per mzpjUseLibrary indica il nome della libreria nel catalogo. |



### mzpjShowTable


Aggiunge una Table nativa oppure una tabella HTML con stili. Le opzioni grafiche non modificano i dati.


```python
mzpjShowTable(data, name=None, title=None, columns=None, formats=None, notes=None, include_index=True, column_groups=None, combine_below=None, footnotes=None, symbols=None, render='native', zebra=False, column_styles=None, row_styles=None, cell_styles=None, digits=3, transpose=False, accordion=False, expanded=True, max_height=None, sticky_header=False, max_width=None, scroll='auto')
```


| Argomento | Significato |
|---|---|

| `data` | Dati della tabella: lista di dizionari-riga, dizionario di liste-colonna, matrice oppure DataFrame pandas supportato. |

| `name` | Chiave univoca del risultato per questa esecuzione; None la genera. Per mzpjUseLibrary indica il nome della libreria nel catalogo. |

| `title` | Titolo visibile; None usa quello predefinito della funzione. |

| `columns` | Nomi delle colonne nell’ordine desiderato. RowStatistic: colonne numeriche da combinare; Correlation: colonne della matrice; Table: colonne da presentare. |

| `formats` | Mappa formati delle colonne native, es. {"p":"pvalue", "Mean":"zto"}; vedere i formati jamovi supportati nella guida tabelle. |

| `notes` | Una stringa o lista di stringhe per le note sotto la tabella. |

| `include_index` | Include l’indice di un DataFrame pandas come colonna aggiuntiva. |

| `column_groups` | Mappa dal nome della colonna al titolo di gruppo per intestazioni raggruppate. |

| `combine_below` | Nomi delle colonne con etichette consecutive ripetute da combinare nella presentazione. |

| `footnotes` | Mappa con chiave (indice riga dati da zero, nome colonna): testo della nota oppure simbolo esplicito. |

| `symbols` | Mappa con chiave (indice riga dati da zero, nome colonna): testo della nota oppure simbolo esplicito. |

| `render` | native (default) crea una Table jamovi; html abilita colori, zebratura, scorrimento e accordion. |

| `zebra` | HTML: False, True per la zebratura predefinita, un colore CSS oppure due colori alternati. La riga zero è la prima riga dati. |

| `column_styles` | Mappa stili HTML per nome colonna, indice riga da zero oppure (riga, colonna). Proprietà: color, background, bold. Cella prevale su riga, riga su colonna, colonna su zebra. |

| `row_styles` | Mappa stili HTML per nome colonna, indice riga da zero oppure (riga, colonna). Proprietà: color, background, bold. Cella prevale su riga, riga su colonna, colonna su zebra. |

| `cell_styles` | Mappa stili HTML per nome colonna, indice riga da zero oppure (riga, colonna). Proprietà: color, background, bold. Cella prevale su riga, riga su colonna, colonna su zebra. |

| `digits` | Numero di decimali nella visualizzazione HTML; non arrotonda i valori numerici del dataset. |

| `transpose` | Scambia righe e colonne nella presentazione. Coordinate di stili e annotazioni seguono le regole della guida dettagliata. |

| `accordion` | True racchiude grafico interattivo/tabella HTML in una sezione collassabile. Non è un’opzione delle tabelle native. |

| `expanded` | Stato iniziale dell’accordion: True aperto, False collassato. |

| `max_height` | Limiti del contenitore HTML in pixel CSS, non limiti del dataset. Usare con scroll e la guida dettagliata delle tabelle. |

| `sticky_header` | Mantiene visibili le intestazioni HTML durante lo scorrimento verticale. |

| `max_width` | Limiti del contenitore HTML in pixel CSS, non limiti del dataset. Usare con scroll e la guida dettagliata delle tabelle. |

| `scroll` | Scorrimento HTML: auto, vertical, horizontal, both oppure none. Le dimensioni esplicite definiscono l’area disponibile. |



### mzpjShowScatter


Dispersione D3 delle coppie numeriche complete.


```python
mzpjShowScatter(dataset, x, y, group=None, labels=None, name=None, title=None, x_label=None, y_label=None, color='#3e6da9', width=None, height=None, accordion=True, expanded=True, result_type='html')
```


| Argomento | Significato |
|---|---|

| `dataset` | Dizionario di colonne con liste di uguale lunghezza, normalmente data. Nessuna conversione automatica in DataFrame pandas. |

| `x` | Nome della colonna numerica per questo asse. |

| `y` | Nome della colonna numerica per questo asse. |

| `group` | Nome opzionale della colonna di raggruppamento; non diventa automaticamente un predittore statistico. |

| `labels` | D3: nome opzionale della colonna con etichette delle osservazioni. Chart.js: lista di etichette delle categorie. |

| `name` | Chiave univoca del risultato per questa esecuzione; None la genera. Per mzpjUseLibrary indica il nome della libreria nel catalogo. |

| `title` | Titolo visibile; None usa quello predefinito della funzione. |

| `x_label` | Etichetta visibile dell’asse; None usa quella predefinita. |

| `y_label` | Etichetta visibile dell’asse; None usa quella predefinita. |

| `color` | Colore del grafico; usare un colore CSS come #3e6da9. |

| `width` | Dimensioni richieste della figura/contenitore in pixel CSS; None usa il default. Plotly ha altezza predefinita 800. Non indica la dimensione del font. |

| `height` | Dimensioni richieste della figura/contenitore in pixel CSS; None usa il default. Plotly ha altezza predefinita 800. Non indica la dimensione del font. |

| `accordion` | True racchiude grafico interattivo/tabella HTML in una sezione collassabile. Non è un’opzione delle tabelle native. |

| `expanded` | Stato iniziale dell’accordion: True aperto, False collassato. |

| `result_type` | D3: html (default) oppure svg (Svg nativo jamovi). Svg conserva le interazioni supportate in Results e fornisce una figura statica per i documenti. |



### mzpjShowHistogram


Istogramma D3 con frequenze o densità esplicite.


```python
mzpjShowHistogram(dataset, variable, bins=10, density=False, name=None, title=None, x_label=None, y_label=None, color='#3e6da9', width=None, height=None, accordion=True, expanded=True, result_type='html')
```


| Argomento | Significato |
|---|---|

| `dataset` | Dizionario di colonne con liste di uguale lunghezza, normalmente data. Nessuna conversione automatica in DataFrame pandas. |

| `variable` | Nome della colonna numerica da riassumere o rappresentare. |

| `bins` | Numero intero positivo di classi di uguale ampiezza dell’istogramma. |

| `density` | False mostra le frequenze; True normalizza a uno l’area dell’istogramma. |

| `name` | Chiave univoca del risultato per questa esecuzione; None la genera. Per mzpjUseLibrary indica il nome della libreria nel catalogo. |

| `title` | Titolo visibile; None usa quello predefinito della funzione. |

| `x_label` | Etichetta visibile dell’asse; None usa quella predefinita. |

| `y_label` | Etichetta visibile dell’asse; None usa quella predefinita. |

| `color` | Colore del grafico; usare un colore CSS come #3e6da9. |

| `width` | Dimensioni richieste della figura/contenitore in pixel CSS; None usa il default. Plotly ha altezza predefinita 800. Non indica la dimensione del font. |

| `height` | Dimensioni richieste della figura/contenitore in pixel CSS; None usa il default. Plotly ha altezza predefinita 800. Non indica la dimensione del font. |

| `accordion` | True racchiude grafico interattivo/tabella HTML in una sezione collassabile. Non è un’opzione delle tabelle native. |

| `expanded` | Stato iniziale dell’accordion: True aperto, False collassato. |

| `result_type` | D3: html (default) oppure svg (Svg nativo jamovi). Svg conserva le interazioni supportate in Results e fornisce una figura statica per i documenti. |



### mzpjShowBoxPlot


Box plot descrittivi D3, opzionalmente con osservazioni individuali.


```python
mzpjShowBoxPlot(dataset, variable, group=None, labels=None, show_points=False, name=None, title=None, x_label=None, y_label=None, color='#3e6da9', width=None, height=None, accordion=True, expanded=True, result_type='html')
```


| Argomento | Significato |
|---|---|

| `dataset` | Dizionario di colonne con liste di uguale lunghezza, normalmente data. Nessuna conversione automatica in DataFrame pandas. |

| `variable` | Nome della colonna numerica da riassumere o rappresentare. |

| `group` | Nome opzionale della colonna di raggruppamento; non diventa automaticamente un predittore statistico. |

| `labels` | D3: nome opzionale della colonna con etichette delle osservazioni. Chart.js: lista di etichette delle categorie. |

| `show_points` | Mostra anche le singole osservazioni/punti oltre al riepilogo o alla linea. |

| `name` | Chiave univoca del risultato per questa esecuzione; None la genera. Per mzpjUseLibrary indica il nome della libreria nel catalogo. |

| `title` | Titolo visibile; None usa quello predefinito della funzione. |

| `x_label` | Etichetta visibile dell’asse; None usa quella predefinita. |

| `y_label` | Etichetta visibile dell’asse; None usa quella predefinita. |

| `color` | Colore del grafico; usare un colore CSS come #3e6da9. |

| `width` | Dimensioni richieste della figura/contenitore in pixel CSS; None usa il default. Plotly ha altezza predefinita 800. Non indica la dimensione del font. |

| `height` | Dimensioni richieste della figura/contenitore in pixel CSS; None usa il default. Plotly ha altezza predefinita 800. Non indica la dimensione del font. |

| `accordion` | True racchiude grafico interattivo/tabella HTML in una sezione collassabile. Non è un’opzione delle tabelle native. |

| `expanded` | Stato iniziale dell’accordion: True aperto, False collassato. |

| `result_type` | D3: html (default) oppure svg (Svg nativo jamovi). Svg conserva le interazioni supportate in Results e fornisce una figura statica per i documenti. |



### mzpjShowBar


Barre D3 da categorie e statistica descrittiva richiesta.


```python
mzpjShowBar(dataset, category, value=None, stat='count', orientation='vertical', name=None, title=None, x_label=None, y_label=None, color='#3e6da9', width=None, height=None, accordion=True, expanded=True, result_type='html')
```


| Argomento | Significato |
|---|---|

| `dataset` | Dizionario di colonne con liste di uguale lunghezza, normalmente data. Nessuna conversione automatica in DataFrame pandas. |

| `category` | Nome della colonna categoriale per i gruppi delle barre. |

| `value` | Colonna numerica usata dalla statistica delle barre; non richiesta per count. |

| `stat` | Aggregazione delle barre: count, mean, sum oppure identity (valori già riassunti). |

| `orientation` | Orientamento delle barre: vertical oppure horizontal. |

| `name` | Chiave univoca del risultato per questa esecuzione; None la genera. Per mzpjUseLibrary indica il nome della libreria nel catalogo. |

| `title` | Titolo visibile; None usa quello predefinito della funzione. |

| `x_label` | Etichetta visibile dell’asse; None usa quella predefinita. |

| `y_label` | Etichetta visibile dell’asse; None usa quella predefinita. |

| `color` | Colore del grafico; usare un colore CSS come #3e6da9. |

| `width` | Dimensioni richieste della figura/contenitore in pixel CSS; None usa il default. Plotly ha altezza predefinita 800. Non indica la dimensione del font. |

| `height` | Dimensioni richieste della figura/contenitore in pixel CSS; None usa il default. Plotly ha altezza predefinita 800. Non indica la dimensione del font. |

| `accordion` | True racchiude grafico interattivo/tabella HTML in una sezione collassabile. Non è un’opzione delle tabelle native. |

| `expanded` | Stato iniziale dell’accordion: True aperto, False collassato. |

| `result_type` | D3: html (default) oppure svg (Svg nativo jamovi). Svg conserva le interazioni supportate in Results e fornisce una figura statica per i documenti. |



### mzpjShowLine


Linee D3, con ordinamento e gestione delle interruzioni espliciti.


```python
mzpjShowLine(dataset, x, y, group=None, labels=None, sort_x=False, connect_gaps=False, show_points=True, name=None, title=None, x_label=None, y_label=None, color='#3e6da9', width=None, height=None, accordion=True, expanded=True, result_type='html')
```


| Argomento | Significato |
|---|---|

| `dataset` | Dizionario di colonne con liste di uguale lunghezza, normalmente data. Nessuna conversione automatica in DataFrame pandas. |

| `x` | Nome della colonna numerica per questo asse. |

| `y` | Nome della colonna numerica per questo asse. |

| `group` | Nome opzionale della colonna di raggruppamento; non diventa automaticamente un predittore statistico. |

| `labels` | D3: nome opzionale della colonna con etichette delle osservazioni. Chart.js: lista di etichette delle categorie. |

| `sort_x` | Ordina i punti per x entro gruppo, invece di seguire l’ordine delle righe. |

| `connect_gaps` | True collega i segmenti anche oltre osservazioni mancanti. |

| `show_points` | Mostra anche le singole osservazioni/punti oltre al riepilogo o alla linea. |

| `name` | Chiave univoca del risultato per questa esecuzione; None la genera. Per mzpjUseLibrary indica il nome della libreria nel catalogo. |

| `title` | Titolo visibile; None usa quello predefinito della funzione. |

| `x_label` | Etichetta visibile dell’asse; None usa quella predefinita. |

| `y_label` | Etichetta visibile dell’asse; None usa quella predefinita. |

| `color` | Colore del grafico; usare un colore CSS come #3e6da9. |

| `width` | Dimensioni richieste della figura/contenitore in pixel CSS; None usa il default. Plotly ha altezza predefinita 800. Non indica la dimensione del font. |

| `height` | Dimensioni richieste della figura/contenitore in pixel CSS; None usa il default. Plotly ha altezza predefinita 800. Non indica la dimensione del font. |

| `accordion` | True racchiude grafico interattivo/tabella HTML in una sezione collassabile. Non è un’opzione delle tabelle native. |

| `expanded` | Stato iniziale dell’accordion: True aperto, False collassato. |

| `result_type` | D3: html (default) oppure svg (Svg nativo jamovi). Svg conserva le interazioni supportate in Results e fornisce una figura statica per i documenti. |



### mzpjShowIntervals


Visualizzazione D3 di stime e intervalli già calcolati.


```python
mzpjShowIntervals(dataset, estimate, lower, upper, labels=None, reference=None, interval_label='Interval', name=None, title=None, x_label=None, y_label=None, color='#3e6da9', width=None, height=None, accordion=True, expanded=True, result_type='html')
```


| Argomento | Significato |
|---|---|

| `dataset` | Dizionario di colonne con liste di uguale lunghezza, normalmente data. Nessuna conversione automatica in DataFrame pandas. |

| `estimate` | Nomi delle colonne numeriche con stima e limiti dell’intervallo già calcolato. La chiamata grafica non calcola gli intervalli. |

| `lower` | Nomi delle colonne numeriche con stima e limiti dell’intervallo già calcolato. La chiamata grafica non calcola gli intervalli. |

| `upper` | Nomi delle colonne numeriche con stima e limiti dell’intervallo già calcolato. La chiamata grafica non calcola gli intervalli. |

| `labels` | D3: nome opzionale della colonna con etichette delle osservazioni. Chart.js: lista di etichette delle categorie. |

| `reference` | Linea verticale opzionale di riferimento numerico nel grafico degli intervalli. |

| `interval_label` | Etichetta dell’intervallo fornito, es. Normal-Wald 95% CI; il grafico non ne verifica il significato statistico. |

| `name` | Chiave univoca del risultato per questa esecuzione; None la genera. Per mzpjUseLibrary indica il nome della libreria nel catalogo. |

| `title` | Titolo visibile; None usa quello predefinito della funzione. |

| `x_label` | Etichetta visibile dell’asse; None usa quella predefinita. |

| `y_label` | Etichetta visibile dell’asse; None usa quella predefinita. |

| `color` | Colore del grafico; usare un colore CSS come #3e6da9. |

| `width` | Dimensioni richieste della figura/contenitore in pixel CSS; None usa il default. Plotly ha altezza predefinita 800. Non indica la dimensione del font. |

| `height` | Dimensioni richieste della figura/contenitore in pixel CSS; None usa il default. Plotly ha altezza predefinita 800. Non indica la dimensione del font. |

| `accordion` | True racchiude grafico interattivo/tabella HTML in una sezione collassabile. Non è un’opzione delle tabelle native. |

| `expanded` | Stato iniziale dell’accordion: True aperto, False collassato. |

| `result_type` | D3: html (default) oppure svg (Svg nativo jamovi). Svg conserva le interazioni supportate in Results e fornisce una figura statica per i documenti. |



### mzpjShowDistribution


Esploratore didattico normale di popolazione/media campionaria; non genera un campione.


```python
mzpjShowDistribution(mean=0, sd=1, n=30, mode='sample_mean', interactive=True, name=None, title=None, x_label=None, y_label=None, color='#3e6da9', width=None, height=None, accordion=True, expanded=True, result_type='html')
```


| Argomento | Significato |
|---|---|

| `mean` | Media nota della popolazione e sua deviazione standard strettamente positiva nel modello didattico normale. |

| `sd` | Media nota della popolazione e sua deviazione standard strettamente positiva nel modello didattico normale. |

| `n` | Numerosità positiva nel modello didattico normale; l’errore standard della media è sd/sqrt(n). |

| `mode` | Vista didattica normale: sample_mean oppure population; non genera osservazioni e non stima un modello. |

| `interactive` | Abilita i controlli interni dell’esploratore normale. Non rieseguono Python. |

| `name` | Chiave univoca del risultato per questa esecuzione; None la genera. Per mzpjUseLibrary indica il nome della libreria nel catalogo. |

| `title` | Titolo visibile; None usa quello predefinito della funzione. |

| `x_label` | Etichetta visibile dell’asse; None usa quella predefinita. |

| `y_label` | Etichetta visibile dell’asse; None usa quella predefinita. |

| `color` | Colore del grafico; usare un colore CSS come #3e6da9. |

| `width` | Dimensioni richieste della figura/contenitore in pixel CSS; None usa il default. Plotly ha altezza predefinita 800. Non indica la dimensione del font. |

| `height` | Dimensioni richieste della figura/contenitore in pixel CSS; None usa il default. Plotly ha altezza predefinita 800. Non indica la dimensione del font. |

| `accordion` | True racchiude grafico interattivo/tabella HTML in una sezione collassabile. Non è un’opzione delle tabelle native. |

| `expanded` | Stato iniziale dell’accordion: True aperto, False collassato. |

| `result_type` | D3: html (default) oppure svg (Svg nativo jamovi). Svg conserva le interazioni supportate in Results e fornisce una figura statica per i documenti. |



### mzpjShowCorrelation


Esploratore descrittivo di correlazioni Pearson/Spearman.


```python
mzpjShowCorrelation(dataset, columns, labels=None, missing='pairwise', method='pearson', name=None, title=None, color='#3e6da9', width=None, height=None, accordion=True, expanded=True, result_type='html')
```


| Argomento | Significato |
|---|---|

| `dataset` | Dizionario di colonne con liste di uguale lunghezza, normalmente data. Nessuna conversione automatica in DataFrame pandas. |

| `columns` | Nomi delle colonne nell’ordine desiderato. RowStatistic: colonne numeriche da combinare; Correlation: colonne della matrice; Table: colonne da presentare. |

| `labels` | D3: nome opzionale della colonna con etichette delle osservazioni. Chart.js: lista di etichette delle categorie. |

| `missing` | Mancanti nella matrice di correlazione: pairwise oppure listwise. Con pairwise le celle possono avere numerosità differenti. |

| `method` | Correlazione: pearson oppure spearman. Ranghi: average, min, max, dense oppure ordinal per i pareggi. |

| `name` | Chiave univoca del risultato per questa esecuzione; None la genera. Per mzpjUseLibrary indica il nome della libreria nel catalogo. |

| `title` | Titolo visibile; None usa quello predefinito della funzione. |

| `color` | Colore del grafico; usare un colore CSS come #3e6da9. |

| `width` | Dimensioni richieste della figura/contenitore in pixel CSS; None usa il default. Plotly ha altezza predefinita 800. Non indica la dimensione del font. |

| `height` | Dimensioni richieste della figura/contenitore in pixel CSS; None usa il default. Plotly ha altezza predefinita 800. Non indica la dimensione del font. |

| `accordion` | True racchiude grafico interattivo/tabella HTML in una sezione collassabile. Non è un’opzione delle tabelle native. |

| `expanded` | Stato iniziale dell’accordion: True aperto, False collassato. |

| `result_type` | D3: html (default) oppure svg (Svg nativo jamovi). Svg conserva le interazioni supportate in Results e fornisce una figura statica per i documenti. |



### mzpjShowPaired


Esploratore di misure appaiate con coppie complete.


```python
mzpjShowPaired(dataset, first, second, group=None, labels=None, name=None, title=None, first_label=None, second_label=None, y_label=None, color='#3e6da9', width=None, height=None, accordion=True, expanded=True, result_type='html')
```


| Argomento | Significato |
|---|---|

| `dataset` | Dizionario di colonne con liste di uguale lunghezza, normalmente data. Nessuna conversione automatica in DataFrame pandas. |

| `first` | Nomi delle colonne numeriche appaiate; una coppia per riga. |

| `second` | Nomi delle colonne numeriche appaiate; una coppia per riga. |

| `group` | Nome opzionale della colonna di raggruppamento; non diventa automaticamente un predittore statistico. |

| `labels` | D3: nome opzionale della colonna con etichette delle osservazioni. Chart.js: lista di etichette delle categorie. |

| `name` | Chiave univoca del risultato per questa esecuzione; None la genera. Per mzpjUseLibrary indica il nome della libreria nel catalogo. |

| `title` | Titolo visibile; None usa quello predefinito della funzione. |

| `first_label` | Etichette visibili delle due misurazioni appaiate. |

| `second_label` | Etichette visibili delle due misurazioni appaiate. |

| `y_label` | Etichetta visibile dell’asse; None usa quella predefinita. |

| `color` | Colore del grafico; usare un colore CSS come #3e6da9. |

| `width` | Dimensioni richieste della figura/contenitore in pixel CSS; None usa il default. Plotly ha altezza predefinita 800. Non indica la dimensione del font. |

| `height` | Dimensioni richieste della figura/contenitore in pixel CSS; None usa il default. Plotly ha altezza predefinita 800. Non indica la dimensione del font. |

| `accordion` | True racchiude grafico interattivo/tabella HTML in una sezione collassabile. Non è un’opzione delle tabelle native. |

| `expanded` | Stato iniziale dell’accordion: True aperto, False collassato. |

| `result_type` | D3: html (default) oppure svg (Svg nativo jamovi). Svg conserva le interazioni supportate in Results e fornisce una figura statica per i documenti. |



### mzpjShowTestDistribution


Esploratore teorico delle code t/chi-quadrato/F, non un test stimato automaticamente.


```python
mzpjShowTestDistribution(distribution='t', df=10, df2=20, statistic=2, tail='right', alpha=0.05, name=None, title=None, color='#3e6da9', width=None, height=None, accordion=True, expanded=True, result_type='html')
```


| Argomento | Significato |
|---|---|

| `distribution` | Distribuzione teorica sotto H0: t, chi2 oppure f. Non stima un test sulle colonne del dataset. |

| `df` | Gradi di libertà interi da 1 a 120. df2 è il secondo grado di libertà della F. |

| `df2` | Gradi di libertà interi da 1 a 120. df2 è il secondo grado di libertà della F. |

| `statistic` | RowStatistic: mean, sum, sd, var, median, mad, min, max, range, n. TestDistribution: valore fornito della statistica teorica. |

| `tail` | left, right oppure two-sided (bilaterale disponibile soltanto per t). |

| `alpha` | Soglia di significatività nell’esploratore teorico, da 0.001 a 0.2; non è una stima dell’affidabilità alpha. |

| `name` | Chiave univoca del risultato per questa esecuzione; None la genera. Per mzpjUseLibrary indica il nome della libreria nel catalogo. |

| `title` | Titolo visibile; None usa quello predefinito della funzione. |

| `color` | Colore del grafico; usare un colore CSS come #3e6da9. |

| `width` | Dimensioni richieste della figura/contenitore in pixel CSS; None usa il default. Plotly ha altezza predefinita 800. Non indica la dimensione del font. |

| `height` | Dimensioni richieste della figura/contenitore in pixel CSS; None usa il default. Plotly ha altezza predefinita 800. Non indica la dimensione del font. |

| `accordion` | True racchiude grafico interattivo/tabella HTML in una sezione collassabile. Non è un’opzione delle tabelle native. |

| `expanded` | Stato iniziale dell’accordion: True aperto, False collassato. |

| `result_type` | D3: html (default) oppure svg (Svg nativo jamovi). Svg conserva le interazioni supportate in Results e fornisce una figura statica per i documenti. |



### mzpjShowChart


Renderer Chart.js; valori e calcoli statistici provengono dallo script.


```python
mzpjShowChart(chart_type, datasets, *, labels=None, name=None, title=None, options=None, width=None, height=None, accordion=True, expanded=True, static=False, floating_legend=None)
```


| Argomento | Significato |
|---|---|

| `chart_type` | Tipo Chart.js: bar, line, scatter, bubble, pie, doughnut, radar oppure polarArea. |

| `datasets` | Lista di dizionari dataset Chart.js con label/data e proprietà grafiche opzionali. I valori devono essere compatibili con JSON. |

| `labels` | D3: nome opzionale della colonna con etichette delle osservazioni. Chart.js: lista di etichette delle categorie. |

| `name` | Chiave univoca del risultato per questa esecuzione; None la genera. Per mzpjUseLibrary indica il nome della libreria nel catalogo. |

| `title` | Titolo visibile; None usa quello predefinito della funzione. |

| `options` | Dizionario di opzioni Chart.js; questa configurazione JSON non accetta callback Python o funzioni JavaScript. |

| `width` | Dimensioni richieste della figura/contenitore in pixel CSS; None usa il default. Plotly ha altezza predefinita 800. Non indica la dimensione del font. |

| `height` | Dimensioni richieste della figura/contenitore in pixel CSS; None usa il default. Plotly ha altezza predefinita 800. Non indica la dimensione del font. |

| `accordion` | True racchiude grafico interattivo/tabella HTML in una sezione collassabile. Non è un’opzione delle tabelle native. |

| `expanded` | Stato iniziale dell’accordion: True aperto, False collassato. |

| `static` | False: HTML interattivo, senza fotografia nativa. True: una sola fotografia statica in Svg nativo per l’esportazione; non conserva l’interattività. |

| `floating_legend` | Configurazione opzionale della legenda Chart.js trascinabile/collassabile; None mantiene quella ordinaria. Le chiavi sono nella guida Chart.js. |



### mzpjShowPlotly


Presenta una figura Plotly interattiva oppure una fotografia statica esplicita.


```python
mzpjShowPlotly(figure, *, name=None, title=None, height=800, config=None, static=False, export_width=960)
```


| Argomento | Significato |
|---|---|

| `figure` | Oggetto Figure di Plotly, ad esempio plotly.graph_objects.Figure, già costruito dallo script. |

| `name` | Chiave univoca del risultato per questa esecuzione; None la genera. Per mzpjUseLibrary indica il nome della libreria nel catalogo. |

| `title` | Titolo visibile; None usa quello predefinito della funzione. |

| `height` | Dimensioni richieste della figura/contenitore in pixel CSS; None usa il default. Plotly ha altezza predefinita 800. Non indica la dimensione del font. |

| `config` | Dizionario di configurazione browser Plotly, es. displaylogo=False; distinto da figure.layout. |

| `static` | False: HTML interattivo, senza fotografia nativa. True: una sola fotografia statica in Svg nativo per l’esportazione; non conserva l’interattività. |

| `export_width` | Larghezza intera della fotografia statica Plotly, 400–2400 pixel; default 960. |



### mzpjRecode


Restituisce una lista ricodificata, conservando righe e regole sui mancanti.


```python
mzpjRecode(values, mapping, *, unmatched='keep')
```


| Argomento | Significato |
|---|---|

| `values` | Sequenza monodimensionale; conserva le posizioni delle righe. Gli helper numerici accettano None/NaN come mancanti. |

| `mapping` | Dizionario dai valori originali ai nuovi valori; None può ricodificare esplicitamente i mancanti. Nessuna espressione viene valutata. |

| `unmatched` | Per valori non presenti nella mappa: keep, missing oppure raise. |



### mzpjRowStatistic


Restituisce UNA statistica per riga in UNA lista. Non assegna automaticamente una colonna al dataset.


```python
mzpjRowStatistic(dataset, columns, *, statistic='mean', reverse=None, bounds=None, min_valid=None, ddof=1, mad_scale=1)
```


| Argomento | Significato |
|---|---|

| `dataset` | Dizionario di colonne con liste di uguale lunghezza, normalmente data. Nessuna conversione automatica in DataFrame pandas. |

| `columns` | Nomi delle colonne nell’ordine desiderato. RowStatistic: colonne numeriche da combinare; Correlation: colonne della matrice; Table: colonne da presentare. |

| `statistic` | RowStatistic: mean, sum, sd, var, median, mad, min, max, range, n. TestDistribution: valore fornito della statistica teorica. |

| `reverse` | Nomi degli item selezionati da invertire con minimo+massimo-valore; richiede bounds. |

| `bounds` | Tupla (minimo, massimo); valida tutti gli item selezionati e definisce gli estremi per l’inversione. Valori fuori limite producono errore. |

| `min_valid` | Minimo numero di item osservati per riga. None richiede tutti gli item selezionati. n conta sempre gli osservati indipendentemente da questa soglia. |

| `ddof` | Correzione del denominatore SD/varianza: 1 campionaria (default), 0 popolazione. Osservazioni/item insufficienti danno un mancante. |

| `mad_scale` | Divisore MAD: 1 dà la deviazione assoluta mediana grezza; normal dà il MAD normalizzato; sono accettati divisori numerici positivi. |



### mzpjStandardize


Restituisce valori centrati/standardizzati, opzionalmente entro gruppi.


```python
mzpjStandardize(values, *, by=None, ddof=1, center=True, scale=True, on_constant='missing')
```


| Argomento | Significato |
|---|---|

| `values` | Sequenza monodimensionale; conserva le posizioni delle righe. Gli helper numerici accettano None/NaN come mancanti. |

| `by` | Sequenza opzionale dei gruppi, lunga quanto values. Gruppi mancanti producono risultati mancanti. |

| `ddof` | Correzione del denominatore SD/varianza: 1 campionaria (default), 0 popolazione. Osservazioni/item insufficienti danno un mancante. |

| `center` | Standardize: sottrae la media del gruppo e/o divide per la SD ordinaria del gruppo. scale=False centra soltanto; disabilitare center non usa il RMS non centrato. |

| `scale` | Standardize: sottrae la media del gruppo e/o divide per la SD ordinaria del gruppo. scale=False centra soltanto; disabilitare center non usa il RMS non centrato. |

| `on_constant` | Standardizzazione di gruppi costanti/insufficienti: missing (default) oppure raise. |



### mzpjRank


Restituisce ranghi con pareggi, direzione e gruppi opzionali espliciti.


```python
mzpjRank(values, *, by=None, method='average', descending=False)
```


| Argomento | Significato |
|---|---|

| `values` | Sequenza monodimensionale; conserva le posizioni delle righe. Gli helper numerici accettano None/NaN come mancanti. |

| `by` | Sequenza opzionale dei gruppi, lunga quanto values. Gruppi mancanti producono risultati mancanti. |

| `method` | Correlazione: pearson oppure spearman. Ranghi: average, min, max, dense oppure ordinal per i pareggi. |

| `descending` | True assegna rango 1 al valore maggiore; False al minore. |



### mzpjEffectSize


Restituisce liste yi, vi, sei, status, una voce per studio. Non stima un modello aggregato.


```python
mzpjEffectSize(measure, *, correction=0.5, to='only0', drop00=False, correct=True, invalid='raise', **inputs)
```


| Argomento | Significato |
|---|---|

| `measure` | OR, RR, RD, MD, SMD, COR, ZCOR, PR, PLO, ARAW, AHW, ABT oppure GEN. Vettori richiesti e scala sono nella sezione metanalisi. |

| `correction` | Correzione di continuità non negativa per OR/RR/RD/PR/PLO; default 0.5. |

| `to` | only0 corregge tutte le celle di ogni studio con zeri; all corregge tutti gli studi; none disabilita la correzione. |

| `drop00` | True esclude studi senza eventi o con tutti eventi in entrambi i bracci prima della correzione, conservando righe mancanti. Solo OR/RR/RD. |

| `correct` | SMD: True usa la correzione esatta di Hedges, False il d non corretto di Cohen; varianza LS in entrambi. False non è ammesso per altre misure. |

| `invalid` | raise interrompe su uno studio invalido indicandone la riga; missing marca come mancanti i valori finiti invalidi con uno status. Errori strutturali/di tipo restano errori. |

| `inputs` | Vettori con nome per EffectSize: OR/RR/RD ai,bi,ci,di; MD/SMD m1i,sd1i,n1i,m2i,sd2i,n2i; COR/ZCOR ri,ni; PR/PLO xi,ni; alpha ai,mi,ni; GEN yi e vi oppure sei. |



### mzpjEffectInterval


Restituisce liste estimate, lower, upper: IC normali-Wald dei singoli studi, con trasformazione grafica opzionale.


```python
mzpjEffectInterval(yi, *, vi=None, sei=None, level=0.95, transform='identity')
```


| Argomento | Significato |
|---|---|

| `yi` | Stime sulla scala di analisi, una per studio. Per OR/RR è la scala logaritmica. |

| `vi` | Varianza campionaria oppure errore standard sulla scala di analisi. Fornire una sola fonte quando richiesto. Non è la varianza di eterogeneità. |

| `sei` | Varianza campionaria oppure errore standard sulla scala di analisi. Fornire una sola fonte quando richiesto. Non è la varianza di eterogeneità. |

| `level` | Probabilità di confidenza tra 0 e 1, default 0.95; non una percentuale come 95. |

| `transform` | EffectInterval: identity, exp, tanh, logistic, ahw, abt per stima/IC visualizzati. SamplingVariance: identity, log, fisher soltanto per estremi Wald noti. |



### mzpjSamplingVariance


Restituisce liste vi e sei a partire da una sola fonte nota di incertezza.


```python
mzpjSamplingVariance(*, sei=None, vi=None, ci_lower=None, ci_upper=None, level=0.95, transform='identity')
```


| Argomento | Significato |
|---|---|

| `sei` | Varianza campionaria oppure errore standard sulla scala di analisi. Fornire una sola fonte quando richiesto. Non è la varianza di eterogeneità. |

| `vi` | Varianza campionaria oppure errore standard sulla scala di analisi. Fornire una sola fonte quando richiesto. Non è la varianza di eterogeneità. |

| `ci_lower` | Vettori degli estremi inferiore/superiore di intervalli noti come normali-Wald, sulla scala dichiarata. |

| `ci_upper` | Vettori degli estremi inferiore/superiore di intervalli noti come normali-Wald, sulla scala dichiarata. |

| `level` | Probabilità di confidenza tra 0 e 1, default 0.95; non una percentuale come 95. |

| `transform` | EffectInterval: identity, exp, tanh, logistic, ahw, abt per stima/IC visualizzati. SamplingVariance: identity, log, fisher soltanto per estremi Wald noti. |



### mzpjMetaWeights


Restituisce liste weight e percent da 1/(vi+tau2); non stima un modello.


```python
mzpjMetaWeights(vi, *, tau2=0)
```


| Argomento | Significato |
|---|---|

| `vi` | Varianza campionaria oppure errore standard sulla scala di analisi. Fornire una sola fonte quando richiesto. Non è la varianza di eterogeneità. |

| `tau2` | Varianza tra studi fornita come scalare non negativo, default 0. Non viene stimata l’eterogeneità. |



### mzpjResourcePath


Restituisce il percorso temporaneo di una risorsa Pj esplicitamente fornita.


```python
mzpjResourcePath(filename)
```


| Argomento | Significato |
|---|---|

| `filename` | Nome di una risorsa Pj esplicitamente inclusa, attualmente mzPj_icon_python.png. Restituisce un percorso temporaneo valido durante l’esecuzione; non cerca file generici del modulo. |



### mzpjUseLibrary


Restituisce il modulo Python importato dopo la scelta della fonte. Non installa pacchetti.


```python
mzpjUseLibrary(name, source='bundled')
```


| Argomento | Significato |
|---|---|

| `name` | Chiave univoca del risultato per questa esecuzione; None la genera. Per mzpjUseLibrary indica il nome della libreria nel catalogo. |

| `source` | bundled carica la copia di Pj; system usa gli import ordinari dell’interprete selezionato, anche embedded. Non cambia interprete. |



### mzpjListLibraries


Restituisce record del catalogo per ShowTable; disponibilità non significa verifica funzionale di ogni pacchetto.


```python
mzpjListLibraries()
```


| Argomento | Significato |
|---|---|



## Examples / Esempi

```python
# One row statistic -> one new output column.
data['custom_mean'] = mzpjRowStatistic(data, ['Sepal.Length', 'Sepal.Width'],
                                     statistic='mean', min_valid=2)
mzpjShowTable({'Mean': data['custom_mean'][:10]}, title='First ten rows')
```

```python
# HTML table: two alternating colours, zero-based cell selection.
mzpjShowTable([{'Group':'A','Mean':4.2}, {'Group':'B','Mean':5.1}],
              render='html', zebra=['#eef4fb','#ffffff'],
              cell_styles={(1,'Mean'):{'color':'#3e6da9','bold':True}},
              accordion=True, max_height=260, max_width=700, scroll='both')
```

```python
# D3 from explicit values: no external dataset needed.
mzpjShowScatter({'x':[1,2,3], 'y':[2,4,3]}, 'x','y',
                title='Illustrative observations', result_type='svg')
```

```python
# Bundled module selection before importing its submodules.
plotly = mzpjUseLibrary('plotly')
import plotly.graph_objects as go
fig = go.Figure(go.Bar(x=['A','B'], y=[4,7]))
mzpjShowPlotly(fig, static=True, title='Static document figure')
```

```python
# Independent-study estimates, analysis-scale variance, back-transformed display.
effects = mzpjEffectSize('RR', ai=[4,8], bi=[26,42], ci=[8,15], di=[27,40])
display = mzpjEffectInterval(effects['yi'], vi=effects['vi'], transform='exp')
mzpjShowTable(display, title='Risk ratios and 95% CI')
```


## Metanalisi per studio: scegliere gli input

OR/RR/RD usano eventi/non-eventi di due gruppi indipendenti; MD/SMD medie, SD e
numerosità dei gruppi; COR/ZCOR r e N; PR/PLO eventi e N totale; ARAW/AHW/ABT
alpha, numero di item e N dei partecipanti; GEN effetto e vi/SE.
SMD restituisce per default g di Hedges con J esatto e varianza LS. OR/RR sono
effetti logaritmici, non rapporti grezzi; ZCOR è Fisher z, PLO un logit, ABT
-log(1-alpha). EffectSize restituisce liste yi,vi,sei,status. I conteggi devono
essere interi; alpha < 1; correlazioni strettamente tra -1 e 1 con N > 3.
Un input richiesto mancante rende mancanti tutti i risultati dello studio senza
eliminarne la riga. invalid='missing' gestisce valori finiti invalidi, non errori
di tipo, lunghezza o input infiniti.
EffectInterval calcola IC normali-Wald dei singoli studi, non intervalli di
predizione. SamplingVariance ricostruisce SE dagli estremi soltanto se gli IC
sono noti come normali-Wald sulla scala scelta. MetaWeights usa tau2 fornito,
non stima l’eterogeneità. Nessuna funzione stima un modello aggregato.
Con celle zero, correction=0.5,to='only0' aggiunge 0.5 a TUTTE le celle dello
studio interessato, modificando anche i denominatori. È una convenzione
esplicita, non una scelta universalmente appropriata. Gli IC grezzi non sono
troncati ai limiti naturali. Ritrasformare gli IC non ritrasforma vi. Consultare
la guida dettagliata delle misure prima dell’utilizzo.

