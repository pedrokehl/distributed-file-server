const fs = require('fs');
let mainDir;

// Sync to hold requests while main directory is not created
function checkMainDir(dirSuffix) {
    mainDir = './files_' + dirSuffix + '/';
    if (!fs.existsSync(mainDir)) {
        fs.mkdirSync(mainDir);
    }
}

function deleteFile(filePath) {
    const fullPath = mainDir + filePath;
    return new Promise(function (resolve, reject){
        fs.unlink(fullPath, function (err, res){
            if (err) reject(err);
            else resolve(res);
        });
    });
}

// Get UTF8 file and already convert it into BASE64
function readFile(filePath) {
    const fullPath = mainDir + filePath;
    return new Promise(function (resolve, reject){
        fs.readFile(fullPath, 'base64', function (err, res){
            if (err) reject(err);
            else resolve(res);
        });
    });
}

function writeFile(filePath, base64file) {
    const file = convertBase64toUTF8(base64file);
    const fullPath = mainDir + filePath;
    return new Promise(function (resolve, reject){
        fs.writeFile(fullPath, file, function (err, res) {
            if (err) reject(err);
            else resolve(res);
        });
    });
}

function convertBase64toUTF8(base64) {
    return Buffer.from(base64, 'base64').toString('ascii');
}

module.exports = {
    checkMainDir,
    deleteFile,
    readFile,
    writeFile
};