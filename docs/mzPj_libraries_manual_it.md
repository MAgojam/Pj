# Manuale delle librerie Python per Pj

Guida operativa con esempi e riferimento statistico. Pj 1.6.0, pj_stats_rust 1.1.0. Edizione del 16 novembre 2026.

Questo manuale è destinato a chi scrive script negli editor Pj e Pjp di jamovi. Spiega come scegliere e attivare le librerie fornite dal modulo, preparare i dati, produrre risultati e usare il backend statistico Rust. Gli esempi sono riproducibili; le analisi richiedono comunque un disegno corretto e un’interpretazione coerente delle ipotesi.

## 1 Ambiente di lavoro e dati

Pj riceve il dataset disponibile nell’editor; Pjp riceve le variabili selezionate nel supplier. In entrambi, data è un dizionario di liste di colonne, non un DataFrame automatico. Le posizioni delle righe devono restare allineate quando si combinano variabili. I mancanti del dataset sono normalmente None. Usare i nomi esatti delle colonne.

```python
print(list(data))
# The following example needs these two selected input columns.
# pairs = [(a, b) for a, b in zip(data['x'], data['y'])
#          if a is not None and b is not None]
```

Creare data["nuova_colonna"] richiede l’Output verso il dataset corrente secondo il meccanismo Pj già previsto: non sovrascrivere una colonna di input. Le analisi, le tabelle e i grafici prodotti dagli helper finiscono nei Results. dataext è un dataset distinto, inizialmente vuoto: Read legge un OMV esterno e Save salva dataext nella destinazione scelta. Il salvataggio del documento jamovi conserva script e analisi; il salvataggio del dataset esterno ha uno scopo diverso.

Le funzioni di trasformazione restituiscono copie. Ordinamento, merge e passaggio long/wide non devono modificare separatamente le righe di variabili appaiate. La guida delle trasformazioni e quella dataext completano il presente manuale.

## 2 Interprete e sorgente delle librerie

Python interpreter sceglie Embedded, incluso in jamovi, oppure System, installato sul computer. È una scelta diversa dalla sorgente della libreria. mzpjUseLibrary(..., source="bundled") usa la copia distribuita da Pj anche con System Python. source="system" usa le normali importazioni dell’interprete selezionato e non cambia interprete. Attivare le librerie prima di importarle; un conflitto con una copia già importata viene segnalato e richiede di correggere l’ordine e rieseguire lo script.

```python
mzpjShowTable(mzpjListLibraries(), title='Available libraries')
sp = mzpjUseLibrary('sympy')
# Independent installation, selected before import:
# sp = mzpjUseLibrary('sympy', source='system')
```

Il catalogo non importa le librerie. Available non certifica ogni loro funzione; Active descrive l’esecuzione corrente. SymPy attiva mpmath, Jinja2 attiva MarkupSafe, Plotly attiva le dipendenze dichiarate. Il bundle Python puro viene verificato tramite SHA e preparato in una cache privata. Il backend Rust è selezionato per sistema e architettura; i binari non sono intercambiabili tra Windows, Linux e macOS.

NumPy, SciPy, pandas e matplotlib non sono inclusi nel bundle di Pj. Possono essere presenti nell’interprete Embedded o System e vanno verificati nelle informazioni Python. Le funzioni Rust qui descritte non richiedono questi package.

## 3 Librerie Python distribuite

| Import | Versione | Dipendenze fornite |
| --- | --- | --- |
| sympy | 1.14.0 | mpmath |
| mpmath | 1.3.0 | None |
| jinja2 | 3.1.6 | markupsafe |
| markupsafe | 3.0.3 | None |
| tabulate | 0.10.0 | None |
| uncertainties | 3.2.3 | None |
| simpy | 4.1.1 | None |
| more_itertools | 10.8.0 | None |
| plotly | 7.1.0 | narwhals, packaging |
| narwhals | 2.26.0 | None |
| packaging | 26.3 | None |

### Matematica simbolica

`sympy` 1.14.0. Espressioni esatte, derivate, integrali e algebra. Usare Rational per le frazioni esatte. Grafici, parsing LaTeX e generazione di codice possono richiedere componenti opzionali.

```python
sp = mzpjUseLibrary('sympy')
x = sp.Symbol('x')
result = sp.integrate(x**2, (x, 0, 1))
print(result)  # 1/3
```

