const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

exports.handler = async function(event, context) {
  try {
    // Return the HTML template directly for GET requests
    if (event.httpMethod === 'GET') {
      const html = fs.readFileSync(path.resolve(__dirname, '../../../templates/index.html'), 'utf8');
      return {
        statusCode: 200,
        headers: {
          'Content-Type': 'text/html',
        },
        body: html
      };
    }
    
    // Handle POST requests to /process_image
    if (event.httpMethod === 'POST' && event.path === '/.netlify/functions/app/process_image') {
      // For simplicity, just return a mock response
      return {
        statusCode: 200,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: "Sample detected text. The Python OCR is not available in this serverless environment.",
          language: "en"
        })
      };
    }
    
    // Handle 404
    return {
      statusCode: 404,
      body: 'Not Found'
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: `Server Error: ${error.toString()}`
    };
  }
}; 