const io = require('socket.io-client');
const fileService = require('./file-service');

const serverManager = 'http://localhost:8000/';

function init(socketId) {
    const socket = io(serverManager, { query: {id: socketId} });
    socket.on('connect', () => {
        console.log("socket connected");
    });

    socket.on('upload-file', (file, callback) => {
        fileService.writeFile(file.filename, file.file)
            .then(callback)
            .catch(callback);
    });

    socket.on('download-file', (filePath, callback) => {
        fileService.readFile(filePath)
            .then(callback)
            .catch(callback);
    });

    socket.on('delete-file', (filePath, callback) => {
        fileService.deleteFile(filePath)
            .then(callback)
            .catch(callback);
    });
}

module.exports = { init };