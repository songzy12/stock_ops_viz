const chart = document.getElementById('{plot_id}');
let activeMarkers = new Set();
function clearMarkers() {
    for (const marker of activeMarkers) marker.style.fill = 'lightcoral';
    activeMarkers.clear();
}
chart.addEventListener('pointermove', event => {
    const trace = chart._fullData.find(item => item.name === 'Operations');
    const plot = chart.querySelector('.nsewdrag');
    if (!trace || trace.visible !== true || !plot) {
        clearMarkers();
        return;
    }
    const plotBounds = plot.getBoundingClientRect();
    if (event.clientX < plotBounds.left || event.clientX > plotBounds.right ||
        event.clientY < plotBounds.top || event.clientY > plotBounds.bottom) {
        clearMarkers();
        return;
    }
    const markers = chart.querySelectorAll('.scatterlayer .trace' + trace.uid + ' .point');
    const matching = new Set();
    for (const marker of markers) {
        const bounds = marker.getBoundingClientRect();
        const x = (bounds.left + bounds.right) / 2;
        if (x >= plotBounds.left && x <= plotBounds.right &&
            Math.abs(event.clientX - x) <= 4) {
            matching.add(marker);
        }
    }
    for (const marker of activeMarkers) {
        if (!matching.has(marker)) marker.style.fill = 'lightcoral';
    }
    for (const marker of matching) {
        if (!activeMarkers.has(marker)) {
            marker.style.fill = 'darkred';
        }
    }
    activeMarkers = matching;
});
chart.addEventListener('pointerleave', clearMarkers);
chart.on('plotly_afterplot', clearMarkers);
