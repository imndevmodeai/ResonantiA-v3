import React, { useState, useRef, useEffect } from 'react';

// It's better practice to manage CDN script loading within the component
// to ensure the libraries are available before they are called.
const loadScript = (src) => {
  return new Promise((resolve, reject) => {
    if (document.querySelector(`script[src="${src}"]`)) {
      resolve();
      return;
    }
    const script = document.createElement('script');
    script.src = src;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error(`Script load error for ${src}`));
    document.head.appendChild(script);
  });
};

const workbookData = [
  {
    category: 'Job & Career',
    words: [
      'Accomplishment', 'Challenge', 'Co-workers', 'Competent', 'Contribution',
      'Collaboration', 'Creativity', 'Dedication', 'Earnings', 'Earning a living',
      'Growth', 'Independence', 'Innovation', 'Learning', 'Mentorship',
      'Passion', 'Positive environment', 'Problem-solving', 'Professionalism',
      'Pride in my work', 'Purpose', 'Recognition', 'Responsibility',
      'Rewarding', 'Security', 'Self-improvement', 'Sense of purpose',
      'Stability', 'Teamwork', 'The commute', 'The work itself', 'Training',
      'Upward mobility', 'Valuable', 'Variety', 'Work-life balance',
      'Workplace culture', 'Working with my hands', 'Working with my mind',
      'Future opportunities'
    ],
  },
  {
    category: 'Family (Daughter)',
    words: [
      'Admiration', 'Connection', 'Devotion', 'Fun', 'Future hope',
      'Growing together', 'Guidance', 'Happiness', 'Heartwarming',
      'Her laughter', 'Her smile', 'Joy', 'Legacy', 'Love',
      'Making memories', 'Meaningful conversations', 'My "why"',
      'My little girl', 'Patience', 'Playfulness', 'Pride',
      'Precious moments', 'Protection', 'Quality time', 'Reconnecting',
      'Resilience', 'Responsibility', 'Role model', 'Support',
      'Tenderness', 'Togetherness', 'Trust', 'Unconditional love',
      'Understanding', 'Vulnerability', 'Warmth', 'Witnessing her growth',
      'Wonderful', 'Childlike wonder', 'Her needs first'
    ],
  },
  {
    category: 'Faith & Religion',
    words: [
      'Awe', 'Blessing', 'Community', 'Comfort', 'Devotion',
      'Forgiveness', 'Foundation', 'Grace', 'Gratitude', 'Guidance',
      'Hope', 'Inner peace', 'Inspiration', 'Joyful', 'Kindness',
      'Meaning of life', 'Meditation', 'Morality', 'Prayer', 'Purpose',
      'Redemption', 'Reflection', 'Repentance', 'Sacredness',
      'Salvation', 'Serenity', 'Service', 'Spiritual growth', 'Strength',
      'Surrender', 'Trust', 'Understanding', 'Unwavering belief',
      'Virtue', 'Worship', 'Daily habit', 'Foundation for life',
      'Higher plan', 'Personal relationship', 'Searching'
    ],
  },
  {
    category: 'Leisure (Fishing)',
    words: [
      'Adventure', 'Anticipation', 'Calmness', 'Centering',
      'Connection with nature', 'De-stressing', 'Focus', 'Freedom',
      'Getting away from it all', 'Hobby', 'Meditation', 'Mindfulness',
      'My time', 'Nature', 'No distractions', 'Obsession',
      'Outdoor activity', 'Passion', 'Patience', 'Peace', 'Quiet',
      'Recharging', 'Reflection', 'Relaxing', 'Restoration',
      'Sanctuary', 'Serenity', 'Solitude', 'Stillness',
      'Sunset/Sunrise', 'The gear', 'The water', 'Thinking time',
      'Thrills', 'Tranquility', 'Unwinding', 'Way of life', 'Joy',
      'Escape', 'Fun'
    ],
  },
  {
    category: 'Self-Improvement',
    words: [
      'Accomplishment', 'Ambition', 'Confidence', 'Courage',
      'Creativity', 'Discipline', 'Empowerment', 'Enriching',
      'Exciting', 'Facing challenges', 'Finding purpose', 'Focus',
      'Future-proofing', 'Growth', 'Honesty', 'Hopeful',
      'Investing in me', 'Learning', 'Mastery', 'Motivation',
      'New beginnings', 'Overcoming obstacles', 'Persistence',
      'Progress', 'Personal growth', 'Potential', 'Resilience',
      'Rewarding', 'Self-awareness', 'Self-care', 'Skill development',
      'Taking control', 'Transformation', 'Unlocking potential',
      'Wisdom', 'Hard work', 'Goal-oriented', 'Knowledge',
      'Stress management', 'Mental exercise'
    ],
  },
  {
    category: 'Health & Personal Well-being',
    words: [
      'Abundance', 'Balance', 'Body positivity', 'Care', 'Clarity',
      'Cleanliness', 'Comfort', 'Consistency', 'Energy', 'Fitness',
      'Focus', 'Happiness', 'Harmony', 'Healing', 'Holistic health',
      'Hygiene', 'Joy', 'Mindfulness', 'Nourishment', 'Optimism',
      'Peace', 'Positivity', 'Relaxation', 'Rejuvenation',
      'Renewal', 'Restoration', 'Self-care', 'Serenity', 'Sleep',
      'Stamina', 'Strength', 'Stress relief', 'Vitality',
      'Well-being', 'Wellness', 'Wholeness', 'Nurturing',
      'Vibrancy', 'Flexibility', 'Foundation for a good day'
    ],
  },
];

