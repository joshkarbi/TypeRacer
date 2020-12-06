const express = require('express');
const { time, error } = require('console');

const app = express()
const port = 80

// Serve the front-end static files.
app.use('/', express.static('static'));

app.listen(port, () => {
	  console.log(`Listening at http://localhost:${port}`)
})