"""Interfaccia Streamlit per l'anonimizzatore di testi basato su Presidio."""

from __future__ import annotations

from typing import Dict

import streamlit as st

from anonimizzatore import PresidioAnonymizer


@st.cache_resource(show_spinner=True)
def get_anonymizer() -> PresidioAnonymizer:
    """Crea un'unica istanza condivisa di :class:`PresidioAnonymizer`."""

    return PresidioAnonymizer()


def _language_label(language_code: str) -> str:
    labels: Dict[str, str] = {
        "en": "Inglese",
        "it": "Italiano",
    }
    return labels.get(language_code, language_code)


def main() -> None:
    st.set_page_config(page_title="Anonimizzatore Presidio", page_icon="🛡️", layout="wide")

    st.title("Anonimizzatore di testo basato su Microsoft Presidio")
    st.write(
        "Questo strumento utilizza [Microsoft Presidio](https://github.com/microsoft/presidio) "
        "per individuare e sostituire automaticamente informazioni sensibili presenti in un testo."
    )

    try:
        anonymizer = get_anonymizer()
    except RuntimeError as exc:
        st.error(
            "Impossibile inizializzare il motore di anonimizzazione. "
            "Verifica di aver installato i modelli spaCy richiesti (ad esempio `en_core_web_sm`).\n\n"
            f"Dettagli: {exc}"
        )
        st.stop()

    if not anonymizer.languages:
        st.warning("Nessun modello linguistico disponibile. Installa almeno un modello spaCy supportato.")
        st.stop()

    default_replacements = anonymizer.default_entity_replacements()

    with st.form("anonymize_form", clear_on_submit=False):
        text_to_process = st.text_area(
            "Inserisci il testo da anonimizzare",
            height=250,
            placeholder="Scrivi o incolla qui il testo contenente dati sensibili...",
        )
        language = st.selectbox(
            "Lingua del testo",
            options=list(anonymizer.languages),
            format_func=_language_label,
        )

        with st.expander("Personalizza sostituzioni", expanded=False):
            default_value = st.text_input(
                "Valore di sostituzione generico",
                value=default_replacements.get("DEFAULT", "<ANONIMO>"),
                help="Usato per tutte le entità che non dispongono di una personalizzazione specifica.",
            )
            custom_replacements: Dict[str, str] = {}
            for entity, placeholder in default_replacements.items():
                if entity == "DEFAULT":
                    continue
                custom_replacements[entity] = st.text_input(
                    f"Sostituzione per {entity}",
                    value=placeholder,
                    key=f"replacement_{entity}",
                )

        submitted = st.form_submit_button("Analizza e anonimizza")

    if submitted:
        if not text_to_process.strip():
            st.warning("Inserisci del testo prima di procedere.")
            return

        with st.spinner("Analisi del testo in corso..."):
            recognizer_results = anonymizer.analyze_text(text=text_to_process, language=language)
            anonymization = anonymizer.anonymize_text(
                text=text_to_process,
                recognizer_results=recognizer_results,
                entity_replacements=custom_replacements,
                default_value=default_value,
            )

        st.session_state["analysis_results"] = PresidioAnonymizer.serialize_recognizer_results(recognizer_results)
        st.session_state["anonymized_text"] = anonymization.text
        st.session_state["anonymized_items"] = anonymization.items

    if "analysis_results" in st.session_state:
        analysis_results = st.session_state.get("analysis_results", [])
        anonymized_text = st.session_state.get("anonymized_text", "")
        anonymized_items = st.session_state.get("anonymized_items", [])

        st.subheader("Risultati dell'analisi")
        if analysis_results:
            st.dataframe(analysis_results, use_container_width=True)
        else:
            st.info("Nessuna entità sensibile rilevata nel testo fornito.")

        st.subheader("Testo anonimizzato")
        st.code(anonymized_text, language="markdown")

        if anonymized_items:
            st.subheader("Dettagli delle sostituzioni")
            st.json(anonymized_items)

        st.caption(
            "I risultati sono memorizzati localmente nella sessione corrente per consentire confronti rapidi."
        )


if __name__ == "__main__":
    main()
