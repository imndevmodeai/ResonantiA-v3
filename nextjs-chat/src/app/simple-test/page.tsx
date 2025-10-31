'use client';

import React, { useState, useEffect, useRef } from 'react';

export default function SimpleTest() {
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState<string[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const connectWebSocket = () => {
      console.log('🔗 Attempting to connect to ws://localhost:8765');
      setMessages(prev => [...prev, '🔗 Attempting to connect to ws://localhost:8765...']);
      
      try {
        wsRef.current = new WebSocket('ws://localhost:8765');
        console.log('✅ WebSocket object created successfully');
        setMessages(prev => [...prev, '✅ WebSocket object created successfully']);
      } catch (error) {
        console.error('❌ Failed to create WebSocket:', error);
        setMessages(prev => [...prev, `❌ Failed to create WebSocket: ${error}`]);
        return;
      }

      wsRef.current.onopen = () => {
        console.log('✅ WebSocket connected!');
        setIsConnected(true);
        setMessages(prev => [...prev, '✅ Connected to VCD Bridge!']);
      };

      wsRef.current.onmessage = (event) => {
        console.log('📨 Received message:', event.data);
        setMessages(prev => [...prev, `📨 ${event.data.substring(0, 100)}...`]);
      };

      wsRef.current.onclose = () => {
        console.log('❌ WebSocket disconnected');
        setIsConnected(false);
        setMessages(prev => [...prev, '❌ Disconnected from VCD Bridge']);
        
        // Attempt to reconnect after 3 seconds
        setTimeout(() => {
          if (!isConnected) {
            connectWebSocket();
          }
        }, 3000);
      };

      wsRef.current.onerror = (error) => {
        console.error('🚨 WebSocket error:', error);
        setMessages(prev => [...prev, `🚨 WebSocket error: ${error}`]);
        console.log('WebSocket readyState:', wsRef.current?.readyState);
        console.log('WebSocket URL:', wsRef.current?.url);
      };
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>Simple WebSocket Test</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <div style={{ 
          display: 'inline-block',
          width: '12px',
          height: '12px',
          borderRadius: '50%',
          backgroundColor: isConnected ? '#10b981' : '#ef4444',
          marginRight: '8px'
        }} />
        <span>Status: {isConnected ? 'Connected' : 'Disconnected'}</span>
      </div>

      <div style={{ 
        height: '400px', 
        overflow: 'auto', 
        border: '1px solid #ccc', 
        padding: '10px',
        backgroundColor: '#f9f9f9'
      }}>
        {messages.map((message, index) => (
          <div key={index} style={{ marginBottom: '5px', fontSize: '14px' }}>
            {message}
          </div>
        ))}
      </div>

      <div style={{ marginTop: '20px' }}>
        <button 
          onClick={() => {
            if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
              wsRef.current.send('Test message from frontend');
            }
          }}
          disabled={!isConnected}
          style={{
            padding: '10px 20px',
            backgroundColor: isConnected ? '#10b981' : '#ccc',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: isConnected ? 'pointer' : 'not-allowed',
            marginRight: '10px'
          }}
        >
          Send Test Message
        </button>
        
        <button 
          onClick={() => {
            console.log('🔄 Manual reconnect attempt');
            setMessages(prev => [...prev, '🔄 Manual reconnect attempt...']);
            if (wsRef.current) {
              wsRef.current.close();
            }
            setTimeout(() => {
              connectWebSocket();
            }, 1000);
          }}
          style={{
            padding: '10px 20px',
            backgroundColor: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Reconnect
        </button>
      </div>
    </div>
  );
}
