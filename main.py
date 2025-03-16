from fastapi import FastAPI, HTTPException, Request, Form, Body, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import json
import os

app = FastAPI(title="IoT Analytics Platform", description="ThingSpeak-like API for IoT data")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
os.makedirs("static", exist_ok=True)
os.makedirs("data", exist_ok=True)
os.makedirs("templates", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

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
    api_key: str = Field(default_factory=lambda: "thinkv_" + str(uuid.uuid4()))
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    last_entry_id: int = 0
    class Config:
        orm_mode = True

class ChannelCreate(BaseModel):
    name: str
    description: Optional[str] = None
    field_names: List[str] = []

channels_db = {}
data_points_db = {}

def save_data_to_file():
    with open("data/channels.json", "w") as f:
        channels_json = {k: v.dict() for k, v in channels_db.items()}
        json.dump(channels_json, f)
    with open("data/data_points.json", "w") as f:
        json.dump(data_points_db, f)

def load_data_from_file():
    try:
        with open("data/channels.json", "r") as f:
            channels_json = json.load(f)
            for k, v in channels_json.items():
                channels_db[k] = Channel(**v)
    except FileNotFoundError:
        pass
    try:
        with open("data/data_points.json", "r") as f:
            data_points = json.load(f)
            data_points_db.update(data_points)
    except FileNotFoundError:
        pass

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
                                    <div class="col-md-6 mb-2"><input type="text" class="form-control" name="field_names" placeholder="Field 1"></div>
                                    <div class="col-md-6 mb-2"><input type="text" class="form-control" name="field_names" placeholder="Field 2"></div>
                                    <div class="col-md-6 mb-2"><input type="text" class="form-control" name="field_names" placeholder="Field 3"></div>
                                    <div class="col-md-6 mb-2"><input type="text" class="form-control" name="field_names" placeholder="Field 4"></div>
                                    <div class="col-md-6 mb-2"><input type="text" class="form-control" name="field_names" placeholder="Field 5"></div>
                                    <div class="col-md-6 mb-2"><input type="text" class="form-control" name="field_names" placeholder="Field 6"></div>
                                    <div class="col-md-6 mb-2"><input type="text" class="form-control" name="field_names" placeholder="Field 7"></div>
                                    <div class="col-md-6 mb-2"><input type="text" class="form-control" name="field_names" placeholder="Field 8"></div>
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
    field_names = [f for f in field_names if f]
    channel_create = ChannelCreate(name=name, description=description, field_names=field_names)
    channel = await create_channel_api(channel_create)
    save_data_to_file()
    return RedirectResponse(url=f"/dashboard/{channel.id}", status_code=303)

@app.post("/channels/api", response_model=Channel)
async def create_channel_api(channel: ChannelCreate):
    channel_id = str(uuid.uuid4())
    fields = {}
    for i, name in enumerate(channel.field_names[:8], 1):
        if name:
            fields[i] = ChannelField(field_id=i, name=name)
    new_channel = Channel(id=channel_id, name=channel.name, description=channel.description, fields=fields)
    channels_db[channel_id] = new_channel
    data_points_db[channel_id] = {i: [] for i in fields.keys()}
    return new_channel

@app.get("/channels/{channel_id}", response_model=Channel)
async def get_channel(channel_id: str):
    if channel_id not in channels_db:
        raise HTTPException(status_code=404, detail="Channel not found")
    return channels_db[channel_id]

@app.get("/update")
async def update_field(channel_id: str, api_key: str, field1: Optional[float] = None, field2: Optional[float] = None, field3: Optional[float] = None, field4: Optional[float] = None, field5: Optional[float] = None, field6: Optional[float] = None, field7: Optional[float] = None, field8: Optional[float] = None):
    if channel_id not in channels_db:
        raise HTTPException(status_code=404, detail="Channel not found")
    channel = channels_db[channel_id]
    if channel.api_key != api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    field_values = {}
    for i, value in enumerate([field1, field2, field3, field4, field5, field6, field7, field8], 1):
        if value is not None and i in channel.fields:
            field_values[i] = value
    timestamp = datetime.now().isoformat()
    for field_id, value in field_values.items():
        channel.fields[field_id].value = value
        channel.fields[field_id].last_updated = timestamp
        if channel_id in data_points_db and field_id in data_points_db[channel_id]:
            data_points_db[channel_id][field_id].append({"value": value, "timestamp": timestamp})
            if len(data_points_db[channel_id][field_id]) > 100:
                data_points_db[channel_id][field_id] = data_points_db[channel_id][field_id][-100:]
    channel.last_entry_id += 1
    save_data_to_file()
    return {"success": True, "entry_id": channel.last_entry_id}

@app.post("/update_multiple")
async def update_multiple_fields(channel_id: str, api_key: str, field_values: Dict[str, float]):
    if channel_id not in channels_db:
        raise HTTPException(status_code=404, detail="Channel not found")
    channel = channels_db[channel_id]
    if channel.api_key != api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    numeric_field_values = {int(k): v for k, v in field_values.items() if k.isdigit()}
    timestamp = datetime.now().isoformat()
    for field_id, value in numeric_field_values.items():
        if field_id in channel.fields and field_id <= 8:
            channel.fields[field_id].value = value
            channel.fields[field_id].last_updated = timestamp
            if channel_id in data_points_db and field_id in data_points_db[channel_id]:
                data_points_db[channel_id][field_id].append({"value": value, "timestamp": timestamp})
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
    return data_points_db[channel_id][field_id][-results:]

@app.get("/dashboard/{channel_id}", response_class=HTMLResponse)
async def get_dashboard(request: Request, channel_id: str):
    if channel_id not in channels_db:
        raise HTTPException(status_code=404, detail="Channel not found")
    channel = channels_db[channel_id]
    return templates.TemplateResponse("dashboard.html", {"request": request, "channel": channel})

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat(), "version": "1.0.0", "channels_count": len(channels_db)}

