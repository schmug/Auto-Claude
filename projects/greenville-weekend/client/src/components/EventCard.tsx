// EventCard component - Modern Trail Guide design
import { useState } from 'react';
import type { Event } from '@/lib/eventsData';
import { CATEGORY_ICONS, CATEGORY_COLORS, CATEGORY_BORDER_COLORS, BUDGET_COLORS } from '@/lib/eventsData';
import { downloadSingleEventIcal } from '@/lib/ical';
import { MapPin, Clock, DollarSign, Calendar, ExternalLink, Download, Leaf, Salad, Home, Trees } from 'lucide-react';

interface EventCardProps {
  event: Event;
  compact?: boolean;
}

export default function EventCard({ event, compact = false }: EventCardProps) {
  const [expanded, setExpanded] = useState(false);
  const borderColor = CATEGORY_BORDER_COLORS[event.category];
  const categoryStyle = CATEGORY_COLORS[event.category];
  const budgetStyle = BUDGET_COLORS[event.budgetTier];

  const dayColors: Record<string, string> = {
    Friday: 'bg-blue-50 text-blue-700 border border-blue-200',
    Saturday: 'bg-purple-50 text-purple-700 border border-purple-200',
    Sunday: 'bg-amber-50 text-amber-700 border border-amber-200',
  };

  return (
    <div
      className="event-card bg-white rounded-lg shadow-sm border border-gray-100 overflow-hidden"
      style={{ borderLeftColor: borderColor, borderLeftWidth: '4px' }}
    >
      {/* Header */}
      <div className="p-4 pb-2">
        <div className="flex items-start justify-between gap-2 mb-2">
          <div className="flex-1 min-w-0">
            <h3 className="font-display text-base font-semibold text-gray-900 leading-tight line-clamp-2">
              {CATEGORY_ICONS[event.category]} {event.name}
            </h3>
          </div>
          <div className="flex flex-col items-end gap-1 shrink-0">
            <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${budgetStyle}`}>
              {event.budgetTier === 'Free' ? 'Free' : event.budgetTier}
            </span>
          </div>
        </div>

        {/* Location & Distance */}
        <div className="flex items-center gap-1.5 text-sm text-gray-600 mb-1">
          <MapPin className="w-3.5 h-3.5 text-gray-400 shrink-0" />
          <span className="font-medium">{event.city}, NC</span>
          <span className="text-gray-400">·</span>
          <span className="text-xs bg-gray-100 px-1.5 py-0.5 rounded font-medium">
            {event.distanceMiles === 0 ? 'Local' : `${event.distanceMiles} mi`}
          </span>
          {event.driveTimeMinutes > 0 && (
            <span className="text-xs text-gray-500">{event.driveTimeMinutes} min drive</span>
          )}
        </div>

        {/* Days & Time */}
        <div className="flex flex-wrap items-center gap-1.5 mb-2">
          {event.days.map(day => (
            <span key={day} className={`text-xs px-2 py-0.5 rounded-full font-medium ${dayColors[day]}`}>
              {day}
            </span>
          ))}
          <span className="text-xs text-gray-600 flex items-center gap-1">
            <Clock className="w-3 h-3" />
            {event.startTime}{event.endTime ? ` – ${event.endTime}` : ''}
          </span>
        </div>

        {/* Price & Weather row */}
        <div className="flex flex-wrap items-center gap-2 mb-2">
          <span className="text-sm font-semibold text-gray-800">
            {event.price}
          </span>
          <span className="text-xs text-gray-500">
            {event.weatherIcon} {event.weather}
          </span>
          <span className={`text-xs px-1.5 py-0.5 rounded border ${event.indoorOutdoor === 'Indoor' ? 'bg-slate-50 text-slate-700 border-slate-200' : event.indoorOutdoor === 'Outdoor' ? 'bg-green-50 text-green-700 border-green-200' : 'bg-teal-50 text-teal-700 border-teal-200'}`}>
            {event.indoorOutdoor === 'Indoor' ? <><Home className="w-3 h-3 inline mr-0.5" />Indoor</> : event.indoorOutdoor === 'Outdoor' ? <><Trees className="w-3 h-3 inline mr-0.5" />Outdoor</> : 'Both'}
          </span>
        </div>

        {/* Dietary badges */}
        <div className="flex flex-wrap gap-1.5 mb-2">
          <span className={`text-xs px-2 py-0.5 rounded-full border ${categoryStyle}`}>
            {event.category}
          </span>
          {event.veganOptions === true && (
            <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center gap-0.5">
              <Leaf className="w-3 h-3" /> Vegan
            </span>
          )}
          {event.vegetarianOptions === true && (
            <span className="text-xs px-2 py-0.5 rounded-full bg-lime-50 text-lime-700 border border-lime-200 flex items-center gap-0.5">
              <Salad className="w-3 h-3" /> Vegetarian
            </span>
          )}
        </div>
      </div>

      {/* Description (collapsible) */}
      {!compact && (
        <div className="px-4 pb-2">
          <p className={`text-sm text-gray-600 leading-relaxed ${expanded ? '' : 'line-clamp-2'}`}>
            {event.description}
          </p>
          {event.description.length > 120 && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="text-xs text-green-700 hover:text-green-900 font-medium mt-0.5"
            >
              {expanded ? 'Show less' : 'Read more'}
            </button>
          )}
        </div>
      )}

      {/* Action buttons */}
      <div className="px-4 pb-3 flex flex-wrap gap-2 mt-1">
        {event.bookingUrl && (
          <a
            href={event.bookingUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-xs font-semibold px-3 py-1.5 rounded-md bg-green-700 text-white hover:bg-green-800 transition-colors"
          >
            <ExternalLink className="w-3 h-3" />
            Book
          </a>
        )}
        {event.infoUrl && (
          <a
            href={event.infoUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-xs font-medium px-3 py-1.5 rounded-md border border-gray-300 text-gray-700 hover:bg-gray-50 transition-colors"
          >
            <ExternalLink className="w-3 h-3" />
            Info
          </a>
        )}
        <button
          onClick={() => downloadSingleEventIcal(event)}
          className="inline-flex items-center gap-1 text-xs font-medium px-3 py-1.5 rounded-md border border-gray-300 text-gray-700 hover:bg-gray-50 transition-colors"
          title="Add to Calendar"
        >
          <Calendar className="w-3 h-3" />
          iCal
        </button>
      </div>
    </div>
  );
}
