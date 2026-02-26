// EventDatabase page - Output #1: Full interactive event database
// Design: Modern Trail Guide - forest green, burnt orange, warm cream
// Features: Search, filter by day/category/budget/indoor/city/dietary, sort, iCal export
import { useState, useMemo } from 'react';
import { EVENTS, ALL_CATEGORIES, ALL_CITIES, CATEGORY_ICONS, type DayFilter, type Category, type BudgetTier, type IndoorOutdoor } from '@/lib/eventsData';
import { downloadICalFile } from '@/lib/ical';
import EventCard from '@/components/EventCard';
import { Search, X, SlidersHorizontal, MapPin, Calendar, ChevronDown, Download, Leaf, Salad } from 'lucide-react';

const DAYS: DayFilter[] = ['Friday', 'Saturday', 'Sunday'];
const BUDGET_TIERS: BudgetTier[] = ['Free', '$', '$$', '$$$', '$$$$'];
const INDOOR_OUTDOOR: IndoorOutdoor[] = ['Indoor', 'Outdoor', 'Both'];

const SORT_OPTIONS = [
  { value: 'day-time', label: 'Day & Time' },
  { value: 'distance', label: 'Distance' },
  { value: 'price-low', label: 'Price: Low to High' },
  { value: 'price-high', label: 'Price: High to Low' },
  { value: 'city', label: 'City' },
];

const BUDGET_ORDER: Record<BudgetTier, number> = { 'Free': 0, '$': 1, '$$': 2, '$$$': 3, '$$$$': 4 };
const DAY_ORDER: Record<DayFilter, number> = { 'Friday': 0, 'Saturday': 1, 'Sunday': 2 };

const WEEKEND_STATS = {
  totalEvents: EVENTS.length,
  freeEvents: EVENTS.filter(e => e.budgetTier === 'Free').length,
  cities: ALL_CITIES.length,
  veganFriendly: EVENTS.filter(e => e.veganOptions === true).length,
};

