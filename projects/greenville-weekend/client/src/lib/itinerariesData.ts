// =============================================================================
// CURATED ITINERARIES DATA
// 6 pre-planned day trips from Greenville, NC
// Weekend: February 27 (Friday) - March 1 (Sunday), 2026
// =============================================================================

export interface ItineraryStop {
  time: string;
  activity: string;
  location: string;
  address: string;
  duration: string;
  price: string;
  notes?: string;
  bookingUrl?: string;
  infoUrl?: string;
  isFood?: boolean;
  veganFriendly?: boolean;
  vegetarianFriendly?: boolean;
  veganDishes?: string[];
  vegetarianDishes?: string[];
}

export interface ItineraryDay {
  period: 'Morning' | 'Afternoon' | 'Evening';
  stops: ItineraryStop[];
}

export interface WeatherPlan {
  condition: 'Good Weather' | 'Rain Alternative';
  description: string;
  adjustments: string[];
}

export interface Itinerary {
  id: string;
  title: string;
  subtitle: string;
  city: string;
  distanceMiles: number;
  driveTimeMinutes: number;
  day: 'Friday' | 'Saturday' | 'Sunday' | 'Any Day';
  weather: string;
  weatherIcon: string;
  theme: string;
  themeIcon: string;
  costRange: string;
  budgetTier: string;
  highlights: string[];
  schedule: ItineraryDay[];
  weatherPlans: WeatherPlan[];
  practicalInfo: {
    departureTime: string;
    returnTime: string;
    parking: string;
    drivingRoute: string;
    tips: string[];
  };
  coverImage?: string;
  tags: string[];
}

