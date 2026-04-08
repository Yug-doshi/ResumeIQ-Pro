"""
Emotion / Confidence Detector — Audio + Text NLC Analysis

Detects emotional states during interview practice:
  - Confident 😎
  - Nervous 😟
  - Hesitant 🤔
  - Neutral 😐

Tech:
  - Audio features (MFCC-like spectral analysis via numpy/scipy)
  - Text sentiment analysis using NLC keyword patterns
  - Ensemble scoring with audio + text signals

Input: audio features (from frontend Web Audio API) + answer text
Output: emotion label, confidence scores, detailed analysis
"""

import numpy as np
import re
from typing import Dict, List, Optional
from sklearn.ensemble import RandomForestClassifier


# =====================================================================
#  EMOTION LABELS & PATTERNS
# =====================================================================

EMOTIONS = {
    "confident": {
        "label": "Confident 😎",
        "color": "#10b981",
        "text_markers": [
            "definitely", "absolutely", "clearly", "certainly", "i believe",
            "i am confident", "i excelled", "i successfully", "i led",
            "i designed", "i implemented", "my approach", "i achieved",
            "proven track record", "expertise", "i'm skilled", "proficient",
            "effectively", "efficiently", "strong background"
        ],
        "negative_markers": []
    },
    "nervous": {
        "label": "Nervous 😟",
        "color": "#ef4444",
        "text_markers": [
            "um", "uh", "err", "hmm", "i think maybe", "i'm not sure",
            "i guess", "sort of", "kind of", "probably", "i don't know",
            "nervous", "sorry", "i can't remember", "let me think",
            "it's hard", "struggling", "worried", "anxious"
        ],
        "negative_markers": ["confident", "definitely", "absolutely"]
    },
    "hesitant": {
        "label": "Hesitant 🤔",
        "color": "#f59e0b",
        "text_markers": [
            "well", "actually", "perhaps", "might", "could be",
            "not entirely sure", "i would say", "possibly", "it depends",
            "on one hand", "however", "but", "although", "some experience",
            "partially", "to some extent", "i think", "maybe"
        ],
        "negative_markers": ["definitely", "absolutely", "certainly"]
    },
    "neutral": {
        "label": "Neutral 😐",
        "color": "#6b7280",
        "text_markers": [],
        "negative_markers": []
    }
}

# Audio feature thresholds (from MFCC-like features)
# These simulate realistic ranges for speech pattern classification
AUDIO_PROFILES = {
    "confident": {
        "pitch_range": (100, 250),    # moderate, steady pitch
        "energy_min": 0.6,            # strong energy
        "speaking_rate": (120, 180),   # steady pace
        "pause_ratio_max": 0.15,      # few pauses
        "pitch_variance_max": 30,     # steady pitch
    },
    "nervous": {
        "pitch_range": (200, 400),    # high pitch
        "energy_min": 0.3,            # variable energy
        "speaking_rate": (180, 300),   # fast/rushing
        "pause_ratio_max": 0.1,       # rushing through
        "pitch_variance_min": 40,     # unstable pitch
    },
    "hesitant": {
        "pitch_range": (80, 200),     # lower pitch
        "energy_min": 0.2,            # low energy
        "speaking_rate": (60, 120),   # slow pace
        "pause_ratio_min": 0.25,      # many pauses
        "pitch_variance_max": 20,     # flat/monotone
    }
}


