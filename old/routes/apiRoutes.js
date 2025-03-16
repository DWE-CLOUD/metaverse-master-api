const express = require('express');
const router = express.Router();
const apiController = require('../controllers/apiController');

// Team 2 - Solaris (Rocket)
router.get('/team2/status', apiController.team2Status);
router.post('/team2/control', apiController.team2Control);

// Team 3 - Healthcare Warehouse
router.get('/team3/status', apiController.team3Status);
router.post('/team3/control', apiController.team3Control);

// Team 4 - Tunnel Rover
router.get('/team4/status', apiController.team4Status);
router.post('/team4/control', apiController.team4Control);

// Team 5 - EEG Brain Simulation
router.get('/team5/data', apiController.team5Data);
router.post('/team5/control', apiController.team5Control);

// Team 6 - Gravity Battery
router.get('/team6/status', apiController.team6Status);
router.post('/team6/control', apiController.team6Control);

// Team 7 - FearTherapy VR
router.get('/team7/session', apiController.team7Session);
router.post('/team7/control', apiController.team7Control);

// Team 8 - Digital Heart Pulse and Blood Flow
router.get('/team8/data', apiController.team8Data);
router.post('/team8/control', apiController.team8Control);

// Team 9 - EarthTwin
router.get('/team9/data', apiController.team9Data);
router.post('/team9/control', apiController.team9Control);

// Team 10 - Remote Surgery Robotic Arm
router.get('/team10/status', apiController.team10Status);
router.post('/team10/control', apiController.team10Control);

// Team 11 - Smart E Yantra Room
router.get('/team11/status', apiController.team11Status);
router.post('/team11/control', apiController.team11Control);

// Team 12 - AI-Based Posture Correction
router.get('/team12/data', apiController.team12Data);
router.post('/team12/control', apiController.team12Control);

// Team 13 - Rescue Twin Rover
router.get('/team13/status', apiController.team13Status);
router.post('/team13/control', apiController.team13Control);

// Team 15 - Metal Detection Rover
router.get('/team15/status', apiController.team15Status);
router.post('/team15/control', apiController.team15Control);

// Team 16 - ICU Ventilator Control System
router.get('/team16/status', apiController.team16Status);
router.post('/team16/control', apiController.team16Control);

module.exports = router;