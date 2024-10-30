import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';
import { Helmet } from 'react-helmet';

console.log("here")
// const baseURL = process.env.NODE_ENV === 'production'
//   ? process.env.REACT_APP_PROD_API_URL
//   : process.env.REACT_APP_LOCAL_API_URL;

const baseURL = process.env.REACT_APP_API_URL;

function App() {
  const [crops, setCrops] = useState([]);
  const [plants, setPlants] = useState([]);
  const [newCropId, setNewCropId] = useState('');
  const [selectedCropId, setSelectedCropId] = useState('');
  const [newPlantId, setNewPlantId] = useState('');
  const [newPlantType, setNewPlantType] = useState('');
  const [newPlantedTime, setNewPlantedTime] = useState('');
  const [newPlantDescription, setNewPlantDescription] = useState('');

  useEffect(() => {
    fetchCrops();
  }, []);

  useEffect(() => {
    fetchPlants();
  }, []);

  const fetchCrops = () => {
    console.log("Base URL: ", baseURL);
    axios.get(`${baseURL}/api/crops`)
      .then(response => {
        console.log("Crops data:", response.data);
        setCrops(response.data);
      })
      .catch(error => {
        console.error("Error fetching crop data:", error);
        setCrops([]); // Set crops to an empty array in case of an error
      });
  }
  
  const fetchPlants = () => {
    console.log("Base URL: ", baseURL);
    axios.get(`${baseURL}/api/plants`)
      .then(response => {
        setPlants(response.data);
      })
      .catch(error => {
        console.error("Error fetching plant data:", error);
        setPlants([]); // Set plants to an empty array in case of an error
      });
  }


  const handleDeletePlant = (cropId, plantId) => {
    axios.delete(`${baseURL}/api/crops/${cropId}/plants/${plantId}`)
      .then(response => {
        if (response.status === 200) {
          fetchCrops(); // Reload crops to reflect the changes
        }
      })
      .catch(error => {
        if (error.response && error.response.status === 404) {
          console.error("Plant not found:", error.response.data);
          // Display an error message to the user
          alert("The selected plant could not be found. It may have already been deleted.");
        } else {
          console.error("Error deleting plant:", error);
          // Display a generic error message to the user
          alert("An error occurred while deleting the plant. Please try again later.");
        }
      });
  }

  const handleCreateCrop = (event) => {
    event.preventDefault();
    if (!newCropId) {
      console.error("Crop ID is required.");
      return;
    }

    const url = `${baseURL}/api/crops`;
    const cropData = { cropId: newCropId, plantedTime: newPlantedTime};


    axios.post(url,cropData )
      .then(response => {
        console.log("Crop created:", response.data);
        fetchCrops();
        setNewCropId('');
        setNewPlantedTime('');
      })
      .catch(error => {
        console.error("Error creating crop:", error.response?.data?.message || error.message);
      });
  }

  const handleAddPlant = (event) => {
    event.preventDefault();
    if (!selectedCropId) {
      console.error("No crop selected for the plant.");
      return;
    }
  
    const url = `${baseURL}/api/crops/${selectedCropId}/plants`;
    const plantData = {
      plantId: newPlantId,
      plantType: newPlantType,
      description: newPlantDescription  // Ensure this matches the backend expected data key
    };
  
    axios.post(url, plantData)
      .then(response => {
        console.log("Plant added:", response.data);
        fetchCrops();
        fetchPlants();
        setNewPlantId('');
        setNewPlantType('');
        setNewPlantDescription('');  // Clear the description input field after submission
      })
      .catch(error => {
        console.error("Error adding plant:", error.response?.data?.message || error.message);
      });
  }
  

  return (
    <div className="App">
      <Helmet>
        <meta charSet="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Crop Manager</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"
          crossOrigin="anonymous" />
      </Helmet>

      <div className="container">
      <h1>Crop Management</h1>
        <table className="table">
          <thead>
            <tr>
              <th>Crop ID</th>
              <th>Plant ID</th>
              <th>Plant Type</th>
              <th>Plant Description</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
          {plants && plants.map(crop =>
            crop.plants && crop.plants.map(plant => (
              <tr key={plant.id}>
                <td>{crop.id}</td>
                <td>{plant.id}</td>
                <td>{plant.type}</td>
                <td>{plant.description}</td>
                <td>
                  <button className="btn btn-danger" onClick={() => handleDeletePlant(crop.id, plant.id)}>
                    Delete
                  </button>
                </td>
              </tr>
            ))
          )}
        </tbody>
        </table>

        <hr/>

        <h2>Create New Crop</h2>
        <form onSubmit={handleCreateCrop}>
          <div className="form-group">
            <label htmlFor="cropId">Crop ID:</label>
            <input
              type="text"
              className="form-control"
              id="cropId"
              value={newCropId}
              onChange={e => setNewCropId(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="plantedTime">Planted Time:</label>
            <input
              type="datetime-local"
              className="form-control"
              id="plantedTime"
              value={newPlantedTime}
              onChange={e => setNewPlantedTime(e.target.value)}
              required
            />
          </div>
          <button type="submit" className="btn btn-primary">Create Crop</button>
        </form>

        <hr/>

        <h2>Add Plant to Crop</h2>
        <form onSubmit={handleAddPlant}>
          <div className="form-group">
            <label htmlFor="cropSelect">Select Crop:</label>
                      <select
            className="form-control"
            id="cropSelect"
            value={selectedCropId}
            onChange={e => setSelectedCropId(e.target.value)}
          >
            <option value="">Select a crop</option>
            {crops && crops.map((cropId, index) => (
              <option key={index} value={cropId}>{cropId}</option>
            ))}
          </select>
          </div>
          <div className="form-group">
            <label htmlFor="plantId">Plant ID:</label>
            <input
              type="text"
              className="form-control"
              id="plantId"
              value={newPlantId}
              onChange={e => setNewPlantId(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="plantType">Plant Type:</label>
            <input
              type="text"
              className="form-control"
              id="plantType"
              value={newPlantType}
              onChange={e => setNewPlantType(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
          <label htmlFor="plantDescription">Plant Description:</label>
          <input
            type="text"
            className="form-control"
            id="plantDescription"
            value={newPlantDescription}
            onChange={e => setNewPlantDescription(e.target.value)}
            required
          />
        </div>

          
          <button type="submit" className="btn btn-primary">Add Plant</button>
        </form>
      </div>
    </div>
  );
}

export default App;


