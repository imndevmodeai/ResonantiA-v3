#!/usr/bin/env node
/**
 * Integrated Development Server
 * Starts both Next.js frontend and ArchE backend server
 * ResonantiA Protocol v3.1-CA Enhanced
 */

const { spawn, exec } = require('child_process');
const path = require('path');
const fs = require('fs');
const WebSocket = require('ws');

// Configuration
const CONFIG = {
  nextPort: 3000,
  archePort: 3005,
  websocketPort: 3004,
  archeServerPath: './arche_persistent_server.py',
  pythonPath: './.venv/bin/python3',
  checkInterval: 2000, // 2 seconds
  maxRetries: 10
};

// ANSI color codes for better output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m'
};

function log(message, color = 'reset') {
  const timestamp = new Date().toLocaleTimeString();
  console.log(`${colors[color]}[${timestamp}] ${message}${colors.reset}`);
}

function logSection(title) {
  console.log(`\n${colors.bright}${colors.cyan}${'='.repeat(50)}`);
  console.log(`${title}`);
  console.log(`${'='.repeat(50)}${colors.reset}\n`);
}

// Check if virtual environment exists
function checkVirtualEnv() {
  const venvPath = path.resolve('.venv');
  if (!fs.existsSync(venvPath)) {
    log('❌ Virtual environment not found!', 'red');
    log('Please create a virtual environment first:', 'yellow');
    log('python3 -m venv .venv', 'cyan');
    log('source .venv/bin/activate', 'cyan');
    log('pip install -r requirements.txt', 'cyan');
    process.exit(1);
  }
  log('✅ Virtual environment found', 'green');
}

// Check if ArchE server file exists
function checkArcheServer() {
  if (!fs.existsSync(CONFIG.archeServerPath)) {
    log(`❌ ArchE server not found: ${CONFIG.archeServerPath}`, 'red');
    process.exit(1);
  }
  log('✅ ArchE server file found', 'green');
}

// Check if port is available
function checkPort(port) {
  return new Promise((resolve) => {
    const net = require('net');
    const server = net.createServer();
    
    server.listen(port, () => {
      server.once('close', () => {
        resolve(true);
      });
      server.close();
    });
    
    server.on('error', () => {
      resolve(false);
    });
  });
}

// Kill process on port
async function killProcessOnPort(port) {
  return new Promise((resolve) => {
    exec(`lsof -ti:${port}`, (error, stdout) => {
      if (stdout.trim()) {
        const pids = stdout.trim().split('\n');
        log(`🔄 Killing processes on port ${port}: ${pids.join(', ')}`, 'yellow');
        
        pids.forEach(pid => {
          exec(`kill -9 ${pid}`, () => {
            log(`✅ Killed process ${pid}`, 'green');
          });
        });
        
        // Wait a bit for processes to be killed
        setTimeout(resolve, 1000);
      } else {
        resolve();
      }
    });
  });
}

// Start ArchE server
function startArcheServer() {
  return new Promise((resolve, reject) => {
    log('🚀 Starting ArchE Persistent Server...', 'blue');
    
    const archeProcess = spawn(CONFIG.pythonPath, [CONFIG.archeServerPath], {
      stdio: 'pipe',
      env: { ...process.env, PYTHONPATH: process.cwd() }
    });
    
    let isReady = false;
    let retries = 0;
    
    archeProcess.stdout.on('data', (data) => {
      const output = data.toString();
      process.stdout.write(`${colors.magenta}[ArchE] ${output}${colors.reset}`);
      
      // Check if server is ready
      if (output.includes('ArchE Persistent Server running on ws://0.0.0.0:3005')) {
        isReady = true;
        log('✅ ArchE server is ready!', 'green');
        resolve(archeProcess);
      }
    });
    
    archeProcess.stderr.on('data', (data) => {
      const error = data.toString();
      process.stderr.write(`${colors.red}[ArchE Error] ${error}${colors.reset}`);
    });
    
    archeProcess.on('error', (error) => {
      log(`❌ Failed to start ArchE server: ${error.message}`, 'red');
      reject(error);
    });
    
    archeProcess.on('exit', (code) => {
      if (code !== 0 && !isReady) {
        log(`❌ ArchE server exited with code ${code}`, 'red');
        reject(new Error(`ArchE server exited with code ${code}`));
      }
    });
    
    // Timeout check
    const timeout = setTimeout(() => {
      if (!isReady) {
        log('⚠️ ArchE server taking longer than expected to start...', 'yellow');
      }
    }, 10000);
    
    archeProcess.on('ready', () => {
      clearTimeout(timeout);
    });
  });
}

