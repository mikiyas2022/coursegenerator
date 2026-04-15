'use client';

import { useState, useEffect } from 'react';

interface SceneBlock {
  amharicText: string;
  latexFormula: string;
  animationType: string;
  highlightVar: string;
}

interface GlobalMeta {
  grade: string;
  subject: string;
  episodeNumber: string;
  title: string;
}

// ── Voice Personas (mirrors VOICE_PERSONAS in compiler.py) ─────────────────
const VOICE_PERSONAS = [
  {
    key: 'mekdes',
    label: 'Mekdes',
    title: 'The Warm Tutor',
    gender: 'female' as const,
    icon: '👩‍🏫',
    badge: 'DEFAULT',
    badgeColor: 'emerald',
    description: 'Intimate, warm, and encouraging. Paces carefully so every student follows.',
    style: 'Rate −18% · Pitch neutral',
  },
  {
    key: 'tigist',
    label: 'Tigist',
    title: 'The Confident Lecturer',
    gender: 'female' as const,
    icon: '🎓',
    badge: 'FEMALE',
    badgeColor: 'pink',
    description: 'Clear and authoritative. Commands the room like a university professor.',
    style: 'Rate −5% · Pitch slightly lower',
  },
  {
    key: 'selamawit',
    label: 'Selamawit',
    title: 'The Patient Professor',
    gender: 'female' as const,
    icon: '📖',
    badge: 'FEMALE',
    badgeColor: 'pink',
    description: 'Slow and deliberate. Every word lands with precision — perfect for hard derivations.',
    style: 'Rate −30% · Pitch raised',
  },
  {
    key: 'ameha',
    label: 'Ameha',
    title: 'The Expert',
    gender: 'male' as const,
    icon: '👨‍🏫',
    badge: 'MALE',
    badgeColor: 'blue',
    description: 'Deep and professional. Like a senior scientist presenting to a national audience.',
    style: 'Rate −12% · Pitch slightly lower',
  },
  {
    key: 'dawit',
    label: 'Dawit',
    title: 'The Energetic Coach',
    gender: 'male' as const,
    icon: '⚡',
    badge: 'MALE',
    badgeColor: 'blue',
    description: 'Upbeat and motivating. Turns dry physics into an exciting challenge.',
    style: 'Rate +5% · Pitch raised',
  },
];

// ── Animation Types ────────────────────────────────────────────────────────
const ANIMATION_TYPES = [
  { value: 'Text Reveal',       label: '📝 Text Reveal',       hint: 'Writes a formula left-to-right using Write().', group: 'Original' },
  { value: 'Formula Morph',     label: '🔄 Formula Morph',     hint: 'Morphs the previous equation into a new one using ReplacementTransform().', group: 'Original' },
  { value: 'Draw 2D Vector',    label: '↗️ Draw 2D Vector',    hint: 'Draws a coordinate plane and grows a vector arrow using GrowArrow().', group: 'Original' },
  { value: 'Projectile Arc',    label: '🏹 Projectile Arc',    hint: 'Traces a parabolic path on axes. Use for kinematics / motion lessons.', group: 'Original' },
  { value: 'Draw Base',         label: '🖊️ Draw Base',         hint: 'Establishes geometry — auto-draws vector arrow or coordinate axes.', group: 'Enhanced' },
  { value: 'Write Text',        label: '✍️ Write Text',        hint: 'Write() first time; TransformMatchingTex() if a formula already exists.', group: 'Enhanced' },
  { value: 'Highlight Concept', label: '🔦 Highlight Concept', hint: 'Writes formula then flashes the Focus Variable with Indicate()+Wiggle().', group: 'Enhanced' },
];

const initialBlock: SceneBlock = {
  amharicText: '',
  latexFormula: '',
  animationType: 'Text Reveal',
  highlightVar: '',
};

type Status = 'idle' | 'loading' | 'success' | 'error';

const badgeBg: Record<string, string> = {
  emerald: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  pink:    'bg-pink-500/20 text-pink-400 border-pink-500/30',
  blue:    'bg-blue-500/20 text-blue-400 border-blue-500/30',
};

