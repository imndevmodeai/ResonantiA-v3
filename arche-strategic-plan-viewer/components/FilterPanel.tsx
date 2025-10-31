import React, { useState } from 'react';
import { FilterState, Location, Platform, ProfileType } from '../types';
import { ChevronDownIcon, SearchIcon } from './icons';

interface FilterPanelProps {
  filters: FilterState;
  onFilterChange: React.Dispatch<React.SetStateAction<FilterState>>;
  totalResults: number;
}

const locations: Location[] = ['Kalamazoo', 'Battle Creek', 'Grand Rapids'];
const platforms: Platform[] = ['FetLife', 'SkipTheGames', 'Chaturbate'];
const profileTypes: ('All' | ProfileType)[] = ['All', 'Female', 'Couple'];

export const FilterPanel: React.FC<FilterPanelProps> = ({ filters, onFilterChange }) => {
    const [isOpen, setIsOpen] = useState(true);

    const handleKeywordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        onFilterChange(prev => ({ ...prev, keyword: e.target.value }));
    };

    const handleCheckboxChange = (field: 'locations' | 'platforms', value: string) => {
        onFilterChange(prev => {
            const currentValues = prev[field] as string[];
            const newValues = currentValues.includes(value)
                ? currentValues.filter(v => v !== value)
                : [...currentValues, value];
            return { ...prev, [field]: newValues };
        });
    };

    const handleProfileTypeChange = (value: 'All' | ProfileType) => {
        onFilterChange(prev => ({ ...prev, profileType: value }));
    }

    return (
        <div className="bg-gray-800/50 border border-gray-700/50 rounded-lg shadow-lg backdrop-blur-sm">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="w-full p-4 text-left flex justify-between items-center bg-gray-800 hover:bg-gray-700/80 focus:outline-none focus:ring-2 focus:ring-cyan-500 rounded-t-lg"
            >
                <h2 className="text-lg font-semibold text-white">Filter & Search Preferences</h2>
                <ChevronDownIcon className={`w-6 h-6 text-gray-400 transform transition-transform duration-300 ${isOpen ? 'rotate-180' : ''}`} />
            </button>
            <div className={`transition-all duration-500 ease-in-out ${isOpen ? 'max-h-[1000px] opacity-100' : 'max-h-0 opacity-0'} overflow-hidden`}>
                <div className="p-6 space-y-6">
                    {/* Keyword Search */}
                    <div>
                        <label htmlFor="keyword-search" className="block text-sm font-medium text-gray-300 mb-2">Keyword</label>
                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <SearchIcon className="h-5 w-5 text-gray-400" />
                            </div>
                            <input
                                type="text"
                                id="keyword-search"
                                value={filters.keyword}
                                onChange={handleKeywordChange}
                                placeholder="Search by name, tags, description..."
                                className="w-full bg-gray-700 border border-gray-600 rounded-md py-2 pl-10 pr-4 text-white focus:ring-cyan-500 focus:border-cyan-500"
                            />
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {/* Locations Filter */}
                        <fieldset>
                            <legend className="block text-sm font-medium text-gray-300 mb-2">Location</legend>
                            <div className="space-y-2">
                                {locations.map(location => (
                                    <div key={location} className="flex items-center">
                                        <input
                                            id={`location-${location}`}
                                            type="checkbox"
                                            checked={filters.locations.includes(location)}
                                            onChange={() => handleCheckboxChange('locations', location)}
                                            className="h-4 w-4 rounded border-gray-500 bg-gray-600 text-cyan-600 focus:ring-cyan-500"
                                        />
                                        <label htmlFor={`location-${location}`} className="ml-3 text-sm text-gray-200">{location}</label>
                                    </div>
                                ))}
                            </div>
                        </fieldset>

                        {/* Platforms Filter */}
                        <fieldset>
                            <legend className="block text-sm font-medium text-gray-300 mb-2">Platform</legend>
                            <div className="space-y-2">
                                {platforms.map(platform => (
                                    <div key={platform} className="flex items-center">
                                        <input
                                            id={`platform-${platform}`}
                                            type="checkbox"
                                            checked={filters.platforms.includes(platform)}
                                            onChange={() => handleCheckboxChange('platforms', platform)}
                                            className="h-4 w-4 rounded border-gray-500 bg-gray-600 text-cyan-600 focus:ring-cyan-500"
                                        />
                                        <label htmlFor={`platform-${platform}`} className="ml-3 text-sm text-gray-200">{platform}</label>
                                    </div>
                                ))}
                            </div>
                        </fieldset>

                        {/* Profile Type Filter */}
                        <fieldset>
                            <legend className="block text-sm font-medium text-gray-300 mb-2">Profile Type</legend>
                            <div className="space-y-2">
                                {profileTypes.map(type => (
                                    <div key={type} className="flex items-center">
                                        <input
                                            id={`type-${type}`}
                                            type="radio"
                                            name="profileType"
                                            checked={filters.profileType === type}
                                            onChange={() => handleProfileTypeChange(type)}
                                            className="h-4 w-4 border-gray-500 bg-gray-600 text-cyan-600 focus:ring-cyan-500"
                                        />
                                        <label htmlFor={`type-${type}`} className="ml-3 text-sm text-gray-200">{type}</label>
                                    </div>
                                ))}
                            </div>
                        </fieldset>
                    </div>
                </div>
            </div>
        </div>
    );
};
