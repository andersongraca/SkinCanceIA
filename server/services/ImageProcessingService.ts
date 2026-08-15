/**
 * Serviço de Processamento de Imagens Dermatoscópicas
 * 
 * Este módulo implementa a lógica de validação, pré-processamento e
 * manipulação de imagens dermatoscópicas carregadas pelos usuários.
 * Segue princípios de encapsulamento e responsabilidade única.
 */

import * as fs from 'fs';
import * as path from 'path';

/**
 * Interface que define as restrições de validação para imagens.
 * Permite configuração flexível dos limites de tamanho e formatos aceitos.
 */
interface ImageValidationConfig {
  /** Tamanho máximo do arquivo em bytes */
  maxFileSizeBytes: number;
  /** Formatos MIME aceitos */
  allowedMimeTypes: string[];
  /** Extensões de arquivo aceitas */
  allowedExtensions: string[];
}

/**
 * Interface que representa o resultado da validação de uma imagem.
 */
interface ValidationResult {
  /** Indica se a validação foi bem-sucedida */
  isValid: boolean;
  /** Mensagem de erro, se houver */
  errorMessage?: string;
  /** Informações sobre o arquivo validado */
  fileInfo?: {
    fileName: string;
    fileSize: number;
    mimeType: string;
    extension: string;
  };
}

/**
 * Classe responsável pelo processamento e validação de imagens dermatoscópicas.
 * Implementa validação de formato, tamanho e pré-processamento básico.
 */
export class ImageProcessingService {
  // Configuração padrão para validação de imagens
  private validationConfig: ImageValidationConfig;

  /**
   * Construtor do serviço de processamento de imagens.
   * Inicializa a configuração padrão com limites apropriados para imagens médicas.
   */
  constructor() {
    // Configuração padrão: máximo 10MB, apenas JPEG e PNG
    this.validationConfig = {
      maxFileSizeBytes: 10 * 1024 * 1024, // 10 MB
      allowedMimeTypes: ['image/jpeg', 'image/png'],
      allowedExtensions: ['.jpg', '.jpeg', '.png'],
    };
  }

  /**
   * Define uma configuração customizada para validação de imagens.
   * Permite ajustar os limites de acordo com requisitos específicos.
   * 
   * @param config - Nova configuração de validação
   */
  public setValidationConfig(config: Partial<ImageValidationConfig>): void {
    this.validationConfig = {
      ...this.validationConfig,
      ...config,
    };
  }

  /**
   * Valida uma imagem carregada verificando formato, tamanho e extensão.
   * Retorna um objeto com o resultado detalhado da validação.
   * 
   * @param filePath - Caminho do arquivo a ser validado
   * @param mimeType - Tipo MIME do arquivo
   * @returns Resultado da validação com detalhes do arquivo ou mensagem de erro
   */
  public validateImage(filePath: string, mimeType: string): ValidationResult {
    try {
      // Verifica se o arquivo existe
      if (!fs.existsSync(filePath)) {
        return {
          isValid: false,
          errorMessage: 'Arquivo não encontrado',
        };
      }

      // Obtém informações do arquivo
      const stats = fs.statSync(filePath);
      const fileName = path.basename(filePath);
      const extension = path.extname(fileName).toLowerCase();

      // Valida o tipo MIME
      if (!this.validationConfig.allowedMimeTypes.includes(mimeType)) {
        return {
          isValid: false,
          errorMessage: `Tipo de arquivo não suportado. Formatos aceitos: ${this.validationConfig.allowedMimeTypes.join(', ')}`,
        };
      }

      // Valida a extensão do arquivo
      if (!this.validationConfig.allowedExtensions.includes(extension)) {
        return {
          isValid: false,
          errorMessage: `Extensão de arquivo não permitida. Extensões aceitas: ${this.validationConfig.allowedExtensions.join(', ')}`,
        };
      }

      // Valida o tamanho do arquivo
      if (stats.size > this.validationConfig.maxFileSizeBytes) {
        const maxSizeMB = this.validationConfig.maxFileSizeBytes / (1024 * 1024);
        return {
          isValid: false,
          errorMessage: `Arquivo muito grande. Tamanho máximo permitido: ${maxSizeMB}MB`,
        };
      }

      // Validação bem-sucedida
      return {
        isValid: true,
        fileInfo: {
          fileName,
          fileSize: stats.size,
          mimeType,
          extension,
        },
      };
    } catch (error) {
      return {
        isValid: false,
        errorMessage: `Erro ao validar arquivo: ${error instanceof Error ? error.message : 'Erro desconhecido'}`,
      };
    }
  }

  /**
   * Gera um nome de arquivo único baseado em timestamp e número aleatório.
   * Evita conflitos de nomes de arquivo no armazenamento.
   * 
   * @param originalFileName - Nome original do arquivo
   * @returns Nome único para o arquivo
   */
  public generateUniqueFileName(originalFileName: string): string {
    const timestamp = Date.now();
    const random = Math.floor(Math.random() * 10000);
    const extension = path.extname(originalFileName);
    const nameWithoutExt = path.basename(originalFileName, extension);
    
    return `${nameWithoutExt}_${timestamp}_${random}${extension}`;
  }

  /**
   * Obtém informações sobre um arquivo de imagem.
   * Retorna detalhes como tamanho, extensão e tipo MIME.
   * 
   * @param filePath - Caminho do arquivo
   * @returns Informações do arquivo ou null se o arquivo não existir
   */
  public getFileInfo(filePath: string): { fileName: string; fileSize: number; extension: string } | null {
    try {
      if (!fs.existsSync(filePath)) {
        return null;
      }

      const stats = fs.statSync(filePath);
      const fileName = path.basename(filePath);
      const extension = path.extname(fileName);

      return {
        fileName,
        fileSize: stats.size,
        extension,
      };
    } catch (error) {
      console.error('Erro ao obter informações do arquivo:', error);
      return null;
    }
  }

  /**
   * Remove um arquivo de imagem do sistema de arquivos.
   * Utilizado para limpeza de arquivos temporários ou quando necessário.
   * 
   * @param filePath - Caminho do arquivo a ser removido
   * @returns true se removido com sucesso, false caso contrário
   */
  public deleteFile(filePath: string): boolean {
    try {
      if (fs.existsSync(filePath)) {
        fs.unlinkSync(filePath);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Erro ao remover arquivo:', error);
      return false;
    }
  }
}

/**
 * Instância singleton do serviço de processamento de imagens.
 * Garante que apenas uma instância seja criada e reutilizada em toda a aplicação.
 */
export const imageProcessingService = new ImageProcessingService();
