import { HashRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import ReviewPanel from './components/ReviewPanel';
import {
  uploadProcurement,
  uploadUtility,
  uploadTravel,
  getProcurementAll,
  getUtilityAll,
  getTravelAll,
  reviewProcurement,
  reviewUtility,
  reviewTravel,
} from './api';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="navbar">
          <div className="navbar-content">
            <a href="/#/" className="navbar-brand">
              Breathe ESG
            </a>
            <p className="navbar-subtitle">Data ingestion and review portal</p>
          </div>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route
              path="/procurement"
              element={
                <ReviewPanel
                  title="SAP Procurement & Fuel Data"
                  sourceType="SAP CSV"
                  uploadFn={uploadProcurement}
                  fetchFn={getProcurementAll}
                  reviewFn={reviewProcurement}
                  fields={[
                    { key: 'document_number', label: 'Document #' },
                    { key: 'vendor_name', label: 'Vendor' },
                    { key: 'material_code', label: 'Material' },
                    { key: 'quantity_original', label: 'Qty', type: 'number' },
                    { key: 'unit_original', label: 'Unit' },
                    { key: 'procurement_date', label: 'Date', type: 'date' },
                    { key: 'amount', label: 'Cost', type: 'currency' },
                  ]}
                />
              }
            />
            <Route
              path="/utility"
              element={
                <ReviewPanel
                  title="Utility Electricity Data"
                  sourceType="Utility CSV"
                  uploadFn={uploadUtility}
                  fetchFn={getUtilityAll}
                  reviewFn={reviewUtility}
                  fields={[
                    { key: 'meter_id', label: 'Meter ID' },
                    { key: 'facility_location', label: 'Facility' },
                    { key: 'consumption_kwh', label: 'kWh', type: 'number' },
                    { key: 'reading_date', label: 'Reading Date', type: 'date' },
                    { key: 'tariff_name', label: 'Tariff' },
                    { key: 'amount', label: 'Cost', type: 'currency' },
                  ]}
                />
              }
            />
            <Route
              path="/travel"
              element={
                <ReviewPanel
                  title="Corporate Travel Data"
                  sourceType="Travel CSV"
                  uploadFn={uploadTravel}
                  fetchFn={getTravelAll}
                  reviewFn={reviewTravel}
                  fields={[
                    { key: 'trip_id', label: 'Trip ID' },
                    { key: 'traveler_name', label: 'Traveler' },
                    { key: 'travel_type', label: 'Type' },
                    { key: 'origin', label: 'From' },
                    { key: 'destination', label: 'To' },
                    { key: 'distance_km', label: 'Distance (km)', type: 'number' },
                    { key: 'travel_date', label: 'Date', type: 'date' },
                    { key: 'amount', label: 'Cost', type: 'currency' },
                  ]}
                />
              }
            />
          </Routes>
        </main>

        <footer className="footer">
          <p>Breathe ESG data ingestion system | Multi-source normalization and audit trail</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
