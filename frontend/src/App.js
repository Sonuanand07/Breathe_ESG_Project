import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useStore } from './store';
import { api } from './services/api';
import './App.css';

// Components
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import RecordDetail from './components/RecordDetail';
import DataIngestion from './components/DataIngestion';
import RecordsList from './components/RecordsList';
import Login from './components/Login';

function App() {
  const { authToken, sidebarOpen, setSidebarOpen, clients, setClients, selectedClient, setSelectedClient } = useStore();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load clients on mount
    if (authToken) {
      api.getClients()
        .then((res) => {
          const clientList = res.data.results || res.data;
          setClients(clientList);

          // If current selection is missing/invalid, pick the first available client.
          const hasValidSelected = selectedClient && selectedClient.id;
          if (!hasValidSelected && clientList?.[0]) {
            setSelectedClient(clientList[0]);
          }
        })
        .catch((err) => console.error('Failed to load clients:', err))
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [authToken, selectedClient, setClients, setSelectedClient]);

  if (!authToken) {
    return <Login />;
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-2xl font-semibold text-gray-700">Loading...</div>
      </div>
    );
  }

  return (
    <Router>
      <div className="flex h-screen bg-gray-50">
        {sidebarOpen && <Sidebar />}
        <div className="flex-1 flex flex-col overflow-hidden">
          <Navbar />
          <main className="flex-1 overflow-auto">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/records" element={<RecordsList />} />
              <Route path="/records/:id" element={<RecordDetail />} />
              <Route path="/ingest" element={<DataIngestion />} />
              <Route path="*" element={<Navigate to="/" />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;
