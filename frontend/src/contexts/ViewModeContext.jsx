import React, { createContext, useContext, useState, useEffect } from 'react';

const ViewModeContext = createContext(null);

export function ViewModeProvider({ children }) {
  const [mode, setMode] = useState(() => {
    return localStorage.getItem('trendscout_view_mode') || 'beginner';
  });

  useEffect(() => {
    localStorage.setItem('trendscout_view_mode', mode);
  }, [mode]);

  const toggleMode = () => setMode((m) => (m === 'beginner' ? 'advanced' : 'beginner'));
  const isBeginner = mode === 'beginner';
  const isAdvanced = mode === 'advanced';

  return (
    <ViewModeContext.Provider value={{ mode, setMode, toggleMode, isBeginner, isAdvanced }}>
      {children}
    </ViewModeContext.Provider>
  );
}

export function useViewMode() {
  const ctx = useContext(ViewModeContext);
  if (!ctx) {
    return { mode: 'beginner', setMode: () => {}, toggleMode: () => {}, isBeginner: true, isAdvanced: false };
  }
  return ctx;
}
