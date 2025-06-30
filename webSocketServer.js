const WebSocket = require('ws');

const wss = new WebSocket.Server({ port: 3001 });

wss.on('connection', ws => {
  console.log('Client connected');

  ws.on('message', message => {
    console.log(`Received message: ${message}`);
    ws.send('>>> Executing query...');
    // Echo the message back to the client (for testing purposes)
    // ws.send(`Server received: ${message}`);
  });

  ws.on('close', () => {
    console.log('Client disconnected');
  });

  ws.onerror = () => {
    console.log('websocket error')
  }

  ws.send('Hello from WebSocket server!');
});

console.log('WebSocket server started on port 3001');