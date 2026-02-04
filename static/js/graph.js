console.log("graph.js loaded");

// Get simulation ID from URL
const simId = (typeof SIM_ID !== "undefined") ? SIM_ID : null;

let network;
let nodesDataset;
let edgesDataset;

let simResults = [];
let timer = null;
let currentDay = 0;

// -------------------------
// LOAD GRAPH + SIMULATION DATA
// -------------------------
Promise.all([
    fetch('/admin/person/list').then(r => r.json()),
    fetch('/admin/contact/list').then(r => r.json()),
    simId ? fetch(`/simulation/${simId}/results`).then(r => r.json()) : Promise.resolve(null)
])
.then(([personsData, contactsData, simData]) => {

    console.log("Data Loaded:", personsData, contactsData, simData);

    // Build nodes
    let nodes = personsData.persons.map(p => ({
        id: p.id,
        label: p.name,
        color: {
            background: "#4c87ff",
            border: "#2a6ad4"
        },
        size: 16
    }));

    // Build edges
    let edges = contactsData.contacts.map(c => ({
        from: c.person1_id,
        to: c.person2_id,
        width: c.weight * 2
    }));

    // Create datasets
    nodesDataset = new vis.DataSet(nodes);
    edgesDataset = new vis.DataSet(edges);

    // Create network
    network = new vis.Network(
        document.getElementById("network"),
        { nodes: nodesDataset, edges: edgesDataset },
        {
            nodes: { shape: "dot", borderWidth: 2 },
            physics: false // Keep graph stable for animation
        }
    );

    // Enable animation if simulation exists
    if (simData && simData.results) {
        simResults = simData.results;
        setupAnimationControls(simResults);
    }
})
.catch(err => {
    console.error("Graph Load Error:", err);
});


// ------------------------------------------------------
// ANIMATION CONTROLS
// ------------------------------------------------------
function setupAnimationControls(results) {
    let maxDay = results.length - 1;

    const slider = document.getElementById("daySlider");
    const dayLabel = document.getElementById("dayLabel");

    slider.max = maxDay;
    dayLabel.innerText = 0;

    document.getElementById("playBtn").onclick = () => startAnimation(maxDay);
    document.getElementById("pauseBtn").onclick = pauseAnimation;

    slider.oninput = function () {
        pauseAnimation();
        showDay(parseInt(this.value));
    };

    showDay(0); // initial state
}


// ------------------------------------------------------
// PLAY ANIMATION
// ------------------------------------------------------
function startAnimation(maxDay) {
    pauseAnimation(); 

    timer = setInterval(() => {
        showDay(currentDay);

        document.getElementById("daySlider").value = currentDay;
        document.getElementById("dayLabel").innerText = currentDay;

        currentDay++;

        if (currentDay > maxDay) {
            pauseAnimation();
        }

    }, 1000); // Animate 1 second per day
}

function pauseAnimation() {
    if (timer) clearInterval(timer);
    timer = null;
}


// ------------------------------------------------------
// RENDER A SPECIFIC DAY
// ------------------------------------------------------
function showDay(day) {
    currentDay = day;
    document.getElementById("dayLabel").innerText = day;

    let result = simResults.find(r => r.day === day);
    if (!result) return;

    // 1. Reset all nodes → Healthy (Blue)
    nodesDataset.forEach(node => {
        nodesDataset.update({
            id: node.id,
            color: {
                background: "#4c87ff",
                border: "#2a6ad4"
            },
            size: 16
        });
    });

    // 2. Mark all infected until today → Red
    simResults.forEach(r => {
        if (r.day <= day) {
            r.infected.forEach(id => {
                nodesDataset.update({
                    id: id,
                    color: {
                        background: "#ff4444",
                        border: "#cc0000"
                    },
                    size: 18
                });
            });
        }
    });

    // 3. Newly infected today → Orange
    result.newly_infected.forEach(id => {
        nodesDataset.update({
            id: id,
            color: {
                background: "#ff9900",
                border: "#cc7700"
            },
            size: 20
        });
    });

    // 4. Patient Zero = bright red and large
    let day0 = simResults.find(r => r.day === 0);
    if (day0 && day0.newly_infected.length > 0) {
        let pz = day0.newly_infected[0];
        nodesDataset.update({
            id: pz,
            color: {
                background: "#ff0000",
                border: "#bb0000"
            },
            size: 25
        });
    }

    // Force redraw
    network.redraw();
}
