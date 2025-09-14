import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface Message {
  id: string;
  type: 'user' | 'system' | 'cli_output' | 'cli_error' | 'cli_complete' | 'welcome' | 'query_received';
  content: string;
  timestamp: string;
}

const MessageList = ({ messages }: { messages: Message[] }) => {
  const getMessageStyle = (type: string) => {
    switch (type) {
      case 'user':
        return 'bg-blue-100 border-l-4 border-blue-500 p-3 ml-8';
      case 'system':
        return 'bg-gray-100 border-l-4 border-gray-500 p-3';
      case 'cli_output':
        return 'bg-green-50 border-l-4 border-green-500 p-3 font-mono text-sm';
      case 'cli_error':
        return 'bg-red-50 border-l-4 border-red-500 p-3 font-mono text-sm';
      case 'cli_complete':
        return 'bg-yellow-50 border-l-4 border-yellow-500 p-3';
      case 'welcome':
        return 'bg-purple-50 border-l-4 border-purple-500 p-3';
      case 'query_received':
        return 'bg-indigo-50 border-l-4 border-indigo-500 p-3';
      default:
        return 'bg-white border-l-4 border-gray-300 p-3';
    }
  };

  const getMessageIcon = (type: string) => {
    switch (type) {
      case 'user':
        return '👤';
      case 'system':
        return '🤖';
      case 'cli_output':
        return '💻';
      case 'cli_error':
        return '❌';
      case 'cli_complete':
        return '✅';
      case 'welcome':
        return '🎉';
      case 'query_received':
        return '🔍';
      default:
        return '💬';
    }
  };

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.map((msg) => (
        <div key={msg.id} className={`rounded-lg ${getMessageStyle(msg.type)}`}>
          <div className="flex items-start">
            <span className="text-lg mr-2">{getMessageIcon(msg.type)}</span>
            <div className="flex-1">
              <div className="text-xs text-gray-500 mb-1">
                {new Date(msg.timestamp).toLocaleTimeString()}
              </div>
              <div className="prose prose-sm max-w-none">
                {msg.type === 'cli_output' || msg.type === 'cli_error' ? (
                  <pre className="whitespace-pre-wrap text-xs bg-gray-800 text-green-400 p-2 rounded overflow-x-auto">
                    {msg.content}
                  </pre>
                ) : (
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {msg.content}
                  </ReactMarkdown>
                )}
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default MessageList;
