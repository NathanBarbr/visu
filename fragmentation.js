// Data based on 9.9M parcels (France 2022)
const dataset = [
    { label: "< 1 ha", count: 4371730, percent: 44, color: "#3f51b5", description: "Jardins et micro-parcelles" },
    { label: "1 - 5 ha", count: 4009550, percent: 41, color: "#03a9f4", description: "Petits champs" },
    { label: "5 - 10 ha", count: 985322, percent: 10, color: "#00bcd4", description: "Parcelles moyennes" },
    { label: "10 - 20 ha", count: 413051, percent: 4, color: "#4caf50", description: "Grandes parcelles" },
    { label: "> 20 ha", count: 117124, percent: 1, color: "#8bc34a", description: "Domaines vastes" }
];

// Flat array of 100 items for the grid
const gridData = [];
dataset.forEach(d => {
    for (let i = 0; i < d.percent; i++) {
        gridData.push({ ...d, id: i });
    }
});

function init() {
    createWaffleChart();
    createLegend();
}

function createWaffleChart() {
    const container = document.getElementById('waffle');
    const width = container.clientWidth;
    const height = width; // Square aspect ratio

    // Grid 10x10
    const cols = 10;
    const cellSize = width / cols;

    const svg = d3.select("#waffle")
        .append("svg")
        .attr("width", width)
        .attr("height", height);

    svg.selectAll(".cell")
        .data(gridData)
        .enter()
        .append("rect")
        .attr("class", "cell")
        .attr("x", (d, i) => (i % cols) * cellSize)
        .attr("y", (d, i) => Math.floor(i / cols) * cellSize)
        .attr("width", cellSize)
        .attr("height", cellSize)
        .attr("fill", d => d.color)
        .attr("rx", 4) // Rounded corners
        .attr("ry", 4)
        .style("opacity", 0)
        .transition()
        .duration(50)
        .delay((d, i) => i * 10) // Stagger animation
        .style("opacity", 1);
}

function createLegend() {
    const legend = document.getElementById('legend');

    dataset.forEach(d => {
        const item = document.createElement('div');
        item.className = 'legend-item';
        item.style.borderLeftColor = d.color;
        item.innerHTML = `
            <div class="legend-color" style="background:${d.color}"></div>
            <div class="legend-text">
                <span class="legend-label">${d.percent}% - ${d.label}</span>
                <span class="legend-value">${new Intl.NumberFormat('fr-FR').format(d.count)} parcelles • ${d.description}</span>
            </div>
        `;
        legend.appendChild(item);
    });
}

// Handle resize (simple reload for now)
window.addEventListener('resize', () => {
    document.getElementById('waffle').innerHTML = "";
    createWaffleChart();
});

init();
