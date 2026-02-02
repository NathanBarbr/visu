
// Map of common codes (reused and expanded)
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
    "1": "Céréales - Blé tendre",
    "2": "Céréales - Maïs",
    "3": "Céréales - Orge",
    "4": "Autres céréales",
    "5": "Oléagineux - Colza",
    "6": "Oléagineux - Tournesol",
    "7": "Autres oléagineux",
    "11": "Gel / Jachère",
    "14": "Riz",
    "15": "Légumineuses",
    "16": "Fourrage",
    "17": "Estives / Landes",
    "18": "Prairies Permanentes",
    "19": "Prairies Temporaires",
    "20": "Vergers",
    "21": "Vignes",
    "22": "Fruits à coque",
    "24": "Autres cultures indus.",
    "25": "Légumes/Fleurs",
    "28": "Divers / Autres"
};

const getLabel = (code) => CODE_LABELS[code] || code;
const formatNumber = (num) => new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 0 }).format(num);

async function init() {
    try {
        const response = await fetch('data_hierarchy_france.json');
        if (!response.ok) throw new Error("Erreur chargement JSON");
        const data = await response.json();

        createVisualization(data);
    } catch (error) {
        console.error(error);
    }
}

function createVisualization(data) {
    const width = document.getElementById('visualization').clientWidth;
    const height = document.getElementById('visualization').clientHeight;

    // Color scale for groups (Top level) - Manual palette to ensure stability
    const palette = [
        "#0ea5e9", // Sky Blue
        "#22c55e", // Green
        "#eab308", // Yellow
        "#f97316", // Orange
        "#ef4444", // Red
        "#a855f7", // Purple
        "#ec4899", // Pink
        "#6366f1", // Indigo
        "#14b8a6", // Teal
        "#f43f5e"  // Rose
    ];
    const color = d3.scaleOrdinal(palette);

    // Create Hierarchy
    const root = d3.hierarchy(data)
        .sum(d => d.children ? 0 : d.value)
        .sort((a, b) => b.value - a.value);

    // Pack layout
    const pack = d3.pack()
        .size([width, height])
        .padding(width * 0.02); // 2% padding relative to width

    const nodes = pack(root);

    const svg = d3.select("#visualization")
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", [0, 0, width, height])
        .style("background", "transparent")
        .on("click", (event) => zoom(event, root));

    // Focus state
    let focus = root;
    let view;

    // Circles
    const circle = svg.append("g")
        .selectAll("circle")
        .data(root.descendants().slice(1))
        .join("circle")
        .attr("fill", d => d.children ? color(d.data.name) : "white")
        .attr("fill-opacity", d => d.children ? 0.2 : 0.6)
        .attr("stroke", d => d.children ? color(d.data.name) : "none")
        .attr("stroke-width", d => d.children ? 1 : 0)
        .on("mouseover", function (event, d) {
            if (d !== focus) {
                d3.select(this).attr("stroke", "white").attr("stroke-width", 2);
            }
            updateSidebar(d);
        })
        .on("mouseout", function (event, d) {
            if (d !== focus) {
                d3.select(this).attr("stroke", d.children ? color(d.data.name) : "none").attr("stroke-width", d.children ? 1 : 0);
            }
        })
        .on("click", (event, d) => zoom(event, d));

    // Labels (New)
    const label = svg.append("g")
        .style("font", "14px 'Outfit', sans-serif")
        .style("pointer-events", "none")
        .style("text-anchor", "middle")
        .style("text-shadow", "0 2px 4px rgba(0,0,0,0.8)")
        .selectAll("text")
        .data(root.descendants().slice(1))
        .join("text")
        .style("fill", "white")
        .style("opacity", d => d.parent === root ? 1 : 0) // Initially only show top groups
        .text(d => {
            const name = getLabel(d.data.name);
            return name.length > 20 ? name.substring(0, 18) + "..." : name;
        });

    // Nodes zoom logic
    const getTargetViewSize = (d) => {
        const diameter = d.r * 2;
        const scaleAdjust = width / Math.min(width, height);
        // Add 10% margin
        return diameter * scaleAdjust * 1.1;
    };

    // Initial Zoom to Root
    zoomTo([root.x, root.y, getTargetViewSize(root)]);

    function zoom(event, d) {
        const focus0 = focus;
        focus = d;

        const targetViewSize = getTargetViewSize(focus);

        const transition = svg.transition()
            .duration(750)
            .tween("zoom", d => {
                const i = d3.interpolateZoom(view, [focus.x, focus.y, targetViewSize]);
                return t => zoomTo(i(t));
            });

        // Labels visibility logic:
        // Show labels only for the direct children of the focused node.
        label.transition(transition)
            .style("opacity", d => d.parent === focus ? 1 : 0);

        // Handle Back Button
        const backBtn = document.getElementById('back-btn');
        if (focus === root) {
            backBtn.style.opacity = '0';
            backBtn.style.pointerEvents = 'none';
        } else {
            backBtn.style.opacity = '1';
            backBtn.style.pointerEvents = 'auto';
            backBtn.onclick = (e) => {
                e.preventDefault();
                e.stopPropagation();
                zoom(e, focus.parent || root);
            }
        }

        if (event) event.stopPropagation();
    }

    function zoomTo(v) {
        const k = width / v[2];
        view = v;

        circle.attr("transform", d => `translate(${(d.x - v[0]) * k + width / 2},${(d.y - v[1]) * k + height / 2})`)
            .attr("r", d => d.r * k);

        label.attr("transform", d => `translate(${(d.x - v[0]) * k + width / 2},${(d.y - v[1]) * k + height / 2})`);
    }
}

function updateSidebar(d) {
    const sidebar = document.getElementById('details');
    sidebar.classList.add('active');

    document.getElementById('d-name').innerText = getLabel(d.data.name);
    document.getElementById('d-surface').innerText = formatNumber(d.value);

    let count = d.data.count;
    if (!count && d.data.children) {
        count = d.leaves().reduce((acc, l) => acc + (l.data.count || 0), 0);
    }
    document.getElementById('d-count').innerText = formatNumber(count || 0);

    const depthMap = ["Région", "Groupe de Culture", "Culture Spécifique"];
    document.querySelector('.breadcrumbs').innerText = depthMap[d.depth] || "Détail";
}

init();
