// index.js
const express = require('express');
const cors = require('cors');
require('dotenv').config();

const apiRoutes = require('./routes/apiRoutes');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// API Routes
app.use('/v1', apiRoutes);

// Root endpoint
app.get('/', (req, res) => {
    res.json({ status: 'success', message: 'Metaverse Master API is running.' });
});

// Start server
app.listen(PORT, () => {
    console.log(`API running on port ${PORT}`);
});