### Calcolo numerico ad alta precisione

`mpmath` 1.3.0. Il contesto ripristina la precisione precedente alla fine del blocco. Convertire in mpf un float già arrotondato non recupera cifre perse: per costanti decimali usare stringhe.

```python
mp = mzpjUseLibrary('mpmath')
with mp.workdps(40):
    integral = mp.quad(lambda x: x*x, [0, 1])
    print(mp.nstr(integral, 30))
```

### Modelli per i report

`jinja2` 3.1.6. Separare struttura del report e valori. Attivare escaping per i dati HTML; produrre testo oppure passare i valori tabellari al normale helper Pj.

```python
jinja = mzpjUseLibrary('jinja2')
env = jinja.Environment(autoescape=True)
text = env.from_string('<p>{{ label }}</p>').render(label='<A>')
print(text)  # <p>&lt;A&gt;</p>
```

### Escaping dei valori HTML

`markupsafe` 3.0.3. MarkupSafe esegue escaping del testo: non valida né analizza statisticamente il dataset. È incluso il fallback Python puro.

```python
safe = mzpjUseLibrary('markupsafe')
print(safe.escape('<study A & B>'))
```

### Tabelle di testo leggibili

`tabulate` 0.10.0. Utile per riepiloghi in console. Per le tabelle native nei Results usare mzpjShowTable: il testo stampato non diventa automaticamente una tabella nativa.

```python
tb = mzpjUseLibrary('tabulate')
print(tb.tabulate([['A', 12], ['B', 15]],
                  headers=['Group', 'N'], tablefmt='github'))
```

### Propagazione delle incertezze

`uncertainties` 3.2.3. La propagazione al primo ordine conserva la dipendenza se si riutilizza lo stesso oggetto incerto. Non equivale a un intervallo di confidenza né sostituisce l’inferenza campionaria.

```python
unc = mzpjUseLibrary('uncertainties')
x = unc.ufloat(2.0, 0.1)
y = x*x
print(y.nominal_value, y.std_dev)  # 4.0 0.4
print((x-x).std_dev)  # 0.0
```

### Simulazione di processi e code

`simpy` 4.1.1. Il tempo simulato dipende dal modello, non dal tempo dell’orologio. Per le code occorrono ipotesi esplicite su arrivi/servizio e un seed quando si introduce casualità.

```python
simpy = mzpjUseLibrary('simpy')
env = simpy.Environment()
def task():
    yield env.timeout(3)
    print('Completion time', env.now)
env.process(task())
env.run()
```

### Raggruppamenti e finestre mobili

`more_itertools` 10.8.0. Gli iteratori si consumano durante la lettura. Conservare deliberatamente l’ordine dei soggetti: finestre adiacenti non sono osservazioni indipendenti.

```python
mi = mzpjUseLibrary('more_itertools')
print(list(mi.chunked([1, 2, 3, 4, 5], 2)))
print(list(mi.windowed([1, 2, 3, 4], 3)))
```

### Grafici interattivi ed esportabili

`plotly` 7.1.0. Pj fornisce il ponte di rendering e le risorse JavaScript. Il risultato statico è destinato anche all’esportazione nativa: verificare salvataggio/export nella build jamovi in uso. L’esempio non richiede servizi browser esterni.

```python
mzpjUseLibrary('plotly')
import plotly.graph_objects as go
fig = go.Figure(go.Bar(x=['A', 'B'], y=[4, 7]))
mzpjShowPlotly(fig, name='manual_plot', static=True,
               title='Illustrative counts')
```

### Scelta del tipo grafico nativo

Aggiornamento grafici (16 novembre 2026): Chart.js, Plotly e D3 condividono `result_type='html'|'svg'|'image'`. Per esportare PNG nativi usare Image e attendere la preparazione nei Results. `static=True` conserva Svg. La [guida ai tipi grafici](mzPj_graphic_result_types_it.md) spiega esempi, limiti e verifiche Windows.

Html mantiene i controlli interattivi. Svg conserva i vettori D3, ma contiene PNG per Chart.js e Plotly. Image acquisisce soltanto la figura e la conserva come Image nativo: attendere la sostituzione del messaggio di preparazione prima di esportare. Il callback non riesegue Python. Questa acquisizione richiede gli editor Pj/Pjp; negli host dell’API R resta disponibile mzpjShowImage con byte PNG già pronti. Il collaudo di questo aggiornamento riguarda solo Windows; le esportazioni desktop del nuovo selettore richiedono ancora accettazione.

