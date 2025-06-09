
# Marc’d Webpage Proposal


## 📌 Description

Marc’d is a digital platform designed to improve the lifestyle and experience of truckers on the road. This web-based version will serve as an informational and onboarding hub, educating users about the features of the mobile app, encouraging engagement, and collecting feedback or early signups. It will also serve as a simplified version of the app’s core functionality — showing real-time weather, truck stop data, and user-generated updates.

---

## 🔑 MVPs (Minimum Viable Product)

- Responsive single-page React website
- Homepage with Hero Banner and Call-to-Action (CTA)
- Features page explaining core app functionalities:
  - GPS-based truck stop finder
  - Real-time weather updates
  - Cleanliness and food quality ratings
  - Parking availability reports
- Contact/Join Waitlist form (integrated with Formspree or EmailJS)
- Basic real-time map preview of truck stop locations
- Deployed publicly via Vercel or Netlify

---

## ✨ Stretch Goals

- User account creation (basic auth)
- Ability to submit truck stop reports via web
- Admin dashboard to moderate user reports
- Language translation support

---

## 🧭 Hierarchy Diagram

Marc'd Web
├── Navbar
│ ├── Home
│ ├── Features
│ ├── Join Waitlist
│ └── Contact
├── HeroBanner
├── FeatureSection
│ ├── Location
│ ├── Weather
│ ├── Parking
│ └── Cleanliness & Food
├── MapPreview
├── CallToAction
├── Footer


---

## 🗃️ ERD (Entity Relationship Diagram)


User
├── id (PK)
├── email
├── name

TruckStop
├── id (PK)
├── name
├── latitude
├── longitude

Report
├── id (PK)
├── truckStopId (FK)
├── userId (FK, optional)
├── cleanliness (1–5)
├── foodQuality (1–5)
├── parkingStatus (enum: Available, Limited, Full)
├── weatherNote (text)
├── timestamp



---

## 🛣️ Routes (Frontend + API)

### Frontend (React)
| Route | Description |
|-------|-------------|
| `/` | Homepage with CTA |
| `/features` | Features overview |
| `/contact` | Contact/Join Waitlist form |
| `/map` (stretch) | Embedded map of truck stops |

### API (Backend - Stretch Goal)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/stops` | Get list of truck stops |
| POST | `/api/reports` | Submit truck stop report |
| GET | `/api/reports` | Get recent reports |

---

## ⏳ Timeline (2-3 Weeks)

| Week | Milestone |
|------|-----------|
| Week 1 | Setup repo, scaffold React app, build homepage, navbar, footer |
| Week 2 | Add Features and Contact sections, connect waitlist form |
| Week 3 | Style for mobile, deploy to Vercel, QA & polish |
| Stretch | Add live map + interactive form submission |

---

## 🧰 Wireframe (Sample Sketch)

+-----------------------------------------+
| Navbar: Home | Features | Join | Contact |
+-----------------------------------------+

| Hero Image w/ Truck + Tagline |
| "Helping Truckers Navigate Life On The Road" |
| [Join the Waitlist] |

+-----------------------------------------+
| Feature Icons + Descriptions |
| 🧭 GPS | 🌦️ Weather | 🅿️ Parking | 🍔 Food |
+-----------------------------------------+

| Map Snapshot Preview |

| Email Signup Form |
| Name | Email | [Submit] |

+-----------------------------------------+
| Footer |
+-----------------------------------------+

![Marc'd Landing Page Mockup](https://i.postimg.cc/5yjmpRh4/667f713c-f671-409e-af85-7f92fb077969.png)


---

## ✅ Tasks

### Setup
- [ ] Create GitHub repo and branch structure
- [ ] Set up React project with Tailwind or MUI
- [ ] Configure Vercel or Netlify for deployment

### Frontend
- [ ] Build HeroBanner with CTA
- [ ] Build FeatureSection with icons/text
- [ ] Build Contact/Waitlist form
- [ ] Build Footer
- [ ] Add responsive mobile styling

### Backend (Optional/Stretch)
- [ ] Set up FastAPI backend
- [ ] Create routes for /stops and /reports
- [ ] Connect to PostgreSQL or MongoDB
- [ ] Deploy backend via Render

---

