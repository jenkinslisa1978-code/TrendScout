import React from "react";
import ReactDOM from "react-dom/client";
import { HelmetProvider } from "react-helmet-async";
import "@/index.css";
import App from "@/App";

// Web Vitals — report core metrics
import { onCLS, onFID, onLCP, onFCP, onTTFB } from 'web-vitals';

const reportVital = (metric) => {
  // Log to console in dev; in production, send to analytics endpoint
  if (process.env.NODE_ENV === 'development') {
    console.log(`[Web Vital] ${metric.name}: ${metric.value.toFixed(2)}`);
  }
};

onCLS(reportVital);
onFCP(reportVital);
onLCP(reportVital);
onTTFB(reportVital);

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <HelmetProvider>
      <App />
    </HelmetProvider>
  </React.StrictMode>,
);