```python
mzpjShowChart('bar', [{'data': [2.5, 3.8]}],
              labels=['A', 'B'], result_type='image',
              name='mean_chart', title='Illustrative means')
```

### Interoperabilità tra dataframe

`narwhals` 2.26.0. Narwhals adatta implementazioni dataframe supportate: non fornisce pandas, Polars o Arrow. Il ramo opzionale è dimostrativo e viene eseguito solo se pandas è già installato nell’interprete scelto.

```python
nw = mzpjUseLibrary('narwhals')
print(nw.__version__)
# An optional installed backend is required for a real dataframe.
try:
    import pandas as pd
except ImportError:
    print('Optional pandas backend not installed')
else:
    frame = nw.from_native(pd.DataFrame({'x': [1, 2, 3]}))
    print(frame.select(nw.col('x').mean()).to_native())
```

### Versioni e requisiti software

`packaging` 26.3. Confrontare versioni interpretate, non stringhe di caratteri. La selezione delle sorgenti può riutilizzare un packaging già caricato e compatibile secondo il contratto del bundle.

```python
mzpjUseLibrary('packaging')
from packaging.version import Version
print(Version('1.6.0') > Version('1.5.0'))  # True
print(Version('1.10') > Version('1.9'))  # True
```

## 4 Riferimento delle funzioni statistiche native

La libreria si importa con import pj_stats_rust as rust e riporta __version__. Nomi e argomenti sono sensibili a maiuscole e minuscole. I nomi storici *_robusta non implicano SE sandwich: ANCOVA e MANCOVA sono modelli classici. Le funzioni univariate richiedono valori numerici finiti; rimuovere i mancanti esplicitamente conservando le coppie. Matrici di correlazione e modelli con gruppi hanno politiche dedicate riportate sotto.

### calcola somma

```python
rust.calcola_somma(dati)
```

Somma compensata di valori finiti; la lista vuota restituisce zero.

### calcola media

```python
rust.calcola_media(dati)
```

Media aritmetica stabile di una lista finita non vuota.

### descrittive complete

```python
rust.descrittive_complete(dati)
```

Almeno due valori finiti. Varianza/SD campionarie, quartili, MAD scalata, asimmetria/curtosi corrette e intervallo t al 95 per cento della media. Momenti non definiti: None.

### quantili

```python
rust.quantili(dati, prob=None)
```

Interpolazione Hyndman–Fan tipo 7; probabilità tra 0 e 1.

### frequenze

```python
rust.frequenze(valori)
```

Categorie stringa, etichette ripulite e vuote escluse. Frequenze, percentuali e cumulative.

### correlazione pearson

```python
rust.correlazione_pearson(x, y)
```

Almeno tre coppie finite e varianze positive; test t e intervallo Fisher al 95 per cento.

### correlazione spearman

```python
rust.correlazione_spearman(x, y)
```

Ranghi medi per parimeriti esatti e p asintotico basato su t, non test esatto di permutazione.

### matrice correlazione

```python
rust.matrice_correlazione(colonne, metodo=None)
```

Colonne nominate della stessa lunghezza, osservazioni finite pairwise. Coppie con meno di tre casi completi omesse; coppie valide costanti generano errore.

### ttest campione singolo

```python
rust.ttest_campione_singolo(dati, mu0=None)
```

Test t a un campione, media teorica zero di default; serve varianza campionaria positiva.

### ttest indipendente

```python
rust.ttest_indipendente(g1, g2, var_uguali=None)
```

Welch di default; var_uguali=True seleziona Student pooled. Intervallo della differenza e Cohen d pooled.

### ttest appaiato

```python
rust.ttest_appaiato(prima, dopo)
```

Coppie finite e allineate della stessa lunghezza; differenza prima meno dopo. Serve varianza positiva delle differenze.

### mann whitney u

```python
rust.mann_whitney_u(g1, g2)
```

Mann–Whitney bilaterale asintotico, corretto per parimeriti e continuità. u_stat è min(U1,U2); presenti anche u1/u2.

### regressione lineare

