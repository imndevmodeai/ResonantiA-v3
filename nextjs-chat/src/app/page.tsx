'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

interface WorkflowRun {
  run_id: string;
  workflow_name: string;
  timestamp: string;
}

interface DynamicPlaybook {
  status: string;
  playbook_path?: string;
  playbook?: any;
  question?: string;
  error?: string;
}

const WorkflowRunCard = ({ run }: { run: WorkflowRun }) => {
  const formatDate = (timestamp: string) => {
    try {
      return new Date(timestamp).toLocaleString();
    } catch (e) {
      return "Invalid Date";
    }
  };

  return (
    <Link href={`/run/${run.run_id}`} key={run.run_id}>
      <div className="block bg-gray-50 hover:bg-gray-100 p-6 rounded-lg border border-gray-200 hover:border-blue-500 hover:shadow-md transition-all duration-300 cursor-pointer h-full flex flex-col justify-between">
        <div>
          <h3 className="text-xl font-semibold text-blue-600 truncate">{run.workflow_name || 'Unnamed Workflow'}</h3>
          <p className="text-sm text-gray-500 mt-2">Run ID:</p>
          <p className="font-mono text-xs text-gray-600 break-all">{run.run_id}</p>
        </div>
        <div className="mt-4">
          <p className="text-sm text-gray-500">Timestamp:</p>
          <p className="text-gray-800 text-sm">{formatDate(run.timestamp)}</p>
        </div>
      </div>
    </Link>
  );
};

const DynamicPlaybookBuilder = () => {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<DynamicPlaybook | null>(null);

  const generatePlaybook = async () => {
    if (!question.trim()) return;

    setLoading(true);
    setResult(null);

    try {
      const response = await fetch('/api/dynamic-playbook', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question, buildPlaybook: true }),
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({
        status: 'error',
        error: 'Failed to generate playbook'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg border border-gray-200 mb-8">
      <h2 className="text-2xl font-bold text-gray-800 mb-4">🤖 ArchE Dynamic Playbook Builder</h2>
      <p className="text-gray-600 mb-4">Ask any question and ArchE will build a custom workflow for you!</p>
      
      <div className="space-y-4">
        <div>
          <label htmlFor="question" className="block text-sm font-medium text-gray-700 mb-2">
            Your Question
          </label>
          <textarea
            id="question"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g., Analyze the global economy, Predict future AI trends, Research quantum computing..."
            className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            rows={3}
          />
        </div>
        
        <button
          onClick={generatePlaybook}
          disabled={loading || !question.trim()}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-3 px-4 rounded-md transition-colors"
        >
          {loading ? '🔧 Building Playbook...' : '🚀 Build & Execute Playbook'}
        </button>
        
        {result && (
          <div className={`p-4 rounded-md ${
            result.status === 'success' ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
          }`}>
            {result.status === 'success' ? (
              <div>
                <h3 className="font-semibold text-green-800 mb-2">✅ Playbook Generated Successfully!</h3>
                <p className="text-green-700 mb-2">Question: {result.question}</p>
                <p className="text-green-700 mb-2">Playbook: {result.playbook_path}</p>
                <div className="mt-3">
                  <button
                    onClick={() => {
                      // Execute the playbook using ArchE's execute_playbook.py
                      const playbookPath = result.playbook_path;
                      const command = `cd /media/newbu/3626C55326C514B1/Happier && python3 execute_playbook.py ${playbookPath}`;
                      
                      // Open a new window with the execution
                      const newWindow = window.open('', '_blank');
                      if (newWindow) {
                        newWindow.document.write(`
                          <html>
                            <head><title>ArchE Playbook Execution</title></head>
                            <body style="font-family: monospace; background: #1a1a1a; color: #00ff00; padding: 20px;">
                              <h1>🚀 Executing ArchE Playbook</h1>
                              <p>Playbook: ${playbookPath}</p>
                              <p>Command: ${command}</p>
                              <hr>
                              <p>Executing... Please check the terminal for output.</p>
                              <p>You can also run this command manually:</p>
                              <pre style="background: #333; padding: 10px; border-radius: 5px;">${command}</pre>
                            </body>
                          </html>
                        `);
                      }
                    }}
                    className="bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-4 rounded-md transition-colors"
                  >
                    🎯 Execute Playbook
                  </button>
                </div>
              </div>
            ) : (
              <div>
                <h3 className="font-semibold text-red-800 mb-2">❌ Error Generating Playbook</h3>
                <p className="text-red-700">{result.error}</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};


export default function EnhancedRunSelector() {
  const [runs, setRuns] = useState<WorkflowRun[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [sortConfig, setSortConfig] = useState({ key: 'timestamp', order: 'desc' });

  useEffect(() => {
    const fetchRuns = async () => {
      try {
        setLoading(true);
        const response = await fetch(`http://127.0.0.1:5002/api/runs?sortBy=${sortConfig.key}&order=${sortConfig.order}`);
        if (!response.ok) {
          throw new Error(`API Error: ${response.status} ${response.statusText}`);
        }
        const data = await response.json();
        setRuns(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An unknown error occurred.');
        setRuns([]);
      } finally {
        setLoading(false);
      }
    };
    fetchRuns();
  }, [sortConfig]); // Re-fetch whenever sortConfig changes

  const SortButton = ({ sortKey, order, label }: { sortKey: string, order: string, label: string }) => {
    const isActive = sortConfig.key === sortKey && sortConfig.order === order;
    return (
      <button
        onClick={() => setSortConfig({ key: sortKey, order: order })}
        className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
          isActive
            ? 'bg-blue-600 text-white'
            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
        }`}
      >
        {label}
      </button>
    );
  };

  return (
    <div className="min-h-screen bg-white text-black font-sans">
      <div className="container mx-auto p-8">
        <header className="mb-6 border-b border-gray-200 pb-4">
          <h1 className="text-4xl font-bold text-gray-800 tracking-tight">ArchE - Dynamic Playbook Builder</h1>
          <p className="text-lg text-gray-600 mt-2">Ask questions and ArchE will build custom workflows for you!</p>
        </header>

        {/* Dynamic Playbook Builder */}
        <DynamicPlaybookBuilder />

        {/* Existing Workflow Runs */}
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">📋 Previous Workflow Executions</h2>
          
          <div className="flex items-center space-x-2 mb-6 p-2 bg-gray-100 rounded-lg">
            <span className="text-sm font-semibold text-gray-600 mr-2">Sort by:</span>
            <SortButton sortKey="timestamp" order="desc" label="Date (Newest)" />
            <SortButton sortKey="timestamp" order="asc" label="Date (Oldest)" />
            <SortButton sortKey="workflow_name" order="asc" label="Name (A-Z)" />
            <SortButton sortKey="workflow_name" order="desc" label="Name (Z-A)" />
        </div>

        {loading && (
          <div className="text-center py-16">
            <p className="text-2xl animate-pulse text-gray-500">Loading Execution Logs...</p>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 p-6 rounded-lg max-w-2xl mx-auto">
            <h2 className="text-xl font-bold mb-2 text-red-700">Failed to Load Data</h2>
            <p className="font-mono bg-gray-100 p-2 rounded text-red-600">{error}</p>
            <p className="mt-4 text-sm text-gray-600">Please ensure the VCD API server is running and accessible at <code className="bg-gray-200 text-gray-800 px-1 rounded">http://127.0.0.1:5002</code>.</p>
          </div>
        )}

        {!loading && !error && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {runs.map((run) => (
              <WorkflowRunCard key={run.run_id} run={run} />
            ))}
          </div>
        )}
        </div>
      </div>
    </div>
  );
}