const IntroductionPage = () => {
  return (
    <div className="bg-white p-8 rounded-lg shadow-md mb-8 page-container" id="page-introduction">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-800">Moral Reconation Therapy (MRT)</h1>
        <h2 className="text-2xl font-semibold text-indigo-600 mt-2">Step 4: Awareness of Positive Qualities</h2>
      </div>
      <div className="text-lg text-gray-700 space-y-4">
        <p>
          This workbook exercise is based on the principles of Step 4 of Moral Reconation Therapy. The goal of this step is to increase awareness of your own positive qualities and the good things in your life.
        </p>
        <p>
          By focusing on these positive aspects, you can begin to build a stronger sense of self-worth and a more positive identity. The following pages contain lists of positive words related to different areas of life.
        </p>
        <p>
          Reflect on these words and add your own thoughts and feelings in the space provided. Honesty and thoroughness are key to this exercise.
        </p>
      </div>
    </div>
  );
};

const CategoryPage = ({ data, onWordsChange, userWords }) => {
  return (
    <div className="bg-white p-6 rounded-lg shadow-md mb-8 page-container" id={`page-${data.category.replace(/\s/g, '-')}`}>
      <h2 className="text-2xl font-bold mb-4 text-center text-gray-800">{data.category}</h2>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-y-2 gap-x-4 mb-6">
        {data.words.map((word, index) => (
          <div key={index} className="flex items-center space-x-2">
            <span className="text-lg text-gray-700 font-medium">{word}</span>
          </div>
        ))}
      </div>
      <div className="mt-4">
        <label htmlFor={`words-for-${data.category}`} className="block text-xl font-semibold mb-2 text-gray-800">My Own Words:</label>
        <textarea
          id={`words-for-${data.category}`}
          rows="4"
          className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all duration-200 resize-none"
          value={userWords}
          onChange={(e) => onWordsChange(data.category, e.target.value)}
          placeholder="Add your own words here, separated by commas or new lines."
        />
      </div>
    </div>
  );
};