```python
rust.regressione_lineare(x, y)
```

OLS semplice con un predittore. Almeno tre righe finite allineate; predittore/risposta costanti e varianza residua nulla sono rifiutati per l’inferenza.

### anova robusta

```python
rust.anova_robusta(y, gruppi)
```

Righe Fisher, Welch e Kruskal–Wallis. Casi completi, almeno due gruppi con due osservazioni ciascuno; Welch richiede varianze positive nei gruppi.

### ancova robusta

```python
rust.ancova_robusta(y, gruppi, covariata)
```

ANCOVA classica con gruppo e una covariata continua, effetti parziali e medie aggiustate alla media generale inclusa della covariata. Senza SE sandwich.

### manova robusta

```python
rust.manova_robusta(y_vars, gruppi)
```

Due o più colonne risposta nominate; test congiunti del gruppo Pillai, Wilks e Hotelling–Lawley. Servono covarianza residua non singolare e df sufficienti.

### mancova robusta

```python
rust.mancova_robusta(y_vars, gruppi, covariata)
```

Modello multivariato classico del gruppo aggiustato per una covariata continua. Ipotesi parziale del gruppo tramite modelli ridotto e pieno.

### bootstrap media

```python
rust.bootstrap_media(dati, n_reps=None, alpha=None, seed=123456789)
```

Bootstrap percentile della media con seed; conserva le vecchie chiavi dei risultati.

### bootstrap statistica

```python
rust.bootstrap_statistica(dati, statistica='media', n_reps=10000, alpha=0.05, seed=123456789)
```

Bootstrap percentile con seed per media o mediana, almeno tre valori finiti; da 2 a 1000000 repliche e 0<alpha<1.

### correggi p

```python
rust.correggi_p(p_values, metodo='holm')
```

Holm, Bonferroni, BH/fdr, BY o none. Conserva le posizioni mancanti e conta i p validi nella molteplicità di default.

### contingenza

```python
rust.contingenza(conteggi)
```

Chi-quadro Pearson senza Yates, Cramer V, attesi e residui Pearson. Test asintotico: controllare la diagnostica delle celle sparse.

### statistiche righe

```python
rust.statistiche_righe(colonne, statistica='media', min_validi=1)
```

Calcolo per riga di media/somma/min/max/SD campionaria/conteggio, conservando le posizioni. None/NaN omessi per riga, infiniti rifiutati.

### rm anova

```python
rust.rm_anova(misure, gruppi=None, livelli=None, missing='listwise')
```

Una VD ripetuta in condizioni ordinate, gruppi tra soggetti opzionali. Test entro-soggetto univariati e multivariati.

### rm ancova

```python
rust.rm_ancova(misure, covariate, gruppi=None, livelli=None, missing='listwise')
```

Una VD ripetuta aggiustata per una o più covariate continue nominate e fisse nel tempo.

### rm manova

```python
rust.rm_manova(misure, gruppi=None, livelli=None, missing='listwise')
```

Due o più VD nominate agli stessi tempi ordinati; test congiunti dei profili e diagnostica per esito.

### rm mancova

```python
rust.rm_mancova(misure, covariate, gruppi=None, livelli=None, missing='listwise')
```

Più VD ripetute e una o più covariate per soggetto; esclusione listwise condivisa tra tutti gli esiti.

Per il bootstrap, alpha è la probabilità esclusa dall’intervallo: alpha=0.05 produce un intervallo percentile al 95 per cento. Il seed riproduce i risultati nella stessa versione del backend. Il limite è un miliardo di valori ricampionati per chiamata. La mediana è più costosa della media e non produce intervalli BCa. Nei test di contingenza controllare gli attesi: il p-value asintotico non sostituisce Fisher nelle tabelle sparse.

## 5 Esempio guidato dalla descrizione al risultato

L’esempio seguente usa valori dichiarati e non altera il dataset. Prima controlla la distribuzione dei dati, poi valuta una differenza appaiata e infine ottiene un intervallo bootstrap della media. Le tre operazioni rispondono a domande diverse: il bootstrap della media non sostituisce il test sulla differenza appaiata.

