import { useState, useEffect, useRef, useCallback } from 'react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

/**
 * Custom hook for WebSocket real-time notifications.
 * Connects to the backend WebSocket endpoint and provides live job updates.
 */
export function useNotifications() {
  const [notifications, setNotifications] = useState([]);
  const [connected, setConnected] = useState(false);
  const [activeJobs, setActiveJobs] = useState({});
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const pingIntervalRef = useRef(null);

  const connect = useCallback(() => {
    const token = localStorage.getItem('access_token') || '';
    const wsUrl = API_URL.replace('https://', 'wss://').replace('http://', 'ws://');
    const url = `${wsUrl}/api/ws/notifications?token=${token}`;

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        setConnected(true);
        // Send ping every 30s to keep alive
        pingIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send('ping');
          }
        }, 30000);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'pong') return;

          // Add to notifications list (max 50)
          setNotifications(prev => [data, ...prev].slice(0, 50));

          // Track active jobs
          if (data.type === 'job_started') {
            setActiveJobs(prev => ({
              ...prev,
              [data.job_type]: { status: 'running', ...data },
            }));
          } else if (data.type === 'job_progress') {
            setActiveJobs(prev => ({
              ...prev,
              [data.job_type]: { status: 'running', ...data },
            }));
          } else if (data.type === 'job_completed') {
            setActiveJobs(prev => {
              const next = { ...prev };
              delete next[data.job_type];
              return next;
            });
          } else if (data.type === 'job_failed') {
            setActiveJobs(prev => {
              const next = { ...prev };
              delete next[data.job_type];
              return next;
            });
          }
        } catch (e) {
          // Ignore parse errors
        }
      };

      ws.onclose = () => {
        setConnected(false);
        clearInterval(pingIntervalRef.current);
        // Reconnect after 5s
        reconnectTimeoutRef.current = setTimeout(connect, 5000);
      };

      ws.onerror = () => {
        ws.close();
      };
    } catch (e) {
      // Reconnect after 5s on error
      reconnectTimeoutRef.current = setTimeout(connect, 5000);
    }
  }, []);

  useEffect(() => {
    connect();
    return () => {
      clearTimeout(reconnectTimeoutRef.current);
      clearInterval(pingIntervalRef.current);
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  const clearNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  return {
    notifications,
    connected,
    activeJobs,
    clearNotifications,
    hasActiveJobs: Object.keys(activeJobs).length > 0,
  };
}
