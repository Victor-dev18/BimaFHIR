"use client";

import { useState } from "react";
import { UploadCloud, CheckCircle, FileText, Loader2, Download, Edit3, ShieldCheck } from "lucide-react";

export default function Dashboard() {
  const [file, setFile] = useState<File | null>(null);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  
  // States for the Human-in-the-Loop editing
  const [fhirData, setFhirData] = useState<any>(null);
  const [editableJson, setEditableJson] = useState<string>("");
  const [isValidJson, setIsValidJson] = useState<boolean>(true);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const uploadedFile = e.target.files?.[0];
    if (!uploadedFile) return;
    
    setFile(uploadedFile);
    setPdfUrl(URL.createObjectURL(uploadedFile));
    setLoading(true);

    const formData = new FormData();
    formData.append("file", uploadedFile);

    try {
      const res = await fetch("http://127.0.0.1:8000/api/v1/extract", {
        method: "POST",
        body: formData,
      });
      
      const data = await res.json();
      setFhirData(data.fhir_bundle);
      // Format the JSON nicely for the editor
      setEditableJson(JSON.stringify(data.fhir_bundle, null, 2));
      setIsValidJson(true);
    } catch (error) {
      console.error("Extraction failed", error);
      alert("Error extracting data. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  // Human-in-the-loop: Handle live JSON edits
  const handleJsonChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;
    setEditableJson(newValue);
    
    try {
      JSON.parse(newValue);
      setIsValidJson(true);
    } catch (error) {
      setIsValidJson(false); // Warn the user if they break the JSON format
    }
  };

  const handleDownload = () => {
    if (!isValidJson) {
      alert("Please fix the JSON formatting errors before downloading.");
      return;
    }
    const blob = new Blob([editableJson], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "NHCX_InsurancePlan_Bundle.json";
    a.click();
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 p-6 font-sans">
      {/* HEADER */}
      <header className="flex justify-between items-center mb-8 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-2">
            <span className="text-blue-500">Bima</span>FHIR
          </h1>
          <p className="text-slate-400 text-sm mt-1">NHCX Insurance Plan Transformation Engine</p>
        </div>
        
        <div className="flex items-center gap-4">
          <label className="cursor-pointer bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-md flex items-center gap-2 transition-all shadow-lg shadow-blue-500/20">
            <UploadCloud size={20} />
            <span>Upload Policy PDF</span>
            <input type="file" accept=".pdf" className="hidden" onChange={handleFileUpload} />
          </label>
        </div>
      </header>

      {/* MAIN WORKSPACE - SPLIT PANE */}
      <div className="flex gap-6 h-[80vh]">
        
        {/* LEFT PANE: PDF Viewer */}
        <div className="w-1/2 bg-slate-900 border border-slate-800 rounded-lg flex flex-col overflow-hidden shadow-xl">
          <div className="bg-slate-800 p-3 text-sm font-semibold flex items-center gap-2 border-b border-slate-700">
            <FileText size={16} className="text-blue-400"/> Source Document
          </div>
          <div className="flex-1 bg-slate-950 flex items-center justify-center">
            {pdfUrl ? (
              <iframe src={pdfUrl} className="w-full h-full" />
            ) : (
              <div className="text-slate-500 flex flex-col items-center">
                <FileText size={48} className="mb-4 opacity-20" />
                <p>Upload a PDF to begin extraction</p>
              </div>
            )}
          </div>
        </div>

        {/* RIGHT PANE: Human-in-the-Loop Validation Editor */}
        <div className="w-1/2 bg-slate-900 border border-slate-800 rounded-lg flex flex-col shadow-xl">
          <div className="bg-slate-800 p-3 text-sm font-semibold flex justify-between items-center border-b border-slate-700">
            <div className="flex items-center gap-2">
              <Edit3 size={16} className="text-amber-400"/> Human Review & Edit Mode
            </div>
            {fhirData && (
              <button 
                onClick={handleDownload} 
                disabled={!isValidJson}
                className={`text-xs px-3 py-1 rounded text-white flex items-center gap-1 transition-all ${isValidJson ? 'bg-green-600 hover:bg-green-500 shadow-lg shadow-green-500/20' : 'bg-slate-700 cursor-not-allowed text-slate-400'}`}
              >
                <Download size={14} /> Download Final Bundle
              </button>
            )}
          </div>
          
          <div className="flex-1 p-4 flex flex-col">
            {loading ? (
              <div className="flex flex-col items-center justify-center h-full text-blue-400 gap-4">
                <Loader2 size={40} className="animate-spin" />
                <p className="animate-pulse">Groq LPU processing complex tables...</p>
              </div>
            ) : fhirData ? (
              <div className="flex flex-col h-full space-y-4">
                <div className="bg-amber-500/10 border border-amber-500/20 text-amber-400 p-3 rounded text-sm flex items-start gap-2">
                   <ShieldCheck size={18} className="mt-0.5 shrink-0" />
                   <div>
                     <p className="font-semibold text-amber-300">Review Required</p>
                     <p className="text-xs mt-1">Please review the extracted NHCX Bundle below. You can edit the text directly to correct any values before downloading.</p>
                   </div>
                </div>
                
                {/* Editable Code Textarea */}
                <div className="flex-1 relative">
                  <textarea 
                    value={editableJson}
                    onChange={handleJsonChange}
                    className={`w-full h-full p-4 bg-slate-950 border rounded-lg font-mono text-xs text-blue-300 focus:outline-none resize-none ${isValidJson ? 'border-slate-800 focus:border-blue-500' : 'border-red-500 focus:border-red-500'}`}
                    spellCheck={false}
                  />
                  {!isValidJson && (
                    <div className="absolute bottom-4 right-4 bg-red-900/80 text-red-200 px-3 py-1 rounded text-xs border border-red-700">
                      Invalid JSON Format
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-full text-slate-500">
                Waiting for data extraction...
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}