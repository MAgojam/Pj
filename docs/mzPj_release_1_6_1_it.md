# Pj 1.6.1

Questa versione richiede **jamovi 28.18.0 o successiva**, inclusa, e mantiene
invariati API1, funzioni Python, dati esterni `dataext` e backend pj_stats_rust
1.1.0. I quattro binari Rust già verificati vengono riutilizzati senza
ricompilazione; il progetto Rust incompleto resta escluso da Git e dai JMO.

La desktop ufficiale 28.18 contiene la correzione del percorso di salvataggio
Svg e il tracciamento della lingua per i risultati Image. Queste correzioni
appartengono a jamovi e non vengono duplicate nel codice di Pj.

Windows e Linux sono compilati e verificati sui runtime ufficiali 28.18 con
Python Embedded e System. I due pacchetti macOS sono compilati separatamente
su Intel e Apple Silicon mediante GitHub Actions. Le verifiche automatiche
non equivalgono a una nuova accettazione visiva desktop.

I manuali delle librerie 1.6.0 in italiano e inglese restano validi: nessuna
funzione statistica o grafica è cambiata. La release 1.6.0 resta disponibile
per il precedente requisito. Il limite di ridimensionamento già confermato
in Rj resta separato; Rj non viene modificato.

La correzione delle proporzioni Office della portable privata non è presente
nella 28.18 ufficiale: non si dichiara risolto il caso di figure senza dimensioni
esplicite in DOCX/ODT. Vedi le [note inglesi](mzPj_release_1_6_1.md).
