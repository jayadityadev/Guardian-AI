import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Upload from './pages/Upload';
import Location from './pages/Location';
import SocialMedia from './pages/SocialMedia';
import SessionHistory from './pages/SessionHistory';
import Support from './pages/Support';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="upload" element={<Upload />} />
          <Route path="dashboard/:sessionId" element={<Dashboard />} />
          <Route path="location" element={<Location />} />
          <Route path="social" element={<SocialMedia />} />
          <Route path="history" element={<SessionHistory />} />
          <Route path="support" element={<Support />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
