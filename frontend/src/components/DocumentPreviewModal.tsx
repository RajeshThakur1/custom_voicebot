import React from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog';
import { Button } from './ui/button';
import { ScrollArea } from './ui/scroll-area';
import { FileText, File, Image as ImageIcon, Download } from 'lucide-react';
import { ImageWithFallback } from './figma/ImageWithFallback';

interface Document {
  id: string;
  name: string;
  type: 'pdf' | 'docx' | 'txt' | 'image';
  size: string;
  uploadDate: string;
  selected: boolean;
}

interface DocumentPreviewModalProps {
  document: Document | null;
  isOpen: boolean;
  onClose: () => void;
}

export function DocumentPreviewModal({ document, isOpen, onClose }: DocumentPreviewModalProps) {
  if (!document) return null;

  const getDocumentIcon = () => {
    switch (document.type) {
      case 'pdf':
        return <FileText className="w-8 h-8 text-red-500" />;
      case 'docx':
        return <File className="w-8 h-8 text-blue-500" />;
      case 'txt':
        return <FileText className="w-8 h-8 text-gray-500" />;
      case 'image':
        return <ImageIcon className="w-8 h-8 text-green-500" />;
      default:
        return <File className="w-8 h-8 text-gray-400" />;
    }
  };

  const renderPreviewContent = () => {
    switch (document.type) {
      case 'image':
        return (
          <div className="flex items-center justify-center min-h-[600px] bg-muted/20 rounded-lg">
            <ImageWithFallback
              src="https://images.unsplash.com/photo-1568667256549-094345857637?w=600&h=400&fit=crop"
              alt={document.name}
              className="max-w-full max-h-[600px] object-contain rounded-lg"
            />
          </div>
        );
      case 'pdf':
        return (
          <div className="min-h-[600px] bg-muted/20 rounded-lg p-8 flex flex-col items-center justify-center text-center">
            <FileText className="w-16 h-16 text-red-500 mb-4" />
            <h3 className="mb-2">PDF Document</h3>
            <p className="text-muted-foreground text-sm mb-4">
              PDF preview is not available in this demo environment.
            </p>
            <p className="text-muted-foreground text-sm">
              In a real application, you would see the PDF content here or be able to download it.
            </p>
          </div>
        );
      case 'docx':
        return (
          <div className="min-h-[600px] bg-muted/20 rounded-lg p-8">
            <div className="space-y-4">
              <div className="flex items-center gap-3 mb-6">
                <File className="w-8 h-8 text-blue-500" />
                <div>
                  <h3>Document Preview</h3>
                  <p className="text-sm text-muted-foreground">DOCX Document</p>
                </div>
              </div>
              <div className="space-y-4 text-sm">
                <p><strong>Executive Summary</strong></p>
                <p>This document contains important business information and strategic insights that have been uploaded to the knowledge base.</p>
                <p><strong>Key Highlights:</strong></p>
                <ul className="list-disc pl-6 space-y-1">
                  <li>Revenue growth of 15% year-over-year</li>
                  <li>Customer satisfaction increased to 94%</li>
                  <li>New sustainability initiatives launched</li>
                  <li>Market expansion into 3 new regions</li>
                </ul>
                <p className="text-muted-foreground">
                  Note: This is a preview of the document content. Full document processing would be available in the complete application.
                </p>
              </div>
            </div>
          </div>
        );
      case 'txt':
        return (
          <div className="min-h-[600px] bg-muted/20 rounded-lg p-6">
            <div className="space-y-4">
              <div className="flex items-center gap-3 mb-6">
                <FileText className="w-8 h-8 text-gray-500" />
                <div>
                  <h3>Text Document</h3>
                  <p className="text-sm text-muted-foreground">Plain Text File</p>
                </div>
              </div>
              <div className="font-mono text-sm bg-background p-4 rounded border space-y-2">
                <p>Meeting Notes - Q4 Planning Session</p>
                <p>Date: December 15, 2024</p>
                <p>Attendees: Product Team, Engineering, Marketing</p>
                <p></p>
                <p>Agenda:</p>
                <p>1. Review Q3 performance metrics</p>
                <p>2. Discuss Q4 product roadmap</p>
                <p>3. Resource allocation planning</p>
                <p>4. Risk assessment and mitigation</p>
                <p></p>
                <p>Action Items:</p>
                <p>- Finalize feature specifications by Dec 20</p>
                <p>- Schedule design review sessions</p>
                <p>- Update project timelines</p>
                <p></p>
                <p className="text-muted-foreground">
                  [This is sample content for demonstration purposes]
                </p>
              </div>
            </div>
          </div>
        );
      default:
        return (
          <div className="min-h-[600px] bg-muted/20 rounded-lg flex items-center justify-center">
            <p className="text-muted-foreground">Preview not available for this file type.</p>
          </div>
        );
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-6xl max-h-[95vh] w-[95vw] flex flex-col">
        <DialogHeader className="flex-shrink-0">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {getDocumentIcon()}
              <div>
                <DialogTitle className="text-left">{document.name}</DialogTitle>
                <DialogDescription className="text-left">
                  {document.size} • {document.uploadDate}
                </DialogDescription>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm">
                <Download className="w-4 h-4 mr-2" />
                Download
              </Button>
            </div>
          </div>
        </DialogHeader>

        <ScrollArea className="flex-1 mt-6">
          {renderPreviewContent()}
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
}