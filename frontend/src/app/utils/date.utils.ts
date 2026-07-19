export function formatDate(dateStr: string | null): string {
    if (!dateStr) return '—';

    const date = new Date(dateStr);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');

    let hours = date.getHours();
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    const period = hours >= 12 ? 'PM' : 'AM';

    hours = hours % 12;
    if (hours === 0) hours = 12;
    
    const hoursStr = String(hours).padStart(2, '0');

    return `${year}-${month}-${day}, ${hoursStr}:${minutes}:${seconds} ${period}`;
}
