# Interazione e moderazione in due grafici — Pj 1.7.0

L’helper `mzpjShowInteraction()` stima il modello `Y ~ X * moderatore + covariate`
e prepara due pannelli, due tabelle native e un report numerico. Si usa in poche
righe, senza scrivere la regressione, i contrasti e i grafici nell’editor.
NumPy e SciPy sono necessari nel Python selezionato; i due runtime Windows
usati per la preview li includono. Non servono pacchetti Python Plotly o
statsmodels. Non estendere questa disponibilità all’embedded macOS senza
verifica: può servire System Python. Nessuna installazione automatica.

```python
report = mzpjShowInteraction(data, 'Dose', 'Score', 'Age',
                            covariates=['Baseline'], unit='Participant')
```

## Interpretazione

Pannello 1 (in alto per default): media della risposta prevista dal modello rispetto a X a diversi
valori del moderatore, con intervalli di confidenza puntuali. Per default sono
usati i quantili16%,50%,84% sui casi completi, rimuovendo duplicati e ricorrendo
a minimo/massimo se necessario. Con `moderator_values=[30,45,60]` si scelgono
fino a cinque valori distinti entro il range osservato. I punti grigi sono
risposte osservate, non risposte aggiustate. Le covariate sono fissate alle loro
medie sui casi completi.

Pannello 2 (in basso per default): effetto condizionale di X lungo il moderatore e relativa incertezza.
Lo zero è il riferimento orizzontale tratteggiato; le verticali puntinate
indicano le soglie Johnson–Neyman interne al range osservato. I punti colorati
corrispondono alle curve del pannello 1. I checkbox **Visible curves** di Plotly Html coordinano curve, bande e punti
senza ricalcolare il modello; in D3 questa funzione è svolta dalla legenda. D3 permette anche focus, selezione e Reset.

Le bande riguardano la media stimata, non la previsione di un nuovo individuo.
Essere entro i range marginali non garantisce un buon supporto congiunto di
X e moderatore: alcune combinazioni possono essere scarsamente osservate.
La figura non dimostra un effetto causale né sostituisce la diagnosi del modello.

## Opzioni principali

- `moderator_type='continuous'` è il default. Un moderatore numerico a due
  gruppi richiede invece `'binary'`; non viene indovinato il significato dei codici.
- `covariates` ammette fino a16 colonne numeriche distinte, inserite in modo
  additivo. X, Y e moderatore sono tre colonne diverse; X e il moderatore
  continuo richiedono almeno tre valori distinti. Disegni costanti/ridondanti
  vengono rifiutati, senza eliminare termini silenziosamente.
- Sono usati i casi completi per tutte le colonne selezionate, incluso unit.
  Testo/booleani non sono misure numeriche; mancanti/non finiti sono esclusi.
- `unit` controlla identificatori ripetuti sui casi mantenuti. Le righe devono
  essere indipendenti: questo non è un modello misto, RM, cluster-robusto,
  pesato, logistico o multivariato. Senza unit l’indipendenza non è verificabile.
- `covariance='HC3'` usa inferenza Wald Normale asintotica con covarianza robusta
  all’eteroschedasticità. `'OLS'` usa varianza residua e t di Student con N−p gdl.
  HC3 non corregge dipendenza o forma del modello e non garantisce copertura
  esatta nei piccoli campioni. Leverage vicino a uno viene rifiutato.
- `level=.95` è la confidenza espressa come proporzione fra0 e1; `points=81`
  controlla la griglia (21–201).
- `renderer='plotly'` oppure `'d3'` cambia solo il disegno. `result_type` può
  essere html/svg/image. Per Image restano cattura silenziosa e titoli conservati;
  Svg/Image non hanno accordion/zoom Html. Svg Plotly incorpora PNG.
- `show_points=False` omette i punti osservati senza modificare la stima;
  è necessario oltre5000 casi completi. Nessun sottocampionamento nascosto.
- `tables=False` disattiva le due tabelle. `name` identifica figura e tabelle;
  omettendolo si generano nomi distinti.
- `width=None`, `height=None`: ogni dimensione omessa usa il PopUp, poi il
  default Pj600×500. Un argomento esplicito prevale per quella figura.
  Larghezza400–2400 per pannelli impilati,720–2400 affiancati; altezza440–1600.
  Plotly Html è responsive;
  width controlla la larghezza statica. D3 può aggiungere altezza per le note.
- `accordion`, `expanded`, `accordion_type`, `modebar` e `palette` seguono gli
  helper grafici. La barra Plotly resta nascosta, salvo richiesta esplicita.