```python
import pj_stats_rust as rust
before = [10., 11., 9., 12., 8., 13., 10., 12.]
after  = [11., 11., 11., 14., 9., 13., 12., 15.]
mzpjShowTable([rust.descrittive_complete(before)], title='Before')
mzpjShowTable([rust.ttest_appaiato(before, after)], title='Paired test')
interval = rust.bootstrap_media(before, n_reps=10000, seed=731)
mzpjShowTable([interval], title='Mean bootstrap interval')
```

Controllare prima di Run che le due liste descrivano gli stessi soggetti nello stesso ordine. Il test appaiato usa prima meno dopo: una stima negativa indica valori medi più alti nella seconda lista. Un p piccolo non dimostra validità delle assunzioni o importanza clinica. L’intervallo è espresso nell’unità delle misure.

## 6 Analisi a misure ripetute

### Modelli e disegno supportato

| Funzione | Variabili dipendenti | Covariate continue per soggetto |
| --- | --- | --- |
| `rm_anova` | Una | Nessuna |
| `rm_ancova` | Una | Una o più |
| `rm_manova` | Due o più agli stessi tempi | Nessuna |
| `rm_mancova` | Due o più agli stessi tempi | Una o più |

Questa versione gestisce **un fattore entro-soggetto** (tempo/condizione), un
**eventuale fattore di gruppo tra soggetti**, covariate continue fisse nel tempo.
Le condizioni ordinate sono comuni a tutti i soggetti. Le distanze temporali
non sono usate come regressore continuo. Non sono implementati più fattori
entro-soggetto, covariate variabili nel tempo o interazioni gruppo×covariata.
Una caratteristica categoriale come il genere è un fattore, non una covariata
continua solo perché codificata con numeri.

Dati in formato **wide**: ogni lista è una colonna temporale e ogni posizione
corrisponde allo **stesso soggetto** in tutte le colonne, esiti, gruppi e
covariate. La funzione non ricostruisce gli ID né aggrega righe duplicate.
Per i dati long usare prima le [trasformazioni del dataset](mzPj_datasets_it.md).

```python
import pj_stats_rust as rust
misure = [list(data['PA_T0']), list(data['PA_T1']), list(data['PA_T2'])]
covariate = {'eta': list(data['eta']), 'BMI_basale': list(data['BMI_0'])}
gruppo = list(data['trattamento'])  # etichette stringa; facoltativo
r = rust.rm_ancova(misure, covariate, gruppi=gruppo,
                  livelli=['Basale', '3 mesi', '6 mesi'])
mzpjShowTable(r['univariate'], title='RM-ANCOVA')
mzpjShowTable(r['sphericity'], title='Sfericità residua')
```

### Firme e input

```python
rust.rm_anova(misure, gruppi=None, livelli=None, missing='listwise')
rust.rm_ancova(misure, covariate, gruppi=None, livelli=None, missing='listwise')
rust.rm_manova(misure, gruppi=None, livelli=None, missing='listwise')
rust.rm_mancova(misure, covariate, gruppi=None, livelli=None, missing='listwise')
```

Per RM-ANOVA/ANCOVA `misure` è la lista delle colonne temporali. Per
RM-MANOVA/MANCOVA è un dizionario **nome esito → lista delle colonne temporali**:

```python
profili = {
    'Ansia': [list(data['A_T0']), list(data['A_T1']), list(data['A_T2'])],
    'Sonno': [list(data['S_T0']), list(data['S_T1']), list(data['S_T2'])],
}
r = rust.rm_mancova(profili, covariate, gruppi=gruppo)
mzpjShowTable(r['multivariate'], title='Test congiunti dei profili')
```

`covariate` contiene nomi e colonne numeriche a livello del soggetto; deve
essere non vuoto per ANCOVA/MANCOVA. Le covariate vengono centrate sulla media
dei **soggetti effettivamente inclusi**. Evitare di duplicare esattamente una
VD basale nella covariata se questo rende degenere l'ipotesi o la covarianza
residua. L'ordine dei tempi è quello delle liste: non viene ordinato per nome.
`livelli` deve contenere etichette uniche e non vuote, una per colonna; altrimenti
si usano T1,T2,... . Esiti, covariate e livelli del gruppo sono ordinati in modo
riproducibile. Ogni gruppo incluso deve avere almeno due soggetti. Una colonna
di gruppo con un solo livello viene rifiutata: va omessa se non serve.

