"""
LSTM-based Resume Scorer — Dual-Input Architecture
Uses Long Short-Term Memory networks for resume-job description matching.

Architecture:
  - Resume Encoder: Bi-LSTM reads resume text
  - JD Encoder: Bi-LSTM reads job description
  - Concatenation: Merge both encodings
  - Dense layers: Predict match score (0-100) and selection probability (0-1)

Falls back to TF-IDF cosine similarity when the model is not trained.
"""

import numpy as np
import re
import os
import pickle

# ===== SAFE IMPORTS (fail gracefully if TensorFlow not installed) =====
try:
    import tensorflow as tf
    from tensorflow.keras.models import Model
    from tensorflow.keras.layers import (
        Input, Embedding, LSTM, Bidirectional, Dense,
        Dropout, concatenate, GlobalAveragePooling1D
    )
    from tensorflow.keras.preprocessing.text import Tokenizer
    from tensorflow.keras.preprocessing.sequence import pad_sequences
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    print("[INFO] TensorFlow not installed — using fallback scoring (TF-IDF).")

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# =====================================================================
#  CONSTANTS
# =====================================================================
MAX_VOCAB_SIZE = 8000       # max words in vocabulary
EMBEDDING_DIM = 100         # word vector dimensions
MAX_SEQUENCE_LEN = 300      # max tokens per document
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')


