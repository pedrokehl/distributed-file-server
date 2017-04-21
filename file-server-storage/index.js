const fileService = require('./file-service');
const socketService = require('./socket-service');

const serverId = process.argv[2];

if (!serverId) {
    console.error('Start the server passing the serverId. (e.a: node index.js 100).');
    process.exit(1);
}

fileService.checkMainDir(serverId);
socketService.init(serverId);