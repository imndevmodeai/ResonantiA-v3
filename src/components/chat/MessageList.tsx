import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const MessageList = ({ messages }) => {
  return (
    <div className="flex-1 overflow-y-auto p-4">
      {messages.map((msg, index) => (
        <div key={index} className="flex items-start mb-4">
          <div className="ml-3">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg}</ReactMarkdown>
          </div>
        </div>
      ))}
    </div>
  );
};

export default MessageList;
