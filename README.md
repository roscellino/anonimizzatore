# Anonimizzatore di testi basato su Microsoft Presidio

Applicazione web con interfaccia grafica (Streamlit) per l'anonimizzazione di testi tramite [Microsoft Presidio](https://github.com/microsoft/presidio). Permette di rilevare informazioni personali (PII) e di sostituirle in modo automatico con placeholder personalizzabili.

## Funzionalità principali

- Riconoscimento di entità sensibili tramite Presidio Analyzer.
- Sostituzione personalizzata delle entità individuate (es. PERSON, EMAIL_ADDRESS, PHONE_NUMBER).
- Supporto multi-lingua basato sui modelli spaCy disponibili (inglese e italiano, se installati).
- Interfaccia grafica intuitiva per inserire testo, lanciare l'analisi e consultare i risultati.
- Visualizzazione dettagliata delle entità riconosciute e delle sostituzioni effettuate.

## Requisiti

- Python 3.9 o superiore.
- Dipendenze Python elencate in `requirements.txt`.
- Modelli spaCy per le lingue da supportare (almeno `en_core_web_sm`).

## Installazione

1. Clona il repository e installa le dipendenze:

   ```bash
   pip install -r requirements.txt
   ```

2. Installa i modelli spaCy necessari (almeno quello inglese):

   ```bash
   python -m spacy download en_core_web_sm
   # facoltativo, per l'italiano
   python -m spacy download it_core_news_sm
   ```

## Avvio dell'applicazione

Esegui il server Streamlit indicando il file principale:

```bash
streamlit run streamlit_app.py
```

L'interfaccia sarà disponibile all'indirizzo `http://localhost:8501`.

## Utilizzo

1. Incolla o digita il testo contenente informazioni sensibili.
2. Seleziona la lingua corrispondente al testo.
3. (Opzionale) Personalizza i placeholder per le diverse entità.
4. Premi **Analizza e anonimizza** per avviare il processo.
5. Consulta la tabella con le entità rilevate, il testo anonimizzato e i dettagli delle sostituzioni.

I dati non vengono memorizzati permanentemente: i risultati restano disponibili solo durante la sessione corrente del browser.

## Struttura del progetto

- `streamlit_app.py`: interfaccia grafica e logica di orchestrazione.
- `anonimizzatore/anonymizer.py`: wrapper riutilizzabile attorno agli engine di Presidio.
- `requirements.txt`: elenco delle dipendenze necessarie per eseguire l'applicazione.

## Sviluppo

Per contribuire o estendere l'applicazione:

- Aggiungi nuove entità personalizzate modificando `default_entity_replacements` in `anonymizer.py`.
- Integra nuovi modelli spaCy aggiungendo la relativa voce al dizionario `_SPACY_MODELS`.
- Esegui test statici con:

  ```bash
  python -m compileall anonimizzatore streamlit_app.py
  ```

## Licenza

Questo progetto è rilasciato con licenza MIT.
