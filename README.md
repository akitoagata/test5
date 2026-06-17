# TradeVault - Multi-Asset Trading Platform Landing Page

Welcome to TradeVault, an award-winning multi-asset trading platform featuring real-time data for crypto, commodities, and stocks.

## 🚀 Features

### Phase 1: Landing Page (Current) ✓
- **Hero Section** - Full-screen with abstract background, live market badge, and CTA buttons
- **Live Market Ticker** - 6 market cards with real-time data and sparkline charts
- **Features Grid** - Premium features: Real-Time Analytics, Bank-Grade Security, Trade Anywhere
- **Platform Overview** - Unified platform concept with architecture diagram
- **Testimonials** - 6 trader reviews with star ratings and quotes
- **FAQ Section** - 6 expandable questions about security, fees, and more
- **Dark CTA Section** - Registration call-to-action with dot pattern background
- **Responsive Navbar** - Transparent on load, solid on scroll, mobile hamburger menu
- **Scroll Animations** - Smooth fade-in effects as sections come into view
- **Footer** - Dark footer with links, certifications, and risk disclaimer

### Upcoming Phases
- Phase 2 — Live market pages
- Phase 3 — Login & registration
- Phase 4 — Trading interface
- Phase 5 — User dashboard
- Phase 6 — Account management

## 🎨 Design System

### Color Palette
- **Primary**: Amber (#F59E0B) - CTA and accents
- **Secondary**: Emerald (#10B981) - Success states
- **Background**: Cream (#FAF9F6) - Main background
- **Text**: Charcoal (#1A1A1A) - Dark text
- **Dark Mode**: Full charcoal backgrounds with white text

### Typography
- **Headings**: Syne (font-weight: 700)
- **Body**: Inter (font-weight: 400-600)

### Components
- Smooth transitions (0.3s ease)
- Framer Motion animations for scroll effects
- Tailwind CSS for responsive design
- Mobile-first approach

## 🛠️ Tech Stack

- **Framework**: Next.js 14
- **React**: 18.2
- **Styling**: Tailwind CSS 3.3
- **Animations**: Framer Motion 10.16
- **Icons**: Lucide React 0.294
- **Language**: TypeScript

## 📦 Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

The application will be available at `http://localhost:3000`

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────┐
│                 Client (Browser)              │
│  React/Next.js + WebSocket Connection        │
└──────────────────┬──────────────────────────┘
                   │ WSS
┌──────────────────▼──────────────────────────┐
│            API Gateway (Fastify)              │
│  - Rate Limiting                             │
│  - Authentication (JWT)                      │
│  - Request Validation                        │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│         Options Engine (Core)                 │
│  - Order Matching                            │
│  - Risk Management                           │
│  - P&L Calculation                           │
│  - Settlement                                │
└──────┬──────────────┬──────────────┬─────────┘
       │              │              │
┌──────▼──────┐ ┌────▼─────┐ ┌─────▼──────────┐
│ PostgreSQL   │ │ Redis    │ │ Message Queue  │
│ - Orders     │ │ - Cache  │ │ (Kafka/Redis)  │
│ - Users      │ │ - PubSub │ │ - Events       │
│ - Positions  │ │ - Locks  │ │ - Notifications│
└──────────────┘ └──────────┘ └────────────────┘
```

## 📊 Live Market Data

Currently displays 6 market pairs:
- **Crypto**: Bitcoin (BTC), Ethereum (ETH)
- **Stocks**: Apple (AAPL), Tesla (TSLA)
- **Commodities**: Gold (GOLD), Crude Oil (CRUDE)

Each market card includes:
- Live price with formatting
- 24h percentage change (color-coded)
- Trending indicator (up/down)
- Sparkline chart visualization
- Category badge

## ✨ Scroll Animations

All major sections feature smooth animations:
- Fade-in with slight upward movement
- Staggered children animations
- Hover effects on interactive elements
- Float animations for background elements

## 🔒 Security & Compliance

- SOC 2 Type II Certified
- Military-grade AES-256 encryption
- 2FA Support
- Cold storage for 95% of funds
- Full regulatory compliance

## 📱 Responsive Design

- Mobile-first approach
- Breakpoints: sm (640px), md (768px), lg (1024px)
- Touch-friendly navigation
- Optimized for all screen sizes

## 🚦 Project Status

**Phase 1 Status**: ✅ Complete
- [x] Hero section with animations
- [x] Live market ticker
- [x] Features showcase
- [x] Platform overview with architecture
- [x] Customer testimonials
- [x] FAQ section
- [x] CTA section
- [x] Responsive navbar
- [x] Footer with links
- [x] Full scroll animations

## 📝 License

This project is proprietary and confidential. All rights reserved.

## 👥 Support

For support, contact: support@tradevault.com

---

**TradeVault** - Trade Smarter. Move Faster. 🚀
