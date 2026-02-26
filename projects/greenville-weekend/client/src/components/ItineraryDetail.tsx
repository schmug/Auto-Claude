// ItineraryDetail - full itinerary view with schedule, food, weather, iCal export
import type { Itinerary } from '@/lib/itinerariesData';
import { downloadICalFile } from '@/lib/ical';
import { EVENTS } from '@/lib/eventsData';
import { MapPin, Clock, DollarSign, Car, Download, ExternalLink, Leaf, Salad, Sun, CloudRain, Info, Utensils, ChevronRight } from 'lucide-react';

interface ItineraryDetailProps {
  itinerary: Itinerary;
}

const PERIOD_ICONS = { Morning: '🌅', Afternoon: '☀️', Evening: '🌙' };
const PERIOD_COLORS = {
  Morning: 'bg-amber-50 border-amber-200 text-amber-800',
  Afternoon: 'bg-blue-50 border-blue-200 text-blue-800',
  Evening: 'bg-indigo-50 border-indigo-200 text-indigo-800',
};

export default function ItineraryDetail({ itinerary }: ItineraryDetailProps) {
  // Find matching events from our database for iCal export
  const matchingEvents = EVENTS.filter(e =>
    e.city === itinerary.city ||
    itinerary.schedule.some(day =>
      day.stops.some(stop =>
        stop.activity.toLowerCase().includes(e.name.toLowerCase().substring(0, 15))
      )
    )
  );

  const handleExportIcal = () => {
    if (matchingEvents.length > 0) {
      downloadICalFile(matchingEvents, `${itinerary.title} - Greenville NC Weekend`);
    } else {
      alert('No matching calendar events found for this itinerary. Use the Event Database to export individual events.');
    }
  };

  const allStops = itinerary.schedule.flatMap(d => d.stops);
  const foodStops = allStops.filter(s => s.isFood);
  const veganStops = foodStops.filter(s => s.veganFriendly);
  const vegStops = foodStops.filter(s => s.vegetarianFriendly);

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      {/* Hero header */}
      <div className="bg-gradient-to-br from-green-800 to-green-900 text-white p-6">
        <div className="flex items-start justify-between gap-4 mb-3">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-2xl">{itinerary.themeIcon}</span>
              <span className="text-sm font-medium bg-white/20 px-2 py-0.5 rounded-full">{itinerary.theme}</span>
            </div>
            <h2 className="font-display text-2xl font-bold leading-tight">{itinerary.title}</h2>
            <p className="text-green-200 text-sm mt-1">{itinerary.subtitle}</p>
          </div>
          <button
            onClick={handleExportIcal}
            className="shrink-0 flex items-center gap-1.5 px-3 py-2 text-sm font-semibold rounded-lg bg-amber-500 hover:bg-amber-400 text-white transition-colors"
          >
            <Download className="w-4 h-4" />
            <span className="hidden sm:inline">Export iCal</span>
          </button>
        </div>

        {/* Key stats */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-4">
          <div className="bg-white/10 rounded-lg p-2.5">
            <div className="text-xs text-green-300 mb-0.5">City</div>
            <div className="text-sm font-semibold flex items-center gap-1">
              <MapPin className="w-3.5 h-3.5" />{itinerary.city}
            </div>
          </div>
          <div className="bg-white/10 rounded-lg p-2.5">
            <div className="text-xs text-green-300 mb-0.5">Drive Time</div>
            <div className="text-sm font-semibold flex items-center gap-1">
              <Car className="w-3.5 h-3.5" />
              {itinerary.driveTimeMinutes === 0 ? 'Local' : `${itinerary.driveTimeMinutes} min`}
            </div>
          </div>
          <div className="bg-white/10 rounded-lg p-2.5">
            <div className="text-xs text-green-300 mb-0.5">Est. Cost</div>
            <div className="text-sm font-semibold flex items-center gap-1">
              <DollarSign className="w-3.5 h-3.5" />{itinerary.costRange}
            </div>
          </div>
          <div className="bg-white/10 rounded-lg p-2.5">
            <div className="text-xs text-green-300 mb-0.5">Best Day</div>
            <div className="text-sm font-semibold">{itinerary.day}</div>
          </div>
        </div>
      </div>

      <div className="p-5">
        {/* Highlights */}
        <div className="mb-5">
          <h3 className="font-display text-base font-semibold text-gray-800 mb-2">Highlights</h3>
          <ul className="space-y-1">
            {itinerary.highlights.map((h, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                <ChevronRight className="w-4 h-4 text-green-600 shrink-0 mt-0.5" />
                {h}
              </li>
            ))}
          </ul>
        </div>

        {/* Schedule */}
        <div className="mb-5">
          <h3 className="font-display text-base font-semibold text-gray-800 mb-3">Full Schedule</h3>
          <div className="space-y-4">
            {itinerary.schedule.map((period, pi) => (
              <div key={pi}>
                <div className={`inline-flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-full border mb-2 ${PERIOD_COLORS[period.period]}`}>
                  {PERIOD_ICONS[period.period]} {period.period}
                </div>
                <div className="space-y-2 ml-2">
                  {period.stops.map((stop, si) => (
                    <div key={si} className={`relative pl-4 pb-3 border-l-2 ${si === period.stops.length - 1 ? 'border-transparent' : 'border-gray-200'}`}>
                      <div className="absolute left-[-5px] top-1 w-2.5 h-2.5 rounded-full bg-green-600 border-2 border-white shadow-sm" />
                      <div className="flex flex-wrap items-start justify-between gap-1 mb-0.5">
                        <div>
                          <span className="text-xs font-bold text-green-700 mr-2">{stop.time}</span>
                          <span className="text-sm font-semibold text-gray-900">{stop.activity}</span>
                          {stop.isFood && <Utensils className="w-3.5 h-3.5 text-amber-600 inline ml-1.5" />}
                        </div>
                        <div className="flex items-center gap-1.5">
                          <span className="text-xs font-medium text-gray-700">{stop.price}</span>
                          <span className="text-xs text-gray-400">· {stop.duration}</span>
                        </div>
                      </div>
                      <div className="text-xs text-gray-500 mb-1 flex items-center gap-1">
                        <MapPin className="w-3 h-3" />{stop.location}
                      </div>
                      {stop.notes && (
                        <p className="text-xs text-gray-600 leading-relaxed">{stop.notes}</p>
                      )}
                      {/* Dietary info for food stops */}
                      {stop.isFood && (
                        <div className="mt-1 flex flex-wrap gap-1">
                          {stop.veganFriendly && stop.veganDishes && (
                            <span className="text-xs bg-emerald-50 text-emerald-700 border border-emerald-200 px-2 py-0.5 rounded-full flex items-center gap-1">
                              <Leaf className="w-3 h-3" /> Vegan: {stop.veganDishes.slice(0, 2).join(', ')}
                            </span>
                          )}
                          {stop.vegetarianFriendly && !stop.veganFriendly && stop.vegetarianDishes && (
                            <span className="text-xs bg-lime-50 text-lime-700 border border-lime-200 px-2 py-0.5 rounded-full flex items-center gap-1">
                              <Salad className="w-3 h-3" /> Veg: {stop.vegetarianDishes.slice(0, 2).join(', ')}
                            </span>
                          )}
                        </div>
                      )}
                      {/* Links */}
                      <div className="flex gap-2 mt-1.5">
                        {stop.bookingUrl && (
                          <a href={stop.bookingUrl} target="_blank" rel="noopener noreferrer"
                            className="text-xs text-green-700 hover:text-green-900 font-medium flex items-center gap-0.5">
                            <ExternalLink className="w-3 h-3" /> Book
                          </a>
                        )}
                        {stop.infoUrl && (
                          <a href={stop.infoUrl} target="_blank" rel="noopener noreferrer"
                            className="text-xs text-gray-500 hover:text-gray-700 flex items-center gap-0.5">
                            <Info className="w-3 h-3" /> Info
                          </a>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Food & Dietary Summary */}
        {foodStops.length > 0 && (
          <div className="mb-5 p-4 bg-amber-50 rounded-lg border border-amber-200">
            <h3 className="font-display text-sm font-semibold text-amber-900 mb-2 flex items-center gap-1.5">
              <Utensils className="w-4 h-4" /> Food Stops ({foodStops.length})
            </h3>
            <div className="space-y-2">
              {foodStops.map((stop, i) => (
                <div key={i} className="flex items-start justify-between gap-2">
                  <div>
                    <span className="text-sm font-medium text-gray-800">{stop.location}</span>
                    <div className="flex flex-wrap gap-1 mt-0.5">
                      {stop.veganFriendly && (
                        <span className="text-xs bg-emerald-100 text-emerald-700 px-1.5 py-0.5 rounded-full flex items-center gap-0.5">
                          <Leaf className="w-3 h-3" /> Vegan options
                        </span>
                      )}
                      {stop.vegetarianFriendly && (
                        <span className="text-xs bg-lime-100 text-lime-700 px-1.5 py-0.5 rounded-full flex items-center gap-0.5">
                          <Salad className="w-3 h-3" /> Vegetarian options
                        </span>
                      )}
                    </div>
                  </div>
                  <span className="text-xs font-medium text-gray-600 shrink-0">{stop.price}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Weather Plans */}
        <div className="mb-5">
          <h3 className="font-display text-sm font-semibold text-gray-800 mb-2">Weather Plans</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {itinerary.weatherPlans.map((plan, i) => (
              <div key={i} className={`p-3 rounded-lg border ${plan.condition === 'Good Weather' ? 'bg-blue-50 border-blue-200' : 'bg-gray-50 border-gray-200'}`}>
                <div className="flex items-center gap-1.5 mb-1.5">
                  {plan.condition === 'Good Weather' ? <Sun className="w-4 h-4 text-amber-500" /> : <CloudRain className="w-4 h-4 text-blue-500" />}
                  <span className="text-xs font-semibold text-gray-800">{plan.condition}</span>
                </div>
                <p className="text-xs text-gray-600 mb-1.5">{plan.description}</p>
                <ul className="space-y-1">
                  {plan.adjustments.map((adj, j) => (
                    <li key={j} className="text-xs text-gray-600 flex items-start gap-1">
                      <span className="text-gray-400 shrink-0">•</span>{adj}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        {/* Practical Info */}
        <div className="p-4 bg-green-50 rounded-lg border border-green-200">
          <h3 className="font-display text-sm font-semibold text-green-900 mb-2 flex items-center gap-1.5">
            <Info className="w-4 h-4" /> Practical Info
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
            <div>
              <span className="text-xs font-semibold text-green-800">Depart:</span>
              <span className="text-xs text-gray-700 ml-1">{itinerary.practicalInfo.departureTime}</span>
            </div>
            <div>
              <span className="text-xs font-semibold text-green-800">Return:</span>
              <span className="text-xs text-gray-700 ml-1">{itinerary.practicalInfo.returnTime}</span>
            </div>
            <div className="sm:col-span-2">
              <span className="text-xs font-semibold text-green-800">Parking:</span>
              <span className="text-xs text-gray-700 ml-1">{itinerary.practicalInfo.parking}</span>
            </div>
            <div className="sm:col-span-2">
              <span className="text-xs font-semibold text-green-800">Route:</span>
              <span className="text-xs text-gray-700 ml-1">{itinerary.practicalInfo.drivingRoute}</span>
            </div>
          </div>
          <div>
            <span className="text-xs font-semibold text-green-800 block mb-1">Tips:</span>
            <ul className="space-y-1">
              {itinerary.practicalInfo.tips.map((tip, i) => (
                <li key={i} className="text-xs text-gray-600 flex items-start gap-1">
                  <span className="text-green-600 shrink-0">✓</span>{tip}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
