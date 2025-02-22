import React, { useCallback, useState } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Edge,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Button } from './ui/button';
import { Database, Server, Layout, Code } from 'lucide-react';
import { ChatBot } from './ChatBot';
import { CodePreview } from './CodePreview';

const initialNodes = [
  {
    id: '1',
    type: 'input',
    data: { label: 'Start' },
    position: { x: 250, y: 25 },
  },
];

const mockGenerateCode = (nodes: any[], edges: any[]) => {
  // This is a mock implementation. In a real app, this would generate actual code based on the diagram
  return `// Generated TypeScript code
interface User {
  id: string;
  email: string;
  password: string;
  createdAt: Date;
}

interface Post {
  id: string;
  title: string;
  content: string;
  authorId: string;
  createdAt: Date;
}

// Database schema
const createUsersTable = \`
  CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
  );
\`;

const createPostsTable = \`
  CREATE TABLE posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    content TEXT,
    author_id UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
  );
\`;

// API endpoints
app.post('/api/users', async (req, res) => {
  const { email, password } = req.body;
  // Implementation...
});

app.post('/api/posts', async (req, res) => {
  const { title, content } = req.body;
  // Implementation...
});

// React components
export function UserProfile({ user }: { user: User }) {
  return (
    <div className="p-4 rounded-lg shadow">
      <h2 className="text-xl font-bold">{user.email}</h2>
      <p className="text-gray-600">Member since {user.createdAt.toLocaleDateString()}</p>
    </div>
  );
}
`;
};

function DiagramEditor() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [isCodePreviewOpen, setIsCodePreviewOpen] = useState(false);
  const [generatedCode, setGeneratedCode] = useState('');

  const onConnect = useCallback(
    (params: Edge | Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges],
  );

  const addDatabaseNode = useCallback(() => {
    const newNode = {
      id: `${Date.now()}`,
      data: { label: 'Database' },
      position: { x: Math.random() * 500, y: Math.random() * 500 },
    };
    setNodes((nds) => [...nds, newNode]);
  }, [setNodes]);

  const addAPINode = useCallback(() => {
    const newNode = {
      id: `${Date.now()}`,
      data: { label: 'API Endpoint' },
      position: { x: Math.random() * 500, y: Math.random() * 500 },
    };
    setNodes((nds) => [...nds, newNode]);
  }, [setNodes]);

  const addComponentNode = useCallback(() => {
    const newNode = {
      id: `${Date.now()}`,
      data: { label: 'UI Component' },
      position: { x: Math.random() * 500, y: Math.random() * 500 },
    };
    setNodes((nds) => [...nds, newNode]);
  }, [setNodes]);

  const handlePromptSubmit = async (prompt: string) => {
    // Mock implementation - in a real app, this would call an API
    await new Promise((resolve) => setTimeout(resolve, 1500));
    
    const newNodes = [
      {
        id: 'users',
        data: { label: 'Users' },
        position: { x: 250, y: 100 },
      },
      {
        id: 'posts',
        data: { label: 'Posts' },
        position: { x: 250, y: 250 },
      },
    ];
    
    const newEdges = [
      {
        id: 'users-posts',
        source: 'users',
        target: 'posts',
        label: 'has many',
      },
    ];
    
    setNodes(newNodes);
    setEdges(newEdges);
  };

  const handleGenerateCode = useCallback(() => {
    const code = mockGenerateCode(nodes, edges);
    setGeneratedCode(code);
    setIsCodePreviewOpen(true);
  }, [nodes, edges]);

  return (
    <div className="w-full h-screen bg-gray-50">
      <div className="absolute top-4 left-4 z-10 flex gap-2">
        <Button onClick={addDatabaseNode} variant="outline" size="sm">
          <Database className="mr-2 h-4 w-4" />
          Add Database
        </Button>
        <Button onClick={addAPINode} variant="outline" size="sm">
          <Server className="mr-2 h-4 w-4" />
          Add API
        </Button>
        <Button onClick={addComponentNode} variant="outline" size="sm">
          <Layout className="mr-2 h-4 w-4" />
          Add Component
        </Button>
        <Button onClick={handleGenerateCode} variant="default" size="sm">
          <Code className="mr-2 h-4 w-4" />
          Generate Code
        </Button>
      </div>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
      <ChatBot onPromptSubmit={handlePromptSubmit} />
      <CodePreview
        isOpen={isCodePreviewOpen}
        onClose={() => setIsCodePreviewOpen(false)}
        code={generatedCode}
      />
    </div>
  );
}

export default DiagramEditor;