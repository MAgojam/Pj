# Statistica nativa Rust in Pj / Pjp

## Distribuzione della libreria nativa — 17 novembre 2026

Nel repository e nei JMO entrano i **binari Python/Rust**, il loader Python
e i metadati in `inst/python/pj_stats_rust` e
`inst/extdata/mzPj_native_libraries.json`. Il progetto Rust non completato
**`pj_stats_rust/` alla radice di Pj rimane soltanto locale**: escluso da
`.gitignore` e `.Rbuildignore`, non entra nel commit né nei JMO.
I comandi di compilazione/test che fanno riferimento a quel progetto locale
sono riservati al manutentore e non funzionano dal solo clone pubblico Pj.

Disponibili e verificati i binari Windows x64 e Linux x64. **Mancano ancora
Apple Intel (`macosx_x86_64`) e Apple Silicon (`macosx_arm64`)**. Il workflow
macOS richiede il binario precompilato della propria architettura e si ferma
prima del JMO se non c'è; non acquisisce né pubblica i sorgenti Rust locali.
La release completa per quattro piattaforme resta da completare con i due
binari Apple e le verifiche previste. Il commit non pubblica una release.


## Versione corrente 1 1 0

Aggiunti i quattro modelli a misure ripetute; vedere la
[guida RM](mzPj_repeated_measures_it.md) e il
[manuale completo delle librerie](mzPj_libraries_manual_it.md).
Binari Windows x64 e Linux x64 verificati; macOS Intel/Apple Silicon sono
predisposti nella CI GitHub Actions e non ancora dichiarati PASSED.
Il package usa directory native separate per piattaforma e architettura.
Le note 1.0.0 seguenti descrivono il nucleo precedente, tuttora verificato.
Lo script72 della versione precedente è stato dichiarato visivamente PASSED
dall'autore. La candidata1.1.0 richiede il proprio PASSED visivo.


La candidata include **pj_stats_rust 1.0.0**, compilata per **Windows x64,
CPython 3.10+ (abi3)**. Il modulo Pj resta alla versione **1.6.0**. Le funzioni
non richiedono NumPy, SciPy, pandas o altri package Python. Le build Linux/macOS
e le relative verifiche desktop restano da completare.

```python
import pj_stats_rust as rust
print(rust.__version__)
```

L'importazione usa la libreria fornita da Pj anche scegliendo l'interprete
System. Per richiedere una libreria installata separatamente, usare
`mzpjUseLibrary('pj_stats_rust', source='system')` prima dell'importazione.
Non si sostituisce una libreria già importata da un'altra sorgente.

Sono mantenuti nomi e chiavi dei risultati dello script71. I valori numerici
possono cambiare: corretti probabilità tramite beta incompleta, quantili t con
pochi gradi di libertà, Mann–Whitney con parimeriti/correzione di continuità,
trasformazioni F multivariate e ipotesi del gruppo aggiustata per la covariata
in MANCOVA. I nomi storici `*_robusta` restano per compatibilità: ANCOVA/MANCOVA
sono modelli lineari classici a pendenza comune, senza errori standard sandwich.

## Funzioni nuove

| Funzione | Uso |
| --- | --- |
| `correggi_p(p_values, metodo='holm')` | Correzione Holm, Bonferroni, BH/`fdr`, BY oppure `none`; conserva ordine e posizioni mancanti |
| `contingenza(conteggi)` | Chi-quadro Pearson senza Yates, Cramer V, frequenze attese, residui Pearson e diagnostica celle sparse |
| `statistiche_righe(colonne, statistica='media', min_validi=1)` | Calcolo nativo per riga su una lista di colonne; conserva tutte le righe |
| `bootstrap_statistica(dati, statistica='media', n_reps=10000, alpha=.05, seed=123456789)` | Bootstrap percentile per media o mediana, riproducibile con seed |

Per `statistiche_righe`, le statistiche sono `media`, `somma`, `min`, `max`,
`dev_std`, `n_validi`. Tutte le colonne devono avere lo stesso numero di righe.
`None` e NaN sono mancanti, gli infiniti generano errore. Se non si raggiunge
`min_validi`, restituisce `None`; la SD campionaria usa n−1 e richiede almeno due
valori. `n_validi` restituisce sempre il conteggio, compreso zero.

