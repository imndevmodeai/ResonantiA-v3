import datetime
import logging
import uuid
from enum import Enum
from typing import Dict, List, Union

# Define a custom exception for analysis errors
class AnalysisError(Exception):
    """
    Custom exception for errors occurring during query complexity analysis.
    """
    pass

# Enum for Routing Protocols
class RoutingProtocol(Enum):
    CRCS = "CRCS"  # Cognitive Resource Conservation Strategy (for simple queries)
    RISE = "RISE"  # Resonating Insight Synthesis Engine (for complex queries)
    UNKNOWN = "UNKNOWN" # Fallback for unclassifiable cases

# Data structure for the analysis result
class QueryAnalysisResult:
    """
    Encapsulates the outcome of a query complexity analysis.
    """
    def __init__(self,
                 query_id: str,
                 original_query: str,
                 complexity_score: float,
                 complexity_classification: str, # e.g., "Simple", "Complex"
                 recommended_protocol: RoutingProtocol,
                 confidence_score: float, # 0.0 to 1.0
                 analysis_timestamp: str): # ISO 8601 format

        if not isinstance(query_id, str) or not query_id:
            raise ValueError("query_id must be a non-empty string.")
        if not isinstance(original_query, str) or not original_query:
            raise ValueError("original_query must be a non-empty string.")
        if not isinstance(complexity_score, (int, float)) or not (0.0 <= complexity_score <= 1.0):
            raise ValueError("complexity_score must be a float between 0.0 and 1.0.")
        if not isinstance(complexity_classification, str) or not complexity_classification:
            raise ValueError("complexity_classification must be a non-empty string.")
        if not isinstance(recommended_protocol, RoutingProtocol):
            raise ValueError("recommended_protocol must be an instance of RoutingProtocol Enum.")
        if not isinstance(confidence_score, (int, float)) or not (0.0 <= confidence_score <= 1.0):
            raise ValueError("confidence_score must be a float between 0.0 and 1.0.")
        if not isinstance(analysis_timestamp, str) or not analysis_timestamp:
            raise ValueError("analysis_timestamp must be a non-empty string.")

        self.query_id: str = query_id
        self.original_query: str = original_query
        self.complexity_score: float = complexity_score
        self.complexity_classification: str = complexity_classification
        self.recommended_protocol: RoutingProtocol = recommended_protocol
        self.confidence_score: float = confidence_score
        self.analysis_timestamp: str = analysis_timestamp

    def to_dict(self) -> Dict[str, Union[str, float]]:
        """Converts the result object to a dictionary for logging/serialization."""
        return {
            "query_id": self.query_id,
            "original_query": self.original_query,
            "complexity_score": self.complexity_score,
            "complexity_classification": self.complexity_classification,
            "recommended_protocol": self.recommended_protocol.value,
            "confidence_score": self.confidence_score,
            "analysis_timestamp": self.analysis_timestamp
        }

    def __repr__(self) -> str:
        return (f"QueryAnalysisResult(query_id='{self.query_id}', "
                f"classification='{self.complexity_classification}', "
                f"protocol='{self.recommended_protocol.value}', "
                f"score={self.complexity_score:.2f}, "
                f"confidence={self.confidence_score:.2f})")


