/*
 FR: Fichier: App.tsx — Composant racine React de l'interface web
 EN: File: App.tsx — Root React component for the web interface
 ES: Archivo: App.tsx — Componente raíz React para la interfaz web
 ZH: 文件: App.tsx — Web 界面根 React 组件
*/

// Application principale O-Red
// FR: Application principale O-Red
// EN: O-Red main application
// ES: Aplicación principal O-Red
// ZH: O-Red 主应用

import React, { Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';

// Layouts
import { MainLayout } from './layouts/MainLayout';
import { AuthLayout } from './layouts/AuthLayout';
import { OnboardingLayout } from './layouts/OnboardingLayout';

// Pages - Lazy loading pour de meilleures performances
const Home = React.lazy(() => import('./pages/Home'));
const Login = React.lazy(() => import('./pages/auth/Login'));
const Register = React.lazy(() => import('./pages/auth/Register'));
const Onboarding = React.lazy(() => import('./pages/onboarding/Onboarding'));
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
const Profiles = React.lazy(() => import('./pages/Profiles'));
const Messages = React.lazy(() => import('./pages/Messages'));
const ORedMind = React.lazy(() => import('./pages/ORedMind'));
const ORedStore = React.lazy(() => import('./pages/ORedStore'));
const ORedOffice = React.lazy(() => import('./pages/ORedOffice'));
const ORedSearch = React.lazy(() => import('./pages/ORedSearch'));
const Settings = React.lazy(() => import('./pages/Settings'));
const Network = React.lazy(() => import('./pages/Network'));
const Security = React.lazy(() => import('./pages/Security'));

// Hooks
import { useAuth } from './hooks/useAuth';
import { useORedNode } from './hooks/useORedNode';

// Components
import { LoadingSpinner } from './components/ui/LoadingSpinner';
import { ErrorBoundary } from './components/ui/ErrorBoundary';
import { PWAPrompt } from './components/pwa/PWAPrompt';

// Animations
const pageVariants = {
  initial: { opacity: 0, y: 20 },
  in: { opacity: 1, y: 0 },
  out: { opacity: 0, y: -20 }
};

const pageTransition = {
  type: 'tween',
  ease: 'anticipate',
  duration: 0.3
};

function App() {
  const { user, isLoading: authLoading } = useAuth();
  const { nodeStatus, isConnected } = useORedNode();

  // Composant de chargement global
  const GlobalLoading = () => (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 flex items-center justify-center">
      <div className="text-center">
        <LoadingSpinner size="lg" />
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-4 text-white"
        >
          <h2 className="text-xl font-semibold">Initialisation d'O-Red</h2>
          <p className="text-gray-300 mt-2">Connexion au réseau décentralisé...</p>
        </motion.div>
      </div>
    </div>
  );

  // Composant de page avec suspense
  const PageWithSuspense = ({ children }: { children: React.ReactNode }) => (
    <Suspense
      fallback={
        <div className="flex items-center justify-center min-h-[400px]">
          <LoadingSpinner size="md" />
        </div>
      }
    >
      <ErrorBoundary>{children}</ErrorBoundary>
    </Suspense>
  );

  // Route protégée
  const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
    if (authLoading) return <GlobalLoading />;
    if (!user) return <Navigate to="/auth/login" replace />;
    return <>{children}</>;
  };

  // Route publique (redirige si connecté)
  const PublicRoute = ({ children }: { children: React.ReactNode }) => {
    if (authLoading) return <GlobalLoading />;
    if (user && !user.needsOnboarding) return <Navigate to="/dashboard" replace />;
    return <>{children}</>;
  };

  // Route d'onboarding
  const OnboardingRoute = ({ children }: { children: React.ReactNode }) => {
    if (authLoading) return <GlobalLoading />;
    if (!user) return <Navigate to="/auth/login" replace />;
    if (!user.needsOnboarding) return <Navigate to="/dashboard" replace />;
    return <>{children}</>;
  };

  if (authLoading) {
    return <GlobalLoading />;
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <AnimatePresence mode="wait">
        <Routes>
          {/* Routes publiques */}
          <Route path="/" element={
            <PublicRoute>
              <PageWithSuspense>
                <motion.div
                  initial="initial"
                  animate="in"
                  exit="out"
                  variants={pageVariants}
                  transition={pageTransition}
                >
                  <Home />
                </motion.div>
              </PageWithSuspense>
            </PublicRoute>
          } />

          {/* Routes d'authentification */}
          <Route path="/auth/*" element={
            <PublicRoute>
              <AuthLayout>
                <Routes>
                  <Route path="login" element={
                    <PageWithSuspense>
                      <motion.div
                        initial="initial"
                        animate="in"
                        exit="out"
                        variants={pageVariants}
                        transition={pageTransition}
                      >
                        <Login />
                      </motion.div>
                    </PageWithSuspense>
                  } />
                  <Route path="register" element={
                    <PageWithSuspense>
                      <motion.div
                        initial="initial"
                        animate="in"
                        exit="out"
                        variants={pageVariants}
                        transition={pageTransition}
                      >
                        <Register />
                      </motion.div>
                    </PageWithSuspense>
                  } />
                </Routes>
              </AuthLayout>
            </PublicRoute>
          } />

          {/* Route d'onboarding */}
          <Route path="/onboarding" element={
            <OnboardingRoute>
              <OnboardingLayout>
                <PageWithSuspense>
                  <motion.div
                    initial="initial"
                    animate="in"
                    exit="out"
                    variants={pageVariants}
                    transition={pageTransition}
                  >
                    <Onboarding />
                  </motion.div>
                </PageWithSuspense>
              </OnboardingLayout>
            </OnboardingRoute>
          } />

          {/* Routes protégées */}
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <MainLayout>
                <PageWithSuspense>
                  <motion.div
                    initial="initial"
                    animate="in"
                    exit="out"
                    variants={pageVariants}
                    transition={pageTransition}
                  >
                    <Dashboard />
                  </motion.div>
                </PageWithSuspense>
              </MainLayout>
            </ProtectedRoute>
          } />

          <Route path="/profiles" element={
            <ProtectedRoute>
              <MainLayout>
                <PageWithSuspense>
                  <motion.div
                    initial="initial"
                    animate="in"
                    exit="out"
                    variants={pageVariants}
                    transition={pageTransition}
                  >
                    <Profiles />
                  </motion.div>
                </PageWithSuspense>
              </MainLayout>
            </ProtectedRoute>
          } />

          <Route path="/messages" element={
            <ProtectedRoute>
              <MainLayout>
                <PageWithSuspense>
                  <motion.div
                    initial="initial"
                    animate="in"
                    exit="out"
                    variants={pageVariants}
                    transition={pageTransition}
                  >
                    <Messages />
                  </motion.div>
                </PageWithSuspense>
              </MainLayout>
            </ProtectedRoute>
          } />

          {/* O-Red Ecosystem Apps */}
          <Route path="/ored-mind" element={
            <ProtectedRoute>
              <MainLayout>
                <PageWithSuspense>
                  <motion.div
                    initial="initial"
                    animate="in"
                    exit="out"
                    variants={pageVariants}
                    transition={pageTransition}
                  >
                    <ORedMind />
                  </motion.div>
                </PageWithSuspense>
              </MainLayout>
            </ProtectedRoute>
          } />

          <Route path="/ored-store" element={
            <ProtectedRoute>
              <MainLayout>
                <PageWithSuspense>
                  <motion.div
                    initial="initial"
                    animate="in"
                    exit="out"
                    variants={pageVariants}
                    transition={pageTransition}
                  >
                    <ORedStore />
                  </motion.div>
                </PageWithSuspense>
              </MainLayout>
            </ProtectedRoute>
          } />

          <Route path="/ored-office" element={
            <ProtectedRoute>
              <MainLayout>
                <PageWithSuspense>
                  <motion.div
                    initial="initial"
                    animate="in"
                    exit="out"
                    variants={pageVariants}
                    transition={pageTransition}
                  >
                    <ORedOffice />
                  </motion.div>
                </PageWithSuspense>
              </MainLayout>
            </ProtectedRoute>
          } />

          <Route path="/ored-search" element={
            <ProtectedRoute>
              <MainLayout>
                <PageWithSuspense>
                  <motion.div
                    initial="initial"
                    animate="in"
                    exit="out"
                    variants={pageVariants}
                    transition={pageTransition}
                  >
                    <ORedSearch />
                  </motion.div>
                </PageWithSuspense>
              </MainLayout>
            </ProtectedRoute>
          } />

          {/* Configuration et administration */}
          <Route path="/settings" element={
            <ProtectedRoute>
              <MainLayout>
                <PageWithSuspense>
                  <motion.div
                    initial="initial"
                    animate="in"
                    exit="out"
                    variants={pageVariants}
                    transition={pageTransition}
                  >
                    <Settings />
                  </motion.div>
                </PageWithSuspense>
              </MainLayout>
            </ProtectedRoute>
          } />

          <Route path="/network" element={
            <ProtectedRoute>
              <MainLayout>
                <PageWithSuspense>
                  <motion.div
                    initial="initial"
                    animate="in"
                    exit="out"
                    variants={pageVariants}
                    transition={pageTransition}
                  >
                    <Network />
                  </motion.div>
                </PageWithSuspense>
              </MainLayout>
            </ProtectedRoute>
          } />

          <Route path="/security" element={
            <ProtectedRoute>
              <MainLayout>
                <PageWithSuspense>
                  <motion.div
                    initial="initial"
                    animate="in"
                    exit="out"
                    variants={pageVariants}
                    transition={pageTransition}
                  >
                    <Security />
                  </motion.div>
                </PageWithSuspense>
              </MainLayout>
            </ProtectedRoute>
          } />

          {/* Route 404 */}
          <Route path="*" element={
            <div className="min-h-screen flex items-center justify-center bg-gray-900">
              <div className="text-center">
                <h1 className="text-6xl font-bold text-white mb-4">404</h1>
                <p className="text-gray-400 mb-8">Page non trouvée dans le réseau O-Red</p>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => window.history.back()}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Retourner
                </motion.button>
              </div>
            </div>
          } />
        </Routes>
      </AnimatePresence>

      {/* PWA Install Prompt */}
      <PWAPrompt />

      {/* Indicateur de statut réseau */}
      {!isConnected && (
        <motion.div
          initial={{ y: 100 }}
          animate={{ y: 0 }}
          className="fixed bottom-4 right-4 bg-yellow-500 text-black px-4 py-2 rounded-lg shadow-lg"
        >
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-yellow-700 rounded-full animate-pulse"></div>
            <span className="text-sm font-medium">Reconnexion au réseau O-Red...</span>
          </div>
        </motion.div>
      )}
    </div>
  );
}

export default App;