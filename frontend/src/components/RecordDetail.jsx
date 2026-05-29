import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { ArrowLeft, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';

export default function RecordDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [record, setRecord] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [actionLoading, setActionLoading] = useState(false);
  const [flagReason, setFlagReason] = useState('');
  const [showFlagModal, setShowFlagModal] = useState(false);

  useEffect(() => {
    setLoading(true);
    api.getRecord(id)
      .then((res) => setRecord(res.data))
      .catch((err) => setError('Failed to load record'))
      .finally(() => setLoading(false));
  }, [id]);

  const handleApprove = async () => {
    setActionLoading(true);
    try {
      await api.approveRecord(id);
      setRecord((r) => ({ ...r, review_status: 'approved' }));
    } catch (err) {
      setError('Failed to approve record');
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    if (!window.confirm('Are you sure you want to reject this record?')) return;
    setActionLoading(true);
    try {
      await api.rejectRecord(id, { reason: 'Rejected by analyst' });
      setRecord((r) => ({ ...r, review_status: 'rejected' }));
    } catch (err) {
      setError('Failed to reject record');
    } finally {
      setActionLoading(false);
    }
  };

  const handleFlag = async () => {
    if (!flagReason) {
      setError('Please provide a reason for flagging');
      return;
    }
    setActionLoading(true);
    try {
      await api.flagRecord(id, { reason: flagReason });
      setRecord((r) => ({ ...r, review_status: 'flagged', flagged_reason: flagReason }));
      setShowFlagModal(false);
    } catch (err) {
      setError('Failed to flag record');
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-gray-500">Loading record...</div>;
  }

  if (!record) {
    return (
      <div className="p-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
          Record not found
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <button
        onClick={() => navigate('/records')}
        className="flex items-center space-x-2 text-blue-600 hover:text-blue-700 mb-6"
      >
        <ArrowLeft size={18} />
        <span>Back to Records</span>
      </button>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800 text-sm">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-2">
          {/* Header */}
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{record.category}</h1>
                <p className="text-gray-600 text-sm mt-1">{record.scope_display}</p>
              </div>
              <span
                className={`px-3 py-1 rounded-full text-sm font-medium ${
                  record.review_status === 'approved'
                    ? 'bg-green-100 text-green-800'
                    : record.review_status === 'rejected'
                    ? 'bg-red-100 text-red-800'
                    : record.review_status === 'flagged'
                    ? 'bg-orange-100 text-orange-800'
                    : 'bg-yellow-100 text-yellow-800'
                }`}
              >
                {record.review_status_display}
              </span>
            </div>

            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="border-l-4 border-blue-500 pl-4">
                <p className="text-xs text-gray-600 uppercase">Quantity</p>
                <p className="text-2xl font-bold text-gray-900">
                  {parseFloat(record.quantity).toFixed(2)} {record.unit_display}
                </p>
              </div>
              <div className="border-l-4 border-green-500 pl-4">
                <p className="text-xs text-gray-600 uppercase">CO₂e</p>
                <p className="text-2xl font-bold text-gray-900">
                  {parseFloat(record.co2e_kg).toFixed(2)} kg
                </p>
              </div>
              <div className="border-l-4 border-purple-500 pl-4">
                <p className="text-xs text-gray-600 uppercase">Quality Score</p>
                <p className="text-2xl font-bold text-gray-900">{record.quality_score}%</p>
              </div>
            </div>
          </div>

          {/* Details */}
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Details</h2>
            <dl className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <dt className="text-sm font-medium text-gray-600">Date</dt>
                  <dd className="text-gray-900">
                    {new Date(record.transaction_date).toLocaleDateString()}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-600">Source</dt>
                  <dd className="text-gray-900">{record.data_source_name || 'Unknown'}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-600">Location</dt>
                  <dd className="text-gray-900">{record.location || 'N/A'}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-600">Business Unit</dt>
                  <dd className="text-gray-900">{record.business_unit || 'N/A'}</dd>
                </div>
              </div>
            </dl>
          </div>

          {/* Source-Specific Details */}
          {record.sap_record && (
            <div className="bg-white rounded-lg shadow p-6 mb-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">SAP Details</h2>
              <dl className="grid grid-cols-2 gap-4">
                <div>
                  <dt className="text-sm font-medium text-gray-600">Plant Code</dt>
                  <dd className="text-gray-900">{record.sap_record.plant_code}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-600">Material #</dt>
                  <dd className="text-gray-900">{record.sap_record.material_number}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-600">PO Number</dt>
                  <dd className="text-gray-900">{record.sap_record.po_number}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-600">Fuel Type</dt>
                  <dd className="text-gray-900">{record.sap_record.fuel_type}</dd>
                </div>
              </dl>
            </div>
          )}

          {record.utility_record && (
            <div className="bg-white rounded-lg shadow p-6 mb-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Utility Details</h2>
              <dl className="grid grid-cols-2 gap-4">
                <div>
                  <dt className="text-sm font-medium text-gray-600">Meter ID</dt>
                  <dd className="text-gray-900">{record.utility_record.meter_id}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-600">Facility</dt>
                  <dd className="text-gray-900">{record.utility_record.facility_name}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-600">Provider</dt>
                  <dd className="text-gray-900">{record.utility_record.utility_provider}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-600">Billing Period</dt>
                  <dd className="text-gray-900">
                    {new Date(record.utility_record.billing_period_start).toLocaleDateString()} -{' '}
                    {new Date(record.utility_record.billing_period_end).toLocaleDateString()}
                  </dd>
                </div>
              </dl>
            </div>
          )}

          {record.travel_record && (
            <div className="bg-white rounded-lg shadow p-6 mb-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Travel Details</h2>
              <dl className="grid grid-cols-2 gap-4">
                <div>
                  <dt className="text-sm font-medium text-gray-600">Trip ID</dt>
                  <dd className="text-gray-900">{record.travel_record.trip_id}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-600">Mode</dt>
                  <dd className="text-gray-900">{record.travel_record.travel_mode_display}</dd>
                </div>
                {record.travel_record.departure_airport && (
                  <div>
                    <dt className="text-sm font-medium text-gray-600">Route</dt>
                    <dd className="text-gray-900">
                      {record.travel_record.departure_airport} → {record.travel_record.arrival_airport}
                    </dd>
                  </div>
                )}
              </dl>
            </div>
          )}

          {/* Audit Log */}
          {record.audit_logs && record.audit_logs.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Audit Trail</h2>
              <div className="space-y-3">
                {record.audit_logs.map((log, idx) => (
                  <div key={idx} className="flex space-x-4 text-sm border-l-2 border-gray-200 pl-4 py-2">
                    <div className="text-gray-600 min-w-max">
                      {new Date(log.timestamp).toLocaleString()}
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{log.action_display}</p>
                      <p className="text-gray-600">{log.description}</p>
                      {log.user_name && <p className="text-xs text-gray-500">by {log.user_name}</p>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Actions Sidebar */}
        <div>
          <div className="bg-white rounded-lg shadow p-6 sticky top-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-6">Actions</h2>

            <div className="space-y-3">
              {record.review_status !== 'approved' && (
                <button
                  onClick={handleApprove}
                  disabled={actionLoading}
                  className="w-full flex items-center justify-center space-x-2 bg-green-600 hover:bg-green-700 text-white font-medium py-3 rounded-lg transition disabled:opacity-50"
                >
                  <CheckCircle size={18} />
                  <span>Approve</span>
                </button>
              )}

              {record.review_status !== 'flagged' && (
                <button
                  onClick={() => setShowFlagModal(true)}
                  disabled={actionLoading}
                  className="w-full flex items-center justify-center space-x-2 bg-orange-600 hover:bg-orange-700 text-white font-medium py-3 rounded-lg transition disabled:opacity-50"
                >
                  <AlertTriangle size={18} />
                  <span>Flag for Review</span>
                </button>
              )}

              {record.review_status !== 'rejected' && (
                <button
                  onClick={handleReject}
                  disabled={actionLoading}
                  className="w-full flex items-center justify-center space-x-2 bg-red-600 hover:bg-red-700 text-white font-medium py-3 rounded-lg transition disabled:opacity-50"
                >
                  <XCircle size={18} />
                  <span>Reject</span>
                </button>
              )}
            </div>

            {record.flagged_reason && (
              <div className="mt-6 p-4 bg-orange-50 border border-orange-200 rounded-lg">
                <p className="text-xs font-medium text-orange-900 mb-1">Flagged Reason:</p>
                <p className="text-sm text-orange-800">{record.flagged_reason}</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Flag Modal */}
      {showFlagModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Flag Record for Review</h3>
            <textarea
              value={flagReason}
              onChange={(e) => setFlagReason(e.target.value)}
              placeholder="Enter reason for flagging..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg mb-4 focus:ring-2 focus:ring-orange-500"
              rows="4"
            />
            <div className="flex space-x-3">
              <button
                onClick={() => setShowFlagModal(false)}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleFlag}
                disabled={actionLoading}
                className="flex-1 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50"
              >
                Flag
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
