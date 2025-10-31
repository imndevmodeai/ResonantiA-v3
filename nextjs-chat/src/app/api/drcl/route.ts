import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import fs from 'fs/promises';
import path from 'path';

export const dynamic = 'force-dynamic';

function buildEnvelope(initial_context: any) {
	const now = new Date();
	const interactionId = `drlc-${now.getTime()}`;
	return {
		archE_meta: {
			protocol: 'DRCL.v1',
			interaction_id: interactionId,
			phase: 'map',
			confidence: 0.9,
			issues: [] as string[],
			depends_on: [] as string[]
		},
		conceptual_map: {
			sprs: ['Cognitive resonancE', 'Implementation resonancE'],
			abstract_workflow: [
				{ step: 1, name: 'Decide RISE Mode', summary: 'embedded|parallel|separate via heuristics' },
				{ step: 2, name: 'Ground Truth Audit', summary: 'validate assumptions vs repo' },
				{ step: 3, name: 'Correction Plan', summary: 'minimal viable edits' }
			],
			territory_assumptions: [
				{ path: 'Happier/workflows/distributed_resonant_corrective_loop.json', must_exist: true }
			]
		},
		dissonance_report: {
			missing: [] as string[],
			mismatch: [] as any[]
		},
		correction_plan: [] as any[],
		synced_blueprint: {
			workflow: 'Happier/workflows/distributed_resonant_corrective_loop.json',
			inputs: { initial_context: initial_context || {} },
			post_checks: ['result keys present', 'errors none']
		},
		iar: {
			status: 'ok',
			notes: 'assembled by /api/drcl stub'
		},
		rise: {
			mode: 'separate',
			reason: 'default stub mode',
			outline: [
				{ phase: 'scaffold', steps: ['collect signals'] },
				{ phase: 'insight', steps: ['hypothesize', 'test'] },
				{ phase: 'synthesis', steps: ['plan'] }
			]
		}
	};
}

async function readFirstExisting(paths: string[]) {
	for (const p of paths) {
		try {
			const data = await fs.readFile(p, 'utf8');
			return data;
		} catch (_e) {
			// continue
		}
	}
	throw new Error('Schema not found in candidate paths');
}

async function tryValidate(envelope: any) {
	const result = { valid: true, errors: [] as any[] };
	try {
		const candidates = [
			path.resolve(process.cwd(), 'protocol', 'drcl_envelope.schema.json'),
			path.resolve(process.cwd(), '..', 'protocol', 'drcl_envelope.schema.json'),
			path.resolve(process.cwd(), '..', '..', 'protocol', 'drcl_envelope.schema.json')
		];
		const schemaJson = await readFirstExisting(candidates);
		const schema = JSON.parse(schemaJson);

		// Prefer Ajv 2020 for draft 2020-12, fallback to standard Ajv
		let ajvInstance: any;
		try {
			const Ajv2020 = (await import('ajv/dist/2020')).default;
			ajvInstance = new Ajv2020({ allErrors: true, strict: false });
		} catch (_e) {
			try {
				const Ajv = (await import('ajv')).default;
				ajvInstance = new Ajv({ allErrors: true, strict: false });
			} catch (_e2) {
				return { valid: true, errors: [{ warning: 'Ajv not available; schema not strictly enforced.' }] };
			}
		}

		const validate = ajvInstance.compile(schema);
		const ok = validate(envelope);
		if (!ok) {
			return { valid: false, errors: validate.errors || [] };
		}
		return result;
	} catch (e: any) {
		return { valid: true, errors: [{ warning: e?.message || 'Schema not found; soft-validated.' }] };
	}
}

export async function POST(req: NextRequest) {
	try {
		const body = await req.json().catch(() => ({}));
		const initial_context = body?.initial_context ?? {};
		const envelope = buildEnvelope(initial_context);
		const validation = await tryValidate(envelope);
		return NextResponse.json({ envelope, validation });
	} catch (e: any) {
		return NextResponse.json({ error: e?.message || 'unknown_error' }, { status: 500 });
	}
}
