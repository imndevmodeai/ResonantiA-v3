'use client';

import { useState, useEffect, useCallback } from 'react';
import ReactFlow, { 
    Background, 
    Controls, 
    MiniMap, 
    Node, 
    Edge,
    useNodesState,
    useEdgesState,
    Position,
    ReactFlowInstance
} from 'reactflow';
import 'reactflow/dist/style.css';
import Link from 'next/link';

// --- TYPE DEFINITIONS ---
interface Task {
    task_key: string;
    action_type: string;
    result?: { status?: string };
    dependencies?: string[];
    // Add full task data structure here if needed
}

interface Stage {
    stage_name: string;
    status: string;
    tasks: Task[];
}

interface RunData {
    run_id: string;
    workflow_name: string;
    overall_status: string;
    stages: Stage[];
}

// --- STYLING CONSTANTS ---
const statusColors: { [key: string]: string } = {
    Success: '#22c55e', // green-500
    Failure: '#ef4444', // red-500
    Skipped: '#eab308', // yellow-500
    Pending: '#a1a1aa', // zinc-400
    default: '#a1a1aa', // zinc-400
};

const STAGE_WIDTH = 350;
const STAGE_HEIGHT = 100;
const TASK_WIDTH = 280;
const TASK_HEIGHT = 70;

// --- NODE & EDGE GENERATION ---
const createGraphLayout = (runData: RunData) => {
    const nodes: Node[] = [];
    const edges: Edge[] = [];
    let yPos = 0;

    runData.stages.forEach((stage, stageIndex) => {
        const stageColor = statusColors[stage.status] || statusColors.default;
        const stageNode: Node = {
            id: stage.stage_name,
            position: { x: 0, y: yPos },
            data: { 
                label: stage.stage_name,
                type: 'stage',
                status: stage.status,
                taskCount: stage.tasks.length,
                rawData: stage // Store raw data for expansion
            },
            style: {
                width: STAGE_WIDTH,
                height: STAGE_HEIGHT,
                background: 'white',
                color: '#1f2937', // gray-800
                border: `2px solid ${stageColor}`,
                borderRadius: '12px',
                fontSize: '16px',
                fontWeight: 'bold',
                boxShadow: `0 6px 20px 0 ${stageColor}30`,
            },
            type: 'default' // Using default node type
        };
        nodes.push(stageNode);

        if (stageIndex > 0) {
            edges.push({
                id: `e-${runData.stages[stageIndex - 1].stage_name}-${stage.stage_name}`,
                source: runData.stages[stageIndex - 1].stage_name,
                target: stage.stage_name,
                type: 'smoothstep',
                style: { stroke: '#9ca3af', strokeWidth: 3 } // gray-400
            });
        }
        
        yPos += STAGE_HEIGHT + 60;
    });

    return { initialNodes: nodes, initialEdges: edges };
};

