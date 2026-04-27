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
  mode:           '3b1b' | 'blackboard';
  correctAnswer?: string;
  showFinalAnswer?: boolean;
}

interface StoryboardScene {
  scene_name:     string;
  concept:        string;
  explanation:    string;
  visual:         string;
  amharic_script: string;
  sentences:      string[];
  latex_formulas: string[];
  narrative_hook?: string;
}

interface StreamEvent {
  type:    string;
  payload: Record<string, unknown>;
}

type UIView =
  | 'input'
  | 'planning'           // Researcher + Scriptwriter running
  | 'storyboard'         // Editable storyboard cards
  | 'rendering'          // Manim Coder + Critic running
  | 'full_auto'          // One-shot full automation
  | 'preview_ready'
  | 'complete'
  | 'error';

// ── Constants ──────────────────────────────────────────────────────────────

const PERSONAS = [
  { id: 1, icon: '👩‍🏫', name: 'Mekdes',    badge: 'FEMALE · WARM',   color: 'emerald', desc: 'Higher pitched, warm female tutor voice' },
  { id: 2, icon: '👨‍🏫', name: 'Ameha',     badge: 'MALE · DEEP',     color: 'blue',    desc: 'Deep, authoritative male voice' },
  { id: 3, icon: '⚡',   name: 'Dawit',     badge: 'MALE · ENERGY',   color: 'blue',    desc: 'Energetic, upbeat coaching voice' },
  { id: 4, icon: '📖',  name: 'Selamawit', badge: 'FEMALE · CALM',   color: 'emerald', desc: 'Patient, methodical professor voice' },
  { id: 5, icon: '🎓',  name: 'Tigist',    badge: 'FEMALE · BRIGHT', color: 'emerald', desc: 'Bright, younger female tutor' },
];
const AUDIENCES = [
  'Kindergarten (Playful/Animated)',
  'Child (Grade 1–6)',
  'Middle School (Curious & Fun)',
  'High School (Exploratory)',
  'University (Rigorous / Academic)',
  'Professional',
  'General Public (Edutainment)',
];
const STYLES = [
  'Seductive & Addictive (High-Retention)',
  'World-Class 3b1b (Deep Visual Insight)',
  'Playful & Expressive Storytelling',
  'Smooth Professional Flawless',
  'Inquiry-Based',
  'Formal / Academic'
];
const BADGE     : Record<string, string> = {
  emerald: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  blue:    'bg-blue-500/20 text-blue-400 border-blue-500/30',
  pink:    'bg-pink-500/20 text-pink-400 border-pink-500/30',
};
const SCENE_COLORS = ['#1E3A8A','#065F46','#6D28D9','#92400E','#1E40AF','#064E3B'];

// ── Main Component ─────────────────────────────────────────────────────────

