const serverManager = 'http://localhost:8000/';
const io = require('socket.io-client');
const fileService = require('./file-service');

function init(socketId) {
    const socket = io(serverManager, { query: socketId });
    socket.on('connect', () => {
        console.log("socket connected");
    });

    socket.on('upload-file', (file, callback) => {
        fileService.writeFile(file.path, file.base64)
            .then(callback)
            .catch((err) => {
                console.log(err);
            });
    });

    socket.on('download-file', (filePath, callback) => {
        fileService.readFile(filePath)
            .then(callback)
            .catch((err) => {
                console.log(err);
            });
    });

    socket.on('delete-file', (filePath, callback) => {
        fileService.deleteFile(filePath)
            .then(callback)
            .catch((err) => {
                console.log(err);
            });
    });
}

module.exports = { init };