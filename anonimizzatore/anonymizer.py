"""Utility di anonimizzazione basata su Microsoft Presidio."""

from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence

from presidio_analyzer import AnalyzerEngine, RecognizerRegistry, RecognizerResult
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine

# Mappa lingua -> modello spaCy raccomandato
_SPACY_MODELS: Mapping[str, str] = {
    "en": "en_core_web_sm",
    "it": "it_core_news_sm",
}


def _is_spacy_model_available(model_name: str) -> bool:
    """Restituisce True se il modello spaCy indicato è installato."""

    return importlib.util.find_spec(model_name) is not None


@dataclass
class AnonymizationResult:
    """Risultato dell'operazione di anonimizzazione."""

    text: str
    items: List[dict]


class PresidioAnonymizer:
    """Wrapper di alto livello attorno agli engine di Presidio."""

    def __init__(self) -> None:
        nlp_configuration = {"nlp_engine_name": "spacy", "models": []}
        available_languages: List[str] = []

        for language, model in _SPACY_MODELS.items():
            if _is_spacy_model_available(model):
                nlp_configuration["models"].append({"lang_code": language, "model_name": model})
                available_languages.append(language)

        if not nlp_configuration["models"]:
            supported = ", ".join(f"{lang} ({model})" for lang, model in _SPACY_MODELS.items())
            raise RuntimeError(
                "Nessun modello spaCy disponibile. Installa almeno uno dei modelli richiesti, ad esempio con\\n"
                f"  python -m spacy download en_core_web_sm\\n"
                f"Modelli supportati: {supported}"
            )

        nlp_engine = NlpEngineProvider(nlp_configuration=nlp_configuration).create_engine()
        registry = RecognizerRegistry()
        registry.load_predefined_recognizers(nlp_engine=nlp_engine)

        self._analyzer = AnalyzerEngine(nlp_engine=nlp_engine, registry=registry)
        self._anonymizer = AnonymizerEngine()
        self._languages = available_languages

    @property
    def languages(self) -> Sequence[str]:
        """Lingue supportate dai modelli spaCy disponibili."""

        return tuple(self._languages)

    @staticmethod
    def default_entity_replacements() -> Dict[str, str]:
        """Restituisce una mappatura di default tra entità e valore sostitutivo."""

        return {
            "DEFAULT": "<ANONIMO>",
            "PERSON": "<PERSONA>",
            "LOCATION": "<LOCALITÀ>",
            "EMAIL_ADDRESS": "<EMAIL>",
            "PHONE_NUMBER": "<TELEFONO>",
            "DATE_TIME": "<DATA>",
            "IBAN_CODE": "<IBAN>",
            "CREDIT_CARD": "<CARTA>",
            "NRP": "<DOCUMENTO>",
        }

    def analyze_text(self, text: str, language: str) -> List[RecognizerResult]:
        """Esegue l'analisi delle entità sensibili in *text* nella lingua indicata."""

        if not text.strip():
            return []

        if language not in self._languages:
            available = ", ".join(self._languages)
            raise ValueError(f"Lingua '{language}' non supportata. Lingue disponibili: {available}")

        return self._analyzer.analyze(text=text, language=language)

    def anonymize_text(
        self,
        text: str,
        recognizer_results: Iterable[RecognizerResult],
        entity_replacements: Optional[Mapping[str, str]] = None,
        default_value: Optional[str] = None,
    ) -> AnonymizationResult:
        """Anonimizza il testo originale usando i risultati di analisi forniti."""

        replacements = dict(self.default_entity_replacements())
        if entity_replacements:
            replacements.update({k: v for k, v in entity_replacements.items() if v})
        if default_value:
            replacements["DEFAULT"] = default_value

        operators: Dict[str, MutableMapping[str, str]] = {
            entity: {"type": "replace", "new_value": value} for entity, value in replacements.items()
        }

        anonymized_result = self._anonymizer.anonymize(
            text=text, analyzer_results=list(recognizer_results), operators=operators
        )

        items = [item.to_dict() for item in anonymized_result.items] if anonymized_result.items else []
        return AnonymizationResult(text=anonymized_result.text, items=items)

    @staticmethod
    def serialize_recognizer_results(results: Iterable[RecognizerResult]) -> List[dict]:
        """Serializza i risultati dell'analisi in un formato pronto per il frontend."""

        return [result.to_dict() for result in results]
