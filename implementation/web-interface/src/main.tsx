/*
 FR: Fichier: main.tsx — Point d'entrée de l'application web (React/Vite)
 EN: File: main.tsx — Web application entrypoint (React/Vite)
 ES: Archivo: main.tsx — Punto de entrada de la aplicación web (React/Vite)
 ZH: 文件: main.tsx — Web 应用入口 (React/Vite)
*/

// Interface principale O-Red - Point d'entrée React

import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';

import App from './App';
import { ORedProvider } from './providers/ORedProvider';
import { ThemeProvider } from './providers/ThemeProvider';
import { AuthProvider } from './providers/AuthProvider';

import './styles/globals.css';

// Configuration du client de requêtes
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      cacheTime: 1000 * 60 * 30, // 30 minutes
      retry: (failureCount, error: any) => {
        // Ne pas retry pour les erreurs d'authentification
        if (error?.response?.status === 401) return false;
        return failureCount < 3;
      },
    },
    mutations: {
      retry: false,
    },
  },
});

// Configuration des toasts
const toastOptions = {
  duration: 4000,
  position: 'top-right' as const,
  style: {
    background: '#1f2937',
    color: '#f3f4f6',
    border: '1px solid #374151',
  },
  success: {
    style: {
      border: '1px solid #10b981',
    },
  },
  error: {
    style: {
      border: '1px solid #ef4444',
    },
  },
};

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider>
          <AuthProvider>
            <ORedProvider>
              <App />
              <Toaster toastOptions={toastOptions} />
            </ORedProvider>
          </AuthProvider>
        </ThemeProvider>
      </QueryClientProvider>
    </BrowserRouter>
  </React.StrictMode>
);