import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { EnhancedMessage } from '@/types/protocol';

interface MessageListProps {
  messages: EnhancedMessage[];
}

const MessageList: React.FC<MessageListProps> = ({ messages }) => {
  const renderMessage = (message: EnhancedMessage, index: number) => {
    const isUser = message.sender === 'user';
    const isSystem = message.sender === 'arche' && message.message_type === 'protocol_init';
    
    return (
      <div
        key={`${message.id || 'msg'}-${index}`}
        className={`message ${isUser ? 'user' : isSystem ? 'system' : 'assistant'}`}
      >
        <div className="message-header">
          <span className="sender">
            {isUser ? '🧑 User' : isSystem ? '⚙️ System' : '🤖 ArchE'}
          </span>
          <span className="timestamp">
            {new Date(message.timestamp).toLocaleTimeString()}
          </span>
          {message.protocol_version && (
            <span className="protocol-badge">
              {message.protocol_version}
            </span>
          )}
        </div>
        
        <div className="message-content">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {typeof message.content === 'string' ? message.content : JSON.stringify(message.content, null, 2)}
          </ReactMarkdown>
        </div>
        
        {/* Enhanced Protocol Indicators */}
        <div className="protocol-indicators">
          {message.iar && (
            <div className="indicator iar">
              <span className="label">IAR:</span>
              <span className={`status ${message.iar.status.toLowerCase()}`}>
                {message.iar.status}
              </span>
              <span className="confidence">
                {(message.iar.confidence * 100).toFixed(0)}%
              </span>
            </div>
          )}
          
          {message.spr_activations && message.spr_activations.length > 0 && (
            <div className="indicator sprs">
              <span className="label">SPRs:</span>
              <span className="count">{message.spr_activations.length}</span>
              <span className="spr-list">
                {message.spr_activations.map(spr => spr.spr_id).join(', ')}
              </span>
            </div>
          )}
          
          {message.temporal_context && (
            <div className="indicator temporal">
              <span className="label">⏰ Temporal:</span>
              <span className="horizon">{message.temporal_context.time_horizon}</span>
            </div>
          )}
          
          {message.meta_cognitive_state && (
            <div className="indicator meta">
              <span className="label">🧠 Meta:</span>
              <span className="sirc-phase">{message.meta_cognitive_state.sirc_phase || 'None'}</span>
            </div>
          )}
          
          {message.complex_system_visioning && (
            <div className="indicator complex">
              <span className="label">🌐 Complex:</span>
              <span className="scenario">{message.complex_system_visioning.scenario_name}</span>
            </div>
          )}
          
          {message.implementation_resonance && (
            <div className="indicator implementation">
              <span className="label">🔧 Implementation:</span>
              <span className="alignment">
                {(message.implementation_resonance.code_documentation_alignment * 100).toFixed(0)}%
              </span>
            </div>
          )}
          
          {message.protocol_init && (
            <div className="indicator protocol-init">
              <span className="label">🧠 Protocol:</span>
              <span className="status">{message.protocol_init.status}</span>
            </div>
          )}
          
          {message.protocol_error && (
            <div className="indicator protocol-error">
              <span className="label">⚠️ Error:</span>
              <span className="error">{message.protocol_error.message}</span>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="messages-container-refactored">
      {messages.map((message, index) => renderMessage(message, index))}
    </div>
  );
};

export default MessageList;


