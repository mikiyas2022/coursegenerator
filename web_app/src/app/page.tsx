'use client';

import { useState, useRef, useEffect, useCallback } from 'react';

// ── Types ──────────────────────────────────────────────────────────────────

interface FormState {
  topic:          string;
  audience:       string;
  style:          string;
  metaphor:       string;
  sourceMaterial: string;
  personaId:      number;
  orientation:    'landscape' | 'portrait';
}

interface StreamEvent {
  type:    string;
  payload: Record<string, unknown>;
}

interface SceneStep {
  scene_name:    string;
  concept:       string;
  explanation:   string;
  visual:        string;
  narrative_hook?: string;
  amharic_script?: string;
}

type Phase =
  | 'idle' | 'researching' | 'scripting' | 'coding'
  | 'rendering' | 'healing' | 'preview_ready' | 'complete' | 'error';

// ── Constants ──────────────────────────────────────────────────────────────

const PERSONAS = [
  { id: 1, key: 'mekdes',    icon: '👩‍🏫', name: 'Mekdes',    title: 'Warm Tutor',         badge: 'DEFAULT', color: 'emerald' },
  { id: 2, key: 'ameha',     icon: '👨‍🏫', name: 'Ameha',     title: 'Deep Expert',         badge: 'MALE',    color: 'blue'    },
  { id: 3, key: 'dawit',     icon: '⚡',   name: 'Dawit',     title: 'Energetic Coach',     badge: 'MALE',    color: 'blue'    },
  { id: 4, key: 'selamawit', icon: '📖',  name: 'Selamawit', title: 'Patient Professor',   badge: 'FEMALE',  color: 'pink'    },
  { id: 5, key: 'tigist',    icon: '🎓',  name: 'Tigist',    title: 'Bright Tutor',        badge: 'FEMALE',  color: 'pink'    },
];

const AUDIENCES  = ['Child (Grade 1–6)', 'High School (Grade 7–12)', 'University', 'Professional'];
const STYLES     = ['Playful / Storytelling', 'Formal / Academic', 'Inquiry-Based / 3b1b Style'];

const BADGE_COLORS: Record<string, string> = {
  emerald: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  blue:    'bg-blue-500/20 text-blue-400 border-blue-500/30',
  pink:    'bg-pink-500/20 text-pink-400 border-pink-500/30',
};

// ── Component ──────────────────────────────────────────────────────────────