class EmotionDetector:
    """
    Classifies speaker emotion using audio features + text NLC analysis.
    """

    def __init__(self):
        self.classifier = RandomForestClassifier(
            n_estimators=100, max_depth=8, random_state=42
        )
        self._train_classifier()

    def _train_classifier(self):
        """Train on synthetic audio feature data."""
        np.random.seed(42)
        n_per_class = 200

        # Feature order: [pitch_mean, pitch_var, energy, speaking_rate, pause_ratio, spectral_centroid]

        # Confident: steady pitch, high energy, moderate speed, few pauses
        X_conf = np.column_stack([
            np.random.normal(170, 30, n_per_class),    # pitch_mean
            np.random.normal(15, 5, n_per_class),      # pitch_var (low)
            np.random.normal(0.75, 0.1, n_per_class),  # energy (high)
            np.random.normal(150, 20, n_per_class),    # speaking_rate
            np.random.normal(0.08, 0.03, n_per_class), # pause_ratio (low)
            np.random.normal(2500, 300, n_per_class),  # spectral_centroid
        ])

        # Nervous: high pitch, variable, fast speech
        X_nerv = np.column_stack([
            np.random.normal(280, 50, n_per_class),
            np.random.normal(55, 15, n_per_class),     # high variance
            np.random.normal(0.5, 0.15, n_per_class),
            np.random.normal(210, 40, n_per_class),    # fast
            np.random.normal(0.05, 0.02, n_per_class), # rushing
            np.random.normal(3200, 400, n_per_class),
        ])

        # Hesitant: low pitch, low energy, slow, many pauses
        X_hesi = np.column_stack([
            np.random.normal(130, 25, n_per_class),
            np.random.normal(10, 4, n_per_class),
            np.random.normal(0.35, 0.1, n_per_class),  # low energy
            np.random.normal(90, 20, n_per_class),     # slow
            np.random.normal(0.35, 0.08, n_per_class), # many pauses
            np.random.normal(1800, 300, n_per_class),
        ])

        # Neutral: average everything
        X_neut = np.column_stack([
            np.random.normal(180, 30, n_per_class),
            np.random.normal(25, 8, n_per_class),
            np.random.normal(0.55, 0.1, n_per_class),
            np.random.normal(140, 25, n_per_class),
            np.random.normal(0.15, 0.05, n_per_class),
            np.random.normal(2200, 300, n_per_class),
        ])

        X = np.vstack([X_conf, X_nerv, X_hesi, X_neut])
        y = np.array([0]*n_per_class + [1]*n_per_class + [2]*n_per_class + [3]*n_per_class)

        # Shuffle
        idx = np.random.permutation(len(y))
        X, y = X[idx], y[idx]

        # Clip to reasonable ranges
        X = np.clip(X, 0, None)

        self.classifier.fit(X, y)
        self.label_map = {0: "confident", 1: "nervous", 2: "hesitant", 3: "neutral"}

    def analyze_emotion(
        self,
        text: str = "",
        audio_features: Optional[Dict] = None
    ) -> Dict:
        """
        Analyze emotion from text and/or audio features.

        Args:
            text: The spoken/typed text answer
            audio_features: Dict with keys:
                - pitch_mean, pitch_variance, energy, speaking_rate,
                  pause_ratio, spectral_centroid
                (from frontend Web Audio API analysis)

        Returns:
            {
                "primary_emotion": str,
                "emotion_label": str,
                "emotion_emoji": str,
                "confidence_scores": {"confident": float, "nervous": float, ...},
                "analysis": {
                    "text_signals": [...],
                    "audio_signals": [...],
                    "overall_assessment": str
                },
                "tips": [str]
            }
        """
        text_scores = self._analyze_text(text)
        audio_scores = self._analyze_audio(audio_features) if audio_features else None

        # ── Blend scores ──
        if audio_scores and text:
            # Both available — audio weighted more
            final_scores = {}
            for emotion in ["confident", "nervous", "hesitant", "neutral"]:
                final_scores[emotion] = (
                    audio_scores.get(emotion, 0) * 0.55 +
                    text_scores.get(emotion, 0) * 0.45
                )
        elif audio_scores:
            final_scores = audio_scores
        else:
            final_scores = text_scores

        # Normalize
        total = sum(final_scores.values())
        if total > 0:
            final_scores = {k: round(v / total, 3) for k, v in final_scores.items()}

        # Primary emotion
        primary = max(final_scores, key=final_scores.get)
        emotion_info = EMOTIONS[primary]

        # ── Build text signals ──
        text_signals = self._get_text_signals(text)

        # ── Build audio signals ──
        audio_signals = self._get_audio_signals(audio_features) if audio_features else []

        # ── Overall assessment ──
        assessment = self._build_assessment(primary, final_scores)

        # ── Tips ──
        tips = self._generate_tips(primary, final_scores, text_signals)

        return {
            "primary_emotion": primary,
            "emotion_label": emotion_info["label"],
            "emotion_color": emotion_info["color"],
            "confidence_scores": {
                "confident": round(final_scores.get("confident", 0) * 100, 1),
                "nervous": round(final_scores.get("nervous", 0) * 100, 1),
                "hesitant": round(final_scores.get("hesitant", 0) * 100, 1),
                "neutral": round(final_scores.get("neutral", 0) * 100, 1),
            },
            "analysis": {
                "text_signals": text_signals,
                "audio_signals": audio_signals,
                "overall_assessment": assessment,
            },
            "tips": tips,
        }

    # ─────────────── TEXT ANALYSIS (NLC) ───────────────

    def _analyze_text(self, text: str) -> Dict[str, float]:
        if not text:
            return {"confident": 0.25, "nervous": 0.25, "hesitant": 0.25, "neutral": 0.25}

        text_lower = text.lower()
        scores = {}

        for emotion, info in EMOTIONS.items():
            markers = info["text_markers"]
            negative = info["negative_markers"]

            if not markers:
                scores[emotion] = 0.15
                continue

            # Count matches
            match_count = sum(1 for m in markers if m in text_lower)
            neg_count = sum(1 for m in negative if m in text_lower)

            # Normalize by number of markers
            raw_score = match_count / max(1, len(markers))
            penalty = neg_count * 0.1

            scores[emotion] = max(0, min(1.0, raw_score * 3 - penalty))

        # Filler word detection boosts nervous/hesitant
        fillers = len(re.findall(r'\b(um|uh|err|hmm|like|you know)\b', text_lower))
        if fillers > 3:
            scores["nervous"] += 0.3
            scores["hesitant"] += 0.2

        # Word count — very short answers suggest hesitance
        word_count = len(text.split())
        if word_count < 15:
            scores["hesitant"] += 0.2
        elif word_count > 80:
            scores["confident"] += 0.15

        # Ensure neutral has a baseline
        if max(scores.values()) < 0.3:
            scores["neutral"] = 0.5

        return scores

    # ─────────────── AUDIO ANALYSIS ───────────────

    def _analyze_audio(self, features: Dict) -> Dict[str, float]:
        """Classify using trained RandomForest on audio features."""
        try:
            feature_vector = np.array([[
                features.get("pitch_mean", 170),
                features.get("pitch_variance", 20),
                features.get("energy", 0.5),
                features.get("speaking_rate", 140),
                features.get("pause_ratio", 0.15),
                features.get("spectral_centroid", 2200),
            ]])

            probabilities = self.classifier.predict_proba(feature_vector)[0]

            scores = {}
            for idx, label in self.label_map.items():
                scores[label] = float(probabilities[idx])

            return scores
        except Exception:
            return {"confident": 0.25, "nervous": 0.25, "hesitant": 0.25, "neutral": 0.25}

    # ─────────────── SIGNAL EXTRACTION ───────────────

    def _get_text_signals(self, text: str) -> List[Dict]:
        if not text:
            return []
        text_lower = text.lower()
        signals = []

        # Check for filler words
        fillers = re.findall(r'\b(um|uh|err|hmm|like|you know)\b', text_lower)
        if fillers:
            signals.append({
                "signal": f"Filler words detected: {len(fillers)}x",
                "type": "warning",
                "suggestion": "Practice reducing filler words for clearer communication"
            })

        # Check for confident language
        confident_words = [w for w in EMOTIONS["confident"]["text_markers"] if w in text_lower]
        if confident_words:
            signals.append({
                "signal": f"Confident language: {', '.join(confident_words[:3])}",
                "type": "positive",
                "suggestion": "Great use of confident language!"
            })

        # Check for hedging
        hedges = [w for w in ["maybe", "perhaps", "possibly", "i think", "sort of", "kind of"] if w in text_lower]
        if hedges:
            signals.append({
                "signal": f"Hedging language: {', '.join(hedges[:3])}",
                "type": "warning",
                "suggestion": "Replace hedging words with definitive statements"
            })

        # Sentence length analysis
        sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
        if sentences:
            avg_length = np.mean([len(s.split()) for s in sentences])
            if avg_length < 5:
                signals.append({
                    "signal": "Very short sentences",
                    "type": "info",
                    "suggestion": "Elaborate more on your answers with specific examples"
                })

        return signals

    def _get_audio_signals(self, features: Dict) -> List[Dict]:
        signals = []

        energy = features.get("energy", 0.5)
        if energy > 0.7:
            signals.append({"signal": "Strong vocal energy", "type": "positive"})
        elif energy < 0.3:
            signals.append({"signal": "Low vocal energy — speak up", "type": "warning"})

        rate = features.get("speaking_rate", 140)
        if rate > 200:
            signals.append({"signal": "Speaking too fast — slow down", "type": "warning"})
        elif rate < 80:
            signals.append({"signal": "Very slow pace — may indicate uncertainty", "type": "info"})

        pause_ratio = features.get("pause_ratio", 0.15)
        if pause_ratio > 0.3:
            signals.append({"signal": "Frequent pauses detected", "type": "warning"})

        pitch_var = features.get("pitch_variance", 20)
        if pitch_var > 50:
            signals.append({"signal": "Voice pitch is unstable", "type": "warning"})
        elif pitch_var < 10:
            signals.append({"signal": "Monotone delivery — add vocal variety", "type": "info"})

        return signals

    def _build_assessment(self, primary: str, scores: Dict) -> str:
        assessments = {
            "confident": "You're coming across as confident and self-assured. Your communication style conveys competence. Keep it up!",
            "nervous": "Signs of nervousness detected. This is normal in interviews — try taking deep breaths and speaking more slowly. Remember: preparation builds confidence.",
            "hesitant": "Your responses show some hesitation. Try to be more direct and decisive in your answers. Use specific examples to back up your statements.",
            "neutral": "Your delivery is calm and measured. While this is professional, try adding more enthusiasm and energy to stand out.",
        }
        return assessments.get(primary, assessments["neutral"])

    def _generate_tips(self, primary: str, scores: Dict, text_signals: List) -> List[str]:
        tips = []

        if primary == "nervous":
            tips.extend([
                "🧘 Take 3 deep breaths before answering each question",
                "⏱️ Pause for 2-3 seconds before responding — this looks thoughtful, not slow",
                "📝 Practice your STAR responses (Situation, Task, Action, Result)",
                "🎯 Focus on specific achievements rather than general statements",
            ])
        elif primary == "hesitant":
            tips.extend([
                "💪 Replace 'I think' with 'I know' or 'In my experience'",
                "🎯 Lead with your strongest point first",
                "📊 Back up statements with specific numbers and examples",
                "⚡ Practice delivering your key points in under 60 seconds",
            ])
        elif primary == "confident":
            tips.extend([
                "✅ Great confidence level — maintain this energy!",
                "🤝 Balance confidence with humility — mention team contributions too",
                "📖 Add more storytelling to make your answers memorable",
            ])
        else:
            tips.extend([
                "🔥 Add more energy and enthusiasm to your voice",
                "📊 Include specific numbers and metrics in your answers",
                "💡 Share personal anecdotes that show your problem-solving skills",
            ])

        return tips[:5]


# =====================================================================
#  QUICK API (singleton)
# =====================================================================
_detector_instance = None

def analyze_speech_emotion(text: str = "", audio_features: Optional[Dict] = None) -> Dict:
    """Quick-use function for emotion detection."""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = EmotionDetector()
    return _detector_instance.analyze_emotion(text, audio_features)
