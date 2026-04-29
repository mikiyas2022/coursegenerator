'use client';

/**
 * page.tsx — 3B1B English Course Factory UI (v5)
 * Single clean input form → Generate 3B1B Course → Live log stream → Done
 */

import React, {
  useCallback, useEffect, useRef, useState,
} from 'react';

// ── Types ─────────────────────────────────────────────────────────────────

type View = 'input' | 'generating' | 'error';

interface LogEntry {
  time: string;
  msg: string;
  phase: string;
  icon: string;
}

interface StreamEvent {
  type: string;
  payload: Record<string, unknown>;
}

// ── Constants ─────────────────────────────────────────────────────────────

const ORCHESTRATOR_URL = process.env.NEXT_PUBLIC_ORCHESTRATOR_URL ?? 'http://localhost:8100';

const PHASE_ICONS: Record<string, string> = {
  researcher:      '🔬',
  scriptwriter:    '✍️',
  visual_designer: '🎨',
  math_verifier:   '🧮',
  coding:          '⚙️',
  final_render:    '🎬',
  postprod:        '✨',
  complete:        '🏆',
  error:           '❌',
  init:            '○',
};

const PHASE_COLORS: Record<string, string> = {
  researcher:      '#3DCCC7',
  scriptwriter:    '#C792EA',
  visual_designer: '#FF8FAB',
  math_verifier:   '#FFD700',
  coding:          '#61AFEF',
  final_render:    '#F97316',
  postprod:        '#4ECDC4',
  complete:        '#4ECDC4',
  error:           '#FF6B6B',
  init:            '#8892B0',
};

const AUDIENCE_OPTIONS = [
  'Middle School (Grade 6–8)',
  'High School (Grade 7–12)',
  'University / Undergraduate',
  'Advanced / Graduate',
  'General Public',
];

const STYLE_OPTIONS = [
  'World-Class 3b1b (Deep Visual Insight)',
  'Playful & Humorous (Casual Explainer)',
  'Rigorous & Mathematical (Proof-Based)',
  'Story-Driven (Narrative First)',
  'Intuition-First (No Formulas Until the End)',
];

const METAPHOR_OPTIONS = [
  '',
  'Abstract mathematical animations',
  'Water flow and fluid analogies',
  'Physical objects and everyday mechanics',
  'Geometric shapes morphing and growing',
  'Nature-inspired (waves, plants, stars)',
  'Engineering and machines',
];

// ── Main Component ────────────────────────────────────────────────────────

