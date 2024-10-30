import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import './App.css';
import AlgorithmsSection from './AlgorithmsSection';
import PlantMonitor from './PlantMonitor';
import ManagerSection from './ManagerSection';
import NavigationBar from './NavigationBar';

function App() {
  return (
    <Router>
      <div className="App">
        <NavigationBar />
        <Routes>
          <Route exact path="/" element={<PlantMonitor />} />
          <Route path="/algorithms" element={<AlgorithmsSection />} />
          <Route path="/manager" element={<ManagerSection />} />
          {/* Add more routes for other components */}
        </Routes>
      </div>
    </Router>
  );
}

export default App;