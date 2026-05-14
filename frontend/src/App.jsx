import { predictRisk } from "./api";
import React, { useState, useEffect } from 'react';
import {
  Brain, Activity, Mic, HeartPulse, Stethoscope,
  Bug, LayoutDashboard, User, UploadCloud, LogOut,
  CheckCircle2, ShieldAlert, FlaskConical, Shield,
  TrendingUp, Lightbulb, FileText, Settings
} from 'lucide-react';
import {
  Radar, RadarChart, PolarGrid, PolarAngleAxis, ResponsiveContainer,
  PieChart, Pie, Cell, Tooltip,
  LineChart, Line, XAxis, YAxis, CartesianGrid
} from 'recharts';

// --- DATA MOCKS ---
const radarData = [
  { subject: 'Microbiome', A: 72, fullMark: 100 },
  { subject: 'Voice', A: 68, fullMark: 100 },
  { subject: 'Autonomic (HRV)', A: 65, fullMark: 100 },
  { subject: 'Inflammation', A: 70, fullMark: 100 },
  { subject: 'AMR', A: 60, fullMark: 100 },
];

const microbiomeData = [
  { name: 'Prevotella', value: 18.2, color: '#3b82f6' },
  { name: 'Bacteroides', value: 15.6, color: '#06b6d4' },
  { name: 'Faecalibacterium', value: 12.8, color: '#eab308' },
  { name: 'Akkermansia', value: 8.7, color: '#a855f7' },
  { name: 'Bifidobacterium', value: 7.1, color: '#ef4444' },
  { name: 'Others', value: 37.6, color: '#64748b' },
];

const trendData = [
  { date: '01 May', microbiome: 65, voice: 55, autonomic: 60, inflammation: 62, amr: 50 },
  { date: '08 May', microbiome: 68, voice: 58, autonomic: 62, inflammation: 65, amr: 52 },
  { date: '15 May', microbiome: 75, voice: 62, autonomic: 68, inflammation: 72, amr: 55 },
  { date: '22 May', microbiome: 78, voice: 65, autonomic: 64, inflammation: 75, amr: 58 },
  { date: '29 May', microbiome: 75, voice: 64, autonomic: 63, inflammation: 71, amr: 59 },
  { date: '05 Jun', microbiome: 72, voice: 68, autonomic: 65, inflammation: 70, amr: 60 },
];

// --- SIDEBAR MENU CONFIGURATION ---
const menuItems = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'profile', label: 'Patient Profile', icon: User },
  { id: 'upload', label: 'Upload Data', icon: UploadCloud },
  { id: 'voice', label: 'Voice Analysis', icon: Mic },
  { id: 'microbiome', label: 'Microbiome Analysis', icon: Bug },
  { id: 'hrv', label: 'Autonomic (HRV)', icon: HeartPulse },
  { id: 'inflammation', label: 'Inflammation', icon: FlaskConical },
  { id: 'amr', label: 'AMR Analysis', icon: Shield },
  { id: 'risk', label: 'Risk Summary', icon: TrendingUp },
  { id: 'explain', label: 'Explainability', icon: Lightbulb },
  { id: 'reports', label: 'Reports', icon: FileText },
  { id: 'settings', label: 'Settings', icon: Settings },
];

// --- REUSABLE COMPONENTS ---
const ScoreCard = ({ title, score, risk, color, icon: Icon }) => (
  <div className="bg-[#0f172a] p-4 rounded-xl border border-slate-800 flex flex-col justify-between">
    <div className="flex justify-between items-start mb-4">
      <h3 className="text-slate-400 text-sm font-medium">{title}</h3>
      <Icon className={`w-5 h-5 ${color}`} />
    </div>
    <div className="flex items-end gap-2 mb-2">
      <span className={`text-4xl font-bold ${color}`}>{score}</span>
      <span className="text-slate-400 text-sm mb-1">/100</span>
    </div>
    <div className="flex items-center gap-2">
      <span className="text-xs text-slate-300">{risk}</span>
    </div>
    <div className="w-full bg-slate-800 rounded-full h-1.5 mt-3">
      <div className={`h-1.5 rounded-full`} style={{ width: `${score}%`, backgroundColor: 'currentColor', color: color.replace('text-', '') }}></div>
    </div>
  </div>
);

