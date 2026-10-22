# AI Knowledge Copilot - Frontend

A modern, responsive React frontend for the AI Knowledge Copilot application. Built with Vite for fast development and production builds.

## Features

- **Responsive Chat Interface**: Modern chat UI with auto-scrolling
- **Document Upload**: Upload documents for knowledge base
- **Source Display**: View retrieved sources for answers
- **Loading States**: Visual feedback during API calls
- **Error Handling**: Graceful error handling and messages
- **Configurable API Endpoint**: Set API URL via environment variable

---

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ChatInterface.tsx    # Main chat component
│   │   ├── DocumentUpload.tsx   # Document upload component
│   │   ├── SourceDisplay.tsx    # Source/results display
│   │   └── LoadingSpinner.tsx   # Loading indicator
│   ├── services/
│   │   ├── api.ts               # API client
│   │   └── documentService.ts   # Document operations
│   ├── hooks/
│   │   ├── useChat.ts           # Chat hook
│   │   └── useDocumentUpload.ts # Document upload hook
│   ├── App.tsx                   # Main app component
│   ├── main.tsx                  # Entry point
│   ├── App.css                   # Styles
│   └── env.d.ts                  # Environment types
├── public/
├── index.html
├── vite.config.ts
├── tsconfig.json
└── package.json
```

---

## Getting Started

### Prerequisites

- Node.js 20+
- npm or yarn

### Installation

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Start development server
npm run dev
```

### Environment Variables

Create a `.env` file with:

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_NAME=AI Knowledge Copilot
VITE_ENV=development
```

---

## Component Overview

### ChatInterface

The main chat component that handles:
- Sending questions to the backend
- Displaying answers
- Showing retrieved sources
- Loading and error states

### DocumentUpload

Handles document upload:
- File selection
- Progress indicators
- Success/error feedback

### SourceDisplay

Displays retrieved sources with:
- Source titles
- Content excerpts
- Link to full source

---

## API Integration

The frontend communicates with the backend via REST API:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/documents` | POST | Upload document |
| `/api/documents` | GET | List documents |
| `/api/questions` | POST | Ask a question |
| `/api/ingest/trigger` | POST | Trigger ingestion |

---

## Testing

Run tests with:

```bash
npm run test
```

Run tests in watch mode:

```bash
npm run test:watch
```

---

## Deployment

### Build for Production

```bash
npm run build
```

The output is in `dist/` directory.

### Deploy to AKS

```bash
# Using Helm
helm upgrade --install ai-knowledge-copilot helm/ai-knowledge-copilot \
  --namespace ai-knowledge-copilot \
  --create-namespace \
  --set frontend.image.repository=aicopi01dev.azurecr.io/ai-knowledge-copilot-frontend \
  --set frontend.image.tag=latest \
  --wait
```

---

## Styling

The application uses CSS custom properties for theming:

```css
:root {
  --primary-color: #4f46e5;
  --secondary-color: #6b7280;
  --background-color: #f3f4f6;
  --text-color: #1f2937;
  --error-color: #ef4444;
  --success-color: #10b981;
  --warning-color: #f59e0b;
}
```

---

## Usage Examples

### Asking a Question

```typescript
import { askQuestion } from './services/api';

const response = await askQuestion({
  question: "What is AI?"
});

console.log(response.answer);
console.log(response.sources);
```

### Uploading a Document

```typescript
import { uploadDocument } from './services/api';

const file = document.getElementById('file-input') as HTMLInputElement;

const response = await uploadDocument({
  title: "AI Guide",
  content_type: "pdf",
  content: file.files[0]
});

console.log(response.id);
```

---

## Troubleshooting

See [Troubleshooting Guide](../docs/troubleshooting.md) for common issues.
