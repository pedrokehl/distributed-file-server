const fileService = require('./file-service');
const socketService = require('./socket-service');

const serverId = process.argv[2];

if (!serverId) {
    console.error('Start the server passing the serverId. (e.a: node server 100)');
    process.exit();
}

fileService.checkMainDir();
socketService.init(serverId);