<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# 

---
##### Starting

##### command to activate venv and start

To activate the virtual environment and start your FastAPI application manually, use these commands:

```bash
cd ~/fastapi-iot
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

Alternatively, if you've set up the systemd service, you can start it with:

```bash
systemctl start fastapi
```

To check the status of your service:

```bash
systemctl status fastapi
```

If you need to restart the service after making changes:

```bash
systemctl restart fastapi
```

And to view the logs:

```bash
journalctl -u fastapi -f
```



# Complete Guide to Building a ThingSpeak-like IoT Platform with FastAPI

This guide will walk you through setting up a ThingSpeak-like IoT platform from scratch using FastAPI on a Linux VPS.

## Step 1: Set Up Your Server Environment

First, update your system and install required packages:

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv -y
```


## Step 2: Create Project Directory and Virtual Environment

```bash
mkdir ~/fastapi-iot
cd ~/fastapi-iot
python3 -m venv venv
source venv/bin/activate
```


## Step 3: Install Required Packages

```bash
pip install fastapi uvicorn python-multipart jinja2 aiofiles
```


## Step 4: Create Directory Structure

```bash
mkdir -p ~/fastapi-iot/static
mkdir -p ~/fastapi-iot/templates
mkdir -p ~/fastapi-iot/data
```


## Step 5: Create the Main Application File

Create a file named `main.py` with the following content:

```bash
nano ~/fastapi-iot/main.py
```

