import React, { useState } from 'react';
import { ProjectPlan } from './components/ProjectPlan';
import { GanttChart } from './components/GanttChart';
import { SearchResults } from './components/SearchResults';
import { projectData } from './constants';
import { PlanIcon, SearchIcon } from './components/icons';

type Tab = 'plan' | 'results';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<Tab>('plan');

  const renderContent = () => {
    switch (activeTab) {
      case 'plan':
        return (
          <>
            <GanttChart phases={projectData} />
            <ProjectPlan phases={projectData} />
          </>
        );
      case 'results':
        return <SearchResults />;
      default:
        return null;
    }
  };

  const TabButton: React.FC<{tab: Tab, label: string, icon: React.ReactNode}> = ({ tab, label, icon }) => (
    <button
        onClick={() => setActiveTab(tab)}
        className={`flex items-center justify-center w-full sm:w-auto px-4 py-2 text-sm font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-cyan-500 transition-colors duration-200 ${
          activeTab === tab
            ? 'bg-cyan-500 text-white shadow-lg'
            : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
        }`}
      >
        {icon}
        <span className="ml-2">{label}</span>
      </button>
  );

  return (
    <div className="min-h-screen bg-gray-900 text-gray-200 font-sans p-4 sm:p-6 md:p-8">
      <div className="max-w-7xl mx-auto">
        <header className="mb-8 md:mb-12 text-center">
          <h1 className="text-4xl sm:text-5xl font-bold text-cyan-400 tracking-tight">
            Arch<span className="text-white">E</span> Strategic Plan
          </h1>
          <p className="mt-2 text-lg text-gray-400">
            Abstraction & Retrieval Cognizant Handler of Exploration
          </p>
        </header>

        <nav className="mb-8 flex justify-center">
          <div className="flex space-x-2 sm:space-x-4 p-1 bg-gray-800 rounded-lg">
            <TabButton tab="plan" label="Strategic Plan" icon={<PlanIcon className="w-5 h-5" />} />
            <TabButton tab="results" label="Search & Results" icon={<SearchIcon className="w-5 h-5" />} />
          </div>
        </nav>

        <main>
          {renderContent()}
        </main>

        <footer className="text-center mt-12 text-gray-500 text-sm">
          <p>&copy; 2024 Happier Project. All Rights Reserved.</p>
        </footer>
      </div>
    </div>
  );
};

export default App;