export default function EventDatabase() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDays, setSelectedDays] = useState<DayFilter[]>([]);
  const [selectedCategories, setSelectedCategories] = useState<Category[]>([]);
  const [selectedBudgets, setSelectedBudgets] = useState<BudgetTier[]>([]);
  const [selectedIndoorOutdoor, setSelectedIndoorOutdoor] = useState<IndoorOutdoor[]>([]);
  const [selectedCities, setSelectedCities] = useState<string[]>([]);
  const [veganOnly, setVeganOnly] = useState(false);
  const [vegetarianOnly, setVegetarianOnly] = useState(false);
  const [sortBy, setSortBy] = useState('day-time');
  const [showFilters, setShowFilters] = useState(false);
  const [maxDistance, setMaxDistance] = useState(130);

  const toggleFilter = <T,>(arr: T[], setArr: (v: T[]) => void, val: T) => {
    setArr(arr.includes(val) ? arr.filter(x => x !== val) : [...arr, val]);
  };

  const clearAll = () => {
    setSearchQuery('');
    setSelectedDays([]);
    setSelectedCategories([]);
    setSelectedBudgets([]);
    setSelectedIndoorOutdoor([]);
    setSelectedCities([]);
    setVeganOnly(false);
    setVegetarianOnly(false);
    setMaxDistance(130);
    setSortBy('day-time');
  };

  const filtered = useMemo(() => {
    let result = EVENTS.filter(e => {
      if (searchQuery) {
        const q = searchQuery.toLowerCase();
        if (!e.name.toLowerCase().includes(q) &&
            !e.description.toLowerCase().includes(q) &&
            !e.city.toLowerCase().includes(q) &&
            !e.category.toLowerCase().includes(q) &&
            !e.tags.some(t => t.toLowerCase().includes(q))) return false;
      }
      if (selectedDays.length > 0 && !e.days.some(d => selectedDays.includes(d))) return false;
      if (selectedCategories.length > 0 && !selectedCategories.includes(e.category)) return false;
      if (selectedBudgets.length > 0 && !selectedBudgets.includes(e.budgetTier)) return false;
      if (selectedIndoorOutdoor.length > 0 && !selectedIndoorOutdoor.includes(e.indoorOutdoor)) return false;
      if (selectedCities.length > 0 && !selectedCities.includes(e.city)) return false;
      if (veganOnly && e.veganOptions !== true) return false;
      if (vegetarianOnly && e.vegetarianOptions !== true) return false;
      if (e.distanceMiles > maxDistance) return false;
      return true;
    });

    result = [...result].sort((a, b) => {
      switch (sortBy) {
        case 'day-time':
          const dayA = DAY_ORDER[a.days[0]] ?? 3;
          const dayB = DAY_ORDER[b.days[0]] ?? 3;
          return dayA !== dayB ? dayA - dayB : a.startTime.localeCompare(b.startTime);
        case 'distance':
          return a.distanceMiles - b.distanceMiles;
        case 'price-low':
          return BUDGET_ORDER[a.budgetTier] - BUDGET_ORDER[b.budgetTier];
        case 'price-high':
          return BUDGET_ORDER[b.budgetTier] - BUDGET_ORDER[a.budgetTier];
        case 'city':
          return a.city.localeCompare(b.city);
        default:
          return 0;
      }
    });

    return result;
  }, [searchQuery, selectedDays, selectedCategories, selectedBudgets, selectedIndoorOutdoor, selectedCities, veganOnly, vegetarianOnly, sortBy, maxDistance]);

  const activeFilterCount = selectedDays.length + selectedCategories.length + selectedBudgets.length +
    selectedIndoorOutdoor.length + selectedCities.length + (veganOnly ? 1 : 0) + (vegetarianOnly ? 1 : 0) +
    (maxDistance < 130 ? 1 : 0);

  const handleDownloadAll = () => {
    downloadICalFile(filtered, `Greenville-NC-Weekend-${filtered.length}-Events`);
  };

  return (
    <div className="min-h-screen bg-[#FAF7F0]">
      {/* Stats bar */}
      <div className="bg-green-800 text-white">
        <div className="container py-3">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-display font-bold text-amber-300">{WEEKEND_STATS.totalEvents}</div>
              <div className="text-xs text-green-300">Total Events</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-display font-bold text-amber-300">{WEEKEND_STATS.freeEvents}</div>
              <div className="text-xs text-green-300">Free Events</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-display font-bold text-amber-300">{WEEKEND_STATS.cities}</div>
              <div className="text-xs text-green-300">Cities Covered</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-display font-bold text-amber-300">{WEEKEND_STATS.veganFriendly}</div>
              <div className="text-xs text-green-300">Vegan-Friendly</div>
            </div>
          </div>
        </div>
      </div>

      {/* Sticky search & controls bar */}
      <div className="sticky top-[88px] z-20 bg-white/95 backdrop-blur-sm border-b border-gray-200 shadow-sm">
        <div className="container py-3">
          <div className="flex flex-wrap items-center gap-2.5">
            {/* Search */}
            <div className="relative flex-1 min-w-[180px]">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search events, cities, categories..."
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-8 py-2 text-sm border border-gray-200 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-green-600 focus:border-transparent"
              />
              {searchQuery && (
                <button onClick={() => setSearchQuery('')} className="absolute right-3 top-1/2 -translate-y-1/2">
                  <X className="w-3.5 h-3.5 text-gray-400 hover:text-gray-600" />
                </button>
              )}
            </div>

            {/* Filter toggle */}
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`flex items-center gap-2 px-3 py-2 text-sm font-medium rounded-lg border transition-colors ${showFilters || activeFilterCount > 0 ? 'bg-green-700 text-white border-green-700' : 'border-gray-300 text-gray-700 hover:bg-gray-50'}`}
            >
              <SlidersHorizontal className="w-4 h-4" />
              <span className="hidden sm:inline">Filters</span>
              {activeFilterCount > 0 && (
                <span className={`text-xs font-bold w-5 h-5 rounded-full flex items-center justify-center ${showFilters || activeFilterCount > 0 ? 'bg-white text-green-700' : 'bg-green-700 text-white'}`}>
                  {activeFilterCount}
                </span>
              )}
            </button>

            {/* Sort */}
            <div className="relative">
              <select
                value={sortBy}
                onChange={e => setSortBy(e.target.value)}
                className="appearance-none pl-3 pr-8 py-2 text-sm border border-gray-300 rounded-lg bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-green-600"
              >
                {SORT_OPTIONS.map(opt => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
              <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
            </div>

            {/* Results count & download */}
            <div className="flex items-center gap-2 ml-auto">
              <span className="text-sm text-gray-600 font-medium whitespace-nowrap">{filtered.length} events</span>
              <button
                onClick={handleDownloadAll}
                className="flex items-center gap-1.5 px-3 py-2 text-sm font-semibold rounded-lg bg-amber-600 text-white hover:bg-amber-700 transition-colors"
                title="Download all filtered events as .ics calendar file"
              >
                <Download className="w-4 h-4" />
                <span className="hidden sm:inline">Export iCal</span>
              </button>
            </div>
          </div>

          {/* Quick day filter chips */}
          {!showFilters && (
            <div className="flex flex-wrap gap-1.5 mt-2.5">
              {DAYS.map(day => (
                <button
                  key={day}
                  onClick={() => toggleFilter(selectedDays, setSelectedDays, day)}
                  className={`text-xs px-2.5 py-1 rounded-full border font-medium transition-colors ${
                    selectedDays.includes(day)
                      ? day === 'Friday' ? 'bg-blue-600 text-white border-blue-600'
                        : day === 'Saturday' ? 'bg-purple-600 text-white border-purple-600'
                        : 'bg-amber-600 text-white border-amber-600'
                      : 'border-gray-300 text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  {day === 'Friday' ? '⛅' : day === 'Saturday' ? '🌧️' : '🌤️'} {day}
                </button>
              ))}
              {ALL_CATEGORIES.map(cat => (
                <button
                  key={cat}
                  onClick={() => toggleFilter(selectedCategories, setSelectedCategories, cat)}
                  className={`text-xs px-2.5 py-1 rounded-full border font-medium transition-colors ${
                    selectedCategories.includes(cat)
                      ? 'bg-green-700 text-white border-green-700'
                      : 'border-gray-200 text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  {CATEGORY_ICONS[cat]} {cat}
                </button>
              ))}
            </div>
          )}

          {/* Expanded filters */}
          {showFilters && (
            <div className="mt-3 pt-3 border-t border-gray-100">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {/* Day filter */}
                <div>
                  <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2 flex items-center gap-1">
                    <Calendar className="w-3.5 h-3.5" /> Day
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {DAYS.map(day => (
                      <button
                        key={day}
                        onClick={() => toggleFilter(selectedDays, setSelectedDays, day)}
                        className={`text-xs px-2.5 py-1 rounded-full border font-medium transition-colors ${
                          selectedDays.includes(day)
                            ? day === 'Friday' ? 'bg-blue-600 text-white border-blue-600'
                              : day === 'Saturday' ? 'bg-purple-600 text-white border-purple-600'
                              : 'bg-amber-600 text-white border-amber-600'
                            : 'border-gray-300 text-gray-600 hover:bg-gray-50'
                        }`}
                      >
                        {day}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Budget filter */}
                <div>
                  <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Budget</p>
                  <div className="flex flex-wrap gap-1.5">
                    {BUDGET_TIERS.map(tier => (
                      <button
                        key={tier}
                        onClick={() => toggleFilter(selectedBudgets, setSelectedBudgets, tier)}
                        className={`text-xs px-2.5 py-1 rounded-full border font-medium transition-colors ${
                          selectedBudgets.includes(tier)
                            ? 'bg-green-700 text-white border-green-700'
                            : 'border-gray-300 text-gray-600 hover:bg-gray-50'
                        }`}
                      >
                        {tier === 'Free' ? '🆓 Free' : tier}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Indoor/Outdoor */}
                <div>
                  <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Setting</p>
                  <div className="flex flex-wrap gap-1.5">
                    {INDOOR_OUTDOOR.map(io => (
                      <button
                        key={io}
                        onClick={() => toggleFilter(selectedIndoorOutdoor, setSelectedIndoorOutdoor, io)}
                        className={`text-xs px-2.5 py-1 rounded-full border font-medium transition-colors ${
                          selectedIndoorOutdoor.includes(io)
                            ? 'bg-green-700 text-white border-green-700'
                            : 'border-gray-300 text-gray-600 hover:bg-gray-50'
                        }`}
                      >
                        {io === 'Indoor' ? '🏠' : io === 'Outdoor' ? '🌳' : '🔄'} {io}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Dietary */}
                <div>
                  <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Dietary</p>
                  <div className="flex flex-wrap gap-1.5">
                    <button
                      onClick={() => setVeganOnly(!veganOnly)}
                      className={`text-xs px-2.5 py-1 rounded-full border font-medium transition-colors ${veganOnly ? 'bg-emerald-600 text-white border-emerald-600' : 'border-gray-300 text-gray-600 hover:bg-gray-50'}`}
                    >
                      <Leaf className="w-3 h-3 inline mr-0.5" /> Vegan
                    </button>
                    <button
                      onClick={() => setVegetarianOnly(!vegetarianOnly)}
                      className={`text-xs px-2.5 py-1 rounded-full border font-medium transition-colors ${vegetarianOnly ? 'bg-lime-600 text-white border-lime-600' : 'border-gray-300 text-gray-600 hover:bg-gray-50'}`}
                    >
                      <Salad className="w-3 h-3 inline mr-0.5" /> Vegetarian
                    </button>
                  </div>
                </div>

                {/* Distance slider */}
                <div className="sm:col-span-2">
                  <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2 flex items-center gap-1">
                    <MapPin className="w-3.5 h-3.5" /> Max Distance: {maxDistance === 130 ? 'Any' : `${maxDistance} miles`}
                  </p>
                  <input
                    type="range"
                    min={0}
                    max={130}
                    step={10}
                    value={maxDistance}
                    onChange={e => setMaxDistance(Number(e.target.value))}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-green-700"
                  />
                  <div className="flex justify-between text-xs text-gray-400 mt-1">
                    <span>Local</span><span>50 mi</span><span>100 mi</span><span>130 mi</span>
                  </div>
                </div>

                {/* City filter */}
                <div className="sm:col-span-2">
                  <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">City</p>
                  <div className="flex flex-wrap gap-1.5">
                    {ALL_CITIES.map(city => (
                      <button
                        key={city}
                        onClick={() => toggleFilter(selectedCities, setSelectedCities, city)}
                        className={`text-xs px-2.5 py-1 rounded-full border font-medium transition-colors ${
                          selectedCities.includes(city)
                            ? 'bg-green-700 text-white border-green-700'
                            : 'border-gray-300 text-gray-600 hover:bg-gray-50'
                        }`}
                      >
                        {city}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Category filter - full width */}
              <div className="mt-3">
                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Category</p>
                <div className="flex flex-wrap gap-1.5">
                  {ALL_CATEGORIES.map(cat => (
                    <button
                      key={cat}
                      onClick={() => toggleFilter(selectedCategories, setSelectedCategories, cat)}
                      className={`text-xs px-2.5 py-1 rounded-full border font-medium transition-colors ${
                        selectedCategories.includes(cat)
                          ? 'bg-green-700 text-white border-green-700'
                          : 'border-gray-300 text-gray-600 hover:bg-gray-50'
                      }`}
                    >
                      {CATEGORY_ICONS[cat]} {cat}
                    </button>
                  ))}
                </div>
              </div>

              {activeFilterCount > 0 && (
                <button
                  onClick={clearAll}
                  className="mt-3 text-xs text-red-600 hover:text-red-800 font-medium flex items-center gap-1"
                >
                  <X className="w-3 h-3" /> Clear all filters
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Event grid */}
      <div className="container py-6">
        {filtered.length === 0 ? (
          <div className="text-center py-20">
            <div className="text-5xl mb-4">🔍</div>
            <h3 className="font-display text-xl text-gray-700 mb-2">No events match your filters</h3>
            <p className="text-gray-500 text-sm mb-4">Try adjusting your search or clearing some filters.</p>
            <button onClick={clearAll} className="text-sm text-green-700 hover:text-green-900 font-medium underline">
              Clear all filters
            </button>
          </div>
        ) : (
          <>
            {/* Group by day */}
            {(['Friday', 'Saturday', 'Sunday'] as DayFilter[]).map(day => {
              const dayEvents = filtered.filter(e => e.days.includes(day));
              if (dayEvents.length === 0) return null;
              const dayWeather = { Friday: '⛅ Partly Cloudy 50°F', Saturday: '🌧️ Rain Possible 59°F', Sunday: '🌤️ Mostly Clear 69°F' };
              const dayBorderColors = { Friday: 'border-blue-400', Saturday: 'border-purple-400', Sunday: 'border-amber-400' };
              const dayTextColors = { Friday: 'text-blue-700', Saturday: 'text-purple-700', Sunday: 'text-amber-700' };
              return (
                <div key={day} className="mb-10">
                  <div className={`flex items-center gap-3 mb-4 pb-2 border-b-2 ${dayBorderColors[day]}`}>
                    <h2 className={`font-display text-2xl font-bold ${dayTextColors[day]}`}>{day}</h2>
                    <span className="text-sm font-medium text-gray-500">{dayWeather[day]}</span>
                    <span className="ml-auto text-sm text-gray-500 font-medium">{dayEvents.length} event{dayEvents.length !== 1 ? 's' : ''}</span>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                    {dayEvents.map(event => (
                      <EventCard key={event.id} event={event} />
                    ))}
                  </div>
                </div>
              );
            })}
          </>
        )}
      </div>
    </div>
  );
}
