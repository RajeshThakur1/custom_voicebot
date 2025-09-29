import React, { useState } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Avatar, AvatarFallback } from './ui/avatar';
import { Badge } from './ui/badge';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from './ui/dropdown-menu';
import { ImageWithFallback } from './figma/ImageWithFallback';
import { Plus, MoreVertical, MessageSquare, Mic, Calendar, Settings, LogOut, Bot } from 'lucide-react';

interface Agent {
  id: string;
  name: string;
  description?: string;
  documentsCount: number;
  lastAccessed?: string;
  model: string;
  status?: 'active' | 'inactive';
}

interface DashboardProps {
  onCreateAgent: () => void;
  onEditAgent: (agentId: string) => void;
  onLogout: () => void;
  savedAgents?: Agent[];
}

const mockAgents: Agent[] = [
  {
    id: 'agent-1',
    name: 'Legal Document Assistant',
    description: 'Helps analyze contracts and legal documents',
    documentsCount: 12,
    lastAccessed: '2 hours ago',
    model: 'GPT-4',
    status: 'active'
  },
  {
    id: 'agent-2',
    name: 'Research Paper Helper',
    description: 'Academic research and citation assistant',
    documentsCount: 8,
    lastAccessed: '1 day ago',
    model: 'Claude-3',
    status: 'active'
  },
  {
    id: 'agent-3',
    name: 'Company Handbook Bot',
    description: 'HR policies and procedures guide',
    documentsCount: 25,
    lastAccessed: '3 days ago',
    model: 'GPT-3.5',
    status: 'inactive'
  }
];

export function Dashboard({ onCreateAgent, onEditAgent, onLogout, savedAgents = [] }: DashboardProps) {
  // Combine mock agents with saved agents, transforming saved agents to match interface
  const transformedSavedAgents: Agent[] = savedAgents.map(agent => ({
    ...agent,
    description: `Custom agent with ${agent.documentsCount} documents`,
    lastAccessed: 'Just now',
    status: 'active' as const
  }));
  
  const [agents] = useState<Agent[]>([...transformedSavedAgents, ...mockAgents]);

  const EmptyState = () => (
    <div className="text-center py-16">
      <ImageWithFallback
        src="https://images.unsplash.com/photo-1597004475902-3f8c38279a4f?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxlbXB0eSUyMHN0YXRlJTIwaWxsdXN0cmF0aW9uJTIwbWluaW1hbHxlbnwxfHx8fDE3NTg5NTA2MzV8MA&ixlib=rb-4.1.0&q=80&w=1080"
        alt="Create your first agent"
        className="w-64 h-64 object-cover rounded-lg mx-auto mb-8 opacity-60"
      />
      <h3 className="text-2xl font-bold mb-4">Create Your First AI Agent</h3>
      <p className="text-muted-foreground mb-8 max-w-md mx-auto">
        Upload your documents and start building conversational AI agents that understand your content.
      </p>
      <Button onClick={onCreateAgent} size="lg" className="px-8">
        <Plus className="w-4 h-4 mr-2" />
        Create Agent
      </Button>
    </div>
  );

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border">
        <div className="flex items-center justify-between px-4 sm:px-6 py-4">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <span className="text-primary-foreground font-bold">AI</span>
              </div>
              <span className="font-medium">DocChat</span>
            </div>
          </div>

          <div className="flex items-center gap-2 sm:gap-4">
            {agents.length > 0 && (
              <Button onClick={onCreateAgent} size="sm" className="sm:size-default">
                <Plus className="w-4 h-4 mr-2" />
                <span className="hidden sm:inline">Create Agent</span>
                <span className="sm:hidden">Create</span>
              </Button>
            )}
            
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm" className="gap-1 sm:gap-2">
                  <Avatar className="w-6 sm:w-8 h-6 sm:h-8">
                    <AvatarFallback>JD</AvatarFallback>
                  </Avatar>
                  <span className="hidden sm:inline">John Doe</span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuItem>
                  <Settings className="w-4 h-4 mr-2" />
                  Settings
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={onLogout}>
                  <LogOut className="w-4 h-4 mr-2" />
                  Log out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="px-4 sm:px-6 py-6 sm:py-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-6 sm:mb-8">
            <h1 className="text-2xl sm:text-3xl font-bold mb-2">Your AI Agents</h1>
            <p className="text-muted-foreground">
              Manage and interact with your document-powered AI agents
            </p>
          </div>

          {agents.length === 0 ? (
            <EmptyState />
          ) : (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {agents.map((agent) => (
                <Card key={agent.id} className="hover:shadow-lg transition-shadow cursor-pointer group">
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                          <Bot className="w-5 h-5 text-primary" />
                        </div>
                        <div>
                          <CardTitle className="text-lg">{agent.name}</CardTitle>
                          <div className="flex items-center gap-2 mt-1">
                            <Badge variant={agent.status === 'active' ? 'default' : 'secondary'} className="text-xs">
                              {agent.status}
                            </Badge>
                            <Badge variant="outline" className="text-xs">
                              {agent.model}
                            </Badge>
                          </div>
                        </div>
                      </div>
                      
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm" className="opacity-0 group-hover:opacity-100 transition-opacity">
                            <MoreVertical className="w-4 h-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => onEditAgent(agent.id)}>
                            Edit Agent
                          </DropdownMenuItem>
                          <DropdownMenuItem>
                            Duplicate
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem className="text-destructive">
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </CardHeader>
                  
                  <CardContent className="space-y-4">
                    {agent.description && (
                      <CardDescription>{agent.description}</CardDescription>
                    )}
                    
                    <div className="flex items-center justify-between text-sm text-muted-foreground">
                      <span>{agent.documentsCount} documents</span>
                      <div className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {agent.lastAccessed}
                      </div>
                    </div>
                    
                    <div className="flex gap-2 pt-2">
                      <Button
                        variant="outline"
                        size="sm"
                        className="flex-1"
                        onClick={() => onEditAgent(agent.id)}
                      >
                        <MessageSquare className="w-3 h-3 mr-1" />
                        Chat
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        className="flex-1"
                        onClick={() => onEditAgent(agent.id)}
                      >
                        <Mic className="w-3 h-3 mr-1" />
                        Voice
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}