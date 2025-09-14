const fs = require('fs');
const path = require('path');

class TimestampedLogger {
    constructor(component = 'websocket', logDir = 'logs') {
        this.component = component;
        this.logDir = logDir;
        this.timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T')[0] + '_' + 
                        new Date().toISOString().replace(/[:.]/g, '-').split('T')[1].split('.')[0];
        
        // Ensure log directory exists
        if (!fs.existsSync(this.logDir)) {
            fs.mkdirSync(this.logDir, { recursive: true });
        }
        
        // Create log file paths
        this.mainLogFile = path.join(this.logDir, `${this.component}_${this.timestamp}.log`);
        this.errorLogFile = path.join(this.logDir, `errors_${this.component}_${this.timestamp}.log`);
        this.performanceLogFile = path.join(this.logDir, `performance_${this.component}_${this.timestamp}.log`);
        
        // Initialize log files with headers
        this.initializeLogFiles();
    }
    
    initializeLogFiles() {
        const header = `================================================================================
🚀 ${this.component.toUpperCase()} Logging Session Started
================================================================================
📅 Session Start Time: ${new Date().toISOString()}
🔧 Component: ${this.component}
📁 Main Log: ${this.mainLogFile}
❌ Error Log: ${this.errorLogFile}
⚡ Performance Log: ${this.performanceLogFile}
================================================================================
`;
        
        fs.writeFileSync(this.mainLogFile, header);
        fs.writeFileSync(this.errorLogFile, header);
        fs.writeFileSync(this.performanceLogFile, header);
    }
    
    formatMessage(level, message, data = null) {
        const timestamp = new Date().toISOString();
        let formattedMessage = `${timestamp} [${level.toUpperCase()}] ${this.component}: ${message}`;
        
        if (data) {
            if (typeof data === 'object') {
                formattedMessage += `\n${JSON.stringify(data, null, 2)}`;
            } else {
                formattedMessage += ` | Data: ${data}`;
            }
        }
        
        return formattedMessage + '\n';
    }
    
    log(level, message, data = null) {
        const formattedMessage = this.formatMessage(level, message, data);
        
        // Write to main log
        fs.appendFileSync(this.mainLogFile, formattedMessage);
        
        // Write to error log if it's an error
        if (level === 'error') {
            fs.appendFileSync(this.errorLogFile, formattedMessage);
        }
        
        // Write to performance log if it's performance related
        if (level === 'performance' || message.includes('performance') || message.includes('timing')) {
            fs.appendFileSync(this.performanceLogFile, formattedMessage);
        }
        
        // Also log to console with color coding
        const colors = {
            info: '\x1b[36m',    // Cyan
            warn: '\x1b[33m',    // Yellow
            error: '\x1b[31m',   // Red
            debug: '\x1b[35m',   // Magenta
            performance: '\x1b[32m' // Green
        };
        
        const reset = '\x1b[0m';
        const color = colors[level] || '';
        
        console.log(`${color}${formattedMessage.trim()}${reset}`);
    }
    
    info(message, data = null) {
        this.log('info', message, data);
    }
    
    warn(message, data = null) {
        this.log('warn', message, data);
    }
    
    error(message, data = null) {
        this.log('error', message, data);
    }
    
    debug(message, data = null) {
        this.log('debug', message, data);
    }
    
    performance(message, data = null) {
        this.log('performance', message, data);
    }
    
    session(sessionId, message, data = null) {
        const sessionMessage = `[SESSION:${sessionId}] ${message}`;
        this.log('info', sessionMessage, data);
    }
    
    getLogFiles() {
        return {
            main: this.mainLogFile,
            error: this.errorLogFile,
            performance: this.performanceLogFile
        };
    }
}

module.exports = TimestampedLogger; 