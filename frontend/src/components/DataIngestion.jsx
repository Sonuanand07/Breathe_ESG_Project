import React, { useEffect, useState, useMemo } from 'react';
import { useStore } from '../store';
import { api } from '../services/api';
import { Upload, CheckCircle, AlertCircle } from 'lucide-react';

export default function DataIngestion() {
  const { selectedClient } = useStore();

  // Debug helper: helps catch cases where sidebar selection is not propagating
  // (kept harmless in production)
  useEffect(() => {
    if (!selectedClient) return;
    // eslint-disable-next-line no-console
    console.debug('Selected client in DataIngestion:', selectedClient);
  }, [selectedClient]);
  const [dataSource, setDataSource] = useState(''); // source_type: sap | utility | travel
  const [dataSources, setDataSources] = useState([]); // DataSource rows for the selected client
  const [selectedDataSourceId, setSelectedDataSourceId] = useState(''); // UUID
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  // (intentionally not used yet)
  // const selectedDataSource = useMemo(
  //   () => dataSources.find((ds) => ds.id === selectedDataSourceId) || null,
  //   [dataSources, selectedDataSourceId]
  // );

  useEffect(() => {
    // When client changes, load its data sources.
    // Reset selection so user must explicitly choose a data source instance.
    setDataSources([]);
    setSelectedDataSourceId('');

    if (!selectedClient || !selectedClient.id) return;

    api.getDataSources(selectedClient.id)
      .then((res) => {
        const rows = res.data.results || res.data;
        setDataSources(rows);
      })
      .catch(() => {
        setError('Failed to load data sources for selected client');
      });
  }, [selectedClient]);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const filteredDataSources = useMemo(() => {
    if (!dataSource) return dataSources;
    return dataSources.filter((ds) => ds.source_type === dataSource);
  }, [dataSources, dataSource]);

  useEffect(() => {
    // If the user picked a different data source type, clear the data source instance.
    setSelectedDataSourceId('');
  }, [dataSource]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!selectedClient || !selectedClient.id) {
      setError('Please select a client from the sidebar first.');
      return;
    }
    if (!dataSource) {
      setError('Please select a required data source type');
      return;
    }
    if (!selectedDataSourceId) {
      setError('Please select a data source');
      return;
    }
    if (!file) {
      setError('Please select a file');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('client_id', selectedClient.id);
      formData.append('data_source_id', selectedDataSourceId);

      let response;
      if (dataSource === 'sap') {
        response = await api.ingestSAP(formData);
      } else if (dataSource === 'utility') {
        response = await api.ingestUtility(formData);
      } else if (dataSource === 'travel') {
        response = await api.ingestTravel(formData);
      } else {
        throw new Error('Unknown data source type');
      }

      setResult({
        success: true,
        ...response.data,
      });
      setFile(null);
      setDataSource('');
      setSelectedDataSourceId('');
    } catch (err) {
      setError(err.response?.data?.error || 'Upload failed');
      setResult({
        success: false,
        error: err.message,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Upload Data</h1>

      {!selectedClient && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-yellow-800 mb-6">
          Please select a client from the sidebar first.
        </div>
      )}


      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Upload Form */}
        <div className="bg-white rounded-lg shadow p-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-6">Upload Source Data</h2>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Data Source Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Data Source Type *
              </label>
              <div className="space-y-3">
                {[
                  { id: 'sap', label: 'SAP (Fuel & Procurement)', desc: 'CSV export from SAP MM module' },
                  { id: 'utility', label: 'Utility Data (Electricity)', desc: 'Meter readings in CSV format' },
                  { id: 'travel', label: 'Corporate Travel', desc: 'Concur/Navan export in CSV' },
                ].map((source) => (
                  <label key={source.id} className="flex items-center p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition">
                    <input
                      id={`source-${source.id}`}
                      name="dataSource"
                      type="radio"
                      value={source.id}
                      checked={dataSource === source.id}
                      onChange={(e) => setDataSource(e.target.value)}
                      className="w-4 h-4 text-blue-600"
                    />
                    <div className="ml-3">
                      <p className="font-medium text-gray-900">{source.label}</p>
                      <p className="text-xs text-gray-600">{source.desc}</p>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {/* Data Source Instance Selection */}
            <div>
              <label htmlFor="dataSourceInstance" className="block text-sm font-medium text-gray-700 mb-2">
                Select Data Source Instance *
              </label>
              <select
                id="dataSourceInstance"
                name="dataSourceInstance"
                value={selectedDataSourceId}
                onChange={(e) => setSelectedDataSourceId(e.target.value)}
                disabled={!selectedClient || !dataSource || filteredDataSources.length === 0 || loading}
                className="w-full border border-gray-200 rounded-lg px-3 py-3 bg-white text-gray-900 disabled:bg-gray-50 disabled:text-gray-400"
              >
                <option value="">{selectedClient && dataSource ? 'Choose an instance...' : 'Select type and client first'}</option>
                {filteredDataSources.map((ds) => (
                  <option key={ds.id} value={ds.id}>
                    {ds.name}
                  </option>
                ))}
              </select>
              {selectedClient && dataSource && filteredDataSources.length === 0 && (
                <p className="text-xs text-gray-500 mt-2">
                  No data source instances are configured for this client and type.
                </p>
              )}
            </div>

            {/* File Upload */}
            <div>
              <label htmlFor="csvFile" className="block text-sm font-medium text-gray-700 mb-2">
                Select CSV File *
              </label>

              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-500 transition cursor-pointer">
                <input
                  id="csvFile"
                  name="csvFile"
                  type="file"
                  accept=".csv,.xlsx"
                  onChange={handleFileChange}
                  disabled={loading}
                  className="hidden"
                />
                <label htmlFor="csvFile" className="cursor-pointer">
                  <Upload size={32} className="mx-auto text-gray-400 mb-2" />
                  <p className="text-sm text-gray-600">
                    {file ? file.name : 'Click to select or drag and drop CSV file'}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">CSV or XLSX format</p>
                </label>
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading || !file || !dataSource || !selectedDataSourceId}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Uploading...' : 'Upload & Ingest Data'}
            </button>
          </form>

        </div>

        {/* Results */}
        <div>
          {/* Sample Data Guide */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
            <h3 className="font-semibold text-blue-900 mb-3">Expected Format</h3>
            <p className="text-sm text-blue-800 mb-4">
              Your CSV should include the required columns for your data source type.
            </p>

            {dataSource === 'sap' && (
              <div className="text-xs text-blue-800 space-y-1">
                <p><strong>Required columns:</strong></p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>EBELN - Purchase Order</li>
                  <li>WERKS - Plant Code</li>
                  <li>MATNR - Material Number</li>
                  <li>MAKTX - Description</li>
                  <li>MENGE - Quantity</li>
                  <li>BSTME - Unit</li>
                  <li>BUDAT - Date (YYYYMMDD)</li>
                </ul>
              </div>
            )}

            {dataSource === 'utility' && (
              <div className="text-xs text-blue-800 space-y-1">
                <p><strong>Required columns:</strong></p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>meter_id</li>
                  <li>facility_name</li>
                  <li>consumption_kwh</li>
                  <li>billing_period_start</li>
                  <li>billing_period_end</li>
                </ul>
              </div>
            )}

            {dataSource === 'travel' && (
              <div className="text-xs text-blue-800 space-y-1">
                <p><strong>Required columns:</strong></p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>trip_id</li>
                  <li>travel_mode</li>
                  <li>For flights: departure_airport, arrival_airport</li>
                  <li>expense_date (YYYY-MM-DD)</li>
                </ul>
              </div>
            )}
          </div>

          {/* Upload Result */}
          {result && (
            <div className={`rounded-lg p-6 ${result.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
              <div className="flex items-start">
                {result.success ? (
                  <CheckCircle className="text-green-600 mr-3 flex-shrink-0 mt-1" size={20} />
                ) : (
                  <AlertCircle className="text-red-600 mr-3 flex-shrink-0 mt-1" size={20} />
                )}
                <div>
                  <h3 className={`font-semibold mb-2 ${result.success ? 'text-green-900' : 'text-red-900'}`}>
                    {result.success ? 'Upload Successful' : 'Upload Failed'}
                  </h3>

                  {result.success && (
                    <div className={`text-sm space-y-1 ${result.success ? 'text-green-800' : 'text-red-800'}`}>
                      <p>Total Records: <strong>{result.total_records}</strong></p>
                      <p>Successfully Imported: <strong>{result.successful_records}</strong></p>
                      {result.failed_records > 0 && (
                        <p>Failed: <strong>{result.failed_records}</strong></p>
                      )}
                      <p className="text-xs mt-3 text-gray-600">
                        Job ID: {result.job_id}
                      </p>
                    </div>
                  )}

                  {!result.success && (
                    <div className="text-sm text-red-800">
                      <p>{result.error || 'An error occurred during upload'}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
