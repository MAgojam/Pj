# Tipi di risultato grafico: Html, Svg e Image

> **Pj 1.6.1 / jamovi 28.18 (18 novembre 2026).** Il minimo è ora
> jamovi 28.18.0 inclusa. Il runtime ufficiale include la correzione del
> salvataggio dei documenti con Svg nativo. Gli avvisi precedenti qui sotto
> descrivono la 28.17. Restano separati i limiti delle proporzioni Office e del
> ridimensionamento Rj; vedi le [note 1.6.1](mzPj_release_1_6_1.md).


Pj 1.6.0 offre `result_type='html'`, `'svg'` oppure `'image'` per Chart.js,
Plotly e tutti i dieci helper grafici D3. La scelta determina il contenitore
nativo nei Results di jamovi; non modifica i calcoli statistici.

| Scelta | Comportamento | Risultato nativo dopo la preparazione |
|---|---|---|
| `html` | Grafico interattivo con i suoi controlli | `Html` |
| `svg` | Contenuto della figura, assi, legenda e note; senza controlli interattivi | `Svg` |
| `image` | Acquisizione PNG dello stesso contenuto della figura | `Image` |

D3 mantiene la geometria vettoriale in Svg. Per Chart.js e Plotly, Svg contiene
un'acquisizione PNG dentro un contenitore SVG: non è una conversione vettoriale.
Con `image` si ottiene invece un vero Image nativo. Lo sfondo acquisito è bianco.

## Scelta nel codice Python

```python
mzpjShowChart('bar', [{'label': 'Mean', 'data': [2.5, 3.8]}],
              labels=['A', 'B'], name='group_means',
              title='Group means', result_type='image', width=700, height=360,
              options={'locale': 'en-US'})

mzpjShowLine({'Time': [0, 1, 2], 'Score': [3, 5, 4]}, 'Time', 'Score',
             name='profile', title='Observed profile', result_type='svg')

# figure è un oggetto Figure di Plotly creato dal chiamante.
# mzpjShowPlotly(figure, name='plotly_image', result_type='image')
```

La preparazione di Image avviene nel browser dei Results di Pj/Pjp dopo il
ritorno da Python. Un breve messaggio viene sostituito dall'immagine nativa.
Attendere che tutti i messaggi di preparazione siano scomparsi prima di
esportare o salvare il documento jamovi. Un errore viene indicato esplicitamente;
non si ripiega silenziosamente su Html o Svg.

L'immagine comprende solo il contenuto della figura: esclude pulsanti,
controlli dell'accordion, zoom, tooltip e pannelli flottanti. Il titolo resta
un'intestazione nativa dei Results. La risposta del browser identifica la
figura corrente con un token univoco e sostituisce solo quel risultato
provvisorio. Conserva gli altri Results, Output e dataext e non riesegue Python.
Risposte vecchie o duplicate vengono ignorate.

Le immagini grandi vengono ridimensionate fino a 4 milioni di pixel e a un
massimo di 4000 pixel per lato; le dimensioni di visualizzazione arrivano a
2000 pixel. Ogni PNG ammette al massimo 1 milione di caratteri base64. Le
acquisizioni in attesa condividono un limite di 1,5 milioni di caratteri e
20 figure per risposta, oltre al limite complessivo dei Results di Pj.
Se necessario ridurre le dimensioni o dividere il rapporto fra più analisi.

## Compatibilità e servizio Python

Le chiamate esistenti restano valide. D3 usa Html come impostazione iniziale.
Per Chart.js e Plotly, `static=False` conserva Html e `static=True` conserva
Svg. `result_type` sceglie esplicitamente il tipo; la combinazione
`static=True, result_type='html'` è contraddittoria e viene rifiutata.
Per il nuovo codice è preferibile `result_type`.

La scelta `image` per questi renderer JavaScript richiede il collegamento
browser/backend dei nuovi editor Pj/Pjp. L'API R del servizio Python non lo
abilita e rifiuta questa scelta con un errore esplicativo. Un altro modulo
deve implementare una propria integrazione di acquisizione supportata; non
basta abilitare un flag.

Il percorso PNG originale rimane disponibile negli editor e nei servizi:

```python
import io
# figure è una Figure Matplotlib; serve Matplotlib nell'interprete selezionato.
buffer = io.BytesIO()
figure.savefig(buffer, format='png', dpi=150, facecolor='white')
mzpjShowImage(buffer, name='my_plot', title='My plot')
buffer.close()
```

`mzpjShowImage` accetta direttamente byte PNG validi o un buffer/stream binario.
Anche `plt.show()` di Matplotlib acquisito da Pj produce Image. `mzpjShowHtml`
rimane Html: il selettore non rasterizza automaticamente pagine HTML arbitrarie.
Gli esempi 05, 06 e 24 mostrano il percorso PNG originale; il 74 confronta le
nuove modalità. I grafici statistici degli esempi 71–73 ora usano Image nativo.

## Verifiche ed esportazioni — 16 novembre 2026

Per questo aggiornamento si compila e verifica soltanto Windows. Pj resta
1.6.0, Rust resta 1.1.0 e minApp resta jamovi 28.17.0 inclusa.

I test browser acquisiscono Chart.js, D3 e Plotly, anche con accordion D3
chiuso e più figure contemporanee. I test del ciclo del motore coprono Pj e
Pjp con Python Embedded e System: conservazione dello stato, risposte vecchie
o duplicate, rifiuto di PNG non validi e assenza di riesecuzione Python.
Il nuovo Image viene renderizzato in PDF tramite il normale renderer R.

Questi controlli non certificano ancora l'intero percorso desktop
PDF/DOCX/LaTeX/OMV del nuovo selettore: resta il collaudo manuale con la
portable Windows 28.17.2. Le precedenti verifiche Word includevano Svg nativi,
ma i precedenti ZIP LaTeX li omettevano. Il successo di Image PNG non certifica
il distinto percorso Svg. La portable corretta 28.17.2 è soltanto Windows;
nessuna nuova compilazione o prova Ubuntu/macOS è eseguita per questo lavoro.
Restano separati l'impaginazione delle tabelle Word larghe e la compilazione TeX.
