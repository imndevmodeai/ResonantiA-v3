import { create } from 'zustand';
import { IAREnvironment, LogEntry, Message } from '@/app/types';

const WEBSOCKET_URL = process.env.NEXT_PUBLIC_WEBSOCKET_URL || 'ws://localhost:8765';

interface AppState {
  messages: Message[];
  logEntries: LogEntry[];
  iarData: IAREnvironment | null;
  isConnected: boolean;
  error: string | null;
  websocket: WebSocket | null;
  reconnectDelayMs: number;
  shouldReconnect: boolean;
  addMessage: (message: Message) => void;
  addLogEntry: (entry: LogEntry) => void;
  setIarData: (data: IAREnvironment) => void;
  setError: (error: string | null) => void;
  connect: () => void;
  disconnect: () => void;
  sendMessage: (message: Omit<Message, 'id' | 'timestamp' | 'protocol_compliance'>) => void;
}

export const useStore = create<AppState>((set, get) => ({
  messages: [],
  logEntries: [],
  iarData: null,
  isConnected: false,
  error: null,
  websocket: null,
  reconnectDelayMs: 1000,
  shouldReconnect: true,
  addMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),
  addLogEntry: (entry) => set((state) => ({ logEntries: [...state.logEntries, entry] })),
  setIarData: (data) => set({ iarData: data }),
  setError: (error) => set({ error }),
  disconnect: () => {
    const ws = get().websocket;
    set({ shouldReconnect: false });
    if (ws) {
      try { ws.close(); } catch {}
      set({ websocket: null, isConnected: false });
    }
  },
  connect: () => {
    const { websocket } = get();
    if (websocket && websocket.readyState < WebSocket.CLOSING) {
      return;
    }

    const ws = new WebSocket(WEBSOCKET_URL);

    ws.onopen = () => {
      set({ isConnected: true, error: null, websocket: ws, reconnectDelayMs: 1000, shouldReconnect: true });
      get().addMessage({
        id: Date.now().toString(),
        content: 'Successfully connected to the ArchE Nexus.',
        timestamp: new Date().toISOString(),
        sender: 'arche',
        message_type: 'system',
        protocol_compliance: true,
      });
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.type === 'connection_established') {
          get().addMessage({
            id: Date.now().toString(),
            content: data.message || 'Connection established.',
            timestamp: new Date().toISOString(),
            sender: 'arche',
            message_type: 'system',
            protocol_compliance: true,
          });
          return;
        }

        if (data.sender && data.content && data.timestamp) {
          get().addMessage(data as Message);
          return;
        }

        if (data.type === 'nexus_event' && data.event) {
          if (data.event.topic === 'arche_response') {
            const payload = data.event.data;
            get().addMessage({
              id: Date.now().toString(),
              content: payload.content,
              timestamp: payload.timestamp || new Date().toISOString(),
              sender: payload.sender || 'arche',
              message_type: 'chat',
              protocol_compliance: true,
            });
            return;
          }
          
          if (data.event.topic === 'aco_event') {
            const payload = data.event.data;
            // Add ACO events as system messages
            get().addMessage({
              id: Date.now().toString(),
              content: `🧠 ACO: ${payload.message}`,
              timestamp: payload.timestamp || new Date().toISOString(),
              sender: 'arche',
              message_type: 'system',
              protocol_compliance: true,
            });
            return;
          }
          
          if (data.event.topic === 'thoughttrail_entry') {
            const payload = data.event.data;
            const entry: LogEntry = {
              id: Date.now().toString(),
              t: new Date().toISOString(),
              severity: 'info',
              msg: payload?.iar?.reflection || 'Thought trail event',
              meta: payload,
            } as unknown as LogEntry;
            get().addLogEntry(entry);
            return;
          }
        }
      } catch (e) {
        console.error('Failed to parse incoming message:', event.data);
        get().setError('Failed to parse incoming message.');
      }
    };

    ws.onerror = (event) => {
      console.error('WebSocket error:', event);
      get().setError('WebSocket connection error.');
    };

    ws.onclose = () => {
      const { reconnectDelayMs, shouldReconnect } = get();
      set({ isConnected: false, websocket: null });
      get().addMessage({
        id: Date.now().toString(),
        content: 'Connection to ArchE Nexus lost.',
        timestamp: new Date().toISOString(),
        sender: 'arche',
        message_type: 'system',
        protocol_compliance: true,
      });
      if (shouldReconnect) {
        const delay = Math.min(reconnectDelayMs * 2, 15000);
        setTimeout(() => {
          set({ reconnectDelayMs: delay });
          get().connect();
        }, reconnectDelayMs);
      }
    };

    set({ websocket: ws });
  },
  sendMessage: (message) => {
    const { websocket } = get();
    if (websocket && websocket.readyState === WebSocket.OPEN) {
      const fullMessage = {
        ...message,
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        protocol_compliance: true,
      };
      if (message.sender === 'user') {
        get().addMessage(fullMessage as Message);
      }
      websocket.send(JSON.stringify(fullMessage));
    } else {
      get().setError('Cannot send message: WebSocket is not connected.');
    }
  },
}));