export default function StudioPage() {
  const [mounted, setMounted] = useState(false);
  const [form, setForm] = useState<FormState>({
    topic:          '',
    audience:       'High School (Grade 7–12)',
    style:          'Inquiry-Based / 3b1b Style',
    metaphor:       '',
    sourceMaterial: '',
    personaId:      1,
    orientation:    'landscape',
  });

  const [phase,       setPhase]       = useState<Phase>('idle');
  const [events,      setEvents]      = useState<StreamEvent[]>([]);
  const [steps,       setSteps]       = useState<SceneStep[]>([]);
  const [scenes,      setScenes]      = useState<SceneStep[]>([]);
  const [codeCount,   setCodeCount]   = useState(0);
  const [healAttempt, setHealAttempt] = useState(0);
  const [previewPath, setPreviewPath] = useState('');
  const [outputFolder,setOutputFolder]= useState('');
  const [errorMsg,    setErrorMsg]    = useState('');
  const [showSource,  setShowSource]  = useState(false);

  const outputRef = useRef<HTMLDivElement>(null);

  useEffect(() => { setMounted(true); }, []);
  useEffect(() => {
    outputRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [events]);

  const setF = (k: keyof FormState, v: unknown) =>
    setForm(f => ({ ...f, [k]: v }));

  const handleGenerate = useCallback(async () => {
    if (!form.topic.trim()) return;

    // Reset
    setPhase('researching');
    setEvents([]);
    setSteps([]);
    setScenes([]);
    setCodeCount(0);
    setHealAttempt(0);
    setPreviewPath('');
    setOutputFolder('');
    setErrorMsg('');

    try {
      const res = await fetch('/api/create', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic:           form.topic,
          audience:        form.audience,
          style:           form.style,
          metaphor:        form.metaphor,
          source_material: form.sourceMaterial,
          persona_id:      form.personaId,
          orientation:     form.orientation,
        }),
      });

      if (!res.ok || !res.body) {
        const j = await res.json().catch(() => ({ error: 'Connection failed' }));
        throw new Error(j.error || 'Orchestrator unreachable');
      }

      const reader  = res.body.getReader();
      const decoder = new TextDecoder();
      let   buffer  = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() ?? '';

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          try {
            const ev: StreamEvent = JSON.parse(line.slice(6));
            setEvents(prev => [...prev, ev]);

            switch (ev.type) {
              case 'researcher_done':
                setPhase('scripting');
                setSteps((ev.payload.steps as SceneStep[]) || []);
                break;
              case 'script_done':
                setPhase('coding');
                setScenes((ev.payload.scenes as SceneStep[]) || []);
                break;
              case 'code_done':
                setPhase('rendering');
                setCodeCount((ev.payload.classes_count as number) || 0);
                break;
              case 'self_healing':
                setPhase('healing');
                setHealAttempt((ev.payload.attempt as number) || 1);
                break;
              case 'preview_ready':
                setPhase('preview_ready');
                setPreviewPath((ev.payload.preview_path as string) || '');
                setOutputFolder((ev.payload.output_folder as string) || '');
                break;
              case 'complete':
                setPhase('complete');
                setOutputFolder((ev.payload.output_folder as string) || '');
                break;
              case 'error':
                setPhase('error');
                setErrorMsg((ev.payload.message as string) || 'Unknown error');
                break;
            }
          } catch { /* skip malformed SSE line */ }
        }
      }
    } catch (err: unknown) {
      setPhase('error');
      setErrorMsg(err instanceof Error ? err.message : String(err));
    }
  }, [form]);

  const handleFinalRender = async () => {
    if (!outputFolder) return;
    try {
      const res = await fetch('http://localhost:8200/render_final', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ output_folder: outputFolder, orientation: form.orientation }),
      });
      const data = await res.json();
      if (data.success) {
        setPhase('complete');
      } else {
        setErrorMsg(data.error || 'Final render failed');
        setPhase('error');
      }
    } catch (e: unknown) {
      setErrorMsg(e instanceof Error ? e.message : String(e));
      setPhase('error');
    }
  };

  if (!mounted) return (
    <div className="min-h-screen bg-[#0B0E14] flex items-center justify-center">
      <div className="text-blue-500 font-mono animate-pulse text-sm tracking-widest">
        INITIALIZING AI STUDIO…
      </div>
    </div>
  );

  const isRunning = ['researching','scripting','coding','rendering','healing'].includes(phase);
  const selectedPersona = PERSONAS.find(p => p.id === form.personaId)!;

  return (
    <main className="min-h-screen bg-[#0B0E14] text-gray-100 font-sans" style={{ fontFamily: "'Inter', sans-serif" }}>
      {/* ── HEADER ─────────────────────────────────────────────────────── */}
      <header className="border-b border-white/5 bg-[#0D1117]/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center text-sm">🎬</div>
            <div>
              <h1 className="font-black text-white text-base tracking-tight">STEM AI Studio</h1>
              <p className="text-[10px] text-gray-500 tracking-widest uppercase">Autonomous Amharic Video Production</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className={`h-2 w-2 rounded-full ${isRunning ? 'bg-emerald-400 animate-pulse' : 'bg-gray-600'}`} />
            <span className="text-xs text-gray-500">{isRunning ? 'Generating…' : 'Ready'}</span>
          </div>
        </div>
      </header>

      {/* ── BODY ───────────────────────────────────────────────────────── */}
      <div className="max-w-7xl mx-auto px-6 py-8 grid grid-cols-1 xl:grid-cols-5 gap-8">

        {/* ══ LEFT — INPUT FORM ════════════════════════════════════════ */}
        <aside className="xl:col-span-2 space-y-6">

          {/* Topic */}
          <section className="rounded-2xl bg-white/[0.03] border border-white/[0.07] p-6">
            <label className="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-3">
              🎯 Core Topic / Concept
            </label>
            <textarea
              rows={3}
              placeholder="e.g. The Pythagorean Theorem, Newton's Laws of Motion, How DNA Replication Works…"
              value={form.topic}
              onChange={e => setF('topic', e.target.value)}
              className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-600 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition"
            />
          </section>

          {/* Audience + Style */}
          <section className="rounded-2xl bg-white/[0.03] border border-white/[0.07] p-6 space-y-4">
            <div>
              <label className="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">
                🎓 Target Audience
              </label>
              <select
                value={form.audience}
                onChange={e => setF('audience', e.target.value)}
                className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 appearance-none cursor-pointer transition"
              >
                {AUDIENCES.map(a => <option key={a} value={a}>{a}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">
                🎭 Narrative Style
              </label>
              <select
                value={form.style}
                onChange={e => setF('style', e.target.value)}
                className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 appearance-none cursor-pointer transition"
              >
                {STYLES.map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
          </section>

          {/* Visual Metaphor */}
          <section className="rounded-2xl bg-white/[0.03] border border-white/[0.07] p-6">
            <label className="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">
              🖼️ Visual Metaphor <span className="text-gray-700 normal-case font-normal">(optional)</span>
            </label>
            <input
              type="text"
              placeholder="e.g. 'Use building a house as the analogy', 'Abstract geometric 3b1b style'"
              value={form.metaphor}
              onChange={e => setF('metaphor', e.target.value)}
              className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition"
            />
          </section>

          {/* Source Material (collapsible) */}
          <section className="rounded-2xl bg-white/[0.03] border border-white/[0.07] p-6">
            <button
              type="button"
              onClick={() => setShowSource(s => !s)}
              className="flex items-center justify-between w-full text-left"
            >
              <label className="block text-xs font-bold text-gray-500 uppercase tracking-widest cursor-pointer">
                📄 Source Material <span className="text-gray-700 normal-case font-normal">(optional)</span>
              </label>
              <span className="text-gray-600 text-xs">{showSource ? '▲' : '▼'}</span>
            </button>
            {showSource && (
              <textarea
                rows={5}
                placeholder="Paste raw text, equations, or research notes. The AI will base the video on this."
                value={form.sourceMaterial}
                onChange={e => setF('sourceMaterial', e.target.value)}
                className="mt-3 w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-xs text-gray-300 placeholder-gray-700 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition font-mono"
              />
            )}
          </section>

          {/* Persona */}
          <section className="rounded-2xl bg-white/[0.03] border border-white/[0.07] p-6">
            <label className="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-4">
              🎙️ Voice Persona
            </label>
            <div className="grid grid-cols-1 gap-2">
              {PERSONAS.map(p => (
                <button
                  key={p.id}
                  type="button"
                  onClick={() => setF('personaId', p.id)}
                  className={`flex items-center gap-3 p-3 rounded-xl border text-left transition-all ${
                    form.personaId === p.id
                      ? 'border-blue-500 bg-blue-500/10'
                      : 'border-white/5 bg-black/20 hover:border-white/15'
                  }`}
                >
                  <span className="text-xl">{p.icon}</span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className={`text-sm font-bold ${form.personaId === p.id ? 'text-blue-300' : 'text-white'}`}>
                        {p.name}
                      </span>
                      <span className={`text-[9px] px-1.5 py-0.5 rounded border font-bold ${BADGE_COLORS[p.color]}`}>
                        {p.badge}
                      </span>
                    </div>
                    <p className="text-[11px] text-gray-600 truncate">{p.title}</p>
                  </div>
                  {form.personaId === p.id && (
                    <span className="text-blue-400 text-xs">✓</span>
                  )}
                </button>
              ))}
            </div>
          </section>

          {/* Orientation */}
          <section className="rounded-2xl bg-white/[0.03] border border-white/[0.07] p-6">
            <label className="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-4">
              📐 Orientation
            </label>
            <div className="grid grid-cols-2 gap-3">
              {(['landscape','portrait'] as const).map(mode => (
                <button
                  key={mode}
                  type="button"
                  onClick={() => setF('orientation', mode)}
                  className={`flex flex-col items-center gap-2 py-4 rounded-xl border-2 transition-all ${
                    form.orientation === mode
                      ? 'border-violet-500 bg-violet-500/10 text-violet-300'
                      : 'border-white/8 bg-black/20 text-gray-600 hover:border-white/15'
                  }`}
                >
                  <div className={`border-2 rounded flex items-center justify-center ${
                    form.orientation === mode ? 'border-violet-400' : 'border-gray-700'
                  } ${mode === 'landscape' ? 'w-14 h-9' : 'w-9 h-14'}`} />
                  <span className="text-[10px] font-bold uppercase tracking-widest">{mode}</span>
                  <span className="text-[9px] opacity-50">
                    {mode === 'landscape' ? '1920×1080' : '1080×1920'}
                  </span>
                </button>
              ))}
            </div>
          </section>

          {/* Generate Button */}
          <button
            type="button"
            disabled={isRunning || !form.topic.trim()}
            onClick={handleGenerate}
            className="w-full py-4 rounded-2xl font-black text-white uppercase tracking-widest text-sm transition-all duration-300 shadow-2xl
              bg-gradient-to-r from-blue-600 via-violet-600 to-blue-600 bg-[length:200%_100%]
              hover:bg-[position:100%_0] disabled:opacity-40 disabled:cursor-not-allowed
              flex items-center justify-center gap-3"
          >
            {isRunning ? (
              <>
                <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Generating…
              </>
            ) : (
              `🤖 Generate with ${selectedPersona.icon} ${selectedPersona.name}`
            )}
          </button>
        </aside>

        {/* ══ RIGHT — LIVE OUTPUT ═══════════════════════════════════════ */}
        <section className="xl:col-span-3 space-y-4" ref={outputRef}>

          {/* Phase Banner */}
          {phase !== 'idle' && (
            <PhaseBanner phase={phase} healAttempt={healAttempt} />
          )}

          {/* Researcher Output */}
          {steps.length > 0 && (
            <OutputCard icon="🔬" title="Learning Journey" color="blue">
              <div className="space-y-3">
                {steps.map((s, i) => (
                  <div key={i} className="flex gap-3 p-3 rounded-xl bg-black/30 border border-white/5">
                    <div className="w-6 h-6 rounded-full bg-blue-600 text-white text-xs font-black flex items-center justify-center flex-shrink-0 mt-0.5">
                      {i + 1}
                    </div>
                    <div>
                      <p className="text-sm font-bold text-blue-300">{s.concept || s.scene_name}</p>
                      <p className="text-xs text-gray-500 mt-0.5 leading-relaxed">{s.explanation}</p>
                      {s.visual && (
                        <p className="text-[11px] text-violet-400 mt-1 italic">📹 {s.visual}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </OutputCard>
          )}

          {/* Scriptwriter Output */}
          {scenes.length > 0 && (
            <OutputCard icon="✍️" title="Amharic Script" color="emerald">
              <div className="space-y-3">
                {scenes.map((s, i) => (
                  <div key={i} className="p-4 rounded-xl bg-black/30 border border-white/5">
                    <p className="text-[10px] font-bold text-gray-600 uppercase tracking-widest mb-2">
                      {s.scene_name}
                    </p>
                    <p className="text-base text-emerald-200 leading-relaxed" style={{ fontFamily: "'Nyala', serif" }}>
                      {s.amharic_script || '…'}
                    </p>
                  </div>
                ))}
              </div>
            </OutputCard>
          )}

          {/* Manim Coder Output */}
          {codeCount > 0 && (
            <OutputCard icon="⚙️" title={`Manim Code Generated`} color="violet">
              <div className="flex items-center gap-3 p-4 bg-black/30 rounded-xl border border-white/5">
                <span className="text-3xl">🐍</span>
                <div>
                  <p className="text-sm font-bold text-violet-300">{codeCount} VoiceoverScene class{codeCount > 1 ? 'es' : ''}</p>
                  <p className="text-xs text-gray-500">With LocalMMSService + tracker.duration sync</p>
                </div>
              </div>
            </OutputCard>
          )}

          {/* Self-Healing */}
          {phase === 'healing' && (
            <OutputCard icon="🔧" title="Self-Healing Critic" color="yellow">
              <div className="p-4 bg-yellow-950/30 rounded-xl border border-yellow-500/20">
                <p className="text-sm text-yellow-400 font-bold">Attempt {healAttempt}/3</p>
                <p className="text-xs text-gray-500 mt-1">
                  Manim traceback detected. The AI is reading the error and rewriting the code…
                </p>
                <div className="flex items-center gap-2 mt-3">
                  {[0,1,2].map(i => (
                    <div
                      key={i}
                      className={`h-1.5 flex-1 rounded-full transition-all ${
                        i < healAttempt ? 'bg-yellow-400' : 'bg-white/10'
                      }`}
                    />
                  ))}
                </div>
              </div>
            </OutputCard>
          )}

          {/* Preview Ready */}
          {(phase === 'preview_ready' || phase === 'complete') && (
            <OutputCard icon="🎬" title="Preview Ready" color="emerald">
              <div className="space-y-4">
                <div className="p-4 bg-emerald-950/30 rounded-xl border border-emerald-500/20">
                  <p className="text-sm font-bold text-emerald-300">✅ Low-quality preview rendered!</p>
                  {previewPath && (
                    <p className="text-[11px] text-gray-600 font-mono mt-2 break-all">{previewPath}</p>
                  )}
                </div>

                {outputFolder && (
                  <button
                    type="button"
                    onClick={handleFinalRender}
                    className="w-full py-3 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 font-bold text-white text-sm transition-all shadow-lg shadow-emerald-500/20 flex items-center justify-center gap-2"
                  >
                    🚀 Render Final 4K Video
                  </button>
                )}
              </div>
            </OutputCard>
          )}

          {/* Final Complete */}
          {phase === 'complete' && outputFolder && (
            <OutputCard icon="🏆" title="Production Complete" color="blue">
              <div className="p-4 bg-blue-950/30 rounded-xl border border-blue-500/20">
                <p className="text-sm font-bold text-blue-300">Your video is ready!</p>
                <p className="text-[11px] font-mono text-gray-500 mt-2 break-all">{outputFolder}</p>
              </div>
            </OutputCard>
          )}

          {/* Error */}
          {phase === 'error' && (
            <OutputCard icon="❌" title="Error" color="red">
              <div className="p-4 bg-red-950/30 rounded-xl border border-red-500/20">
                <p className="text-xs text-red-400 font-mono whitespace-pre-wrap">{errorMsg}</p>
                <p className="text-[11px] text-gray-600 mt-3">
                  Make sure the orchestrator is running: <code className="text-blue-400">./run_all.sh</code>
                </p>
              </div>
            </OutputCard>
          )}

          {/* Idle state */}
          {phase === 'idle' && (
            <div className="flex flex-col items-center justify-center py-24 text-center text-gray-700 space-y-4">
              <div className="text-6xl opacity-20">🎬</div>
              <div>
                <p className="font-bold text-gray-500">AI Studio is ready</p>
                <p className="text-sm mt-1">Enter a topic and click Generate to begin.</p>
                <p className="text-xs mt-3 font-mono text-gray-700">
                  TTS :8100 • Orchestrator :8200 • Frontend :3011
                </p>
              </div>
            </div>
          )}
        </section>
      </div>
    </main>
  );
}

// ── Sub-Components ─────────────────────────────────────────────────────────

function PhaseBanner({ phase, healAttempt }: { phase: Phase; healAttempt: number }) {
  const configs: Record<Phase, { icon: string; label: string; color: string }> = {
    idle:          { icon: '○',  label: 'Idle',                          color: 'gray'    },
    researching:   { icon: '🔬', label: 'Researcher analyzing topic…',   color: 'blue'    },
    scripting:     { icon: '✍️', label: 'Writing Amharic script…',       color: 'emerald' },
    coding:        { icon: '⚙️', label: 'Manim Developer coding…',       color: 'violet'  },
    rendering:     { icon: '🎞️', label: 'Rendering preview…',            color: 'blue'    },
    healing:       { icon: '🔧', label: `Self-healing attempt ${healAttempt}/3…`, color: 'yellow' },
    preview_ready: { icon: '🎬', label: 'Preview ready!',                color: 'emerald' },
    complete:      { icon: '✅', label: 'Production complete!',           color: 'emerald' },
    error:         { icon: '❌', label: 'Error occurred',                 color: 'red'     },
  };

  const c = configs[phase];
  const colorMap: Record<string, string> = {
    blue:    'border-blue-500/30 bg-blue-950/30 text-blue-300',
    emerald: 'border-emerald-500/30 bg-emerald-950/30 text-emerald-300',
    violet:  'border-violet-500/30 bg-violet-950/30 text-violet-300',
    yellow:  'border-yellow-500/30 bg-yellow-950/30 text-yellow-300',
    red:     'border-red-500/30 bg-red-950/30 text-red-300',
    gray:    'border-white/10 bg-white/5 text-gray-400',
  };

  const isRunning = ['researching','scripting','coding','rendering','healing'].includes(phase);

  return (
    <div className={`flex items-center gap-3 px-5 py-3 rounded-2xl border ${colorMap[c.color]}`}>
      {isRunning
        ? <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
        : <span>{c.icon}</span>
      }
      <span className="text-sm font-semibold">{c.label}</span>
    </div>
  );
}

function OutputCard({
  icon, title, color, children,
}: {
  icon: string;
  title: string;
  color: 'blue' | 'emerald' | 'violet' | 'yellow' | 'red';
  children: React.ReactNode;
}) {
  const borders: Record<string, string> = {
    blue:    'border-blue-500/20',
    emerald: 'border-emerald-500/20',
    violet:  'border-violet-500/20',
    yellow:  'border-yellow-500/20',
    red:     'border-red-500/20',
  };
  const headers: Record<string, string> = {
    blue:    'text-blue-400',
    emerald: 'text-emerald-400',
    violet:  'text-violet-400',
    yellow:  'text-yellow-400',
    red:     'text-red-400',
  };

  return (
    <div className={`rounded-2xl bg-white/[0.02] border ${borders[color]} overflow-hidden`}
         style={{ animation: 'fadeSlideIn 0.3s ease-out' }}>
      <div className="px-5 py-4 border-b border-white/5">
        <h3 className={`text-sm font-bold ${headers[color]} flex items-center gap-2`}>
          <span>{icon}</span> {title}
        </h3>
      </div>
      <div className="p-5">{children}</div>
      <style>{`
        @keyframes fadeSlideIn {
          from { opacity: 0; transform: translateY(8px); }
          to   { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
}
