# OnPoint Pros Landing Page

A modern, high-converting landing page for OnPoint Pros - Frisco's premier general contractor and renovation team.

## Features

- **Luxury Minimalist Design** - Clean whites, slate grays, and royal blue accents
- **Traffic Segmentation** - Separates Homeowners (high-ticket) and Investors (volume)
- **Mobile-First Responsive** - Looks great on all devices
- **Tailwind CSS** - No custom CSS required, fully CDN-based
- **Click-to-Call** - One-tap calling from mobile devices

## Sections

1. Sticky Header with Call-to-Action
2. Hero with dual CTAs for traffic segmentation
3. "Choose Your Path" two-column service breakdown
4. Social Proof / Testimonials
5. Portfolio Gallery (placeholder)
6. Contact Form Footer

## Deployment to GitHub Pages

### Quick Setup

1. Create a new repository on GitHub (e.g., `onpoint-pros-site`)

2. Initialize and push:
```bash
cd onpoint-landing
git init
git add .
git commit -m "Initial commit: OnPoint Pros landing page"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/onpoint-pros-site.git
git push -u origin main
```

3. Enable GitHub Pages:
   - Go to repository **Settings** → **Pages**
   - Source: **Deploy from a branch**
   - Branch: **main** / **(root)**
   - Click **Save**

4. Your site will be live at: `https://YOUR_USERNAME.github.io/onpoint-pros-site/`

### Custom Domain (Optional)

1. Add a `CNAME` file with your domain:
```
www.onpointprostx.com
```

2. Configure DNS with your registrar:
   - Add CNAME record: `www` → `YOUR_USERNAME.github.io`
   - Or A records pointing to GitHub's IPs

## Customization

### Update Phone Number
Replace `(469) 555-1234` and `tel:+14695551234` with your actual business number.

### Add Real Images
Replace the placeholder gallery items with actual project photos by adding `<img>` tags inside the gallery divs.

### Connect Contact Form
The form currently has `action="#"`. To make it functional:
- Use a service like Formspree, Netlify Forms, or your own backend
- Update the `action` attribute with your form endpoint

## Tech Stack

- HTML5 (Semantic)
- Tailwind CSS v3 (CDN)
- No JavaScript frameworks required

---

© 2026 OnPoint Pros