export default function HomePage() {
  const [view, setView] = useState<View>('input');

  // Form state
  const [topic,     setTopic]     = useState('');
  const [audience,  setAudience]  = useState(AUDIENCE_OPTIONS[1]);
  const [style,     setStyle]     = useState(STYLE_OPTIONS[0]);
  const [metaphor,  setMetaphor]  = useState(METAPHOR_OPTIONS[0]);
  const [source,    setSource]    = useState('');

  // Generation state
  const [logs,       setLogs]       = useState<LogEntry[]>([]);
  const [errorMsg,   setErrorMsg]   = useState('');
  const [outputPath, setOutputPath] = useState('');
  const [masterPath, setMasterPath] = useState('');
  const [sizeMb,     setSizeMb]     = useState(0);

  const bottomRef = useRef<HTMLDivElement>(null);
  const sourceRef = useRef<EventSource | null>(null);

  // Auto-scroll logs
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  // Cleanup SSE on unmount
  useEffect(() => () => sourceRef.current?.close(), []);

  // ── Add log entry ──────────────────────────────────────────────────────
  const addLog = useCallback((msg: string, phase: string) => {
    const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    const icon = PHASE_ICONS[phase] ?? '○';
    setLogs(prev => [...prev, { time: now, msg, phase, icon }]);
  }, []);

  // ── Generate ───────────────────────────────────────────────────────────
  const handleGenerate = useCallback(async () => {
    if (!topic.trim()) return;
    setView('generating');
    setLogs([]);
    setOutputPath('');
    setMasterPath('');
    setSizeMb(0);
    sourceRef.current?.close();

    const body = JSON.stringify({
      topic,
      audience,
      style,
      metaphor,
      source_material: source,
      persona_id:  1,
      orientation: 'landscape',
      run_postprod: true,
    });

    addLog(`Starting 3B1B course on "${topic}"…`, 'init');

    try {
      const resp = await fetch(`${ORCHESTRATOR_URL}/generate_full`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body,
      });

      if (!resp.ok || !resp.body) {
        throw new Error(`HTTP ${resp.status}`);
      }

      const reader = resp.body.getReader();
      const dec    = new TextDecoder();
      let   buf    = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buf += dec.decode(value, { stream: true });

        const parts = buf.split('\n\n');
        buf = parts.pop() ?? '';

        for (const part of parts) {
          const line = part.trim();
          if (!line.startsWith('data:')) continue;
          try {
            const ev: StreamEvent = JSON.parse(line.slice(5).trim());
            handleEvent(ev);
          } catch { /* skip malformed */ }
        }
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setErrorMsg(msg);
      setView('error');
    }
  }, [topic, audience, style, metaphor, source, addLog]);

  const handleEvent = useCallback((ev: StreamEvent) => {
    const p = ev.payload ?? {};
    const msg = (p.message as string) ?? ev.type;
    const phase = (p.phase as string) ?? ev.type;

    if (ev.type === 'ping') return; // suppress ping noise

    if (ev.type === 'error') {
      addLog(msg, 'error');
      setErrorMsg(msg);
      setView('error');
      return;
    }

    addLog(msg, phase);

    if (ev.type === 'complete') {
      setOutputPath((p.output_folder as string) ?? '');
      setMasterPath((p.master_path as string) ?? '');
      setSizeMb((p.size_mb as number) ?? 0);
    }
  }, [addLog]);

  const isDone = logs.some(l => l.phase === 'complete');

  // ── Render ──────────────────────────────────────────────────────────────
  return (
    <main style={{ minHeight: '100vh', background: '#1C1C2E', color: '#FFFEF0', fontFamily: 'Inter, sans-serif' }}>
      <style>{`
        * { box-sizing: border-box; margin: 0; padding: 0; }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: rgba(255,255,255,0.04); }
        ::-webkit-scrollbar-thumb { background: #3DCCC7; border-radius: 4px; }
        @keyframes fadeUp { from { opacity:0; transform:translateY(12px); } to { opacity:1; transform:translateY(0); } }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.5} }
        @keyframes glow { 0%,100%{box-shadow:0 0 20px rgba(61,204,199,0.3)} 50%{box-shadow:0 0 40px rgba(61,204,199,0.6)} }
        .card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07); border-radius: 16px; padding: 20px; }
        .btn-primary {
          background: linear-gradient(135deg, #3DCCC7, #1E3A8A);
          border: none; border-radius: 14px; color: #fff; cursor: pointer;
          font-size: 16px; font-weight: 700; letter-spacing: 0.5px;
          padding: 16px 32px; transition: all 0.2s; width: 100%;
          font-family: Inter, sans-serif;
        }
        .btn-primary:hover { filter: brightness(1.12); transform: translateY(-1px); }
        .btn-primary:active { transform: translateY(0); }
        .btn-primary:disabled { opacity: 0.45; cursor: not-allowed; transform: none; }
        .input-field {
          width: 100%; background: rgba(0,0,0,0.35); border: 1px solid rgba(255,255,255,0.1);
          border-radius: 12px; color: #FFFEF0; font-size: 14px; font-family: Inter, sans-serif;
          padding: 12px 16px; outline: none; transition: border-color 0.2s;
        }
        .input-field:focus { border-color: #3DCCC7; }
        .select-field {
          width: 100%; background: rgba(0,0,0,0.35); border: 1px solid rgba(255,255,255,0.1);
          border-radius: 12px; color: #FFFEF0; font-size: 13px; font-family: Inter, sans-serif;
          padding: 11px 14px; outline: none; appearance: none; cursor: pointer;
          transition: border-color 0.2s;
        }
        .select-field:focus { border-color: #3DCCC7; }
        label { display: block; font-size: 10px; font-weight: 700; color: #8892B0; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 6px; }
        .log-entry { animation: fadeUp 0.2s ease-out; }
      `}</style>

      {/* ── HEADER ── */}
      <header style={{ padding: '28px 32px 0', maxWidth: 720, margin: '0 auto' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 4 }}>
          <div style={{
            background: 'linear-gradient(135deg, #3DCCC7, #1E3A8A)',
            borderRadius: 12, width: 42, height: 42,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 22, animation: 'glow 3s ease-in-out infinite',
          }}>π</div>
          <div>
            <h1 style={{ fontSize: 20, fontWeight: 800, color: '#FFFEF0', lineHeight: 1 }}>
              3B1B English Course Factory
            </h1>
            <p style={{ fontSize: 11, color: '#8892B0', marginTop: 3 }}>
              Grant Sanderson–quality STEM explainer videos • Kokoro TTS • 42 base + 1000+ generated templates
            </p>
          </div>
        </div>
      </header>

      <div style={{ maxWidth: 720, margin: '0 auto', padding: '24px 32px 48px' }}>

        {/* ════ INPUT VIEW ════ */}
        {view === 'input' && (
          <div style={{ animation: 'fadeUp 0.4s ease-out' }}>

            {/* Hero section */}
            <div className="card" style={{ marginBottom: 16, borderColor: 'rgba(61,204,199,0.2)' }}>
              <p style={{ fontSize: 13, color: '#ABB2BF', lineHeight: 1.65 }}>
                Generate a <strong style={{ color: '#3DCCC7' }}>world-class educational video</strong> on any STEM topic.
                The AI writes a full 6–8 scene episode with hooks, worked examples, visual intuition, and "aha!" moments —
                then animates and narrates it automatically using Manim + Kokoro TTS.
              </p>
            </div>

            {/* Topic */}
            <div className="card" style={{ marginBottom: 12 }}>
              <label htmlFor="topic-input">Topic</label>
              <textarea
                id="topic-input"
                className="input-field"
                placeholder="e.g. Why does the Pythagorean theorem work? · Fourier series visualized · Newton's Laws of Motion · The beauty of complex numbers"
                value={topic}
                onChange={e => setTopic(e.target.value)}
                rows={3}
                style={{ resize: 'vertical', minHeight: 72 }}
              />
            </div>

            {/* Config grid */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 12 }}>
              <div className="card">
                <label htmlFor="audience-select">Audience</label>
                <select id="audience-select" className="select-field" value={audience} onChange={e => setAudience(e.target.value)}>
                  {AUDIENCE_OPTIONS.map(o => <option key={o}>{o}</option>)}
                </select>
              </div>
              <div className="card">
                <label htmlFor="style-select">Narration Style</label>
                <select id="style-select" className="select-field" value={style} onChange={e => setStyle(e.target.value)}>
                  {STYLE_OPTIONS.map(o => <option key={o}>{o}</option>)}
                </select>
              </div>
            </div>

            <div className="card" style={{ marginBottom: 12 }}>
              <label htmlFor="metaphor-select">Visual Metaphor Theme (optional)</label>
              <select id="metaphor-select" className="select-field" value={metaphor} onChange={e => setMetaphor(e.target.value)}>
                <option value="">Auto-select best metaphor</option>
                {METAPHOR_OPTIONS.filter(Boolean).map(o => <option key={o}>{o}</option>)}
              </select>
            </div>

            {/* Optional source material */}
            <div className="card" style={{ marginBottom: 20 }}>
              <label htmlFor="source-input">Source Material (optional)</label>
              <textarea
                id="source-input"
                className="input-field"
                placeholder="Paste lecture notes, textbook excerpts, or any reference text here. The AI will ground the explanations in this material."
                value={source}
                onChange={e => setSource(e.target.value)}
                rows={4}
                style={{ resize: 'vertical', minHeight: 80 }}
              />
            </div>

            {/* Generate button */}
            <button
              id="generate-btn"
              className="btn-primary"
              onClick={handleGenerate}
              disabled={!topic.trim()}
            >
              🚀 Generate 3B1B Course
            </button>

            {/* Pipeline info */}
            <div style={{ marginTop: 16, display: 'flex', justifyContent: 'center', gap: 20, flexWrap: 'wrap' }}>
              {[
                ['🔬', 'Researcher'],
                ['✍️', 'Scriptwriter'],
                ['🎨', 'Visual Designer'],
                ['🧮', 'Math Verifier'],
                ['⚙️', 'Template Orchestrator'],
                ['🎬', 'Manim + Kokoro'],
                ['✨', 'Post-Production'],
              ].map(([icon, name]) => (
                <div key={name} style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 11, color: '#8892B0' }}>
                  <span>{icon}</span><span>{name}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ════ GENERATING VIEW ════ */}
        {view === 'generating' && (
          <div style={{ animation: 'fadeUp 0.3s ease-out' }}>

            {/* Status header */}
            <div className="card" style={{ marginBottom: 12, borderColor: isDone ? 'rgba(61,204,199,0.4)' : 'rgba(255,215,0,0.2)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <div style={{
                  width: 36, height: 36, borderRadius: '50%',
                  background: isDone ? 'rgba(61,204,199,0.15)' : 'rgba(255,215,0,0.1)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: 20,
                  animation: isDone ? 'none' : 'pulse 1.8s ease-in-out infinite',
                }}>
                  {isDone ? '🏆' : '⚡'}
                </div>
                <div>
                  <div style={{ fontSize: 15, fontWeight: 700, color: isDone ? '#3DCCC7' : '#FFD700' }}>
                    {isDone ? '3B1B Masterpiece Complete!' : `Generating: "${topic}"`}
                  </div>
                  <div style={{ fontSize: 11, color: '#8892B0', marginTop: 2 }}>
                    {isDone
                      ? `${sizeMb > 0 ? `${sizeMb} MB · ` : ''}${outputPath || 'Render complete'}`
                      : 'AI pipeline running — this takes 5–15 minutes…'}
                  </div>
                </div>
              </div>
            </div>

            {/* Final video path */}
            {isDone && masterPath && (
              <div className="card" style={{ marginBottom: 12, borderColor: 'rgba(61,204,199,0.25)', background: 'rgba(61,204,199,0.04)' }}>
                <label>Output Video</label>
                <p style={{ fontSize: 12, color: '#3DCCC7', fontFamily: 'monospace', wordBreak: 'break-all', marginTop: 4 }}>
                  {masterPath}
                </p>
              </div>
            )}

            {/* Log stream */}
            <div className="card" style={{ marginBottom: 12 }}>
              <label style={{ marginBottom: 10 }}>Pipeline Log</label>
              <div style={{ maxHeight: 420, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 6 }}>
                {logs.map((log, i) => {
                  const isLast = i === logs.length - 1 && !isDone;
                  const color = PHASE_COLORS[log.phase] ?? '#8892B0';
                  return (
                    <div key={i} className="log-entry" style={{ display: 'flex', alignItems: 'flex-start', gap: 10 }}>
                      <span style={{ fontSize: 14, flexShrink: 0, marginTop: 1 }}>{log.icon}</span>
                      <span style={{
                        flex: 1, fontSize: 13, color,
                        fontWeight: isLast ? 700 : 400,
                        opacity: isLast ? 1 : 0.75,
                        lineHeight: 1.5,
                      }}>{log.msg}</span>
                      <span style={{ fontSize: 9, color: '#3E4451', fontFamily: 'monospace', flexShrink: 0, marginTop: 3 }}>
                        {log.time}
                      </span>
                    </div>
                  );
                })}

                {!isDone && logs.length > 0 && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, paddingTop: 4 }}>
                    <div style={{ display: 'flex', gap: 3 }}>
                      {[0, 1, 2].map(i => (
                        <div key={i} style={{
                          width: 5, height: 5, borderRadius: '50%', background: '#3DCCC7',
                          animation: `pulse 1.4s ease-in-out ${i * 0.2}s infinite`,
                        }} />
                      ))}
                    </div>
                    <span style={{ fontSize: 11, color: '#8892B0' }}>Processing…</span>
                  </div>
                )}

                <div ref={bottomRef} />
              </div>
            </div>

            <button
              id="cancel-btn"
              onClick={() => { setView('input'); setLogs([]); }}
              style={{
                width: '100%', padding: '12px 0',
                borderRadius: 12, border: '1px solid rgba(255,255,255,0.08)',
                background: 'transparent', color: '#8892B0', cursor: 'pointer',
                fontSize: 13, fontFamily: 'Inter, sans-serif', transition: 'color 0.2s',
              }}
              onMouseOver={e => (e.currentTarget.style.color = '#FFFEF0')}
              onMouseOut={e  => (e.currentTarget.style.color = '#8892B0')}
            >
              ← Back to Input
            </button>
          </div>
        )}

        {/* ════ ERROR VIEW ════ */}
        {view === 'error' && (
          <div style={{ animation: 'fadeUp 0.3s ease-out' }}>
            <div className="card" style={{ marginBottom: 16, borderColor: 'rgba(255,107,107,0.3)', background: 'rgba(255,107,107,0.05)' }}>
              <p style={{ fontWeight: 700, color: '#FF6B6B', marginBottom: 10, fontSize: 14 }}>❌ Pipeline Error</p>
              <pre style={{ fontSize: 11, color: 'rgba(255,107,107,0.8)', fontFamily: 'monospace', whiteSpace: 'pre-wrap', lineHeight: 1.5 }}>
                {errorMsg}
              </pre>
              <p style={{ fontSize: 11, color: '#8892B0', marginTop: 12 }}>
                Make sure the orchestrator is running:{' '}
                <code style={{ color: '#3DCCC7' }}>./run_all.sh</code>
              </p>
            </div>
            <button
              id="retry-btn"
              className="btn-primary"
              onClick={() => setView('input')}
            >
              ← Start Over
            </button>
          </div>
        )}
      </div>
    </main>
  );
}
