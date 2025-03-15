// controllers/apiController.js

// Team 2 - Solaris (Rocket)
exports.team2Status = (req, res) => {
    res.json({ status: "success", data: { rocket_status: "ready" } });
};

exports.team2Control = (req, res) => {
    const { action } = req.body;
    res.json({ status: "success", data: { action_performed: action } });
};

// Team 3 - Healthcare Warehouse
exports.team3Status = (req, res) => {
    res.json({ status: "success", data: { robot_status: "idle" } });
};

exports.team3Control = (req, res) => {
    const { action } = req.body;
    res.json({ status: "success", data: { action_performed: action } });
};

// Team 4 - Tunnel Rover
exports.team4Status = (req, res) => {
    res.json({ status: "success", data: { rover_status: "active" } });
};

exports.team4Control = (req, res) => {
    const { action } = req.body;
    res.json({ status: "success", data: { action_performed: action } });
};

// Team 5 - EEG Brain Simulation
exports.team5Data = (req, res) => {
    res.json({ status: "success", data: { eeg_activity: "normal" } });
};

exports.team5Control = (req, res) => {
    const { action } = req.body;
    res.json({ status: "success", data: { action_performed: action } });
};

// Team 6 - Gravity Battery
exports.team6Status = (req, res) => {
    res.json({ status: "success", data: { battery_status: "charged" } });
};

exports.team6Control = (req, res) => {
    const { action } = req.body;
    res.json({ status: "success", data: { action_performed: action } });
};

// Team 7 - FearTherapy VR
exports.team7Session = (req, res) => {
    res.json({ status: "success", data: { session_status: "in_progress" } });
};

exports.team7Control = (req, res) => {
    const { action } = req.body;
    res.json({ status: "success", data: { action_performed: action } });
};

// Team 8 - Digital Heart Pulse and Blood Flow
exports.team8Data = (req, res) => {
    res.json({ status: "success", data: { heart_rate: "72bpm", blood_pressure: "120/80" } });
};

exports.team8Control = (req, res) => {
    const { action } = req.body;
    res.json({ status: "success", data: { action_performed: action } });
};

// Team 9 - EarthTwin
exports.team9Data = (req, res) => {
    res.json({ status: "success", data: { earth_model: "stable" } });
};

exports.team9Control = (req, res) => {
    const { action } = req.body;
    res.json({ status: "success", data: { action_performed: action } });
};

// Team 10 - Remote Surgery Robotic Arm
exports.team10Status = (req, res) => {
    res.json({ status: "success", data: { arm_status: "standby" } });
};

exports.team10Control = (req, res) => {
    const { action } = req.body;
    res.json({ status: "success", data: { action_performed: action } });
};

// Team 11 - Smart E Yantra Room
exports.team11Status = (req, res) => {
    res.json({ status: "success", data: { room_status: "online" } });
};

exports.team11Control = (req, res) => {
    const { action } = req.body;
    res.json({ status: "success", data: { action_performed: action } });
};

// Team 12 - AI-Based Posture Correction
exports.team12Data = (req, res) => {
    res.json({ status: "success", data: { posture: "good" } });
};

exports.team12Control = (req, res) => {
    const { action } = req.body;
    res.json({ status: "success", data: { action_performed: action } });
};

// Team 13 - Rescue Twin Rover
exports.team13Status = (req, res) => {
    res.json({ status: "success", data: { rover_status: "searching" } });
};

exports.team13Control = (req, res) => {
    const { action } = req.body;
    res.json({ status: "success", data: { action_performed: action } });
};

// Team 15 - Metal Detection Rover
exports.team15Status = (req, res) => {
    res.json({ status: "success", data: { rover_status: "scanning" } });
};

exports.team15Control = (req, res) => {
    const { action } = req.body;
    res.json({ status: "success", data: { action_performed: action } });
};

// Team 16 - ICU Ventilator Control System
exports.team16Status = (req, res) => {
    res.json({ status: "success", data: { ventilator_status: "normal" } });
};

exports.team16Control = (req, res) => {
    const { action } = req.body;
    res.json({ status: "success", data: { action_performed: action } });
};