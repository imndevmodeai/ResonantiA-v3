const WebSocket = require('ws');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');
const TimestampedLogger = require('./nextjs-chat/src/utils/timestampedLogger.js');

// Initialize timestamped logger
const logger = new TimestampedLogger('websocket', 'logs');

// Note: IAR and other protocol data comes from the Python ArchE backend
// The VCD frontend receives and displays this data, it doesn't generate it
logger.info('VCD WebSocket Server - IAR data will be received from Python ArchE backend');

// Load port configuration from environment variables
let port = process.env.WEBSOCKET_PORT || 3006; // Use environment variable, fallback to 3006
const archePort = process.env.ARCHE_PORT || 3005; // Use environment variable for arche backend

try {
  port = parseInt(port, 10);
  if (isNaN(port)) {
    logger.warn('Invalid WEBSOCKET_PORT env var. Using default 3006');
    port = 3006;
  }
} catch (error) {
  logger.warn(`Could not parse WEBSOCKET_PORT, using default port ${port}`);
}

// Create WebSocket server on configured port
const wss = new WebSocket.Server({ port });

// VCD WebSocket Server ready - IAR data comes from Python ArchE backend

logger.info(`ArchE Protocol v3.1-CA WebSocket Server running on port ${port}`);
logger.info('Cognitive Bus ready for protocol-enhanced connections');
logger.info(`Connect at: ws://localhost:${port}`);

const clients = new Set();
let archeWebSocket = null;
let archeInterfaceReady = false;

async function processMessageThroughProtocol(content, sender = 'user') {
  const timestamp = new Date().toISOString();
  
  const enhancedMessage = {
    id: uuidv4(),
    content,
    timestamp,
    sender: sender === 'assistant' ? 'arche' : sender,
    message_type: 'chat',
    protocol_compliance: true,
    protocol_version: 'v3.1-CA'
  };

  // Note: IAR and protocol data will be added by the Python ArchE backend
  // This function just creates the basic message structure for the VCD
  
  return enhancedMessage;
}

async function initializeArcheInterface() {
  if (archeWebSocket && archeWebSocket.readyState === WebSocket.OPEN) return;

  console.log('🚀 Initializing connection to ArchE persistent server...');
  const archeServerUrl = `ws://localhost:${archePort}`;
  
  try {
    archeWebSocket = new WebSocket(archeServerUrl);
    
    archeWebSocket.on('open', () => {
      console.log(`✅ Connected to ArchE persistent server at ${archeServerUrl}`);
      archeInterfaceReady = true;
    });
    
    archeWebSocket.on('message', async (data) => {
      try {
        const response = JSON.parse(data.toString());
        logger.info('Received response from Python server:', response);
        
        // Extract content from the response object
        let content = '';
        if (typeof response === 'string') {
          content = response;
        } else if (response.content) {
          content = response.content;
        } else if (response.message) {
          content = response.message;
        } else if (response.error) {
          content = `Error: ${response.error}`;
        } else {
          // Convert complex object to readable string
          content = JSON.stringify(response, null, 2);
        }
        
        const enhancedResponse = await processMessageThroughProtocol(content, 'assistant');
        clients.forEach(client => {
          if (client.readyState === WebSocket.OPEN) {
            client.send(JSON.stringify(enhancedResponse));
          }
        });
      } catch (error) {
        logger.error('Error parsing ArchE response', { error: error.message });
        // Send error message to clients
        const errorResponse = await processMessageThroughProtocol(
          `Error processing response: ${error.message}`, 
          'system'
        );
        clients.forEach(client => {
          if (client.readyState === WebSocket.OPEN) {
            client.send(JSON.stringify(errorResponse));
          }
        });
      }
    });
    
    archeWebSocket.on('error', (error) => {
      logger.error('ArchE WebSocket connection error', { error: error.message });
      archeInterfaceReady = false;
    });
    
    archeWebSocket.on('close', () => {
      logger.warn('ArchE WebSocket connection closed');
      archeWebSocket = null;
      archeInterfaceReady = false;
      setTimeout(() => {
        logger.info('Attempting to reconnect to ArchE persistent server');
        initializeArcheInterface();
      }, 5000);
    });
    
  } catch (error) {
    logger.error('Failed to connect to ArchE persistent server', { error: error.message });
    const errorMessage = {
      id: uuidv4(),
      content: `Failed to connect to ArchE persistent server: ${error.message}`,
      timestamp: new Date().toISOString(),
      sender: 'system',
      message_type: 'error',
    };
    clients.forEach(client => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(JSON.stringify(errorMessage));
      }
    });
  }
}

async function sendQueryToArche(query) {
    if (!archeInterfaceReady) {
        await initializeArcheInterface();
        await new Promise(resolve => {
            const interval = setInterval(() => {
                if (archeInterfaceReady) {
                    clearInterval(interval);
                    resolve();
                }
            }, 100);
        });
    }

  try {
    archeWebSocket.send(query);
    logger.info(`Sent query to ArchE interface: ${query.substring(0, 50)}...`);
  } catch (error) {
    logger.error('Error sending query to ArchE interface', { error: error.message });
  }
}

wss.on('connection', async (ws) => {
  logger.info('Client connected to ArchE Cognitive Bus');
  clients.add(ws);

  const initMessage = await processMessageThroughProtocol('connection established', 'system');
  ws.send(JSON.stringify(initMessage));

  await initializeArcheInterface();

  ws.on('message', async (message) => {
    const userQuery = message.toString().trim();
    if (!userQuery || userQuery === 'heartbeat' || userQuery.includes('connection')) {
      return;
    }
    logger.info('Received user query', { query: userQuery.substring(0, 100) + '...' });
    await sendQueryToArche(userQuery);
  });

  ws.on('close', () => {
    logger.info('Client disconnected from ArchE Cognitive Bus');
    clients.delete(ws);
  });

  ws.on('error', (error) => {
    logger.error('WebSocket error', { error: error.message });
    clients.delete(ws);
  });
});

wss.on('error', (error) => {
  logger.error('WebSocket server error', { error: error.message });
});


