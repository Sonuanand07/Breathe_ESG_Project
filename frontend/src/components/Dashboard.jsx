import React, { useEffect, useState } from 'react';
import { useStore } from '../store';
import { api } from '../services/api';
import { AlertCircle, CheckCircle, Clock, BarChart3 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Dashboard() {
  const { selectedClient, setDashboardSummary, dashboardSummary } = useStore();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    if (!selectedClient) return;

    setLoading(true);
    setError('');

    api.getDashboardSummary(selectedClient.id)
      .then((res) => setDashboardSummary(res.data))
      .catch((err) => setError('Failed to load dashboard data'))
      .finally(() => setLoading(false));
  }, [selectedClient, setDashboardSummary]);

  if (!selectedClient) {
    return (
      <div className="p-8">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-yellow-800">
          <p>Please select a client from the sidebar to get started.</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-gray-500">Loading dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
          {error}
        </div>
      </div>
    );
  }

  const cards = [
    {
      label: 'Total Records',
      value: dashboardSummary?.total_records || 0,
      icon: BarChart3,
      color: 'bg-blue-50 text-blue-600',
    },
    {
      label: 'Pending Review',
      value: dashboardSummary?.pending || 0,
      icon: Clock,
      color: 'bg-yellow-50 text-yellow-600',
      action: () => navigate('/records?status=pending'),
    },
    {
      label: 'Approved',
      value: dashboardSummary?.approved || 0,
      icon: CheckCircle,
      color: 'bg-green-50 text-green-600',
    },
    {
      label: 'Issues',
      value: (dashboardSummary?.flagged || 0) + (dashboardSummary?.rejected || 0),
      icon: AlertCircle,
      color: 'bg-red-50 text-red-600',
      action: () => navigate('/records?status=flagged'),
    },
  ];

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">
        {selectedClient.name} - Overview
      </h1>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {cards.map((card) => {
          const Icon = card.icon;
          return (
            <button
              key={card.label}
              onClick={card.action}
              className={`p-6 rounded-lg cursor-pointer transition hover:shadow-lg ${card.color}`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium opacity-75">{card.label}</p>
                  <p className="text-3xl font-bold mt-2">{card.value}</p>
                </div>
                <Icon size={32} className="opacity-20" />
              </div>
            </button>
          );
        })}
      </div>

      {/* Scope Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {['scope_1', 'scope_2', 'scope_3'].map((scope, idx) => (
          <div key={scope} className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-600 mb-2">
              {scope === 'scope_1' ? 'Scope 1' : scope === 'scope_2' ? 'Scope 2' : 'Scope 3'}
            </h3>
            <p className="text-2xl font-bold text-gray-900">
              {dashboardSummary?.by_scope?.[scope] || 0}
            </p>
            <p className="text-xs text-gray-500 mt-2">
              {scope === 'scope_1'
                ? 'Direct Emissions'
                : scope === 'scope_2'
                ? 'Purchased Energy'
                : 'Other Indirect'}
            </p>
          </div>
        ))}
      </div>

      {/* Total Emissions */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg p-8 text-white">
        <h3 className="text-lg font-medium mb-2">Total CO₂e Emissions</h3>
        <p className="text-4xl font-bold">
          {(dashboardSummary?.total_co2e_kg / 1000).toFixed(2)} metric tons
        </p>
        <p className="text-blue-100 text-sm mt-2">
          Based on {dashboardSummary?.total_records} records ingested
        </p>
      </div>

      {/* Next Steps */}
      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="font-semibold text-blue-900 mb-3">Next Steps</h3>
        <ul className="text-sm text-blue-800 space-y-2">
          <li>
            • <strong>Review Pending Records:</strong> {dashboardSummary?.pending} records awaiting approval
          </li>
          <li>
            • <strong>Address Issues:</strong> {dashboardSummary?.flagged} flagged for further analysis
          </li>
          <li>
            • <strong>Upload New Data:</strong> Upload additional data sources to expand your footprint
          </li>
        </ul>
      </div>
    </div>
  );
}
