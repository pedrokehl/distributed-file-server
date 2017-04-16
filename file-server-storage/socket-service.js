const io = require('socket.io-client');
const fileService = require('./file-service');

const serverManager = 'http://127.0.0.1:8000/';

function init(socketId) {
    const socket = io(serverManager, { query: {id: socketId} });
    socket.on('connect', () => {
        console.log("socket connected");
    });

    socket.on('connect_error', () => {
        console.error('There is already a file-server with this id or the connection was refused.');
        process.exit(1);
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

    socket.on('transfer-file', (req, callback) => {
        fileService.readFile(req.filename)
            .then((file64) => {
                req.file = file64;
                return req.filename;
            }).then(fileService.deleteFile)
            .then(() => callback(req))
            .catch(callback);
    });
}

module.exports = { init };