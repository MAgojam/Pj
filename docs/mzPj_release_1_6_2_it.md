# Pj 1.6.2

Richiede jamovi 28.18.0 o successivo. Aggiornamenti:

- Dimensioni per singola figura: `mzpjShowImage(..., width=, height=)` e nuovo `mzpjShowSvg(markup, width=, height=)`. Valori locali per il solo risultato; omissione usa il popup globale. Una sola misura mantiene il rapporto PNG/SVG. Byte PNG originali invariati. Esempio76 e guide italiano/inglese.
- Accordion Html condivisi `line` e `bordered`, animati, per contenuti/grafici/tabelle Html. Svg/Image/Table nativi esclusi. Gli Svg nativi non hanno zoom Html o observer che riscrivono le dimensioni gestite da jamovi. Esempio75 per il confronto.
- Scrollbar editor visibili e trascinabili, spazio prima della toolbar ridotto, tipografia popup coerente tra Windows e Ubuntu.
- Esempi didattici ampliati e istruzioni Data Library chiarite: i file contengono già analisi salvate. Aggiungere una nuova analisi Pj/Pjp nello stesso documento per il confronto e salvare le modifiche fuori dalla libreria; gli OMV distribuiti restano invariati.
- Protezione dello stato di cattura Image: la conferma PNG insieme ad aggiornamenti informativi non deve rieseguire Python e ricreare catture pendenti.

Il manutentore ha comunicato PASSED visivi Windows e Ubuntu26.04 dualboot/WSL2 per aggiornamenti editor, accordion e risultati grafici. I test automatici su dimensioni individuali, due Python, stato cattura e API sono distinti. I manifest dei pacchetti finali registrano i controlli per SO; nessuna accettazione visiva desktop macOS è dedotta da Actions.

API1, minApp28.18.0 e quattro binari pj_stats_rust1.1.0 invariati. Nessuna ricompilazione Rust. I sorgenti del progetto Rust indipendente non sono distribuiti nel modulo/JMO.

Il gancio nativo è in basso a sinistra nel jamovi Ubuntu provato, anche con Rj ufficiale e MetaJam: questa versione non ne corregge la posizione. Dimensioni individuali e popup globale offrono controlli alternativi. Export Svg dipendente dal jamovi ospitante; il modulo non distribuisce patch private della portable.

I manuali librerie1.6.0 restano validi per le funzioni statistiche invariate. Manuali helper Python e guide dimensioni italiano/inglese aggiornati accompagnano questa versione.