const WaveformBars = () => (
  <div className="flex items-center justify-center gap-[2px] h-16 w-full opacity-80">
    {[...Array(40)].map((_, i) => (
      <div key={i} className="w-1 bg-purple-500 rounded-full" style={{ height: `${Math.max(20, Math.random() * 100)}%`, opacity: 0.5 + Math.random() * 0.5 }}></div>
    ))}
  </div>
);

// --- PLACEHOLDER PAGE COMPONENT ---
// This acts as a temporary screen for all the new tabs until we build them out
const PlaceholderPage = ({ title }) => (
  <div className="flex flex-col items-center justify-center h-full text-center p-6">
    <div className="bg-[#0f172a] p-12 rounded-2xl border border-slate-800 max-w-md w-full">
      <h2 className="text-2xl font-bold text-white mb-2">{title}</h2>
      <p className="text-slate-400 mb-6">This module is currently under development. Check back soon for updates.</p>
      <div className="animate-pulse flex space-x-4 justify-center">
        <div className="rounded-full bg-slate-800 h-10 w-10"></div>
        <div className="flex-1 space-y-4 py-1 max-w-[200px]">
          <div className="h-2 bg-slate-800 rounded"></div>
          <div className="space-y-3">
            <div className="grid grid-cols-3 gap-4">
              <div className="h-2 bg-slate-800 rounded col-span-2"></div>
              <div className="h-2 bg-slate-800 rounded col-span-1"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
);

