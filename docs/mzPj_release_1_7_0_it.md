# Pj 1.7.0

Richiede jamovi 28.18.0 o successiva. Sono previsti pacchetti Windows x64,
Linux x64, macOS Intel e Apple Silicon. Scegliere il JMO del proprio sistema.

## Nuovi helper grafici

- Renderer offline comuni mzGraphics per D3 e Plotly, con sorgenti non minificati
  riproducibili forniti separatamente dalle librerie dei rispettivi autori.
- Cinque helper Plotly guidati: dispersione, linee, barre, boxplot e heatmap.
  Non richiedono il package Python Plotly. La barra è nascosta per default;
  modebar=True o 'hover' la rendono disponibile quando serve.
- mzpjShowInteraction stima un modello di interazione per osservazioni
  indipendenti, con moderatore continuo o binario ed eventuali covariate numeriche.
  Due pannelli mostrano medie stimate e pendenze condizionali, con tabelle native
  e report numerico. Richiede NumPy e SciPy nel Python selezionato.

HC3 usa inferenza asintotica Normale/Wald; OLS usa gradi di libertà residui e t
di Student. Gli intervalli sono puntuali, non simultanei né di predizione
individuale. Identificativi ripetuti sono rifiutati: non è un modello misto o
a misure ripetute. Per moderatori continui include informazioni Johnson–Neyman
entro il range osservato. Consultare la guida prima dell’interpretazione.

## Dimensioni e correzioni di rendering

I grafici generati usano prima gli argomenti width/height, poi i valori Settings
della popup, poi 600 per 500 pixel. Vale per Html, Svg e Image. Gli helper diretti
PNG/SVG conservano le proporzioni quando si passa una sola dimensione locale.
Lo script 80 illustra la precedenza nei tre motori.

Lo slider sottile comune espande tutta la figura Html e il suo spazio nei Results.
Lo zoom sugli assi Plotly è separato. Svg/Image nativi usano il ridimensionamento
jamovi senza accordion o controlli zoom Html. La preparazione Image è fuori
dall’area visibile; le immagini finali conservano il titolo senza segnaposto
Preparing Image.

I Chart Html invariati riutilizzano canvas e stato della legenda dopo Run.
Tutte le chiamate Python restano eseguite: dati, opzioni o dimensioni pertinenti
aggiornano il Chart. La geometria Plotly è sincronizzata per evitare sovrapposizioni
con le tabelle successive.

## Esempi e documentazione

Gli script 77–80 coprono renderer comuni, helper Plotly, interazione stimata e
precedenza delle dimensioni. L’intera raccolta pubblica è stata controllata sul
runner Python 1.7.0. Restano espliciti i requisiti di package esterni opzionali.
Gli esempi della Data Library conservano le analisi salvate: aggiungere una nuova
analisi Pj/Pjp nello stesso documento per confrontarle. Il salvataggio delle
modifiche lascia invariato il file originale della Data Library.

Manuali delle librerie IT/EN aggiornati alla 1.7.0 in Markdown, Word e PDF,
insieme ai riferimenti delle funzioni e alle guide grafiche specifiche.

## Compatibilità

L’API del servizio resta alla versione 1. pj_stats_rust resta alla 1.1.0: i quattro
binari esistenti sono riutilizzati senza ricompilare il progetto Rust privato.
I test sono materiale di sviluppo ed esclusi dal JMO di installazione, come
script e manuali.

L’accettazione visiva Windows e WSL2 dell’autore è distinta dai test automatici.
Actions macOS verifica build e backend; non implica una prova desktop visiva.
La posizione dell’aggancio di ridimensionamento Ubuntu dipende dal runtime host;
argomenti locali e Settings offrono un controllo alternativo delle dimensioni.
Verificare il formato di esportazione desiderato con il jamovi installato.
