/*
 FR: Fichier: App.test.tsx — Tests unitaires pour le composant App (React)
 EN: File: App.test.tsx — Unit tests for the App component (React)
 ES: Archivo: App.test.tsx — Pruebas unitarias para el componente App (React)
 ZH: 文件: App.test.tsx — App 组件（React）的单元测试
*/

// Tests pour l'interface web React O-Red
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import userEvent from '@testing-library/user-event';
import { vi, describe, it, expect, beforeEach } from 'vitest';

// Mocks pour les services
vi.mock('../src/services/api', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
  authService: {
    login: vi.fn(),
    register: vi.fn(),
    logout: vi.fn(),
    getCurrentUser: vi.fn(),
    isAuthenticated: vi.fn(),
  },
  nodeService: {
    getNodes: vi.fn(),
    registerNode: vi.fn(),
    getNodeStats: vi.fn(),
  },
  aiService: {
    submitRequest: vi.fn(),
    getRequests: vi.fn(),
    getModels: vi.fn(),
  }
}));

// Mock des composants non critiques
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    button: ({ children, ...props }: any) => <button {...props}>{children}</button>,
    form: ({ children, ...props }: any) => <form {...props}>{children}</form>,
  },
  AnimatePresence: ({ children }: any) => children,
}));

// Helper pour wrapper les composants avec les providers nécessaires
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {children}
      </BrowserRouter>
    </QueryClientProvider>
  );
};