// Start Next.js development server
function startNextServer() {
  return new Promise((resolve, reject) => {
    log('🚀 Starting Next.js development server...', 'blue');
    
    const nextProcess = spawn('npm', ['run', 'dev'], {
      stdio: 'pipe',
      env: { ...process.env, PORT: CONFIG.nextPort }
    });
    
    let isReady = false;
    
    nextProcess.stdout.on('data', (data) => {
      const output = data.toString();
      process.stdout.write(`${colors.cyan}[Next.js] ${output}${colors.reset}`);
      
      // Check if Next.js is ready
      if (output.includes('Ready in') || output.includes('Local:')) {
        isReady = true;
        log('✅ Next.js server is ready!', 'green');
        resolve(nextProcess);
      }
    });
    
    nextProcess.stderr.on('data', (data) => {
      const error = data.toString();
      process.stderr.write(`${colors.red}[Next.js Error] ${error}${colors.reset}`);
    });
    
    nextProcess.on('error', (error) => {
      log(`❌ Failed to start Next.js server: ${error.message}`, 'red');
      reject(error);
    });
    
    nextProcess.on('exit', (code) => {
      if (code !== 0 && !isReady) {
        log(`❌ Next.js server exited with code ${code}`, 'red');
        reject(new Error(`Next.js server exited with code ${code}`));
      }
    });
  });
}

// Health check function
async function healthCheck() {
  const checks = [
    { name: 'Next.js Frontend', url: `http://localhost:${CONFIG.nextPort}` },
    { name: 'ArchE Backend', url: `ws://localhost:${CONFIG.archePort}` },
    { name: 'WebSocket Server', url: `ws://localhost:${CONFIG.websocketPort}` }
  ];
  
  log('🔍 Performing health check...', 'blue');
  
  for (const check of checks) {
    try {
      if (check.url.startsWith('ws://')) {
        // WebSocket health check
        const ws = new WebSocket(check.url);
        await new Promise((resolve, reject) => {
          const timeout = setTimeout(() => reject(new Error('Timeout')), 3000);
          ws.on('open', () => {
            clearTimeout(timeout);
            ws.close();
            resolve();
          });
          ws.on('error', reject);
        });
      } else {
        // HTTP health check
        const http = require('http');
        await new Promise((resolve, reject) => {
          const req = http.get(check.url, (res) => {
            if (res.statusCode === 200) {
              resolve();
            } else {
              reject(new Error(`Status: ${res.statusCode}`));
            }
          });
          req.on('error', reject);
          req.setTimeout(3000, () => reject(new Error('Timeout')));
        });
      }
      log(`✅ ${check.name} is healthy`, 'green');
    } catch (error) {
      log(`❌ ${check.name} health check failed: ${error.message}`, 'red');
    }
  }
}

// Graceful shutdown
function setupGracefulShutdown(processes) {
  const shutdown = (signal) => {
    log(`\n🛑 Received ${signal}, shutting down gracefully...`, 'yellow');
    
    processes.forEach((proc, name) => {
      if (proc && !proc.killed) {
        log(`🔄 Stopping ${name}...`, 'yellow');
        proc.kill('SIGTERM');
        
        // Force kill after 5 seconds
        setTimeout(() => {
          if (!proc.killed) {
            log(`⚠️ Force killing ${name}...`, 'yellow');
            proc.kill('SIGKILL');
          }
        }, 5000);
      }
    });
    
    setTimeout(() => {
      log('✅ All processes stopped', 'green');
      process.exit(0);
    }, 6000);
  };
  
  process.on('SIGINT', () => shutdown('SIGINT'));
  process.on('SIGTERM', () => shutdown('SIGTERM'));
}

// Main function
async function main() {
  try {
    logSection('ArchE Integrated Development Server');
    log('ResonantiA Protocol v3.1-CA Enhanced', 'cyan');
    
    // Pre-flight checks
    logSection('Pre-flight Checks');
    checkVirtualEnv();
    checkArcheServer();
    
    // Check and clear ports
    logSection('Port Management');
    const ports = [CONFIG.nextPort, CONFIG.archePort, CONFIG.websocketPort];
    
    for (const port of ports) {
      const isAvailable = await checkPort(port);
      if (!isAvailable) {
        log(`⚠️ Port ${port} is in use, attempting to clear...`, 'yellow');
        await killProcessOnPort(port);
        await new Promise(resolve => setTimeout(resolve, 2000));
      }
      log(`✅ Port ${port} is available`, 'green');
    }
    
    // Start servers
    logSection('Starting Servers');
    
    const processes = new Map();
    
    // Start ArchE server first
    const archeProcess = await startArcheServer();
    processes.set('ArchE Server', archeProcess);
    
    // Wait a bit for ArchE to fully initialize
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Start Next.js server
    const nextProcess = await startNextServer();
    processes.set('Next.js Server', nextProcess);
    
    // Setup graceful shutdown
    setupGracefulShutdown(processes);
    
    // Wait for both servers to be ready
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    // Perform health check
    logSection('Health Check');
    await healthCheck();
    
    // Display connection information
    logSection('Connection Information');
    log(`🌐 Frontend: http://localhost:${CONFIG.nextPort}`, 'green');
    log(`🧠 ArchE Backend: ws://localhost:${CONFIG.archePort}`, 'green');
    log(`📡 WebSocket Server: ws://localhost:${CONFIG.websocketPort}`, 'green');
    log(`\n🎯 Press Ctrl+C to stop all servers`, 'yellow');
    
    // Keep the process alive
    process.stdin.resume();
    
  } catch (error) {
    log(`❌ Failed to start development environment: ${error.message}`, 'red');
    process.exit(1);
  }
}

// Run the main function
if (require.main === module) {
  main();
}

module.exports = { main, CONFIG }; 