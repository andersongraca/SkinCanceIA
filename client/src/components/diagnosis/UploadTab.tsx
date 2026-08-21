import React, { useRef, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { AlertCircle, CheckCircle, Upload as UploadIcon, X, Loader2 } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { trpc } from '@/lib/trpc';
import type { ClassificationResponse } from './types';

interface UploadTabProps {
  onImageSelected: (file: File) => void;
  onClassificationStart: () => void;
  onClassificationComplete: (response: ClassificationResponse) => void;
  onClassificationError: (error: string) => void;
  isProcessing: boolean;
  statusMessage: string;
  progress: number;
  selectedImage: File | null;
  imagePreview: string | null;
  onClearImage: () => void;
}

function fileToDataUrl(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result));
    reader.onerror = () => reject(new Error('Não foi possível ler o arquivo selecionado.'));
    reader.readAsDataURL(file);
  });
}

function formatClassificationError(error: unknown): string {
  const message = error instanceof Error ? error.message : String(error);
  if (/failed to fetch|fetch failed|networkerror/i.test(message)) {
    return 'Não foi possível conectar ao backend local. Inicie o MariaDB e o servidor em http://localhost:3000 e tente novamente.';
  }
  return message || 'Erro ao classificar imagem.';
}

export default function UploadTab({
  onImageSelected,
  onClassificationStart,
  onClassificationComplete,
  onClassificationError,
  isProcessing,
  statusMessage,
  progress,
  selectedImage,
  imagePreview,
  onClearImage,
}: UploadTabProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [validationError, setValidationError] = useState<string | null>(null);
  const uploadMutation = trpc.diagnosis.uploadImage.useMutation();
  const classifyMutation = trpc.diagnosis.classifyStoredImage.useMutation();

  const MAX_FILE_SIZE = 10 * 1024 * 1024;
  const ALLOWED_FORMATS = ['image/jpeg', 'image/png'] as const;
  const ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png'];

  const validateImageFile = (file: File): { isValid: boolean; error?: string } => {
    if (!ALLOWED_FORMATS.includes(file.type as (typeof ALLOWED_FORMATS)[number])) {
      return { isValid: false, error: 'Formato não suportado. Formatos aceitos: JPEG e PNG.' };
    }
    const fileName = file.name.toLowerCase();
    if (!ALLOWED_EXTENSIONS.some(ext => fileName.endsWith(ext))) {
      return { isValid: false, error: `Extensão não permitida. Extensões aceitas: ${ALLOWED_EXTENSIONS.join(', ')}.` };
    }
    if (file.size > MAX_FILE_SIZE) {
      return { isValid: false, error: 'Arquivo muito grande. O tamanho máximo permitido é 10 MB.' };
    }
    return { isValid: true };
  };

  const acceptFile = (file: File) => {
    setValidationError(null);
    const validation = validateImageFile(file);
    if (!validation.isValid) {
      setValidationError(validation.error || 'Erro ao validar arquivo.');
      return;
    }
    onImageSelected(file);
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) acceptFile(file);
  };

  const handleClassify = async () => {
    if (!selectedImage) {
      onClassificationError('Nenhuma imagem selecionada.');
      return;
    }

    onClassificationStart();

    try {
      const dataUrl = await fileToDataUrl(selectedImage);
      const uploaded = await uploadMutation.mutateAsync({
        fileName: selectedImage.name,
        mimeType: selectedImage.type as 'image/jpeg' | 'image/png',
        dataUrl,
      });
      const response = await classifyMutation.mutateAsync({ imageId: uploaded.imageId });
      onClassificationComplete(response as ClassificationResponse);
    } catch (error) {
      onClassificationError(formatClassificationError(error));
    }
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();
    if (isProcessing) return;
    const file = event.dataTransfer.files?.[0];
    if (file) acceptFile(file);
  };

  const handleUploadClick = () => {
    if (!isProcessing) fileInputRef.current?.click();
  };

  return (
    <div className="space-y-6">
      {validationError && (
        <Alert variant="destructive" className="animate-in fade-in slide-in-from-top-2 duration-300">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Imagem inválida</AlertTitle>
          <AlertDescription>{validationError}</AlertDescription>
        </Alert>
      )}

      <Card className="border-2 border-dashed transition-all">
        <CardHeader>
          <CardTitle>Upload de imagem dermatoscópica</CardTitle>
          <CardDescription>
            Selecione uma imagem JPEG ou PNG de até 10 MB. A elegibilidade dermatoscópica será verificada no servidor.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {!imagePreview && (
            <div
              onDragOver={handleDragOver}
              onDrop={handleDrop}
              className="border-2 border-dashed border-slate-300 rounded-lg p-8 text-center hover:border-slate-400 transition-colors cursor-pointer bg-slate-50/50"
              onClick={handleUploadClick}
            >
              <UploadIcon className="w-12 h-12 mx-auto mb-4 text-slate-400" />
              <p className="text-lg font-medium text-slate-900 mb-2">Arraste uma imagem aqui ou clique para selecionar</p>
              <p className="text-sm text-slate-500">Formatos suportados: JPEG, PNG | Tamanho máximo: 10 MB</p>
            </div>
          )}

          <input
            ref={fileInputRef}
            type="file"
            accept={ALLOWED_FORMATS.join(',')}
            onChange={handleFileChange}
            className="hidden"
          />

          {imagePreview && (
            <div className="space-y-4 animate-in fade-in duration-500">
              <div className="relative border rounded-lg overflow-hidden bg-slate-50 shadow-inner">
                <img src={imagePreview} alt="Prévia da imagem" className="w-full h-auto max-h-96 object-contain mx-auto" />
                <Button variant="destructive" size="icon" className="absolute top-2 right-2 rounded-full h-8 w-8 shadow-md" onClick={onClearImage} disabled={isProcessing}>
                  <X className="h-4 w-4" />
                </Button>
              </div>

              {selectedImage && (
                <div className="bg-slate-50 p-4 rounded-lg border border-slate-100 grid grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Nome do arquivo</p>
                    <p className="text-sm text-slate-700 truncate font-medium">{selectedImage.name}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Tamanho</p>
                    <p className="text-sm text-slate-700 font-medium">{(selectedImage.size / 1024 / 1024).toFixed(2)} MB</p>
                  </div>
                </div>
              )}

              <Button onClick={handleClassify} disabled={isProcessing} className="w-full bg-blue-600 hover:bg-blue-700 text-white shadow-sm" size="lg">
                {isProcessing ? (
                  <span className="flex items-center gap-2"><Loader2 className="h-4 w-4 animate-spin" /> Processando no servidor...</span>
                ) : 'Iniciar análise de câncer'}
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {isProcessing && (
        <Card className="border-blue-100 bg-blue-50/30">
          <CardContent className="pt-6 space-y-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <p className="font-medium text-blue-900">{statusMessage}</p>
                <span className="text-sm font-bold text-blue-600">{progress}%</span>
              </div>
              <Progress value={progress} className="h-2 bg-blue-100" />
            </div>
          </CardContent>
        </Card>
      )}

      {statusMessage && statusMessage.startsWith('Erro:') && (
        <Alert variant="destructive"><AlertCircle className="h-4 w-4" /><AlertDescription>{statusMessage}</AlertDescription></Alert>
      )}
      {statusMessage && statusMessage.includes('sucesso') && (
        <Alert className="border-green-200 bg-green-50"><CheckCircle className="h-4 w-4 text-green-600" /><AlertDescription className="text-green-800">{statusMessage}</AlertDescription></Alert>
      )}

      <Card className="bg-slate-50 border-slate-200">
        <CardHeader className="pb-2"><CardTitle className="text-sm font-bold text-slate-700 flex items-center gap-2"><AlertCircle className="w-4 h-4 text-blue-500" />Dicas para melhor resultado</CardTitle></CardHeader>
        <CardContent className="space-y-2 text-xs text-slate-600">
          <p>Use imagens de alta qualidade capturadas com dermatoscópio.</p>
          <p>Certifique-se de que a lesão está bem iluminada e centralizada.</p>
          <p>Evite sombras, reflexos ou pelos excessivos na área da lesão.</p>
          <p>Mantenha a imagem em foco; entradas de baixa qualidade serão rejeitadas pelo sistema.</p>
        </CardContent>
      </Card>
    </div>
  );
}
