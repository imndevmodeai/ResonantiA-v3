/* Minimal WebSocket Bus Stub for ArchE UI
 * Starts a WS server at ws://localhost:3004
 * - Sends a protocol_init message on connect
 * - Additionally calls the DRCL API (/api/drcl) and streams the envelope
 */

const WebSocket = require('ws');
const httpTarget = process.env.NEXT_BASE || 'http://localhost:3001';

const PORT = process.env.WS_PORT ? parseInt(process.env.WS_PORT, 10) : 3004;
const wss = new WebSocket.Server({ port: PORT });

function nowIso() {
	return new Date().toISOString();
}

function sendJson(ws, obj) {
	try {
		ws.send(JSON.stringify(obj));
	} catch (e) {
		console.error('Send error:', e);
	}
}

async function runDrcl(goal) {
	try {
		const res = await fetch(`${httpTarget}/api/drcl`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ initial_context: {
				goal,
				constraints: {
					ui_entry: ['nextjs-chat/src/components/Chat.tsx'],
					schema_path: 'protocol/drcl_envelope.schema.json',
					workflow_path: 'Happier/workflows/distributed_resonant_corrective_loop.json',
					single_surface: true
				},
				desired_outputs: ['RISE mode decision','UI integration plan','assembled DRCL envelope','schema validation result']
			} })
		});
		const data = await res.json();
		return { ok: res.ok, data };
	} catch (e) {
		return { ok: false, error: e?.message || 'drcl_call_failed' };
	}
}

wss.on('connection', (ws) => {
	console.log(`[WS-BUS] client connected @ ${nowIso()}`);
	sendJson(ws, {
		id: `init-${Date.now()}`,
		content: 'ResonantiA Protocol active',
		timestamp: nowIso(),
		sender: 'arche',
		message_type: 'protocol_init',
		protocol_compliance: true,
		protocol_version: 'v3.1-CA',
		protocol_init: { status: 'online' }
	});

	ws.on('message', async (msg) => {
		const text = msg.toString();
		let command = 'run_drcl'; // default to run_drcl
		let payload = { goal: text };
		if (text.startsWith('{')) {
			try {
				const data = JSON.parse(text);
				command = data.command;
				payload = data.payload;
			} catch (e) {
				command = 'error';
				payload = { message: 'invalid command json' };
			}
		}

		console.log('[WS-BUS] rx:', command, payload);
		
		if (command === 'run_drcl') {
			sendJson(ws, {
				id: `drcl-start-${Date.now()}`,
				content: 'Starting DRCL on your query…',
				timestamp: nowIso(),
				sender: 'arche',
				message_type: 'drcl_status_update',
				payload: { drclStatus: 'Running DRCL…' }
			});
			const res = await runDrcl(payload.goal);
			if (res.ok) {
				sendJson(ws, {
					id: `drcl-ok-${Date.now()}`,
					content: JSON.stringify(res.data, null, 2),
					timestamp: nowIso(),
					sender: 'arche',
					message_type: 'drcl_envelope',
					payload: { envelope: res.data.envelope, validation: res.data.validation }
				});
			} else {
				sendJson(ws, {
					id: `drcl-err-${Date.now()}`,
					content: `DRCL error: ${res.error || 'unknown'}`,
					timestamp: nowIso(),
					sender: 'arche',
					message_type: 'protocol_error',
					protocol_error: { message: res.error || 'drcl_error' }
				});
			}
		}
	});

	ws.on('close', () => console.log('[WS-BUS] client disconnected'));
	ws.on('error', (e) => console.error('[WS-BUS] error:', e));
});

wss.on('listening', () => {
	console.log(`[WS-BUS] listening on ws://localhost:${PORT}`);
});

wss.on('error', (e) => {
	console.error('[WS-BUS] server error:', e);
});
