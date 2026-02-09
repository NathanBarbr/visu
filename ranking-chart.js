
// Ranking Chart Logic
let rankingData = null;

async function initRanking() {
    try {
        const res = await fetch('data_rankings.json');
        rankingData = await res.json();

        populateSelect();

        // Select first available culture by default (e.g. Wheat)
        const defaultCult = "BTH";
        if (rankingData[defaultCult]) {
            document.getElementById('culture-select').value = defaultCult;
            renderRanking(defaultCult);
        } else {
            // Fallback to first key
            const first = Object.keys(rankingData)[0];
            if (first) {
                document.getElementById('culture-select').value = first;
                renderRanking(first);
            }
        }

        document.getElementById('culture-select').addEventListener('change', (e) => {
            renderRanking(e.target.value);
        });

    } catch (e) {
        console.error("Error loading ranking data", e);
    }
}

function populateSelect() {
    const select = document.getElementById('culture-select');

    // Sort cultures by total surface (if available in structure, otherwise just name)
    // Structure is { cultCode: [{region, surface}, ...] }
    // Let's compute total surface to sort list
    const options = Object.keys(rankingData).map(code => {
        const total = rankingData[code].reduce((sum, r) => sum + r.surface, 0);
        return {
            code,
            label: (window.CODE_LABELS && window.CODE_LABELS[code]) || code,
            total
        };
    });

    options.sort((a, b) => b.total - a.total);

    options.forEach(opt => {
        const el = document.createElement('option');
        el.value = opt.code;
        el.textContent = `${opt.label}`;
        select.appendChild(el);
    });
}

function renderRanking(code) {
    const data = rankingData[code];
    if (!data) return;

    // Top regions
    const container = document.getElementById('ranking-chart');
    container.innerHTML = '';

    const width = container.clientWidth;
    const height = 400;
    const margin = { top: 20, right: 60, bottom: 20, left: 160 }; // increased left margin for region names

    const svg = d3.select("#ranking-chart")
        .append("svg")
        .attr("width", width)
        .attr("height", height);

    const x = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.surface)])
        .range([margin.left, width - margin.right]);

    const y = d3.scaleBand()
        .domain(data.map(d => d.region))
        .range([margin.top, height - margin.bottom])
        .padding(0.2);

    // Color scale based on surface intensity or just a nice blue
    const color = d3.scaleSequential()
        .domain([0, d3.max(data, d => d.surface)])
        .interpolator(d3.interpolateBlues);

    // Bars
    svg.append("g")
        .selectAll("rect")
        .data(data)
        .join("rect")
        .attr("x", x(0))
        .attr("y", d => y(d.region))
        .attr("width", d => x(d.surface) - x(0))
        .attr("height", y.bandwidth())
        .attr("fill", "#0a84ff") // Flat blue for cleanliness or dynamic
        .attr("rx", 4)
        .on("mouseover", function (event, d) {
            d3.select(this).attr("opacity", 0.8);
            // Tooltip logic similar to other charts
            const tooltip = d3.select("#tooltip");
            if (!tooltip.empty()) {
                tooltip.style("opacity", 1)
                    .html(`<strong>${d.region}</strong><br>
                                 Surface: <b>${Math.round(d.surface).toLocaleString()} ha</b>`)
                    .style("left", (event.pageX + 15) + "px")
                    .style("top", (event.pageY - 28) + "px");
            }
        })
        .on("mouseout", function () {
            d3.select(this).attr("opacity", 1);
            d3.select("#tooltip").style("opacity", 0);
        });

    // Labels (Region names)
    svg.append("g")
        .attr("transform", `translate(${margin.left},0)`)
        .call(d3.axisLeft(y).tickSize(0))
        .select(".domain").remove()
        .selectAll("text")
        .style("font-size", "0.85rem")
        .style("fill", "#f5f5f7")
        .style("text-anchor", "end")
        .attr("dx", "-10px");

    // Values at end of bars
    svg.append("g")
        .selectAll("text")
        .data(data)
        .join("text")
        .attr("x", d => x(d.surface) + 5)
        .attr("y", d => y(d.region) + y.bandwidth() / 2)
        .attr("dy", "0.35em")
        .text(d => Math.round(d.surface).toLocaleString() + " ha")
        .style("font-size", "0.75rem")
        .style("fill", "#a1a1a6");

}
