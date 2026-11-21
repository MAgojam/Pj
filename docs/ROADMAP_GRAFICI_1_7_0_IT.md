# Pj 1.7.0: grafici guidati avanzati

## Stato e versione

Pj 1.7.0: l’autore ha confermato PASSED Windows e Ubuntu 26.04 WSL2 con
entrambi i Python, inclusi gli script 78–80. Il commit di implementazione
5922eb3 è firmato. I manuali IT/EN e le relative edizioni Word/PDF sono stati
aggiornati; gli esempi pubblici sono stati ricontrollati sul runner corrente.
Le quattro build finali sono in preparazione; la release non è ancora pubblicata.
Il backend pj_stats_rust 1.1.0 resta invariato e non viene ricompilato.

## Funzione scelta e implementata

`mzpjShowInteraction` stima esplicitamente `Y ~ X * M + covariate numeriche`
per osservazioni indipendenti, con moderatore continuo oppure binario.
Una chiamata produce due pannelli coordinati: curve delle medie stimate e
pendenza condizionale di X con intervalli puntuali. Per il moderatore continuo
calcola le soglie Johnson–Neyman entro il range osservato; per il binario mostra
le due pendenze rispetto al gruppo di riferimento scelto. Restituisce anche il
report numerico e, per default, due tabelle native.

Covarianza HC3 con inferenza Normale asintotica oppure OLS con t di Student e
gradi di libertà residui. I renderer D3/Plotly ricevono lo stesso payload dal
calcolo Python, senza duplicare la statistica in JavaScript. Non è un modello
misto o per misure ripetute. Guida completa e limiti:
[mzPj_interaction_it.md](mzPj_interaction_it.md), esempio `79_interaction_model.py`.

Confronti indipendenti Statsmodels PASSED per coefficienti, covarianza,
previsioni, effetti, intervalli e soglie; prove browser offline nei due renderer
con Html/Svg/Image PASSED. Prova visiva dello script79 accettata su Windows e WSL2 nei due Python.
Nessuna nuova prova desktop macOS è dedotta dai test automatici.

## Ulteriori proposte da selezionare

- Diagnostica regressione pronta: residui versus stimati e Q–Q, con dati/modello
  e assunzioni espliciti. Esistono già script dimostrativi (25/59), ma non un
  helper dedicato: riutilizzare preparazione e validazioni invece di duplicarle.
- Concordanza Bland–Altman: confronto dei metodi e differenze rispetto alla media
  delle misure; definire trattamento di coppie/ripetizioni e limiti prima di
  implementare. Il helper D3 paired già presente non va ricreato con un altro nome.

## Regole di implementazione e verifica

Ricette e interazioni JavaScript nel progetto comune mzGraphics; preparazione
numerica nell’host, con riuso dei calcoli esistenti. Non ampliare il progetto
Rust in questa fase senza una necessità concordata. Conservare le firme e i
comportamenti già accettati. Le modalità descrittiva e basata su modello devono
essere distinguibili nelle opzioni, nei titoli e nella documentazione.

Coordinare colori, legenda e hover dei due pannelli. Verificare layout con pannelli
affiancati e, se utile, impilati. Ogni tipo deve esportare solo la figura; nessun
accordion o zoom Html nei risultati nativi. Preparazione Image silenziosa, errori
visibili e titoli conservati restano requisiti. Aggiungere esempi inglesi con dati
simulati e guide IT/EN. Confrontare i calcoli con riferimenti indipendenti, poi
verificare le quattro piattaforme. Windows e WSL2 sono stati accettati;
Rj resta rinviato al suo ultimo blocco.

## Riferimenti consultati

- https://www.statsmodels.org/stable/generated/statsmodels.graphics.factorplots.interaction_plot.html
- https://plotly.com/javascript/subplots/


Verifica finale Windows: 16 casi backend Html/Svg e 8 cicli Image Pj/Pjp con
entrambi i Python e renderer PASSED; una sola esecuzione Python, due tabelle e
titolo conservati. Installata preview 1.7.0 con backup e 69 file verificati;
caricamento a freddo UTF-8 PASSED. Prova visiva dello script79 PASSED su Windows e WSL2.
