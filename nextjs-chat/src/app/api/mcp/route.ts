import { NextResponse } from 'next/server';

// This API route acts as a proxy to the Python backend.
// This is a common pattern to avoid CORS issues and to keep the backend URL private.
const PYTHON_API_URL = 'http://localhost:5001/api/mcp';

export async function GET() {
  try {
    const response = await fetch(PYTHON_API_URL, {
        // Use 'no-cache' to ensure we always get the latest data from the backend
        cache: 'no-cache',
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch data from Python API: ${response.statusText}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
    
  } catch (error: any) {
    console.error("Error fetching from Python API:", error);
    // Return a structured error response
    return NextResponse.json(
        { error: 'Failed to fetch data from backend service.', details: error.message },
        { status: 500 }
    );
  }
}
