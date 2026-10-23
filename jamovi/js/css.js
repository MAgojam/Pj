
const css = `
#editor-box {
    margin-bottom: 6px ;
    flex-grow: 1 ;
    display: flex ;
    flex-direction: column ;
    position: relative ;
}

#editor {
    border: 1.5px solid rgba(62, 109, 169, 0.45) ;
    border-radius: 8px ;
    overflow: hidden ;
    flex-grow: 1 ;
    transition: border-color 0.2s ease, box-shadow 0.2s ease ;
}

#editor:focus-within {
    border-color: #3e6da9 ;
    box-shadow: 0 0 0 2px rgba(62, 109, 169, 0.15) ;
}

#toolbar {
    display: flex ;
    align-items: center ;
    justify-content: space-between ;
    flex-wrap: wrap ;
    gap: 6px 12px ;
    padding: 2px 0 8px ;
    position: relative ;
    z-index: 10 ;
}
#editor-heading, #editor-actions {
    display: flex ;
    align-items: center ;
    gap: 8px ;
    min-width: 0 ;
}
#editor-heading { flex: 1 1 130px ; }
#editor-heading > span:first-of-type { white-space: nowrap ; color: #3e6da9 ; }
#editor-filename {
    max-width: 180px ;
    overflow: hidden ;
    text-overflow: ellipsis ;
    white-space: nowrap ;
    color: #64748b ;
    font-size: 11px ;
}
#editor-actions { margin-left: auto ; }
#clear-script, #editor-actions button, #editor-replace button {
    font: inherit ;
    font-size: 12px ;
    color: #3e6da9 ;
    background: #fff ;
    border: 1px solid rgba(62, 109, 169, .4) ;
    border-radius: 4px ;
    padding: 5px 9px ;
    white-space: nowrap ;
    cursor: pointer ;
}
#clear-script:hover, #editor-actions button:hover, #editor-replace button:hover {
    background: rgba(62, 109, 169, .07) ;
}
#clear-script {
    flex-shrink: 0 ;
    font-size: 11px ;
    padding: 4px 6px ;
    background: transparent ;
    border-color: rgba(62, 109, 169, .25) ;
}
#clear-script:hover { background: rgba(62, 109, 169, .07) ; }
#clear-script:focus-visible, #editor-actions button:focus-visible { outline: 2px solid #3e6da9 ; outline-offset: 2px ; }
#editor-message, #editor-replace {
    margin-bottom: 8px ;
    padding: 8px ;
    background: rgba(62, 109, 169, .07) ;
    color: #334155 ;
    font-size: 12px ;
}
#editor-replace:not([hidden]) { display: flex ; align-items: center ; gap: 8px ; flex-wrap: wrap ; }
#editor-replace > span { flex: 1 ; }
#config { position: relative ; }

#info {
    display: flex ;
    position: absolute ;
    bottom: 4px ;
    right: 16px ;
    color: #333333 ;
}

#run, #config {
    width: 21px ;
    height: 21px ;
    border-radius: 2px ;
    background-size: auto 80% ;
    background-position: center ;
    background-repeat: no-repeat ;
}

#run:hover, #config:hover {
    background-color: rgba(62, 109, 169, 0.12) ;
}

#menu {
    opacity: 0 ;
    pointer-events: none ;
    transform: translateX(110%) ;
    transition:
        transform 0.28s ease-out,
        opacity 0.20s ease-out ;

    display: grid ;
    position: absolute ;
    top: 24px ;
    right: 0px ;
    width: 260px ;
    box-sizing: border-box ;
    color: #333333 ;
    background-color: #ffffff ;
    border: 1.5px solid #3e6da9 ;
    box-shadow: 0 4px 14px rgba(62, 109, 169, 0.22) ;
    border-radius: 8px ;
    z-index: 20 ;
    cursor: move ;

    padding: 14px ;
    align-items: center ;
    grid-column-gap: 6px ;
    grid-row-gap: 12px ;
}

#menu.visible {
    opacity: 1 ;
    pointer-events: auto ;
    transform: translateX(0) ;
}

#menu > label {
    grid-column: 1 ;
    max-width: 90px ;
    overflow: hidden ;
    text-overflow: ellipsis ;
    white-space: nowrap ;
    font-size: 12px ;
    font-weight: 500 ;
    color: #555555 ;
}

#output-label, #output {
    grid-row: 1 ;
}

#python-label, #python-version {
    grid-row: 4 ;
}

#output, #python-version {
    grid-column: 2 / span 2 ;
    width: 100% ;
    max-width: 100% ;
    box-sizing: border-box ;
    overflow: hidden ;
    text-overflow: ellipsis ;
    padding: 5px 8px ;
    border: 1px solid #ccc ;
    border-radius: 4px ;
    font-size: 12px ;
    background: #ffffff ;
    cursor: pointer ;
    transition: border-color 0.2s ease, box-shadow 0.2s ease ;
}

#output:focus, #python-version:focus {
    outline: none ;
    border-color: #3e6da9 ;
    box-shadow: 0 0 0 2px rgba(62, 109, 169, 0.20) ;
}

#code-label, #r-version {
    grid-row: 3 ;
}

#menu > #code-label {
    grid-column: 1 / -1 ;
    max-width: none ;
    display: flex ;
    align-items: center ;
    gap: 8px ;
    overflow: visible ;
}

#pj-module-version {
    color: #64748b ;
    background: #f0f5fa ;
    border-radius: 4px ;
    padding: 1px 6px ;
    font-size: 11px ;
    font-weight: 400 ;
}

/* =====================================================
   VARIABLE SUPPLIER (Pjp) - le variabili qui selezionate
   diventano il dizionario "data" nel codice Python.
   Classi applicate da main.js::styleVariableSupplier().
   ===================================================== */

.pj-vs-source {
    border-radius: 8px ;
    border: 2px solid #3e6da9 ;
    background-color: #ffffff ;
    box-shadow: none ;
}

.pj-vs-transfer-btn {
    border-radius: 6px ;
    border: 1px solid rgba(62, 109, 169, 0.45) ;
    background: #f5f8fc ;
    box-shadow: 0 1px 3px rgba(62, 109, 169, 0.15) ;
    transition: all 0.2s ease-in-out ;
}

.pj-vs-transfer-btn:hover {
    background: #eef4fb ;
    border-color: #3e6da9 ;
}

.pj-vs-target {
    border-radius: 8px ;
    transition: background-color 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease ;
}

/* Vuoto: bordo tratteggiato, invita a trascinare le variabili */
.pj-vs-target.pj-vs-empty {
    border: 2px dashed rgba(62, 109, 169, 0.55) ;
    background: rgba(62, 109, 169, 0.06) ;
}

/* Compilato: bordo pieno, sfondo e ombra piu' marcati */
.pj-vs-target.pj-vs-filled {
    border: 2px solid #3e6da9 ;
    background: rgba(62, 109, 169, 0.14) ;
    box-shadow: 0 2px 6px rgba(62, 109, 169, 0.20) ;
}

/* Ghost-label (placeholder nativo jamovi) quando il box e' vuoto */
.pj-vs-target.pj-vs-empty .column-ghost-label {
    color: rgba(62, 109, 169, 0.7) ;
    font-weight: 400 ;
    font-style: italic ;
}

/* Freccia a doppio chevron al posto di quella di default */
.jmv-toolbar .jmv-toolbar-button.jmv-variable-transfer > .jmv-toolbar-button-icon {
    width: 22px ;
    height: 22px ;
    background-position: center ;
    background-repeat: no-repeat ;
    opacity: 0.65 ;
    transition: opacity 0.2s ease, transform 0.1s ease ;
}

.pj-vs-transfer-btn:hover > .jmv-toolbar-button-icon {
    opacity: 1 ;
}

.pj-vs-transfer-btn:active > .jmv-toolbar-button-icon {
    transform: scale(0.85) ;
}

.jmv-toolbar.arrow-right .jmv-toolbar-button.jmv-variable-transfer > .jmv-toolbar-button-icon {
    background-image: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%20fill='none'%3E%3Cpath%20d='M11%206.3%2016.7%2012%2011%2017.7'%20stroke='%233E6DA9'%20stroke-width='3.75'%20stroke-linecap='round'%20stroke-linejoin='round'/%3E%3Cpath%20d='M5.3%206.3%2011%2012%205.3%2017.7'%20stroke='%23ECA038'%20stroke-width='3.75'%20stroke-linecap='round'%20stroke-linejoin='round'/%3E%3C/svg%3E") ;
}

.jmv-toolbar.arrow-left .jmv-toolbar-button.jmv-variable-transfer > .jmv-toolbar-button-icon {
    background-image: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%20fill='none'%3E%3Cpath%20d='M11%206.3%205.3%2012%2011%2017.7'%20stroke='%23ECA038'%20stroke-width='3.75'%20stroke-linecap='round'%20stroke-linejoin='round'/%3E%3Cpath%20d='M18.7%206.3%2013%2012%2018.7%2017.7'%20stroke='%233E6DA9'%20stroke-width='3.75'%20stroke-linecap='round'%20stroke-linejoin='round'/%3E%3C/svg%3E") ;
}

/* =====================================================
   ACCORDION "Variables" (Pjp) - CustomControl al posto del
   CollapseBox nativo, stesso stile "Info & Notes" gia' in uso
   in Metafora (icona +/- animata via SVG, titolo con separatori).
   Classi applicate da main.js::pjpAccordion_creating/applyAccordionState().
   ===================================================== */

.pj-accordion-header {
    font-size: 12px ;
    font-weight: 500 ;
    border: none ;
    background-color: transparent ;
    padding: 4px 0 ;
    color: #3e6da9 ;
    width: 100% ;
    text-align: left ;
    cursor: pointer ;
    display: flex ;
    align-items: center ;
    transition: all 0.3s ease ;
    border-radius: 0 ;
}

.pj-accordion-header:hover {
    color: #1565c0 ;
    background-color: transparent ;
}

.pj-accordion-header.pj-accordion-expanded {
    font-weight: 700 ;
}

.pj-accordion-icon-container {
    width: 18px ;
    height: 18px ;
    display: flex ;
    align-items: center ;
    justify-content: center ;
    margin-right: 6px ;
    flex-shrink: 0 ;
    border-right: 1px solid rgba(62, 109, 169, 0.50) ;
    padding-right: 6px ;
}

.pj-plus-minus-icon {
    width: 12px ;
    height: 12px ;
}

.pj-plus-minus-icon .horizontal,
.pj-plus-minus-icon .vertical {
    transition: transform 0.3s ease, opacity 0.3s ease ;
    transform-origin: center ;
}

.pj-accordion-header.pj-accordion-expanded .pj-plus-minus-icon .vertical {
    transform: rotate(90deg) ;
    opacity: 0 ;
}

.pj-accordion-title {
    margin-left: 0px ;
    display: flex ;
    align-items: center ;
    flex-grow: 1 ;
}

.pj-accordion-title::before,
.pj-accordion-title::after {
    content: '' ;
    height: 1px ;
    background-color: rgba(62, 109, 169, 0.50) ;
    transition: all 0.3s ease ;
}

.pj-accordion-title::before {
    flex-basis: 30px ;
    margin: 0 8px ;
}

.pj-accordion-title::after {
    flex-basis: 30px ;
    margin-left: 8px ;
}

.pj-accordion-header.pj-accordion-expanded .pj-accordion-title::before,
.pj-accordion-header.pj-accordion-expanded .pj-accordion-title::after {
    height: 2px ;
    background-color: rgba(62, 109, 169, 0.70) ;
}

.pj-accordion-header.pj-accordion-expanded .pj-accordion-title::after {
    flex-grow: 1 ;
}

.pj-accordion-content {
    max-height: 0 ;
    overflow: hidden ;
    transition: max-height 0.3s ease-out ;
}

.pj-accordion-content.pj-accordion-expanded {
    max-height: 2000px ;
    transition: max-height 0.4s ease-in ;
}

/* =====================================================
   FILE SELECTOR (Pj/Pjp) - "Service script (.py)".
   Bottone e nome del file affiancati sulla stessa riga
   invece che impilati; stile coerente col resto del modulo.
   ===================================================== */

.mzpj-service-origin { display: none !important ; }
.silky-options-header.mzpj-editor-header { justify-content: flex-start ; gap: 8px ; }
.mzpj-editor-header > .silky-options-title { flex: 0 0 auto ; white-space: nowrap ; }
.silky-options-title.mzpj-icon-title { display: inline-flex ; align-items: center ; }
.silky-options-title > .mzpj-title-icon {
    display: inline-flex ;
    align-items: center ;
    justify-content: center ;
    flex: 0 0 48px ;
    box-sizing: border-box ;
    width: 48px ;
    height: 48px ;
    padding: 4px ;
    background: #ffffff ;
    border: 1px solid rgba(62, 109, 169, .20) ;
    border-radius: 10px ;
    margin-inline-end: 8px ;
    vertical-align: middle ;
    pointer-events: none ;
}
.mzpj-title-icon > svg { display: block ; width: 38px ; height: 38px ; }
.mzpj-editor-header > .silky-sp-back-button { flex-shrink: 0 ; margin-inline-start: auto ; }
.mzpj-service-header {
    display: flex ;
    align-items: center ;
    justify-content: flex-start ;
    flex: 0 1 auto ;
    min-width: 0 ;
    gap: 6px ;
    margin-inline-start: 4px ;
}
.mzpj-service-header > label {
    flex: 0 0 auto ;
    font-size: 11px ;
    color: #64748b ;
    margin: 0 !important ;
}
.mzpj-service-header .jmv-file-selector {
    flex: 0 1 auto ;
    min-width: 0 ;
    max-width: 100% ;
    gap: 6px ;
}
.mzpj-service-header .jmv-file-selector-button {
    margin: 0 !important ;
    padding: 4px 9px ;
    font-size: 11px ;
}
.mzpj-service-header .jmv-file-selector-list { flex: 0 1 auto ; }
.mzpj-service-header .jmv-file-selector-list:empty { display: none !important ; }
.mzpj-service-header .jmv-file-selector-item {
    padding: 3px 6px 3px 9px ;
    font-size: 11px ;
    max-width: 100% ;
}
.mzpj-service-header .jmv-file-selector-name { max-width: 160px ; }
@media (max-width: 500px) {
    .mzpj-service-header > label { display: none !important ; }
    .mzpj-service-header .jmv-file-selector-name { max-width: 110px ; }
}

.jmv-file-selector {
    display: flex !important ;
    flex-direction: row !important ;
    flex-wrap: nowrap !important ;
    align-items: center !important ;
    justify-content: flex-start !important ;
    gap: 10px ;
}

.jmv-file-selector.busy {
    opacity: 0.6 ;
    pointer-events: none ;
}

.jmv-file-selector-button {
    flex-shrink: 0 !important ;
    padding: 6px 18px ;
    border: 1px solid #3e6da9 ;
    border-radius: 5px ;
    background: #f5f8fc ;
    color: #3e6da9 ;
    font-size: 12.5px ;
    font-weight: 500 ;
    line-height: 1.4 ;
    cursor: pointer ;
    transition: background 0.2s ease, box-shadow 0.2s ease ;
}

.jmv-file-selector-button:hover {
    background: #eef4fb ;
    box-shadow: 0 1px 3px rgba(62, 109, 169, 0.25) ;
}

.jmv-file-selector-button:disabled {
    opacity: 0.5 ;
    cursor: default ;
}

.jmv-file-selector-list {
    display: flex !important ;
    flex-direction: row !important ;
    flex-wrap: nowrap !important ;
    align-items: center !important ;
    gap: 6px ;
    min-width: 0 ;
    overflow: hidden ;
}

.jmv-file-selector-item {
    display: flex ;
    align-items: center ;
    gap: 6px ;
    min-width: 0 ;
    padding: 6px 8px 6px 12px ;
    background: rgba(62, 109, 169, 0.10) ;
    border: 1px solid rgba(62, 109, 169, 0.35) ;
    border-radius: 14px ;
    font-size: 12.5px ;
    color: #333333 ;
}

.jmv-file-selector-item.unavailable {
    border-color: rgba(200, 60, 60, 0.5) ;
    background: rgba(200, 60, 60, 0.08) ;
}

.jmv-file-selector-name {
    white-space: nowrap ;
    overflow: hidden ;
    text-overflow: ellipsis ;
    min-width: 0 ;
    max-width: 160px ;
    line-height: 1.6 ;
    display: inline-block ;
}

.jmv-file-selector-remove {
    border: none ;
    background: transparent ;
    color: #3e6da9 ;
    cursor: pointer ;
    font-size: 13px ;
    line-height: 1 ;
    padding: 1px 3px ;
    border-radius: 50% ;
}

.jmv-file-selector-remove:hover {
    color: #ffffff ;
    background: #c0392b ;
}

#figure-size {
    grid-row: 2;
    grid-column: 1 / span 2 ;
    margin: 10px 0px;
}

#figure-size-title {
    margin-bottom: 8px;
    font-size: 11px ;
    font-weight: 700 ;
    text-transform: uppercase ;
    letter-spacing: 0.4px ;
    color: #3e6da9 ;
    padding-bottom: 4px ;
    border-bottom: 1px solid rgba(62, 109, 169, 0.35) ;
}

#figure-size-row {
    display: flex ;
    align-items: center ;
    gap: 6px ;
    cursor: auto ;
}

#figure-size-row label {
    font-size: 12px ;
    font-weight: 500 ;
    color: #555555 ;
    white-space: nowrap ;
}

#figure-size input {
    width: 55px;
    padding: 4px 6px ;
    border: 1px solid #ccc ;
    border-radius: 4px ;
    font-size: 12px ;
    transition: border-color 0.2s ease, box-shadow 0.2s ease ;
}

#figure-size input:focus {
    outline: none ;
    border-color: #3e6da9 ;
    box-shadow: 0 0 0 2px rgba(62, 109, 169, 0.20) ;
}

#run {
    background-image: url('data:image/svg+xml;base64,PHN2ZyBpZD0ic3ZnMiIgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGhlaWdodD0iMjQiIHdpZHRoPSIyNCIgdmVyc2lvbj0iMS4xIiB4bWxuczpjYz0iaHR0cDovL2NyZWF0aXZlY29tbW9ucy5vcmcvbnMjIiB4bWxuczpkYz0iaHR0cDovL3B1cmwub3JnL2RjL2VsZW1lbnRzLzEuMS8iIHZpZXdCb3g9IjAgMCAyNCAyNCI+PG1ldGFkYXRhIGlkPSJtZXRhZGF0YTEwIj48cmRmOlJERj48Y2M6V29yayByZGY6YWJvdXQ9IiI+PGRjOmZvcm1hdD5pbWFnZS9zdmcreG1sPC9kYzpmb3JtYXQ+PGRjOnR5cGUgcmRmOnJlc291cmNlPSJodHRwOi8vcHVybC5vcmcvZGMvZGNtaXR5cGUvU3RpbGxJbWFnZSIvPjxkYzp0aXRsZS8+PC9jYzpXb3JrPjwvcmRmOlJERj48L21ldGFkYXRhPjxwYXRoIGlkPSJwYXRoNCIgZmlsbD0iIzJhOGEyYSIgZD0ibTMgMjJ2LTIwbDE4IDEwLTE4IDEweiIvPjwvc3ZnPg==');
}

#config {
    background-image: url('data:image/svg+xml;base64,PHN2ZyBpZD0ic3ZnMiIgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGhlaWdodD0iMjQiIHdpZHRoPSIyNCIgdmVyc2lvbj0iMS4xIiB4bWxuczpjYz0iaHR0cDovL2NyZWF0aXZlY29tbW9ucy5vcmcvbnMjIiB4bWxuczpkYz0iaHR0cDovL3B1cmwub3JnL2RjL2VsZW1lbnRzLzEuMS8iIHZpZXdCb3g9IjAgMCAyNCAyNCI+PG1ldGFkYXRhIGlkPSJtZXRhZGF0YTEwIj48cmRmOlJERj48Y2M6V29yayByZGY6YWJvdXQ9IiI+PGRjOmZvcm1hdD5pbWFnZS9zdmcreG1sPC9kYzpmb3JtYXQ+PGRjOnR5cGUgcmRmOnJlc291cmNlPSJodHRwOi8vcHVybC5vcmcvZGMvZGNtaXR5cGUvU3RpbGxJbWFnZSIvPjxkYzp0aXRsZS8+PC9jYzpXb3JrPjwvcmRmOlJERj48L21ldGFkYXRhPjxwYXRoIGlkPSJwYXRoNDEzOCIgZD0ibTEwLjk0OSAwLjgxNDQ1Yy0wLjE4NCAwLjU1MTk1LTAuMzQ1IDEuMS0wLjU5MiAxLjU4Mi0wLjMzIDAuNjQ3LTAuODc3OSAxLjI0MTgtMS42NzkzIDEuNTc0M2EwLjgxNDggMC44MTQ4IDAgMCAxIC0wLjAwMTk1IDAgMC44MTQ4IDAuODE0OCAwIDAgMSAtMC4yOTY4OCAwLjA2MjVjLTAuNzAxNCAwLjIxNDItMS40MDAzIDAuMjExMS0yLjAwNTkgMC4wMTU2LTAuNTE1OC0wLjE2NjQtMS4wMTg1LTAuNDM5NC0xLjU0MS0wLjcwMTFsLTEuNDg0NCAxLjQ4NDRjMC4yNjA3IDAuNTIwMiAwLjUzMjYgMS4wMjEzIDAuNjk5MyAxLjUzNyAwLjIyMzcgMC42OTIyIDAuMjU2OCAxLjUwMzgtMC4wNzYyIDIuMzA2Ny0wLjMzMjQgMC44MDE3LTAuOTI3MiAxLjM1MDItMS41NzQyIDEuNjgxMi0wLjQ4MjEgMC4yNDctMS4wMjk5IDAuNDA4LTEuNTgyIDAuNTkydjIuMTAxNmMwLjU1MTMxIDAuMTgzMzEgMS4wOTggMC4zNDMxOSAxLjU4MDEgMC41ODk4NCAwLjY0NzI1IDAuMzMxMTYgMS4yNDM1IDAuODc5OTMgMS41NzYyIDEuNjgxNmEwLjgxNDggMC44MTQ4IDAgMCAxIDAgMC4wMDJjMC4zMzQ4MiAwLjgwOTg4IDAuMjk3OCAxLjYyNDUgMC4wNzIyNjYgMi4zMTg0LTAuMTY3NjggMC41MTU4Ny0wLjQzNzcxIDEuMDEwOC0wLjY5NTMxIDEuNTIzNGwxLjQ4NDQgMS40ODYzYzAuNTE5MDgtMC4yNjAyMSAxLjAxOTItMC41MzI0MSAxLjUzNTItMC42OTkyMiAwLjYwNjEtMC4xOTU5NCAxLjMwNjYtMC4yMDAwNSAyLjAwOTggMC4wMTM2N2EwLjgxNDggMC44MTQ4IDAgMCAxIDAuMjk4ODMgMC4wNjI1IDAuODE0OCAwLjgxNDggMCAwIDEgMC4wMDE5NSAwYzAuODAwOSAwLjMzMTcxIDEuMzQ4NyAwLjkyNTU2IDEuNjc5NyAxLjU3MjMgMC4yNDY2NyAwLjQ4MTk4IDAuNDA3NzcgMS4wMzA2IDAuNTkxOCAxLjU4NGgyLjEwMTZjMC4xODM5NC0wLjU1MjQzIDAuMzQ0MTUtMS4wOTk2IDAuNTkxOC0xLjU4MiAwLjMzMjM3LTAuNjQ3NDcgMC44ODQzMS0xLjI0MzUgMS42ODc1LTEuNTc4MWEwLjgxNDggMC44MTQ4IDAgMCAxIDAuMDAyIDAgMC44MTQ4IDAuODE0OCAwIDAgMSAwLjI5ODgzIC0wLjA2MjVjMC42OTczNi0wLjIxMTcxIDEuMzkzMy0wLjIwNzIxIDEuOTk2MS0wLjAxMTcyIDAuNTEzOTkgMC4xNjY3IDEuMDE2NSAwLjQzOTQ1IDEuNTM5MSAwLjcwMTE3bDEuNDg0NC0xLjQ4NDRjLTAuMjYwNC0wLjUxOTQ0LTAuNTMyNjItMS4wMTkyLTAuNjk5MjItMS41MzUyLTAuMjIzNjYtMC42OTI2My0wLjI1NjM4LTEuNTA1MyAwLjA3NjE3LTIuMzA4NiAwLjMzMjY2LTAuODAyMzEgMC45Mjg1OS0xLjM1MDIgMS41NzYyLTEuNjgxNiAwLjQ4MjUtMC4yNDY5MiAxLjAzMDItMC40MDgxNCAxLjU4Mi0wLjU5MTh2LTIuMTAxNmMtMC41NTctMC4xODQtMS4xMDktMC4zNDYtMS41OS0wLjU5My0wLjY0Ni0wLjMzMS0xLjIzNi0wLjg3OTEtMS41NjctMS42NzczYTAuODE0OCAwLjgxNDggMCAwIDEgMCAtMC4wMDE5NSAwLjgxNDggMC44MTQ4IDAgMCAxIC0wLjA2MjUgLTAuMjk2ODhjLTAuMjEzLTAuNzAxNy0wLjIxLTEuNDAwMi0wLjAxNS0yLjAwNTkgMC4xNjctMC41MTU3IDAuNDQtMS4wMTkgMC43MDEtMS41NDFsLTEuNDg0LTEuNDg0M2MtMC41MTkgMC4yNTk5LTEuMDE5IDAuNTMyMy0xLjUzNSAwLjY5OTItMC42MDYgMC4xOTYxLTEuMzA2IDAuMjAwMS0yLjAxLTAuMDEzN2EwLjgxNDggMC44MTQ4IDAgMCAxIC0wLjI5ODgzIC0wLjA2MjUgMC44MTQ4IDAuODE0OCAwIDAgMSAtMC4wMDIgMGMtMC44LTAuMzMxNi0xLjM0OC0wLjkyNC0xLjY3OS0xLjU3MDMtMC4yNDctMC40ODE5LTAuNDA4LTEuMDMxNy0wLjU5Mi0xLjU4NmgtMi4xMDE2em0xLjA1MSA2LjM3MWMyLjY0OTQgMCA0LjgxNDUgMi4xNjUxIDQuODE0NSA0LjgxNDVzLTIuMTY1MSA0LjgxNDUtNC44MTQ1IDQuODE0NS00LjgxNDUtMi4xNjUtNC44MTQ1LTQuODE0YzAtMi42NDk0IDIuMTY1MS00LjgxNDUgNC44MTQ1LTQuODE0NXoiIHRyYW5zZm9ybT0ibWF0cml4KDEuMDI2OSAwIDAgMS4wMjc1IC0uMzIyOTEgLS4zMzczMikiIHN0cm9rZT0iI2JlYmVkNiIgZmlsbD0iI2QzZDZlMyIvPjwvc3ZnPg==');

    margin-right: 3px;
}

.ace_editor.ace_autocomplete .ace_completion-highlight {
    color: inherit ;
    text-shadow: none ;
}

.ace_editor.ace_autocomplete .ace_line {
    line-height: 20px ;
}

.ace_icon_data,
.ace_icon_func,
.ace_icon_var,
.ace_icon_ns {
    display: inline-block ;
    width: 24px ;
    background-repeat: no-repeat ;
    background-size: 12px ;
    background-position: center ;
}

.ace_icon_data {
    background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABYAAAAWCAYAAADEtGw7AAAAQklEQVR42mOImrXnPy0wA4jYeu8jVfGowZgG0yTy2jqn/8cFLly4SpYcyMwhajBIETXxEA6K0TAeDePRMMZjMC0wAFMtrQuuiigOAAAAAElFTkSuQmCC');
}

.ace_icon_func {
    background-image: url('data:image/svg+xml;base64,PHN2ZyBpZD0ic3ZnMiIgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGhlaWdodD0iMjQiIHdpZHRoPSIyNCIgdmVyc2lvbj0iMS4xIiB4bWxuczpjYz0iaHR0cDovL2NyZWF0aXZlY29tbW9ucy5vcmcvbnMjIiB4bWxuczpkYz0iaHR0cDovL3B1cmwub3JnL2RjL2VsZW1lbnRzLzEuMS8iIHZpZXdCb3g9IjAgMCAyNCAyNCI+PG1ldGFkYXRhIGlkPSJtZXRhZGF0YTEwIj48cmRmOlJERj48Y2M6V29yayByZGY6YWJvdXQ9IiI+PGRjOmZvcm1hdD5pbWFnZS9zdmcreG1sPC9kYzpmb3JtYXQ+PGRjOnR5cGUgcmRmOnJlc291cmNlPSJodHRwOi8vcHVybC5vcmcvZGMvZGNtaXR5cGUvU3RpbGxJbWFnZSIvPjxkYzp0aXRsZS8+PC9jYzpXb3JrPjwvcmRmOlJERj48L21ldGFkYXRhPjxyZWN0IGlkPSJyZWN0NDE1NiIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIgdHJhbnNmb3JtPSJtYXRyaXgoLjY4ODgxIC43MjQ5NCAtLjcxNjU4IC42OTc1MSAwIDApIiBoZWlnaHQ9IjIxLjYxMSIgd2lkdGg9IjExLjIxNSIgc3Ryb2tlPSIjM2M2Y2E1IiB5PSItMTEuMjQiIHg9IjExLjM2MiIgc3Ryb2tlLXdpZHRoPSIuNzk0NjEiIGZpbGw9IiM3NzlmY2UiLz48L3N2Zz4=');
}

.ace_icon_ns {
    background-image: url('data:image/svg+xml;base64,PHN2ZyBpZD0ic3ZnMiIgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGhlaWdodD0iMjQiIHdpZHRoPSIyNCIgdmVyc2lvbj0iMS4xIiB4bWxuczpjYz0iaHR0cDovL2NyZWF0aXZlY29tbW9ucy5vcmcvbnMjIiB4bWxuczpkYz0iaHR0cDovL3B1cmwub3JnL2RjL2VsZW1lbnRzLzEuMS8iIHZpZXdCb3g9IjAgMCAyNCAyNCI+PG1ldGFkYXRhIGlkPSJtZXRhZGF0YTEwIj48cmRmOlJERj48Y2M6V29yayByZGY6YWJvdXQ9IiI+PGRjOmZvcm1hdD5pbWFnZS9zdmcreG1sPC9kYzpmb3JtYXQ+PGRjOnR5cGUgcmRmOnJlc291cmNlPSJodHRwOi8vcHVybC5vcmcvZGMvZGNtaXR5cGUvU3RpbGxJbWFnZSIvPjxkYzp0aXRsZS8+PC9jYzpXb3JrPjwvcmRmOlJERj48L21ldGFkYXRhPjxwYXRoIGlkPSJwYXRoNDE1NCIgZD0ibTExLjk5OCAwLjYwOTM4LTEwLjQ2MyA1LjcwN3YxMS40OTRsMTAuNDY1IDUuNTg1IDEwLjQ2NS01LjU4NHYtMTEuNDNsLTEwLjQ2Ny01Ljc3MTZ6bS0wLjAwMzkgMS4xMzY3YTAuNTM0NCAwLjUzNDQgMCAwIDEgMC4yNTggMC4wNjY0bDcuOTE2IDQuMzY1MmEwLjUzNDQgMC41MzQ0IDAgMCAxIC0wLjAwNTkgMC45Mzk0NWwtNy45MDQgNC4yMTY4YTAuNTM0NCAwLjUzNDQgMCAwIDEgLTAuNTA4IC0wLjAwMmwtNy44NzMtNC4yOTI5YTAuNTM0NCAwLjUzNDQgMCAwIDEgMCAtMC45Mzc1bDcuODYxLTQuMjg5MWEwLjUzNDQgMC41MzQ0IDAgMCAxIDAuMjU1ODYgLTAuMDY2NDA2em05LjAxMTcgNi4wNDg4YTAuNTM0NCAwLjUzNDQgMCAwIDEgMC41MjkzIDAuNTM1MTZ2OC42MDE2YTAuNTM0NCAwLjUzNDQgMCAwIDEgLTAuMjgzMiAwLjQ3MDdsLTggNC4yNjc2YTAuNTM0NCAwLjUzNDQgMCAwIDEgLTAuNzg3MTEgLTAuNDcwN3YtOC41OTk2YTAuNTM0NCAwLjUzNDQgMCAwIDEgMC4yODMyIC0wLjQ3MDdsOC00LjI2OTVhMC41MzQ0IDAuNTM0NCAwIDAgMSAwLjI1NzgxIC0wLjA2NDQ1M3oiIHRyYW5zZm9ybT0ibWF0cml4KDEuMDU3MyAwIDAgMS4wNTI3IC0uNjg4MjAgLS42MjY0NikiIGZpbGw9IiM4OTViYTgiLz48L3N2Zz4=');
}

`;

let node = document.createElement('style');
node.innerHTML = css;
document.body.appendChild(node);

module.exports = undefined;
