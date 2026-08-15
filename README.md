# SkinCancerCADDermoIA

## Sistema de Diagnóstico Auxiliado por Computador para Detecção de Câncer de Pele

O **SkinCancerCADDermoIA** é uma plataforma avançada de auxílio ao diagnóstico dermatológico, focada na detecção precoce de lesões de pele malignas (como melanoma) através do processamento de imagens dermatoscópicas. O sistema utiliza múltiplas arquiteturas de redes neurais para fornecer uma análise robusta e confiável.

### 🚀 Funcionalidades

- **Upload e Processamento**: Suporte para upload de imagens dermatoscópicas com validação automática de formato e qualidade.
- **Múltiplos Modelos de Análise**:
  - **CNN (Rede Neural Convolucional)**: Focada em características texturais e padrões locais.
  - **Vision Transformer (ViT)**: Analisa relações globais e contextos espaciais da lesão.
  - **Modelo Híbrido**: Combina o melhor das arquiteturas CNN e Transformer.
  - **Ensemble**: Sistema de votação ponderada para decisão final de alta precisão.
- **Visualização de Resultados**: Exibição clara da classificação (Benigna/Maligna) com níveis de confiança detalhados por modelo.
- **Histórico de Diagnósticos**: Registro completo de análises anteriores para acompanhamento.
- **Dashboard de Métricas**: Visualização de desempenho dos modelos (Acurácia, Sensibilidade, Especificidade, F1-Score e AUC).

### 🛠️ Tecnologias Utilizadas

- **Frontend**: React 19, TypeScript, Tailwind CSS, Lucide React, Recharts.
- **Backend**: Node.js, Express, tRPC (para APIs tipadas).
- **Banco de Dados**: MySQL com Drizzle ORM.
- **Processamento**: Serviços modulares seguindo princípios de Programação Orientada a Objetos (POO).

### 📋 Pré-requisitos

- Node.js (v18 ou superior)
- MySQL
- pnpm ou npm

### 🔧 Instalação e Execução

1. Clone o repositório:
   ```bash
   git clone https://github.com/andersonga/SkinCancerCADDermoIA.git
   ```

2. Instale as dependências:
   ```bash
   pnpm install
   ```

3. Configure as variáveis de ambiente no arquivo `.env`.

4. Execute as migrações do banco de dados:
   ```bash
   pnpm db:push
   ```

5. Inicie o servidor de desenvolvimento:
   ```bash
   pnpm dev
   ```

### 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---
Desenvolvido por [Anderson](mailto:andersonga@dcomp.ufs.br).
