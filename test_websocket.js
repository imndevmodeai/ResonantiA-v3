const WebSocket = require('ws');

const ws = new WebSocket('ws://localhost:3004');

ws.on('open', function open() {
  console.log('Connected to WebSocket server');
  
  // Send the complete Fog of War benchmark query
  const testMessage = "Benchmark Query 2: The 'Fog of War' Query - Design a comprehensive strategy for navigating an unknown competitive landscape where information is limited, risks are high, and the stakes involve significant resource allocation. The strategy must account for multiple unknown variables, potential adversarial actions, and the need for rapid adaptation to emerging intelligence.";
  console.log('Sending Fog of War benchmark query...');
  ws.send(testMessage);
});

ws.on('message', function message(data) {
  console.log('Received:', data.toString());
});

ws.on('error', function error(err) {
  console.error('WebSocket error:', err);
});

ws.on('close', function close() {
  console.log('WebSocket connection closed');
});

// Close after 60 seconds to allow for full processing
setTimeout(() => {
  ws.close();
  process.exit(0);
}, 60000); 