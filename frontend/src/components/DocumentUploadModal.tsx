import React, { useState, useRef, DragEvent } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Progress } from './ui/progress';
import { Upload, FileText, File, X, Image } from 'lucide-react';
import { APIService } from '../services/api';

export interface Document {
  id: string;
  name: string;
  type: 'pdf' | 'docx' | 'txt' | 'image';
  size: string;
  uploadDate: string;
  selected: boolean;
}

interface DocumentUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUpload: (document: Document) => void;
}

export function DocumentUploadModal({ isOpen, onClose, onUpload }: DocumentUploadModalProps) {
  const [documentName, setDocumentName] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const acceptedTypes = {
    'application/pdf': 'pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
    'application/msword': 'docx',
    'text/plain': 'txt',
    'image/jpeg': 'image',
    'image/jpg': 'image',
    'image/png': 'image',
    'image/gif': 'image',
    'image/webp': 'image',
    'image/svg+xml': 'image'
  };

  const getFileType = (file: File): 'pdf' | 'docx' | 'txt' | 'image' | null => {
    const type = acceptedTypes[file.type as keyof typeof acceptedTypes];
    return (type as 'pdf' | 'docx' | 'txt' | 'image') || null;
  };

  const getFileIcon = (file: File) => {
    const type = getFileType(file);
    switch (type) {
      case 'pdf':
        return <FileText className="w-6 h-6 text-red-500" />;
      case 'docx':
        return <File className="w-6 h-6 text-blue-500" />;
      case 'txt':
        return <FileText className="w-6 h-6 text-gray-500" />;
      case 'image':
        return <Image className="w-6 h-6 text-green-500" />;
      default:
        return <File className="w-6 h-6 text-gray-400" />;
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleFileSelect = (file: File) => {
    const fileType = getFileType(file);
    if (!fileType) {
      alert('Please select a valid file (PDF, DOCX, TXT, or Image).');
      return;
    }

    setSelectedFile(file);
    if (!documentName) {
      // Auto-fill document name from filename (without extension)
      const nameWithoutExt = file.name.replace(/\.[^/.]+$/, '');
      setDocumentName(nameWithoutExt);
    }
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(false);

    const files = Array.from<File>(e.dataTransfer.files as FileList);
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    if (!documentName.trim()) {
      alert('Please enter a document name');
      return;
    }

    try {
      setIsUploading(true);
      setUploadProgress(0);

      const response = await APIService.uploadPdf(selectedFile,documentName, (percent) => {
        setUploadProgress(percent);
      });

      const fileType = getFileType(selectedFile)!;
      const newDocument: Document = {
        id: String(response.id ?? `doc-${Date.now()}`),
        name: String(response.name ?? documentName.trim()),
        type: fileType,
        size: formatFileSize(selectedFile.size),
        uploadDate: 'Just now',
        selected: true,
      };

      onUpload(newDocument);
      handleClose();
    } catch (err) {
      console.error(err);
      alert('Failed to upload document. Please try again.');
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const handleClose = () => {
    setDocumentName('');
    setSelectedFile(null);
    setIsDragOver(false);
    setIsUploading(false);
    setUploadProgress(0);
    onClose();
  };

  const removeSelectedFile = () => {
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-md max-h-[85vh] flex flex-col">
        <DialogHeader className="flex-shrink-0">
          <DialogTitle>Add Document</DialogTitle>
          <DialogDescription>
            Upload a document or image to your knowledge base. Supported formats: PDF, DOCX, TXT, JPG, PNG, GIF, WebP, SVG.
          </DialogDescription>
        </DialogHeader>

        <div className="flex-1 overflow-y-auto space-y-4 pr-1">
          {/* Document Name Field */}
          <div className="space-y-2">
            <Label htmlFor="document-name">
              Document Name <span className="text-destructive">*</span>
            </Label>
            <Input
              id="document-name"
              placeholder="Enter document name..."
              value={documentName}
              onChange={(e) => setDocumentName(e.target.value)}
              disabled={isUploading}
              required
            />
            {!documentName.trim() && selectedFile && (
              <p className="text-sm text-destructive">Document name is required</p>
            )}
          </div>

          {/* File Upload Area */}
          <div className="space-y-4">
            <Label>Upload File</Label>
            
            {!selectedFile ? (
              <div
                className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors cursor-pointer ${
                  isDragOver
                    ? 'border-primary bg-primary/5'
                    : 'border-border hover:border-primary/50 hover:bg-muted/50'
                }`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
              >
                <Upload className="w-8 h-8 text-muted-foreground mx-auto mb-3" />
                <div className="space-y-2">
                  <p className="font-medium text-sm">
                    {isDragOver ? 'Drop your file here' : 'Drag & drop your file here'}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    or <span className="text-primary underline">click to browse</span>
                  </p>
                  <p className="text-xs text-muted-foreground">
                    PDF, DOCX, TXT, JPG, PNG, GIF, WebP, SVG
                  </p>
                </div>
              </div>
            ) : (
              <div className="border border-border rounded-lg p-3">
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 mt-0.5">
                    {getFileIcon(selectedFile)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-sm truncate">{selectedFile.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {formatFileSize(selectedFile.size)}
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={removeSelectedFile}
                    disabled={isUploading}
                    className="flex-shrink-0 h-8 w-8 p-0"
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            )}

            {/* Hidden file input */}
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.docx,.doc,.txt,.jpg,.jpeg,.png,.gif,.webp,.svg"
              onChange={handleFileInputChange}
              className="hidden"
            />
          </div>

          {/* Upload Progress */}
          {isUploading && (
            <div className="space-y-2 bg-muted/30 p-3 rounded-lg">
              <div className="flex items-center justify-between text-sm">
                <span>Uploading...</span>
                <span>{uploadProgress}%</span>
              </div>
              <Progress value={uploadProgress} className="h-2" />
            </div>
          )}
        </div>

        {/* Actions - Fixed Footer */}
        <div className="flex-shrink-0 flex justify-end gap-3 pt-4 border-t border-border">
          <Button variant="outline" onClick={handleClose} disabled={isUploading}>
            Cancel
          </Button>
          <Button
            onClick={handleUpload}
            disabled={!selectedFile || !documentName.trim() || isUploading}
          >
            {isUploading ? 'Uploading...' : 'Upload Document'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}