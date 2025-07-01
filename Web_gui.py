// App.jsx
// Dependencies: react, axios, jspdf, tailwindcss

import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { jsPDF } from 'jspdf';

export default function App() {
  const [inputText, setInputText] = useState('');
  const [outputText, setOutputText] = useState('');
  const [originalOutput, setOriginalOutput] = useState('');
  const [theme, setTheme] = useState('light');
  const [searchVisible, setSearchVisible] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const outputRef = useRef(null);

  // Toggle light/dark theme
  const toggleTheme = () => setTheme(prev => prev === 'light' ? 'dark' : 'light');

  // Analyze: call backend to process text
  const handleAnalyze = async () => {
    try {
      const { data } = await axios.post('http://localhost:5000/api/process', { text: inputText });
      setOriginalOutput(data.output);
      setOutputText(data.output);
    } catch (e) {
      console.error(e);
      alert('Error during processing');
    }
  };

  // Highlight placeholders (***) in the output
  const getHighlightedHTML = (text) => {
    return text
      .split('***')
      .map((part, i, arr) => {
        if (i < arr.length - 1) return `${part}<span class=\"bg-yellow-300 font-bold px-0.5\">***</span>`;
        return part;
      })
      .join('');
  };

  // Copy output to clipboard
  const handleCopy = () => navigator.clipboard.writeText(originalOutput);

  // Clear both fields
  const handleClear = () => {
    setInputText('');
    setOriginalOutput('');
    setOutputText('');
  };

  // Save output as .txt
  const handleSaveText = () => {
    const blob = new Blob([originalOutput], { type: 'text/plain' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'output.txt';
    link.click();
  };

  // Export output as PDF
  const handleExportPDF = () => {
    const doc = new jsPDF();
    const lines = doc.splitTextToSize(originalOutput, 180);
    doc.text(lines, 10, 10);
    doc.save('output.pdf');
  };

  // Simulate typing of the output
  const handleSimulateTyping = () => {
    setOutputText('');
    let idx = 0;
    const interval = setInterval(() => {
      setOutputText(prev => prev + originalOutput.charAt(idx));
      idx++;
      if (idx >= originalOutput.length) clearInterval(interval);
    }, 20);
  };

  // Keyboard shortcuts: Ctrl+F to open search, Escape to close
  useEffect(() => {
    const onKeyDown = (e) => {
      if (e.ctrlKey && e.key === 'f') {
        e.preventDefault();
        setSearchVisible(true);
      }
      if (e.key === 'Escape') {
        setSearchVisible(false);
      }
    };
    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
  }, []);

  // Search in output text
  const handleSearch = (e) => {
    if (e.key === 'Enter' && searchTerm) {
      window.find(searchTerm);
    }
  };

  return (
    <div className={theme === 'light' ? 'bg-gray-100 min-h-screen p-4' : 'bg-gray-900 min-h-screen p-4'}>
      <div className={
        `max-w-6xl mx-auto bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 transition-colors`}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <img src="/viatica.png" alt="Logo" className="w-6 h-6" />
            <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">Viatica 1.0 Beta</h1>
          </div>
          <button
            onClick={toggleTheme}
            className="px-3 py-1 bg-gray-200 dark:bg-gray-700 rounded hover:bg-gray-300 dark:hover:bg-gray-600"
          >
            Toggle Theme
          </button>
        </div>

        {/* Toolbar */}
        <div className="flex space-x-2 mb-4">
          <button onClick={handleAnalyze} className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600">Analyze</button>
          <button onClick={handleCopy}   className="px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600">Copy</button>
          <button onClick={handleSimulateTyping} className="px-3 py-1 bg-indigo-500 text-white rounded hover:bg-indigo-600">Sim Typing</button>
          <button onClick={handleSaveText} className="px-3 py-1 bg-yellow-500 text-white rounded hover:bg-yellow-600">Save As</button>
          <button onClick={handleExportPDF} className="px-3 py-1 bg-purple-500 text-white rounded hover:bg-purple-600">Export PDF</button>
          <button onClick={handleClear} className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600">Clear</button>
        </div>

        {/* Main Content: Textareas */}
        <div className="flex space-x-4 h-[500px]">
          {/* Input Side */}
          <div className="flex-1 flex flex-col">
            <label className="mb-2 text-gray-700 dark:text-gray-300">Input Text:</label>
            <textarea
              value={inputText}
              onChange={e => setInputText(e.target.value)}
              className="flex-1 p-2 border rounded resize-none bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
          </div>

          {/* Output Side */}
          <div className="flex-1 flex flex-col relative">
            <label className="mb-2 text-gray-700 dark:text-gray-300">Output Text:</label>
            <div
              ref={outputRef}
              contentEditable
              suppressContentEditableWarning
              className="flex-1 p-2 border rounded overflow-auto bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              dangerouslySetInnerHTML={{ __html: getHighlightedHTML(outputText) }}
            />
            {searchVisible && (
              <input
                type="text"
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
                onKeyDown={handleSearch}
                placeholder="Search (Enter)..."
                className="absolute top-0 right-0 m-2 p-1 border rounded bg-yellow-200 text-gray-900"
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// server.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from new_tester import process  # import your processing function

app = Flask(__name__)
CORS(app)

@app.route('/api/process', methods=['POST'])
def api_process():
    data = request.get_json() or {}
    text = data.get('text', '')
    output = process(text)
    return jsonify({'output': output})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
