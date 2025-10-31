import React, { useEffect, useRef } from 'react';
import './StreamDisplay.css';

const StreamDisplay = ({ data }) => {
  const endOfMessagesRef = useRef(null);

  const scrollToBottom = () => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: "smooth" });
  }

  useEffect(() => {
    scrollToBottom();
  }, [data]);

  const renderMessage = (msg, index) => {
    const { type, payload } = msg;

    switch (type) {
      case 'TEXT_RESPONSE':
        return <div key={index} className="message arche-response">{payload}</div>;
      case 'STATUS_UPDATE':
        return <div key={index} className="message status-update">Status: {payload.task} ({Math.round(payload.progress * 100)}%)</div>;
      case 'SYSTEM_MESSAGE':
        return <div key={index} className="message system-message">{payload}</div>;
      case 'SYSTEM_ERROR':
        return <div key={index} className="message system-error">Error: {payload}</div>;
      case 'COMMAND_COMPLETE':
        return <div key={index} className="message command-complete">✓ Command Complete: {payload.final_reflection.summary}</div>;
      default:
        return <div key={index} className="message unknown-message">Unknown message type: {JSON.stringify(msg)}</div>;
    }
  };

  return (
    <div className="stream-display">
      {data.map(renderMessage)}
      <div ref={endOfMessagesRef} />
    </div>
  );
};

export default StreamDisplay;
