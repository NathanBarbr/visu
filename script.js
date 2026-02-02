
// Map of common codes (incomplete, but covers top items)
const CODE_LABELS = {
    "PPH": "Prairies permanentes",
    "SPH": "Surface pastorale",
    "BTH": "Blé tendre d'hiver",
    "MIS": "Maïs",
    "PTR": "Prairie temporaire",
    "ORH": "Orge d'hiver",
    "TTH": "Triticale d'hiver",
    "TRN": "Tournesol",
    "CZH": "Colza d'hiver",
    "MLG": "Mélange Gram./Légum.",
    "LUZ": "Luzerne",
    "VRC": "Vigne (Cuve)",
    "JAC": "Jachère",
    "SOJ": "Soja",
    "SNE": "Surf. non exploitée",
    "NOX": "Noyer",
    "VRG": "Verger",
    "SGH": "Seigle d'hiver",
    "BTP": "Blé tendre détruit",
    // Groups
    "1": "Blé tendre",
    "2": "Maïs",
    "3": "Orge",
    "4": "Autres céréales",
    "5": "Colza",
    "6": "Tournesol",
    "7": "Autres oléagineux",
    "11": "Gel / Jachère",
    "14": "Riz",
    "15": "Légumineuses",
    "16": "Fourrage",
    "17": "Estives / Landes",
    "18": "Prairies Perm.",
    "19": "Prairies Temp.",
    "20": "Vergers",
    "21": "Vignes",
    "22": "Fruits à coque",
    "24": "Autres indus.",
    "25": "Légumes/Fleurs",
    "28": "Divers / Autres"
};

const getLabel = (code) => CODE_LABELS[code] || code;

const formatNumber = (num) => new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 0 }).format(num);

async function init() {
    try {
        const response = await fetch('data_summary_france.json');
        if (!response.ok) throw new Error("Erreur chargement JSON");
        const data = await response.json();

        renderKPIs(data);
        renderCultureChart(data.culture);
        renderGroupChart(data.group);

    } catch (error) {
        console.error(error);
        document.body.innerHTML += `<div style="color:red; text-align:center; margin-top:2rem">
            Erreur: Impossible de charger 'data_summary.json'.<br>
            Assurez-vous de lancer ce fichier via un serveur local (ex: python -m http.server)
        </div>`;
    }
}

function renderKPIs(data) {
    // Calculate totals from 'group' array (it covers everything)
    const totalSurface = data.group.reduce((acc, curr) => acc + curr.surface, 0);
    const totalParcels = data.group.reduce((acc, curr) => acc + curr.count, 0);

    // Animation for numbers
    animateValue("kpi-surface", 0, totalSurface, 1500);
    animateValue("kpi-parcels", 0, totalParcels, 1500);
    animateValue("kpi-avg-size", 0, totalSurface / totalParcels, 1500, 2);
}

function animateValue(id, start, end, duration, decimals = 0) {
    const obj = document.getElementById(id);
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const value = progress * (end - start) + start;
        obj.innerHTML = new Intl.NumberFormat('fr-FR', {
            maximumFractionDigits: decimals,
            minimumFractionDigits: decimals
        }).format(value);
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

function renderCultureChart(data) {
    // Top 15
    const dataset = data.slice(0, 15);

    const margin = { top: 20, right: 30, bottom: 40, left: 150 };
    const width = document.getElementById('chart-culture').clientWidth - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    const svg = d3.select("#chart-culture")
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    const x = d3.scaleLinear()
        .domain([0, d3.max(dataset, d => d.surface)])
        .range([0, width]);

    const y = d3.scaleBand()
        .range([0, height])
        .domain(dataset.map(d => getLabel(d.code)))
        .padding(0.2);

    svg.append("g")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(x).ticks(5).tickFormat(d => formatNumber(d) + " ha"))
        .selectAll("text")
        .style("opacity", 0.7);

    svg.append("g")
        .call(d3.axisLeft(y))
        .selectAll("text")
        .style("font-size", "12px");

    // Bars
    svg.selectAll("myRect")
        .data(dataset)
        .join("rect")
        .attr("class", "bar")
        .attr("x", x(0))
        .attr("y", d => y(getLabel(d.code)))
        .attr("width", 0) // animate from 0
        .attr("height", y.bandwidth())
        .transition()
        .duration(1000)
        .attr("width", d => x(d.surface));

    // Tooltip logic could be added here
}

function renderGroupChart(data) {
    // Prepare data: Top 5 + Others
    const top5 = data.slice(0, 5);
    const others = data.slice(5);
    const othersSurface = others.reduce((acc, curr) => acc + curr.surface, 0);

    const plotData = [...top5, { code: "OTHER", surface: othersSurface, count: 0 }];

    const width = 300;
    const height = 300;
    const radius = Math.min(width, height) / 2;

    // Create SVG with fixed height so legend flows below
    const svg = d3.select("#chart-group")
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", `0 0 ${width} ${height}`)
        .append("g")
        .attr("transform", `translate(${width / 2},${height / 2})`);

    const color = d3.scaleOrdinal()
        .domain(plotData.map(d => d.code))
        .range(["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#64748b"]);

    const pie = d3.pie()
        .value(d => d.surface)
        .sort(null); // keep order

    const arc = d3.arc()
        .innerRadius(radius * 0.5) // Donut
        .outerRadius(radius * 0.8);

    const outerArc = d3.arc()
        .innerRadius(radius * 0.9)
        .outerRadius(radius * 0.9);

    const arcs = svg.selectAll("arc")
        .data(pie(plotData))
        .enter()
        .append("g")
        .attr("class", "arc");

    arcs.append("path")
        .attr("d", arc)
        .attr("fill", d => color(d.data.code))
        .transition()
        .duration(1000)
        .attrTween("d", function (d) {
            var i = d3.interpolate(d.startAngle + 0.1, d.endAngle);
            return function (t) {
                d.endAngle = i(t);
                return arc(d);
            }
        });

    // Legend
    const legendContainer = d3.select("#chart-group")
        .append("div")
        .style("display", "flex")
        .style("flex-wrap", "wrap")
        .style("justify-content", "center")
        .style("margin-top", "20px")
        .style("gap", "15px");

    const legendItems = legendContainer.selectAll(".legend-item")
        .data(plotData)
        .enter()
        .append("div")
        .attr("class", "legend-item")
        .style("display", "flex")
        .style("align-items", "center")
        .style("font-size", "0.9rem")
        .style("color", "#cbd5e1");

    legendItems.append("div")
        .style("width", "12px")
        .style("height", "12px")
        .style("border-radius", "50%")
        .style("background-color", d => color(d.code))
        .style("margin-right", "8px");

    legendItems.append("span")
        .text(d => d.code === "OTHER" ? "Autres" : getLabel(d.code));
}

init();
