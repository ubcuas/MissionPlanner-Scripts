const io = require('socket.io-client');

const socket = io('ws://localhost:9001');

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

socket.on('message', async function(data) {
    let statusData = JSON.parse(data.status_data);
    console.log('Received status data:', statusData);
    
    await sleep(500);

    socket.emit("message", "test");
});

socket.on('connect', function() {
    console.log('Connected to the server');
    console.log("emitting message");
    socket.emit("message", "test");
});

socket.on('disconnect', function() {
    console.log('Disconnected from the server');
});