`None` e NaN sono mancanti, gli infiniti generano errore. Per il gruppo sono
mancanti `None` e le etichette vuote. Con `missing='listwise'` si esclude tutto
il soggetto se manca un valore richiesto in **qualsiasi esito** o covariata.
Tutti i test del report usano lo stesso insieme di soggetti. Con
`missing='raise'` il primo soggetto incompleto genera errore. `included_rows`
restituisce gli indici originali a base zero; non si spostano separatamente le
colonne e non si imputano valori. `data` e `dataext` non vengono modificati.

### Ipotesi e interpretazione

Modello con intercetta, contrasti a somma zero per i gruppi e covariate centrate.
I test sono **parziali di tipo III**, cioè ogni termine è valutato dopo gli altri.
`Time` valuta il profilo medio con **uguale peso per ogni livello del gruppo**,
alle covariate centrate. Con gruppi sbilanciati non equivale automaticamente
alla media pesata per numerosità. Sono disponibili Time×Group e Time×ciascuna
covariata, oltre agli effetti tra soggetti sulle medie temporali. Non si aggiunge
automaticamente Group×covariata.

Il calcolo usa contrasti temporali ortonormali e proiezioni QR con controllo
del rango e riortogonalizzazione. Non tratta le righe soggetto×tempo come
osservazioni indipendenti, non inverte le equazioni normali e non sottrae due
SSCP quasi uguali. Il lavoro numerico è Rust con rilascio del lock Python.

Ogni funzione restituisce:

| Chiave | Contenuto |
| --- | --- |
| `n_input`, `n_subjects`, `n_excluded`, `included_rows` | Contabilità dei soggetti e indici originali inclusi, a base zero |
| `levels`, `outcomes`, `groups`, `covariate_reference`, `subject_error_df` | Disegno effettivo, centri delle covariate e df residui del soggetto |
| `univariate` | F, df, p non corretto, eta quadrato parziale, epsilon e p GG/HF per esito/effetto |
| `multivariate` | Pillai, Wilks e Hotelling–Lawley congiunti per profili entro-soggetto e medie tra soggetti |
| `sphericity` | Mauchly residuo con correzione di secondo ordine ed epsilon GG/HF per esito |
| `descriptives` | N, media e SD osservate per gruppo/tempo: **non medie marginali aggiustate** |
| `notes`, `ss_type`, `missing`, `model` | Metodo e indicazioni interpretative |

Nelle righe univariate `df1` e `df2` sono **non corretti**: per GG moltiplicarli
entrambi per `epsilon_GG`; per HF per `epsilon_HF`. F non cambia. Gli effetti
tra soggetti non richiedono correzioni di sfericità. Con due tempi epsilon=1 e
Mauchly non è applicabile: statistiche/p mancanti con stato esplicito.
Le correzioni sono per singolo esito, non per una miscela di unità di misura.

Anche RM-ANOVA/ANCOVA con una sola VD restituiscono i test multivariati dei
contrasti temporali: un'alternativa senza assunto di sfericità nel medesimo
disegno. Con più VD si valuta congiuntamente il profilo esito×tempo. Servono
covarianza residua non singolare e sufficienti df residui; qui i df del soggetto
devono superare la dimensione del profilo testato. Se non disponibili, le righe
hanno `None` e una motivazione in `status`; restano i test univariati validi.
Analoga indicazione per Mauchly non calcolabile. Controllare sempre gli stati.
Non si corregge automaticamente la molteplicità tra esiti, effetti e statistiche:
scegliere le ipotesi a priori e usare `correggi_p` quando appropriato.

Servono rango pieno e df residui positivi. Covariate collineari vengono rifiutate,
non eliminate silenziosamente. Limiti operativi:256 colonne esito×tempo, 64
colonne del disegno tra soggetti, 10 milioni di valori per modello. Restano le
assunzioni del GLM classico, indipendenza tra soggetti e pendenze delle covariate
comuni tra gruppi. L'esecuzione riuscita non certifica tali assunzioni né
rimuove automaticamente il confondimento in senso causale.

### Alternative moderne