api_router = APIRouter(prefix="/api/v1")

@api_router.get("/channels/{channel_id}", response_model=Channel)
async def api_get_channel(channel_id: str):
    if channel_id not in channels_db:
        raise HTTPException(status_code=404, detail="Channel not found")
    return channels_db[channel_id]

@api_router.get("/channels/{channel_id}/fields/{field_id}", response_model=ChannelField)
async def api_get_field(channel_id: str, field_id: int):
    if channel_id not in channels_db:
        raise HTTPException(status_code=404, detail="Channel not found")
    channel = channels_db[channel_id]
    if field_id not in channel.fields:
        raise HTTPException(status_code=404, detail="Field not found")
    return channel.fields[field_id]

@api_router.post("/channels/{channel_id}/update/{api_key}")
async def api_update_channel(channel_id: str, api_key: str, update_data: Dict[str, float] = Body(...)):
    if channel_id not in channels_db:
        raise HTTPException(status_code=404, detail="Channel not found")
    channel = channels_db[channel_id]
    if channel.api_key != api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    timestamp = datetime.now().isoformat()
    for key, value in update_data.items():
        try:
            field_num = int(key)
        except ValueError:
            continue
        if field_num in channel.fields:
            channel.fields[field_num].value = value
            channel.fields[field_num].last_updated = timestamp
            if channel_id in data_points_db and field_num in data_points_db[channel_id]:
                data_points_db[channel_id][field_num].append({"value": value, "timestamp": timestamp})
                if len(data_points_db[channel_id][field_num]) > 100:
                    data_points_db[channel_id][field_num] = data_points_db[channel_id][field_num][-100:]
    channel.last_entry_id += 1
    save_data_to_file()
    return {"success": True, "entry_id": channel.last_entry_id}

app.include_router(api_router)

@app.on_event("startup")
async def startup_event():
    load_data_from_file()
    if not channels_db:
        sample_channel = ChannelCreate(name="Temperature Monitor", description="A channel for monitoring temperature and humidity", field_names=["Temperature", "Humidity", "Pressure", "Battery"])
        channel = await create_channel_api(sample_channel)
        timestamp = datetime.now().isoformat()
        for field_id in channel.fields:
            if field_id == 1:
                value = 22.5
            elif field_id == 2:
                value = 45.0
            elif field_id == 3:
                value = 1013.2
            elif field_id == 4:
                value = 98.0
            else:
                value = 0
            channel.fields[field_id].value = value
            channel.fields[field_id].last_updated = timestamp
            data_points_db[channel.id][field_id].append({"value": value, "timestamp": timestamp})
        channel.last_entry_id = 1
        save_data_to_file()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