const MRTWorkbook = () => {
  const [userWords, setUserWords] = useState({
    'Job & Career': "I am proud of the skills I have developed. My work provides stability for my family, and I am learning to find satisfaction in a job well done. I am working towards a future with more opportunities.",
    'Family (Daughter)': "My daughter is my biggest motivation for change. I want to be a father she can be proud of. Every moment with her is a reminder of the good I want to build in my life. Our connection is the most important thing to me.",
    'Faith & Religion': "My faith provides a foundation when things are difficult. It gives me hope and a sense of purpose beyond myself. I am learning to trust in a higher plan and find peace in daily reflection and prayer.",
    'Leisure (Fishing)': "Fishing is more than a hobby; it's how I find peace and quiet. It allows me to connect with nature and clear my head. The patience it teaches me is something I can apply to my daily life.",
    'Self-Improvement': "I am committed to personal growth and becoming a better person. Every day is a new beginning and a chance to make progress. I am learning to be more disciplined and to face challenges with courage.",
    'Health & Personal Well-being': "Taking care of my health is the foundation for everything else. I am focusing on getting enough rest, eating better, and managing stress. A healthy body and mind give me the energy to work on my goals."
  });
  const [isLoading, setIsLoading] = useState(false);
  const [libsLoaded, setLibsLoaded] = useState(false);
  const pdfRef = useRef();

  useEffect(() => {
    Promise.all([
      loadScript("https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"),
      loadScript("https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js")
    ]).then(() => {
      setLibsLoaded(true);
      console.log("PDF generation libraries loaded.");
    }).catch(error => {
      console.error("Failed to load PDF libraries:", error);
      alert("Could not load necessary libraries for PDF generation. Please check your internet connection and try again.");
    });
  }, []);

  const handleWordsChange = (category, value) => {
    setUserWords(prev => ({
      ...prev,
      [category]: value,
    }));
  };

  const handleGeneratePdf = async () => {
    if (!libsLoaded) {
      alert("PDF libraries are not loaded yet. Please wait a moment and try again.");
      return;
    }
    if (isLoading) return;

    setIsLoading(true);
    const pages = pdfRef.current.querySelectorAll('.page-container');
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF('p', 'mm', 'a4');
    const pdfWidth = doc.internal.pageSize.getWidth();
    const pdfHeight = doc.internal.pageSize.getHeight();
    const margin = 10; // 10mm margin

    for (let i = 0; i < pages.length; i++) {
      const page = pages[i];
      if (i > 0) {
        doc.addPage();
      }

      const canvas = await window.html2canvas(page, { scale: 2, useCORS: true });
      const imgData = canvas.toDataURL('image/png');
      const imgProps = doc.getImageProperties(imgData);
      
      const canvasWidth = pdfWidth - (margin * 2);
      const canvasHeight = (imgProps.height * canvasWidth) / imgProps.width;

      let position = 0;
      if (canvasHeight > pdfHeight - (margin * 2)) {
         console.warn(`Content on page ${i+1} might be too long to fit on a single PDF page.`);
      }

      doc.addImage(imgData, 'PNG', margin, margin, canvasWidth, canvasHeight);
    }

    doc.save('mrt-step4-workbook.pdf');
    setIsLoading(false);
  };

  return (
    <div className="flex flex-col items-center min-h-screen bg-gray-100 p-4 font-sans text-gray-900">
      <div className="w-full max-w-4xl p-6 bg-white rounded-lg shadow-xl mb-8">
        <h1 className="text-3xl font-extrabold text-center mb-4 text-indigo-700">MRT Workbook PDF Generator</h1>
        <p className="text-center text-gray-600 mb-6">
          The fields below have been pre-filled with reflective statements based on the principles of MRT Step 4. You can edit them or add your own thoughts before generating the PDF.
        </p>
        <button
          onClick={handleGeneratePdf}
          disabled={isLoading || !libsLoaded}
          className="flex items-center justify-center w-full px-6 py-3 bg-indigo-600 text-white font-bold text-lg rounded-full shadow-lg hover:bg-indigo-700 transition-all duration-300 transform hover:scale-105 focus:outline-none focus:ring-4 focus:ring-indigo-500 focus:ring-opacity-50 disabled:bg-gray-400 disabled:cursor-not-allowed disabled:transform-none"
        >
          {isLoading ? (
            <>
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Generating PDF...
            </>
          ) : (
            <>
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" x2="12" y1="15" y2="3"/>
              </svg>
              Generate & Download PDF
            </>
          )}
        </button>
        {!libsLoaded && <p className="text-center text-sm text-yellow-600 mt-2">Loading PDF libraries, please wait...</p>}
      </div>
      
      <div ref={pdfRef} className="w-full max-w-4xl">
        <IntroductionPage />
        {workbookData.map((data, index) => (
          <CategoryPage
            key={index}
            data={data}
            onWordsChange={handleWordsChange}
            userWords={userWords[data.category] || ''}
          />
        ))}
      </div>
    </div>
  );
};

export default MRTWorkbook;