class LSTMResumeScorer:
    """
    Dual-input Bi-LSTM model that reads both resume and job description
    and predicts:
      1. match_score (0-100)
      2. selection_probability (0-1)
    """

    def __init__(self):
        self.max_vocab = MAX_VOCAB_SIZE
        self.embed_dim = EMBEDDING_DIM
        self.max_len = MAX_SEQUENCE_LEN
        self.tokenizer = None
        self.model = None
        self.is_trained = False

        # Try to load pre-trained model
        self._try_load_model()

    # ─────────────── BUILD MODEL ───────────────
    def build_model(self):
        """Build dual-input Bi-LSTM architecture."""
        if not TF_AVAILABLE:
            return None

        # ── Resume input branch ──
        resume_input = Input(shape=(self.max_len,), name='resume_input')
        resume_embed = Embedding(
            input_dim=self.max_vocab,
            output_dim=self.embed_dim,
            input_length=self.max_len,
            name='resume_embedding'
        )(resume_input)
        resume_lstm = Bidirectional(
            LSTM(64, return_sequences=True, dropout=0.3),
            name='resume_bilstm'
        )(resume_embed)
        resume_pool = GlobalAveragePooling1D(name='resume_pool')(resume_lstm)

        # ── Job description input branch ──
        jd_input = Input(shape=(self.max_len,), name='jd_input')
        jd_embed = Embedding(
            input_dim=self.max_vocab,
            output_dim=self.embed_dim,
            input_length=self.max_len,
            name='jd_embedding'
        )(jd_input)
        jd_lstm = Bidirectional(
            LSTM(64, return_sequences=True, dropout=0.3),
            name='jd_bilstm'
        )(jd_embed)
        jd_pool = GlobalAveragePooling1D(name='jd_pool')(jd_lstm)

        # ── Merge both branches ──
        merged = concatenate([resume_pool, jd_pool], name='merge')

        # ── Dense prediction layers ──
        dense_1 = Dense(128, activation='relu', name='dense_1')(merged)
        drop_1 = Dropout(0.3)(dense_1)
        dense_2 = Dense(64, activation='relu', name='dense_2')(drop_1)
        drop_2 = Dropout(0.2)(dense_2)

        # ── Two outputs ──
        match_score = Dense(1, activation='sigmoid', name='match_score')(drop_2)
        selection_prob = Dense(1, activation='sigmoid', name='selection_prob')(drop_2)

        model = Model(
            inputs=[resume_input, jd_input],
            outputs=[match_score, selection_prob]
        )

        model.compile(
            optimizer='adam',
            loss={'match_score': 'mse', 'selection_prob': 'binary_crossentropy'},
            loss_weights={'match_score': 1.0, 'selection_prob': 0.5},
            metrics={'match_score': 'mae', 'selection_prob': 'accuracy'}
        )

        self.model = model
        return model

    # ─────────────── TEXT PREPROCESSING ───────────────
    @staticmethod
    def clean_text(text):
        """Basic text cleaning for any document."""
        text = text.lower()
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def prepare_texts(self, texts, fit=False):
        """Tokenize and pad a list of texts."""
        cleaned = [self.clean_text(t) for t in texts]

        if self.tokenizer is None:
            self.tokenizer = Tokenizer(num_words=self.max_vocab, oov_token='<OOV>')

        if fit:
            self.tokenizer.fit_on_texts(cleaned)

        sequences = self.tokenizer.texts_to_sequences(cleaned)
        padded = pad_sequences(sequences, maxlen=self.max_len, padding='post', truncating='post')
        return padded

    # ─────────────── SCORE RESUME (MAIN API) ───────────────
    def score_resume(self, resume_text, job_description=""):
        """
        Score a resume against a job description.

        Returns dict:
          {
            "match_score": int 0-100,
            "selection_probability": float 0-1,
            "method": "lstm" | "tfidf_fallback"
          }
        """
        # ── Try LSTM model first ──
        if self.is_trained and self.model is not None and TF_AVAILABLE:
            return self._score_with_lstm(resume_text, job_description)

        # ── Fallback to TF-IDF ──
        return self._score_with_tfidf(resume_text, job_description)

    def _score_with_lstm(self, resume_text, job_description):
        """Score using the trained LSTM model."""
        resume_seq = self.prepare_texts([resume_text])
        jd_seq = self.prepare_texts([job_description if job_description else "general software engineering role"])

        predictions = self.model.predict([resume_seq, jd_seq], verbose=0)
        match_raw = float(predictions[0][0][0])
        select_raw = float(predictions[1][0][0])

        return {
            "match_score": int(min(100, max(0, match_raw * 100))),
            "selection_probability": round(select_raw, 3),
            "method": "lstm"
        }

    def _score_with_tfidf(self, resume_text, job_description):
        """
        Multi-signal fallback scoring when LSTM model is not available.
        Uses TF-IDF + skill overlap + resume quality signals for accurate scoring.
        """
        resume_clean = self.clean_text(resume_text)
        jd_clean = self.clean_text(job_description) if job_description else ""

        # ── Signal 1: Resume quality baseline ──
        quality = self._assess_resume_quality(resume_clean)

        if not jd_clean:
            # Without a JD, score based on resume quality alone
            base_score = int(quality * 70 + 15)  # 15-85 range
            base_score = min(75, max(20, base_score))
            return {
                "match_score": base_score,
                "selection_probability": round(base_score / 100 * 0.85, 3),
                "method": "tfidf_fallback"
            }

        # ── Signal 2: TF-IDF cosine similarity ──
        try:
            vectorizer = TfidfVectorizer(max_features=500, stop_words='english')
            tfidf_matrix = vectorizer.fit_transform([resume_clean, jd_clean])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        except Exception:
            similarity = 0.3

        # ── Signal 3: Direct keyword overlap ──
        resume_words = set(resume_clean.split())
        jd_words = set(jd_clean.split())
        # Remove very common words
        common_stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                           'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
                           'should', 'could', 'may', 'might', 'shall', 'can', 'and', 'or',
                           'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from',
                           'as', 'into', 'that', 'this', 'it', 'not', 'no', 'so', 'if', 'we',
                           'you', 'they', 'our', 'your', 'their', 'its', 'all', 'each', 'every',
                           'any', 'some', 'such', 'than', 'too', 'very', 'just', 'about', 'more',
                           'also', 'up', 'out', 'how', 'what', 'when', 'where', 'who', 'which',
                           'years', 'experience', 'looking', 'role', 'work', 'working', 'using',
                           'strong', 'required', 'requirements', 'preferred', 'including'}
        jd_keywords = jd_words - common_stopwords
        jd_keywords = {w for w in jd_keywords if len(w) > 2}
        if jd_keywords:
            keyword_overlap = len(resume_words & jd_keywords) / len(jd_keywords)
        else:
            keyword_overlap = 0.3

        # ── Signal 4: Tech-specific skill matching ──
        tech_skills = [
            'python', 'javascript', 'java', 'react', 'angular', 'vue', 'node', 'nodejs',
            'sql', 'mysql', 'postgresql', 'mongodb', 'docker', 'kubernetes', 'aws', 'azure',
            'gcp', 'git', 'github', 'linux', 'tensorflow', 'pytorch', 'flask', 'django',
            'fastapi', 'express', 'typescript', 'html', 'css', 'api', 'rest', 'graphql',
            'redis', 'kafka', 'ci', 'cd', 'agile', 'scrum', 'testing', 'jenkins',
            'terraform', 'ansible', 'machine', 'learning', 'deep', 'nlp', 'pandas', 'numpy',
            'scikit', 'keras', 'next', 'tailwind', 'bootstrap', 'webpack', 'vite',
            'microservices', 'spring', 'golang', 'rust', 'swift', 'kotlin', 'firebase'
        ]
        jd_tech = {w for w in jd_clean.split() if w in tech_skills}
        resume_tech = {w for w in resume_clean.split() if w in tech_skills}
        if jd_tech:
            tech_overlap = len(resume_tech & jd_tech) / len(jd_tech)
        else:
            tech_overlap = min(1.0, len(resume_tech) / 8)  # reward having tech skills
        # ── Signal 5: Skill breadth (total tech skills in resume) ──
        skill_breadth = min(1.0, len(resume_tech) / 10)  # 10+ tech skills → 1.0

        # ── Combine signals with weighted formula ──
        # Nonlinear scaling for TF-IDF (boost low but non-zero similarities)
        scaled_similarity = min(1.0, similarity * 2.5)  # 0.2 sim → 0.5 scaled

        combined = (
            scaled_similarity * 0.15 +     # TF-IDF textual similarity
            keyword_overlap * 0.15 +        # Direct keyword matching
            tech_overlap * 0.30 +           # Technical skill matching (most important)
            skill_breadth * 0.15 +          # Skill breadth bonus
            quality * 0.25                  # Resume quality/completeness
        )

        # Apply sigmoid-like curve to map to 0-100 nicely
        # This prevents extreme low/high scores
        match_score = int(combined * 100)
        match_score = min(95, max(8, match_score))

        # Selection probability: correlated but slightly more conservative
        selection_prob = round(min(0.92, combined * 0.95), 3)

        return {
            "match_score": match_score,
            "selection_probability": selection_prob,
            "method": "tfidf_fallback"
        }

    def _assess_resume_quality(self, text_clean):
        """
        Assess the overall quality of a resume text (0.0-1.0).
        Checks: word count, sections, action verbs, technical terms, metrics.
        """
        score = 0.0
        text_lower = text_clean.lower() if text_clean else ""
        word_count = len(text_lower.split())

        # Word count (content depth)
        if word_count >= 300:
            score += 0.20
        elif word_count >= 200:
            score += 0.15
        elif word_count >= 100:
            score += 0.10
        else:
            score += 0.03

        # Resume sections present
        sections = ['experience', 'education', 'skills', 'projects', 'summary',
                    'objective', 'profile', 'certif', 'achievement']
        section_count = sum(1 for s in sections if s in text_lower)
        score += min(0.25, section_count * 0.05)

        # Action verbs (impact language)
        action_verbs = ['developed', 'implemented', 'designed', 'led', 'managed',
                       'created', 'built', 'optimized', 'improved', 'deployed',
                       'architected', 'delivered', 'automated', 'integrated', 'reduced']
        verb_count = sum(1 for v in action_verbs if v in text_lower)
        score += min(0.20, verb_count * 0.03)

        # Technical terms density
        tech_terms = ['api', 'database', 'server', 'cloud', 'framework', 'library',
                     'algorithm', 'system', 'application', 'architecture', 'deployment',
                     'testing', 'performance', 'security', 'integration']
        tech_count = sum(1 for t in tech_terms if t in text_lower)
        score += min(0.15, tech_count * 0.025)

        # Quantifiable achievements
        import re
        metrics = re.findall(r'\d+%|\$\d+|\d+\+?\s*(?:users|clients|projects|team)', text_lower)
        score += min(0.10, len(metrics) * 0.025)

        # Contact info / professional signals
        if re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', text_lower):
            score += 0.05
        if any(w in text_lower for w in ['github', 'linkedin', 'portfolio']):
            score += 0.05

        return min(1.0, score)

    # ─────────────── TRAINING ───────────────
    def train(self, resume_texts, jd_texts, match_scores, selection_labels, epochs=15):
        """
        Train the LSTM model on labelled data.

        Args:
            resume_texts:    list of resume strings
            jd_texts:        list of job description strings
            match_scores:    list of floats 0-1 (target match score / 100)
            selection_labels: list of 0/1 (selected or not)
            epochs:          training epochs
        """
        if not TF_AVAILABLE:
            print("[WARN] TensorFlow not available, skipping training.")
            return

        # Prepare data
        all_texts = resume_texts + jd_texts
        resume_seqs = self.prepare_texts(resume_texts, fit=True)
        # Re-fit tokenizer with all texts for JD too
        self.tokenizer.fit_on_texts([self.clean_text(t) for t in all_texts])
        resume_seqs = self.prepare_texts(resume_texts)
        jd_seqs = self.prepare_texts(jd_texts)

        y_match = np.array(match_scores, dtype='float32')
        y_select = np.array(selection_labels, dtype='float32')

        # Build model if needed
        if self.model is None:
            self.build_model()

        # Train
        self.model.fit(
            [resume_seqs, jd_seqs],
            {'match_score': y_match, 'selection_prob': y_select},
            epochs=epochs,
            batch_size=16,
            validation_split=0.2,
            verbose=1
        )

        self.is_trained = True
        self._save_model()
        print("[OK] LSTM model trained and saved.")

    # ─────────────── SAVE / LOAD ───────────────
    def _save_model(self):
        os.makedirs(MODEL_DIR, exist_ok=True)
        if self.model:
            self.model.save(os.path.join(MODEL_DIR, 'lstm_scorer.h5'))
        if self.tokenizer:
            with open(os.path.join(MODEL_DIR, 'tokenizer.pkl'), 'wb') as f:
                pickle.dump(self.tokenizer, f)

    def _try_load_model(self):
        model_path = os.path.join(MODEL_DIR, 'lstm_scorer.h5')
        tok_path = os.path.join(MODEL_DIR, 'tokenizer.pkl')

        if os.path.exists(model_path) and os.path.exists(tok_path) and TF_AVAILABLE:
            try:
                self.model = tf.keras.models.load_model(model_path)
                with open(tok_path, 'rb') as f:
                    self.tokenizer = pickle.load(f)
                self.is_trained = True
                print("[OK] Loaded pre-trained LSTM model.")
            except Exception as e:
                print(f"[WARN] Could not load model: {e}")


# =====================================================================
#  QUICK API FUNCTION (used by main.py)
# =====================================================================
_scorer_instance = None

def get_lstm_score(resume_text, job_description=""):
    """
    Quick-use function that returns match score & selection probability.
    Reuses a singleton scorer instance.
    """
    global _scorer_instance
    if _scorer_instance is None:
        _scorer_instance = LSTMResumeScorer()
    return _scorer_instance.score_resume(resume_text, job_description)
