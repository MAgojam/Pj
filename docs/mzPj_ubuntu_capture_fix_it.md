# Ubuntu 26.04: selettore script e acquisizione delle immagini

19 novembre 2026. Correzione sul ramo fix/linux-native-image-capture.
Rj e' sospeso per richiesta del manutentore. Questa verifica riguarda Pj/Pjp.

## 1. Cartella iniziale del selettore

Il Load dell'editor usa un input file HTML e FileReader; non imposta alcuna
cartella iniziale. Nel runtime del repository (R, Python e JavaScript) non e'
presente /home/magojam/A_Lavoro/Pj/pjscript come percorso predefinito.
Il messaggio osservato appartiene al selettore nativo GTK della desktop.
La scomparsa dopo aver scelto una cartella valida e dopo il riavvio e' coerente
con una posizione ricordata dal profilo del selettore/applicazione. Non prova
quale file di preferenze la contenga: senza il profilo del dual boot non si puo'
attribuirla con certezza a GTK, al portale o al profilo Chromium.

Non cancellare il profilo jamovi e non inserire un altro percorso fisso in Pj.
Se ricompare, confermare OK, scegliere Home o una cartella esistente e poi lo
script. Nel caso riportato questa operazione ha gia' ripristinato i caricamenti.

## 2. Rigenerazione delle PNG

La .load di Pj classificava la risposta graphicCapture come operazione di sola
visualizzazione soltanto con graphicCapture ed editorState tra le differenze.
Se la stessa richiesta riportava dataextInfo aggiornato, ricadeva nel normale
Run: lo script ricreava Html temporanei, token e PNG, generando il lampeggiamento.
Il test aggiunto riproduce il difetto sul pacchetto 1.6.1 precedente alla patch.

La correzione ammette anche i campi informativi/sincronizzazione dataextInfo e
createdColumns. Un payload ancora presente viene trattato come risposta grafica,
conservando i controlli su token e PNG. Un Run esplicito, una modifica al codice,
all'interprete o ai dati non vengono assorbiti da questa classificazione.
Non cambia alcun calcolo statistico, renderer D3 o libreria Rust.

## 3. Esempi aggiornati

- 58: chiarita la distinzione tra Svg nativo e controlli Html.
- 59: rimossi i riferimenti alla preview e al pacchetto stabile 1.3.0; Plotly e'
  gia' distribuito in Pj. Messaggio di importazione coerente con i due Python.
- 60: la protezione delle dimensioni e' gia' disponibile, non piu' una preview.
- 73: riferimento corrente e nota finale valida per il GRAPHIC_RESULT_TYPE scelto.
- README: superata la sospensione generale dei test Ubuntu legata a jamovi 28.17;
  usare la 28.18 ufficiale e verificare separatamente i formati di esportazione.

Restano corretti i requisiti reali di pandas/matplotlib in 06 e 11, le richieste
di selezionare dati e la necessita' del Service 13 per l'esempio 14. Non eliminare
questi controlli. Tutti i 72 script presenti sono analizzabili come UTF-8.

## 4. Verifiche eseguite e limiti

Windows: test di regressione Pj/Pjp con Python embedded/System; primi esempi
01-22 (13 come Service di 14) e Plotly 59. I requisiti opzionali sono distinti
da un difetto del modulo. Test integrato 73 con iframe separati: 17 tabelle,
due profili acquisiti e il controllo PNG originale; una sola esecuzione Python.

Linux: compilazione da clone locale del commit pubblico con patch applicata,
backend Flatpak 28.18.0.0 sotto Ubuntu 26.04 WSL2, entrambi i Python e Pj/Pjp.
Stesso giro browser/backend del 73 superato, con una PNG per richiesta e stato
informativo sincronizzato. Rendering JS eseguito in Chromium headless Windows
collegato al backend Linux; NON e' una verifica visiva del dual boot.
Verificata la decodifica anche con png fornito dal modulo jmv della Flatpak;
il JMO di prova contiene inoltre questa dipendenza dichiarata negli Imports.
Prodotto un PDF con le tre Image native per ogni combinazione.

La descrizione Flatpak puo' mostrare 28.7: il file /app/lib/jamovi/version e il
commit Flatpak installato identificano effettivamente la 28.18.0.0.
Non confondere metadati descrittivi e versione eseguita.

## 5. Applicazione alla prova da utente

Il pacchetto di prova contiene JMO Linux e patch dei sorgenti. Per il clone
GitHub gia' presente, da una cartella di lavoro senza modifiche in conflitto:

```sh
cd /percorso/del/clone/Pj
git apply --check /percorso/pj_capture_fix.patch
git apply /percorso/pj_capture_fix.patch
```

Ricompilare con la stessa procedura jmvtools gia' utilizzata su quel sistema.
In alternativa installare il JMO Linux di prova. Salvare i documenti e riavviare
jamovi per caricare il modulo aggiornato. Ripetere 73: devono stabilizzarsi due
profili e l'icona PNG, senza messaggi Preparing persistenti. Provare anche Save
OMV ed esportazione desiderata; il collaudo automatico non certifica tutti gli
export desktop. Non occorre ricompilare pj_stats_rust.

La versione di questo candidato resta 1.6.1; questa non e' una nuova release
pubblica. Il clone del repository pubblico richiede la patch finche' la
correzione non viene integrata e pubblicata.
