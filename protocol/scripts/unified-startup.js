#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const PortManager = require('./port-manager');
const TimestampedLogger = require('../utils/timestampedLogger.js');

// Initialize timestamped logger for startup
const logger = new TimestampedLogger('startup', 'logs');

class UnifiedStartup {
  constructor() {
    this.portManager = new PortManager();
    this.processes = new Map();
    this.pythonExecutable = this.findPythonExecutable();
  }

  findPythonExecutable() {
    const venvPython3 = path.join(process.cwd(), '.venv', 'bin', 'python3');
    if (fs.existsSync(venvPython3)) {
      logger.info(`Found Python executable in virtual environment: ${venvPython3}`);
      return venvPython3;
    }
    
    const venvPython = path.join(process.cwd(), '.venv', 'bin', 'python');
    if (fs.existsSync(venvPython)) {
      logger.info(`Found Python executable in virtual environment: ${venvPython}`);
      return venvPython;
    }

    logger.warn('Could not find Python in .venv. Defaulting to python3 from system PATH');
    // On many modern systems, 'python3' is the standard. 
    // We'll let spawn() handle the error if it's not in the PATH.
    return 'python3';
  }

  async initialize() {
    logger.info('ArchE Unified Startup System');
    logger.info('Single Entry Point - All Services');
    logger.info('Centralized Port Management');
    
    await this.portManager.updateConfig();
    this.portManager.generateEnvFile();
    
    logger.info('Building server-side utilities');
    try {
      // Execute the new build script before starting servers
      const { execSync } = require('child_process');
      execSync('node scripts/build-server-utils.js', { stdio: 'pipe' });
      logger.info('Server-side utilities built successfully');
    } catch (error) {
      logger.error('FATAL: Failed to build server-side utilities. Startup aborted', {
        stdout: error.stdout.toString(),
        stderr: error.stderr.toString()
      });
      process.exit(1);
    }
    
    logger.info('Port configuration initialized');
  }

  async startArchePersistentServer() {
    console.log('\n🧠 Starting ArchE Persistent Server (Cognitive Core)...');
    
    return new Promise((resolve, reject) => {
      if (!this.pythonExecutable) {
        return reject(new Error("Python executable not found."));
      }
      const env = { 
        ...process.env, 
        ...this.portManager.config.environment,
        // Explicitly set PYTHONPATH to ensure modules are found, especially when not running from an activated shell
        PYTHONPATH: process.cwd() 
      };

      console.log(`🧠 Passing environment to ArchE Core: ARCHE_PORT=${env.ARCHE_PORT}, WEBSOCKET_PORT=${env.WEBSOCKET_PORT}`);

      const archeProcess = spawn(this.pythonExecutable, ['-u', 'Three_PointO_ArchE/mastermind_server.py'], {
        env: env,
        stdio: 'pipe',
        cwd: process.cwd()
      });

      this.processes.set('arche_persistent', archeProcess);

      archeProcess.stdout.on('data', (data) => {
        const output = data.toString();
        console.log(`🧠 ArchE Core: ${output.trim()}`);
        
        if (output.includes('ArchE Persistent Server running on')) {
          console.log('✅ ArchE Cognitive Core ready');
          resolve();
        }
      });

      archeProcess.stderr.on('data', (data) => {
        console.error(`❌ ArchE Core Error: ${data.toString()}`);
      });

      archeProcess.on('close', (code) => {
        console.log(`🔄 ArchE Cognitive Core exited with code ${code}`);
        if (code !== 0) {
          reject(new Error(`ArchE Cognitive Core failed to start with code ${code}`));
        }
      });
      
      archeProcess.on('error', (err) => {
        console.error(`❌ Failed to start ArchE Core process with command '${this.pythonExecutable}'. Error: ${err.message}`);
        reject(err);
      });

      setTimeout(() => {
        if (!archeProcess.killed) {
          console.log('✅ ArchE Cognitive Core started (timeout)');
          resolve();
        }
      }, 15000);
    });
  }

