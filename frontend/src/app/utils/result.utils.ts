const RESULT_COLORS: Record<string, string> = {
    PASS: '#4caf50',
    FAIL: '#f44336',
    BLOCKED: '#2196f3',
    NOT_EXECUTED: '#757575',
    IN_PROGRESS: '#ffd700',
};

/**
 * Returns the display color associated with a test result status.
 * Falls back to a neutral gray for unknown or missing results.
 */
export function getResultColor(result: string | null | undefined): string {
    return RESULT_COLORS[result?.toUpperCase() ?? ''] ?? '#757575';
}
