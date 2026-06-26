import { describe, expect, it } from 'vitest';
import type {
	ConceptFrontmatter,
	ConceptType,
	PathYUserContext,
	Visibility,
	XAiLibraryCurator
} from './types';

describe('Type contracts (umbrella doc §3.3 + §3.6.1 + §3.6.2)', () => {
	it('ConceptType has 8 values per OKF v0.1 spec', () => {
		const allTypes: ConceptType[] = [
			'dataset',
			'metric',
			'api_endpoint',
			'runbook',
			'integration',
			'event',
			'reference',
			'decision'
		];
		expect(allTypes).toHaveLength(8);
		expect(new Set(allTypes).size).toBe(8);
	});

	it('Visibility has 4 values per Path Y scope priority (§3.6.3)', () => {
		const allVisibilities: Visibility[] = ['public', 'org', 'personal', 'project'];
		expect(allVisibilities).toHaveLength(4);
	});

	it('XAiLibraryCurator has 5 values per §3.6.2 curation governance', () => {
		const allCurators: XAiLibraryCurator[] = [
			'rule-based',
			'llm-system_admin',
			'human-self-user',
			'human-org-head',
			'human-system-admin'
		];
		expect(allCurators).toHaveLength(5);
	});

	it('PathYUserContext has 8 required fields per §3.6.1', () => {
		const ctx: PathYUserContext = {
			version: 'v0',
			user_id: 'u_001',
			org_id: 'ou_root',
			org_unit_ids: ['ou_root'],
			project_ids: [],
			roles: ['developer'],
			request_id: 'req_001',
			issued_at: '2026-06-22T00:00:00Z'
		};
		expect(ctx.version).toBe('v0');
		expect(typeof ctx.user_id).toBe('string');
		expect(typeof ctx.org_id).toBe('string');
		expect(Array.isArray(ctx.org_unit_ids)).toBe(true);
		expect(Array.isArray(ctx.project_ids)).toBe(true);
		expect(Array.isArray(ctx.roles)).toBe(true);
		expect(typeof ctx.request_id).toBe('string');
		expect(typeof ctx.issued_at).toBe('string');
	});

	it('ConceptFrontmatter has 12 fields (7 core + 5 x_ai_library_)', () => {
		const fm: ConceptFrontmatter = {
			type: 'dataset',
			title: 'Test',
			description: 'desc',
			resource: 'r',
			tags: ['t'],
			timestamp: '2026-06-22T00:00:00Z',
			x_ai_library_source: 's',
			x_ai_library_bundle: 'b',
			x_ai_library_version: 1,
			x_ai_library_curator: 'rule-based',
			x_ai_library_owner_org_id: 'ou',
			x_ai_library_owner_user_id: 'u',
			x_ai_library_owner_org_unit_ids: ['ou'],
			x_ai_library_owner_project_ids: [],
			x_ai_library_visibility: 'org'
		};
		const keys = Object.keys(fm);
		expect(keys.length).toBeGreaterThanOrEqual(12);
	});
});

describe('Type-safe instantiation', () => {
	it('PathYUserContext with empty arrays', () => {
		const ctx: PathYUserContext = {
			version: 'v0',
			user_id: 'u',
			org_id: 'o',
			org_unit_ids: [],
			project_ids: [],
			roles: [],
			request_id: 'r',
			issued_at: '2026-06-22T00:00:00Z'
		};
		expect(ctx.org_unit_ids).toHaveLength(0);
	});

	it('ConceptFrontmatter optional fields are all omittable', () => {
		const fm: ConceptFrontmatter = {
			type: 'event',
			x_ai_library_version: 1,
			x_ai_library_curator: 'rule-based',
			x_ai_library_visibility: 'public'
		};
		expect(fm.title).toBeUndefined();
		expect(fm.description).toBeUndefined();
		expect(fm.resource).toBeUndefined();
		expect(fm.tags).toBeUndefined();
		expect(fm.timestamp).toBeUndefined();
		expect(fm.x_ai_library_source).toBeUndefined();
		expect(fm.x_ai_library_bundle).toBeUndefined();
		expect(fm.x_ai_library_owner_org_id).toBeUndefined();
		expect(fm.x_ai_library_owner_user_id).toBeUndefined();
		expect(fm.x_ai_library_owner_org_unit_ids).toBeUndefined();
		expect(fm.x_ai_library_owner_project_ids).toBeUndefined();
	});
});