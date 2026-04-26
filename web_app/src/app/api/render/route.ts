import path from 'path';

const ORCHESTRATOR_URL = process.env.ORCHESTRATOR_URL || 'http://127.0.0.1:8205';

export async function POST(req: Request) {
  try {
    const body = await req.json();

    // Assign output folder inside Local_Video_Output if not provided
    if (!body.output_folder) {
      const safe = String(body.scenes?.[0]?.concept || 'lesson')
        .replace(/[^a-zA-Z0-9_\u1200-\u137F]/g, '_')
        .slice(0, 40);
      body.output_folder = path.join(process.cwd(), '..', 'Local_Video_Output', `${Date.now()}_${safe}`);
    }

    const orchRes = await fetch(`${ORCHESTRATOR_URL}/render_scenes`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(body),
    });

    if (!orchRes.ok || !orchRes.body) {
      const text = await orchRes.text().catch(() => 'unknown');
      return new Response(
        `data: ${JSON.stringify({ type: 'error', payload: { message: `Orchestrator: ${text}` } })}\n\n`,
        { status: 502, headers: { 'Content-Type': 'text/event-stream' } }
      );
    }

    return new Response(orchRes.body, {
      headers: {
        'Content-Type':  'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection':    'keep-alive',
      },
    });

  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    return new Response(
      `data: ${JSON.stringify({ type: 'error', payload: { message: `Render unreachable: ${msg}` } })}\n\n`,
      { status: 503, headers: { 'Content-Type': 'text/event-stream' } }
    );
  }
}
