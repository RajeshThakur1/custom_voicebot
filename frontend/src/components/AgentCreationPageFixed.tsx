import React, { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Checkbox } from './ui/checkbox';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { ScrollArea } from './ui/scroll-area';
import { 
  ArrowLeft, 
  Upload, 
  FileText, 
  File, 
  Trash2, 
  Eye, 
  Send, 
  Mic, 
  MicOff,
  Volume2,
  Download,
  Image,
  Edit2,
  Check,
  X
} from 'lucide-react';
import { ImageWithFallback } from './figma/ImageWithFallback';
import { DocumentUploadModal } from './DocumentUploadModal';
import { DocumentPreviewModal } from './DocumentPreviewModal';
import { DeleteConfirmationDialog } from './DeleteConfirmationDialog';

interface Document {
  id: string;
  name: string;
  type: 'pdf' | 'docx' | 'txt' | 'image';
  size: string;
  uploadDate: string;
  selected: boolean;
}

interface Message {
  id: string;
  type: 'user' | 'agent';
  content: string;
  timestamp: string;
}

interface AgentCreationPageProps {
  agentId: string | null;
  onBack: () => void;
  onSave?: (agent: { id: string; name: string; model: string; documentsCount: number }) => void;
}

const mockDocuments: Document[] = [
  {
    id: 'doc-1',
    name: 'Annual Report 2023.pdf',
    type: 'pdf',
    size: '2.4 MB',
    uploadDate: '2 hours ago',
    selected: true
  },
  {
    id: 'doc-2',
    name: 'Product Specifications.docx',
    type: 'docx',
    size: '856 KB',
    uploadDate: '1 day ago',
    selected: true
  },
  {
    id: 'doc-3',
    name: 'Meeting Notes.txt',
    type: 'txt',
    size: '24 KB',
    uploadDate: '3 days ago',
    selected: false
  }
];

const mockMessages: Message[] = [
  {
    id: 'msg-1',
    type: 'user',
    content: 'What are the key findings from the annual report?',
    timestamp: '2:30 PM'
  },
  {
    id: 'msg-2',
    type: 'agent',
    content: 'Based on the annual report, here are the key findings: 1) Revenue grew by 15% year-over-year, 2) Customer satisfaction increased to 94%, and 3) We expanded into 3 new markets. The report also highlights our sustainability initiatives and cost optimization efforts.',
    timestamp: '2:31 PM'
  },
  {
    id: 'msg-3',
    type: 'user',
    content: 'Tell me more about the sustainability initiatives',
    timestamp: '2:32 PM'
  }
];

