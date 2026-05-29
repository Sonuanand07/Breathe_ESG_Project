import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useStore } from '../store';
import { Menu, LogOut } from 'lucide-react';

export default function Navbar() {
  const navigate = useNavigate();
  const { sidebarOpen, setSidebarOpen, logout, selectedClient } = useStore();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="bg-white border-b border-gray-200 h-16 flex items-center justify-between px-6 shadow-sm">
      <div className="flex items-center space-x-4">
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="p-2 hover:bg-gray-100 rounded-lg text-gray-600"
        >
          <Menu size={24} />
        </button>
        <div>
          <h1 className="text-lg font-semibold text-gray-900">
            {selectedClient?.name || 'Breathe ESG'}
          </h1>
          <p className="text-xs text-gray-500">Data Ingestion & Review</p>
        </div>
      </div>

      <button
        onClick={handleLogout}
        className="flex items-center space-x-2 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition"
      >
        <LogOut size={18} />
        <span className="text-sm">Logout</span>
      </button>
    </nav>
  );
}
