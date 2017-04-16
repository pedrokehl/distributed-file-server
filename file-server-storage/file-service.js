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
        fs.readFile(fullPath, (err, res) => {
            if (err) reject(err);
            else resolve(convertBinaryToBase64(res));
        });
    });
}

function writeFile(filePath, base64file) {
    const file = convertBase64ToBinary(base64file);
    const fullPath = mainDir + filePath;
    return new Promise((resolve, reject) => {
        fs.writeFile(fullPath, file, (err, res) => {
            if (err) reject(err);
            else resolve(res);
        });
    });
}

function convertBase64ToBinary(base64) {
    return Buffer.from(base64, 'base64');
}

function convertBinaryToBase64(binary) {
    return new Buffer(binary).toString('base64');
}

module.exports = {
    checkMainDir,
    deleteFile,
    readFile,
    writeFile
};