import { NextResponse } from 'next/server';
import path from 'path';

const ORCHESTRATOR_URL = 'http://127.0.0.1:8206';

export async function POST(req: Request) {
  try {
    const body = await req.json();

    // Determine output folder inside Local_Video_Output
    const safeTitle    = String(body.topic || 'lesson').replace(/[^a-zA-Z0-9_\u1200-\u137F]/g, '_').slice(0, 40);
    const outputFolder = path.join(process.cwd(), '..', 'Local_Video_Output', `${Date.now()}_${safeTitle}`);

    const orchResponse = await fetch(`${ORCHESTRATOR_URL}/create`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ ...body, output_folder: outputFolder }),
    });

    if (!orchResponse.ok || !orchResponse.body) {
      const text = await orchResponse.text().catch(() => 'unknown error');
      return NextResponse.json({ error: `Orchestrator error: ${text}` }, { status: 502 });
    }

    // Proxy the SSE stream transparently to the browser
    return new Response(orchResponse.body, {
      headers: {
        'Content-Type':  'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection':    'keep-alive',
      },
    });

  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    return NextResponse.json(
      { error: `Failed to reach orchestrator: ${msg}. Is it running on port 8200?` },
      { status: 503 },
    );
  }
}
