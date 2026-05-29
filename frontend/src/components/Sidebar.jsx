import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useStore } from '../store';
import {
  BarChart3,
  FileText,
  Upload,
  ChevronDown,
} from 'lucide-react';

export default function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { selectedClient, setSelectedClient, clients } = useStore();
  const [clientOpen, setClientOpen] = React.useState(true);

  const menuItems = [
    { path: '/', label: 'Dashboard', icon: BarChart3 },
    { path: '/records', label: 'Review Records', icon: FileText },
    { path: '/ingest', label: 'Upload Data', icon: Upload },
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <div className="w-64 bg-gray-900 text-white flex flex-col h-screen">
      <div className="p-6 border-b border-gray-800">
        <h2 className="text-xl font-bold">Breathe ESG</h2>
      </div>

      {/* Client Selection */}
      <div className="p-4 border-b border-gray-800">
        <button
          onClick={() => setClientOpen(!clientOpen)}
          className="w-full flex items-center justify-between px-3 py-2 rounded-lg hover:bg-gray-800 transition"
        >
          <span className="text-sm font-medium text-gray-300">Client</span>
          <ChevronDown
            size={16}
            className={`transition-transform ${clientOpen ? 'rotate-180' : ''}`}
          />
        </button>

        {clientOpen && (
          <div className="mt-2 space-y-1">
            {clients.map((client) => (
              <button
                key={client.id}
                onClick={() => setSelectedClient(client)}
                className={`w-full text-left px-3 py-2 rounded-lg text-sm transition ${
                  selectedClient?.id === client.id
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:bg-gray-800'
                }`}
              >
                {client.name}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Menu Items */}
      <nav className="flex-1 p-4 space-y-2">
        {menuItems.map(({ path, label, icon: Icon }) => (
          <button
            key={path}
            onClick={() => navigate(path)}
            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition ${
              isActive(path)
                ? 'bg-blue-600 text-white'
                : 'text-gray-300 hover:bg-gray-800'
            }`}
          >
            <Icon size={20} />
            <span className="font-medium">{label}</span>
          </button>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-800 text-xs text-gray-500 text-center">
        <p>v1.0.0</p>
      </div>
    </div>
  );
}
