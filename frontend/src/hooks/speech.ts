import { useCallback, useEffect, useRef, useState } from 'react';
import type { Lang } from '../api/types';

type SpeechAlternativeLike = { transcript: string };
type SpeechResultLike = { isFinal: boolean; 0: SpeechAlternativeLike };
type SpeechEventLike = { resultIndex: number; results: ArrayLike<SpeechResultLike> };
type SpeechErrorLike = { error?: string };
type RecognitionLike = {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  onresult: ((event: SpeechEventLike) => void) | null;
  onerror: ((event: SpeechErrorLike) => void) | null;
  onend: (() => void) | null;
  onstart: (() => void) | null;
  start(): void;
  stop(): void;
  abort(): void;
};
type RecognitionConstructor = new () => RecognitionLike;
type SpeechWindow = Window & {
  SpeechRecognition?: RecognitionConstructor;
  webkitSpeechRecognition?: RecognitionConstructor;
};

function recognitionLanguage(lang: Lang) {
  return lang === 'hi' || lang === 'hinglish' ? 'hi-IN' : 'en-IN';
}

function synthesisLanguage(lang: Lang) {
  return lang === 'hi' ? 'hi-IN' : 'en-IN';
}

export function useSpeechRecognition(lang: Lang) {
  const recognitionRef = useRef<RecognitionLike | null>(null);
  const simulationTimerRef = useRef<number | null>(null);
  const [supported, setSupported] = useState(false);
  const [listening, setListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interim, setInterim] = useState('');
  const [error, setError] = useState('');

  // Detect browser speech support on mount
  useEffect(() => {
    if (typeof window === 'undefined') return;
    const speechWindow = window as SpeechWindow;
    const isSupported = Boolean(speechWindow.SpeechRecognition || speechWindow.webkitSpeechRecognition);
    setSupported(isSupported);

    return () => {
      if (simulationTimerRef.current) {
        window.clearInterval(simulationTimerRef.current);
        simulationTimerRef.current = null;
      }
      if (recognitionRef.current) {
        try { recognitionRef.current.abort(); } catch { /* ignore */ }
        recognitionRef.current = null;
      }
    };
  }, []);

  const stop = useCallback(() => {
    if (simulationTimerRef.current) {
      window.clearInterval(simulationTimerRef.current);
      simulationTimerRef.current = null;
    }
    if (recognitionRef.current) {
      try { recognitionRef.current.stop(); } catch { /* ignore */ }
      recognitionRef.current = null;
    }
    setListening(false);
    setInterim('');
  }, []);

  const reset = useCallback(() => {
    stop();
    setTranscript('');
    setInterim('');
    setError('');
  }, [stop]);

  const start = useCallback(() => {
    if (typeof window === 'undefined') return;
    stop();
    setError('');

    const speechWindow = window as SpeechWindow;
    const Constructor = speechWindow.SpeechRecognition ?? speechWindow.webkitSpeechRecognition;

    if (!Constructor) {
      setError('Web Speech recognition is not available in this browser. You can use the sample explanation button or type directly.');
      return;
    }

    try {
      // Re-create a fresh SpeechRecognition instance on every start session.
      // This eliminates Chromium's InvalidStateError on reused instances.
      const recognition = new Constructor();
      recognition.lang = recognitionLanguage(lang);
      recognition.continuous = true;
      recognition.interimResults = true;

      recognition.onstart = () => {
        setListening(true);
        setError('');
      };

      recognition.onend = () => {
        setListening(false);
        setInterim('');
        recognitionRef.current = null;
      };

      recognition.onerror = (event) => {
        const errType = event?.error;
        if (errType === 'not-allowed' || errType === 'permission-denied') {
          setError('Microphone permission denied. Allow microphone access in your browser or click "Sample voice explanation".');
        } else if (errType === 'no-speech') {
          setError('No speech detected. Please speak into your microphone or try the sample explanation.');
        } else if (errType === 'network') {
          setError('Speech recognition network service error. Click "Sample voice explanation" to test offline.');
        } else if (errType === 'audio-capture') {
          setError('No microphone found. Please connect an audio input device.');
        } else if (errType && errType !== 'aborted') {
          setError(`Microphone notice: ${errType}`);
        }
        setListening(false);
        setInterim('');
        recognitionRef.current = null;
      };

      recognition.onresult = (event) => {
        let finalChunk = '';
        let interimChunk = '';
        for (let i = event.resultIndex; i < event.results.length; i += 1) {
          const item = event.results[i];
          if (item.isFinal) {
            finalChunk += `${item[0].transcript} `;
          } else {
            interimChunk += item[0].transcript;
          }
        }
        if (finalChunk.trim()) {
          setTranscript((prev) => (prev ? `${prev.trim()} ${finalChunk.trim()}` : finalChunk.trim()));
        }
        setInterim(interimChunk.trim());
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Could not initialize microphone input.');
      setListening(false);
      recognitionRef.current = null;
    }
  }, [lang, stop]);

  // Robust fallback simulation: stream sample spoken words with live wave animation
  const simulate = useCallback((sampleText: string) => {
    stop();
    setTranscript('');
    setInterim('');
    setError('');
    setListening(true);

    const words = sampleText.trim().split(/\s+/);
    let index = 0;
    let accumulated = '';

    simulationTimerRef.current = window.setInterval(() => {
      if (index >= words.length) {
        if (simulationTimerRef.current) {
          window.clearInterval(simulationTimerRef.current);
          simulationTimerRef.current = null;
        }
        setListening(false);
        setInterim('');
        return;
      }

      const nextWord = words[index];
      index += 1;
      accumulated = accumulated ? `${accumulated} ${nextWord}` : nextWord;

      if (index % 3 === 0 || index === words.length) {
        setTranscript(accumulated);
        setInterim('');
      } else {
        setInterim(nextWord);
      }
    }, 110);
  }, [stop]);

  return { supported, listening, transcript, interim, error, start, stop, reset, simulate };
}

export function useSpeechSynthesis(lang: Lang) {
  const [supported, setSupported] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const activeUtterancesRef = useRef<SpeechSynthesisUtterance[]>([]);

  useEffect(() => {
    setSupported(typeof window !== 'undefined' && 'speechSynthesis' in window && 'SpeechSynthesisUtterance' in window);
    return () => {
      if (typeof window !== 'undefined' && window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  const cancel = useCallback(() => {
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
    activeUtterancesRef.current = [];
    setSpeaking(false);
  }, []);

  const speak = useCallback((text: string) => {
    if (typeof window === 'undefined' || !('speechSynthesis' in window) || !text.trim()) return;

    window.speechSynthesis.cancel();
    activeUtterancesRef.current = [];

    // Timeout avoids Chrome audio thread cancel collision bug
    window.setTimeout(() => {
      const phrases = text.split(/(?<=[.!?।])\s+/).filter(Boolean);
      if (!phrases.length) phrases.push(text.trim());

      const targetLang = synthesisLanguage(lang).toLowerCase();
      const voices = window.speechSynthesis.getVoices();
      const matchedVoice = voices.find((v) => v.lang.toLowerCase() === targetLang)
        ?? voices.find((v) => v.lang.toLowerCase().startsWith(targetLang.slice(0, 2)))
        ?? voices.find((v) => v.lang.toLowerCase().startsWith('en'))
        ?? voices[0];

      const speakNext = (index: number) => {
        if (index >= phrases.length) {
          setSpeaking(false);
          activeUtterancesRef.current = [];
          return;
        }

        const utterance = new SpeechSynthesisUtterance(phrases[index]);
        utterance.lang = matchedVoice?.lang ?? targetLang;
        if (matchedVoice) utterance.voice = matchedVoice;
        utterance.rate = 0.95;

        utterance.onstart = () => setSpeaking(true);
        utterance.onend = () => speakNext(index + 1);
        utterance.onerror = () => {
          setSpeaking(false);
          activeUtterancesRef.current = [];
        };

        // Keep reference alive to prevent Chrome garbage collection cutoff
        activeUtterancesRef.current.push(utterance);
        window.speechSynthesis.speak(utterance);
      };

      if (voices.length > 0) {
        speakNext(0);
      } else {
        const onVoicesChanged = () => {
          window.speechSynthesis.removeEventListener('voiceschanged', onVoicesChanged);
          speakNext(0);
        };
        window.speechSynthesis.addEventListener('voiceschanged', onVoicesChanged, { once: true });
        window.setTimeout(() => {
          window.speechSynthesis.removeEventListener('voiceschanged', onVoicesChanged);
          if (!activeUtterancesRef.current.length) speakNext(0);
        }, 500);
      }
    }, 60);
  }, [lang]);

  return { supported, speaking, speak, cancel };
}