```python
colonne = [list(data['Sepal.Length']), list(data['Sepal.Width'])]
medie = rust.statistiche_righe(colonne, min_validi=2)
# Solo se si vuole usare l'Output verso il dataset corrente:
# data['rust_row_mean'] = medie
```

In Pj `data` è il dataset disponibile all'editor, in Pjp sono le variabili
selezionate. Queste funzioni non modificano automaticamente `data` o `dataext`.
Lo script72 dimostra i calcoli usando dati propri e aggiunge sei tabelle nei
Results, senza richiedere Service.

`correggi_p` restituisce `None` nelle posizioni mancanti; la molteplicità di
default conta i soli p-value validi, come nei riferimenti R verificati. Gli
altri valori devono essere tra 0 e 1. BH e BY controllano FDR con condizioni
diverse; [documentazione R](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/p.adjust.html).

`contingenza` richiede conteggi interi non negativi, tabella rettangolare con
margini positivi e totale massimo 2^53−1. È un test asintotico, non un test
esatto di Fisher: controllare `min_expected` e `cells_expected_lt5`. I residui
sono Pearson ordinari, non residui standardizzati aggiustati.

## Bootstrap e validazione

Anche `bootstrap_media(dati, n_reps=None, alpha=None, seed=123456789)` ora
accetta il seed e mantiene le vecchie chiavi della media. Servono almeno tre
osservazioni finite; repliche tra 2 e 1.000.000, alpha strettamente tra 0 e 1,
non oltre un miliardo di valori ricampionati per chiamata. La mediana ordina
ogni campione ed è più costosa della media. L'intervallo è percentile, non BCa.

Il generatore SplitMix64 con selezione degli indici senza bias sostituisce
quello precedente: stesso input e seed riproducono il risultato nella stessa
versione del backend, senza promettere gli stessi numeri delle vecchie build.
Non è un generatore crittografico. Bootstrap e nuove operazioni batch rilasciano
il lock Python durante il calcolo Rust, senza parallelizzare automaticamente
una singola chiamata.

Le funzioni univariate e i test appaiati richiedono valori numerici finiti;
i mancanti vanno rimossi esplicitamente rispettando le coppie. La matrice di
correlazione applica invece eliminazione pairwise, controllando prima le
lunghezze. I modelli con gruppi applicano casi completi listwise; ogni gruppo
deve avere almeno due osservazioni complete. Varianza residua nulla, gruppi
insufficienti e covarianza multivariata singolare generano un errore esplicito.

Pearson perfetto non produce più NaN nei limiti: con n=3 l'intervallo è [-1,1],
con n>3 e |r|=1 i limiti coincidono con r. Asimmetria/curtosi corrette non
definite restituiscono `None`. I casi estremi fuori dagli intervalli verificati
e i modelli mal condizionati non sono certificati dai test.

## Compilazione e prove

- `python pj_stats_rust/build_native.py --offline`: compila Windows x64, prova
  il binario candidato e conserva il precedente fuori dal progetto. Dopo va
  ricompilato il **JMO**, altrimenti jamovi usa ancora il binario precedente.
- `python -B pj_stats_rust/tests/test_native.py`: test senza dipendenze Python.
- `cargo test --lib --locked --manifest-path pj_stats_rust/Cargo.toml`: test Rust.
- Riferimenti riproducibili in `pj_stats_rust/tests/reference.R` e relativo JSON;
  jsonlite serve solo a serializzare i riferimenti durante i test con R.

Verifiche automatiche del 16 novembre2026: **17 gruppi Python PASSED** con
System e con l'eseguibile Embedded della portable28.17.2, **4 gruppi Rust PASSED**,
confronti con R4.6.2. Compresi script71/72 con chiamate alle tabelle catturate.
Il PASSED visivo dell'autore precedente riguardava il vecchio binario: per
questa candidata è ancora necessaria la prova in jamovi con entrambi i Python.
La [guida inglese](mzPj_rust.md) descrive il contratto completo delle API.


Verifica integrata aggiuntiva: servizio Pj R→Python su Iris, script71/72,
entrambi gli interpreti PASSED. Verificata corrispondenza hash di binario e
loader nel JMO finale. Resta la prova visiva/export di questa candidata.


Gli esempi 71 e 72 includono grafici statici Chart.js. Lo script 73 aggiunge un controllo Image nativo distinto dai due profili Svg. Pjscript/README.md distingue i tipi; le nuove prove LaTeX restano da completare.
