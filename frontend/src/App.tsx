import { useState, ChangeEvent, DragEvent } from 'react'

interface PredictionResult {
  success: boolean;
  prediction: string;
  intervention: string;
  status: string;
  filename: string;
  info: string;
  ai_analysis: {
    description: string;
    how_to_fix: string;
  } | null;
}

function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [language, setLanguage] = useState('English');

  const languages = [
    { name: 'English', native: 'English' },
    { name: 'Hindi', native: 'हिन्दी' },
    { name: 'Marathi', native: 'मराठी' }
  ];

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      processFile(file);
    }
  };

  const processFile = (file: File) => {
    if (!file.type.startsWith('image/')) {
      setError('Please upload a valid image file (PNG, JPG, etc.)');
      return;
    }
    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
    setResult(null);
    setError(null);
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('language', language);

    const apiUrl = import.meta.env.VITE_API_URL || '';

    try {
      const response = await fetch(`${apiUrl}/predict`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to analyze image');
      }

      const data: PredictionResult = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-green-50 py-12 px-4 sm:px-6 lg:px-8 font-sans">
      <div className="max-w-3xl mx-auto">
        <div className="flex justify-end mb-4">
          <div className="flex items-center space-x-2 bg-white px-3 py-1.5 rounded-full shadow-sm border border-green-100">
            <svg className="h-4 w-4 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5h12M9 3v2m1.048 9.5a18.022 18.022 0 01-3.833-5.5m-2.14 1.774a18.091 18.091 0 01-2.457-3.074M18 19l-3-3m0 0l-3 3m3-3V8m0 12a9 9 0 110-18 9 9 0 010 18z" />
            </svg>
            <select 
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="bg-transparent text-sm font-bold text-green-800 focus:outline-none cursor-pointer"
            >
              {languages.map((lang) => (
                <option key={lang.name} value={lang.name}>
                  {lang.native}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="text-center mb-12">
          <h1 className="text-4xl font-extrabold text-green-800 mb-4">
            Crop Health Diagnostics
          </h1>
          <p className="text-lg text-green-600">
            Intelligent Precision Intervention System
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-xl overflow-hidden p-8 border border-green-100">
          <div className="mb-8">
            <label className="block text-sm font-medium text-gray-700 mb-4 text-center">
              Upload or Drag & Drop a clear image of the crop leaf
            </label>
            <div 
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={`mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-dashed rounded-xl transition-all cursor-pointer relative ${
                isDragging ? 'border-green-600 bg-green-50 scale-[1.02]' : 'border-green-300 hover:border-green-500'
              }`}
            >
              <div className="space-y-1 text-center">
                <svg
                  className={`mx-auto h-12 w-12 transition-colors ${isDragging ? 'text-green-600' : 'text-green-400'}`}
                  stroke="currentColor"
                  fill="none"
                  viewBox="0 0 48 48"
                  aria-hidden="true"
                >
                  <path
                    d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                    strokeWidth={2}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
                <div className="flex text-sm text-gray-600 justify-center">
                  <label
                    htmlFor="file-upload"
                    className="relative cursor-pointer bg-white rounded-md font-medium text-green-600 hover:text-green-500 focus-within:outline-none"
                  >
                    <span>Upload a file</span>
                    <input
                      id="file-upload"
                      name="file-upload"
                      type="file"
                      className="sr-only"
                      accept="image/*"
                      onChange={handleFileChange}
                    />
                  </label>
                  <p className="pl-1">or drag and drop</p>
                </div>
                <p className="text-xs text-gray-500">PNG, JPG, GIF up to 10MB</p>
              </div>
            </div>
          </div>

          {previewUrl && (
            <div className="mb-8 flex flex-col items-center">
              <div className="relative group">
                <img
                  src={previewUrl}
                  alt="Preview"
                  className="max-h-64 rounded-lg shadow-md border-2 border-green-200 transition-transform group-hover:scale-[1.01]"
                />
                <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-5 rounded-lg transition-all" />
              </div>
              <button
                onClick={handleUpload}
                disabled={loading}
                className={`mt-6 inline-flex items-center px-8 py-3 border border-transparent text-base font-bold rounded-full shadow-lg text-white ${
                  loading ? 'bg-green-400 cursor-not-allowed' : 'bg-green-600 hover:bg-green-700 active:scale-95'
                } focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-all`}
              >
                {loading ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Analyzing...
                  </>
                ) : (
                  'Run Diagnostics'
                )}
              </button>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-8 rounded-r-lg">
              <div className="flex items-center">
                <svg className="h-5 w-5 text-red-400 mr-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <p className="text-sm text-red-700 font-medium">{error}</p>
              </div>
            </div>
          )}

          {result && (
            <div className={`mt-8 p-6 rounded-xl border-2 transition-all duration-500 animate-in fade-in slide-in-from-bottom-4 ${result.status === 'Healthy' ? 'bg-green-50 border-green-200' : 'bg-yellow-50 border-yellow-200'}`}>
              <div className="flex flex-col md:flex-row gap-8">
                {/* Image Display within Result */}
                <div className="md:w-1/3 flex flex-col items-center">
                  <div className="relative w-full aspect-square rounded-lg overflow-hidden border-2 border-white shadow-md">
                    <img
                      src={previewUrl!}
                      alt="Analyzed Crop"
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <p className="mt-2 text-xs text-gray-500 font-mono italic">{result.filename}</p>
                </div>

                {/* Information Content */}
                <div className="md:w-2/3 space-y-4">
                  <h3 className={`text-xl font-bold flex items-center ${result.status === 'Healthy' ? 'text-green-800' : 'text-yellow-800'}`}>
                    {result.status === 'Healthy' ? (
                      <svg className="h-6 w-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    ) : (
                      <svg className="h-6 w-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                    )}
                    Diagnostic Results
                  </h3>

                  <div className="flex justify-between items-center pb-2 border-b border-gray-200">
                    <span className="text-gray-600 font-medium">Status</span>
                    <span className={`px-4 py-1 rounded-full text-sm font-black tracking-wide uppercase ${result.status === 'Healthy' ? 'bg-green-200 text-green-900' : 'bg-yellow-200 text-yellow-900'}`}>
                      {result.status}
                    </span>
                  </div>

                  <div className="flex justify-between items-center pb-2 border-b border-gray-200">
                    <span className="text-gray-600 font-medium">Prediction</span>
                    <span className="text-gray-900 font-bold capitalize text-lg">
                      {result.prediction.replace(/___/g, ' ').replace(/_/g, ' ')}
                    </span>
                  </div>

                  <div>
                    <span className="text-gray-600 font-medium block mb-2">Disease Information</span>
                    <div className="text-gray-800 bg-white p-4 rounded-lg border border-gray-100 shadow-inner leading-relaxed text-sm">
                      {result.info}
                    </div>
                  </div>

                  <div>
                    <span className="text-gray-600 font-medium block mb-2 mt-4">How to Fix (Intervention Plan)</span>
                    <div className="text-gray-800 bg-green-50 p-4 rounded-lg border border-green-100 shadow-inner leading-relaxed text-sm italic">
                      <ul className="list-disc pl-5 space-y-1">
                        {result.intervention.split('. ').map((step, index) => (
                          <li key={index}>{step.endsWith('.') ? step : step + '.'}</li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  {/* New AI Analysis Section */}
                  <div className="mt-8 pt-6 border-t border-gray-200">
                    <div className="flex items-center mb-4">
                      <div className="bg-purple-100 p-2 rounded-lg mr-3">
                        <svg className="h-5 w-5 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                      </div>
                      <h4 className="text-lg font-bold text-purple-900">AI Expert Diagnostic Insights</h4>
                    </div>
                    
                    <div className="bg-gradient-to-br from-purple-50 to-white p-5 rounded-xl border border-purple-100 shadow-sm relative overflow-hidden">
                      <div className="absolute top-0 right-0 p-2 opacity-10">
                        <svg className="h-16 w-16 text-purple-900" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"></path>
                        </svg>
                      </div>

                      {result.ai_analysis && (
                        <div className="text-gray-700 text-sm leading-relaxed space-y-4 relative z-10">
                          <p className="text-xs text-purple-700 font-black uppercase tracking-widest mb-2 flex items-center">
                            <span className="h-px w-4 bg-purple-300 mr-2"></span>
                            AI Analysis Complete
                          </p>
                          
                          <div>
                            <p className="font-extrabold text-purple-900 mb-1 flex items-center">
                              Expert Summary
                            </p>
                            <p className="pl-3 border-l-2 border-purple-400 text-gray-800 italic">{result.ai_analysis.description}</p>
                          </div>
                          
                          <div className="mt-4">
                            <p className="font-extrabold text-purple-900 mb-2 flex items-center">
                              Strategic Intervention Path
                            </p>
                            <ul className="grid grid-cols-1 gap-2">
                              {result.ai_analysis.how_to_fix.split('. ').map((step, index) => (
                                step.trim() && (
                                  <li key={index} className="flex items-start bg-white/50 p-2 rounded-lg border border-purple-50 hover:border-purple-200 transition-colors">
                                    <span className="flex-shrink-0 w-6 h-6 rounded-md bg-purple-600 text-white flex items-center justify-center text-[10px] font-bold mr-3 shadow-sm">
                                      {index + 1}
                                    </span>
                                    <span className="text-gray-700 font-medium">{step.endsWith('.') ? step : step + '.'}</span>
                                  </li>
                                )
                              ))}
                            </ul>
                          </div>
                        </div>
                      )}
                      
                      {!result.ai_analysis && result.status !== 'Healthy' && (
                        <div className="text-center py-6 text-purple-800 italic">
                          <p>Consulting our AI expert pathologist for additional insights on {result.prediction.replace(/___/g, ' ').replace(/_/g, ' ')}...</p>
                        </div>
                      )}

                      {!result.ai_analysis && result.status === 'Healthy' && (
                        <div className="text-center py-6 text-green-800 italic">
                          <p>Plant is in excellent health. No additional deep analysis required.</p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="mt-12 text-center text-green-700 opacity-60">
          <p>© 2026 Intelligent Crop Health Systems</p>
        </div>
      </div>
    </div>
  );
}

export default App;
