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
    return new Promise((resolve, reject) => {
        fs.unlink(fullPath, (err, res) => {
            if (err) reject(err);
            else resolve(res);
        });
    });
}

// Get UTF8 file and already convert it into BASE64
function readFile(filePath) {
    const fullPath = mainDir + filePath;
    return new Promise((resolve, reject) => {
        fs.readFile(fullPath, 'base64', (err, res) => {
            console.log('err:' + err);
            if (err) reject(err);
            else resolve(res);
        });
    });
}

function writeFile(filePath, base64file) {
    const file = convertBase64toBinary(base64file);
    const fullPath = mainDir + filePath;
    return new Promise((resolve, reject) => {
        fs.writeFile(fullPath, file, (err, res) => {
            if (err) reject(err);
            else resolve(res);
        });
    });
}

function convertBase64toBinary(base64) {
    return Buffer.from(base64, 'base64');
}

module.exports = {
    checkMainDir,
    deleteFile,
    readFile,
    writeFile
};