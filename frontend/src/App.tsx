import React, { useState } from 'react';
import { LandingPage } from './components/LandingPage';
import { LoginPage } from './components/LoginPage';
import { Dashboard } from './components/Dashboard';
import { AgentCreationPage } from './components/AgentCreationPage';

type Page = 'landing' | 'login' | 'dashboard' | 'create-agent';

interface Agent {
  id: string;
  name: string;
  model: string;
  documentsCount: number;
}

export default function App() {
  const [currentPage, setCurrentPage] = useState<Page>('landing');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null);
  const [savedAgents, setSavedAgents] = useState<Agent[]>([]);

  const navigateTo = (page: Page) => {
    setCurrentPage(page);
  };

  const login = () => {
    setIsLoggedIn(true);
    setCurrentPage('dashboard');
  };

  const logout = () => {
    setIsLoggedIn(false);
    setCurrentPage('landing');
  };

  const createAgent = () => {
    setSelectedAgentId(null);
    setCurrentPage('create-agent');
  };

  const editAgent = (agentId: string) => {
    setSelectedAgentId(agentId);
    setCurrentPage('create-agent');
  };

  const saveAgent = (agent: Agent) => {
    setSavedAgents(prev => {
      const existingIndex = prev.findIndex(a => a.id === agent.id);
      if (existingIndex >= 0) {
        // Update existing agent
        const updated = [...prev];
        updated[existingIndex] = agent;
        return updated;
      } else {
        // Add new agent
        return [...prev, agent];
      }
    });
  };

  switch (currentPage) {
    case 'landing':
      return <LandingPage onNavigateToLogin={() => navigateTo('login')} onGetStarted={() => navigateTo('login')} />;
    case 'login':
      return <LoginPage onLogin={login} onBack={() => navigateTo('landing')} />;
    case 'dashboard':
      return (
        <Dashboard
          onCreateAgent={createAgent}
          onEditAgent={editAgent}
          onLogout={logout}
          savedAgents={savedAgents}
        />
      );
    case 'create-agent':
      return (
        <AgentCreationPage
          agentId={selectedAgentId}
          onBack={() => navigateTo('dashboard')}
          onSave={saveAgent}
        />
      );
    default:
      return <LandingPage onNavigateToLogin={() => navigateTo('login')} onGetStarted={() => navigateTo('login')} />;
  }
}