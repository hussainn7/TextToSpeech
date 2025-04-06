exports.handler = async function(event, context) {
  try {
    // Handle POST requests to /process_image
    if (event.httpMethod === 'POST' && event.path === '/.netlify/functions/app/process_image') {
      // For simplicity, just return a mock response
      return {
        statusCode: 200,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Headers': 'Content-Type'
        },
        body: JSON.stringify({
          text: "Sample detected text. The OCR service is running in demo mode in this serverless environment.",
          language: "en"
        })
      };
    }
    
    // Handle OPTIONS requests (CORS preflight)
    if (event.httpMethod === 'OPTIONS') {
      return {
        statusCode: 200,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Headers': 'Content-Type',
          'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
        },
        body: ''
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