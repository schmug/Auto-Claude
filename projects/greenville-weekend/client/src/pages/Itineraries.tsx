// Itineraries page - Output #2: Curated day trip itineraries
// Design: Modern Trail Guide - forest green, burnt orange, warm cream
import { useState } from 'react';
import { ITINERARIES } from '@/lib/itinerariesData';
import ItineraryCard from '@/components/ItineraryCard';
import ItineraryDetail from '@/components/ItineraryDetail';
import { Map, List } from 'lucide-react';

const DAY_FILTERS = ['All', 'Friday', 'Saturday', 'Sunday', 'Any Day'] as const;
type DayFilter = typeof DAY_FILTERS[number];

export default function Itineraries() {
  const [selectedId, setSelectedId] = useState<string>(ITINERARIES[0].id);
  const [dayFilter, setDayFilter] = useState<DayFilter>('All');

  const filtered = ITINERARIES.filter(it =>
    dayFilter === 'All' || it.day === dayFilter || (dayFilter === 'Any Day' && it.day === 'Any Day')
  );

  const selected = ITINERARIES.find(it => it.id === selectedId) || ITINERARIES[0];

  return (
    <div className="min-h-screen bg-[#FAF7F0]">
      {/* Day filter bar */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="container py-3">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide mr-1">Filter by day:</span>
            {DAY_FILTERS.map(day => (
              <button
                key={day}
                onClick={() => setDayFilter(day)}
                className={`text-xs px-3 py-1.5 rounded-full border font-medium transition-colors ${
                  dayFilter === day
                    ? 'bg-green-700 text-white border-green-700'
                    : 'border-gray-300 text-gray-600 hover:bg-gray-50'
                }`}
              >
                {day}
              </button>
            ))}
            <span className="ml-auto text-xs text-gray-500">{filtered.length} itineraries</span>
          </div>
        </div>
      </div>

      {/* Main layout: sidebar + detail */}
      <div className="container py-6">
        <div className="flex gap-6 items-start">
          {/* Sidebar: itinerary list */}
          <div className="w-full sm:w-80 lg:w-96 shrink-0">
            <div className="space-y-3">
              {filtered.length === 0 ? (
                <div className="text-center py-10 text-gray-500 text-sm">
                  No itineraries for this day filter.
                </div>
              ) : (
                filtered.map(it => (
                  <ItineraryCard
                    key={it.id}
                    itinerary={it}
                    selected={selectedId === it.id}
                    onClick={() => setSelectedId(it.id)}
                  />
                ))
              )}
            </div>
          </div>

          {/* Detail panel */}
          <div className="flex-1 min-w-0 hidden sm:block">
            <ItineraryDetail itinerary={selected} />
          </div>
        </div>

        {/* Mobile: show detail below list when selected */}
        <div className="sm:hidden mt-4">
          <ItineraryDetail itinerary={selected} />
        </div>
      </div>
    </div>
  );
}