class QueryComplexityAnalyzerService:
    """
    A lightweight utility for analyzing query text complexity and suggesting optimal routing.
    """

    def __init__(self, config: Dict[str, Union[float, str, Dict[str, float]]]):
        """
        Initializes the QueryComplexityAnalyzerService with configuration.

        Args:
            config (Dict): Configuration dictionary containing thresholds, model paths, etc.
                           Expected keys:
                               - 'complexity_threshold_simple_to_complex': float (e.g., 0.5)
                               - 'nlp_model_path': str (optional, default: 'default_nlp_model')
                               - 'feature_weights': Dict[str, float] (optional, default: {'word_count': 0.1, 'unique_words': 0.2, 'avg_word_len': 0.3})
                               - 'default_confidence': float (e.g., 0.7)
        """
        if not isinstance(config, dict):
            raise ValueError("Config must be a dictionary.")

        self._config: Dict[str, Union[float, str, Dict[str, float]]] = config
        self._logger: logging.Logger = self._get_logger()

        self._nlp_model = self._load_nlp_model(config.get('nlp_model_path', 'default_nlp_model'))
        self._complexity_threshold: float = config.get('complexity_threshold_simple_to_complex', 0.5)
        self._feature_weights: Dict[str, float] = config.get(
            'feature_weights',
            {'word_count': 0.1, 'unique_words': 0.2, 'avg_word_len': 0.3, 'sentence_count': 0.4}
        )
        self._default_confidence: float = config.get('default_confidence', 0.7)

        if not isinstance(self._complexity_threshold, (int, float)) or not (0.0 <= self._complexity_threshold <= 1.0):
            raise ValueError("complexity_threshold_simple_to_complex must be a float between 0.0 and 1.0.")
        if not isinstance(self._default_confidence, (int, float)) or not (0.0 <= self._default_confidence <= 1.0):
            raise ValueError("default_confidence must be a float between 0.0 and 1.0.")
        if not isinstance(self._feature_weights, dict):
            raise ValueError("feature_weights must be a dictionary.")
        if not all(isinstance(k, str) and isinstance(v, (int, float)) for k, v in self._feature_weights.items()):
            raise ValueError("All feature weights must be string keys and float values.")

        self._logger.info("QueryComplexityAnalyzerService initialized with config: %s", config)

    def _get_logger(self) -> logging.Logger:
        """
        Initializes and returns a logger instance.
        This method can be extended to configure logging levels, handlers, etc.
        """
        logger = logging.getLogger(self.__class__.__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def _load_nlp_model(self, model_path: str) -> object:
        """
        Placeholder for loading an NLP model.
        In a real-world scenario, this would load a pre-trained model (e.g., spaCy, Hugging Face).

        Args:
            model_path (str): The path or identifier for the NLP model.

        Returns:
            object: A mock NLP model object.
        """
        self._logger.info("Simulating NLP model loading from: %s", model_path)
        # In a real implementation, this would load a model, e.g.:
        # import spacy
        # try:
        #     nlp = spacy.load(model_path)
        # except OSError:
        #     self._logger.error("NLP model '%s' not found. Please install it (e.g., python -m spacy download en_core_web_sm).", model_path)
        #     raise AnalysisError(f"NLP model '{model_path}' not found.")
        # return nlp
        class MockNLPModel:
            def __init__(self, path: str):
                self.path = path
            def process(self, text: str) -> Dict[str, Union[int, float]]:
                # Simple mock processing
                words = text.split()
                sentences = text.count('.') + text.count('?') + text.count('!')
                return {
                    'word_count': len(words),
                    'unique_words': len(set(words)),
                    'avg_word_len': sum(len(word) for word in words) / len(words) if words else 0,
                    'sentence_count': sentences if sentences > 0 else 1 # Ensure at least 1 sentence for short queries
                }
        return MockNLPModel(model_path)

    def _extract_features(self, query_text: str) -> Dict[str, Union[int, float]]:
        """
        Extracts relevant linguistic features from the query text using the loaded NLP model.

        Args:
            query_text (str): The raw textual content of the query.

        Returns:
            Dict[str, Union[int, float]]: A dictionary of extracted features.
        """
        try:
            # In a real implementation, self._nlp_model would be used to parse the text
            # and extract features like POS tags, named entities, dependency parse info, etc.
            # For this placeholder, we use the mock model's process method.
            features = self._nlp_model.process(query_text)
            self._logger.debug("Extracted features for query: %s", features)
            return features
        except Exception as e:
            self._logger.error("Error extracting features for query: '%s' - %s", query_text, e)
            raise AnalysisError(f"Failed to extract features: {e}") from e

    def _calculate_complexity_score(self, features: Dict[str, Union[int, float]]) -> float:
        """
        Calculates a complexity score based on extracted features and configured weights.
        The score is normalized to be between 0.0 and 1.0.

        Args:
            features (Dict[str, Union[int, float]]): A dictionary of extracted features.

        Returns:
            float: A normalized complexity score (0.0 to 1.0).
        """
        raw_score = 0.0
        total_weight = 0.0

        for feature_name, weight in self._feature_weights.items():
            feature_value = features.get(feature_name, 0)
            raw_score += feature_value * weight
            total_weight += weight

        # Simple normalization (can be improved with min/max scaling or sigmoid)
        if total_weight > 0:
            # For demonstration, let's assume a max possible raw score for normalization.
            # In a real system, this would be determined empirically or by model design.
            # A simple heuristic: assume max feature value for word_count/sentence_count is 100, avg_word_len is 10.
            # This is a very basic normalization. A more robust system would use a trained model or statistical bounds.
            max_possible_raw_score = (
                self._feature_weights.get('word_count', 0) * 100 +
                self._feature_weights.get('unique_words', 0) * 50 +
                self._feature_weights.get('avg_word_len', 0) * 10 +
                self._feature_weights.get('sentence_count', 0) * 10
            )
            if max_possible_raw_score > 0:
                normalized_score = min(1.0, raw_score / max_possible_raw_score)
            else:
                normalized_score = 0.0 # No features or weights, assume minimal complexity
        else:
            normalized_score = 0.0 # No weights configured, assume minimal complexity

        self._logger.debug("Calculated complexity score: %.4f (raw: %.4f)", normalized_score, raw_score)
        return normalized_score

    def _classify_complexity(self, complexity_score: float) -> str:
        """
        Classifies the query complexity based on the score and a predefined threshold.

        Args:
            complexity_score (float): The calculated complexity score.

        Returns:
            str: The classification ("Simple" or "Complex").
        """
        if complexity_score >= self._complexity_threshold:
            classification = "Complex"
        else:
            classification = "Simple"
        self._logger.debug("Classified complexity as: %s (score: %.4f, threshold: %.4f)",
                           classification, complexity_score, self._complexity_threshold)
        return classification

    def _recommend_protocol(self, classification: str) -> RoutingProtocol:
        """
        Recommends a routing protocol based on the complexity classification.

        Args:
            classification (str): The complexity classification ("Simple" or "Complex").

        Returns:
            RoutingProtocol: The recommended routing protocol.
        """
        if classification == "Simple":
            protocol = RoutingProtocol.CRCS
        elif classification == "Complex":
            protocol = RoutingProtocol.RISE
        else:
            protocol = RoutingProtocol.UNKNOWN
            self._logger.warning("Unknown classification '%s', defaulting to UNKNOWN protocol.", classification)
        self._logger.debug("Recommended protocol: %s for classification: %s", protocol.value, classification)
        return protocol

    def analyze_query(self, query_id: str, query_text: str) -> QueryAnalysisResult:
        """
        Analyzes the complexity of the given query text and recommends a routing protocol.

        Args:
            query_id (str): A unique identifier for the query