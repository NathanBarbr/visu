// Map of common codes
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

// Palette cohérente avec le thème sombre et élégant
const COLORS = {
    bar: "#f5f5f7",
    barHover: "#a1a1a6",
    // Donut chart - palette harmonieuse avec des tons chauds/terreux
    palette: ["#7C9A7C", "#D4A574", "#C9A87C", "#9B8AA6", "#8FA3B0", "#636366"]
    // Vert sauge, Terracotta, Doré, Mauve, Bleu-gris, Gris
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
        document.body.innerHTML += `<div style="color:#ff453a; text-align:center; margin-top:2rem">
            Erreur: Impossible de charger 'data_summary_france.json'.<br>
            Assurez-vous de lancer ce fichier via un serveur local (ex: python -m http.server)
        </div>`;
    }
}

function renderKPIs(data) {
    const totalSurface = data.group.reduce((acc, curr) => acc + curr.surface, 0);
    const totalParcels = data.group.reduce((acc, curr) => acc + curr.count, 0);

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
    const dataset = data.slice(0, 15);

    const margin = { top: 20, right: 30, bottom: 40, left: 150 };
    const container = document.getElementById('chart-culture');
    const width = container.clientWidth - margin.left - margin.right;
    const height = 420 - margin.top - margin.bottom;

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
        .padding(0.25);

    // Axes
    svg.append("g")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(x).ticks(5).tickFormat(d => formatNumber(d) + " ha"))
        .selectAll("text")
        .style("fill", "#86868b")
        .style("font-size", "11px");

    svg.append("g")
        .call(d3.axisLeft(y))
        .selectAll("text")
        .style("fill", "#a1a1a6")
        .style("font-size", "12px");

    // Style des lignes d'axes
    svg.selectAll(".domain, .tick line")
        .style("stroke", "#3a3a3c");

    // Barres - en blanc/gris clair pour cohérence
    svg.selectAll("myRect")
        .data(dataset)
        .join("rect")
        .attr("x", x(0))
        .attr("y", d => y(getLabel(d.code)))
        .attr("width", 0)
        .attr("height", y.bandwidth())
        .attr("fill", COLORS.bar)
        .attr("rx", 3)
        .style("cursor", "pointer")
        .on("mouseover", function () {
            d3.select(this).attr("fill", COLORS.barHover);
        })
        .on("mouseout", function () {
            d3.select(this).attr("fill", COLORS.bar);
        })
        .transition()
        .duration(800)
        .delay((d, i) => i * 50)
        .attr("width", d => x(d.surface));
}

function renderGroupChart(data) {
    const top5 = data.slice(0, 5);
    const others = data.slice(5);
    const othersSurface = others.reduce((acc, curr) => acc + curr.surface, 0);

    const plotData = [...top5, { code: "OTHER", surface: othersSurface, count: 0 }];

    const width = 280;
    const height = 280;
    const radius = Math.min(width, height) / 2;

    const svg = d3.select("#chart-group")
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", `0 0 ${width} ${height}`)
        .append("g")
        .attr("transform", `translate(${width / 2},${height / 2})`);

    // Palette en dégradé de gris/blanc
    const color = d3.scaleOrdinal()
        .domain(plotData.map(d => d.code))
        .range(COLORS.palette);

    const pie = d3.pie()
        .value(d => d.surface)
        .sort(null);

    const arc = d3.arc()
        .innerRadius(radius * 0.55)
        .outerRadius(radius * 0.85);

    const arcs = svg.selectAll("arc")
        .data(pie(plotData))
        .enter()
        .append("g")
        .attr("class", "arc");

    arcs.append("path")
        .attr("d", arc)
        .attr("fill", d => color(d.data.code))
        .attr("stroke", "#2c2c2e")
        .attr("stroke-width", 2)
        .style("cursor", "pointer")
        .transition()
        .duration(800)
        .attrTween("d", function (d) {
            var i = d3.interpolate(d.startAngle, d.endAngle);
            return function (t) {
                d.endAngle = i(t);
                return arc(d);
            }
        });

    // Légende
    const legendContainer = d3.select("#chart-group")
        .append("div")
        .style("display", "flex")
        .style("flex-wrap", "wrap")
        .style("justify-content", "center")
        .style("margin-top", "24px")
        .style("gap", "12px 20px");

    const legendItems = legendContainer.selectAll(".legend-item")
        .data(plotData)
        .enter()
        .append("div")
        .style("display", "flex")
        .style("align-items", "center")
        .style("font-size", "0.85rem")
        .style("color", "#a1a1a6");

    legendItems.append("div")
        .style("width", "10px")
        .style("height", "10px")
        .style("border-radius", "3px")
        .style("background-color", d => color(d.code))
        .style("margin-right", "8px");

    legendItems.append("span")
        .text(d => d.code === "OTHER" ? "Autres" : getLabel(d.code));
}

init();