Queste funzioni implementano il GLM classico richiesto, **non modelli misti**.
Un LMM gaussiano è una possibile estensione per tempi specifici del soggetto,
covariate variabili nel tempo e traiettorie incomplete. Richiede una struttura
esplicita di effetti casuali e covarianza residua. Non elimina le ipotesi sul
meccanismo dei mancanti: likelihood e dati incompleti richiedono un modello
appropriato e i predittori mancanti richiedono comunque una strategia.
Riferimenti: [lme](https://stat.ethz.ch/R-manual/R-devel/library/nlme/html/lme.html)
e [lmer](https://lme4.github.io/lme4/reference/lmer.html).

Possibile sviluppo successivo: LMM gaussiano ML/REML con intercetta casuale,
poi pendenza casuale, diagnostica/predizioni e successivamente modelli misti
multivariati. **Non sono implementati** nella libreria1.1.0; non si riciclano
per essi i df e i test F del GLM attuale.



Lo script 73 fornisce la guida eseguibile completa: quattro modelli, 17 tabelle e due grafici dei profili osservati, su dati simulati esplicitamente dichiarati. Si può eseguire con qualsiasi dataset aperto perché non usa data come sorgente. Per passare ai dati reali sostituire le liste in modo esplicito; non confrontare automaticamente i risultati simulati con Iris.

### Risultati guidati dello script 73

I dati sono simulati. Le linee rappresentano medie osservate di gruppo, non traiettorie individuali né medie aggiustate. Si usano 44 soggetti completi dei 45 iniziali, dopo un’esclusione condivisa.

![Profiles](manuals/assets/rm_profiles_IT.png)

| Modello | N | F Pillai | df1 | df2 | p |
| --- | --- | --- | --- | --- | --- |
| RM-ANOVA | 44 | 0.841 | 2 | 40 | 0.439 |
| RM-ANCOVA | 44 | 0.802 | 2 | 38 | 0.4558 |
| RM-MANOVA | 44 | 3.753 | 4 | 38 | 0.01141 |
| RM-MANCOVA | 44 | 3.897 | 4 | 36 | 0.009914 |

La tabella riporta il test multivariato di Time. Ogni riga valuta il proprio profilo e aggiustamento: confrontare i p-value tra modelli non costituisce una procedura di selezione del modello. Il valore numerico è una guida al controllo dello script, non una conclusione clinica.

## 7 Verifica dei risultati e compatibilità

Il minimo dichiarato per il modulo è jamovi 28.17.0. I pacchetti di rilascio restano Pj 1.6.0 per Windows x64, Linux x64, macOS Intel e macOS Apple Silicon; i due macOS sono compilati con GitHub Actions e richiedono i rispettivi esiti. La prova visiva con jamovi 28.17.0 su Windows e Ubuntu WSL2 precede il commit firmato e il rilascio. Una build riuscita o un test numerico non equivale a una prova GUI di salvataggio/esportazione.

Per la nuova libreria RM sono disponibili 24 disegni di riferimento R e 2.405 confronti numerici. Windows e Ubuntu WSL2 passano i test automatici; il Python del Flatpak è verificato separatamente. Flatpak può mostrare un’etichetta AppStream obsoleta: nel sistema usato qui l’etichetta 28.7 corrispondeva al programma reale 28.17.0.0. Per identificare la versione usare il programma e jamovi --version.

Se una funzione non viene trovata, verificare la versione del backend nel JMO installato, non solo nei sorgenti. Con errori di rango controllare covariate duplicate e gruppi insufficienti; con None o stati unavailable leggere la motivazione. Se un package opzionale manca, controllare l’interprete scelto prima di installarlo altrove. Per importazioni da sorgenti diverse correggere l’ordine e rieseguire lo script.

## 8 Riferimenti e materiali di lavoro

Gli esempi 71, 72 e73 sono nella cartella pjscript del repository. Il riferimento completo degli helper Pj resta nel manuale delle funzioni; le guide OMV, dataext e trasformazioni spiegano i file e i dataset esterni. Le versioni delle librerie riportate qui derivano dal catalogo distribuito e non promettono aggiornamenti automatici a ogni rilascio upstream.

- [R repeated measures GLM](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/anova.mlm.html)
- [R multiple testing](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/p.adjust.html)
- [R mixed models with nlme](https://stat.ethz.ch/R-manual/R-devel/library/nlme/html/lme.html)
- [R mixed models with lme4](https://lme4.github.io/lme4/reference/lmer.html)
- [PyO3 parallelism](https://pyo3.rs/v0.29.0/parallelism)
