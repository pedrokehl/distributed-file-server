const fileService = require('./file-service');
const socketService = require('./socket-service');

fileService.checkMainDir();
socketService.init('123');