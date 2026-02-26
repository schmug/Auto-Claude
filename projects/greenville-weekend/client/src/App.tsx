// App.tsx - Greenville NC Weekend Itinerary Generator
// Design: Modern Trail Guide - forest green, burnt orange, warm cream
// Navigation: top header with weather strip, tab-based routing
import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Route, Switch, Link, useLocation } from "wouter";
import ErrorBoundary from "./components/ErrorBoundary";
import { ThemeProvider } from "./contexts/ThemeContext";
import EventDatabase from "./pages/EventDatabase";
import Itineraries from "./pages/Itineraries";
import MapViewPage from "./pages/MapViewPage";
import NotFound from "./pages/NotFound";
import { List, Compass, Map } from "lucide-react";

const WEEKEND_WEATHER = [
  { day: 'Fri 2/27', icon: '⛅', temp: '50°F', note: 'Partly Cloudy' },
  { day: 'Sat 2/28', icon: '🌧️', temp: '59°F', note: 'Rain Possible' },
  { day: 'Sun 3/1', icon: '🌤️', temp: '69°F', note: 'Mostly Clear' },
];

function Nav() {
  const [location] = useLocation();

  const links = [
    { href: '/', label: 'Event Database', shortLabel: 'Events', icon: <List className="w-4 h-4" /> },
    { href: '/itineraries', label: 'Curated Itineraries', shortLabel: 'Itineraries', icon: <Compass className="w-4 h-4" /> },
    { href: '/map', label: 'Map View', shortLabel: 'Map', icon: <Map className="w-4 h-4" /> },
  ];

  return (
    <header className="bg-green-900 text-white shadow-lg sticky top-0 z-30">
      {/* Top bar */}
      <div className="container py-2.5">
        <div className="flex items-center justify-between gap-3">
          {/* Logo */}
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 bg-amber-500 rounded-lg flex items-center justify-center text-white font-bold text-sm shadow-md shrink-0">
              GNC
            </div>
            <div>
              <div className="font-display text-base sm:text-lg font-bold leading-tight">Greenville NC Weekend</div>
              <div className="text-xs text-green-300 leading-tight hidden sm:block">Events within 2-hour drive · Feb 27 – Mar 1, 2026</div>
            </div>
          </div>

          {/* Weather strip - hidden on very small screens */}
          <div className="hidden md:flex items-center gap-4">
            {WEEKEND_WEATHER.map(w => (
              <div key={w.day} className="text-center">
                <div className="text-xs text-green-400 font-medium">{w.day}</div>
                <div className="text-sm font-semibold">{w.icon} {w.temp}</div>
                <div className="text-xs text-green-400">{w.note}</div>
              </div>
            ))}
          </div>

          {/* Mobile weather - compact */}
          <div className="flex md:hidden items-center gap-2">
            {WEEKEND_WEATHER.map(w => (
              <div key={w.day} className="text-center">
                <div className="text-xs text-green-400">{w.day.split(' ')[0]}</div>
                <div className="text-sm">{w.icon}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Nav tabs */}
      <div className="border-t border-green-800">
        <div className="container">
          <nav className="flex">
            {links.map(link => (
              <Link key={link.href} href={link.href}>
                <a className={`flex items-center gap-1.5 px-3 sm:px-5 py-2.5 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
                  location === link.href
                    ? 'border-amber-400 text-amber-300 bg-green-800/50'
                    : 'border-transparent text-green-300 hover:text-white hover:border-green-600'
                }`}>
                  {link.icon}
                  <span className="hidden sm:inline">{link.label}</span>
                  <span className="sm:hidden">{link.shortLabel}</span>
                </a>
              </Link>
            ))}
          </nav>
        </div>
      </div>
    </header>
  );
}

function Router() {
  return (
    <Switch>
      <Route path="/" component={EventDatabase} />
      <Route path="/itineraries" component={Itineraries} />
      <Route path="/map" component={MapViewPage} />
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider defaultTheme="light">
        <TooltipProvider>
          <Toaster />
          <div className="min-h-screen flex flex-col bg-[#FAF7F0]">
            <Nav />
            <main className="flex-1">
              <Router />
            </main>
            <footer className="bg-green-900 text-green-400 text-xs py-3">
              <div className="container flex flex-wrap items-center justify-between gap-2">
                <span>Greenville NC Weekend Guide · Feb 27 – Mar 1, 2026 · 45 events within 2-hour drive</span>
                <span className="text-green-500">Always verify event details before attending</span>
              </div>
            </footer>
          </div>
        </TooltipProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
