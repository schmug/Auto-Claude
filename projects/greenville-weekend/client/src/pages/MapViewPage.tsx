// MapView page - Interactive map of all events
// Design: Modern Trail Guide
import { useState, useRef } from 'react';
import { MapView } from '@/components/Map';
import { EVENTS, CATEGORY_ICONS, CATEGORY_BORDER_COLORS, type Event, type DayFilter, type Category } from '@/lib/eventsData';
import { MapPin, X, ExternalLink, Calendar } from 'lucide-react';
import { downloadSingleEventIcal } from '@/lib/ical';

const DAYS: DayFilter[] = ['Friday', 'Saturday', 'Sunday'];

export default function MapViewPage() {
  const [selectedDay, setSelectedDay] = useState<DayFilter | 'All'>('All');
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const mapRef = useRef<google.maps.Map | null>(null);
  const markersRef = useRef<google.maps.Marker[]>([]);
  const infoWindowRef = useRef<google.maps.InfoWindow | null>(null);

  const filteredEvents = EVENTS.filter(e => {
    if (selectedDay === 'All') return true;
    return e.days.includes(selectedDay as DayFilter);
  }).filter(e => e.lat && e.lng);

  const handleMapReady = (map: google.maps.Map) => {
    mapRef.current = map;

    // Clear existing markers
    markersRef.current.forEach(m => m.setMap(null));
    markersRef.current = [];

    if (infoWindowRef.current) {
      infoWindowRef.current.close();
    }
    infoWindowRef.current = new google.maps.InfoWindow();

    // Add Greenville center marker
    new google.maps.Marker({
      position: { lat: 35.6127, lng: -77.3664 },
      map,
      title: 'Greenville, NC (Home Base)',
      icon: {
        path: google.maps.SymbolPath.CIRCLE,
        scale: 10,
        fillColor: '#2D5016',
        fillOpacity: 1,
        strokeColor: '#fff',
        strokeWeight: 2,
      },
      zIndex: 1000,
    });

    // Add event markers
    filteredEvents.forEach(event => {
      if (!event.lat || !event.lng) return;

      const color = CATEGORY_BORDER_COLORS[event.category] || '#2D5016';

      const marker = new google.maps.Marker({
        position: { lat: event.lat, lng: event.lng },
        map,
        title: event.name,
        icon: {
          path: google.maps.SymbolPath.CIRCLE,
          scale: 8,
          fillColor: color,
          fillOpacity: 0.9,
          strokeColor: '#fff',
          strokeWeight: 2,
        },
      });

      marker.addListener('click', () => {
        setSelectedEvent(event);
        const content = `
          <div style="font-family: 'DM Sans', sans-serif; max-width: 220px; padding: 4px;">
            <div style="font-weight: 700; font-size: 14px; color: #1a1a1a; margin-bottom: 4px;">${CATEGORY_ICONS[event.category]} ${event.name}</div>
            <div style="font-size: 12px; color: #555; margin-bottom: 2px;">📍 ${event.city}, NC</div>
            <div style="font-size: 12px; color: #555; margin-bottom: 2px;">🕐 ${event.startTime}</div>
            <div style="font-size: 12px; font-weight: 600; color: #2D5016;">${event.price}</div>
          </div>
        `;
        infoWindowRef.current?.setContent(content);
        infoWindowRef.current?.open(map, marker);
      });

      markersRef.current.push(marker);
    });

    // Fit bounds to show all markers
    if (filteredEvents.length > 0) {
      const bounds = new google.maps.LatLngBounds();
      bounds.extend({ lat: 35.6127, lng: -77.3664 }); // Greenville
      filteredEvents.forEach(e => {
        if (e.lat && e.lng) bounds.extend({ lat: e.lat, lng: e.lng });
      });
      map.fitBounds(bounds, { top: 40, right: 40, bottom: 40, left: 40 });
    }
  };

  return (
    <div className="min-h-screen bg-[#FAF7F0] flex flex-col">
      {/* Controls */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="container py-3">
          <div className="flex flex-wrap items-center gap-3">
            <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Show:</span>
            <button
              onClick={() => setSelectedDay('All')}
              className={`text-xs px-3 py-1.5 rounded-full border font-medium transition-colors ${selectedDay === 'All' ? 'bg-green-700 text-white border-green-700' : 'border-gray-300 text-gray-600 hover:bg-gray-50'}`}
            >
              All Days ({EVENTS.filter(e => e.lat && e.lng).length})
            </button>
            {DAYS.map(day => (
              <button
                key={day}
                onClick={() => setSelectedDay(day)}
                className={`text-xs px-3 py-1.5 rounded-full border font-medium transition-colors ${
                  selectedDay === day
                    ? day === 'Friday' ? 'bg-blue-600 text-white border-blue-600'
                      : day === 'Saturday' ? 'bg-purple-600 text-white border-purple-600'
                      : 'bg-amber-600 text-white border-amber-600'
                    : 'border-gray-300 text-gray-600 hover:bg-gray-50'
                }`}
              >
                {day} ({EVENTS.filter(e => e.days.includes(day) && e.lat && e.lng).length})
              </button>
            ))}
            <span className="ml-auto text-xs text-gray-500">{filteredEvents.length} events on map</span>
          </div>
        </div>
      </div>

      {/* Map + sidebar layout */}
      <div className="flex-1 flex relative">
        {/* Map */}
        <div className="flex-1 min-h-[500px]">
          <MapView
            onMapReady={handleMapReady}
            className="w-full h-full min-h-[500px]"
            initialCenter={{ lat: 35.9, lng: -77.8 }}
            initialZoom={8}
          />
        </div>

        {/* Selected event sidebar */}
        {selectedEvent && (
          <div className="absolute right-4 top-4 w-72 bg-white rounded-xl shadow-xl border border-gray-200 overflow-hidden z-10">
            <div className="bg-green-800 text-white p-3 flex items-start justify-between">
              <div>
                <div className="text-xs text-green-300 mb-0.5">{selectedEvent.category}</div>
                <h3 className="font-display text-sm font-semibold leading-tight">
                  {CATEGORY_ICONS[selectedEvent.category]} {selectedEvent.name}
                </h3>
              </div>
              <button onClick={() => setSelectedEvent(null)} className="text-green-300 hover:text-white ml-2 shrink-0">
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="p-3 space-y-2">
              <div className="flex items-center gap-1.5 text-sm text-gray-600">
                <MapPin className="w-3.5 h-3.5 text-gray-400" />
                {selectedEvent.city}, NC · {selectedEvent.distanceMiles === 0 ? 'Local' : `${selectedEvent.distanceMiles} mi`}
              </div>
              <div className="text-sm">
                <span className="font-semibold text-gray-800">{selectedEvent.price}</span>
                <span className="text-gray-500 ml-2 text-xs">{selectedEvent.startTime}</span>
              </div>
              <div className="flex flex-wrap gap-1">
                {selectedEvent.days.map(d => (
                  <span key={d} className={`text-xs px-2 py-0.5 rounded-full font-medium ${d === 'Friday' ? 'bg-blue-50 text-blue-700' : d === 'Saturday' ? 'bg-purple-50 text-purple-700' : 'bg-amber-50 text-amber-700'}`}>
                    {d}
                  </span>
                ))}
                <span className="text-xs text-gray-500">{selectedEvent.weatherIcon}</span>
              </div>
              <p className="text-xs text-gray-600 leading-relaxed line-clamp-3">{selectedEvent.description}</p>
              <div className="flex gap-2 pt-1">
                {selectedEvent.bookingUrl && (
                  <a href={selectedEvent.bookingUrl} target="_blank" rel="noopener noreferrer"
                    className="flex items-center gap-1 text-xs font-semibold px-2.5 py-1.5 rounded-md bg-green-700 text-white hover:bg-green-800">
                    <ExternalLink className="w-3 h-3" /> Book
                  </a>
                )}
                <button
                  onClick={() => downloadSingleEventIcal(selectedEvent)}
                  className="flex items-center gap-1 text-xs font-medium px-2.5 py-1.5 rounded-md border border-gray-300 text-gray-700 hover:bg-gray-50">
                  <Calendar className="w-3 h-3" /> iCal
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="bg-white border-t border-gray-200 py-2">
        <div className="container">
          <div className="flex flex-wrap gap-3 text-xs text-gray-600">
            <span className="font-semibold text-gray-700">Legend:</span>
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 rounded-full bg-green-800 inline-block border border-white shadow-sm" />
              Greenville (Home)
            </span>
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 rounded-full bg-purple-600 inline-block border border-white shadow-sm" />
              Music
            </span>
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 rounded-full bg-blue-600 inline-block border border-white shadow-sm" />
              Sports
            </span>
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 rounded-full bg-green-600 inline-block border border-white shadow-sm" />
              Nature
            </span>
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 rounded-full bg-amber-600 inline-block border border-white shadow-sm" />
              History
            </span>
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 rounded-full bg-pink-600 inline-block border border-white shadow-sm" />
              Arts
            </span>
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 rounded-full bg-teal-600 inline-block border border-white shadow-sm" />
              Festival
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
