// This will simulate live coordinate updates
setInterval(() => {
    let lat = (12.9716 + Math.random() * 0.01).toFixed(4);
    let lng = (77.5946 + Math.random() * 0.01).toFixed(4);
    document.getElementById('lat').innerText = lat;
    document.getElementById('lng').innerText = lng;
}, 3000);