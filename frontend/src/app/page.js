'use client';

import { useState } from 'react';
import axios from 'axios';

const getRiskBreakdown = (prediction) => {
  const factors = {
    road: prediction.risk_factors.some(f => f.includes('road') || f.includes('Urban')) ? 1 : 0,
    weather: prediction.risk_factors.some(f => f.includes('weather') || f.includes('Rain') || f.includes('Snow') || f.includes('Fog')) ? 1 : 0,
    speed: prediction.risk_factors.some(f => f.includes('speed')) ? 1 : 0,
    visibility: prediction.risk_factors.some(f => f.includes('visibility') || f.includes('Night')) ? 1 : 0,
    junction: prediction.risk_factors.some(f => f.includes('junction')) ? 1 : 0
  };
  
  return factors;
};

const getFactorSeverity = (probability) => {
  const prob = parseFloat(probability);
  if (prob >= 70) return 'High';
  if (prob >= 40) return 'Medium';
  return 'Low';
};

export default function Home() {
  const [formData, setFormData] = useState({
    road_type: 1,
    weather_conditions: 'Fine',
    speed_limit: 20,
    time_of_day: 'Afternoon',
    junction_detail: 'Not at junction'
  });

  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      console.log('Sending data:', formData);
      const response = await axios.post('http://127.0.0.1:5000/api/predict', formData);
      console.log('API Response:', response.data);
      setPrediction(response.data.prediction);
    } catch (err) {
      console.error('API Error:', err);
      setError(
        err.response?.data?.details 
          ? `Validation error: ${JSON.stringify(err.response.data.details)}`
          : err.response?.data?.error 
          ? err.response.data.error
          : 'An error occurred while making the prediction. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'road_type' || name === 'speed_limit' ? parseInt(value, 10) : value
    }));
  };

  const getRiskColor = (probability) => {
    const prob = parseFloat(probability);
    if (prob >= 70) return 'red';
    if (prob >= 40) return 'orange';
    return 'green';
  };

  const renderRiskMeter = (probability) => {
    const prob = parseFloat(probability);
    return (
      <div className="w-full h-4 bg-gray-200 rounded-full overflow-hidden">
        <div 
          className={`h-full transition-all duration-500 ${
            prob >= 70 ? 'bg-red-500' :
            prob >= 40 ? 'bg-orange-500' :
            'bg-green-500'
          }`}
          style={{ width: `${prob}%` }}
        />
      </div>
    );
  };

  const handlePrint = () => {
    window.print();
  };

  const handleExport = () => {
    const timestamp = new Date().toLocaleString().replace(/[/\\?%*:|"<>]/g, '-');
    const data = {
      timestamp,
      assessment: {
        inputs: formData,
        results: prediction
      }
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `risk-assessment-${timestamp}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const renderRiskBreakdown = (prediction) => {
    const factors = getRiskBreakdown(prediction);
    const severity = getFactorSeverity(prediction.probability);
    
    return (
      <div className="grid grid-cols-5 gap-2 print:gap-4">
        {Object.entries(factors).map(([factor, value]) => (
          <div key={factor} className="text-center">
            <div className={`h-20 relative rounded-lg border ${
              value ? 'bg-red-50 border-red-200' : 'bg-green-50 border-green-200'
            }`}>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className={`text-2xl ${value ? 'text-red-500' : 'text-green-500'}`}>
                  {value ? '⚠️' : '✓'}
                </span>
              </div>
            </div>
            <span className="text-sm font-medium text-gray-600 capitalize mt-1 block">
              {factor}
            </span>
          </div>
        ))}
      </div>
    );
  };

  const renderTrendIndicator = (probability) => {
    const prob = parseFloat(probability);
    const angle = (prob / 100) * 180 - 90;
    
    return (
      <div className="relative h-32 w-32 mx-auto print:hidden">
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-24 h-24 rounded-full border-4 border-gray-200">
            <div 
              className="w-1 h-12 bg-blue-600 origin-bottom transform transition-transform duration-700"
              style={{ 
                position: 'absolute',
                bottom: '50%',
                left: 'calc(50% - 2px)',
                transformOrigin: 'bottom',
                transform: `rotate(${angle}deg)`
              }}
            />
          </div>
          <div className="absolute bottom-0 w-full text-center text-sm font-medium text-gray-600">
            {probability}
          </div>
        </div>
        <div className="absolute top-0 left-0 w-full text-center text-xs text-gray-500">High</div>
        <div className="absolute bottom-0 left-0 text-xs text-gray-500">Low</div>
        <div className="absolute bottom-0 right-0 text-xs text-gray-500">High</div>
      </div>
    );
  };

  return (
    <main className="min-h-screen p-8 bg-gradient-to-b from-gray-50 to-white print:bg-white print:p-0">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-800 mb-2 tracking-tight">
            Road Safety Risk Assessment
          </h1>
          <p className="text-gray-600 text-lg font-light">Make informed decisions about road safety conditions</p>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-8 print:shadow-none">
          <form onSubmit={handleSubmit} className="space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {/* Road Type */}
              <div className="space-y-2">
                <label className="block text-sm font-semibold text-gray-700 mb-1">Road Type</label>
                <div className="relative">
                  <select
                    name="road_type"
                    value={formData.road_type}
                    onChange={handleInputChange}
                    className="block w-full px-4 py-3 rounded-lg border-gray-200 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 bg-white shadow-sm transition-colors duration-200 ease-in-out"
                  >
                    <option value="1">Residential</option>
                    <option value="2">A Road</option>
                    <option value="3">B Road</option>
                    <option value="6">Urban</option>
                  </select>
                  <div className="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
                    <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </div>
              </div>

              {/* Weather Conditions */}
              <div className="space-y-2">
                <label className="block text-sm font-semibold text-gray-700 mb-1">Weather Conditions</label>
                <div className="relative">
                  <select
                    name="weather_conditions"
                    value={formData.weather_conditions}
                    onChange={handleInputChange}
                    className="block w-full px-4 py-3 rounded-lg border-gray-200 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 bg-white shadow-sm transition-colors duration-200 ease-in-out"
                  >
                    <option value="Fine">Fine</option>
                    <option value="Rain">Rain</option>
                    <option value="Snow">Snow</option>
                    <option value="Fog">Fog</option>
                  </select>
                  <div className="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
                    <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </div>
              </div>

              {/* Speed Limit */}
              <div className="space-y-2">
                <label className="block text-sm font-semibold text-gray-700 mb-1">Speed Limit</label>
                <div className="relative">
                  <select
                    name="speed_limit"
                    value={formData.speed_limit}
                    onChange={handleInputChange}
                    className="block w-full px-4 py-3 rounded-lg border-gray-200 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 bg-white shadow-sm transition-colors duration-200 ease-in-out"
                  >
                    <option value="20">20 mph</option>
                    <option value="30">30 mph</option>
                    <option value="40">40 mph</option>
                    <option value="50">50 mph</option>
                    <option value="60">60 mph</option>
                    <option value="70">70 mph</option>
                  </select>
                  <div className="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
                    <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </div>
              </div>

              {/* Time of Day */}
              <div className="space-y-2">
                <label className="block text-sm font-semibold text-gray-700 mb-1">Time of Day</label>
                <div className="relative">
                  <select
                    name="time_of_day"
                    value={formData.time_of_day}
                    onChange={handleInputChange}
                    className="block w-full px-4 py-3 rounded-lg border-gray-200 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 bg-white shadow-sm transition-colors duration-200 ease-in-out"
                  >
                    <option value="Morning">Morning</option>
                    <option value="Afternoon">Afternoon</option>
                    <option value="Evening">Evening</option>
                    <option value="Night">Night</option>
                  </select>
                  <div className="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
                    <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </div>
              </div>

              {/* Junction Detail */}
              <div className="space-y-2">
                <label className="block text-sm font-semibold text-gray-700 mb-1">Junction Detail</label>
                <div className="relative">
                  <select
                    name="junction_detail"
                    value={formData.junction_detail}
                    onChange={handleInputChange}
                    className="block w-full px-4 py-3 rounded-lg border-gray-200 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 bg-white shadow-sm transition-colors duration-200 ease-in-out"
                  >
                    <option value="Not at junction">Not at junction</option>
                    <option value="T Junction">T Junction</option>
                    <option value="Crossroads">Crossroads</option>
                    <option value="Roundabout">Roundabout</option>
                  </select>
                  <div className="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
                    <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex justify-center pt-4">
              <button
                type="submit"
                disabled={loading}
                className="px-8 py-3 bg-blue-600 text-white text-lg font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 transition-colors duration-200 ease-in-out shadow-sm"
              >
                {loading ? 'Analyzing...' : 'Assess Risk'}
              </button>
            </div>
          </form>

          {error && (
            <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-600">{error}</p>
            </div>
          )}

          {prediction && !error && (
            <div className="mt-6 space-y-6">
              {/* Export/Print Controls - Hidden in Print */}
              <div className="flex justify-end space-x-4 print:hidden">
                <button
                  onClick={handlePrint}
                  className="inline-flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
                >
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
                  </svg>
                  Print Report
                </button>
                <button
                  onClick={handleExport}
                  className="inline-flex items-center px-4 py-2 bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                >
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  Export JSON
                </button>
              </div>

              {/* Print Header - Only visible in Print */}
              <div className="hidden print:block mb-8">
                <div className="text-sm text-gray-500 mb-2">
                  Generated on: {new Date().toLocaleString()}
                </div>
                <div className="text-sm text-gray-500">
                  Assessment ID: {Math.random().toString(36).substr(2, 9).toUpperCase()}
                </div>
              </div>

              {/* Results Section */}
              <div className="bg-gray-50 border border-gray-200 rounded-md p-6 print:bg-white">
                <h2 className="text-xl font-bold mb-6 text-gray-800">Risk Assessment Results</h2>
                
                {/* Risk Level and Probability Section */}
                <div className="space-y-6 mb-8">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <div className="flex items-center justify-between mb-4">
                        <span className="font-medium text-lg">Risk Level:</span>
                        <span className={`px-4 py-2 rounded-full text-sm font-semibold ${
                          prediction.risk_level === 'High Risk' ? 'bg-red-100 text-red-800' :
                          prediction.risk_level === 'Medium Risk' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {prediction.risk_level || 'Unknown'}
                        </span>
                      </div>
                      {renderRiskMeter(prediction.probability.replace('%', ''))}
                    </div>
                    <div>
                      {renderTrendIndicator(prediction.probability.replace('%', ''))}
                    </div>
                  </div>
                </div>

                {/* Risk Factor Breakdown */}
                <div className="mb-8">
                  <h3 className="font-semibold text-lg mb-4 text-gray-800">Risk Factor Analysis</h3>
                  {renderRiskBreakdown(prediction)}
                </div>

                {/* Risk Factors Section */}
                {prediction.risk_factors && prediction.risk_factors.length > 0 && (
                  <div className="mb-6 print:mb-8">
                    <h3 className="font-semibold text-lg mb-3 text-gray-800">Risk Factors</h3>
                    <div className="bg-white rounded-lg border border-gray-200 p-4 print:bg-gray-50">
                      <ul className="space-y-2">
                        {prediction.risk_factors.map((factor, index) => (
                          <li key={index} className="flex items-start">
                            <span className="inline-block w-2 h-2 mt-2 mr-2 bg-red-500 rounded-full print:border print:border-red-500" />
                            <span className="text-gray-700">{factor}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}

                {/* Recommendations Section */}
                {prediction.recommendations && prediction.recommendations.length > 0 && (
                  <div className="print:mb-8">
                    <h3 className="font-semibold text-lg mb-3 text-gray-800">Recommendations</h3>
                    <div className="bg-white rounded-lg border border-gray-200 p-4 print:bg-gray-50">
                      <ul className="space-y-2">
                        {prediction.recommendations.map((recommendation, index) => (
                          <li key={index} className="flex items-start">
                            <span className="inline-block w-4 h-4 mt-1 mr-2 print:hidden">
                              <svg className="w-4 h-4 text-blue-500" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                              </svg>
                            </span>
                            <span className="hidden print:inline-block print:mr-2">•</span>
                            <span className="text-gray-700">{recommendation}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}

                {/* Print Footer - Only visible in Print */}
                <div className="hidden print:block mt-8 pt-8 border-t border-gray-200 text-sm text-gray-500">
                  <p>This report was generated by the Road Safety Risk Assessment System.</p>
                  <p>For more information or questions about this assessment, please contact support.</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
