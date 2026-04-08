import React, { useState, useRef, useEffect } from 'react';
import { Mic, MicOff, Loader2 } from 'lucide-react';

/*
  VoiceRecorder — Web Speech API for voice-to-text interview answers
  Props:
    onTranscript — callback(text) when transcription is ready
    disabled     — boolean
*/
function VoiceRecorder({ onTranscript, disabled = false }) {
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState('');
  const recognitionRef = useRef(null);

  /* Check browser support */
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const isSupported = !!SpeechRecognition;

  useEffect(() => {
    if (!isSupported) return;

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onresult = (event) => {
      let finalText = '';
      let interimText = '';

      for (let i = 0; i < event.results.length; i++) {
        const result = event.results[i];
        if (result.isFinal) {
          finalText += result[0].transcript + ' ';
        } else {
          interimText += result[0].transcript;
        }
      }

      const full = finalText + interimText;
      setTranscript(full);
    };

    recognition.onerror = (event) => {
      setError(`Voice error: ${event.error}`);
      setIsRecording(false);
    };

    recognition.onend = () => {
      setIsRecording(false);
    };

    recognitionRef.current = recognition;

    return () => {
      if (recognitionRef.current) {
        try { recognitionRef.current.stop(); } catch (e) { /* ignore */ }
      }
    };
  }, [isSupported]);

  const startRecording = () => {
    if (!recognitionRef.current) return;
    setError('');
    setTranscript('');
    setIsRecording(true);
    recognitionRef.current.start();
  };

  const stopRecording = () => {
    if (!recognitionRef.current) return;
    recognitionRef.current.stop();
    setIsRecording(false);

    /* send transcript to parent */
    if (transcript.trim() && onTranscript) {
      onTranscript(transcript.trim());
    }
  };

  if (!isSupported) {
    return (
      <div className="text-sm text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-900/20 px-4 py-3 rounded-xl">
        ⚠️ Voice recording is not supported in this browser. Please use Chrome or Edge.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-3">
        <button
          onClick={isRecording ? stopRecording : startRecording}
          disabled={disabled}
          className={`flex items-center gap-2 px-5 py-2.5 rounded-xl font-medium text-sm transition-all duration-300 ${
            isRecording
              ? 'bg-red-500 text-white shadow-lg shadow-red-500/30 animate-pulse-slow'
              : 'bg-brand-500/10 text-brand-600 dark:text-brand-400 hover:bg-brand-500/20'
          } disabled:opacity-50`}
        >
          {isRecording ? (
            <>
              <MicOff className="w-4 h-4" />
              Stop Recording
            </>
          ) : (
            <>
              <Mic className="w-4 h-4" />
              Start Voice Answer
            </>
          )}
        </button>

        {isRecording && (
          <div className="flex items-center gap-2 text-sm text-red-500">
            <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
            Listening...
          </div>
        )}
      </div>

      {/* Live transcript preview */}
      {transcript && (
        <div className="p-4 rounded-xl bg-gray-50 dark:bg-surface-800 border border-gray-200 dark:border-gray-700">
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-1 font-medium">
            Transcribed text:
          </p>
          <p className="text-gray-800 dark:text-gray-200 text-sm leading-relaxed">
            {transcript}
          </p>
        </div>
      )}

      {error && (
        <p className="text-sm text-red-500">{error}</p>
      )}
    </div>
  );
}

export default VoiceRecorder;
