#!/usr/bin/env node

const UnifiedStartup = require('./scripts/unified-startup');

async function main() {
  console.log('🚀 ArchE Unified Startup');
  console.log('==================================================');
  console.log('🎯 Single Command - All Services');
  console.log('🔧 Centralized Port Management');
  console.log('==================================================');
  
  const startup = new UnifiedStartup();
  
  try {
    await startup.startAllServices();
  } catch (error) {
    console.error('❌ Startup failed:', error.message);
    process.exit(1);
  }
}

main(); 