import { useCallback, useEffect, useState } from 'react';
import './ReviewPanel.css';

export default function ReviewPanel({
  title,
  uploadFn,
  fetchFn,
  reviewFn,
  fields,
  sourceType,
}) {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [selectedIds, setSelectedIds] = useState(new Set());
  const [reviewerName, setReviewerName] = useState('');
  const [reviewComments, setReviewComments] = useState('');
  const [filterStatus, setFilterStatus] = useState('PENDING');

  const fetchRecords = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetchFn();
      const filtered = response.data.filter((record) => record.review_status === filterStatus);
      setRecords(filtered);
      setError(null);
    } catch (err) {
      setError('Failed to fetch records');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [fetchFn, filterStatus]);

  useEffect(() => {
    Promise.resolve().then(fetchRecords);
  }, [fetchRecords]);

  const handleFileUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setSuccess(null);
    setError(null);

    try {
      const response = await uploadFn(file);
      setSuccess(`Successfully ingested ${response.data.rows_ingested} records`);
      setTimeout(() => {
        fetchRecords();
        event.target.value = '';
      }, 1000);
    } catch (err) {
      setError(`Upload failed: ${err.response?.data?.error || err.message}`);
    } finally {
      setUploading(false);
    }
  };

  const toggleRecord = (id) => {
    const nextSelected = new Set(selectedIds);
    if (nextSelected.has(id)) {
      nextSelected.delete(id);
    } else {
      nextSelected.add(id);
    }
    setSelectedIds(nextSelected);
  };

  const toggleAll = () => {
    if (selectedIds.size === records.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(records.map((record) => record.id)));
    }
  };

  const handleBulkReview = async (status) => {
    if (selectedIds.size === 0) {
      setError('Please select at least one record');
      return;
    }

    if (!reviewerName.trim()) {
      setError('Please enter your name');
      return;
    }

    setLoading(true);
    try {
      const response = await reviewFn(
        Array.from(selectedIds),
        status,
        reviewComments,
        reviewerName,
      );
      setSuccess(`${response.data.updated_count} records updated`);
      setSelectedIds(new Set());
      setReviewComments('');
      setTimeout(() => fetchRecords(), 1000);
    } catch (err) {
      setError(`Review failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const renderCell = (record, field) => {
    const value = record[field.key];
    if (field.type === 'currency') {
      return `$${parseFloat(value || 0).toFixed(2)}`;
    }
    if (field.type === 'date') {
      return new Date(value).toLocaleDateString();
    }
    if (field.type === 'number') {
      return parseFloat(value || 0).toFixed(2);
    }
    return value || '-';
  };

  return (
    <div className="review-panel">
      <div className="review-header">
        <p className="eyebrow">{sourceType}</p>
        <h1>{title}</h1>
        <p>Upload CSV files or review pending records.</p>
      </div>

      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      <div className="upload-section">
        <label className="upload-input">
          <span className="upload-button">Upload {sourceType} file</span>
          <input
            type="file"
            accept=".csv"
            onChange={handleFileUpload}
            disabled={uploading}
            style={{ display: 'none' }}
          />
        </label>
        {uploading && <span className="upload-status">Uploading...</span>}
      </div>

      <div className="controls-section">
        <div className="filter-group">
          <label>Filter by status</label>
          <select value={filterStatus} onChange={(event) => setFilterStatus(event.target.value)}>
            <option value="PENDING">Pending review</option>
            <option value="APPROVED">Approved</option>
            <option value="REJECTED">Rejected</option>
            <option value="LOCKED">Locked for audit</option>
          </select>
        </div>

        <div className="reviewer-info">
          <label>Reviewer</label>
          <input
            type="text"
            placeholder="Your name"
            value={reviewerName}
            onChange={(event) => setReviewerName(event.target.value)}
            maxLength="100"
          />
        </div>
      </div>

      {selectedIds.size > 0 && (
        <div className="review-actions">
          <textarea
            placeholder="Add review comments (optional)"
            value={reviewComments}
            onChange={(event) => setReviewComments(event.target.value)}
            rows="3"
          />
          <div className="action-buttons">
            <button
              onClick={() => handleBulkReview('APPROVED')}
              disabled={loading}
              className="btn btn-success"
            >
              Approve ({selectedIds.size})
            </button>
            <button
              onClick={() => handleBulkReview('REJECTED')}
              disabled={loading}
              className="btn btn-danger"
            >
              Reject ({selectedIds.size})
            </button>
            <button
              onClick={() => handleBulkReview('LOCKED')}
              disabled={loading}
              className="btn btn-info"
            >
              Lock for audit ({selectedIds.size})
            </button>
          </div>
        </div>
      )}

      <div className="records-section">
        <div className="records-header">
          <h3>Records ({records.length})</h3>
          {records.length > 0 && (
            <label className="checkbox">
              <input
                type="checkbox"
                checked={selectedIds.size === records.length && records.length > 0}
                onChange={toggleAll}
              />
              Select all
            </label>
          )}
        </div>

        {loading && <p>Loading records...</p>}
        {records.length === 0 && !loading && (
          <p className="empty-message">No {filterStatus.toLowerCase()} records found</p>
        )}

        {records.length > 0 && (
          <div className="table-container">
            <table className="records-table">
              <thead>
                <tr>
                  <th style={{ width: '40px' }}>
                    <input
                      type="checkbox"
                      checked={selectedIds.size === records.length}
                      onChange={toggleAll}
                    />
                  </th>
                  {fields.map((field) => (
                    <th key={field.key}>{field.label}</th>
                  ))}
                  <th style={{ width: '150px' }}>Status</th>
                  <th style={{ width: '150px' }}>Flags</th>
                </tr>
              </thead>
              <tbody>
                {records.map((record) => (
                  <tr key={record.id} className={selectedIds.has(record.id) ? 'selected' : ''}>
                    <td>
                      <input
                        type="checkbox"
                        checked={selectedIds.has(record.id)}
                        onChange={() => toggleRecord(record.id)}
                      />
                    </td>
                    {fields.map((field) => (
                      <td key={field.key}>{renderCell(record, field)}</td>
                    ))}
                    <td>
                      <span className={`badge badge-${record.review_status.toLowerCase()}`}>
                        {record.review_status}
                      </span>
                    </td>
                    <td>
                      {record.suspicious_flag && (
                        <span className="badge badge-warning" title={record.suspicious_reason}>
                          Suspicious
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
