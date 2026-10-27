# Run in the Pj/Pjp editor, or load as a service script with Service... and Run.
import uuid

chart_id = 'mzpj_bars_' + uuid.uuid4().hex
mzpjShowHtml(
    d3_script +
    f'<div id="{chart_id}" data-width="{mzpjFigureSize["width"]}" '
    f'data-height="{mzpjFigureSize["height"]}"></div>' + """
    <script>
    (function () {
        const root = document.getElementById('CHART_ID');
        const values = [12, 25, 18, 31];
        const width = Number(root.dataset.width);
        const height = Number(root.dataset.height);
        const svg = d3.select(root).append('svg')
            .attr('width', width).attr('height', height);
        const scale = d3.scaleLinear().domain([0, d3.max(values)])
            .range([0, Math.max(0, width - 20)]);
        const bands = d3.scaleBand().domain(d3.range(values.length))
            .range([10, Math.max(10, height - 10)]).padding(0.25);
        svg.selectAll('rect').data(values).join('rect')
            .attr('x', 10).attr('y', (d, i) => bands(i))
            .attr('width', d => scale(d)).attr('height', bands.bandwidth())
            .attr('fill', '#3e6da9');
    })();
    </script>
    """.replace('CHART_ID', chart_id),
    name="d3_bars",
    title="D3 bar chart"
)