export const ITINERARIES: Itinerary[] = [
  // ─── ITINERARY 1: WILMINGTON CULTURAL WEEKEND ────────────────────────────────
  {
    id: 'wilmington-culture',
    title: 'Wilmington Arts & Irish Weekend',
    subtitle: 'Theater, Gallery Crawl & Celtic Celebration',
    city: 'Wilmington',
    distanceMiles: 120,
    driveTimeMinutes: 120,
    day: 'Friday',
    weather: 'Rain Possible 57°F',
    weatherIcon: '🌧️',
    theme: 'Arts & Culture',
    themeIcon: '🎭',
    costRange: '$30–$100/person',
    budgetTier: '$$–$$$',
    highlights: [
      'Fourth Friday Gallery Night (Free)',
      "'To Kill a Mockingbird' at Thalian Hall",
      'Historic downtown Wilmington riverfront',
      'Cape Fear Hooley Irish Festival (Saturday)',
    ],
    schedule: [
      {
        period: 'Morning',
        stops: [
          {
            time: '8:00 AM',
            activity: 'Depart Greenville',
            location: 'Greenville, NC',
            address: 'Greenville, NC 27858',
            duration: '2 hours drive',
            price: 'Gas ~$15',
            notes: 'Take US-264 W to I-40 E toward Wilmington. Arrive ~10 AM.',
          },
          {
            time: '10:00 AM',
            activity: 'Breakfast at Boca Bay',
            location: 'Boca Bay Restaurant',
            address: '2025 Eastwood Rd, Wilmington, NC 28403',
            duration: '1 hour',
            price: '$12–$18',
            isFood: true,
            vegetarianFriendly: true,
            vegetarianDishes: ['Avocado Toast', 'Veggie Omelette', 'Acai Bowl'],
            veganFriendly: true,
            veganDishes: ['Acai Bowl', 'Avocado Toast (no egg)'],
            notes: 'Casual coastal breakfast spot near Wrightsville Beach.',
          },
        ],
      },
      {
        period: 'Afternoon',
        stops: [
          {
            time: '11:30 AM',
            activity: 'Explore Historic Downtown Wilmington',
            location: 'Riverwalk & Historic District',
            address: 'Water St, Wilmington, NC 28401',
            duration: '2 hours',
            price: 'Free',
            notes: 'Walk the 1.75-mile Riverwalk along the Cape Fear River. Browse shops on Front Street. Visit the USS North Carolina Battleship (visible from riverwalk).',
            infoUrl: 'https://www.wilmingtondowntown.com/',
          },
          {
            time: '1:30 PM',
            activity: 'Lunch at Rx Restaurant & Bar',
            location: 'Rx Restaurant',
            address: '421 Castle St, Wilmington, NC 28401',
            duration: '1.5 hours',
            price: '$15–$25',
            isFood: true,
            vegetarianFriendly: true,
            veganFriendly: true,
            vegetarianDishes: ['Roasted Beet Salad', 'Grain Bowl', 'Veggie Flatbread'],
            veganDishes: ['Grain Bowl (vegan option)', 'Roasted Beet Salad'],
            notes: 'Farm-to-table restaurant in a converted pharmacy. Excellent cocktails.',
          },
          {
            time: '3:00 PM',
            activity: 'Burgwin-Wright House & Gardens',
            location: 'Burgwin-Wright House',
            address: '224 Market St, Wilmington, NC 28401',
            duration: '1 hour',
            price: '$10',
            notes: 'Colonial-era house museum with beautiful gardens. Opening reception for "Salt Sisters: Marsh to Mellow" art exhibit during Fourth Friday.',
            infoUrl: 'https://www.burgwinwrighthouse.com/',
          },
          {
            time: '4:30 PM',
            activity: 'Historic Happy Hour Walking Tour',
            location: 'Starting at Gazebo Bar',
            address: 'Downtown Wilmington',
            duration: '1.5 hours',
            price: '$30',
            notes: '1.5-mile walk through Wilmington history with stops at wine bars.',
            bookingUrl: 'https://www.eventbrite.com/d/nc--wilmington/wine-tasting-events/',
          },
        ],
      },
      {
        period: 'Evening',
        stops: [
          {
            time: '6:00 PM',
            activity: 'Fourth Friday Gallery Night',
            location: 'Downtown Wilmington Galleries',
            address: 'Multiple venues, Downtown Wilmington',
            duration: '2 hours',
            price: 'Free',
            notes: 'Self-guided gallery crawl. Highlights: Cathryn O\'Donnell Gallery (closing reception), WHQR MC Erny Gallery. Full list at ArtsWilmington.org.',
            infoUrl: 'https://artswilmington.org/',
          },
          {
            time: '8:00 PM',
            activity: "Dinner at Circa 1922",
            location: 'Circa 1922',
            address: '8 N Front St, Wilmington, NC 28401',
            duration: '1.5 hours',
            price: '$25–$45',
            isFood: true,
            vegetarianFriendly: true,
            vegetarianDishes: ['Mushroom Risotto', 'Caprese Salad', 'Pasta Primavera'],
            notes: 'Upscale tapas in a historic building. Perfect pre-theater dinner.',
          },
          {
            time: '9:30 PM',
            activity: "'To Kill a Mockingbird' at Thalian Hall",
            location: 'Thalian Hall',
            address: '310 Chestnut St, Wilmington, NC 28401',
            duration: '2 hours',
            price: 'Check website',
            notes: 'Starring Cullen Moss (Netflix\'s Outer Banks) as Atticus Finch. Powerful theatrical experience.',
            bookingUrl: 'https://www.thalianhall.org/',
          },
        ],
      },
    ],
    weatherPlans: [
      {
        condition: 'Good Weather',
        description: 'Enjoy the full outdoor experience',
        adjustments: [
          'Add a morning walk on Wrightsville Beach (20 min from downtown)',
          'Extend Riverwalk stroll to include Greenfield Lake Park',
          'Consider outdoor dining at Front Street Brewery patio',
        ],
      },
      {
        condition: 'Rain Alternative',
        description: 'Friday has some rain possible — pivot to indoor activities',
        adjustments: [
          'Skip the walking tour; visit Cameron Art Museum instead ($8)',
          'Spend more time at indoor galleries during Fourth Friday',
          'Add Geoffrey Asmus comedy show at Dead Crow (7 PM, $30–$42)',
        ],
      },
    ],
    practicalInfo: {
      departureTime: '8:00 AM from Greenville',
      returnTime: '11:30 PM–12:00 AM (after show)',
      parking: 'Free parking at Wilmington Convention Center garage on weekends. Street parking available downtown.',
      drivingRoute: 'US-264 W to I-40 E → Exit 420B toward Downtown Wilmington. ~2 hours.',
      tips: [
        'Book Thalian Hall tickets in advance — shows often sell out',
        'Fourth Friday is free but galleries can get crowded after 7 PM',
        'Uber/Lyft available in downtown Wilmington for evening',
        'Consider staying overnight to catch Saturday\'s Cape Fear Hooley',
      ],
    },
    tags: ['theater', 'art', 'gallery', 'Irish', 'historic', 'nightlife', 'culture'],
  },

  // ─── ITINERARY 2: RALEIGH CULTURE & FOOD ─────────────────────────────────────
  {
    id: 'raleigh-culture-food',
    title: 'Raleigh Cultural Saturday',
    subtitle: 'African American Cultural Celebration, Museums & Craft Beer',
    city: 'Raleigh',
    distanceMiles: 85,
    driveTimeMinutes: 81,
    day: 'Saturday',
    weather: 'Rain Possible 59°F',
    weatherIcon: '🌧️',
    theme: 'Arts & Culture',
    themeIcon: '🎨',
    costRange: '$20–$60/person',
    budgetTier: '$–$$',
    highlights: [
      '25th Annual African American Cultural Celebration (FREE)',
      'NC Museum of Natural Sciences (FREE)',
      'Historic Mordecai Park',
      'Raleigh Brewing live music',
    ],
    schedule: [
      {
        period: 'Morning',
        stops: [
          {
            time: '7:30 AM',
            activity: 'Depart Greenville',
            location: 'Greenville, NC',
            address: 'Greenville, NC 27858',
            duration: '1.5 hours drive',
            price: 'Gas ~$12',
            notes: 'Take US-264 W toward Raleigh. Arrive ~9 AM.',
          },
          {
            time: '9:00 AM',
            activity: 'Breakfast at Beasley\'s Chicken + Honey',
            location: "Beasley's Chicken + Honey",
            address: '237 S Wilmington St, Raleigh, NC 27601',
            duration: '1 hour',
            price: '$10–$18',
            isFood: true,
            vegetarianFriendly: true,
            vegetarianDishes: ['Honey Biscuits', 'Veggie Hash', 'Pancakes'],
            notes: 'Award-winning Southern breakfast spot in downtown Raleigh.',
          },
          {
            time: '10:00 AM',
            activity: 'NC Museum of Natural Sciences',
            location: 'NC Museum of Natural Sciences',
            address: '11 West Jones Street, Raleigh, NC 27601',
            duration: '1.5 hours',
            price: 'Free (3D movies: donations)',
            notes: 'Largest natural history museum in the Southeast. See live animals, 3D movies, and hands-on exhibits. Daily ranger programs.',
            infoUrl: 'https://naturalsciences.org/',
          },
        ],
      },
      {
        period: 'Afternoon',
        stops: [
          {
            time: '10:30 AM',
            activity: '25th Annual African American Cultural Celebration',
            location: 'NC Museum of Art',
            address: '2110 Blue Ridge Rd, Raleigh, NC 27607',
            duration: '4 hours',
            price: 'Free',
            notes: 'Runs 10:30 AM–4:30 PM. Live performances, demonstrations, art, food vendors, and community. Celebrating Black History Month. A highlight of the Raleigh calendar.',
            bookingUrl: 'https://ncartmuseum.org/events/25th-annual-african-american-cultural-celebration/',
            infoUrl: 'https://www.ncmuseumofhistory.org/aacc',
          },
          {
            time: '1:00 PM',
            activity: 'Lunch at the AACC Food Vendors',
            location: 'NC Museum of Art (AACC)',
            address: '2110 Blue Ridge Rd, Raleigh, NC 27607',
            duration: '45 min',
            price: '$10–$20',
            isFood: true,
            vegetarianFriendly: true,
            notes: 'Food vendors at the celebration offer diverse options including vegetarian choices.',
          },
          {
            time: '3:00 PM',
            activity: 'Mordecai Historic Park Tour',
            location: 'Mordecai Historic Park',
            address: '1 Mimosa St, Raleigh, NC 27604',
            duration: '1.5 hours',
            price: 'Free–$5',
            notes: 'Tour the 1785 Mordecai House and birthplace of President Andrew Johnson. Last tour at 3 PM. Guided tours available.',
            infoUrl: 'https://www.raleigh-nc.org/parks/mordecai-historic-park',
          },
          {
            time: '5:00 PM',
            activity: "Pinot's Palette – Goldfinch & Thistles Paint Class",
            location: "Pinot's Palette Brier Creek",
            address: '10410 Moncreiffe Road Suite 101, Raleigh, NC',
            duration: '2 hours',
            price: '$39',
            notes: 'Guided painting class 3–5 PM. BYOB welcome. All materials provided. Perfect rainy Saturday activity.',
            bookingUrl: 'https://www.pinotspalette.com/briercreek',
          },
        ],
      },
      {
        period: 'Evening',
        stops: [
          {
            time: '6:30 PM',
            activity: 'Dinner at Bida Manda',
            location: 'Bida Manda Laotian Restaurant',
            address: '222 S Blount St, Raleigh, NC 27601',
            duration: '1.5 hours',
            price: '$20–$35',
            isFood: true,
            vegetarianFriendly: true,
            veganFriendly: true,
            vegetarianDishes: ['Papaya Salad', 'Tofu Larb', 'Vegetable Curry'],
            veganDishes: ['Papaya Salad (vegan)', 'Tofu Larb', 'Steamed Rice with Vegetables'],
            notes: 'James Beard-nominated Laotian restaurant. Outstanding vegetarian and vegan options.',
          },
          {
            time: '9:00 PM',
            activity: 'RBC After Dark: Zac Lor Live at Raleigh Brewing',
            location: 'Raleigh Brewing Company',
            address: '3709 Neil St, Raleigh, NC 27607',
            duration: '3 hours',
            price: 'TBD',
            notes: 'Live music 9 PM–midnight. Craft beers, vegetarian food options. Great way to end a cultural Saturday.',
            bookingUrl: 'https://www.raleighbrewing.com/upcoming-events',
          },
        ],
      },
    ],
    weatherPlans: [
      {
        condition: 'Good Weather',
        description: 'Saturday has rain in the forecast — most activities are indoors',
        adjustments: [
          'If rain clears, visit NC Museum of Art outdoor sculpture garden',
          'Walk the Neuse River Greenway near Mordecai Park',
        ],
      },
      {
        condition: 'Rain Alternative',
        description: 'This itinerary is mostly rain-proof — all major activities are indoor',
        adjustments: [
          'All activities are indoors — no changes needed',
          'Add Duke vs. Virginia basketball at Cameron Indoor (12 PM, from $17)',
          'Visit NC History Museum (free, downtown Raleigh)',
        ],
      },
    ],
    practicalInfo: {
      departureTime: '7:30 AM from Greenville',
      returnTime: '12:30 AM (after Raleigh Brewing)',
      parking: 'Free street parking on weekends downtown. Moore Square Parking Deck near museums.',
      drivingRoute: 'US-264 W to I-440 → Follow signs to downtown Raleigh. ~1.5 hours.',
      tips: [
        'AACC is free but can get crowded — arrive early for best parking at NC Museum of Art',
        'Paint class requires advance booking at Pinot\'s Palette',
        'Raleigh Brewing is 15 min from downtown — consider Uber',
        'Excellent day for families with children (museums are free)',
      ],
    },
    tags: ['culture', 'museum', 'art', 'free', 'brewery', 'family', 'Black History Month'],
  },

  // ─── ITINERARY 3: COASTAL NATURE DAY ─────────────────────────────────────────
  {
    id: 'crystal-coast-nature',
    title: 'Crystal Coast Nature Escape',
    subtitle: 'Aquarium, Beaches & Coastal Trails',
    city: 'Pine Knoll Shores / Morehead City',
    distanceMiles: 90,
    driveTimeMinutes: 90,
    day: 'Sunday',
    weather: 'Mostly Clear 69°F',
    weatherIcon: '🌤️',
    theme: 'Nature & Outdoors',
    themeIcon: '🌊',
    costRange: '$25–$70/person',
    budgetTier: '$–$$',
    highlights: [
      'NC Aquarium at Pine Knoll Shores',
      'Fort Macon State Park (free)',
      'Atlantic Beach boardwalk',
      'Fresh seafood lunch in Morehead City',
    ],
    schedule: [
      {
        period: 'Morning',
        stops: [
          {
            time: '7:00 AM',
            activity: 'Depart Greenville',
            location: 'Greenville, NC',
            address: 'Greenville, NC 27858',
            duration: '1.5 hours drive',
            price: 'Gas ~$12',
            notes: 'Take US-264 E to NC-101 S toward Morehead City. Arrive ~8:30 AM.',
          },
          {
            time: '8:30 AM',
            activity: 'Breakfast at Sanitary Fish Market',
            location: 'Sanitary Fish Market & Restaurant',
            address: '501 Evans St, Morehead City, NC 28557',
            duration: '1 hour',
            price: '$10–$20',
            isFood: true,
            vegetarianFriendly: true,
            vegetarianDishes: ['Pancakes', 'Eggs Benedict', 'Veggie Omelette'],
            notes: 'Iconic Morehead City seafood institution since 1938. Breakfast menu available.',
          },
          {
            time: '9:00 AM',
            activity: 'NC Aquarium at Pine Knoll Shores',
            location: 'NC Aquarium at Pine Knoll Shores',
            address: '1 Roosevelt Blvd, Pine Knoll Shores, NC 28512',
            duration: '2.5 hours',
            price: '$15/adults, $13/children',
            notes: 'Opens 9 AM. Journey from NC mountains to the Crystal Coast. Sharks, sea turtles, stingrays, and thousands of aquatic animals. Buy tickets in advance online.',
            bookingUrl: 'https://www.ncaquariums.com/pine-knoll-shores',
          },
        ],
      },
      {
        period: 'Afternoon',
        stops: [
          {
            time: '11:30 AM',
            activity: 'Fort Macon State Park',
            location: 'Fort Macon State Park',
            address: '2300 E Fort Macon Rd, Atlantic Beach, NC 28512',
            duration: '2 hours',
            price: 'Free',
            notes: 'Civil War-era fort with stunning ocean views. Walk the beach (late February can be beautiful and uncrowded). Trails through maritime forest.',
            infoUrl: 'https://www.ncparks.gov/state-parks/fort-macon-state-park',
          },
          {
            time: '1:30 PM',
            activity: 'Lunch at Amos Mosquito\'s',
            location: "Amos Mosquito's Restaurant & Bar",
            address: '703 E Fort Macon Rd, Atlantic Beach, NC 28512',
            duration: '1.5 hours',
            price: '$15–$30',
            isFood: true,
            vegetarianFriendly: true,
            veganFriendly: true,
            vegetarianDishes: ['Black Bean Burger', 'Veggie Wrap', 'Caprese Salad'],
            veganDishes: ['Black Bean Burger (no cheese)', 'Garden Salad'],
            notes: 'Casual beach bar with excellent seafood and vegetarian options. Outdoor seating with ocean views.',
          },
          {
            time: '3:00 PM',
            activity: 'Atlantic Beach Boardwalk & Stroll',
            location: 'Atlantic Beach',
            address: 'Atlantic Beach, NC 28512',
            duration: '1.5 hours',
            price: 'Free',
            notes: 'Late February beach walks are peaceful and beautiful. Mild temperatures (69°F Sunday). Shell collecting, bird watching, and fresh sea air.',
          },
          {
            time: '4:30 PM',
            activity: 'Beaufort Historic Site & Waterfront',
            location: 'Beaufort Historic Site',
            address: '138 Turner St, Beaufort, NC 28516',
            duration: '1.5 hours',
            price: 'Free (tours $8)',
            notes: 'Charming waterfront town with wild horses visible on Carrot Island across the water. Historic district walking tour available.',
            infoUrl: 'https://beauforthistoricsite.org/',
          },
        ],
      },
      {
        period: 'Evening',
        stops: [
          {
            time: '6:00 PM',
            activity: 'Dinner at Circa 81',
            location: 'Circa 81',
            address: '4426 Arendell St, Morehead City, NC 28557',
            duration: '1.5 hours',
            price: '$20–$40',
            isFood: true,
            vegetarianFriendly: true,
            vegetarianDishes: ['Pasta Primavera', 'Caprese', 'Mushroom Risotto'],
            notes: 'Upscale casual dining in Morehead City. Fresh local seafood and vegetarian options.',
          },
          {
            time: '7:30 PM',
            activity: 'Depart for Greenville',
            location: 'Morehead City, NC',
            address: 'Morehead City, NC 28557',
            duration: '1.5 hours drive',
            price: 'Gas ~$12',
            notes: 'Return via NC-101 N to US-264 E. Arrive Greenville ~9 PM.',
          },
        ],
      },
    ],
    weatherPlans: [
      {
        condition: 'Good Weather',
        description: 'Sunday is forecast to be the best day of the weekend (69°F, clear)',
        adjustments: [
          'Add a beach walk at Emerald Isle (30 min from Atlantic Beach)',
          'Kayak rental at Beaufort waterfront (seasonal availability)',
          'Sunset viewing from Fort Macon beach',
        ],
      },
      {
        condition: 'Rain Alternative',
        description: 'If weather turns, pivot to indoor coastal attractions',
        adjustments: [
          'Spend more time at the Aquarium (easily 3+ hours)',
          'Visit NC Maritime Museum in Beaufort (free)',
          'Browse shops in Beaufort\'s historic district',
        ],
      },
    ],
    practicalInfo: {
      departureTime: '7:00 AM from Greenville',
      returnTime: '~9:00 PM',
      parking: 'Free parking at Aquarium, Fort Macon, and Atlantic Beach. Beaufort waterfront has metered parking.',
      drivingRoute: 'US-264 E → NC-101 S → US-70 E toward Morehead City/Atlantic Beach. ~1.5 hours.',
      tips: [
        'Buy Aquarium tickets online in advance to save time',
        'Fort Macon is free — great for a long walk',
        'Beaufort has wild horses visible across the water (bring binoculars)',
        'Sunday is the best weather day — perfect for this coastal itinerary',
        'Dress in layers — coastal temperatures can be cooler than inland',
      ],
    },
    tags: ['nature', 'beach', 'aquarium', 'coastal', 'hiking', 'seafood', 'family'],
  },

  // ─── ITINERARY 4: NEW BERN HISTORY & CHARM ───────────────────────────────────
  {
    id: 'new-bern-history',
    title: 'New Bern History & Charm',
    subtitle: 'Colonial Capital, Tryon Palace & Coastal Town',
    city: 'New Bern',
    distanceMiles: 46,
    driveTimeMinutes: 60,
    day: 'Any Day',
    weather: 'Varies by day',
    weatherIcon: '🏛️',
    theme: 'History & Culture',
    themeIcon: '🏛️',
    costRange: '$30–$80/person',
    budgetTier: '$–$$',
    highlights: [
      'Tryon Palace – NC\'s first capitol',
      'Historic downtown & Birthplace of Pepsi',
      'Neuse River waterfront',
      'Charming local restaurants',
    ],
    schedule: [
      {
        period: 'Morning',
        stops: [
          {
            time: '9:00 AM',
            activity: 'Depart Greenville',
            location: 'Greenville, NC',
            address: 'Greenville, NC 27858',
            duration: '1 hour drive',
            price: 'Gas ~$8',
            notes: 'Take US-264 W to US-70 W toward New Bern. Easy 1-hour drive.',
          },
          {
            time: '10:00 AM',
            activity: 'Breakfast at The Chelsea',
            location: 'The Chelsea Restaurant',
            address: '335 Middle St, New Bern, NC 28560',
            duration: '1 hour',
            price: '$12–$20',
            isFood: true,
            vegetarianFriendly: true,
            veganFriendly: true,
            vegetarianDishes: ['Avocado Toast', 'Veggie Frittata', 'Granola Bowl'],
            veganDishes: ['Avocado Toast (no egg)', 'Granola Bowl'],
            notes: 'Beloved New Bern breakfast spot in a historic building. Farm-to-table approach.',
          },
          {
            time: '11:00 AM',
            activity: 'Tryon Palace Historic Site & Gardens',
            location: 'Tryon Palace',
            address: '529 S Front St, New Bern, NC 28562',
            duration: '3 hours',
            price: '$10–$22',
            notes: 'NC\'s first permanent capitol (1770). Tour the reconstructed Palace, historic homes, and 14 acres of formal gardens. NC History Center with interactive exhibits. Mon–Sat 10 AM–5 PM, Sun 12–5 PM.',
            bookingUrl: 'https://www.tryonpalace.org/plan-your-visit/tickets',
            infoUrl: 'https://www.tryonpalace.org/',
          },
        ],
      },
      {
        period: 'Afternoon',
        stops: [
          {
            time: '1:30 PM',
            activity: 'Lunch at Cow Café',
            location: 'Cow Café',
            address: '319 Middle St, New Bern, NC 28560',
            duration: '1 hour',
            price: '$10–$18',
            isFood: true,
            vegetarianFriendly: true,
            vegetarianDishes: ['Grilled Cheese', 'Veggie Sandwich', 'Tomato Soup'],
            notes: 'Quirky cow-themed café in the heart of downtown. Great sandwiches and ice cream.',
          },
          {
            time: '2:30 PM',
            activity: 'Birthplace of Pepsi-Cola',
            location: 'Pepsi Store',
            address: '256 Middle St, New Bern, NC 28560',
            duration: '30 min',
            price: 'Free',
            notes: 'Pepsi-Cola was invented in New Bern in 1893 by pharmacist Caleb Bradham. Visit the replica drugstore and museum. Free admission.',
            infoUrl: 'https://www.pepsistore.com/',
          },
          {
            time: '3:00 PM',
            activity: 'New Bern Waterfront & Bicentennial Park',
            location: 'Union Point Park',
            address: 'Union Point Park, New Bern, NC 28560',
            duration: '1 hour',
            price: 'Free',
            notes: 'Beautiful park at the confluence of the Neuse and Trent Rivers. Great views, walking paths, and the iconic New Bern bear statues.',
          },
          {
            time: '4:00 PM',
            activity: 'Downtown Art Galleries & Shopping',
            location: 'Middle Street, New Bern',
            address: 'Middle St, New Bern, NC 28560',
            duration: '1.5 hours',
            price: 'Free (shopping optional)',
            notes: 'New Bern has a thriving arts community. Browse galleries, antique shops, and boutiques on Middle Street.',
          },
        ],
      },
      {
        period: 'Evening',
        stops: [
          {
            time: '6:00 PM',
            activity: 'Dinner at 1710 Restaurant',
            location: '1710 Restaurant at Tryon Palace',
            address: '529 S Front St, New Bern, NC 28562',
            duration: '1.5 hours',
            price: '$25–$45',
            isFood: true,
            vegetarianFriendly: true,
            vegetarianDishes: ['Seasonal Vegetable Plate', 'Mushroom Risotto', 'Garden Salad'],
            notes: 'Upscale dining in the Tryon Palace complex. Colonial-inspired cuisine with modern touches.',
          },
          {
            time: '7:30 PM',
            activity: 'Depart for Greenville',
            location: 'New Bern, NC',
            address: 'New Bern, NC 28560',
            duration: '1 hour drive',
            price: 'Gas ~$8',
            notes: 'Return via US-70 E to US-264 E. Arrive Greenville ~8:30 PM.',
          },
        ],
      },
    ],
    weatherPlans: [
      {
        condition: 'Good Weather',
        description: 'New Bern is lovely in mild weather',
        adjustments: [
          'Extend time at Tryon Palace gardens',
          'Walk along the Neuse River Trail',
          'Visit Lawson Creek Park for nature walk',
        ],
      },
      {
        condition: 'Rain Alternative',
        description: 'Most New Bern attractions are indoor-friendly',
        adjustments: [
          'Tryon Palace and NC History Center are fully indoor',
          'Spend extra time in downtown galleries and shops',
          'Visit New Bern Fireman\'s Museum (indoor, $5)',
        ],
      },
    ],
    practicalInfo: {
      departureTime: '9:00 AM from Greenville',
      returnTime: '~8:30 PM',
      parking: 'Free parking throughout downtown New Bern. Tryon Palace has dedicated parking.',
      drivingRoute: 'US-264 W to US-70 W → Follow signs to downtown New Bern. ~1 hour.',
      tips: [
        'New Bern is one of NC\'s most charming small cities — allow extra time to explore',
        'Tryon Palace is the highlight — buy combination tickets for best value',
        'The Birthplace of Pepsi is a fun, free stop',
        'Great option for any day of the weekend — close and easy drive',
      ],
    },
    tags: ['history', 'colonial', 'charming', 'easy drive', 'family', 'culture', 'gardens'],
  },

  // ─── ITINERARY 5: DURHAM ARTS & ENTERTAINMENT ────────────────────────────────
  {
    id: 'durham-arts-entertainment',
    title: 'Durham Arts & Entertainment Weekend',
    subtitle: 'Nevermore Film Festival, Duke Basketball & Craft Beer',
    city: 'Durham',
    distanceMiles: 109,
    driveTimeMinutes: 104,
    day: 'Saturday',
    weather: 'Rain Possible 59°F',
    weatherIcon: '🌧️',
    theme: 'Entertainment',
    themeIcon: '🎬',
    costRange: '$50–$120/person',
    budgetTier: '$$–$$$',
    highlights: [
      'Duke vs. Virginia Basketball at Cameron Indoor',
      'Nevermore Horror Film Festival',
      'Durham food & craft beer scene',
      'American Tobacco Campus',
    ],
    schedule: [
      {
        period: 'Morning',
        stops: [
          {
            time: '8:00 AM',
            activity: 'Depart Greenville',
            location: 'Greenville, NC',
            address: 'Greenville, NC 27858',
            duration: '1.75 hours drive',
            price: 'Gas ~$14',
            notes: 'Take US-264 W to I-40 W toward Durham. Arrive ~9:45 AM.',
          },
          {
            time: '9:45 AM',
            activity: 'Breakfast at Dame\'s Chicken & Waffles',
            location: "Dame's Chicken & Waffles",
            address: '317 W Main St, Durham, NC 27701',
            duration: '1 hour',
            price: '$12–$20',
            isFood: true,
            vegetarianFriendly: true,
            vegetarianDishes: ['Veggie Waffle', 'Tofu & Waffles', 'Fruit Bowl'],
            notes: 'Durham institution for creative chicken and waffle combinations. Vegetarian options available.',
          },
          {
            time: '10:30 AM',
            activity: 'Bennett Place State Historic Site',
            location: 'Bennett Place',
            address: '4409 Bennett Memorial Rd, Durham, NC 27705',
            duration: '1.5 hours',
            price: 'Free (tours $1–$4)',
            notes: 'Site of the largest Civil War troop surrender. Guided tours at 11 AM. Reconstructed farmhouse and outbuildings.',
            infoUrl: 'https://historicsites.nc.gov/all-sites/bennett-place',
          },
        ],
      },
      {
        period: 'Afternoon',
        stops: [
          {
            time: '12:00 PM',
            activity: 'Duke Men\'s Basketball vs. Virginia',
            location: 'Cameron Indoor Stadium',
            address: '115 Whitford Dr, Durham, NC 27708',
            duration: '2.5 hours',
            price: 'From $17 (resale)',
            notes: 'ACC conference game at the legendary Cameron Indoor Stadium. One of the most electric atmospheres in college basketball. Buy tickets early.',
            bookingUrl: 'https://seatgeek.com/duke-blue-devils-mens-basketball-tickets/ncaa-basketball/2026-02-28-12-pm/17724477',
          },
          {
            time: '3:00 PM',
            activity: 'American Tobacco Campus & Durham Bulls Athletic Park',
            location: 'American Tobacco Campus',
            address: '318 Blackwell St, Durham, NC 27701',
            duration: '1 hour',
            price: 'Free',
            notes: 'Beautiful redeveloped tobacco warehouse complex with restaurants, shops, and public art. Walk along the Little River.',
          },
          {
            time: '4:00 PM',
            activity: 'Nevermore Film Festival – Afternoon Screening',
            location: 'Carolina Theatre',
            address: '309 W Morgan St, Durham, NC 27701',
            duration: '2 hours',
            price: '$13.50/film',
            notes: '27th Annual Nevermore Film Festival. Saturday afternoon screenings of horror, dark fantasy, and sci-fi films. Check schedule at carolinatheatre.org.',
            bookingUrl: 'https://carolinatheatre.org/festival/nevermore-film-festival/',
          },
        ],
      },
      {
        period: 'Evening',
        stops: [
          {
            time: '6:30 PM',
            activity: 'Dinner at Saltbox Seafood Joint',
            location: 'Saltbox Seafood Joint',
            address: '608 N Mangum St, Durham, NC 27701',
            duration: '1 hour',
            price: '$15–$25',
            isFood: true,
            vegetarianFriendly: true,
            vegetarianDishes: ['Hush Puppies', 'Coleslaw', 'Corn on the Cob'],
            notes: 'James Beard-nominated seafood shack. Simple, incredible food. Cash-friendly.',
          },
          {
            time: '8:00 PM',
            activity: 'Nevermore Film Festival – Evening Screening',
            location: 'Carolina Theatre',
            address: '309 W Morgan St, Durham, NC 27701',
            duration: '2 hours',
            price: '$13.50/film',
            notes: 'Evening horror/sci-fi screenings. World and US premieres. Check schedule for Saturday evening films.',
            bookingUrl: 'https://carolinatheatre.org/festival/nevermore-film-festival/',
          },
          {
            time: '10:30 PM',
            activity: 'Depart for Greenville',
            location: 'Durham, NC',
            address: 'Durham, NC 27701',
            duration: '1.75 hours drive',
            price: 'Gas ~$14',
            notes: 'Return via I-40 E to US-264 E. Arrive Greenville ~12:15 AM.',
          },
        ],
      },
    ],
    weatherPlans: [
      {
        condition: 'Good Weather',
        description: 'Saturday has rain in the forecast — most activities are indoors',
        adjustments: [
          'If dry, walk the American Tobacco Campus outdoor areas',
          'Visit Duke Gardens (free, beautiful even in late February)',
        ],
      },
      {
        condition: 'Rain Alternative',
        description: 'This itinerary is almost entirely indoor-friendly',
        adjustments: [
          'All major activities (basketball, film festival, restaurants) are indoor',
          'Add Seth Meyers comedy show at DPAC (7 PM Friday) if doing Friday instead',
          'Visit Durham Museum of Life and Science if time allows',
        ],
      },
    ],
    practicalInfo: {
      departureTime: '8:00 AM from Greenville',
      returnTime: '~12:15 AM',
      parking: 'Parking decks near American Tobacco Campus ($5–$10). Street parking near Carolina Theatre.',
      drivingRoute: 'US-264 W → I-40 W toward Durham. Take Exit 279B for downtown Durham. ~1.75 hours.',
      tips: [
        'Cameron Indoor tickets sell out fast — buy resale tickets early',
        'Nevermore Film Festival: buy a 5-pass ($60) for best value',
        'Durham has excellent food scene — explore beyond these suggestions',
        'Consider staying overnight to catch Brett Young at DPAC Sunday night',
      ],
    },
    tags: ['film festival', 'basketball', 'Duke', 'horror', 'craft beer', 'entertainment'],
  },

  // ─── ITINERARY 6: NATURE & STATE PARKS ───────────────────────────────────────
  {
    id: 'nature-state-parks',
    title: 'Eastern NC Nature & Parks Day',
    subtitle: 'Ranger Hikes, Cliffs & Coastal Wetlands',
    city: 'Multiple Parks',
    distanceMiles: 49,
    driveTimeMinutes: 64,
    day: 'Friday',
    weather: 'Partly Cloudy 50°F',
    weatherIcon: '⛅',
    theme: 'Nature & Outdoors',
    themeIcon: '🌲',
    costRange: '$10–$30/person',
    budgetTier: 'Free–$',
    highlights: [
      'Cliffs of the Neuse State Park – Ranger Hike',
      'Goose Creek State Park wetlands',
      'Neuse River views',
      'Budget-friendly outdoor adventure',
    ],
    schedule: [
      {
        period: 'Morning',
        stops: [
          {
            time: '8:00 AM',
            activity: 'Depart Greenville',
            location: 'Greenville, NC',
            address: 'Greenville, NC 27858',
            duration: '45 min drive',
            price: 'Gas ~$6',
            notes: 'Take US-264 W to NC-111 S toward Kinston, then to Seven Springs.',
          },
          {
            time: '8:45 AM',
            activity: 'Cliffs of the Neuse State Park – Morning Hike',
            location: 'Cliffs of the Neuse State Park',
            address: '240 Park Entrance Road, Seven Springs, NC 28578',
            duration: '3 hours',
            price: 'Free',
            notes: 'Park opens 7 AM. Hike the trails along the 90-foot bluffs overlooking the Neuse River. Ranger-led hike at 2 PM Friday. Bring water and snacks.',
            infoUrl: 'https://www.ncparks.gov/state-parks/cliffs-neuse-state-park',
          },
          {
            time: '10:30 AM',
            activity: 'Picnic Lunch at the Park',
            location: 'Cliffs of the Neuse Picnic Area',
            address: '240 Park Entrance Road, Seven Springs, NC 28578',
            duration: '30 min',
            price: 'Bring your own',
            isFood: true,
            vegetarianFriendly: true,
            veganFriendly: true,
            notes: 'Pack a picnic lunch! The park has beautiful picnic areas with river views.',
          },
        ],
      },
      {
        period: 'Afternoon',
        stops: [
          {
            time: '2:00 PM',
            activity: 'Ranger-Led Hike at Cliffs of the Neuse',
            location: 'Cliffs of the Neuse State Park',
            address: '240 Park Entrance Road, Seven Springs, NC 28578',
            duration: '1 hour',
            price: 'Free',
            notes: 'Free ranger-led hike every Friday at 2 PM. Learn about the geology, ecology, and history of this unique park.',
            infoUrl: 'https://www.ncparks.gov/state-parks/cliffs-neuse-state-park',
          },
          {
            time: '3:30 PM',
            activity: 'Drive to Goose Creek State Park',
            location: 'En route to Washington, NC',
            address: 'Washington, NC 27889',
            duration: '45 min drive',
            price: 'Gas ~$4',
            notes: 'Take NC-111 N to US-264 E toward Washington, NC.',
          },
          {
            time: '4:15 PM',
            activity: 'Goose Creek State Park – Coastal Wetlands Walk',
            location: 'Goose Creek State Park',
            address: '2190 Camp Leach Road, Washington, NC 27889',
            duration: '2 hours',
            price: 'Free',
            notes: 'Coastal state park on the Pamlico River. Hike the Flatty Creek Trail through cypress swamp. Outstanding bird watching in late February (migratory species). Park open until 6 PM Friday.',
            infoUrl: 'https://www.ncparks.gov/state-parks/goose-creek-state-park',
          },
        ],
      },
      {
        period: 'Evening',
        stops: [
          {
            time: '6:30 PM',
            activity: 'Dinner in Washington, NC',
            location: 'Bill\'s Hot Dogs',
            address: '109 Gladden St, Washington, NC 27889',
            duration: '45 min',
            price: '$5–$10',
            isFood: true,
            vegetarianFriendly: true,
            vegetarianDishes: ['Veggie Hot Dog', 'Chips', 'Drinks'],
            notes: 'Washington NC institution since 1928. Simple, delicious, and cheap. Or explore other downtown Washington restaurants.',
          },
          {
            time: '7:30 PM',
            activity: 'Return to Greenville',
            location: 'Washington, NC',
            address: 'Washington, NC 27889',
            duration: '45 min drive',
            price: 'Gas ~$4',
            notes: 'Take US-264 E back to Greenville. Arrive ~8:15 PM.',
          },
        ],
      },
    ],
    weatherPlans: [
      {
        condition: 'Good Weather',
        description: 'Friday is partly cloudy with no rain — perfect for hiking',
        adjustments: [
          'Add kayak or canoe rental at Cliffs of the Neuse (seasonal)',
          'Extend Goose Creek visit to watch sunset over Pamlico River',
          'Visit Pettigrew State Park (Lake Phelps) instead of Goose Creek for a longer drive',
        ],
      },
      {
        condition: 'Rain Alternative',
        description: 'If rain develops, pivot to indoor options',
        adjustments: [
          'Visit Tryon Palace in New Bern (1 hour from Greenville, fully indoor)',
          'Explore downtown Washington NC shops and galleries',
          'Head to Greenville Museum of Art (open Tue–Sat)',
        ],
      },
    ],
    practicalInfo: {
      departureTime: '8:00 AM from Greenville',
      returnTime: '~8:15 PM',
      parking: 'Free parking at all state parks.',
      drivingRoute: 'US-264 W → NC-111 S to Cliffs of the Neuse. Then NC-111 N → US-264 E to Goose Creek/Washington.',
      tips: [
        'Bring layers — 50°F can feel cool in the shade',
        'Pack a picnic lunch to save money and enjoy the parks',
        'Ranger hike at 2 PM is free and highly recommended',
        'Saturday has a moonlight ranger hike at Cliffs of the Neuse (7 PM) — consider that instead',
        'Excellent budget option — total cost under $30 per person',
      ],
    },
    tags: ['hiking', 'nature', 'state parks', 'ranger hike', 'budget', 'free', 'birds', 'wetlands'],
  },
];
