import * as echarts from 'echarts';

export const STATUS_ORDER: string[] = ['NOT_EXECUTED', 'BLOCKED', 'FAIL', 'PASS'];

export const STATUS_COLORS: Record<string, string> = {
  PASS: '#3fb950',
  FAIL: '#f44336',
  BLOCKED: '#2196f3',
  NOT_EXECUTED: '#757575',
};

export function buildDataViewContent(opt: any): string {
  const xData: string[] = (opt.xAxis as any[])[0]?.data ?? [];
  const seriesList: any[] = (opt.series as any[]) ?? [];
  const displayOrder = ['PASS', 'FAIL', 'BLOCKED', 'NOT EXECUTED'];
  const ordered = displayOrder
    .map((name) => seriesList.find((s) => s.name === name))
    .filter(Boolean);

  const colW = `style="width:120px;min-width:120px;max-width:120px"`;
  const cycleW = `style="width:100px;min-width:100px;max-width:100px"`;
  const thStyle = `padding:6px 0;border-bottom:1px solid #444;color:#bdbdbd;font-weight:600;text-align:center;white-space:nowrap;`;
  const tdStyle = `padding:5px 0;border-bottom:1px solid #2e2e2e;text-align:center;color:#e0e0e0;`;

  const th = (txt: string, extra = '') => `<th ${extra} style="${thStyle}">${txt}</th>`;
  const td = (txt: string | number, extra = '') => `<td ${extra} style="${tdStyle}">${txt}</td>`;

  const colDefs = `<colgroup><col ${cycleW}>${ordered.map(() => `<col ${colW}>`).join('')}</colgroup>`;
  const header = `<tr>${th('CYCLE', cycleW)}${ordered.map((s: any) => th(s.name, colW)).join('')}</tr>`;
  const rows = [...xData]
    .reverse()
    .map((cat, i) => {
      const origIdx = xData.length - 1 - i;
      return `<tr>${td(cat, cycleW)}${ordered.map((s: any) => td(s.data[origIdx] ?? 0, colW)).join('')}</tr>`;
    })
    .join('');

  return `<div style="overflow:auto;max-height:100%;padding:10px">
    <table style="border-collapse:collapse;font-size:13px;table-layout:fixed">
      ${colDefs}
      <thead>${header}</thead>
      <tbody>${rows}</tbody>
    </table>
  </div>`;
}

export function buildChartOption(
  categories: string[],
  series: echarts.SeriesOption[],
  projectKey: string,
  xLabels: string[] = [],
): echarts.EChartsOption {
  const labelInterval = Math.max(0, Math.ceil(categories.length / 16) - 1);
  const labelMap = new Map<string, string>(categories.map((key, i) => [key, xLabels[i] ?? key]));
  return {
    toolbox: {
      right: 20,
      top: 6,
      itemSize: 16,
      itemGap: 12,
      iconStyle: { borderColor: '#9e9e9e' },
      emphasis: { iconStyle: { borderColor: '#e0e0e0' } },
      feature: {
        dataZoom: { yAxisIndex: 'none', title: { zoom: 'Zoom', back: 'Reset Zoom' } },
        restore: { title: 'Restore' },
        dataView: {
          title: 'Data View',
          readOnly: true,
          backgroundColor: '#1e1e1e',
          textareaColor: '#252525',
          textColor: '#e0e0e0',
          buttonColor: '#1565c0',
          buttonTextColor: '#fff',
          optionToContent: buildDataViewContent,
        },
        saveAsImage: { title: 'Save Image', name: `results-${projectKey}`, pixelRatio: 2 },
      },
    },
    tooltip: {
      trigger: 'axis',
      order: 'seriesDesc',
      axisPointer: { type: 'line' },
      backgroundColor: '#1a1a1a',
      borderColor: '#3a3a3a',
      borderWidth: 1,
      textStyle: { color: '#e0e0e0', fontSize: 10 },
    },
    legend: {
      data: STATUS_ORDER.map((s) => s.replace('_', ' ')),
      bottom: 0,
      textStyle: { color: '#e0e0e0', fontSize: 12 },
    },
    grid: { left: '2%', right: '2%', bottom: '6%', top: '7%', containLabel: true },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: categories,
      axisLabel: {
        show: true,
        interval: labelInterval,
        color: '#9e9e9e',
        fontSize: 11,
        formatter: (value: string) => labelMap.get(value) ?? value,
      },
      axisTick: { show: true, interval: labelInterval },
    },
    yAxis: {
      type: 'value',
      minInterval: 1,
      axisLabel: { color: '#e0e0e0' },
      splitLine: { lineStyle: { color: '#333' } },
    },
    series,
  };
}
