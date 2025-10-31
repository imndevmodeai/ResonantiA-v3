import React, { useState, useEffect } from 'react';
import './App.css';
import CommandInput from './CommandInput';
import StreamDisplay from './StreamDisplay';
import DashboardView from './DashboardView';

function App() {
  const [streamData, setStreamData] = useState([]);
  const [webSocket, setWebSocket] = useState(null);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8888/ws/v1/stream');

    ws.onopen = () => {
      console.log('WebSocket Connected');
      setStreamData(prev => [...prev, {type: 'SYSTEM_MESSAGE', payload: 'Connected to ArchE Nexus.'}]);
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      console.log('WebSocket Message:', message);
      setStreamData(prev => [...prev, message]);
    };

    ws.onclose = () => {
      console.log('WebSocket Disconnected');
      setStreamData(prev => [...prev, {type: 'SYSTEM_MESSAGE', payload: 'Connection lost. Attempting to reconnect...'}]);
    };

    ws.onerror = (error) => {
      console.error('WebSocket Error:', error);
      setStreamData(prev => [...prev, {type: 'SYSTEM_MESSAGE', payload: 'An error occurred with the connection.'}]);
    };

    setWebSocket(ws);

    return () => {
      ws.close();
    };
  }, []);

  const handleSendCommand = async (command) => {
    try {
      const response = await fetch('http://localhost:8888/api/v1/command', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ command }),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const result = await response.json();
      console.log('Command API response:', result);
    } catch (error) {
      console.error("Failed to send command:", error);
      setStreamData(prev => [...prev, {type: 'SYSTEM_ERROR', payload: `Failed to send command: ${error.message}`}]);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>ArchE Nexus Interface</h1>
      </header>
      <main className="App-main">
        <div className="left-panel">
          <StreamDisplay data={streamData} />
          <CommandInput onSendCommand={handleSendCommand} />
        </div>
        <div className="right-panel">
          <DashboardView />
        </div>
      </main>
    </div>
  );
}

export default App;
