import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { EnhancedMessage } from '@/types/protocol';

type ProtocolStatus = Record<string, boolean>;

interface MessageListProps {
  messages: EnhancedMessage[];
  protocolStatus?: ProtocolStatus;
}

const MessageList: React.FC<MessageListProps> = ({ messages }) => {
  console.log('MessageList received messages:', messages);
  console.log('MessageList messages length:', messages.length);

  return (
    <div className="space-y-4">
      {messages.map((msg, index) => {
        console.log(`Rendering message ${index}:`, msg);
        return (
          <div key={index} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`p-3 rounded-lg max-w-lg ${
                msg.sender === 'user' ? 'bg-green-800 text-white' :
                msg.message_type === 'spr' ? 'bg-purple-800 text-purple-200' :
                (msg.message_type === 'protocol_init' || msg.message_type === 'error') ? 'bg-red-800 text-red-200 italic' :
                'bg-blue-800 text-white'
              }`}>
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default MessageList;