```python
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import json
import os

# Initialize FastAPI
app = FastAPI(title="IoT Analytics Platform", description="ThingSpeak-like API for IoT data")

# Create directories if they don't exist
os.makedirs("static", exist_ok=True)
os.makedirs("data", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="templates")

# Data models
class ChannelField(BaseModel):
    field_id: int
    name: str
    value: float = 0
    last_updated: str = Field(default_factory=lambda: datetime.now().isoformat())

class Channel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    fields: Dict[int, ChannelField] = {}
    metadata: Optional[Dict[str, Any]] = None
    api_key: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    last_entry_id: int = 0
    
    class Config:
        orm_mode = True

class ChannelCreate(BaseModel):
    name: str
    description: Optional[str] = None
    field_names: List[str] = []  # Names for fields 1-8

# In-memory database (replace with a real database in production)
channels_db = {}
data_points_db = {}  # To store historical data

# Save data to file function
def save_data_to_file():
    # Save channels
    with open("data/channels.json", "w") as f:
        channels_json = {k: v.dict() for k, v in channels_db.items()}
        json.dump(channels_json, f)
    
    # Save data points
    with open("data/data_points.json", "w") as f:
        json.dump(data_points_db, f)

# Load data from file function
def load_data_from_file():
    try:
        with open("data/channels.json", "r") as f:
            channels_json = json.load(f)
            for k, v in channels_json.items():
                channels_db[k] = Channel(**v)
    except FileNotFoundError:
        pass  # No saved data yet
    
    try:
        with open("data/data_points.json", "r") as f:
            data_points = json.load(f)
            data_points_db.update(data_points)
    except FileNotFoundError:
        pass  # No saved data yet

# API Endpoints
@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
        <head>
            <title>IoT Analytics Platform</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body { padding: 20px; }
                .container { max-width: 800px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>IoT Analytics Platform</h1>
                <p class="lead">A ThingSpeak-like platform for IoT data collection and visualization</p>
                
                <div class="card mb-4">
                    <div class="card-header">Channels</div>
                    <div class="card-body">
                        <a href="/channels" class="btn btn-primary">View All Channels</a>
                        <a href="/create-channel" class="btn btn-success">Create New Channel</a>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">API Documentation</div>
                    <div class="card-body">
                        <a href="/docs" class="btn btn-info">View API Docs</a>
                    </div>
                </div>
            </div>
        </body>
    </html>
    """

@app.get("/channels", response_class=HTMLResponse)
async def list_channels():
    channels_html = "".join([
        f"""
        <div class="card mb-3">
            <div class="card-header">{channel.name}</div>
            <div class="card-body">
                <p>{channel.description or ""}</p>
                <p><small>Created: {channel.created_at}</small></p>
                <a href="/dashboard/{channel.id}" class="btn btn-primary">View Dashboard</a>
                <a href="/channels/{channel.id}" class="btn btn-info">API Info</a>
            </div>
        </div>
        """ for channel in channels_db.values()
    ])
    
    return f"""
    <html>
        <head>
            <title>Channels - IoT Analytics Platform</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {{ padding: 20px; }}
                .container {{ max-width: 800px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Channels</h1>
                <a href="/" class="btn btn-secondary mb-4">Home</a>
                <a href="/create-channel" class="btn btn-success mb-4">Create New Channel</a>
                
                {channels_html if channels_db else '<div class="alert alert-info">No channels created yet.</div>'}
            </div>
        </body>
    </html>
    """

@app.get("/create-channel", response_class=HTMLResponse)
async def create_channel_form():
    return """
    <html>
        <head>
            <title>Create Channel - IoT Analytics Platform</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body { padding: 20px; }
                .container { max-width: 800px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Create New Channel</h1>
                <a href="/channels" class="btn btn-secondary mb-4">Back to Channels</a>
                
                <div class="card">
                    <div class="card-body">
                        <form action="/channels" method="post">
                            <div class="mb-3">
                                <label for="name" class="form-label">Channel Name</label>
                                <input type="text" class="form-control" id="name" name="name" required>
                            </div>
                            <div class="mb-3">
                                <label for="description" class="form-label">Description</label>
                                <textarea class="form-control" id="description" name="description" rows="3"></textarea>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Fields (up to 8)</label>
                                <div class="row">
                                    <div class="col-md-6 mb-2">
                                        <input type="text" class="form-control" name="field_names" placeholder="Field 1">
                                    </div>
                                    <div class="col-md-6 mb-2">
                                        <input type="text" class="form-control" name="field_names" placeholder="Field 2">
                                    </div>
                                    <div class="col-md-6 mb-2">
                                        <input type="text" class="form-control" name="field_names" placeholder="Field 3">
                                    </div>
                                    <div class="col-md-6 mb-2">
                                        <input type="text" class="form-control" name="field_names" placeholder="Field 4">
                                    </div>
                                    <div class="col-md-6 mb-2">
                                        <input type="text" class="form-control" name="field_names" placeholder="Field 5">
                                    </div>
                                    <div class="col-md-6 mb-2">
                                        <input type="text" class="form-control" name="field_names" placeholder="Field 6">
                                    </div>
                                    <div class="col-md-6 mb-2">
                                        <input type="text" class="form-control" name="field_names" placeholder="Field 7">
                                    </div>
                                    <div class="col-md-6 mb-2">
                                        <input type="text" class="form-control" name="field_names" placeholder="Field 8">
                                    </div>
                                </div>
                            </div>
                            <button type="submit" class="btn btn-primary">Create Channel</button>
                        </form>
                    </div>
                </div>
            </div>
        </body>
    </html>
    """

@app.post("/channels")
async def create_channel_submit(request: Request):
    form_data = await request.form()
    name = form_data.get("name")
    description = form_data.get("description", "")
    field_names = form_data.getlist("field_names")
    
    # Filter out empty field names
    field_names = [f for f in field_names if f]
    
    channel_create = ChannelCreate(
        name=name,
        description=description,
        field_names=field_names
    )
    
    channel = await create_channel_api(channel_create)
    save_data_to_file()
    
    return RedirectResponse(url=f"/dashboard/{channel.id}", status_code=303)

@app.post("/channels/api", response_model=Channel)
async def create_channel_api(channel: ChannelCreate):
    channel_id = str(uuid.uuid4())
    fields = {}
    
    # Create up to 8 fields
    for i, name in enumerate(channel.field_names[:8], 1):
        if name:  # Only create fields with names
            fields[i] = ChannelField(field_id=i, name=name)
    
    new_channel = Channel(
        id=channel_id,
        name=channel.name,
        description=channel.description,
        fields=fields
    )
    
    channels_db[channel_id] = new_channel
    data_points_db[channel_id] = {i: [] for i in fields.keys()}
    
    return new_channel

@app.get("/channels/{channel_id}", response_model=Channel)
async def get_channel(channel_id: str):
    if channel_id not in channels_db:
        raise HTTPException(status_code=404, detail="Channel not found")
    return channels_db[channel_id]

@app.get("/update")
async def update_field(channel_id: str, api_key: str, field1: Optional[float] = None, field2: Optional[float] = None, 
                      field3: Optional[float] = None, field4: Optional[float] = None,
                      field5: Optional[float] = None, field6: Optional[float] = None,
                      field7: Optional[float] = None, field8: Optional[float] = None):
    """Update fields using query parameters (ThingSpeak-compatible)"""
    if channel_id not in channels_db:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    channel = channels_db[channel_id]
    
    if channel.api_key != api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Create a dictionary of field values
    field_values = {}
    for i, value in enumerate([field1, field2, field3, field4, field5, field6, field7, field8], 1):
        if value is not None and i in channel.fields:
            field_values[i] = value
    
    # Update fields
    timestamp = datetime.now().isoformat()
    for field_id, value in field_values.items():
        channel.fields[field_id].value = value
        channel.fields[field_id].last_updated = timestamp
        
        # Store historical data
        if channel_id in data_points_db and field_id in data_points_db[channel_id]:
            data_points_db[channel_id][field_id].append({"value": value, "timestamp": timestamp})
            # Keep only last 100 points for simplicity
            if len(data_points_db[channel_id][field_id]) > 100:
                data_points_db[channel_id][field_id] = data_points_db[channel_id][field_id][-100:]
    
    channel.last_entry_id += 1
    save_data_to_file()
    
    return {"success": True, "entry_id": channel.last_entry_id}

@app.post("/update_multiple")
async def update_multiple_fields(channel_id: str, api_key: str, field_values: Dict[str, float]):
    """Update multiple fields at once using JSON"""
    if channel_id not in channels_db:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    channel = channels_db[channel_id]
    
    if channel.api_key != api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Convert string keys to integers
    numeric_field_values = {int(k): v for k, v in field_values.items() if k.isdigit()}
    
    # Update fields
    timestamp = datetime.now().isoformat()
    for field_id, value in numeric_field_values.items():
        if field_id in channel.fields and field_id <= 8:
            channel.fields[field_id].value = value
            channel.fields[field_id].last_updated = timestamp
            
            # Store historical data
            if channel_id in data_points_db and field_id in data_points_db[channel_id]:
                data_points_db[channel_id][field_id].append({"value": value, "timestamp": timestamp})
                # Keep only last 100 points for simplicity
                if len(data_points_db[channel_id][field_id]) > 100:
                    data_points_db[channel_id][field_id] = data_points_db[channel_id][field_id][-100:]
    
    channel.last_entry_id += 1
    save_data_to_file()
    
    return {"success": True, "entry_id": channel.last_entry_id}

@app.get("/channels/{channel_id}/fields/{field_id}")
async def get_field(channel_id: str, field_id: int):
    if channel_id not in channels_db:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    channel = channels_db[channel_id]
    
    if field_id not in channel.fields:
        raise HTTPException(status_code=404, detail=f"Field {field_id} not found")
    
    return channel.fields[field_id]

@app.get("/channels/{channel_id}/fields/{field_id}/data")
async def get_field_data(channel_id: str, field_id: int, results: int = 10):
    if channel_id not in channels_db:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    if channel_id not in data_points_db or field_id not in data_points_db[channel_id]:
        raise HTTPException(status_code=404, detail=f"No data for field {field_id}")
    
    # Return the last 'results' number of data points
    return data_points_db[channel_id][field_id][-results:]

@app.get("/dashboard/{channel_id}", response_class=HTMLResponse)
async def get_dashboard(request: Request, channel_id: str):
    if channel_id not in channels_db:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    channel = channels_db[channel_id]
    
    return templates.TemplateResponse(
        "dashboard.html", 
        {"request": request, "channel": channel}
    )

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "channels_count": len(channels_db)
    }

# Load data on startup
@app.on_event("startup")
async def startup_event():
    load_data_from_file()
    
    # Add a sample channel if the database is empty
    if not channels_db:
        sample_channel = ChannelCreate(
            name="Temperature Monitor",
            description="A channel for monitoring temperature and humidity",
            field_names=["Temperature", "Humidity", "Pressure", "Battery"]
        )
        channel = await create_channel_api(sample_channel)
        
        # Add some initial data
        timestamp = datetime.now().isoformat()
        for field_id in channel.fields:
            if field_id == 1:  # Temperature
                value = 22.5
            elif field_id == 2:  # Humidity
                value = 45.0
            elif field_id == 3:  # Pressure
                value = 1013.2
            elif field_id == 4:  # Battery
                value = 98.0
            else:
                value = 0
            
            channel.fields[field_id].value = value
            channel.fields[field_id].last_updated = timestamp
            
            # Store historical data
            data_points_db[channel.id][field_id].append({"value": value, "timestamp": timestamp})
        
        channel.last_entry_id = 1
        save_data_to_file()

if __name__ == "__main__":
    import uvicorn```