export function AgentCreationPage({ agentId, onBack, onSave }: AgentCreationPageProps) {
  const [agentName, setAgentName] = useState(agentId ? 'Legal Document Assistant' : 'Untitled Agent');
  const [selectedModel, setSelectedModel] = useState('gpt-4');
  const [isEditingName, setIsEditingName] = useState(false);
  const [originalAgentName, setOriginalAgentName] = useState(agentId ? 'Legal Document Assistant' : 'Untitled Agent');
  const [documents, setDocuments] = useState<Document[]>(mockDocuments);
  const [messages, setMessages] = useState<Message[]>(mockMessages);
  const [voiceMessages, setVoiceMessages] = useState<Message[]>([
    {
      id: 'voice-msg-1',
      type: 'agent',
      content: 'Hello! Welcome to Gautham Motors Customer Care. I\'m your assistant here to help you book service appointments, answer questions about our',
      timestamp: '2:28 PM'
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [previewDocument, setPreviewDocument] = useState<Document | null>(null);
  const [isPreviewModalOpen, setIsPreviewModalOpen] = useState(false);
  const [deleteDocument, setDeleteDocument] = useState<Document | null>(null);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);

  const generateAgentId = () => {
    return `agent_${Math.random().toString(36).substring(2, 11)}`;
  };

  const currentAgentId = agentId || generateAgentId();

  const toggleDocumentSelection = (docId: string) => {
    setDocuments(docs => 
      docs.map(doc => 
        doc.id === docId ? { ...doc, selected: !doc.selected } : doc
      )
    );
  };



  const handleDocumentUpload = (newDocument: Document) => {
    setDocuments(prev => [newDocument, ...prev]);
  };

  const openUploadModal = () => {
    setIsUploadModalOpen(true);
  };

  const closeUploadModal = () => {
    setIsUploadModalOpen(false);
  };

  const handlePreviewDocument = (document: Document) => {
    setPreviewDocument(document);
    setIsPreviewModalOpen(true);
  };

  const closePreviewModal = () => {
    setIsPreviewModalOpen(false);
    setPreviewDocument(null);
  };

  const handleDeleteDocument = (document: Document) => {
    setDeleteDocument(document);
    setIsDeleteDialogOpen(true);
  };

  const confirmDeleteDocument = () => {
    if (deleteDocument) {
      setDocuments(prev => prev.filter(doc => doc.id !== deleteDocument.id));
      setIsDeleteDialogOpen(false);
      setDeleteDocument(null);
    }
  };

  const closeDeleteDialog = () => {
    setIsDeleteDialogOpen(false);
    setDeleteDocument(null);
  };

  const handleNameEdit = () => {
    setOriginalAgentName(agentName);
    setIsEditingName(true);
  };

  const handleNameSave = () => {
    if (agentName.trim()) {
      setOriginalAgentName(agentName.trim());
      setAgentName(agentName.trim());
      setIsEditingName(false);
    }
  };

  const handleNameCancel = () => {
    setAgentName(originalAgentName);
    setIsEditingName(false);
  };

  const sendMessage = () => {
    if (!inputMessage.trim()) return;

    const newMessage: Message = {
      id: `msg-${Date.now()}`,
      type: 'user',
      content: inputMessage,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, newMessage]);
    setInputMessage('');

    // Simulate agent response
    setTimeout(() => {
      const agentResponse: Message = {
        id: `msg-${Date.now()}-agent`,
        type: 'agent',
        content: 'I understand your question. Let me analyze the selected documents to provide you with a comprehensive answer...',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, agentResponse]);
    }, 1000);
  };

  const toggleVoiceListening = () => {
    if (isListening) {
      // Stop listening and start processing/speaking
      setIsListening(false);
      setIsSpeaking(true);
      
      // Simulate processing user speech and agent response
      setTimeout(() => {
        const userMessage: Message = {
          id: `voice-msg-${Date.now()}`,
          type: 'user',
          content: 'What are the available service packages for my vehicle?',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        setVoiceMessages(prev => [...prev, userMessage]);
        
        // Agent response after processing
        setTimeout(() => {
          const agentResponse: Message = {
            id: `voice-msg-${Date.now()}-agent`,
            type: 'agent',
            content: 'We offer three main service packages: Basic Maintenance, Comprehensive Care, and Premium Plus. Each includes different levels of inspection, oil changes, and additional services. Would you like me to explain the details of each package?',
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          };
          setVoiceMessages(prev => [...prev, agentResponse]);
          setIsSpeaking(false);
        }, 2000);
      }, 1000);
    } else {
      // Start listening
      setIsListening(true);
    }
  };

  const endVoiceCall = () => {
    setIsListening(false);
    setIsSpeaking(false);
  };

  const handleSaveAgent = () => {
    if (onSave) {
      const agent = {
        id: currentAgentId,
        name: agentName,
        model: selectedModel,
        documentsCount: documents.length
      };
      onSave(agent);
    }
    onBack();
  };

  const getFileIcon = (type: string) => {
    switch (type) {
      case 'pdf':
        return <FileText className="w-4 h-4 text-red-500" />;
      case 'docx':
        return <File className="w-4 h-4 text-blue-500" />;
      case 'txt':
        return <FileText className="w-4 h-4 text-gray-500" />;
      case 'image':
        return <Image className="w-4 h-4 text-green-500" />;
      default:
        return <File className="w-4 h-4" />;
    }
  };

  const selectedDocsCount = documents.filter(doc => doc.selected).length;

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Fixed Header */}
      <header className="sticky top-0 z-50 border-b border-border bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60">
        <div className="px-4 sm:px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3 sm:gap-4">
              <Button variant="ghost" onClick={onBack} size="sm">
                <ArrowLeft className="w-4 h-4" />
              </Button>
              
              {/* Agent Info - Always visible, responsive layout */}
              <div className="flex items-center gap-2 sm:gap-4">
                <div className="text-sm">
                  <div className="flex items-center gap-2">
                    {isEditingName ? (
                      <div className="flex items-center gap-1">
                        <Input
                          value={agentName}
                          onChange={(e) => setAgentName(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') handleNameSave();
                            if (e.key === 'Escape') handleNameCancel();
                          }}
                          onBlur={handleNameSave}
                          className="h-6 text-sm font-medium w-32 sm:w-40"
                          autoFocus
                        />
                        <Button variant="ghost" size="sm" onClick={handleNameSave} className="h-6 w-6 p-0">
                          <Check className="w-3 h-3" />
                        </Button>
                        <Button variant="ghost" size="sm" onClick={handleNameCancel} className="h-6 w-6 p-0">
                          <X className="w-3 h-3" />
                        </Button>
                      </div>
                    ) : (
                      <div className="flex items-center gap-1 group cursor-pointer" onClick={handleNameEdit}>
                        <span className="font-medium">{agentName}</span>
                        <Edit2 className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                      </div>
                    )}
                  </div>
                  <div className="text-muted-foreground text-xs hidden sm:block">agent_1rn6sajv1</div>
                </div>
                <Badge variant="secondary" className="hidden sm:inline-flex">{selectedModel.toUpperCase()}</Badge>
                <Badge variant="secondary" className="sm:hidden text-xs">{selectedModel.toUpperCase()}</Badge>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <Select value={selectedModel} onValueChange={setSelectedModel}>
                <SelectTrigger className="w-20 sm:w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="gpt-4">GPT-4</SelectItem>
                  <SelectItem value="gpt-3.5">GPT-3.5</SelectItem>
                  <SelectItem value="claude-3">Claude-3</SelectItem>
                  <SelectItem value="gemini">Gemini</SelectItem>
                </SelectContent>
              </Select>
              
              <Button size="sm" className="hidden sm:flex" onClick={handleSaveAgent}>
                Save Agent
              </Button>
              <Button size="sm" className="sm:hidden px-3" onClick={handleSaveAgent}>
                Save
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex flex-col lg:flex-row min-h-0">
        {/* Left Panel - Knowledge Base */}
        <div className="w-full lg:w-1/2 border-b lg:border-b-0 lg:border-r border-border flex flex-col min-h-0">
          {/* Knowledge Base Header - Fixed */}
          <div className="sticky top-[73px] z-40 bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60 border-b border-border">
            <div className="p-4 sm:p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg sm:text-xl font-bold">Knowledge Base</h2>
                  <p className="text-sm text-muted-foreground">
                    {selectedDocsCount} of {documents.length} documents selected
                  </p>
                </div>
                <Button onClick={openUploadModal} size="sm" className="sm:size-default">
                  <Upload className="w-4 h-4 mr-2" />
                  <span className="hidden sm:inline">Add Documents</span>
                  <span className="sm:hidden">Add</span>
                </Button>
              </div>
            </div>
          </div>

          {/* Documents List - Scrollable */}
          <div className="flex-1 overflow-y-auto">
            <div className="p-4 sm:p-6">
              {documents.length === 0 ? (
                <div className="text-center py-8 sm:py-12">
                  <ImageWithFallback
                    src="https://images.unsplash.com/photo-1616861771635-49063a4636ed?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHxtb2Rlcm4lMjB3b3Jrc3BhY2UlMjBkb2N1bWVudHMlMjBmaWxlc3xlbnwxfHx8fDE3NTg5NTA2MzJ8MA&ixlib=rb-4.1.0&q=80&w=1080"
                    alt="Upload documents"
                    className="w-32 sm:w-48 h-20 sm:h-32 object-cover rounded-lg mx-auto mb-4 opacity-60"
                  />
                  <h3 className="font-medium mb-2">No documents uploaded</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    Upload PDFs, Word docs, images or text files to get started
                  </p>
                  <Button onClick={openUploadModal} size="sm">
                    <Upload className="w-4 h-4 mr-2" />
                    Upload Documents
                  </Button>
                </div>
              ) : (
                <div className="space-y-3">
                  {documents.map((doc) => (
                    <Card key={doc.id} className="p-3 sm:p-4">
                      <div className="flex items-start gap-3">
                        <Checkbox
                          checked={doc.selected}
                          onCheckedChange={() => toggleDocumentSelection(doc.id)}
                          className="mt-1"
                        />
                        
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            {getFileIcon(doc.type)}
                            <span className="font-medium text-sm truncate">{doc.name}</span>
                          </div>
                          <div className="flex items-center gap-2 sm:gap-4 text-xs text-muted-foreground">
                            <span>{doc.size}</span>
                            <span className="hidden sm:inline">•</span>
                            <span>{doc.uploadDate}</span>
                          </div>
                        </div>

                        <div className="flex items-center gap-1">
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            className="h-8 w-8 p-0"
                            onClick={() => handlePreviewDocument(doc)}
                          >
                            <Eye className="w-4 h-4" />
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            className="h-8 w-8 p-0 text-destructive hover:text-destructive"
                            onClick={() => handleDeleteDocument(doc)}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Panel - Agent Interaction */}
        <div className="w-full lg:w-1/2 flex flex-col min-h-0">
          {/* Agent Interaction Header - Fixed, same height as Knowledge Base header */}
          <div className="sticky top-[73px] z-40 bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60 border-b border-border">
            <div className="p-4 sm:p-6">
              <h2 className="text-lg sm:text-xl font-bold">Agent Interaction</h2>
              <p className="text-sm text-muted-foreground">
                Test your agent with chat or voice
              </p>
            </div>
          </div>

          <Tabs defaultValue="chat" className="flex-1 flex flex-col min-h-0">
            <div className="px-4 sm:px-6 pt-4 border-b border-border">
              <TabsList className="w-fit">
                <TabsTrigger value="chat">Chat</TabsTrigger>
                <TabsTrigger value="voice">Voice</TabsTrigger>
              </TabsList>
            </div>

            <TabsContent value="chat" className="flex-1 flex flex-col mt-0 min-h-0">
              {/* Chat Messages - Scrollable */}
              <div className="flex-1 overflow-y-auto">
                <div className="p-4 sm:p-6 space-y-4">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[80%] rounded-lg p-3 ${
                          message.type === 'user'
                            ? 'bg-primary text-primary-foreground'
                            : 'bg-muted'
                        }`}
                      >
                        <p className="text-sm">{message.content}</p>
                        <p className="text-xs opacity-70 mt-1">{message.timestamp}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Chat Input - Fixed at bottom */}
              <div className="border-t border-border bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60">
                <div className="p-4 sm:p-6">
                  {selectedDocsCount === 0 && (
                    <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                      <p className="text-sm text-yellow-800">
                        Select at least one document to enable chat functionality.
                      </p>
                    </div>
                  )}
                  <div className="flex gap-2">
                    <Input
                      placeholder="Ask your agent anything..."
                      value={inputMessage}
                      onChange={(e) => setInputMessage(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                      disabled={selectedDocsCount === 0}
                    />
                    <Button 
                      onClick={sendMessage} 
                      disabled={!inputMessage.trim() || selectedDocsCount === 0}
                      size="sm"
                      className="px-3"
                    >
                      <Send className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="voice" className="flex-1 flex flex-col mt-0">
              {selectedDocsCount === 0 ? (
                <div className="flex-1 flex flex-col items-center justify-center p-12">
                  <div className="text-center space-y-4">
                    <div className="w-24 h-24 bg-muted rounded-full flex items-center justify-center mx-auto">
                      <MicOff className="w-8 h-8 text-muted-foreground" />
                    </div>
                    <h3 className="font-medium">Voice interaction disabled</h3>
                    <p className="text-sm text-muted-foreground max-w-md">
                      Select at least one document from your knowledge base to enable voice chat.
                    </p>
                  </div>
                </div>
              ) : (
                <>
                  {/* Voice Chat Transcript */}
                  <ScrollArea className="flex-1 p-6">
                    <div className="space-y-4">
                      {voiceMessages.map((message) => (
                        <div
                          key={message.id}
                          className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                          <div
                            className={`max-w-[80%] rounded-lg p-3 ${
                              message.type === 'user'
                                ? 'bg-primary text-primary-foreground'
                                : 'bg-muted'
                            }`}
                          >
                            <p className="text-sm">{message.content}</p>
                            <p className="text-xs opacity-70 mt-1">{message.timestamp}</p>
                          </div>
                        </div>
                      ))}
                      
                      {/* Live transcript indicator */}
                      {isListening && (
                        <div className="flex justify-end">
                          <div className="max-w-[80%] rounded-lg p-3 bg-primary/10 border border-primary/20">
                            <p className="text-sm text-muted-foreground italic">
                              Listening... speak now
                            </p>
                          </div>
                        </div>
                      )}
                      
                      {isSpeaking && (
                        <div className="flex justify-start">
                          <div className="max-w-[80%] rounded-lg p-3 bg-muted border">
                            <div className="flex items-center gap-2 text-sm text-muted-foreground">
                              <Volume2 className="w-3 h-3" />
                              <span className="italic">Agent is speaking...</span>
                              <div className="flex gap-1 ml-2">
                                <div className="w-1 h-1 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                                <div className="w-1 h-1 bg-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                                <div className="w-1 h-1 bg-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                              </div>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </ScrollArea>

                  {/* Voice Controls at Bottom */}
                  <div className="p-6 border-t border-border">
                    <div className="flex flex-col items-center space-y-4">
                      {/* Voice Status Text */}
                      <div className="text-center">
                        <h3 className="font-medium text-sm">
                          {isListening ? 'Listening...' : isSpeaking ? 'Agent Speaking...' : 'Test your agent'}
                        </h3>
                        <p className="text-xs text-muted-foreground mt-1">
                          {isListening 
                            ? 'Speak clearly into your microphone'
                            : isSpeaking
                            ? 'Agent is responding to your query'
                            : 'Tap the microphone to start voice conversation'
                          }
                        </p>
                      </div>

                      {/* Voice Button */}
                      <div className="relative">
                        <Button
                          size="lg"
                          className={`w-16 h-16 rounded-full transition-all ${
                            isListening 
                              ? 'bg-red-500 hover:bg-red-600' 
                              : isSpeaking
                              ? 'bg-blue-500 hover:bg-blue-600'
                              : 'bg-primary hover:bg-primary/90'
                          }`}
                          onClick={toggleVoiceListening}
                          disabled={isSpeaking}
                        >
                          {isListening ? (
                            <MicOff className="w-6 h-6" />
                          ) : isSpeaking ? (
                            <Volume2 className="w-6 h-6" />
                          ) : (
                            <Mic className="w-6 h-6" />
                          )}
                        </Button>
                        
                        {/* Animated ring for listening state */}
                        {isListening && (
                          <div className="absolute inset-0 rounded-full border-4 border-red-500 animate-ping" />
                        )}
                        
                        {/* Animated ring for speaking state */}
                        {isSpeaking && (
                          <div className="absolute inset-0 rounded-full border-4 border-blue-500 animate-pulse" />
                        )}
                      </div>

                      {/* End Call Button */}
                      {(isListening || isSpeaking || voiceMessages.length > 1) && (
                        <Button 
                          variant="outline" 
                          onClick={endVoiceCall}
                          className="text-red-500 border-red-500 hover:bg-red-50"
                        >
                          End the Call
                        </Button>
                      )}
                    </div>
                  </div>
                </>
              )}
            </TabsContent>
          </Tabs>
        </div>
      </div>

      {/* Document Upload Modal */}
      <DocumentUploadModal
        isOpen={isUploadModalOpen}
        onClose={closeUploadModal}
        onUpload={handleDocumentUpload}
      />

      {/* Document Preview Modal */}
      <DocumentPreviewModal
        document={previewDocument}
        isOpen={isPreviewModalOpen}
        onClose={closePreviewModal}
      />

      {/* Delete Confirmation Dialog */}
      <DeleteConfirmationDialog
        isOpen={isDeleteDialogOpen}
        onClose={closeDeleteDialog}
        onConfirm={confirmDeleteDocument}
        documentName={deleteDocument?.name || ''}
      />
    </div>
  );
}