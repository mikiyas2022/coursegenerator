import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promises as fs } from 'fs';
import path from 'path';
import { promisify } from 'util';

const execPromise = promisify(exec);

const PROJECT_ROOT = path.resolve(process.cwd(), '..');
const OUTPUT_BASE  = path.join(PROJECT_ROOT, 'Local_Video_Output');
const COMPILER_DIR = path.join(PROJECT_ROOT, 'video_compiler');

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const { grade, subject, episodeNumber, title, blocks, orientation, persona } = body;

    if (!grade || !subject || !episodeNumber || !title || !blocks?.length) {
      return NextResponse.json({ status: 'error', message: 'Missing required fields.' }, { status: 400 });
    }

    const videoOrientation: string = orientation === 'portrait' ? 'portrait' : 'landscape';
    const voicePersona: string     = persona || 'mekdes';

    const safeTitle  = String(title).replace(/\s+/g, '_');
    const folderName = `Ep${episodeNumber}_${safeTitle}`;
    const folderPath = path.join(OUTPUT_BASE, `Grade_${grade}`, subject, folderName);
    await fs.mkdir(folderPath, { recursive: true });

    const scriptData     = { grade, subject, episodeNumber, title, blocks, orientation: videoOrientation, persona: voicePersona };
    const scriptDataPath = path.join(folderPath, 'script_data.json');
    await fs.writeFile(scriptDataPath, JSON.stringify(scriptData, null, 2));

    const compilerScript = path.join(COMPILER_DIR, 'compiler.py');
    const VENV_PYTHON    = '/tmp/stem_venv/bin/python3';

    let pythonCmd = 'python3';
    try { await fs.access(VENV_PYTHON); pythonCmd = VENV_PYTHON; } catch (_) {}

    const customEnv = {
      ...process.env,
      PATH: '/tmp/stem_venv/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin',
      VIRTUAL_ENV: '/tmp/stem_venv',
      PYTHONPATH: COMPILER_DIR,
    };

    const compilerCmd = `"${pythonCmd}" "${compilerScript}" "${scriptDataPath}" "${folderPath}" "${videoOrientation}"`;

    console.log(`Rendering [${videoOrientation}] with voice [${voicePersona}]...`);
    try {
      const { stdout, stderr } = await execPromise(compilerCmd, { env: customEnv, timeout: 600_000 });
      if (stdout) console.log('[compiler]', stdout);
      if (stderr) console.warn('[compiler err]', stderr);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      return NextResponse.json({ status: 'error', message: `Compiler failed: ${msg}` }, { status: 500 });
    }

    return NextResponse.json({
      status: 'success',
      message: `Video generated! Voice: ${voicePersona} | Orientation: ${videoOrientation}`,
      folderPath,
      sceneBlocks: blocks.length,
      orientation: videoOrientation,
      persona: voicePersona,
    });

  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ status: 'error', message: msg }, { status: 500 });
  }
}
