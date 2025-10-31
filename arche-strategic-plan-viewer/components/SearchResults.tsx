import React, { useState, useMemo } from 'react';
import { FilterPanel } from './FilterPanel';
import { ProfileCard } from './ProfileCard';
import { mockProfileData } from '../constants';
import { FilterState, Profile } from '../types';
import { SearchIcon } from './icons';
import { ProfileModal } from './ProfileModal';

export const SearchResults: React.FC = () => {
    const [filters, setFilters] = useState<FilterState>({
        keyword: '',
        locations: [],
        platforms: [],
        profileType: 'All',
    });

    const [selectedProfile, setSelectedProfile] = useState<Profile | null>(null);

    const filteredProfiles = useMemo(() => {
        // Only show a subset of profiles initially if no filters are applied
        if (filters.keyword === '' && filters.locations.length === 0 && filters.platforms.length === 0 && filters.profileType === 'All') {
            return mockProfileData.slice(0, 4);
        }

        return mockProfileData.filter(profile => {
            const keywordMatch = filters.keyword.length === 0 ||
                profile.name.toLowerCase().includes(filters.keyword.toLowerCase()) ||
                profile.description.toLowerCase().includes(filters.keyword.toLowerCase()) ||
                profile.tags.some(tag => tag.toLowerCase().includes(filters.keyword.toLowerCase()));
            
            const locationMatch = filters.locations.length === 0 || filters.locations.includes(profile.location);
            const platformMatch = filters.platforms.length === 0 || filters.platforms.includes(profile.platform);
            const profileTypeMatch = filters.profileType === 'All' || profile.profileType === filters.profileType;

            return keywordMatch && locationMatch && platformMatch && profileTypeMatch;
        });
    }, [filters]);

    const handleCloseModal = () => {
        setSelectedProfile(null);
    }

    return (
        <div className="space-y-6">
            <FilterPanel filters={filters} onFilterChange={setFilters} totalResults={mockProfileData.length} />
            
            <div className="border-t border-gray-700 pt-6">
                <p className="text-gray-400 mb-4 text-sm">
                    Showing <span className="font-bold text-white">{filteredProfiles.length}</span> of <span className="font-bold text-white">{mockProfileData.length}</span> results
                </p>
                {filteredProfiles.length > 0 ? (
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                        {filteredProfiles.map(profile => (
                            <ProfileCard key={profile.id} profile={profile} onClick={() => setSelectedProfile(profile)} />
                        ))}
                    </div>
                ) : (
                    <div className="text-center py-16 px-6 bg-gray-800/50 rounded-lg">
                        <SearchIcon className="w-12 h-12 mx-auto text-gray-500" />
                        <h3 className="mt-2 text-xl font-semibold text-white">No Profiles Found</h3>
                        <p className="mt-1 text-gray-400">Try adjusting your search filters to find what you're looking for.</p>
                    </div>
                )}
            </div>
            {selectedProfile && (
                <ProfileModal profile={selectedProfile} onClose={handleCloseModal} />
            )}
        </div>
    );
};