describe('Interface Web O-Red', () => {
  let wrapper: any;

  beforeEach(() => {
    wrapper = createWrapper();
    vi.clearAllMocks();
  });

  describe('Composant App principal', () => {
    it('devrait afficher la page de connexion par défaut', async () => {
      const { authService } = await import('../src/services/api');
      authService.isAuthenticated.mockReturnValue(false);

      const App = (await import('../src/App')).default;
      render(<App />, { wrapper });

      expect(screen.getByText(/connexion/i)).toBeInTheDocument();
    });

    it('devrait afficher le tableau de bord si authentifié', async () => {
      const { authService } = await import('../src/services/api');
      authService.isAuthenticated.mockReturnValue(true);
      authService.getCurrentUser.mockReturnValue({
        id: '1',
        username: 'testuser',
        email: 'test@example.com'
      });

      const App = (await import('../src/App')).default;
      render(<App />, { wrapper });

      await waitFor(() => {
        expect(screen.getByText(/tableau de bord/i)).toBeInTheDocument();
      });
    });
  });

  describe('Authentification', () => {
    describe('Composant Login', () => {
      it('devrait permettre la saisie des identifiants', async () => {
        const Login = (await import('../src/components/Auth/Login')).default;
        render(<Login />, { wrapper });

        const usernameInput = screen.getByLabelText(/nom d'utilisateur/i);
        const passwordInput = screen.getByLabelText(/mot de passe/i);

        await userEvent.type(usernameInput, 'testuser');
        await userEvent.type(passwordInput, 'password123');

        expect(usernameInput).toHaveValue('testuser');
        expect(passwordInput).toHaveValue('password123');
      });

      it('devrait appeler le service d\'authentification lors de la soumission', async () => {
        const { authService } = await import('../src/services/api');
        authService.login.mockResolvedValue({
          access_token: 'fake-token',
          token_type: 'bearer'
        });

        const Login = (await import('../src/components/Auth/Login')).default;
        render(<Login />, { wrapper });

        const usernameInput = screen.getByLabelText(/nom d'utilisateur/i);
        const passwordInput = screen.getByLabelText(/mot de passe/i);
        const submitButton = screen.getByRole('button', { name: /connexion/i });

        await userEvent.type(usernameInput, 'testuser');
        await userEvent.type(passwordInput, 'password123');
        await userEvent.click(submitButton);

        await waitFor(() => {
          expect(authService.login).toHaveBeenCalledWith({
            username: 'testuser',
            password: 'password123'
          });
        });
      });

      it('devrait afficher les erreurs de validation', async () => {
        const Login = (await import('../src/components/Auth/Login')).default;
        render(<Login />, { wrapper });

        const submitButton = screen.getByRole('button', { name: /connexion/i });
        await userEvent.click(submitButton);

        await waitFor(() => {
          expect(screen.getByText(/nom d'utilisateur requis/i)).toBeInTheDocument();
          expect(screen.getByText(/mot de passe requis/i)).toBeInTheDocument();
        });
      });
    });

    describe('Composant Register', () => {
      it('devrait permettre l\'inscription d\'un nouvel utilisateur', async () => {
        const { authService } = await import('../src/services/api');
        authService.register.mockResolvedValue({
          id: '1',
          username: 'newuser',
          email: 'new@example.com'
        });

        const Register = (await import('../src/components/Auth/Register')).default;
        render(<Register />, { wrapper });

        const usernameInput = screen.getByLabelText(/nom d'utilisateur/i);
        const emailInput = screen.getByLabelText(/email/i);
        const passwordInput = screen.getByLabelText(/mot de passe/i);
        const confirmPasswordInput = screen.getByLabelText(/confirmer/i);
        const submitButton = screen.getByRole('button', { name: /inscription/i });

        await userEvent.type(usernameInput, 'newuser');
        await userEvent.type(emailInput, 'new@example.com');
        await userEvent.type(passwordInput, 'password123');
        await userEvent.type(confirmPasswordInput, 'password123');
        await userEvent.click(submitButton);

        await waitFor(() => {
          expect(authService.register).toHaveBeenCalledWith({
            username: 'newuser',
            email: 'new@example.com',
            password: 'password123'
          });
        });
      });

      it('devrait vérifier que les mots de passe correspondent', async () => {
        const Register = (await import('../src/components/Auth/Register')).default;
        render(<Register />, { wrapper });

        const passwordInput = screen.getByLabelText(/mot de passe/i);
        const confirmPasswordInput = screen.getByLabelText(/confirmer/i);
        const submitButton = screen.getByRole('button', { name: /inscription/i });

        await userEvent.type(passwordInput, 'password123');
        await userEvent.type(confirmPasswordInput, 'differentpassword');
        await userEvent.click(submitButton);

        await waitFor(() => {
          expect(screen.getByText(/mots de passe ne correspondent pas/i)).toBeInTheDocument();
        });
      });
    });
  });

  describe('Tableau de bord', () => {
    it('devrait afficher les statistiques du réseau', async () => {
      const { nodeService } = await import('../src/services/api');
      nodeService.getNodes.mockResolvedValue([
        { id: '1', status: 'active', node_id: 'node1' },
        { id: '2', status: 'active', node_id: 'node2' },
      ]);

      const Dashboard = (await import('../src/components/Dashboard/Dashboard')).default;
      render(<Dashboard />, { wrapper });

      await waitFor(() => {
        expect(screen.getByText(/2 nœuds actifs/i)).toBeInTheDocument();
      });
    });

    it('devrait afficher les requêtes IA récentes', async () => {
      const { aiService } = await import('../src/services/api');
      aiService.getRequests.mockResolvedValue([
        {
          id: '1',
          model_type: 'text_generation',
          status: 'completed',
          created_at: '2024-01-01T10:00:00Z'
        },
        {
          id: '2',
          model_type: 'image_generation',
          status: 'processing',
          created_at: '2024-01-01T11:00:00Z'
        }
      ]);

      const Dashboard = (await import('../src/components/Dashboard/Dashboard')).default;
      render(<Dashboard />, { wrapper });

      await waitFor(() => {
        expect(screen.getByText(/text_generation/i)).toBeInTheDocument();
        expect(screen.getByText(/image_generation/i)).toBeInTheDocument();
      });
    });
  });

  describe('Gestion des nœuds', () => {
    it('devrait afficher la liste des nœuds', async () => {
      const { nodeService } = await import('../src/services/api');
      nodeService.getNodes.mockResolvedValue([
        {
          id: '1',
          node_id: 'node-123',
          ip_address: '192.168.1.100',
          status: 'active',
          capabilities: ['ai_computing', 'storage']
        },
        {
          id: '2',
          node_id: 'node-456',
          ip_address: '192.168.1.101',
          status: 'inactive',
          capabilities: ['relay']
        }
      ]);

      const NodeList = (await import('../src/components/Nodes/NodeList')).default;
      render(<NodeList />, { wrapper });

      await waitFor(() => {
        expect(screen.getByText('node-123')).toBeInTheDocument();
        expect(screen.getByText('node-456')).toBeInTheDocument();
        expect(screen.getByText('192.168.1.100')).toBeInTheDocument();
      });
    });

    it('devrait permettre l\'enregistrement d\'un nouveau nœud', async () => {
      const { nodeService } = await import('../src/services/api');
      nodeService.registerNode.mockResolvedValue({
        id: '1',
        node_id: 'new-node-789',
        status: 'active'
      });

      const NodeRegister = (await import('../src/components/Nodes/NodeRegister')).default;
      render(<NodeRegister />, { wrapper });

      const nodeIdInput = screen.getByLabelText(/id du nœud/i);
      const ipInput = screen.getByLabelText(/adresse ip/i);
      const portInput = screen.getByLabelText(/port/i);
      const submitButton = screen.getByRole('button', { name: /enregistrer/i });

      await userEvent.type(nodeIdInput, 'new-node-789');
      await userEvent.type(ipInput, '192.168.1.102');
      await userEvent.type(portInput, '8001');
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(nodeService.registerNode).toHaveBeenCalledWith({
          node_id: 'new-node-789',
          ip_address: '192.168.1.102',
          port: 8001,
          capabilities: expect.any(Array)
        });
      });
    });
  });

  describe('Interface IA', () => {
    it('devrait permettre de soumettre une requête IA', async () => {
      const { aiService } = await import('../src/services/api');
      aiService.getModels.mockResolvedValue([
        { id: 'text_generation', name: 'Génération de texte' },
        { id: 'image_generation', name: 'Génération d\'images' }
      ]);
      aiService.submitRequest.mockResolvedValue({
        id: 'req-123',
        status: 'submitted'
      });

      const AIInterface = (await import('../src/components/AI/AIInterface')).default;
      render(<AIInterface />, { wrapper });

      await waitFor(() => {
        expect(screen.getByText(/génération de texte/i)).toBeInTheDocument();
      });

      const modelSelect = screen.getByLabelText(/modèle/i);
      const promptInput = screen.getByLabelText(/prompt/i);
      const submitButton = screen.getByRole('button', { name: /soumettre/i });

      await userEvent.selectOptions(modelSelect, 'text_generation');
      await userEvent.type(promptInput, 'Générer un texte sur l\'IA décentralisée');
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(aiService.submitRequest).toHaveBeenCalledWith({
          model_type: 'text_generation',
          input_data: 'Générer un texte sur l\'IA décentralisée',
          parameters: expect.any(Object)
        });
      });
    });

    it('devrait afficher l\'historique des requêtes', async () => {
      const { aiService } = await import('../src/services/api');
      aiService.getRequests.mockResolvedValue([
        {
          id: 'req-1',
          model_type: 'text_generation',
          input_data: 'Premier prompt',
          status: 'completed',
          output_data: 'Réponse générée',
          created_at: '2024-01-01T10:00:00Z'
        }
      ]);

      const AIHistory = (await import('../src/components/AI/AIHistory')).default;
      render(<AIHistory />, { wrapper });

      await waitFor(() => {
        expect(screen.getByText('Premier prompt')).toBeInTheDocument();
        expect(screen.getByText('Réponse générée')).toBeInTheDocument();
        expect(screen.getByText(/completed/i)).toBeInTheDocument();
      });
    });
  });

  describe('Navigation', () => {
    it('devrait naviguer entre les pages', async () => {
      const { authService } = await import('../src/services/api');
      authService.isAuthenticated.mockReturnValue(true);

      const App = (await import('../src/App')).default;
      render(<App />, { wrapper });

      // Navigation vers les nœuds
      const nodesLink = screen.getByRole('link', { name: /nœuds/i });
      await userEvent.click(nodesLink);

      await waitFor(() => {
        expect(window.location.pathname).toBe('/nodes');
      });

      // Navigation vers l'IA
      const aiLink = screen.getByRole('link', { name: /ia/i });
      await userEvent.click(aiLink);

      await waitFor(() => {
        expect(window.location.pathname).toBe('/ai');
      });
    });

    it('devrait rediriger vers la connexion si non authentifié', async () => {
      const { authService } = await import('../src/services/api');
      authService.isAuthenticated.mockReturnValue(false);

      const App = (await import('../src/App')).default;
      render(<App />, { wrapper });

      // Tentative d'accès à une page protégée
      window.history.pushState({}, 'Test page', '/dashboard');

      await waitFor(() => {
        expect(window.location.pathname).toBe('/login');
      });
    });
  });

  describe('Responsive Design', () => {
    it('devrait s\'adapter aux petits écrans', async () => {
      // Mock de la taille d'écran mobile
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      });

      const App = (await import('../src/App')).default;
      render(<App />, { wrapper });

      // Vérifier que le menu mobile est présent
      const mobileMenu = screen.getByRole('button', { name: /menu/i });
      expect(mobileMenu).toBeInTheDocument();
    });
  });

  describe('Gestion des erreurs', () => {
    it('devrait afficher les erreurs de l\'API', async () => {
      const { nodeService } = await import('../src/services/api');
      nodeService.getNodes.mockRejectedValue(new Error('Erreur réseau'));

      const NodeList = (await import('../src/components/Nodes/NodeList')).default;
      render(<NodeList />, { wrapper });

      await waitFor(() => {
        expect(screen.getByText(/erreur lors du chargement/i)).toBeInTheDocument();
      });
    });

    it('devrait avoir un boundary d\'erreur fonctionnel', async () => {
      const ThrowError = () => {
        throw new Error('Test error');
      };

      const ErrorBoundary = (await import('../src/components/ErrorBoundary')).default;
      
      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>,
        { wrapper }
      );

      await waitFor(() => {
        expect(screen.getByText(/quelque chose s'est mal passé/i)).toBeInTheDocument();
      });
    });
  });

  describe('Performance', () => {
    it('devrait charger paresseusement les composants', async () => {
      // Test que les composants sont chargés à la demande
      const App = (await import('../src/App')).default;
      render(<App />, { wrapper });

      // Vérifier que seuls les composants nécessaires sont chargés
      expect(screen.queryByTestId('ai-interface')).not.toBeInTheDocument();
      
      // Navigation qui devrait déclencher le lazy loading
      const aiLink = screen.getByRole('link', { name: /ia/i });
      await userEvent.click(aiLink);

      await waitFor(() => {
        expect(screen.getByTestId('ai-interface')).toBeInTheDocument();
      });
    });
  });
});

