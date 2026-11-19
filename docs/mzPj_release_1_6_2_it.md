# Pj 1.6.2 — bozza

Versione in preparazione, non pubblicata. Richiede jamovi 28.18.0 o successivo.
Al momento si prepara e verifica solo il candidato Windows.

- Contenitore accordion condiviso per Html: `line` predefinito con +/- SVG
  animato e linea estensibile; `bordered` con chevron SVG rotante e due bordi.
  D3, Chart.js, Plotly, HTML libero e tabelle HTML usano gli stessi argomenti.
  Svg, Image e Table nativi esclusi. [Guida](mzPj_accordions_it.md), esempio 75.
- Rimossa la personalizzazione locale dello script 04; aggiornati gli esempi
  grafici manuali per evitare contenitori esterni annidati.
- Scrollbar Ace con cursore visibile e contrastato, limitato all'editor.
- Spazio sopra la toolbar ridotto: Pj dimezza padding superiore e margine del
  layout precedente; Pjp dimezza il margine dopo l'area Variables.
- Esempi 04, 07-09, 12, 15 e 17 ampliati; istruzioni sugli input chiarite.
- Confronto degli script tramite una nuova analisi nello stesso documento,
  mantenendo i Results salvati negli esempi Data Library. Il file originale della
  libreria resta invariato e le modifiche si salvano come documento separato.
- Inclusa la correzione di stato della cattura Image: l'arrivo del PNG insieme a
  opzioni informative non deve rilanciare Python e ricreare le catture pendenti.

Lo script 04 usa attualmente Svg per evitare la cattura PNG asincrona. Il difetto
Image segnalato necessita di nuova prova desktop su questo candidato; i test
automatici non sostituiscono l'accettazione visiva del manutentore.

API1, minApp e binari Rust 1.1.0 invariati. Nessuna ricompilazione Rust necessaria.
Build degli altri sistemi, commit firmato, tag e pubblicazione ancora da eseguire.
