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
        """Fallback scoring using TF-IDF cosine similarity."""
        resume_clean = self.clean_text(resume_text)
        jd_clean = self.clean_text(job_description) if job_description else ""

        if not jd_clean:
            # Without a JD, give a moderate baseline score
            word_count = len(resume_clean.split())
            base_score = min(65, 30 + word_count // 10)
            return {
                "match_score": base_score,
                "selection_probability": round(base_score / 100 * 0.9, 3),
                "method": "tfidf_fallback"
            }

        try:
            vectorizer = TfidfVectorizer(max_features=500, stop_words='english')
            tfidf_matrix = vectorizer.fit_transform([resume_clean, jd_clean])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        except Exception:
            similarity = 0.4

        match_score = int(min(100, max(0, similarity * 120)))  # scale up slightly
        selection_prob = round(min(0.95, similarity * 1.1), 3)

        return {
            "match_score": match_score,
            "selection_probability": selection_prob,
            "method": "tfidf_fallback"
        }

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
