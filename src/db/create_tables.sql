CREATE TABLE Plant(
    PlantID VARCHAR(50) PRIMARY KEY,
    PlantType VARCHAR(50),
    Time_Planted DATETIME
);

CREATE TABLE PlantData(
    PlantID VARCHAR(50),
    Log_Time DATETIME,
    ROI INT,
    ROI_X INT,
    ROI_Y INT,
    Greeness INT,
    Soil_Type VARCHAR(50),
    Light_Type VARCHAR(50),
    Light_Frequency VARCHAR(50),
    Light_Amount VARCHAR(50),
    Water_Type VARCHAR(50),
    Water_Frequency VARCHAR(50),
    Water_Amount VARCHAR(50),
    FOREIGN KEY (PlantId) REFERENCES Plant(PlantId)
);

CREATE TABLE Crop(
    CropId VARCHAR(50) PRIMARY KEY,
    PlantID VARCHAR(50),
    FOREIGN KEY (PlantId) REFERENCES Plant(PlantId)
);

CREATE TABLE ImageData (
    ImageID INT IDENTITY(1,1) PRIMARY KEY,
    CropId VARCHAR(50),
    Log_Time DATETIME,
    Image VARBINARY(MAX),
    FOREIGN KEY (CropId) REFERENCES Crop(CropId)

);

CREATE TABLE CurrentCrops (
    CropId VARCHAR(50) PRIMARY KEY,
    TimePlanted DATETIME
);


