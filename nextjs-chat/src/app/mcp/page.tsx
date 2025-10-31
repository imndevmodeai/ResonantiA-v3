'use client';

import { useState, useEffect } from 'react';

type Instance = {
  id: string;
  name: string;
  status: 'online' | 'offline';
  capabilities: string[];
  last_active: string;
};

type Task = {
  task_id: string;
  description: string;
  required_capability: string;
  status: 'pending' | 'in_progress' | 'completed';
  assigned_to: string | null;
};

type Spr = {
  id: string;
  concept: string;
  created_at: string;
};

type McpData = {
  instances: Instance[];
  roadmap: Task[];
  knowledge_graph: {
    spr_count: number;
    recent_additions: Spr[];
  };
};

const StatusIndicator = ({ status }: { status: 'online' | 'offline' }) => (
  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
    status === 'online' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
  }`}>
    {status}
  </span>
);

const TaskStatus = ({ status }: { status: 'pending' | 'in_progress' | 'completed' }) => {
    let colorClass = '';
    switch (status) {
        case 'completed':
            colorClass = 'bg-blue-100 text-blue-800';
            break;
        case 'in_progress':
            colorClass = 'bg-yellow-100 text-yellow-800';
            break;
        case 'pending':
            colorClass = 'bg-gray-100 text-gray-800';
            break;
    }
    return (
        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${colorClass}`}>
            {status.replace('_', ' ')}
        </span>
    );
};

export default function McpDashboard() {
  const [data, setData] = useState<McpData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/mcp');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const result = await response.json();
        setData(result);
      } catch (e: any) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <div className="text-center p-8">Loading MCP Dashboard...</div>;
  if (error) return <div className="text-center p-8 text-red-500">Error: {error}</div>;
  if (!data) return <div className="text-center p-8">No data available.</div>;

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <main className="container mx-auto p-4 sm:p-6 lg:p-8">
        <h1 className="text-3xl font-bold mb-6 text-cyan-400">ArchE Mission Control Panel</h1>

        {/* Instances Section */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4 text-gray-300">Registered Instances</h2>
          <div className="bg-gray-800 shadow-lg rounded-lg overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-700">
              <thead className="bg-gray-700">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Name</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Status</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Capabilities</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Last Active</th>
                </tr>
              </thead>
              <tbody className="bg-gray-800 divide-y divide-gray-700">
                {data.instances.map((instance) => (
                  <tr key={instance.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-white">{instance.name}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <StatusIndicator status={instance.status} />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">{instance.capabilities.join(', ')}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">{new Date(instance.last_active).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Roadmap Section */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4 text-gray-300">Orchestrator Roadmap</h2>
           <div className="bg-gray-800 shadow-lg rounded-lg overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-700">
              <thead className="bg-gray-700">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Description</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Status</th>
                   <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Assigned To</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Capability Needed</th>
                </tr>
              </thead>
              <tbody className="bg-gray-800 divide-y divide-gray-700">
                {data.roadmap.map((task) => (
                  <tr key={task.task_id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-white">{task.description}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <TaskStatus status={task.status} />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">{task.assigned_to || 'Unassigned'}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">{task.required_capability}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
        
        {/* Knowledge Graph Section */}
        <section>
          <h2 className="text-2xl font-semibold mb-4 text-gray-300">Knowledge Graph (KnO)</h2>
           <div className="bg-gray-800 shadow-lg rounded-lg p-6">
                <p className="text-lg text-white">Total SPRs: <span className="font-bold text-cyan-400">{data.knowledge_graph.spr_count}</span></p>
                <div className="mt-4">
                    <h3 className="text-md font-medium text-gray-400 mb-2">Recent Additions:</h3>
                    <ul className="list-disc list-inside space-y-1">
                        {data.knowledge_graph.recent_additions.map(spr => (
                             <li key={spr.id} className="text-sm text-gray-300">
                                <span className="font-semibold">{spr.concept}</span> ({new Date(spr.created_at).toLocaleDateString()})
                            </li>
                        ))}
                    </ul>
                </div>
           </div>
        </section>

      </main>
    </div>
  );
}
