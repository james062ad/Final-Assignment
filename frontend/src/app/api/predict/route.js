export async function POST(request) {
  try {
    const data = await request.json();
    console.log('Proxy received data:', data);
    
    const API_URL = 'https://road-safety-app.onrender.com';
    
    console.log('Sending request to:', `${API_URL}/predict`);
    
    const response = await fetch(`${API_URL}/predict`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Origin': 'https://road-safety-app.vercel.app'
      },
      body: JSON.stringify(data),
      cache: 'no-store'
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('Backend API error:', errorText);
      return new Response(JSON.stringify({ error: `Server error: ${response.status}` }), {
        status: response.status,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    const result = await response.text();
    console.log('Backend API response:', result);
    
    return new Response(result, {
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error) {
    console.error('Proxy error:', error);
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
} 