// --- THE MAIN APP ---
function App() {
  // 1. STATE: This tracks which page is currently open!
  const [activePage, setActivePage] = useState('dashboard');
  useEffect(() => {
  const payload = {
    microbiome: {
      shannon_index: 2.1,
      proteobacteria: 0.3
    },
    voice: {
      jitter: 0.02,
      shimmer: 0.03
    },
    hrv: {
      rmssd: 18,
      sdnn: 30
    },
    inflammation: {
      il6: 12,
      tnf_alpha: 18
    }
  };

  fetch("http://127.0.0.1:8000/predict", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  })
    .then(res => res.json())
    .then(data => console.log("AI Prediction Data:", data));
}, []);

  return (
    <div className="flex h-screen bg-[#020617] text-white font-sans">

      {/* SIDEBAR */}
      <aside className="w-64 bg-[#050B14] border-r border-slate-800 flex flex-col hidden md:flex">

        {/* LOGO */}
        <div className="p-6 flex flex-col items-center border-b border-slate-800">
          <Brain className="w-12 h-12 text-purple-500 mb-2" />
          <h1 className="text-xl font-bold text-white tracking-wide">NeuroBiome <span className="text-blue-500">X</span></h1>
          <p className="text-[10px] text-slate-400 text-center mt-1">Neurodegenerative Risk<br />Prediction Platform</p>
        </div>

        {/* DYNAMIC NAVIGATION MENU */}
        <nav className="flex-1 p-4 space-y-1 overflow-y-auto custom-scrollbar">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activePage === item.id;

            return (
              <button
                key={item.id}
                onClick={() => setActivePage(item.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${isActive
                  ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg shadow-indigo-900/20'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
                  }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                {item.label}
              </button>
            )
          })}
        </nav>

        {/* AI STATUS & LOGOUT (Bottom Area) */}
        <div className="p-4 space-y-2 border-t border-slate-800 bg-[#050B14]">
          <div className="bg-[#0f172a] rounded-lg p-3 border border-slate-800">
            <div className="flex items-center gap-2 mb-1">
              <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
              <span className="text-sm font-medium text-white">AI Status</span>
            </div>
            <p className="text-xs text-slate-400">All systems operational</p>
          </div>

          <button className="w-full flex items-center gap-3 text-slate-400 hover:text-white bg-[#0f172a] border border-slate-800 hover:bg-slate-800 px-4 py-3 rounded-lg text-sm transition-colors mt-2">
            <LogOut className="w-4 h-4" /> Logout
          </button>
        </div>
      </aside>

      {/* MAIN CONTENT AREA */}
      <main className="flex-1 flex flex-col overflow-hidden">

        {/* HEADER */}
        <header className="flex justify-between items-center p-6 border-b border-slate-800 bg-[#020617]/80 backdrop-blur-md z-10 sticky top-0">
          <div>
            <h2 className="text-2xl font-bold flex items-center gap-2">
              {menuItems.find(m => m.id === activePage)?.label}
            </h2>
            <p className="text-slate-400 text-sm mt-1">
              {activePage === 'dashboard'
                ? 'Gut-Brain Neurodegenerative Vulnerability Assessment'
                : 'Manage patient data and analytics parameters'}
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className="bg-[#0f172a] border border-slate-700 rounded-lg px-4 py-2 text-sm text-slate-300">
              Patient ID: PDBR-2024-001 ⌄
            </div>
          </div>
        </header>

        {/* ROUTER LOGIC: Show different content based on the active tab */}
        <div className="flex-1 overflow-y-auto">

          {activePage === 'dashboard' ? (
            /* --- DASHBOARD PAGE CONTENT --- */
            <div className="p-6 pb-24">
              {/* Metric Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
                <ScoreCard title="Overall Risk Score" score="78" risk="High Risk" color="text-pink-500" icon={Brain} />
                <ScoreCard title="Microbiome Score" score="72" risk="High Risk" color="text-orange-500" icon={Bug} />
                <ScoreCard title="Voice Score" score="68" risk="Moderate Risk" color="text-purple-500" icon={Mic} />
                <ScoreCard title="Autonomic Score" score="65" risk="Moderate Risk" color="text-blue-500" icon={HeartPulse} />
                <ScoreCard title="Inflammation Score" score="70" risk="High Risk" color="text-emerald-500" icon={Stethoscope} />
                <ScoreCard title="AMR Score" score="60" risk="Moderate Risk" color="text-yellow-500" icon={Activity} />
              </div>

              {/* Middle Row Charts */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
                <div className="bg-[#0f172a] p-6 rounded-xl border border-slate-800 h-80 flex flex-col">
                  <h3 className="text-sm font-medium mb-4">Risk Radar (Multimodal View)</h3>
                  <div className="flex-1 w-full relative">
                    <ResponsiveContainer width="100%" height="100%">
                      <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                        <PolarGrid stroke="#334155" />
                        <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 10 }} />
                        <Radar name="Risk" dataKey="A" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.4} />
                        <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155' }} />
                      </RadarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                <div className="bg-[#0f172a] p-6 rounded-xl border border-slate-800 h-80 overflow-y-auto">
                  <div className="flex items-center gap-2 mb-4">
                    <Brain className="w-5 h-5 text-pink-500" />
                    <h3 className="text-sm font-medium">Risk Interpretation</h3>
                  </div>
                  <p className="text-sm text-slate-300 leading-relaxed mb-4">
                    The patient shows <span className="text-pink-500 font-semibold">high risk of neurodegenerative vulnerability.</span><br /><br />
                    Key contributing factors include gut dysbiosis, neuroinflammation, and autonomic imbalance.
                  </p>
                  <div className="bg-emerald-950/30 border border-emerald-900/50 rounded-lg p-4">
                    <h4 className="text-emerald-500 text-xs font-semibold uppercase tracking-wider mb-3">Recommendations</h4>
                    <ul className="space-y-2">
                      <li className="flex items-start gap-2 text-sm text-emerald-100/70"><CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" /> Dietary modification</li>
                      <li className="flex items-start gap-2 text-sm text-emerald-100/70"><CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" /> Probiotic & Prebiotic support</li>
                    </ul>
                  </div>
                </div>

                <div className="bg-[#0f172a] p-6 rounded-xl border border-slate-800 h-80 flex flex-col">
                  <h3 className="text-sm font-medium mb-2">Microbiome Composition</h3>
                  <div className="flex-1 flex items-center">
                    <div className="w-1/2 h-full relative">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie data={microbiomeData} cx="50%" cy="50%" innerRadius={45} outerRadius={65} paddingAngle={2} dataKey="value" stroke="none">
                            {microbiomeData.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.color} />
                            ))}
                          </Pie>
                        </PieChart>
                      </ResponsiveContainer>
                    </div>
                    <div className="w-1/2 flex flex-col justify-center gap-2 pl-2">
                      {microbiomeData.map((item, index) => (
                        <div key={index} className="flex items-center justify-between text-[11px]">
                          <div className="flex items-center gap-2">
                            <div className="w-2 h-2 rounded-sm" style={{ backgroundColor: item.color }}></div>
                            <span className="text-slate-300">{item.name}</span>
                          </div>
                          <span className="text-slate-400">{item.value}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Bottom Row */}
              <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                <div className="lg:col-span-2 bg-[#0f172a] p-6 rounded-xl border border-slate-800 flex flex-col h-80">
                  <h3 className="text-sm font-medium mb-4">Trend Over Time</h3>
                  <div className="flex-1 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={trendData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                        <XAxis dataKey="date" stroke="#64748b" fontSize={10} tickLine={false} axisLine={false} />
                        <YAxis stroke="#64748b" fontSize={10} tickLine={false} axisLine={false} />
                        <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155' }} />
                        <Line type="monotone" dataKey="microbiome" stroke="#f97316" strokeWidth={2} dot={false} />
                        <Line type="monotone" dataKey="voice" stroke="#a855f7" strokeWidth={2} dot={false} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* THE FIXED VOICE ANALYSIS PANEL */}
                <div className="bg-[#0f172a] p-6 rounded-xl border border-slate-800 h-80 flex flex-col">
                  <h3 className="text-sm font-medium mb-4">Voice Analysis</h3>
                  <div className="bg-[#020617] rounded-lg p-2 mb-4 border border-slate-800">
                    <WaveformBars />
                  </div>

                  {/* High/Low indicators added back */}
                  <div className="grid grid-cols-3 gap-2 mb-auto">
                    <div>
                      <p className="text-slate-400 text-xs">Jitter</p>
                      <p className="text-white font-bold text-lg">2.31%</p>
                      <p className="text-pink-500 text-[10px] mt-1">High</p>
                    </div>
                    <div>
                      <p className="text-slate-400 text-xs">Shimmer</p>
                      <p className="text-white font-bold text-lg">8.72%</p>
                      <p className="text-pink-500 text-[10px] mt-1">High</p>
                    </div>
                    <div>
                      <p className="text-slate-400 text-xs">HNR</p>
                      <p className="text-white font-bold text-lg">14.6 dB</p>
                      <p className="text-pink-500 text-[10px] mt-1">Low</p>
                    </div>
                  </div>

                  {/* THE MISSING BUTTON RESTORED */}
                  <button className="w-full bg-indigo-900/30 hover:bg-indigo-900/50 text-indigo-300 border border-indigo-500/20 py-2.5 rounded-lg text-sm transition-colors mt-4 font-medium">
                    View Detailed Analysis
                  </button>
                </div>

                <div className="bg-[#0f172a] p-6 rounded-xl border border-slate-800 h-80 flex flex-col">
                  <h3 className="text-sm font-medium mb-4">Recent Uploads</h3>
                  <div className="flex-1 overflow-y-auto space-y-4 pr-2">
                    <div className="flex items-center gap-3"><div className="w-8 h-8 rounded-full bg-purple-500/20 flex items-center justify-center text-purple-500"><Mic className="w-4 h-4" /></div><div><p className="text-sm text-white">Voice Sample</p><p className="text-[10px] text-slate-400">2 min ago</p></div></div>
                    <div className="flex items-center gap-3"><div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center text-blue-500"><HeartPulse className="w-4 h-4" /></div><div><p className="text-sm text-white">HRV Data</p><p className="text-[10px] text-slate-400">15 min ago</p></div></div>
                  </div>
                </div>
              </div>

            </div>
          ) : (
            /* --- OTHER PAGES (Placeholders) --- */
            <PlaceholderPage title={menuItems.find(m => m.id === activePage)?.label} />
          )}

        </div>
      </main>
    </div>
  );
}

export default App;