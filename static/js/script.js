// map https://leafletjs.com/examples/quick-start/
var map = L.map('map').setView([33.5014206777, -86.8071344686], 17.5);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);
var marker = L.marker([33.5014206777, -86.8071344686]).addTo(map);