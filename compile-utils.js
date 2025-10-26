// compile-utils.js
// Simple TypeScript to JavaScript transpiler for WebSocket server utilities

const fs = require('fs');
const path = require('path');

// Simple TypeScript to JavaScript conversion
function transpileTS(content) {
  return content
    // Remove TypeScript imports and replace with require
    .replace(/import\s+\{([^}]+)\}\s+from\s+['"]([^'"]+)['"];?/g, (match, imports, module) => {
      if (module.startsWith('@/')) {
        const relativePath = module.replace('@/', './');
        return `const { ${imports} } = require('${relativePath}');`;
      }
      return `const { ${imports} } = require('${module}');`;
    })
    // Remove export keywords
    .replace(/export\s+/g, '')
    // Convert class declarations to module.exports
    .replace(/class\s+(\w+)\s*\{/, (match, className) => {
      return `class ${className} {`;
    })
    // Add module.exports at the end
    .replace(/(\n\s*})/g, (match, closingBrace) => {
      return `${closingBrace}\n\nmodule.exports = { ${match.includes('class') ? 'IARProcessor, SPRDetector' : 'IARReflection, SPRActivation, TemporalContext, MetaCognitiveState, AgentGroup, HumanFactorModeling, EnvironmentalFactor, InterventionScenario, RealismAssessment, ComplexSystemVisioningData, ImplementationResonance, EnhancedMessage'};`;
    })
    // Remove TypeScript type annotations
    .replace(/:\s*[A-Za-z<>[\]|&\s]+(?=\s*[=,;)])/g, '')
    .replace(/\?\s*:/g, ':')
    // Remove optional chaining operators
    .replace(/\?\./g, '.')
    // Remove interface definitions
    .replace(/interface\s+\w+\s*\{[^}]*\}/g, '')
    // Remove type aliases
    .replace(/type\s+\w+\s*=\s*[^;]+;/g, '');
}

// Create JavaScript versions of the TypeScript utilities
const utilFiles = [
  'utils/iarProcessor.ts',
  'utils/sprDetector.ts',
  'types/protocol.ts'
];

console.log('🔄 Transpiling TypeScript utilities for WebSocket server...');

utilFiles.forEach(file => {
  if (fs.existsSync(file)) {
    const content = fs.readFileSync(file, 'utf8');
    const jsContent = transpileTS(content);
    const jsFile = file.replace('.ts', '.js');
    
    fs.writeFileSync(jsFile, jsContent);
    console.log(`✅ Transpiled ${file} -> ${jsFile}`);
  } else {
    console.log(`⚠️  File not found: ${file}`);
  }
});

console.log('🎉 TypeScript transpilation complete!');
console.log('📝 Note: This is a simple transpiler. For production, use proper TypeScript compilation.'); 