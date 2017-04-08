const socket = require('socket.io-client')('http://localhost:8000');

socket.on('connect', () => {
    console.log("socket connected");
});

socket.on('upload-file', (file) => {
    console.log(file);
});

socket.on('download-file', (file) => {
    console.log(file);
});

socket.on('delete-file', (file) => {
    console.log(file);
    socket.emit('file-deleted', file);
});
