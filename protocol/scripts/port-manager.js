#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

// Load centralized port configuration
const configPath = path.join(__dirname, '..', 'config', 'ports.json');
const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));

class PortManager {
  constructor() {
    this.config = config;
    this.usedPorts = new Set();
  }

  // Check if a port is available
  async checkPort(port) {
    return new Promise((resolve) => {
      const net = require('net');
      const server = net.createServer();
      
      server.listen(port, () => {
        server.once('close', () => {
          resolve(true); // Port is available
        });
        server.close();
      });
      
      server.on('error', () => {
        resolve(false); // Port is in use
      });
    });
  }

  // Get next available port, avoiding already assigned ports in this run
  async getNextAvailablePort(startPort) {
    let port = startPort;
    while (true) {
      if (this.usedPorts.has(port)) {
        port++;
        continue;
      }
      const isAvailable = await this.checkPort(port);
      if (isAvailable) {
        return port;
      }
      port++;
    }
  }

  // Update configuration with available ports
  async updateConfig() {
    console.log('🔍 Checking port availability...');
    
    // Use a fresh copy of the config for this run
    const updatedConfig = JSON.parse(JSON.stringify(this.config));
    this.usedPorts.clear(); // Clear used ports for this check cycle

    // First pass: lock in all the available default ports
    for (const [service, port] of Object.entries(this.config.ports)) {
      const isAvailable = await this.checkPort(port);
      if (isAvailable) {
        this.usedPorts.add(port);
        console.log(`✅ Port ${port} for ${service} is available and reserved for this run.`);
      }
    }

    // Second pass: reassign conflicting ports
    for (const [service, port] of Object.entries(this.config.ports)) {
        // We check if the original port was available. If not, it needs reassigning.
        const isAvailable = await this.checkPort(port);
        if (!isAvailable || !this.usedPorts.has(port)) { // Also check if another service stole it
             // Find a new port that is not in use on the system AND not already taken in this run
             const newPort = await this.getNextAvailablePort(port + 1);
             this.usedPorts.add(newPort); // Reserve the new port
             console.log(`⚠️  Port ${port} for ${service} is in use.`);
             console.log(`🔄 Reassigning ${service} to port ${newPort}`);
             updatedConfig.ports[service] = newPort;
             updatedConfig.urls[service] = updatedConfig.urls[service].replace(`:${port}`, `:${newPort}`);
        }
    }
    
    // Update environment variables
    updatedConfig.environment.PORT = updatedConfig.ports.nextjs.toString(); // Set PORT for Next.js
    updatedConfig.environment.NEXT_PUBLIC_WEBSOCKET_URL = updatedConfig.urls.websocket;
    updatedConfig.environment.NEXT_PUBLIC_ARCHE_PORT = updatedConfig.ports.arche_python.toString();
    updatedConfig.environment.WEBSOCKET_URL = updatedConfig.urls.websocket;
    updatedConfig.environment.WEBSOCKET_PORT = updatedConfig.ports.websocket.toString();
    updatedConfig.environment.ARCHE_PORT = updatedConfig.ports.arche_python.toString();

    // Save updated configuration to the instance variable AND the file
    this.config = updatedConfig;
    fs.writeFileSync(configPath, JSON.stringify(updatedConfig, null, 2));
    console.log('💾 Updated port configuration saved');
    
    // No need to return, the instance's config is updated
  }

  // Generate environment file
  generateEnvFile() {
    const envContent = Object.entries(this.config.environment)
      .map(([key, value]) => `${key}=${value}`)
      .join('\n');
    
    const envPath = path.join(__dirname, '..', '.env.local');
    fs.writeFileSync(envPath, envContent);
    console.log('📝 Generated .env.local file');
  }

  // Start service with correct port
  async startService(serviceName, command, args = []) {
    const port = this.config.ports[serviceName];
    if (!port) {
      throw new Error(`Unknown service: ${serviceName}`);
    }

    console.log(`🚀 Starting ${serviceName} on port ${port}...`);
    
    const env = { ...process.env, ...this.config.environment };
    
    return new Promise((resolve, reject) => {
      const child = spawn(command, args, {
        env,
        stdio: 'inherit',
        cwd: path.join(__dirname, '..')
      });

      child.on('close', (code) => {
        if (code === 0) {
          resolve();
        } else {
          reject(new Error(`${serviceName} exited with code ${code}`));
        }
      });

      child.on('error', (error) => {
        reject(error);
      });
    });
  }
}

// CLI interface
async function main() {
  const portManager = new PortManager();
  const command = process.argv[2];
  const service = process.argv[3];

  try {
    switch (command) {
      case 'check':
        await portManager.updateConfig();
        break;
      
      case 'start':
        if (!service) {
          console.log('Usage: node port-manager.js start <service>');
          console.log('Available services:', Object.keys(portManager.config.ports).join(', '));
          return;
        }
        await portManager.startService(service, 'node', [`${service}.js`]);
        break;
      
      case 'env':
        portManager.generateEnvFile();
        break;
      
      default:
        console.log('Port Manager - Centralized Port Configuration');
        console.log('');
        console.log('Usage:');
        console.log('  node port-manager.js check          - Check and update port availability');
        console.log('  node port-manager.js start <service> - Start a service with correct port');
        console.log('  node port-manager.js env            - Generate .env.local file');
        console.log('');
        console.log('Current configuration:');
        console.log(JSON.stringify(portManager.config, null, 2));
    }
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = PortManager; 