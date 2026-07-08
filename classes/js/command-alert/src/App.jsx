// ... existing code ...
import React, { useState, useEffect } from 'react';
import { ShieldCheck, Siren, AlertTriangle, Activity, History, MapPin, Users, BellRing, Sparkles, MessageSquare } from 'lucide-react';

const App = () => {
  const [alertLevel, setAlertLevel] = useState('safe'); // 'safe', 'warning', 'danger'
// ... existing code ...
  const [alertsLog, setAlertsLog] = useState([
    { id: 1, type: 'מ"מ', distance: 100, time: '09:45', level: 'warning' },
    { id: 2, type: 'מג"ד', distance: 200, time: '08:30', level: 'safe' }
  ]);
  const [isFlashing, setIsFlashing] = useState(false);
  const [excuse, setExcuse] = useState('');
  const [isGeneratingExcuse, setIsGeneratingExcuse] = useState(false);

  const commanders = ['רס"ר', 'מ"מ', 'מ"פ', 'סמ"פ', 'מג"ד', 'קצין תורן'];

  const generateExcuse = async () => {
    setIsGeneratingExcuse(true);
    setExcuse('');
    const apiKey = ""; // API Key is injected by the environment
    const prompt = `אני חייל בצה"ל. ה${commanderType} נמצא במרחק ${distance} מטרים ממני! תן לי תירוץ צבאי אחד, קצר, יצירתי, אמין ומצחיק (בסלנג צה"לי של ימינו) שמסביר למה אני לא עושה כלום או מה אני "כביכול" עושה עכשיו, כדי שלא אקבל תלונה או ריתוק. משפט אחד בלבד.`;

    try {
      const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=${apiKey}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }]
        })
      });
      const data = await response.json();
      const text = data.candidates?.[0]?.content?.parts?.[0]?.text;
      setExcuse(text ? text.trim() : "האמת? פשוט תגיד שהלכת להביא מפתח אפס לטנק.");
    } catch (error) {
      setExcuse("הקשר נפל! אין תירוצים הפעם, תתחיל לרוץ!");
    } finally {
      setIsGeneratingExcuse(false);
    }
  };

  // Determine dynamic styles based on alert level
  const getThemeColors = () => {
    switch (alertLevel) {
      case 'danger': return 'from-red-200 via-rose-100 to-red-50';
      case 'warning': return 'from-amber-200 via-orange-100 to-amber-50';
      default: return 'from-sky-200 via-cyan-100 to-blue-50';
    }
  };

  const getGlassBorder = () => {
    switch (alertLevel) {
      case 'danger': return 'border-red-200 shadow-red-100';
      case 'warning': return 'border-amber-200 shadow-amber-100';
      default: return 'border-sky-200 shadow-sky-100';
    }
  };

  return (
    <div dir="rtl" className={`min-h-screen font-sans text-slate-800 bg-slate-50 relative overflow-hidden transition-colors duration-1000 ${isFlashing ? 'animate-pulse' : ''}`}>
      
      {/* Background Liquid Glass Blobs - Light Mode */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-0 pointer-events-none">
        <div className={`absolute -top-[20%] -right-[10%] w-[70vw] h-[70vw] rounded-full mix-blend-multiply filter blur-[100px] opacity-60 animate-blob bg-gradient-to-r ${getThemeColors()} transition-all duration-1000`}></div>
        <div className={`absolute top-[40%] -left-[20%] w-[60vw] h-[60vw] rounded-full mix-blend-multiply filter blur-[100px] opacity-50 animate-blob animation-delay-2000 bg-gradient-to-r ${getThemeColors()} transition-all duration-1000`}></div>
        <div className={`absolute -bottom-[20%] right-[20%] w-[80vw] h-[80vw] rounded-full mix-blend-multiply filter blur-[120px] opacity-60 animate-blob animation-delay-4000 bg-gradient-to-r ${getThemeColors()} transition-all duration-1000`}></div>
      </div>

      {/* Main Content */}
      <div className="relative z-10 max-w-md mx-auto p-4 sm:p-6 min-h-screen flex flex-col justify-between">
        
        {/* Header */}
        <header className="flex items-center justify-between py-4 mb-4">
          <div className="flex items-center gap-3">
            <div className={`p-3 rounded-2xl bg-white/80 backdrop-blur-md border border-white shadow-sm`}>
              <Siren className={`w-8 h-8 ${alertLevel === 'danger' ? 'text-red-500 animate-bounce' : alertLevel === 'warning' ? 'text-amber-500' : 'text-sky-500'}`} />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-slate-800">
                Command Alert
              </h1>
              <p className="text-xs text-slate-500 font-semibold tracking-widest uppercase">מערכת התרעה טקטית</p>
            </div>
          </div>
          
          <div className={`flex items-center gap-2 px-4 py-2 rounded-full bg-white/80 backdrop-blur-md border ${getGlassBorder()} shadow-sm transition-all`}>
            <Activity className={`w-4 h-4 ${alertLevel === 'danger' ? 'text-red-500 animate-ping' : 'text-sky-500'}`} />
            <span className={`text-sm font-bold ${alertLevel === 'danger' ? 'text-red-600' : alertLevel === 'warning' ? 'text-amber-600' : 'text-sky-600'}`}>
              {alertLevel === 'safe' ? 'שגרה' : alertLevel === 'warning' ? 'כוננות' : 'סכנה!'}
            </span>
          </div>
        </header>

        {/* Main Control Panel (Light Liquid Glass Card) */}
        <div className={`flex-1 flex flex-col gap-6 p-6 rounded-3xl bg-white/60 backdrop-blur-xl border border-white shadow-[0_8px_30px_rgb(0,0,0,0.04)] transition-all duration-500`}>
          
          {/* Commander Selector */}
          <div className="space-y-3">
            <label className="flex items-center gap-2 text-sm font-bold text-slate-700">
              <Users className="w-4 h-4 text-sky-500" />
              מי מתקרב?
            </label>
            <div className="grid grid-cols-3 gap-2">
              {commanders.map((cmd) => (
                <button
                  key={cmd}
                  onClick={() => setCommanderType(cmd)}
                  className={`py-2 rounded-xl text-sm font-bold transition-all duration-300 ${
                    commanderType === cmd 
                    ? 'bg-sky-500 shadow-md shadow-sky-200 text-white border border-sky-400' 
                    : 'bg-white/80 text-slate-600 hover:bg-sky-50 border border-slate-200/80 shadow-sm hover:shadow'
                  }`}
                >
                  {cmd}
                </button>
              ))}
            </div>
          </div>

          {/* Distance Slider */}
          <div className="space-y-3 mt-2">
            <div className="flex items-center justify-between text-sm font-bold text-slate-700">
              <label className="flex items-center gap-2">
                <MapPin className="w-4 h-4 text-sky-500" />
                מרחק משוער:
              </label>
              <span className="text-sky-700 bg-sky-100 px-3 py-1 rounded-lg border border-sky-200">
                {distance} מטרים
              </span>
            </div>
            <input 
              type="range" 
              min="10" 
              max="200" 
              step="10"
              value={distance}
              onChange={(e) => setDistance(e.target.value)}
              className="w-full h-2 rounded-lg appearance-none cursor-pointer accent-sky-500 shadow-inner"
              style={{
                background: `linear-gradient(to left, #38bdf8 ${(distance-10)/190 * 100}%, #e2e8f0 ${(distance-10)/190 * 100}%)`
              }}
            />
            <div className="flex justify-between text-xs text-slate-400 font-semibold">
              <span>קרוב מאוד</span>
              <span>רחוק</span>
            </div>
          </div>

          {/* Big Alert Button */}
          <div className="mt-4 pt-4 flex justify-center border-t border-slate-200/50">
            <button 
              onClick={triggerAlert}
              className={`relative group w-40 h-40 md:w-48 md:h-48 rounded-full flex items-center justify-center transition-all duration-300 
                ${alertLevel === 'danger' 
                  ? 'bg-red-50 shadow-[0_0_40px_rgba(239,68,68,0.3)]' 
                  : 'bg-white/50 hover:bg-white/80 shadow-xl border border-white hover:border-sky-200'}`}
            >
              {/* Pulsing rings */}
              <div className="absolute w-full h-full rounded-full border border-sky-200 animate-ping opacity-40"></div>
              <div className="absolute w-[80%] h-[80%] rounded-full border border-sky-300 animate-ping animation-delay-1000 opacity-50"></div>
              
              {/* Inner Button */}
              <div className={`w-[70%] h-[70%] rounded-full flex flex-col items-center justify-center gap-2 transition-all duration-300 backdrop-blur-md shadow-[inset_0_-4px_10px_rgba(0,0,0,0.1)]
                ${alertLevel === 'danger' ? 'bg-gradient-to-br from-red-500 to-red-600 border border-red-400 shadow-red-300/50 shadow-lg' : 'bg-gradient-to-br from-sky-400 to-sky-500 border border-sky-300 shadow-sky-300/50 shadow-lg'}`}>
                <BellRing className="w-10 h-10 text-white animate-pulse" />
                <span className="font-bold text-lg md:text-xl tracking-wider text-white drop-shadow-md">התרע!</span>
              </div>
            </button>
          </div>

          {/* AI Smart Excuse Generator */}
          <div className="mt-2 pt-4">
            <button
              onClick={generateExcuse}
              disabled={isGeneratingExcuse}
              className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-sky-50 hover:bg-sky-100 border border-sky-200 text-sky-700 transition-all font-bold shadow-sm"
            >
              {isGeneratingExcuse ? (
                <span className="animate-pulse flex items-center gap-2"><Sparkles className="w-5 h-5" /> Gemini ממציא...</span>
              ) : (
                <>
                  <Sparkles className="w-5 h-5 text-sky-500" />
                  תירוץ חירום ✨
                </>
              )}
            </button>
            
            {excuse && (
              <div className="mt-3 p-4 rounded-xl bg-white border border-sky-100 relative shadow-md shadow-sky-100/50">
                <MessageSquare className="absolute top-4 right-3 w-4 h-4 text-sky-400" />
                <p className="text-sm text-slate-700 pr-6 leading-relaxed font-medium">
                  {excuse}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Recent Alerts Log */}
        <div className="mt-6">
          <div className="flex items-center gap-2 mb-3 px-2">
            <History className="w-5 h-5 text-slate-400" />
            <h3 className="text-sm font-bold text-slate-600">היסטוריית דיווחים</h3>
          </div>
          
          <div className="space-y-2">
            {alertsLog.map((alert) => (
              <div key={alert.id} className="flex items-center justify-between p-3 rounded-2xl bg-white/80 backdrop-blur-sm border border-white shadow-sm hover:shadow-md transition-all">
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-full ${
                    alert.level === 'danger' ? 'bg-red-50 text-red-500 border border-red-100' : 
                    alert.level === 'warning' ? 'bg-amber-50 text-amber-500 border border-amber-100' : 'bg-sky-50 text-sky-500 border border-sky-100'
                  }`}>
                    {alert.level === 'danger' ? <AlertTriangle className="w-4 h-4" /> : <ShieldCheck className="w-4 h-4" />}
                  </div>
                  <div>
                    <p className="font-bold text-sm text-slate-700">{alert.type} <span className="text-slate-400 font-medium ml-1">זוהה</span></p>
                    <p className="text-xs font-semibold text-slate-500">{alert.distance} מטרים</p>
                  </div>
                </div>
                <span className="text-xs font-mono font-bold text-slate-500 bg-slate-100 px-2 py-1 rounded-lg border border-slate-200">{alert.time}</span>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* Embedded Styles for Blob Animation */}
      <style dangerouslySetInnerHTML={{__html: `
        @keyframes blob {
          0% { transform: translate(0px, 0px) scale(1); }
          33% { transform: translate(30px, -50px) scale(1.1); }
          66% { transform: translate(-20px, 20px) scale(0.9); }
          100% { transform: translate(0px, 0px) scale(1); }
        }
        .animate-blob {
          animation: blob 10s infinite;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .animation-delay-4000 {
          animation-delay: 4s;
        }
        .animation-delay-1000 {
          animation-delay: 1s;
        }
      `}} />
    </div>
  );
};

export default App;