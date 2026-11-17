# Modelli a misure ripetute con il backend Rust

[English version](mzPj_repeated_measures.md). Candidata Pj 1.6.0 con
**pj_stats_rust 1.1.0**. I calcoli non richiedono NumPy, SciPy, pandas o R;
R serve soltanto a generare i riferimenti indipendenti dei test.

## Modelli e disegno supportato

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

## Firme e input

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

## Ipotesi e interpretazione

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

## Alternative moderne

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

## Esempio e verifiche

Lo script `73_rust_repeated_measures.py` usa **dati simulati dichiarati**:
quattro modelli, 17 tabelle e due grafici D3 dei profili osservati. Non modifica
il dataset aperto. Per i dati reali sostituire esplicitamente le liste delle
colonne: anche con Iris aperto lo script analizza il suo esempio simulato.

Riferimenti indipendenti in `tests/reference_repeated.R`:24 disegni con 2/3/4
tempi,una/due VD,zero/tre gruppi sbilanciati,zero/due covariate e soggetti
incompleti. Il test Python verifica 2.405 valori, equivalenza col t appaiato a
due tempi, rango, mancanti, ordine/unità di misura e covarianza congiunta
singolare. [R anova.mlm](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/anova.mlm.html).

Build native Windows x64 e Ubuntu 26.04 WSL2 x64 PASSED; il binario Linux passa
anche nel Python 3.13 del Flatpak jamovi 28.17.0.0 (etichetta AppStream 28.7). Questa prova non certifica tutte le
funzioni salvataggio/export di Pj 1.6.0 su quel Flatpak meno recente. Gate della
desktop ufficiale/minApp invariato; build macOS e verifica visiva/export della
nuova candidata ancora da completare.


Lo script 73 richiede esplicitamente `result_type="svg"` per i due grafici. Nei Results resta l’accordion; l’export nativo riceve soltanto grafico, legenda e note. La compatibilita’ del salvataggio OMV con Svg resta una verifica separata sulla versione jamovi installata.
