import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs/promises';

export const dynamic = 'force-dynamic';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { question, buildPlaybook = true } = body;

    if (!question) {
      return NextResponse.json({ error: 'Question is required' }, { status: 400 });
    }

    // Escape the question for safe Python string usage
    const escapedQuestion = question
      .replace(/\\/g, '\\\\')  // Escape backslashes
      .replace(/"/g, '\\"')    // Escape double quotes
      .replace(/\n/g, '\\n')   // Escape newlines
      .replace(/\r/g, '\\r')   // Escape carriage returns
      .replace(/\t/g, '\\t');  // Escape tabs

    // Create a Python script to generate the playbook
    const pythonScript = `
import sys
import os
import json
from datetime import datetime

# Add ArchE to path
sys.path.append('Three_PointO_ArchE')
sys.path.append('.')

try:
    from natural_language_interface import ArchENaturalLanguageInterface
    
    interface = ArchENaturalLanguageInterface()
    
    # Generate playbook
    question = "${escapedQuestion}"
    playbook = interface.generate_dynamic_playbook(question)
    
    # Save playbook
    playbook_name = f"dynamic_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    playbook_path = f"workflows/{playbook_name}"
    
    os.makedirs("workflows", exist_ok=True)
    with open(playbook_path, 'w') as f:
        json.dump(playbook, f, indent=2)
    
    print(json.dumps({
        'status': 'success',
        'playbook_path': playbook_path,
        'playbook': playbook,
        'question': question
    }))
    
except Exception as e:
    print(json.dumps({
        'status': 'error',
        'error': str(e),
        'question': "${escapedQuestion}"
    }))
`;

    // Write the script to a temporary file
    const scriptPath = path.join(process.cwd(), 'temp_playbook_generator.py');
    await fs.writeFile(scriptPath, pythonScript);

    // Execute the Python script
    const result = await new Promise((resolve, reject) => {
      const python = spawn('python3', [scriptPath], {
        cwd: path.join(process.cwd(), '..'), // Go up one level to the Happier directory
        stdio: ['pipe', 'pipe', 'pipe']
      });

      let output = '';
      let error = '';

      python.stdout.on('data', (data) => {
        output += data.toString();
      });

      python.stderr.on('data', (data) => {
        error += data.toString();
      });

      python.on('close', (code) => {
        if (code === 0) {
          try {
            const result = JSON.parse(output);
            resolve(result);
          } catch (e) {
            reject(new Error('Failed to parse Python output'));
          }
        } else {
          reject(new Error(`Python script failed: ${error}`));
        }
      });
    });

    // Clean up temporary file
    await fs.unlink(scriptPath);

    return NextResponse.json(result);

  } catch (error: any) {
    return NextResponse.json({ 
      error: error.message || 'Unknown error occurred' 
    }, { status: 500 });
  }
}
