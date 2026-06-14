import { TestCycle } from '../../services/tm.cycles.service';

export interface ProgressSegment {
    key: string;
    label: string;
    result: string;
    count: number;
    color: string;
    pct: number;
}

export const RESULT_COLORS: Record<string, string> = {
    pass: '#3fb950',
    fail: '#f85149',
    blocked: '#58a6ff',
    in_progress: '#d29922',
    not_executed: '#757575',
};

const BUCKET_LABELS: Record<string, string> = {
    pass: 'Pass',
    fail: 'Fail',
    blocked: 'Blocked',
    in_progress: 'In Progress',
    not_executed: 'Not Run',
};

const BUCKET_ORDER = ['pass', 'fail', 'blocked', 'in_progress', 'not_executed'];

const ALIASES: Record<string, string> = { passed: 'pass', failed: 'fail' };

function normalizeStatus(s: string): string {
    const key = s.toLowerCase().replace(/[-\s]/g, '_');
    return ALIASES[key] ?? key;
}

/**
 * Returns progress segments for a single cycle (only non-zero counts).
 */
export function getProgressSummary(cycle: TestCycle): ProgressSegment[] {
    const counts: Record<string, number> = {};

    Object.values(cycle.executions ?? {}).forEach(status => {
        const key = normalizeStatus(status);
        const bucket = BUCKET_LABELS[key] ? key : 'not_executed';
        counts[bucket] = (counts[bucket] ?? 0) + 1;
    });

    const total = Object.values(counts).reduce((s, c) => s + c, 0);

    return BUCKET_ORDER
        .filter(key => (counts[key] ?? 0) > 0)
        .map(key => ({
            key,
            label: BUCKET_LABELS[key],
            result: key.toUpperCase(),
            count: counts[key],
            color: RESULT_COLORS[key],
            pct: total ? Math.round((counts[key] / total) * 100) : 0,
        }));
}

/**
 * Returns progress segments keyed by cycle key for a list of cycles.
 */
export function computeProgressSummaries(cycles: TestCycle[]): Record<string, ProgressSegment[]> {
    const summaries: Record<string, ProgressSegment[]> = {};
    for (const cycle of cycles) {
        const segments = getProgressSummary(cycle);
        if (segments.length > 0) {
            summaries[cycle.test_cycle_key] = segments;
        }
    }
    return summaries;
}