  async startWebSocketServer() {
    console.log('\n🔌 Starting WebSocket Server...');
    
    return new Promise((resolve, reject) => {
      const wsProcess = spawn('node', ['webSocketServer.js'], {
        env: { ...process.env, ...this.portManager.config.environment },
        stdio: 'pipe',
        cwd: process.cwd()
      });

      this.processes.set('websocket', wsProcess);

      wsProcess.stdout.on('data', (data) => {
        const output = data.toString();
        console.log(`📡 WebSocket: ${output.trim()}`);
        
        if (output.includes('WebSocket Server running on port')) {
          console.log('✅ WebSocket Server ready');
          resolve();
        }
      });

      wsProcess.stderr.on('data', (data) => {
        console.error(`❌ WebSocket Error: ${data.toString()}`);
      });

      wsProcess.on('close', (code) => {
        console.log(`🔄 WebSocket Server exited with code ${code}`);
      });

      setTimeout(() => {
        if (!wsProcess.killed) {
          console.log('✅ WebSocket Server started (timeout)');
          resolve();
        }
      }, 10000);
    });
  }

  async startNextJS() {
    console.log('\n🌐 Starting Next.js UI...');
    
    return new Promise((resolve, reject) => {
      const nextProcess = spawn('npm', ['run', 'dev'], {
        env: { ...process.env, ...this.portManager.config.environment },
        stdio: 'pipe',
        cwd: path.join(process.cwd(), 'nextjs-chat')
      });

      this.processes.set('nextjs', nextProcess);

      nextProcess.stdout.on('data', (data) => {
        const output = data.toString();
        console.log(`🌐 NextJS: ${output.trim()}`);
        
        if (output.includes('Ready') || output.includes('started server')) {
          console.log('✅ Next.js UI ready');
          resolve();
        }
      });

      nextProcess.stderr.on('data', (data) => {
        console.error(`❌ NextJS Error: ${data.toString()}`);
      });

      nextProcess.on('close', (code) => {
        console.log(`🔄 Next.js UI exited with code ${code}`);
      });

      setTimeout(() => {
        if (!nextProcess.killed) {
          console.log('✅ Next.js UI started (timeout)');
          resolve();
        }
      }, 15000);
    });
  }

  async startAllServices() {
    try {
      await this.initialize();
      
      // Start services in the correct dependency order
      await this.startArchePersistentServer(); // 1. Start the backend cognitive core
      await this.startWebSocketServer();      // 2. Start the middleware bridge
      await this.startNextJS();                 // 3. Start the frontend UI
      
      console.log('\n🎉 All services started successfully!');
      console.log('==================================================');
      console.log(`🧠 ArchE Core Server: ${this.portManager.config.urls.arche_python}`);
      console.log(`🔗 Middleware Bridge: ${this.portManager.config.urls.websocket}`);
      console.log(`🌐 Next.js UI: ${this.portManager.config.urls.nextjs}`);
      console.log('==================================================');
      console.log('💡 Press Ctrl+C to stop all services');
      
      process.on('SIGINT', () => {
        console.log('\n🛑 Shutting down all services...');
        this.shutdown();
      });
      
    } catch (error) {
      console.error('❌ Startup failed:', error.message);
      this.shutdown();
      process.exit(1);
    }
  }

  shutdown() {
    console.log('🔄 Stopping all services...');
    
    for (const [name, process] of this.processes) {
      if (!process.killed) {
        console.log(`🛑 Stopping ${name}...`);
        process.kill('SIGTERM');
      }
    }
    
    setTimeout(() => {
      for (const [name, process] of this.processes) {
        if (!process.killed) {
          console.log(`💀 Force killing ${name}...`);
          process.kill('SIGKILL');
        }
      }
      process.exit(0);
    }, 5000);
  }
}

async function main() {
  const startup = new UnifiedStartup();
  
  const command = process.argv[2];
  
  switch (command) {
    case 'start':
      await startup.startAllServices();
      break;
    
    case 'check':
      await startup.portManager.updateConfig();
      break;
    
    default:
      console.log('ArchE Unified Startup System');
      console.log('');
      console.log('Usage:');
      console.log('  node unified-startup.js start  - Start all services');
      console.log('  node unified-startup.js check  - Check port configuration');
  }
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = UnifiedStartup;