export default function StudioPage() {
  const [mounted,       setMounted]       = useState(false);
  const [activeTab,     setActiveTab]     = useState<'3b1b' | 'blackboard'>('3b1b');
  const [view,          setView]          = useState<UIView>('input');
  const [form,          setForm]          = useState<FormState>({
    topic: '', audience: 'High School (Exploratory)',
    style: 'World-Class 3b1b (Deep Visual Insight)', metaphor: '',
    sourceMaterial: '', personaId: 1, orientation: 'landscape',
    mode: '3b1b',
    correctAnswer: '',
    showFinalAnswer: true
  });

  // Storyboard data (editable)
  const [scenes,        setScenes]        = useState<StoryboardScene[]>([]);

  // Render phase
  const [renderEvents,  setRenderEvents]  = useState<StreamEvent[]>([]);
  const [previewPath,   setPreviewPath]   = useState('');
  const [outputFolder,  setOutputFolder]  = useState('');
  const [masterPath,    setMasterPath]    = useState('');
  const [errorMsg,      setErrorMsg]      = useState('');
  const [statusMsg,     setStatusMsg]     = useState('');
  const [planningLogs,  setPlanningLogs]  = useState<{msg: string, time: string}[]>([]);
  const [healAttempt,   setHealAttempt]   = useState(0);
  const [visualFeedback,setVisualFeedback]= useState('');
  const [showSource,    setShowSource]    = useState(false);
  const [fullAutoLogs,  setFullAutoLogs]  = useState<{msg: string, phase: string, time: string}[]>([]);

  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => { setMounted(true); }, []);
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [renderEvents]);

  const setF = (k: keyof FormState, v: unknown) =>
    setForm(f => ({ ...f, [k]: v }));

  // ── Scene editing ──────────────────────────────────────────────────────
  const updateScene = (idx: number, field: keyof StoryboardScene, value: unknown) =>
    setScenes(prev => prev.map((s, i) => i === idx ? { ...s, [field]: value } : s));

  const updateLatex = (idx: number, value: string) =>
    updateScene(idx, 'latex_formulas', value.split(',').map(s => s.trim()).filter(Boolean));

  // ── Phase 1: Generate Storyboard ──────────────────────────────────────
  const generateStoryboard = useCallback(async () => {
    if (!form.topic.trim()) return;
    setView('planning');
    setScenes([]);
    setErrorMsg('');
    setStatusMsg('Researcher is analyzing your topic…');
    setPlanningLogs([{ msg: 'Researcher is analyzing your topic…', time: new Date().toLocaleTimeString() }]);

    try {
      const res = await fetch('/api/storyboard', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic:           form.topic,
          audience:        form.audience,
          style:           form.style,
          metaphor:        form.metaphor,
          source_material: form.sourceMaterial,
        }),
      });

      if (!res.body) throw new Error('No response stream');
      const reader  = res.body.getReader();
      const decoder = new TextDecoder();
      let   buf     = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buf += decoder.decode(value, { stream: true });
        const lines = buf.split('\n');
        buf = lines.pop() ?? '';

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          try {
            const ev: StreamEvent = JSON.parse(line.slice(6));
            if (ev.type === 'status' || ev.type === 'ping') {
              if (ev.payload && (ev.payload.message as string)) {
                const msg = ev.payload.message as string;
                setStatusMsg(msg);
                setPlanningLogs(prev => {
                  // Avoid duplicate spam
                  if (prev.length > 0 && prev[prev.length - 1].msg === msg) return prev;
                  return [...prev, { msg, time: new Date().toLocaleTimeString() }];
                });
              }
            }
            if (ev.type === 'researcher_done') {
              // The status event will handle this now naturally
            }
            if (ev.type === 'storyboard_ready') {
              const incoming = (ev.payload.scenes as StoryboardScene[]) || [];
              setScenes(incoming);
              setView('storyboard');
            }
            if (ev.type === 'error') {
              setErrorMsg((ev.payload.message as string) || 'Unknown error');
              setView('error');
            }
          } catch { /* ignore bad lines */ }
        }
      }
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : String(err));
      setView('error');
    }
  }, [form]);

  // ── Full Automation (one-shot) ────────────────────────────────────────────
  const generateFullVideo = useCallback(async (modeArg: '3b1b' | 'blackboard' = '3b1b') => {
    if (!form.topic.trim()) return;
    setF('mode', modeArg);
    setView('full_auto');
    setFullAutoLogs([{ msg: '🚀 Starting full 3B1B pipeline…', phase: 'init', time: new Date().toLocaleTimeString() }]);
    setMasterPath('');
    setErrorMsg('');

    const addLog = (msg: string, phase: string) =>
      setFullAutoLogs(prev => [...prev, { msg, phase, time: new Date().toLocaleTimeString() }]);

    try {
      const res = await fetch('/api/generate-full', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic:           form.topic,
          audience:        form.audience,
          style:           form.style,
          metaphor:        form.metaphor,
          source_material: form.sourceMaterial,
          persona_id:      form.personaId,
          orientation:     form.orientation,
          run_postprod:    true,
          mode:            modeArg,
          // Blackboard-specific fields
          question:        modeArg === 'blackboard' ? form.topic : '',
          correct_answer:  modeArg === 'blackboard' ? (form.correctAnswer || '') : '',
          subject_grade:   modeArg === 'blackboard' ? (form.metaphor || '') : '',
          silent:          modeArg === 'blackboard',
          tts_enabled:     modeArg !== 'blackboard',
        }),
      });
      if (!res.body) throw new Error('No stream');
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buf = '';
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buf += decoder.decode(value, { stream: true });
        const lines = buf.split('\n');
        buf = lines.pop() ?? '';
        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          try {
            const ev = JSON.parse(line.slice(6)) as StreamEvent;
            const msg = (ev.payload.message as string) || ev.type;
            const phase = (ev.payload.phase as string) || ev.type;
            if (ev.type !== 'ping') addLog(msg, phase);
            if (ev.type === 'complete') {
              setMasterPath((ev.payload.master_path as string) || (ev.payload.output_folder as string) || '');
              setOutputFolder((ev.payload.output_folder as string) || '');
              setView('complete');
            }
            if (ev.type === 'error') {
              setErrorMsg(msg);
              setView('error');
            }
          } catch { /* ignore */ }
        }
      }
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : String(err));
      setView('error');
    }
  }, [form]);

  // ── Phase 2: Approve & Render ──────────────────────────────────────────
  const approveAndRender = useCallback(async () => {
    setView('rendering');
    setRenderEvents([]);
    setPreviewPath('');
    setOutputFolder('');
    setHealAttempt(0);
    setVisualFeedback('');
    setErrorMsg('');

    try {
      const res = await fetch('/api/render', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          scenes:      scenes,
          persona_id:  form.personaId,
          orientation: form.orientation,
        }),
      });

      if (!res.body) throw new Error('No response stream');
      const reader  = res.body.getReader();
      const decoder = new TextDecoder();
      let   buf     = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buf += decoder.decode(value, { stream: true });
        const lines = buf.split('\n');
        buf = lines.pop() ?? '';

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          try {
            const ev: StreamEvent = JSON.parse(line.slice(6));
            setRenderEvents(prev => [...prev, ev]);
            switch (ev.type) {
              case 'self_healing':
                setHealAttempt((ev.payload.attempt as number) || 1); break;
              case 'visual_critique':
                setVisualFeedback((ev.payload.feedback as string) || ''); break;
              case 'preview_ready':
                setPreviewPath((ev.payload.preview_path as string) || '');
                setOutputFolder((ev.payload.output_folder as string) || '');
                setView('preview_ready'); break;
              case 'complete':
                setOutputFolder((ev.payload.output_folder as string) || '');
                setView('complete'); break;
              case 'error':
                setErrorMsg((ev.payload.message as string) || 'Unknown error');
                setView('error'); break;
            }
          } catch { /* ignore */ }
        }
      }
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : String(err));
      setView('error');
    }
  }, [scenes, form]);

  // ── Phase 3: Final 4K Render ──────────────────────────────────────────
  const renderFinal = async () => {
    if (!outputFolder) return;
    try {
      const res = await fetch('http://localhost:8205/render_final', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ output_folder: outputFolder, orientation: form.orientation }),
      });
      const data = await res.json();
      if (data.success) setView('complete');
      else { setErrorMsg(data.error || 'Final render failed'); setView('error'); }
    } catch (e: unknown) {
      setErrorMsg(e instanceof Error ? e.message : String(e));
      setView('error');
    }
  };

  if (!mounted) return (
    <div className="min-h-screen bg-[#0B0E14] flex items-center justify-center">
      <div className="text-blue-500 font-mono animate-pulse text-xs tracking-widest">INITIALIZING AI STUDIO…</div>
    </div>
  );

  const persona = PERSONAS.find(p => p.id === form.personaId)!;
  const isRunning = view === 'planning' || view === 'rendering';

  // ════════════════════════════════════════════════════════════
  return (
    <main className="min-h-screen bg-[#0B0E14] text-gray-100" style={{ fontFamily: "'Inter', sans-serif" }}>

      {/* ── HEADER ─────────────────────────────────────────────────── */}
      <header className="sticky top-0 z-50 border-b border-white/5 bg-[#0B0E14]/90 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center text-xs">🎬</div>
            <div>
              <p className="font-black text-white text-sm tracking-tight">STEM AI Studio</p>
              <p className="text-[9px] text-gray-600 uppercase tracking-widest">Autonomous Amharic Video Production</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            {/* Phase breadcrumb */}
            <div className="hidden sm:flex items-center gap-1 text-[10px]">
              {(['input','storyboard','rendering','complete'] as const).map((v, i, arr) => (
                <span key={v} className="flex items-center gap-1">
                  <span className={`px-2 py-0.5 rounded-full font-bold ${
                    view === v || (view === 'planning' && v === 'storyboard') || (view === 'preview_ready' && v === 'rendering')
                      ? 'bg-blue-600 text-white'
                      : ['complete','preview_ready'].includes(view) && i < arr.length
                        ? 'bg-emerald-900/50 text-emerald-400'
                        : 'bg-white/5 text-gray-600'
                  }`}>
                    {v === 'input' ? '1. Input' : v === 'storyboard' ? '2. Storyboard' : v === 'rendering' ? '3. Render' : '4. Done'}
                  </span>
                  {i < arr.length - 1 && <span className="text-gray-700">›</span>}
                </span>
              ))}
            </div>
            <div className="flex items-center gap-1.5">
              <span className={`w-1.5 h-1.5 rounded-full ${isRunning ? 'bg-emerald-400 animate-pulse' : 'bg-gray-600'}`} />
              <span className="text-[10px] text-gray-500">{isRunning ? 'Running…' : 'Idle'}</span>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">

        {/* ════ VIEW: INPUT ════════════════════════════════════════════ */}
        {view === 'input' && (
          <div className="max-w-2xl mx-auto space-y-5">
            <div className="text-center mb-8">
              <h1 className="text-3xl font-black bg-gradient-to-r from-blue-400 to-violet-400 bg-clip-text text-transparent">
                Create an Amharic STEM Video
              </h1>
              <p className="text-gray-500 text-sm mt-2">The AI will research, script, and animate your topic automatically.</p>
            </div>

            {/* TABS */}
            <div className="flex bg-black/40 p-1 rounded-xl border border-white/10 mb-8">
              <button
                onClick={() => { setActiveTab('3b1b'); setF('mode', '3b1b'); }}
                className={`flex-1 py-3 text-sm font-bold rounded-lg transition-all ${
                  activeTab === '3b1b' ? 'bg-gradient-to-r from-blue-600 to-violet-600 text-white shadow-lg shadow-blue-500/20' : 'text-gray-500 hover:text-gray-300'
                }`}
              >
                🎬 3B1B Explanatory Videos
              </button>
              <button
                onClick={() => { setActiveTab('blackboard'); setF('mode', 'blackboard'); }}
                className={`flex-1 py-3 text-sm font-bold rounded-lg transition-all ${
                  activeTab === 'blackboard' ? 'bg-gradient-to-r from-emerald-600 to-teal-600 text-white shadow-lg shadow-emerald-500/20' : 'text-gray-500 hover:text-gray-300'
                }`}
              >
                ✍️ Blackboard Q&A Solutions (EUEE)
              </button>
            </div>

            {activeTab === '3b1b' ? (
              <div className="space-y-5 animate-fade-in">
                <Card>
                  <Label>🎯 Topic / Concept</Label>
                  <textarea
                    rows={3}
                    placeholder="e.g. The Pythagorean Theorem, Newton's Laws of Motion…"
                    value={form.topic}
                    onChange={e => setF('topic', e.target.value)}
                    className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-600 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition"
                  />
                </Card>

            <div className="grid grid-cols-2 gap-4">
              <Card>
                <Label>🎓 Audience</Label>
                <Select value={form.audience} onChange={e => setF('audience', e.target.value)}>
                  {AUDIENCES.map(a => <option key={a}>{a}</option>)}
                </Select>
              </Card>
              <Card>
                <Label>🎭 Style</Label>
                <Select value={form.style} onChange={e => setF('style', e.target.value)}>
                  {STYLES.map(s => <option key={s}>{s}</option>)}
                </Select>
              </Card>
            </div>

            <Card>
              <Label>🖼️ Visual Metaphor <span className="text-gray-700 normal-case font-normal text-[11px]">(optional)</span></Label>
              <input
                type="text"
                placeholder="e.g. 'Use a building construction analogy', 'Abstract 3b1b style'"
                value={form.metaphor}
                onChange={e => setF('metaphor', e.target.value)}
                className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition"
              />
            </Card>

            <Card>
              <button type="button" onClick={() => setShowSource(s => !s)}
                className="flex items-center justify-between w-full text-left">
                <Label>📄 Source Material <span className="text-gray-700 normal-case font-normal text-[11px]">(optional)</span></Label>
                <span className="text-gray-600 text-xs">{showSource ? '▲' : '▼'}</span>
              </button>
              {showSource && (
                <textarea rows={4} value={form.sourceMaterial}
                  onChange={e => setF('sourceMaterial', e.target.value)}
                  placeholder="Paste raw text, equations, or research notes…"
                  className="mt-3 w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-xs text-gray-300 placeholder-gray-700 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition font-mono" />
              )}
            </Card>

            <div className="grid grid-cols-5 gap-2">
              {PERSONAS.map(p => (
                <button key={p.id} type="button" onClick={() => setF('personaId', p.id)}
                  className={`flex flex-col items-center gap-1.5 p-3 rounded-xl border transition-all ${
                    form.personaId === p.id ? 'border-blue-500 bg-blue-500/10' : 'border-white/5 bg-black/20 hover:border-white/15'}`}>
                  <span className="text-xl">{p.icon}</span>
                  <span className={`text-[10px] font-bold ${form.personaId === p.id ? 'text-blue-300' : 'text-gray-500'}`}>{p.name}</span>
                  <span className={`text-[9px] px-1.5 py-0.5 rounded border font-bold ${BADGE[p.color]}`}>{p.badge}</span>
                  <span className="text-[8px] text-gray-600 text-center leading-tight">{p.desc}</span>
                </button>
              ))}
            </div>

            <div className="grid grid-cols-2 gap-3">
              {(['landscape','portrait'] as const).map(mode => (
                <button key={mode} type="button" onClick={() => setF('orientation', mode)}
                  className={`flex flex-col items-center gap-2 py-4 rounded-xl border-2 transition-all ${
                    form.orientation === mode ? 'border-violet-500 bg-violet-500/10 text-violet-300' : 'border-white/8 bg-black/20 text-gray-600 hover:border-white/15'}`}>
                  <div className={`border-2 rounded ${form.orientation === mode ? 'border-violet-400' : 'border-gray-700'} ${mode === 'landscape' ? 'w-12 h-8' : 'w-8 h-12'}`} />
                  <span className="text-[10px] font-bold uppercase tracking-widest">{mode}</span>
                </button>
              ))}
            </div>

              {/* One-shot full automation button */}
              <button type="button" disabled={!form.topic.trim()}
                onClick={() => generateFullVideo('3b1b')}
                className="w-full py-4 rounded-2xl bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-400 hover:to-orange-400 font-black text-black text-sm uppercase tracking-widest transition-all shadow-xl shadow-yellow-500/30 disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2">
                ⚡ Generate 3B1B Video (Auto)
              </button>
              
              <p className="text-center text-[10px] text-gray-600">↑ Zero human intervention — full pipeline runs automatically</p>

              {/* Manual storyboard flow */}
              <button type="button" disabled={!form.topic.trim()}
                onClick={generateStoryboard}
                className="w-full py-3 rounded-2xl bg-gradient-to-r from-blue-600/60 to-violet-600/60 hover:from-blue-500/80 hover:to-violet-500/80 font-bold text-white text-sm uppercase tracking-widest transition-all border border-blue-500/30 disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2">
                🤖 Generate Storyboard (Manual Review)
              </button>
              </div>
            ) : (
              <div className="space-y-5 animate-fade-in">
                <Card>
                  <Label>📝 Exam Question (Amharic + LaTeX)</Label>
                  <textarea
                    rows={4}
                    placeholder="e.g. Physics Grade 12 EUEE 2025: A 10kg block slides..."
                    value={form.topic}
                    onChange={e => setF('topic', e.target.value)}
                    className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-600 resize-none focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition"
                  />
                </Card>

                <Card>
                  <Label>✅ Optional Final Answer</Label>
                  <input
                    type="text"
                    placeholder="e.g. '42 m/s^2'"
                    value={form.correctAnswer || ''}
                    onChange={e => setF('correctAnswer', e.target.value)}
                    className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition"
                  />
                  <label className="flex items-center gap-2 mt-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={form.showFinalAnswer}
                      onChange={e => setF('showFinalAnswer', e.target.checked)}
                      className="w-4 h-4 rounded border-white/10 bg-black/40 text-emerald-500 focus:ring-emerald-500/50"
                    />
                    <span className="text-sm text-gray-400">Show final answer at the end</span>
                  </label>
                </Card>

                <Card>
                  <Label>📚 Subject & Grade (Optional)</Label>
                  <input
                    type="text"
                    placeholder="e.g. 'Physics Grade 12 EUEE 2025'"
                    value={form.metaphor}
                    onChange={e => setF('metaphor', e.target.value)}
                    className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition"
                  />
                </Card>
                
                <button type="button" disabled={!form.topic.trim()}
                  onClick={() => generateFullVideo('blackboard')}
                  className="w-full py-4 rounded-2xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 font-black text-white text-sm uppercase tracking-widest transition-all shadow-xl shadow-emerald-500/30 disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2">
                  ✍️ Generate Blackboard Q&A
                </button>
                <p className="text-center text-[10px] text-gray-600">Silent, realistic chalk simulation — high-quality step-by-step solver</p>
              </div>
            )}
          </div>
        )}

        {/* ════ VIEW: PLANNING (streaming) ═════════════════════════════ */}
        {view === 'planning' && (
          <div className="max-w-2xl mx-auto flex flex-col py-16 space-y-8">
            <div className="flex flex-col items-center justify-center text-center space-y-4">
              <div className="w-16 h-16 rounded-full border-4 border-blue-500 border-t-transparent animate-spin" />
              <div>
                <p className="text-xl font-black text-white">{statusMsg}</p>
                <p className="text-sm text-gray-400 mt-2">Qwen is researching and writing your Amharic script…</p>
              </div>
            </div>

            {/* Stepper / Terminal Feed */}
            <div className="w-full bg-black/60 rounded-2xl border border-white/10 overflow-hidden shadow-2xl">
              <div className="bg-white/5 border-b border-white/5 px-4 py-2 flex items-center justify-between">
                <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Live Execution Log</span>
              </div>
              <div className="p-4 flex flex-col gap-3 max-h-[300px] overflow-y-auto">
                {planningLogs.map((log, i) => (
                  <div key={i} className="flex gap-4 items-start animate-fade-in">
                    <div className="flex flex-col items-center mt-1">
                      <div className={`w-3 h-3 rounded-full flex-shrink-0 ${i === planningLogs.length - 1 ? 'bg-blue-500 animate-pulse' : 'bg-emerald-500'}`} />
                      {i < planningLogs.length - 1 && <div className="w-0.5 h-full bg-white/10 mt-2 mb-1" />}
                    </div>
                    <div className="flex-1 pb-2">
                      <p className={`text-sm ${i === planningLogs.length - 1 ? 'text-white font-bold' : 'text-gray-400'}`}>{log.msg}</p>
                      <p className="text-[10px] text-gray-600 font-mono mt-0.5">{log.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ════ VIEW: STORYBOARD (editable cards) ══════════════════════ */}
        {view === 'storyboard' && (
          <div className="space-y-6">
            {/* Header bar */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-white/5">
              <div>
                <h2 className="text-xl font-black text-white">📋 Storyboard Review</h2>
                <p className="text-sm text-gray-500 mt-1">
                  Review and edit the AI-generated script before rendering. Click any field to modify it.
                </p>
              </div>
              <div className="flex gap-3">
                <button onClick={() => setView('input')}
                  className="px-5 py-2.5 rounded-xl border border-white/10 text-sm text-gray-400 hover:border-white/20 transition">
                  ← Back
                </button>
                <button onClick={approveAndRender}
                  className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 font-bold text-white text-sm transition-all shadow-lg shadow-emerald-500/20 flex items-center gap-2">
                  ✅ Approve &amp; Render {persona.icon}
                </button>
              </div>
            </div>

            {/* Scene cards */}
            <div className="space-y-5">
              {scenes.map((scene, idx) => (
                <div key={scene.scene_name}
                  className="rounded-2xl border border-white/[0.07] overflow-hidden"
                  style={{ animation: `fadeSlideIn 0.3s ease-out ${idx * 0.05}s both` }}>

                  {/* Card header */}
                  <div className="px-6 py-4 flex items-center gap-4"
                    style={{ background: `${SCENE_COLORS[idx % SCENE_COLORS.length]}22`, borderBottom: `1px solid ${SCENE_COLORS[idx % SCENE_COLORS.length]}33` }}>
                    <div className="w-8 h-8 rounded-full flex items-center justify-center font-black text-sm text-white flex-shrink-0"
                      style={{ background: SCENE_COLORS[idx % SCENE_COLORS.length] }}>
                      {idx + 1}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs text-gray-500 uppercase tracking-widest">{scene.scene_name}</p>
                      <p className="font-bold text-white truncate">{scene.concept}</p>
                    </div>
                    <span className="text-[10px] text-gray-600 hidden sm:block">{scene.explanation?.slice(0, 80)}…</span>
                  </div>

                  {/* Editable fields */}
                  <div className="p-6 grid grid-cols-1 lg:grid-cols-2 gap-6 bg-white/[0.01]">

                    {/* Amharic Script */}
                    <div>
                      <label className="block text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-2">
                        ✍️ Amharic Script <span className="text-blue-500">(editable)</span>
                      </label>
                      <textarea
                        rows={5}
                        value={scene.amharic_script}
                        onChange={e => updateScene(idx, 'amharic_script', e.target.value)}
                        className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-base text-emerald-200 placeholder-gray-700 resize-none focus:outline-none focus:ring-2 focus:ring-emerald-500/40 transition leading-relaxed"
                        style={{ fontFamily: "'Nyala', serif", fontSize: '16px' }}
                      />
                    </div>

                    {/* Visual Plan */}
                    <div className="space-y-4">
                      <div>
                        <label className="block text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-2">
                          📹 Visual Plan <span className="text-blue-500">(editable)</span>
                        </label>
                        <textarea
                          rows={3}
                          value={scene.visual}
                          onChange={e => updateScene(idx, 'visual', e.target.value)}
                          className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-sm text-violet-300 placeholder-gray-700 resize-none focus:outline-none focus:ring-2 focus:ring-violet-500/40 transition"
                        />
                      </div>
                      <div>
                        <label className="block text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-2">
                          🧮 LaTeX Formulas <span className="text-gray-700 font-normal">(comma-separated)</span>
                        </label>
                        <input
                          type="text"
                          value={scene.latex_formulas?.join(', ') || ''}
                          onChange={e => updateLatex(idx, e.target.value)}
                          placeholder="e.g. F = ma, E = mc^2"
                          className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-2.5 text-sm font-mono text-yellow-300 placeholder-gray-700 focus:outline-none focus:ring-2 focus:ring-yellow-500/40 transition"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Bottom approve */}
            <div className="sticky bottom-6 pt-4">
              <div className="max-w-md mx-auto bg-[#0B0E14]/90 backdrop-blur-md rounded-2xl border border-white/10 p-4 flex items-center gap-4">
                <div className="flex-1">
                  <p className="text-sm font-bold text-white">{scenes.length} scenes ready</p>
                  <p className="text-[11px] text-gray-500">Review complete? Approve to start rendering.</p>
                </div>
                <button onClick={approveAndRender}
                  className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 font-bold text-white text-sm transition-all shadow-lg shadow-emerald-500/20 whitespace-nowrap flex items-center gap-2">
                  ✅ Approve &amp; Render
                </button>
              </div>
            </div>
          </div>
        )}

        {/* ════ VIEW: RENDERING ════════════════════════════════════════ */}
        {(view === 'rendering' || view === 'preview_ready' || view === 'complete') && (
          <div className="max-w-2xl mx-auto space-y-4">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-black text-white">🎬 Rendering Pipeline</h2>
              {view !== 'rendering' && (
                <button onClick={() => setView('storyboard')}
                  className="text-xs text-gray-500 hover:text-gray-300 transition">
                  ← Edit Storyboard
                </button>
              )}
            </div>

            {/* Event log */}
            <div className="space-y-3">
              {renderEvents.map((ev, i) => (
                <RenderEventCard key={i} ev={ev} />
              ))}
            </div>

            {/* Visual feedback card */}
            {visualFeedback && (
              <div className="rounded-2xl border border-yellow-500/20 bg-yellow-950/20 p-5">
                <p className="text-sm font-bold text-yellow-400 mb-2">🖼️ Visual Critique Feedback</p>
                <pre className="text-xs text-yellow-200/80 whitespace-pre-wrap font-mono leading-relaxed">{visualFeedback}</pre>
                <p className="text-[11px] text-gray-600 mt-2">Manim Coder is applying these spatial corrections…</p>
              </div>
            )}

            {/* Preview ready */}
            {(view === 'preview_ready' || view === 'complete') && (
              <div className="rounded-2xl border border-emerald-500/20 bg-emerald-950/20 p-6 space-y-4">
                <p className="font-bold text-emerald-300">✅ Preview rendered successfully!</p>
                {previewPath && (
                  <p className="text-[11px] text-gray-600 font-mono break-all">{previewPath}</p>
                )}
                <button onClick={renderFinal}
                  className="w-full py-3 rounded-xl bg-gradient-to-r from-blue-600 to-violet-600 hover:from-blue-500 hover:to-violet-500 font-bold text-white text-sm transition-all shadow-lg shadow-blue-500/20 flex items-center justify-center gap-2">
                  🚀 Render Final 4K Video
                </button>
              </div>
            )}

            {/* Complete */}
            {view === 'complete' && outputFolder && (
              <div className="rounded-2xl border border-blue-500/20 bg-blue-950/20 p-5 space-y-3">
                <p className="font-bold text-blue-300">🏆 Production complete!</p>
                <p className="text-[11px] font-mono text-gray-600 break-all">{masterPath || outputFolder}</p>
              </div>
            )}

            {/* Running spinner */}
            {view === 'rendering' && (
              <div className="flex items-center gap-3 py-4 text-gray-500">
                <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                <span className="text-sm">Pipeline running… {healAttempt > 0 && `(self-healing attempt ${healAttempt}/3)`}</span>
              </div>
            )}

            <div ref={bottomRef} />
          </div>
        )}

        {/* ════ VIEW: FULL AUTO ════════════════════════════════════════ */}
        {view === 'full_auto' && (
          <div className="max-w-2xl mx-auto space-y-6">
            <div className="text-center space-y-3">
              <div className="w-20 h-20 mx-auto rounded-full bg-gradient-to-br from-yellow-500 to-orange-500 flex items-center justify-center text-3xl shadow-2xl shadow-yellow-500/30 animate-pulse">
                ⚡
              </div>
              <h2 className="text-2xl font-black text-white">{form.mode === '3b1b' ? '3B1B Mode' : 'Blackboard Q&A'} Active</h2>
              <p className="text-gray-400 text-sm">Full automation running — sit back and watch the magic happen.</p>
            </div>

            <div className="rounded-2xl border border-yellow-500/20 bg-yellow-950/10 overflow-hidden">
              <div className="px-4 py-2 border-b border-yellow-500/10 bg-yellow-500/5 flex items-center justify-between">
                <span className="text-[10px] font-bold text-yellow-400/70 uppercase tracking-widest">Pipeline Log</span>
                <span className="text-[9px] text-gray-600">{fullAutoLogs.length} events</span>
              </div>
              <div className="p-4 max-h-[400px] overflow-y-auto space-y-2">
                {fullAutoLogs.map((log, i) => {
                  const isLast = i === fullAutoLogs.length - 1;
                  const phaseColors: Record<string, string> = {
                    researcher: 'text-blue-400', scriptwriter: 'text-violet-400',
                    visual_designer: 'text-pink-400', math_verifier: 'text-yellow-400',
                    coding: 'text-teal-400', final_render: 'text-orange-400',
                    postprod: 'text-emerald-400', complete: 'text-emerald-300',
                    error: 'text-red-400', init: 'text-gray-400',
                  };
                  const color = phaseColors[log.phase] || 'text-gray-400';
                  return (
                    <div key={i} className={`flex items-start gap-3 text-sm ${color} ${isLast ? 'font-bold' : 'opacity-70'}`}
                         style={{ animation: 'fadeSlideIn 0.2s ease-out' }}>
                      <span className="mt-0.5 flex-shrink-0">{isLast ? '▶' : '✓'}</span>
                      <span className="flex-1">{log.msg}</span>
                      <span className="text-[9px] text-gray-700 font-mono flex-shrink-0">{log.time}</span>
                    </div>
                  );
                })}
                <div ref={bottomRef} />
              </div>
            </div>

            <button onClick={() => { setView('input'); setFullAutoLogs([]); }}
              className="w-full py-3 rounded-xl border border-white/10 text-gray-500 hover:text-gray-300 text-sm transition">
              ← Cancel / Start Over
            </button>
          </div>
        )}

        {/* ════ VIEW: ERROR ════════════════════════════════════════════ */}
        {view === 'error' && (
          <div className="max-w-xl mx-auto py-16 space-y-6">
            <div className="rounded-2xl border border-red-500/20 bg-red-950/20 p-6">
              <p className="font-bold text-red-400 mb-3">❌ Error</p>
              <pre className="text-xs text-red-300/80 font-mono whitespace-pre-wrap">{errorMsg}</pre>
              <p className="text-[11px] text-gray-600 mt-4">
                Ensure the orchestrator is running: <code className="text-blue-400">./run_all.sh</code>
              </p>
            </div>
            <button onClick={() => setView('input')}
              className="w-full py-3 rounded-xl border border-white/10 text-gray-400 hover:border-white/20 text-sm transition">
              ← Start Over
            </button>
          </div>
        )}
      </div>

      <style>{`
        @keyframes fadeSlideIn {
          from { opacity: 0; transform: translateY(10px); }
          to   { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </main>
  );
}

// ── Sub-components ─────────────────────────────────────────────────────────

function Card({ children }: { children: React.ReactNode }) {
  return (
    <div className="rounded-2xl bg-white/[0.03] border border-white/[0.07] p-5 space-y-3">
      {children}
    </div>
  );
}

function Label({ children }: { children: React.ReactNode }) {
  return (
    <label className="block text-[10px] font-bold text-gray-500 uppercase tracking-widest">
      {children}
    </label>
  );
}

function Select({ value, onChange, children }: {
  value: string;
  onChange: (e: React.ChangeEvent<HTMLSelectElement>) => void;
  children: React.ReactNode;
}) {
  return (
    <select value={value} onChange={onChange}
      className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 appearance-none cursor-pointer transition">
      {children}
    </select>
  );
}

function RenderEventCard({ ev }: { ev: StreamEvent }) {
  const configs: Record<string, { icon: string; color: string; label: string }> = {
    status:          { icon: '○',  color: 'text-gray-400',   label: '' },
    code_done:       { icon: '⚙️', color: 'text-violet-400', label: 'Manim Code' },
    self_healing:    { icon: '🔧', color: 'text-yellow-400', label: 'Self-Healing' },
    visual_critique: { icon: '🖼️', color: 'text-orange-400', label: 'Visual Check' },
    preview_ready:   { icon: '🎬', color: 'text-emerald-400',label: 'Preview Ready' },
    complete:        { icon: '✅', color: 'text-emerald-400', label: 'Complete' },
    error:           { icon: '❌', color: 'text-red-400',     label: 'Error' },
  };
  const c = configs[ev.type] || { icon: '·', color: 'text-gray-600', label: '' };
  const msg = (ev.payload.message as string) || ev.type;

  return (
    <div className={`flex items-start gap-3 text-sm ${c.color}`}
         style={{ animation: 'fadeSlideIn 0.2s ease-out' }}>
      <span className="mt-0.5 flex-shrink-0">{c.icon}</span>
      <span className="flex-1">{msg}</span>
    </div>
  );
}
