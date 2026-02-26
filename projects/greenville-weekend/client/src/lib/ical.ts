// iCal export utility for Greenville NC Weekend Itinerary Generator
import type { Event } from './eventsData';

function formatICalDate(dateStr: string, timeStr: string): string {
  // dateStr: "Friday" | "Saturday" | "Sunday"
  // timeStr: "7:30 PM"
  const dateMap: Record<string, string> = {
    'Friday': '20260227',
    'Saturday': '20260228',
    'Sunday': '20260301',
  };
  
  const baseDate = dateMap[dateStr] || '20260228';
  
  if (!timeStr || timeStr === 'Various' || timeStr === 'Various showtimes' || timeStr.includes('/')) {
    return `${baseDate}T120000`;
  }
  
  const match = timeStr.match(/(\d+):(\d+)\s*(AM|PM)/i);
  if (!match) return `${baseDate}T120000`;
  
  let hours = parseInt(match[1]);
  const minutes = parseInt(match[2]);
  const meridiem = match[3].toUpperCase();
  
  if (meridiem === 'PM' && hours !== 12) hours += 12;
  if (meridiem === 'AM' && hours === 12) hours = 0;
  
  return `${baseDate}T${String(hours).padStart(2, '0')}${String(minutes).padStart(2, '0')}00`;
}

function formatICalEndDate(dateStr: string, startTime: string, endTime?: string): string {
  if (endTime && endTime !== 'Various') {
    return formatICalDate(dateStr, endTime);
  }
  // Default: 2 hours after start
  const start = formatICalDate(dateStr, startTime);
  const year = parseInt(start.substring(0, 4));
  const month = parseInt(start.substring(4, 6));
  const day = parseInt(start.substring(6, 8));
  const hour = parseInt(start.substring(9, 11));
  const min = parseInt(start.substring(11, 13));
  
  const date = new Date(year, month - 1, day, hour + 2, min);
  return `${date.getFullYear()}${String(date.getMonth() + 1).padStart(2, '0')}${String(date.getDate()).padStart(2, '0')}T${String(date.getHours()).padStart(2, '0')}${String(date.getMinutes()).padStart(2, '0')}00`;
}

function escapeICalText(text: string): string {
  return text
    .replace(/\\/g, '\\\\')
    .replace(/;/g, '\\;')
    .replace(/,/g, '\\,')
    .replace(/\n/g, '\\n')
    .replace(/\r/g, '');
}

function foldLine(line: string): string {
  // RFC 5545: lines should be no longer than 75 octets
  if (line.length <= 75) return line;
  const parts: string[] = [];
  let remaining = line;
  parts.push(remaining.substring(0, 75));
  remaining = remaining.substring(75);
  while (remaining.length > 0) {
    parts.push(' ' + remaining.substring(0, 74));
    remaining = remaining.substring(74);
  }
  return parts.join('\r\n');
}

function generateUID(eventId: string): string {
  return `${eventId}-greenville-weekend-2026@manus.im`;
}

export function eventToICalEvent(event: Event): string {
  const day = event.days[0] || 'Saturday';
  const dtstart = formatICalDate(day, event.startTime);
  const dtend = formatICalEndDate(day, event.startTime, event.endTime);
  
  const description = [
    event.description,
    '',
    `Price: ${event.price}`,
    `Budget: ${event.budgetTier}`,
    event.veganOptions === true ? '🌱 Vegan options available' : '',
    event.vegetarianOptions === true ? '🥗 Vegetarian options available' : '',
    event.bookingUrl ? `Book: ${event.bookingUrl}` : '',
    event.infoUrl ? `Info: ${event.infoUrl}` : '',
  ].filter(Boolean).join('\\n');

  const location = `${event.address}\\, ${event.city}\\, ${event.state}`;
  
  const lines = [
    'BEGIN:VEVENT',
    foldLine(`UID:${generateUID(event.id)}`),
    `DTSTART:${dtstart}`,
    `DTEND:${dtend}`,
    foldLine(`SUMMARY:${escapeICalText(event.name)}`),
    foldLine(`LOCATION:${location}`),
    foldLine(`DESCRIPTION:${escapeICalText(description)}`),
    event.infoUrl ? foldLine(`URL:${event.infoUrl}`) : '',
    event.lat && event.lng ? `GEO:${event.lat};${event.lng}` : '',
    'END:VEVENT',
  ].filter(Boolean).join('\r\n');
  
  return lines;
}

export function generateICalFile(events: Event[], calName = 'Greenville NC Weekend Events'): string {
  const header = [
    'BEGIN:VCALENDAR',
    'VERSION:2.0',
    'PRODID:-//Greenville NC Weekend Itinerary//EN',
    `X-WR-CALNAME:${calName}`,
    'X-WR-TIMEZONE:America/New_York',
    'CALSCALE:GREGORIAN',
    'METHOD:PUBLISH',
  ].join('\r\n');
  
  const footer = 'END:VCALENDAR';
  
  const eventStrings = events.map(eventToICalEvent).join('\r\n');
  
  return `${header}\r\n${eventStrings}\r\n${footer}`;
}

export function downloadICalFile(events: Event[], filename = 'greenville-weekend-events.ics'): void {
  const content = generateICalFile(events);
  const blob = new Blob([content], { type: 'text/calendar;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

export function downloadSingleEventIcal(event: Event): void {
  const calContent = [
    'BEGIN:VCALENDAR',
    'VERSION:2.0',
    'PRODID:-//Greenville NC Weekend Itinerary//EN',
    `X-WR-CALNAME:${escapeICalText(event.name)}`,
    'X-WR-TIMEZONE:America/New_York',
    'CALSCALE:GREGORIAN',
    'METHOD:PUBLISH',
    eventToICalEvent(event),
    'END:VCALENDAR',
  ].join('\r\n');
  
  const blob = new Blob([calContent], { type: 'text/calendar;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${event.id}.ics`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