// Tests d'intégration E2E (simulation)
describe('Tests d\'intégration', () => {
  it('devrait permettre un flux complet d\'authentification et utilisation', async () => {
    const { authService, nodeService, aiService } = await import('../src/services/api');
    
    // Mock des services
    authService.login.mockResolvedValue({ access_token: 'token' });
    authService.isAuthenticated.mockReturnValue(true);
    nodeService.getNodes.mockResolvedValue([]);
    aiService.getRequests.mockResolvedValue([]);

    const App = (await import('../src/App')).default;
    const { container } = render(<App />, { wrapper: createWrapper() });

    // 1. Connexion
    const usernameInput = screen.getByLabelText(/nom d'utilisateur/i);
    const passwordInput = screen.getByLabelText(/mot de passe/i);
    
    await userEvent.type(usernameInput, 'testuser');
    await userEvent.type(passwordInput, 'password123');
    await userEvent.click(screen.getByRole('button', { name: /connexion/i }));

    // 2. Accès au tableau de bord
    await waitFor(() => {
      expect(screen.getByText(/tableau de bord/i)).toBeInTheDocument();
    });

    // 3. Navigation vers les nœuds
    await userEvent.click(screen.getByRole('link', { name: /nœuds/i }));
    
    await waitFor(() => {
      expect(screen.getByText(/liste des nœuds/i)).toBeInTheDocument();
    });

    // Vérifier que tous les services ont été appelés
    expect(authService.login).toHaveBeenCalled();
    expect(nodeService.getNodes).toHaveBeenCalled();
  });
});