## Moderatore a due gruppi

```python
report = mzpjShowInteraction(data, 'Dose', 'Score', 'Treatment',
                            moderator_type='binary', reference='Control',
                            covariates=['Baseline'], unit='Participant')
```

Servono esattamente due livelli sui casi completi. Il riferimento è codificato0,
l’altro1; omettendolo vale l’ordine deterministico delle categorie, sempre
riportato. Si mostrano le due rette e le due pendenze, senza regioni J–N.
Più di due livelli richiedono contrasti progettati esplicitamente.

## Coefficienti, intervalli e limiti inferenziali

X, covariate e moderatore continuo sono centrati alle medie; per il calcolo QR
si usa anche una scala interna. Le tabelle restituiscono coefficienti e
covarianza nelle unità originali della **parametrizzazione centrata**. Il
moderatore binario resta0/1. Il coefficiente di X è quindi l’effetto al
moderatore medio oppure nel gruppo di riferimento; quello del moderatore
è l’effetto a X medio. L’intercetta non è quella all’origine grezza delle colonne.
Medie e codifica sono documentate nelle note e nel report.

L’effetto di X è beta_X + beta_XM × moderatore centrato. La varianza del
contrasto include la covarianza incrociata. Le soglie Johnson–Neyman risolvono
l’equazione effetto² − critico² × varianza=0. Si riportano soltanto radici entro
il range osservato, usando lo stesso criterio t/Normale del modello.
Gli intervalli sono **puntuali**, senza correzione FDR o familiare: non sono
bande simultanee. Il modello è dichiarato, non selezionato cercando soglie
favorevoli. I controlli su rango e leverage non sostituiscono un esame diagnostico.

## Report e prova

Il report restituisce formula, N, esclusioni, gdl, R², metodo di covarianza,
centratura/riferimento, coefficienti e matrice di covarianza, effetti condizionali
e regioni/soglie J–N osservate. Le tabelle native conservano p-value numerici.

Lo [script79](../pjscript/79_interaction_model.py) genera partecipanti indipendenti
simulati: provare i due renderer e Html/Svg/Image nei due Python. La [guida
inglese](mzPj_interaction.md) contiene firma completa, test e riferimenti.
Le verifiche confrontano i risultati numerici con statsmodels indipendente;
il PASSED automatico non sostituisce il collaudo visivo dell’autore.

## Disposizione e interazione dei grafici

`panel_layout='stacked'` è il default: ciascun pannello usa tutta la larghezza
utile. Dimensioni omesse: prima i valori del PopUp, poi il default600×500.
Non vengono più assegnate altezze automatiche1020/620. Per pannelli più alti
si può impostare Height800 nel PopUp o passare `height=800`. Un argomento
esplicito prevale; `panel_layout` non cambia le dimensioni. Usare
l'affiancamento solo con un'area Results sufficientemente ampia. Le note Plotly
Html si adattano alla larghezza effettiva del contenitore e ai suoi cambiamenti.

In Plotly Html si trascina un rettangolo dentro un pannello per ingrandire gli
assi. **Reset axes** ripristina gli intervalli originali di entrambi i pannelli.
Il cursore **Figure size** ingrandisce invece tutta la figura e la sua area in
Results; **Reset size** ripristina le dimensioni iniziali. È distinto dallo zoom
degli assi e svolge il ruolo del cursore dimensionale D3 Html.
La barra Plotly resta nascosta per default; `modebar=True` la rende disponibile.

Cliccando un punto colorato nel pannello 2 si evidenzia la curva corrispondente
nel pannello 1. Un testo riporta la variazione stimata della risposta per un'unità
di X, intervallo e p-value. **Show all curves** annulla l'evidenziazione e ripristina
le curve nascoste. I checkbox **Visible curves** nascondono o mostrano insieme curva, banda e punto.
Show all curves è disabilitato quando tutte le curve sono già visibili e non
ci sono evidenziazioni da annullare. Reset axes è disabilitato agli intervalli
originali.
Queste operazioni non ristimano il modello. Nei risultati Svg/Image nativi i
controlli Html non vengono esportati.

Lo zoom dimensionale D3 Html espande anche il contenitore del grafico e del risultato. Non introduce un riquadro interno fisso con barre di scorrimento. Una figura più larga dello spazio disponibile in Results o sullo schermo può comunque richiedere lo scorrimento esterno. Il ridimensionamento nativo Svg/Image rimane invariato.
