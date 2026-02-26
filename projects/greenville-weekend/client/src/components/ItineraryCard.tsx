// ItineraryCard - compact card for itinerary list
import type { Itinerary } from '@/lib/itinerariesData';
import { MapPin, Clock, DollarSign, ChevronRight } from 'lucide-react';

interface ItineraryCardProps {
  itinerary: Itinerary;
  selected: boolean;
  onClick: () => void;
}

const THEME_COLORS: Record<string, string> = {
  'Arts & Culture': 'border-l-pink-500',
  'Nature & Outdoors': 'border-l-green-600',
  'History & Culture': 'border-l-amber-600',
  'Entertainment': 'border-l-indigo-600',
};

const THEME_BG: Record<string, string> = {
  'Arts & Culture': 'bg-pink-600',
  'Nature & Outdoors': 'bg-green-700',
  'History & Culture': 'bg-amber-700',
  'Entertainment': 'bg-indigo-700',
};

export default function ItineraryCard({ itinerary, selected, onClick }: ItineraryCardProps) {
  const borderClass = THEME_COLORS[itinerary.theme] || 'border-l-green-600';
  const bgClass = THEME_BG[itinerary.theme] || 'bg-green-700';

  return (
    <button
      onClick={onClick}
      className={`w-full text-left p-4 rounded-lg border-l-4 transition-all duration-200 ${borderClass} ${
        selected
          ? 'bg-white shadow-md ring-2 ring-green-600 ring-offset-1'
          : 'bg-white shadow-sm hover:shadow-md hover:-translate-y-0.5'
      }`}
    >
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-lg">{itinerary.themeIcon}</span>
            <span className={`text-xs font-semibold px-2 py-0.5 rounded-full text-white ${bgClass}`}>
              {itinerary.theme}
            </span>
          </div>
          <h3 className="font-display text-base font-semibold text-gray-900 leading-tight">
            {itinerary.title}
          </h3>
          <p className="text-xs text-gray-500 mt-0.5">{itinerary.subtitle}</p>
        </div>
        <ChevronRight className={`w-4 h-4 mt-1 shrink-0 transition-transform ${selected ? 'rotate-90 text-green-700' : 'text-gray-400'}`} />
      </div>

      <div className="flex flex-wrap gap-2 text-xs text-gray-600">
        <span className="flex items-center gap-1">
          <MapPin className="w-3 h-3 text-gray-400" />
          {itinerary.city}
        </span>
        <span className="flex items-center gap-1">
          <Clock className="w-3 h-3 text-gray-400" />
          {itinerary.driveTimeMinutes === 0 ? 'Local' : `${itinerary.driveTimeMinutes} min drive`}
        </span>
        <span className="flex items-center gap-1">
          <DollarSign className="w-3 h-3 text-gray-400" />
          {itinerary.costRange}
        </span>
      </div>

      <div className="flex items-center gap-2 mt-2">
        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
          itinerary.day === 'Friday' ? 'bg-blue-50 text-blue-700' :
          itinerary.day === 'Saturday' ? 'bg-purple-50 text-purple-700' :
          itinerary.day === 'Sunday' ? 'bg-amber-50 text-amber-700' :
          'bg-gray-100 text-gray-700'
        }`}>
          {itinerary.day}
        </span>
        <span className="text-xs text-gray-500">{itinerary.weatherIcon} {itinerary.weather}</span>
      </div>
    </button>
  );
}
