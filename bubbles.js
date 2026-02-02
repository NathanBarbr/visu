
// Map of common codes (reused)
const CODE_LABELS = {
    "PPH": "Prairies permanentes", "SPH": "Surface pastorale", "BTH": "Blé tendre",
    "MIS": "Maïs", "PTR": "Prairie temporaire", "ORH": "Orge d'hiver",
    "TTH": "Triticale", "TRN": "Tournesol", "CZH": "Colza",
    "MLG": "Mélange Gram/Légu", "LUZ": "Luzerne", "VRC": "Vignes",
    "JAC": "Jachère", "SOJ": "Soja", "SNE": "Non exploité",
    "NOX": "Noyer", "VRG": "Verger", "SGH": "Seigle",
    "BTP": "Blé détruit", "LIH": "Lin", "SPL": "Surf. pasto. ligneuse",
    "BOR": "Bordures", "OLI": "Oliviers", "MDI": "Maïs doux"
};
const getLabel = (code) => CODE_LABELS[code] || code;

async function init() {
    try {
        const response = await fetch('data_summary_france.json');
        const data = await response.json();
        createBubbleChart(data.culture);
    } catch (e) { console.error(e); }
}

function createBubbleChart(data) {
    // Process data: Calculate Avg Size and filter small items to avoid clutter
    let dataset = data.map(d => ({
        ...d,
        label: getLabel(d.code),
        avgSize: d.surface / d.count,
    })).filter(d => d.surface > 1000 && d.count > 100); // Filter out noise

    const container = document.getElementById('chart');
    const width = container.clientWidth;
    const height = container.clientHeight;
    const margin = { top: 40, right: 100, bottom: 60, left: 80 };

    const svg = d3.select("#chart")
        .append("svg")
        .attr("width", width)
        .attr("height", height);

    // X Axis: Average Parcel Size (Log scale maybe better?)
    // Let's use Linear first, but limits are 0 to ~8ha
    const x = d3.scaleLinear()
        .domain([0, d3.max(dataset, d => d.avgSize) * 1.1])
        .range([margin.left, width - margin.right]);

    // Y Axis: Total Surface (Log scale highly recommended as sizes span 10^3 to 10^6)
    const y = d3.scaleLog()
        .domain([1000, d3.max(dataset, d => d.surface) * 1.5])
        .range([height - margin.bottom, margin.top]);

    // Bubble Size: Number of Parcels? Or just fixed?
    // Let's use Count for radius to show "frequency"
    const z = d3.scaleSqrt()
        .domain([0, d3.max(dataset, d => d.count)])
        .range([4, 40]);

    // Color: just pretty
    const color = d3.scaleOrdinal(d3.schemeSpectral[11]);

    // Grid
    svg.append("g")
        .attr("class", "grid")
        .attr("transform", `translate(0,${height - margin.bottom})`)
        .call(d3.axisBottom(x).ticks(10).tickSize(-(height - margin.top - margin.bottom)).tickFormat(""))

    svg.append("g")
        .attr("class", "grid")
        .attr("transform", `translate(${margin.left},0)`)
        .call(d3.axisLeft(y).ticks(5).tickSize(-(width - margin.left - margin.right)).tickFormat(""))

    // Axes
    svg.append("g")
        .attr("transform", `translate(0,${height - margin.bottom})`)
        .call(d3.axisBottom(x).ticks(10).tickFormat(d => d + " ha"))
        .attr("class", "axis");

    svg.append("g")
        .attr("transform", `translate(${margin.left},0)`)
        .call(d3.axisLeft(y).ticks(5, "~s"))
        .attr("class", "axis");

    // Axis Labels
    svg.append("text")
        .attr("x", width / 2)
        .attr("y", height - 20)
        .attr("fill", "#94a3b8")
        .style("text-anchor", "middle")
        .text("Surface Moyenne d'une Parcelle (Hectares)");

    svg.append("text")
        .attr("transform", "rotate(-90)")
        .attr("x", -height / 2)
        .attr("y", 25)
        .attr("fill", "#94a3b8")
        .style("text-anchor", "middle")
        .text("Surface Totale Cultivée (Logarithmique)");

    // Bubbles
    const tooltip = d3.select("#tooltip");

    const bubbles = svg.append("g")
        .selectAll("circle")
        .data(dataset)
        .join("circle")
        .attr("class", "bubble")
        .attr("cx", d => x(d.avgSize))
        .attr("cy", d => y(d.surface))
        .attr("r", d => z(d.count))
        .style("fill", (d, i) => color(i))
        .style("opacity", 0.7)
        .on("mouseover", (event, d) => {
            tooltip.style("opacity", 1)
                .html(`
                    <strong style="color:${color(dataset.indexOf(d))}">${d.label}</strong><br>
                    Surface Moyenne: <b>${d.avgSize.toFixed(2)} ha</b><br>
                    Surface Totale: <b>${Math.round(d.surface).toLocaleString()} ha</b><br>
                    Nombre Parcelles: <b>${d.count}</b>
                `)
                .style("left", (event.pageX + 15) + "px")
                .style("top", (event.pageY - 28) + "px");
        })
        .on("mouseout", () => tooltip.style("opacity", 0));

    // Labels for big bubbles
    svg.append("g")
        .selectAll("text")
        .data(dataset.filter(d => d.count > 5000 || d.surface > 50000))
        .join("text")
        .attr("class", "label")
        .attr("x", d => x(d.avgSize))
        .attr("y", d => y(d.surface))
        .attr("dy", d => -z(d.count) - 5) // above bubble
        .text(d => d.label);

}

init();