<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# 

---

# after that what are all the processes

After creating the main.py file, here are the remaining steps to complete your ThingSpeak-like IoT platform:

## Step 6: Create the Dashboard Template

Create a dashboard.html file in the templates directory:

```bash
nano ~/fastapi-iot/templates/dashboard.html
```

Add the following content:

```html
<!DOCTYPE html>
<html>
<head>
    <title>{{ channel.name }} Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { padding: 20px; }
        .container { max-width: 1000px; margin: 0 auto; }
        .chart-container { height: 400px; margin-bottom: 20px; }
        .api-info { background-color: #f8f9fa; padding: 15px; border-radius: 5px; }
        pre { margin: 0; }
        .current-value { font-size: 24px; font-weight: bold; }
        .field-card { transition: all 0.3s ease; }
        .field-card:hover { transform: translateY(-5px); box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ channel.name }}</h1>
        <p class="lead">{{ channel.description }}</p>
        
        <div class="mb-4">
            <a href="/channels" class="btn btn-secondary">Back to Channels</a>
            <button id="refreshBtn" class="btn btn-primary">Refresh Data</button>
        </div>
        
        <div class="row mb-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">Channel Information</div>
                    <div class="card-body">
                        <p><strong>Channel ID:</strong> {{ channel.id }}</p>
                        <p><strong>Created:</strong> {{ channel.created_at }}</p>
                        <p><strong>Last Entry ID:</strong> {{ channel.last_entry_id }}</p>
                        <p><strong>Fields:</strong> {{ channel.fields|length }}</p>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">API Information</div>
                    <div class="card-body api-info">
                        <p><strong>API Key:</strong> {{ channel.api_key }}</p>
                        <p><strong>Update URL:</strong></p>
                        <pre>/update?channel_id={{ channel.id }}&api_key={{ channel.api_key }}&field1=value1&field2=value2</pre>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="card mb-4">
            <div class="card-header">Current Values</div>
            <div class="card-body">
                <div class="row">
                    {% for field_id, field in channel.fields.items() %}
                    <div class="col-md-3 mb-3">
                        <div class="card field-card">
                            <div class="card-body text-center">
                                <h5 class="card-title">{{ field.name }}</h5>
                                <p class="current-value" id="field-{{ field_id }}-value">{{ field.value }}</p>
                                <p class="text-muted"><small>Last updated: <span id="field-{{ field_id }}-updated">{{ field.last_updated }}</span></small></p>
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
        
        {% for field_id, field in channel.fields.items() %}
        <div class="card mb-4">
            <div class="card-header">{{ field.name }} History</div>
            <div class="card-body">
                <div class="chart-container">
                    <canvas id="chart-{{ field_id }}"></canvas>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
    
    <script>
        // Initialize charts
        const charts = {};
        {% for field_id, field in channel.fields.items() %}
        (function() {
            const ctx = document.getElementById('chart-{{ field_id }}').getContext('2d');
            charts[{{ field_id }}] = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: '{{ field.name }}',
                        data: [],
                        borderColor: 'hsl({{ loop.index0 * 45 }}, 70%, 50%)',
                        tension: 0.1,
                        fill: false
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: false
                        },
                        x: {
                            reverse: true
                        }
                    }
                }
            });
            
            // Load initial data
            loadFieldData({{ field_id }});
        })();
        {% endfor %}
        
        // Function to load field data
        async function loadFieldData(fieldId) {
            try {
                const response = await fetch(`/channels/{{ channel.id }}/fields/${fieldId}/data?results=20`);
                const data = await response.json();
                
                if (data && data.length > 0) {
                    // Format timestamps
                    const labels = data.map(point => {
                        const date = new Date(point.timestamp);
                        return date.toLocaleTimeString();
                    });
                    
                    // Extract values
                    const values = data.map(point => point.value);
                    
                    // Update chart
                    charts[fieldId].data.labels = labels;
                    charts[fieldId].data.datasets[0].data = values;
                    charts[fieldId].update();
                }
            } catch (error) {
                console.error(`Error loading data for field ${fieldId}:`, error);
            }
        }
        
        // Refresh data
        document.getElementById('refreshBtn').addEventListener('click', async () => {
            // Refresh channel data
            const response = await fetch('/channels/{{ channel.id }}');
            const channelData = await response.json();
            
            // Update field values
            for (const [fieldId, field] of Object.entries(channelData.fields)) {
                document.getElementById(`field-${fieldId}-value`).textContent = field.value;
                document.getElementById(`field-${fieldId}-updated`).textContent = field.last_updated;
            }
            
            // Refresh charts
            for (const fieldId of Object.keys(channelData.fields)) {
                loadFieldData(parseInt(fieldId));
            }
        });
        
        // Auto-refresh every 30 seconds
        setInterval(() => {
            document.getElementById('refreshBtn').click();
        }, 30000);
    </script>
</body>
</html>
```


