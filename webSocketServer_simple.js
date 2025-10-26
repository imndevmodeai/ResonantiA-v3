const WebSocket = require('ws');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');

// Simple logger
const logger = {
  info: (msg, data) => console.log(`[INFO] ${msg}`, data || ''),
  warn: (msg, data) => console.log(`[WARN] ${msg}`, data || ''),
  error: (msg, data) => console.log(`[ERROR] ${msg}`, data || '')
};

// Load port configuration
let port = process.env.WEBSOCKET_PORT || 3005;

try {
  port = parseInt(port, 10);
  if (isNaN(port)) {
    logger.warn('Invalid WEBSOCKET_PORT env var. Using default 3005');
    port = 3005;
  }
} catch (error) {
  logger.warn(`Could not parse WEBSOCKET_PORT, using default port ${port}`);
}

// Create WebSocket server
const wss = new WebSocket.Server({ port });

logger.info(`ArchE WebSocket Server running on port ${port}`);
logger.info(`Connect at: ws://localhost:${port}`);

const clients = new Set();

// Simple message processing without protocol modules
async function processMessage(content, sender = 'user') {
  const timestamp = new Date().toISOString();
  
  const message = {
    id: uuidv4(),
    content,
    timestamp,
    sender: sender === 'assistant' ? 'arche' : sender,
    message_type: 'chat',
    protocol_compliance: true,
    protocol_version: 'v3.1-CA'
  };

  // Add basic protocol simulation
  if (content.toLowerCase().includes('thought')) {
    message.type = 'thought';
    message.metadata = {
      iar_processed: true,
      spr_detected: ['ThoughtTrail'],
      temporal_context: { dimension: '4D', analysis: 'basic' }
    };
  } else if (content.toLowerCase().includes('spr')) {
    message.type = 'spr';
    message.metadata = {
      spr_activations: ['CognitiveResonance'],
      meta_cognitive_state: 'active'
    };
  } else {
    message.type = 'response';
    message.metadata = {
      iar_processed: true,
      protocol_status: 'operational'
    };
  }

  return message;
}

// Handle WebSocket connections
wss.on('connection', (ws, req) => {
  const clientId = uuidv4();
  clients.add(ws);
  
  logger.info(`Client connected: ${clientId}`);
  
  // Send welcome message
  const welcomeMessage = {
    id: uuidv4(),
    type: 'system',
    content: 'Welcome to ArchE Cognitive Bus. Connection established successfully.',
    timestamp: new Date().toISOString(),
    sender: 'arche',
    message_type: 'system',
    protocol_compliance: true,
    protocol_version: 'v3.1-CA'
  };
  
  ws.send(JSON.stringify(welcomeMessage));

  // Handle incoming messages
  ws.on('message', async (data) => {
    try {
      const message = data.toString();
      
      // Handle heartbeat
      if (message === 'heartbeat') {
        ws.send(JSON.stringify({
          id: uuidv4(),
          type: 'system',
          content: 'heartbeat',
          timestamp: new Date().toISOString(),
          sender: 'arche'
        }));
        return;
      }

      logger.info(`Received message: ${message.substring(0, 100)}...`);

      // Process message through ArchE backend
      const processedMessage = await processMessage(message, 'user');
      
      // Send processed message back to client
      ws.send(JSON.stringify(processedMessage));

      // If it's a question, generate a response
      if (message.includes('?') || message.toLowerCase().includes('help')) {
        const response = {
          id: uuidv4(),
          type: 'response',
          content: `I received your message: "${message}". This is a test response from the simplified ArchE WebSocket server. The full protocol modules are not loaded, but basic communication is working.`,
          timestamp: new Date().toISOString(),
          sender: 'arche',
          message_type: 'response',
          protocol_compliance: true,
          protocol_version: 'v3.1-CA',
          metadata: {
            iar_processed: true,
            spr_detected: ['BasicResponse'],
            temporal_context: { dimension: '3D', analysis: 'basic' },
            meta_cognitive_state: 'responsive'
          }
        };
        
        // Send response after a short delay to simulate processing
        setTimeout(() => {
          ws.send(JSON.stringify(response));
        }, 1000);
      }

    } catch (error) {
      logger.error('Error processing message:', error);
      ws.send(JSON.stringify({
        id: uuidv4(),
        type: 'system',
        content: 'Error processing message. Please try again.',
        timestamp: new Date().toISOString(),
        sender: 'arche',
        error: true
      }));
    }
  });

  // Handle client disconnection
  ws.on('close', (code, reason) => {
    clients.delete(ws);
    logger.info(`Client disconnected: ${clientId} (Code: ${code})`);
  });

  // Handle errors
  ws.on('error', (error) => {
    logger.error(`WebSocket error for client ${clientId}:`, error);
    clients.delete(ws);
  });
});

// Handle server errors
wss.on('error', (error) => {
  logger.error('WebSocket server error:', error);
});

// Graceful shutdown
process.on('SIGINT', () => {
  logger.info('Shutting down WebSocket server...');
  wss.close(() => {
    logger.info('WebSocket server closed');
    process.exit(0);
  });
});

logger.info('WebSocket server ready for connections'); 