import { useState, useEffect, useRef } from 'react';
import { trackEvent } from '@/services/analytics';

const NAMES = [
  'Sarah', 'James', 'Emma', 'Oliver', 'Amelia', 'George', 'Isla', 'Harry',
  'Mia', 'Jack', 'Sophie', 'William', 'Lily', 'Thomas', 'Grace', 'Charlie',
  'Olivia', 'Daniel', 'Ava', 'Noah', 'Chloe', 'Ethan', 'Emily', 'Liam',
];

const CITIES = [
  'London', 'Manchester', 'Birmingham', 'Leeds', 'Bristol', 'Edinburgh',
  'Glasgow', 'Liverpool', 'Sheffield', 'Newcastle', 'Nottingham', 'Cardiff',
  'Belfast', 'Southampton', 'Brighton', 'Oxford', 'Cambridge', 'Reading',
];

const ACTIONS = [
  { text: 'just signed up', icon: 'signup' },
  { text: 'researched a trending product', icon: 'research' },
  { text: 'ran a viability check', icon: 'viability' },
  { text: 'saved a product to their shortlist', icon: 'save' },
  { text: 'used the profit calculator', icon: 'tool' },
];

function pick(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function timeSuffix() {
  const mins = Math.floor(Math.random() * 12) + 1;
  return `${mins} min ago`;
}

/**
 * Social proof toast notifications.
 * Shows periodic activity notifications on public marketing pages.
 */
export default function SocialProofToast() {
  const [notification, setNotification] = useState(null);
  const [visible, setVisible] = useState(false);
  const timeoutRef = useRef(null);
  const intervalRef = useRef(null);

  const showNotification = () => {
    const name = pick(NAMES);
    const city = pick(CITIES);
    const action = pick(ACTIONS);
    const time = timeSuffix();

    setNotification({ name, city, action: action.text, time });
    setVisible(true);

    trackEvent('social_proof_impression', { action: action.text });

    // Auto-hide after 4 seconds
    timeoutRef.current = setTimeout(() => {
      setVisible(false);
    }, 4000);
  };

  useEffect(() => {
    // First notification after 8 seconds
    const initialDelay = setTimeout(() => {
      showNotification();
      // Then every 25-40 seconds
      intervalRef.current = setInterval(() => {
        showNotification();
      }, 25000 + Math.random() * 15000);
    }, 8000);

    return () => {
      clearTimeout(initialDelay);
      clearTimeout(timeoutRef.current);
      clearInterval(intervalRef.current);
    };
  }, []);

  if (!notification || !visible) return null;

  return (
    <div
      className="fixed bottom-20 left-4 z-50 max-w-xs animate-in slide-in-from-left-5 fade-in duration-300"
      data-testid="social-proof-toast"
    >
      <div className="bg-white rounded-xl shadow-lg border border-slate-200 px-4 py-3 flex items-start gap-3">
        <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center flex-shrink-0 mt-0.5">
          <span className="text-xs font-bold text-indigo-600">{notification.name[0]}</span>
        </div>
        <div className="min-w-0">
          <p className="text-sm text-slate-800 leading-snug">
            <span className="font-semibold">{notification.name}</span>
            {' from '}
            <span className="font-medium">{notification.city}</span>
            {' '}
            {notification.action}
          </p>
          <p className="text-xs text-slate-400 mt-0.5">{notification.time}</p>
        </div>
      </div>
    </div>
  );
}