export default function Dashboard() {
  const [mounted, setMounted]       = useState(false);
  const [persona, setPersona]       = useState('mekdes');
  const [orientation, setOrientation] = useState<'landscape' | 'portrait'>('landscape');
  const [meta, setMeta]             = useState<GlobalMeta>({ grade: '12', subject: 'Physics', episodeNumber: '1', title: 'Vector_Resolution' });
  const [blocks, setBlocks]         = useState<SceneBlock[]>([]);
  const [status, setStatus]         = useState<Status>('idle');
  const [message, setMessage]       = useState('');
  const [outputPath, setOutputPath] = useState('');
  const [currentStep, setCurrentStep] = useState('');

  useEffect(() => { setMounted(true); setBlocks([{ ...initialBlock }]); }, []);

  const STEPS = ['Initializing pipeline…','Synthesising voice…','Animating…','Synchronising…','Finalising…','Success!'];

  const addBlock    = (e: React.MouseEvent) => { e.preventDefault(); setBlocks(b => [...b, { ...initialBlock }]); };
  const removeBlock = (i: number) => setBlocks(b => b.filter((_, idx) => idx !== i));
  const updateBlock = (i: number, field: keyof SceneBlock, val: string) =>
    setBlocks(b => b.map((bl, idx) => idx === i ? { ...bl, [field]: val } : bl));
  const updateMeta = (field: keyof GlobalMeta, val: string) =>
    setMeta(m => ({ ...m, [field]: val }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!mounted) return;
    setStatus('loading'); setMessage(''); setOutputPath('');
    try {
      for (let i = 0; i < STEPS.length - 1; i++) {
        setCurrentStep(STEPS[i]);
        await new Promise(r => setTimeout(r, 600));
      }
      const res  = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...meta, blocks, orientation, persona }),
      });
      const data = await res.json();
      if (!res.ok || data.status === 'error') throw new Error(data.message || 'Generation failed');
      setCurrentStep(STEPS[STEPS.length - 1]);
      setStatus('success');
      setMessage(data.message || 'Done!');
      setOutputPath(data.folderPath || '');
    } catch (err: unknown) {
      setStatus('error');
      setMessage(`Failed: ${err instanceof Error ? err.message : String(err)}`);
    }
  };

  if (!mounted) return (
    <div className="min-h-screen bg-[#141414] flex items-center justify-center">
      <div className="text-emerald-500 font-mono animate-pulse">BOOTING MASTERPIECE ENGINE...</div>
    </div>
  );

  const selectedPersona = VOICE_PERSONAS.find(p => p.key === persona)!;

  return (
    <main className="min-h-screen bg-[#141414] text-gray-100 py-12 px-6 font-sans">
      <div className="max-w-5xl mx-auto space-y-10">

        {/* Header */}
        <div className="text-center">
          <h1 className="text-5xl font-black tracking-tight bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent mb-3">
            STEM MASTERPIECE FACTORY
          </h1>
          <p className="text-gray-500 text-lg">3Blue1Brown-Style · Amharic Neural TTS · 1080p60</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-10">

          {/* ── Voice Persona ────────────────────────────────────────────── */}
          <section className="bg-gray-900/50 rounded-3xl p-8 border border-white/5 shadow-2xl">
            <h2 className="text-xl font-bold text-pink-400 mb-2 flex items-center gap-2">
              <span className="p-1.5 bg-pink-500/10 rounded-lg">🎙️</span> Narrator Persona
            </h2>
            <p className="text-xs text-gray-600 mb-6">Choose the voice character that will narrate your lesson. Female voices are recommended by default.</p>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {VOICE_PERSONAS.map(p => (
                <button
                  key={p.key}
                  type="button"
                  onClick={() => setPersona(p.key)}
                  className={`relative text-left p-4 rounded-2xl border-2 transition-all duration-200 ${
                    persona === p.key
                      ? 'border-pink-500 bg-pink-500/10'
                      : 'border-white/8 bg-black/20 hover:border-white/15'
                  }`}
                >
                  {/* Selected checkmark */}
                  {persona === p.key && (
                    <div className="absolute top-2 right-2 w-5 h-5 rounded-full bg-pink-500 flex items-center justify-center text-white text-[10px] font-black">✓</div>
                  )}
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-2xl">{p.icon}</span>
                    <div>
                      <div className="flex items-center gap-1.5">
                        <span className={`font-black text-sm ${persona === p.key ? 'text-pink-300' : 'text-white'}`}>{p.label}</span>
                        <span className={`text-[10px] px-1.5 py-0.5 rounded border font-bold ${badgeBg[p.badgeColor]}`}>{p.badge}</span>
                      </div>
                      <p className="text-[11px] text-gray-500">{p.title}</p>
                    </div>
                  </div>
                  <p className="text-[11px] text-gray-500 leading-relaxed mb-2">{p.description}</p>
                  <p className={`text-[10px] font-mono ${persona === p.key ? 'text-pink-500' : 'text-gray-700'}`}>{p.style}</p>
                </button>
              ))}
            </div>

            {/* Live preview of selected */}
            <div className="mt-4 flex items-center gap-3 text-sm text-gray-500 bg-black/30 rounded-xl px-4 py-3 border border-white/5">
              <span>{selectedPersona.icon}</span>
              <span>Using <strong className="text-pink-400">{selectedPersona.label}</strong> — {selectedPersona.description}</span>
            </div>
          </section>

          {/* ── Episode Architecture ─────────────────────────────────────── */}
          <section className="bg-gray-900/50 rounded-3xl p-8 border border-white/5 shadow-2xl">
            <h2 className="text-xl font-bold text-emerald-400 mb-6 flex items-center gap-2">
              <span className="p-1.5 bg-emerald-500/10 rounded-lg">📋</span> Episode Architecture
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              {([['Grade','grade','12'],['Subject','subject','Physics'],['Episode','episodeNumber','1'],['Filename','title','Vector_Resolution']] as [string,string,string][]).map(([label,key,ph]) => (
                <div key={key}>
                  <label className="block text-xs font-bold text-gray-500 mb-2 uppercase tracking-widest">{label}</label>
                  <input type="text" value={meta[key as keyof GlobalMeta]}
                    onChange={e => updateMeta(key as keyof GlobalMeta, e.target.value)}
                    placeholder={ph} required
                    className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition" />
                </div>
              ))}
            </div>
          </section>

          {/* ── Orientation ──────────────────────────────────────────────── */}
          <section className="bg-gray-900/50 rounded-3xl p-8 border border-white/5 shadow-2xl">
            <h2 className="text-xl font-bold text-purple-400 mb-6 flex items-center gap-2">
              <span className="p-1.5 bg-purple-500/10 rounded-lg">📐</span> Video Orientation
            </h2>
            <div className="grid grid-cols-2 gap-4">
              {(['landscape', 'portrait'] as const).map(mode => (
                <button key={mode} type="button" onClick={() => setOrientation(mode)}
                  className={`relative flex flex-col items-center gap-3 py-6 rounded-2xl border-2 transition-all ${
                    orientation === mode ? 'border-purple-500 bg-purple-500/10 text-purple-300' : 'border-white/10 bg-black/20 text-gray-500 hover:border-white/20'
                  }`}>
                  {orientation === mode && <div className="absolute top-2 right-2 w-5 h-5 rounded-full bg-purple-500 flex items-center justify-center text-white text-[10px] font-black">✓</div>}
                  <div className={`border-2 rounded flex items-center justify-center ${orientation === mode ? 'border-purple-400' : 'border-gray-600'} ${mode === 'landscape' ? 'w-20 h-12' : 'w-12 h-20'}`}>
                    <div className={`rounded-sm ${orientation === mode ? 'bg-purple-400' : 'bg-gray-600'} ${mode === 'landscape' ? 'w-12 h-1.5' : 'w-1.5 h-12'}`} />
                  </div>
                  <div className="text-center">
                    <p className="font-black text-sm uppercase tracking-widest">{mode}</p>
                    <p className="text-[11px] opacity-60 mt-0.5">{mode === 'landscape' ? '1920 × 1080 · YouTube / PC' : '1080 × 1920 · TikTok / Reels'}</p>
                  </div>
                </button>
              ))}
            </div>
          </section>

          {/* ── Animation Blocks ─────────────────────────────────────────── */}
          <section className="space-y-6">
            <div className="flex items-center justify-between px-2">
              <h2 className="text-xl font-bold text-blue-400 flex items-center gap-2">
                <span className="p-1.5 bg-blue-500/10 rounded-lg">🎞️</span> Animation Blocks
              </h2>
              <button type="button" onClick={addBlock}
                className="px-6 py-2.5 bg-blue-600 hover:bg-blue-500 rounded-full text-white text-sm font-bold shadow-lg transition-all active:scale-95">
                + New Scene
              </button>
            </div>

            <div className="space-y-4">
              {blocks.map((block, i) => {
                const typeInfo = ANIMATION_TYPES.find(t => t.value === block.animationType);
                const isHL     = block.animationType === 'Highlight Concept';
                return (
                  <div key={`block-${i}`} className="bg-gray-900/40 border border-white/5 rounded-3xl p-8 hover:border-blue-500/30 transition-all duration-300">
                    <div className="flex items-center justify-between mb-8">
                      <div className="flex items-center gap-4">
                        <div className="bg-blue-500 text-white w-10 h-10 rounded-full flex items-center justify-center font-black text-lg">{i + 1}</div>
                        <div>
                          <span className="text-sm font-bold text-gray-400 uppercase tracking-widest">SCENE BLOCK</span>
                          <span className={`ml-3 text-xs px-2 py-0.5 rounded-full font-semibold ${typeInfo?.group === 'Enhanced' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-blue-500/10 text-blue-400'}`}>{block.animationType}</span>
                        </div>
                      </div>
                      {blocks.length > 1 && (
                        <button type="button" onClick={() => removeBlock(i)} className="p-2 text-gray-600 hover:text-red-500 transition-colors">✕</button>
                      )}
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
                      <div className="md:col-span-8 space-y-6">
                        <div>
                          <label className="block text-xs font-black text-gray-500 mb-2 uppercase tracking-tighter">🗣️ Amharic Script</label>
                          <textarea rows={3} value={block.amharicText}
                            onChange={e => updateBlock(i, 'amharicText', e.target.value)}
                            placeholder="አማርኛ እዚህ ይጻፉ..." required
                            className="w-full bg-black/40 border border-white/10 rounded-2xl px-5 py-4 text-base text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 resize-none transition" />
                        </div>
                        <div>
                          <label className="block text-xs font-black text-gray-500 mb-2 uppercase tracking-tighter">🧮 LaTeX Mathematics</label>
                          <input type="text" value={block.latexFormula}
                            onChange={e => updateBlock(i, 'latexFormula', e.target.value)}
                            placeholder="e.g. F_x = F\cos(\theta)"
                            className="w-full bg-black/40 border border-white/10 rounded-xl px-5 py-3 text-sm font-mono text-emerald-300 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition" />
                        </div>
                      </div>

                      <div className="md:col-span-4 space-y-6 lg:border-l lg:border-white/5 lg:pl-8">
                        <div>
                          <label className="block text-xs font-black text-gray-500 mb-2 uppercase tracking-tighter">⚡ Animation Type</label>
                          <select value={block.animationType} onChange={e => updateBlock(i, 'animationType', e.target.value)}
                            className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 appearance-none cursor-pointer transition">
                            <optgroup label="── Original Types">
                              {ANIMATION_TYPES.filter(t => t.group === 'Original').map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
                            </optgroup>
                            <optgroup label="── Enhanced Types">
                              {ANIMATION_TYPES.filter(t => t.group === 'Enhanced').map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
                            </optgroup>
                          </select>
                          {typeInfo && <p className="mt-2 text-[11px] text-gray-600 leading-relaxed">{typeInfo.hint}</p>}
                        </div>

                        {isHL && (
                          <div>
                            <label className="block text-xs font-black text-yellow-700 mb-2 uppercase tracking-tighter">✨ Focus Variable</label>
                            <input type="text" value={block.highlightVar}
                              onChange={e => updateBlock(i, 'highlightVar', e.target.value)}
                              placeholder="Exact substring to flash, e.g. F_x"
                              className="w-full bg-black/40 border border-yellow-500/40 rounded-xl px-4 py-3 text-sm text-yellow-300 font-mono focus:outline-none focus:ring-2 focus:ring-yellow-500/50 transition" />
                            <p className="mt-2 text-[11px] text-yellow-800">Flashed via Indicate()+Wiggle().</p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </section>

          {/* ── Submit ───────────────────────────────────────────────────── */}
          <div className="pt-2">
            <button type="submit" disabled={status === 'loading'}
              className="w-full py-5 rounded-3xl bg-gradient-to-r from-blue-600 to-emerald-600 hover:from-blue-500 hover:to-emerald-500 disabled:opacity-50 transition-all duration-500 shadow-2xl shadow-blue-500/20">
              <span className="text-xl font-black text-white tracking-widest uppercase flex items-center justify-center gap-3">
                {status === 'loading'
                  ? <><span className="w-5 h-5 border-4 border-white border-t-transparent rounded-full animate-spin" />{currentStep}</>
                  : `🎬 Render with ${selectedPersona.icon} ${selectedPersona.label}`}
              </span>
            </button>
          </div>

          {/* ── Feedback ────────────────────────────────────────────────── */}
          {status !== 'idle' && (
            <div className={`rounded-3xl p-8 border backdrop-blur-md transition-all ${
              status === 'success' ? 'bg-emerald-950/30 border-emerald-500/30 text-emerald-300'
              : status === 'error' ? 'bg-red-950/30 border-red-500/30 text-red-300'
              : 'bg-gray-900/50 border-white/10 text-gray-400'}`}>
              <p className="font-bold mb-4 flex items-center gap-2">
                {status === 'loading' && <span className="text-blue-400">⚡ PROCESSING:</span>}
                {status === 'success' && <span className="text-emerald-400">✓ RENDER COMPLETE:</span>}
                {status === 'error'   && <span className="text-red-400">✕ ERROR:</span>}
                {message}
              </p>
              {outputPath && <div className="bg-black/40 rounded-2xl p-4 font-mono text-[10px] break-all border border-white/5 opacity-70">FILE: {outputPath}</div>}
            </div>
          )}
        </form>
      </div>
    </main>
  );
}
