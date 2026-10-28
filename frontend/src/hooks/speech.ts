import { useCallback, useEffect, useRef, useState } from 'react';
import type { Lang } from '../api/types';

// Person 4's expected interface is preserved. This implementation uses browser-native APIs only
// and can be replaced by their final hooks without changing page components.
type SpeechAlternativeLike = { transcript: string };
type SpeechResultLike = { isFinal: boolean; 0: SpeechAlternativeLike };
type SpeechEventLike = { resultIndex: number; results: ArrayLike<SpeechResultLike> };
type SpeechErrorLike = { error?: string };
type RecognitionLike = {
  lang: string; continuous: boolean; interimResults: boolean;
  onresult: ((event: SpeechEventLike) => void) | null;
  onerror: ((event: SpeechErrorLike) => void) | null;
  onend: (() => void) | null;
  onstart: (() => void) | null;
  start(): void; stop(): void; abort(): void;
};
type RecognitionConstructor = new () => RecognitionLike;
type SpeechWindow = Window & { SpeechRecognition?: RecognitionConstructor; webkitSpeechRecognition?: RecognitionConstructor };

function recognitionLanguage(lang: Lang) { return lang === 'hi' || lang === 'hinglish' ? 'hi-IN' : 'en-IN'; }
function synthesisLanguage(lang: Lang) { return lang === 'hi' ? 'hi-IN' : 'en-IN'; }

export function useSpeechRecognition(lang: Lang) {
  const recognitionRef = useRef<RecognitionLike | null>(null);
  const [supported, setSupported] = useState(false);
  const [listening, setListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interim, setInterim] = useState('');

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const speechWindow = window as SpeechWindow;
    const Constructor = speechWindow.SpeechRecognition ?? speechWindow.webkitSpeechRecognition;
    if (!Constructor) { setSupported(false); return; }
    const recognition = new Constructor();
    recognition.lang = recognitionLanguage(lang);
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.onstart = () => setListening(true);
    recognition.onend = () => { setListening(false); setInterim(''); };
    recognition.onerror = () => { setListening(false); };
    recognition.onresult = (event) => {
      let finalText = '';
      let interimText = '';
      for (let index = event.resultIndex; index < event.results.length; index += 1) {
        const result = event.results[index];
        if (result.isFinal) finalText += `${result[0].transcript} `;
        else interimText += result[0].transcript;
      }
      if (finalText.trim()) setTranscript((current) => `${current}${current ? ' ' : ''}${finalText.trim()}`);
      setInterim(interimText.trim());
    };
    recognitionRef.current = recognition;
    setSupported(true);
    return () => { recognition.abort(); recognitionRef.current = null; setListening(false); };
  }, [lang]);

  const start = useCallback(() => {
    if (!recognitionRef.current || listening) return;
    try { recognitionRef.current.start(); } catch { /* browser can reject duplicate start attempts */ }
  }, [listening]);
  const stop = useCallback(() => { try { recognitionRef.current?.stop(); } catch { setListening(false); } }, []);
  const reset = useCallback(() => { setTranscript(''); setInterim(''); }, []);
  return { supported, listening, transcript, interim, start, stop, reset };
}

export function useSpeechSynthesis(lang: Lang) {
  const [supported, setSupported] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);
  useEffect(() => {
    setSupported(typeof window !== 'undefined' && 'speechSynthesis' in window && 'SpeechSynthesisUtterance' in window);
    return () => { if (typeof window !== 'undefined' && window.speechSynthesis) window.speechSynthesis.cancel(); };
  }, []);
  const cancel = useCallback(() => {
    if (typeof window !== 'undefined' && window.speechSynthesis) window.speechSynthesis.cancel();
    utteranceRef.current = null;
    setSpeaking(false);
  }, []);
  const speak = useCallback((text: string) => {
    if (typeof window === 'undefined' || !('speechSynthesis' in window) || !text.trim()) return;
    window.speechSynthesis.cancel();
    const phrases = text.split(/(?<=[.!?।])\s+/).filter(Boolean);
    const speakNext = (index: number) => {
      if (index >= phrases.length) { setSpeaking(false); return; }
      const utterance = new SpeechSynthesisUtterance(phrases[index]);
      utterance.lang = synthesisLanguage(lang);
      utterance.onstart = () => setSpeaking(true);
      utterance.onend = () => speakNext(index + 1);
      utterance.onerror = () => setSpeaking(false);
      const voices = window.speechSynthesis.getVoices();
      const voice = voices.find((candidate) => candidate.lang.toLowerCase() === utterance.lang.toLowerCase());
      if (voice) utterance.voice = voice;
      utteranceRef.current = utterance;
      window.speechSynthesis.speak(utterance);
    };
    const voices = window.speechSynthesis.getVoices();
    if (voices.length) speakNext(0);
    else {
      const onVoicesChanged = () => { window.speechSynthesis.removeEventListener('voiceschanged', onVoicesChanged); speakNext(0); };
      window.speechSynthesis.addEventListener('voiceschanged', onVoicesChanged, { once: true });
      // Some browsers never dispatch voiceschanged if no remote voices are available.
      window.setTimeout(() => { window.speechSynthesis.removeEventListener('voiceschanged', onVoicesChanged); if (!utteranceRef.current) speakNext(0); }, 700);
    }
  }, [lang]);
  return { supported, speaking, speak, cancel };
}