## Step 7: Create a Test Device Simulator

Create a script to simulate IoT device data:

```bash
nano ~/fastapi-iot/test_device.py
```

Add the following content:

```python
import requests
import time
import random
import argparse

def simulate_device(channel_id, api_key, interval=5):
    """Simulate an IoT device sending data to the platform"""
    print(f"Starting device simulation for channel {channel_id}")
    print(f"Press Ctrl+C to stop")
    
    base_url = f"http://localhost:8000/update"
    
    try:
        while True:
            # Generate random data
            temperature = 20 + random.uniform(-5, 5)
            humidity = 50 + random.uniform(-10, 10)
            pressure = 1013 + random.uniform(-5, 5)
            battery = min(100, max(0, 95 + random.uniform(-1, 0.5)))
            
            # Send data to the API
            params = {
                "channel_id": channel_id,
                "api_key": api_key,
                "field1": round(temperature, 2),
                "field2": round(humidity, 2),
                "field3": round(pressure, 2),
                "field4": round(battery, 2)
            }
            
            response = requests.get(base_url, params=params)
            
            if response.status_code == 200:
                print(f"Data sent: Temp={params['field1']}°C, Humidity={params['field2']}%, "
                      f"Pressure={params['field3']}hPa, Battery={params['field4']}%")
            else:
                print(f"Error sending data: {response.text}")
            
            # Wait for the specified interval
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("Simulation stopped")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IoT Device Simulator")
    parser.add_argument("channel_id", help="Channel ID to send data to")
    parser.add_argument("api_key", help="API key for the channel")
    parser.add_argument("--interval", type=int, default=5, help="Interval between data points in seconds")
    
    args = parser.parse_args()
    simulate_device(args.channel_id, args.api_key, args.interval)
```


