Distributed File Server
=======================

### Summary of features

- A Python application that works like a manager to control the file-servers and get the requests from the clients.
- A node.JS server that can have multiple instances in different environments that store the files
- Balance the number of files per server, as file-servers connects and clients send files
- Restrict 36 files per directory, if it exceeds, should create a new directory


![alt text](https://github.com/pedrokehl/distributed-file-server/blob/master/docs/distributed-file-server-diagram.png "Distributed File Server Diagram")

### Client

Not implemented yet.
Responsible for sending requests to the manager.

### File Manager
Implemented with Python using the Flask framework to provide a REST API, MongoDB to persist files and Socket.IO to communicate with File Servers

- Receive client requests
- Control which server should receive which file
- Persist information about files
- Balance servers


![alt text](https://github.com/pedrokehl/distributed-file-server/blob/master/docs/manager-diagram.png "File Manager Diagram")


### File Server
Implemented with node.JS using socket.IO to communicate with the File Manager.

- Connect with manager using Socket.IO
- Receive manager requests like:
    - delete-file
    - upload-file
    - download-file
    - transfer-file
- Control how many files per directory to do not exceed the number provided (36) then create another

## Requirements

- Can have many file-servers running simultaneously
- A file send to the File-Manager should be saved in only one server
- There's no replication between file-servers
- A file server must have only 36 files/folder per directory
- The client will send a base64 file, but the file-server must save it as a normal

### Upload File
Store a file in one of the file-servers

##### Request
POST: [http://localhost:8000/file](http://localhost:8000/file)

Body:

| Field         | Description     | Required |
| ------------- |-------------| :---------: |
| filename | Name of the file, will be used to get the file later | X |
| file | Content of the file encoded in base64 | X |
##### Response

- filename: Filename provided
- id: Generated ID for the file saved

### Download file
Get the content of the file with the name provided

GET: [http://localhost:8000/file/:filename](http://localhost:8000/file/:filename)

### Delete file
Delete the file of the file with the name provided

DELETE: [http://localhost:8000/file/:filename](http://localhost:8000/file/:filename)


### Response codes

Code  | Content              | Description
------- | ---------------------- | ------------
1       | Servers unavailable  | When no server is available
2       | File does not exist    | When the client request a file that does not exists
3       | File name already exists | When the client tries to upload a file with a name that is already in use
4       | File unavailable   | When the server of the file requests is unavailable


### Instructions

    # Clone de project
    git clone --depth=1 https://github.com/pedrokehl/distributed-file-server.git
    
    # Run MongoDB
    Execute mongod
    
    # Go to file-server-manager directory
    cd distributed-file-server/file-server-storage
    
    # Install Python dependencies
    pip install -r requirements.txt
    
    # Run the manager
    python main.py
    
    # go to file-server-storage directory
    cd ../file-server-storage
    
    # Install dependencies
    npm install
    
    # Start the server with the server id
    node index.js 100

### TODO

- Implement the client
- Change the manager to accept files directly instead of base64