import React from 'react';
import { Button } from './ui/button';
import { ImageWithFallback } from './figma/ImageWithFallback';

interface LandingPageProps {
  onNavigateToLogin: () => void;
  onGetStarted: () => void;
}

export function LandingPage({ onNavigateToLogin, onGetStarted }: LandingPageProps) {
  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="flex items-center justify-between px-4 sm:px-6 py-4 border-b border-border">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
            <span className="text-primary-foreground font-bold">AI</span>
          </div>
          <span className="font-medium">DocChat</span>
        </div>
        <div className="flex items-center gap-2 sm:gap-4">
          <Button variant="ghost" onClick={onNavigateToLogin} size="sm" className="sm:size-default">
            Login
          </Button>
          <Button onClick={onGetStarted} size="sm" className="sm:size-default">
            <span className="hidden sm:inline">Get Started</span>
            <span className="sm:hidden">Start</span>
          </Button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="px-4 sm:px-6 py-12 sm:py-20 max-w-7xl mx-auto">
        <div className="grid lg:grid-cols-2 gap-8 lg:gap-16 items-center">
          <div className="space-y-6 sm:space-y-8">
            <div className="space-y-4">
              <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold leading-tight">
                Create Conversational AI Agents for Your Documents in Minutes
              </h1>
              <p className="text-lg sm:text-xl text-muted-foreground">
                Upload your files, select a model, and instantly chat or talk with your data. 
                Transform static documents into interactive conversations.
              </p>
            </div>
            
            <div className="flex flex-col sm:flex-row items-center gap-3 sm:gap-4">
              <Button size="lg" onClick={onGetStarted} className="w-full sm:w-auto px-6 sm:px-8">
                Get Started Free
              </Button>
              <Button variant="outline" size="lg" className="w-full sm:w-auto">
                Watch Demo
              </Button>
            </div>
          </div>

          <div className="relative mt-8 lg:mt-0">
            <ImageWithFallback
              src="https://images.unsplash.com/photo-1725798451557-fc60db3eb6a2?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxhaSUyMGNvbnZlcnNhdGlvbiUyMGNoYXQlMjBpbnRlcmZhY2UlMjBwZW9wbGUlMjB0YWxraW5nfGVufDF8fHx8MTc1ODk1MDYzMHww&ixlib=rb-4.1.0&q=80&w=1080"
              alt="AI conversation interface"
              className="w-full h-[250px] sm:h-[350px] lg:h-[400px] object-cover rounded-2xl shadow-2xl"
            />
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="px-4 sm:px-6 py-12 sm:py-20 bg-muted/30">
        <div className="max-w-6xl mx-auto">
          <div className="text-center space-y-4 mb-12 sm:mb-16">
            <h2 className="text-2xl sm:text-3xl font-bold">How It Works</h2>
            <p className="text-lg sm:text-xl text-muted-foreground">
              Get your AI agent up and running in three simple steps
            </p>
          </div>

          <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-8 sm:gap-12">
            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-primary rounded-full flex items-center justify-center mx-auto text-primary-foreground font-bold text-xl">
                1
              </div>
              <h3 className="text-xl font-bold">Upload Documents</h3>
              <p className="text-muted-foreground">
                Upload your PDFs, Word docs, or text files. We support all major document formats.
              </p>
            </div>

            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-primary rounded-full flex items-center justify-center mx-auto text-primary-foreground font-bold text-xl">
                2
              </div>
              <h3 className="text-xl font-bold">Choose Your Model</h3>
              <p className="text-muted-foreground">
                Select from powerful AI models including GPT-4, Claude, and more to power your agent.
              </p>
            </div>

            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-primary rounded-full flex items-center justify-center mx-auto text-primary-foreground font-bold text-xl">
                3
              </div>
              <h3 className="text-xl font-bold">Chat or Talk</h3>
              <p className="text-muted-foreground">
                Start conversing with your documents through text chat or voice interaction.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="px-6 py-12 border-t border-border">
        <div className="max-w-6xl mx-auto text-center">
          <div className="flex items-center justify-center gap-2 mb-4">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <span className="text-primary-foreground font-bold">AI</span>
            </div>
            <span className="font-medium">DocChat</span>
          </div>
          <p className="text-muted-foreground">
            Transform your documents into conversational AI experiences
          </p>
        </div>
      </footer>
    </div>
  );
}