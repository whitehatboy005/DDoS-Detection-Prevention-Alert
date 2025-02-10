document.addEventListener("DOMContentLoaded", function () {
    updateStats(); // Load stats on page load
    setInterval(updateStats, 5000); // Refresh every 5 seconds
});

function updateStats() {
    fetch("/api/stats")
        .then(response => response.json())
        .then(data => {
            console.log("Received data:", data);  // ✅ Debugging output
            updateTrafficData(data.traffic);
            updateBlockedIps(data.blocked_ips);  // ✅ Fix key name
        })
        .catch(error => console.error("Error fetching stats:", error));
}

// ✅ Update Traffic Data
function updateTrafficData(traffic) {
    let trafficDiv = document.getElementById("traffic-data");
    trafficDiv.innerHTML = ""; // Clear previous content

    if (Object.keys(traffic).length === 0) {
        trafficDiv.innerHTML = "<p>No traffic data available.</p>";
        return;
    }

    Object.entries(traffic).forEach(([ip, requests]) => {
        let p = document.createElement("p");
        p.textContent = `${ip}: ${requests} requests`;
        trafficDiv.appendChild(p);
    });
}

// ✅ Update Blocked IPs List
function updateBlockedIps(blockedIps) {
    let blockedDiv = document.getElementById("blocked-ips");
    blockedDiv.innerHTML = ""; // Clear previous content

    if (blockedIps.length === 0) {
        blockedDiv.innerHTML = "<p>No blocked IPs.</p>";
        return;
    }

    blockedIps.forEach(ip => {
        let p = document.createElement("p");
        p.textContent = ip;
        blockedDiv.appendChild(p);
    });
}
