import React, { useEffect, useState } from 'react';
import axios from 'axios';
import moment from 'moment';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import 'bootstrap/dist/css/bootstrap.min.css';
import './PlantMonitor.css';
import { Helmet } from 'react-helmet';

const baseURL = process.env.REACT_APP_API_URL;
console.log('Base URL:', baseURL);

function PlantMonitor() {
  const [plantData, setPlantData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(`${baseURL}/api/plant-data`);
        const data = response.data;
        const formattedData = data.map((entry) => ({
          ...entry,
          Log_Time: moment(entry.Log_Time).format('YYYY-MM-DD HH:mm'),
        }));
        setPlantData(formattedData);
      } catch (error) {
        console.error('Error fetching plant data:', error);
      }
    };

    fetchData();
    const intervalId = setInterval(fetchData, 5000);

    return () => {
      clearInterval(intervalId);
    };
  }, []);

  // Group plant data by plant ID
  const groupedData = plantData.reduce((acc, entry) => {
    if (!acc[entry.PlantID]) {
      acc[entry.PlantID] = [];
    }
    acc[entry.PlantID].push(entry);
    return acc;
  }, {});

  // Generate random color for each plant
  const getRandomColor = () => {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
      color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
  };

  return (
    <div className="PlantMonitor">
      <Helmet>
        <meta charSet="UTF-8" />
        <link
          rel="stylesheet"
          href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"
          integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3"
          crossOrigin="anonymous"
        />
      </Helmet>
      <div className="container text-center">
        <h1>Plant Monitor</h1>
        <img id="camera" src={`${baseURL}/video_feed`} className="img-fluid" alt="Live Camera Feed" />
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={400}>
            <LineChart>
              <CartesianGrid strokeDasharray="3 3" strokeOpacity={0.5} />
              <XAxis dataKey="Log_Time" stroke="#000000" strokeWidth={2} />
              <YAxis stroke="#000000" strokeWidth={2} />
              <Tooltip />
              <Legend />
              {Object.entries(groupedData).map(([plantId, data]) => (
                <Line
                  key={plantId}
                  type="monotone"
                  dataKey="Greeness"
                  data={data}
                  name={`Plant ${plantId}`}
                  stroke={getRandomColor()}
                  strokeWidth={2}
                  activeDot={{ r: 5 }}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

export default PlantMonitor;