## Step 8: Create a Systemd Service

Create a systemd service file to run your FastAPI application as a background service:

```bash
nano /etc/systemd/system/fastapi.service
```

Add the following content:

```
[Unit]
Description=FastAPI IoT Analytics Platform
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/root/fastapi-iot
ExecStart=/root/fastapi-iot/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
systemctl daemon-reload
systemctl enable fastapi
systemctl start fastapi
```


## Step 9: Configure Nginx as a Reverse Proxy

Install Nginx if not already installed:

```bash
apt install nginx -y
```

Create a Nginx configuration file:

```bash
nano /etc/nginx/sites-available/fastapi
```

Add the following content:

```
server {
    listen 80;
    server_name your_server_ip;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Replace `your_server_ip` with your actual server IP address.

Enable the site and restart Nginx:

```bash
ln -s /etc/nginx/sites-available/fastapi /etc/nginx/sites-enabled/
systemctl restart nginx
```


## Step 10: Test Your IoT Platform

1. Visit your platform at `http://your_server_ip`
2. Create a new channel with fields like "Temperature", "Humidity", "Pressure", and "Battery"
3. Note the Channel ID and API Key from the dashboard
4. Install the requests library for the test device simulator:

```bash
source ~/fastapi-iot/venv/bin/activate
pip install requests
```

5. Run the test device simulator:

```bash
python ~/fastapi-iot/test_device.py YOUR_CHANNEL_ID YOUR_API_KEY --interval 10
```


## Step 11: Secure Your Platform (Optional)

For production use, add SSL to secure your API:

1. Install Certbot:

```bash
apt install certbot python3-certbot-nginx -y
```

2. Generate a certificate (if you have a domain name):

```bash
certbot --nginx -d yourdomain.com
```


## Step 12: Implement Additional Features (Optional)

Consider implementing these additional features to enhance your platform:

1. User authentication
2. Database persistence with PostgreSQL
3. Data export functionality
4. Mobile app integration
5. Alert notifications when values exceed thresholds



