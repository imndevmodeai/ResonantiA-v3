// scripts/build-server-utils.js
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('🔧 Starting server-side utility build process...');

const utilsDir = path.join(__dirname, '..', 'utils');
const typesDir = path.join(__dirname, '..', 'types');
const nextjsChatDir = path.join(__dirname, '..', 'nextjs-chat');

// Function to find the local typescript compiler
function getTscPath() {
  const localTsc = path.join(nextjsChatDir, 'node_modules', '.bin', 'tsc');
  if (fs.existsSync(localTsc)) {
    console.log(`✅ Found local TypeScript compiler: ${localTsc}`);
    return localTsc;
  }
  console.log('⚠️  Local TypeScript compiler not found in nextjs-chat/node_modules. Falling back to global `tsc`. Please run `npm install` in `nextjs-chat` if this fails.');
  return 'tsc';
}

// Common compiler options for server-side JS compatibility
const tsconfigOptions = {
  "compilerOptions": {
    "target": "es2020",
    "module": "commonjs",
    "esModuleInterop": true,
    "forceConsistentCasingInFileNames": true,
    "strict": true,
    "skipLibCheck": true,
    "outDir": "./", // Output .js files next to .ts files
    "declaration": false
  }
};

const tscPath = getTscPath();

try {
  const command = `${tscPath} --project tsconfig.server.json`;
  console.log(`🔥 Executing build command: ${command}`);
  execSync(command, { stdio: 'inherit' });
  console.log('✅ Server-side utility build process completed successfully.');
} catch (error) {
  console.error('❌ A critical error occurred during the build process.');
  process.exit(1);
}
