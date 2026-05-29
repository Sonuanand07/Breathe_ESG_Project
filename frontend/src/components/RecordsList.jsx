import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useStore } from '../store';
import { api } from '../services/api';
import { ChevronRight } from 'lucide-react';

export default function RecordsList() {
  const [searchParams] = useSearchParams();
  const { selectedClient } = useStore();
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    status: searchParams.get('status') || '',
    scope: '',
    category: '',
  });
  const navigate = useNavigate();

  useEffect(() => {
    if (!selectedClient) return;

    setLoading(true);
    const params = {
      client: selectedClient.id,
      review_status: filters.status,
      scope: filters.scope,
      category: filters.category,
      ordering: '-created_at',
    };

    api.getRecords(params)
      .then((res) => setRecords(res.data.results || res.data))
      .catch((err) => console.error('Failed to load records:', err))
      .finally(() => setLoading(false));
  }, [selectedClient, filters]);

  const getStatusBadge = (status) => {
    const styles = {
      pending: 'bg-yellow-100 text-yellow-800',
      approved: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
      flagged: 'bg-orange-100 text-orange-800',
    };
    return (
      <span className={`px-2 py-1 rounded text-xs font-medium ${styles[status] || 'bg-gray-100'}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  const getScopeLabel = (scope) => {
    const labels = {
      scope_1: 'Scope 1',
      scope_2: 'Scope 2',
      scope_3: 'Scope 3',
    };
    return labels[scope] || scope;
  };

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Review Records</h1>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Status
            </label>
            <select
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="approved">Approved</option>
              <option value="flagged">Flagged</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Scope
            </label>
            <select
              value={filters.scope}
              onChange={(e) => setFilters({ ...filters, scope: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Scopes</option>
              <option value="scope_1">Scope 1</option>
              <option value="scope_2">Scope 2</option>
              <option value="scope_3">Scope 3</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Category
            </label>
            <select
              value={filters.category}
              onChange={(e) => setFilters({ ...filters, category: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Categories</option>
              <option value="fleet_fuel">Fleet Fuel</option>
              <option value="purchased_electricity">Electricity</option>
              <option value="business_flights">Flights</option>
              <option value="hotel_stays">Hotels</option>
              <option value="ground_transport_rental_car">Rental Cars</option>
            </select>
          </div>
        </div>
      </div>

      {/* Records Table */}
      {loading ? (
        <div className="text-center py-12 text-gray-500">Loading records...</div>
      ) : records.length === 0 ? (
        <div className="text-center py-12 text-gray-500">No records found.</div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-200">
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    Category
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    Scope
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    Quantity
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    CO₂e (kg)
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-700 uppercase tracking-wider">
                    Quality
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-700 uppercase tracking-wider">
                    &nbsp;
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {records.map((record) => (
                  <tr
                    key={record.id}
                    className="hover:bg-gray-50 cursor-pointer transition"
                    onClick={() => navigate(`/records/${record.id}`)}
                  >
                    <td className="px-6 py-4 text-sm text-gray-900 font-medium">
                      {record.category}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {getScopeLabel(record.scope)}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {parseFloat(record.quantity).toFixed(2)} {record.unit}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600 font-medium">
                      {parseFloat(record.co2e_kg).toFixed(2)}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {new Date(record.transaction_date).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 text-sm">
                      {getStatusBadge(record.review_status)}
                    </td>
                    <td className="px-6 py-4 text-sm text-right font-medium">
                      {record.quality_score}%
                    </td>
                    <td className="px-6 py-4 text-right">
                      <ChevronRight size={18} className="text-gray-400" />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
