'use client';

import { useEffect, useRef } from 'react';
import { useStore } from '@/app/store';

export function WebSocketManager() {
  const connect = useStore((state) => state.connect);
  const hasConnected = useRef(false);

  useEffect(() => {
    if (!hasConnected.current) {
      connect();
      hasConnected.current = true;
    }
  }, [connect]);

  return null; // This component does not render anything
}