// --- MAIN COMPONENT ---
export default function WorkflowVisualizer({ params }: { params: { run_id: string } }) {
    const [runData, setRunData] = useState<RunData | null>(null);
    const [selectedElement, setSelectedElement] = useState<any | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const [reactFlowInstance, setReactFlowInstance] = useState<ReactFlowInstance | null>(null);

    // Initial graph layout effect
    useEffect(() => {
        if (!runData) return;

        const initialNodes: Node[] = [];
        const initialEdges: Edge[] = [];
        let yPos = 0;

        runData.stages.forEach((stage, stageIndex) => {
            const stageColor = statusColors[stage.status] || statusColors.default;
            initialNodes.push({
                id: stage.stage_name,
                position: { x: 0, y: yPos },
                data: { label: stage.stage_name, type: 'stage', rawData: stage },
                style: { width: STAGE_WIDTH, height: STAGE_HEIGHT, border: `2px solid ${stageColor}`, fontSize: '16px', fontWeight: 'bold' },
            });

            if (stageIndex > 0) {
                initialEdges.push({
                    id: `e-${runData.stages[stageIndex - 1].stage_name}-${stage.stage_name}`,
                    source: runData.stages[stageIndex - 1].stage_name,
                    target: stage.stage_name,
                    type: 'smoothstep',
                    style: { stroke: '#9ca3af', strokeWidth: 3 }
                });
            }
            yPos += STAGE_HEIGHT + 60;
        });

        setNodes(initialNodes);
        setEdges(initialEdges);
        setTimeout(() => reactFlowInstance?.fitView(), 100);

    }, [runData, setNodes, setEdges, reactFlowInstance]);

    // Data fetching effect
    useEffect(() => {
        if (!params.run_id) return;
        const fetchRunDetails = async () => {
            try { setLoading(true);
                const response = await fetch(`http://127.0.0.1:5002/api/run/${params.run_id}`);
                if (!response.ok) throw new Error(`API Error: ${response.status} ${response.statusText}`);
                const data: RunData = await response.json();
                setRunData(data);
            } catch (err) { setError(err instanceof Error ? err.message : 'Unknown error');
            } finally { setLoading(false); }
        };
        fetchRunDetails();
    }, [params.run_id]);

    const onNodeClick = useCallback((_event: React.MouseEvent, node: Node) => {
        setSelectedElement(node.data.rawData);

        if (node.data.type === 'stage') {
            const stage = node.data.rawData as Stage;
            
            setNodes(currentNodes => {
                const isExpanded = currentNodes.some(n => n.parentNode === node.id);
                
                if (isExpanded) {
                    // Collapse: remove task nodes and their edges
                    const taskIds = stage.tasks.map(t => t.task_key);
                    setEdges(eds => eds.filter(e => !taskIds.includes(e.source) && !taskIds.includes(e.target)));
                    return currentNodes.filter(n => n.parentNode !== node.id);
                } else {
                    // Expand: add task nodes and edges
                    const newNodes: Node[] = stage.tasks.map((task, index) => {
                        const taskColor = statusColors[task.result?.status || 'Success'] || statusColors.default;
                        return {
                            id: task.task_key,
                            position: { x: (index % 2 === 0 ? -1 : 1) * (TASK_WIDTH / 2 + 60), y: (Math.floor(index / 2) + 1) * (TASK_HEIGHT + 20) },
                            data: { label: task.task_key, type: 'task', rawData: task },
                            parentNode: node.id,
                            extent: 'parent',
                            style: { width: TASK_WIDTH, height: TASK_HEIGHT, border: `1px solid ${taskColor}`, background: '#f9fafb' }
                        };
                    });

                    const newEdges: Edge[] = [];
                    stage.tasks.forEach(task => {
                        task.dependencies?.forEach(dep => {
                             // Check if the dependency is within the same stage or cross-stage
                            if (stage.tasks.some(t => t.task_key === dep)) {
                                // Intra-stage edge
                                newEdges.push({ id: `e-${dep}-${task.task_key}`, source: dep, target: task.task_key, type: 'smoothstep' });
                            }
                        });
                    });
                    
                    setEdges(eds => [...eds, ...newEdges]);
                    return [...currentNodes, ...newNodes];
                }
            });
            setTimeout(() => reactFlowInstance?.fitView({ duration: 500 }), 100);
        }
    }, [setNodes, setEdges, reactFlowInstance]);

    // --- Render Logic ---
    if (loading) return <div className="flex items-center justify-center h-screen bg-white text-gray-500 text-2xl animate-pulse">Deconstructing ThoughtTrail...</div>;
    if (error) return <div className="flex items-center justify-center h-screen bg-white text-red-600 text-2xl p-8">{error}</div>;

    return (
        <div className="flex h-screen bg-white text-black font-sans">
            <div className="w-2/3 h-full">
                <ReactFlow
                    nodes={nodes}
                    edges={edges}
                    onNodesChange={onNodesChange}
                    onEdgesChange={onEdgesChange}
                    onNodeClick={onNodeClick}
                    onInit={setReactFlowInstance}
                    fitView
                    nodesDraggable={true}
                    className="bg-gray-50"
                >
                    <Background /> <Controls /> <MiniMap />
                </ReactFlow>
            </div>
            <aside className="w-1/3 h-full bg-gray-50 p-6 overflow-y-auto border-l border-gray-200">
                <Link href="/" className="text-blue-500 hover:text-blue-700 transition-colors mb-6 block font-semibold">&larr; Back to All Runs</Link>
                <h2 className="text-3xl font-bold mb-4 border-b border-gray-200 pb-3 text-gray-800">Deconstruction</h2>
                {selectedElement ? (
                    <div className="space-y-4">
                        <div>
                            <h3 className="text-xl font-semibold text-blue-600">{selectedElement.stage_name || selectedElement.task_key}</h3>
                            <p className="text-sm text-gray-500">Status: {selectedElement.status || selectedElement.result?.status}</p>
                        </div>
                        <div className="bg-white rounded-lg p-4 text-sm border border-gray-200">
                            <h4 className="font-bold text-gray-700 mb-2">Full IAR Data:</h4>
                            <pre className="whitespace-pre-wrap text-xs text-gray-600">
                                {JSON.stringify(selectedElement, null, 2)}
                            </pre>
                        </div>
                    </div>
                ) : (
                    <div className="flex items-center justify-center h-full text-gray-400">
                        <p>Select a stage to deconstruct its logic.</p>
                    </div>
                )}
            </aside>
        </div>
    );
}
