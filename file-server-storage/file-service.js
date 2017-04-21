const fs = require('fs');
const path = require('path');

const MAX_FILES = 36;
const SUB_FOLDER = 'more';

let mainDir;
let dirInfo;

// Sync to hold requests while main directory is not created
function checkMainDir(dirSuffix) {
    mainDir = 'files_' + dirSuffix;
    if (!fs.existsSync(mainDir)) {
        fs.mkdirSync(mainDir);
        dirInfo = {
            allFiles: [],
            dirLen: 0,
            dirPath: mainDir,
            filesDict: {}
        }
    } else {
        dirInfo = walkFolders(mainDir);
        checkToCreateSubFolder();
    }
}

function walkFolders(dirPath, allFiles, filesDict) {
    const files = fs.readdirSync(dirPath);
    let res = {
        allFiles: allFiles || [],
        dirLen: files.length,
        filesDict: filesDict || {},
        dirPath
    };

    files.forEach((file) => {
        const filePath = path.join(dirPath, file);
        if (fs.statSync(filePath).isDirectory()) {
            res = walkFolders(filePath, res.allFiles, res.filesDict);
        }
        else {
            res.allFiles.push(file);
            res.filesDict[file] = filePath;
        }
    });
    return res;
}

function checkToCreateSubFolder() {
    if(dirInfo.dirLen + 1 >= MAX_FILES) {
        const newFolder = path.join(dirInfo.dirPath, SUB_FOLDER);
        fs.mkdirSync(newFolder);
        dirInfo.dirPath = newFolder;
        dirInfo.dirLen = 0;
    }
}

function deleteFile(filename) {
    return new Promise((resolve, reject) => {
        fs.unlink(dirInfo.filesDict[filename], (err, res) => {
            if (err) reject(err);
            else {
                delete dirInfo.filesDict[filename];
                resolve(res);
            }
        });
    });
}

// Get UTF8 file and already convert it into BASE64
function readFile(filename) {
    return new Promise((resolve, reject) => {
        fs.readFile(dirInfo.filesDict[filename], (err, res) => {
            if (err) reject(err);
            else resolve(convertBinaryToBase64(res));
        });
    });
}

function writeFile(filename, base64file) {
    const file = convertBase64ToBinary(base64file);
    const fullPath = path.join(dirInfo.dirPath, filename);
    return new Promise((resolve, reject) => {
        fs.writeFile(fullPath, file, (err, res) => {
            if (err) reject(err);
            else resolve(res);
            dirInfo.dirLen++;
            dirInfo.filesDict[filename] = fullPath;
            checkToCreateSubFolder();
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