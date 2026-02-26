# BankPulse - UI Layout Design : Option "Sidebar Collapsed"

**Date** : 26 février 2026  
**Statut** : En cours (Phase 1 ✅ + Phase 2 ✅ + Phase 3 ✅ livrées)
**Philosophie** : Interface ultra-compacte, focus maximal sur les données, idéale pour Power Users

---

## 📋 PRD — Étape 8 : Frontend Next.js (Assemblage final)

> Phase 1 livrée : squelette Next.js 16, design tokens BankPulse, shadcn/ui v3, fonts Inter + JetBrains Mono, proxy rewrites → FastAPI
> Phase 2 livrée : Sidebar (collapsed/expand desktop + Sheet mobile), TopBar (breadcrumbs, user menu), DashboardLayout — `components/layout/sidebar.tsx` · `top-bar.tsx` · `app/(dashboard)/layout.tsx`
> Phase 3 livrée : Auth — pages Login/Register (Zod + react-hook-form), cookies HttpOnly via route handlers, `proxy.ts` (protection routes), hook `useAuth`, logout TopBar — `app/(auth)/` · `app/api/auth/` · `hooks/useAuth.ts`

**Objectif** : Interface utilisateur complète connectée à l'API, utilisable par un beta-testeur.

### Composants à livrer (par étape API associée)

| Étape API | Composants UI |
|-----------|---------------|
| ~~Étape 2~~ ✅ | Pages Login / Register avec validation form — **Phase 3 livrée** |
| Étape 3 | Page "Mes comptes" + modal import CSV + progress bar upload |
| Étape 4 | Page Transactions — inline category selector |
| Étape 5 | Dashboard : KPI cards, Donut chart (Recharts), Top merchants, Recurring subscriptions |
| Étape 6 | Page Transactions avancée : filtres, recherche, bulk actions, export |
| Étape 7 | Page Budgets : Progress bars par catégorie, badges d'alerte |

### Requirements P0

| Req | Description |
|-----|-------------|
| R8.1 ✅ | Routing Next.js avec layout authentifié — `proxy.ts` (redirect `/login` si pas de cookie) |
| R8.2 ✅ | Gestion du JWT en cookie HttpOnly — route handlers `/api/auth/*` + `response.cookies.set()` |
| R8.3 | Composants shadcn/ui : Table, Card, Badge, Progress, Dialog |
| R8.4 | Recharts : DonutChart, BarChart, LineChart (préparation Phase 2) |
| R8.5 | États vides (empty states) sur chaque vue : "Aucune transaction", "Aucun budget" |
| R8.6 | Responsive : desktop first, lisible sur tablette |

---

## 🎯 Vision & Philosophie

### Concept Général
L'Option "Sidebar Collapsed" privilégie **l'espace de contenu au détriment de la navigation permanente**. La sidebar est rétractée par défaut (64px), ne montrant que les icônes. Au hover, elle s'expand pour révéler les labels. Cette approche est inspirée de produits comme **Grafana**, **Datadog**, **Linear**, et bien sûr **Stripe Dashboard**.

### Principes de Design
- **Data First** : Maximum d'espace horizontal pour les charts, tables et KPIs
- **Navigation Contextuelle** : Breadcrumbs en haut pour se situer dans l'app
- **Micro-interactions** : Hover expand, skeleton loaders, transitions fluides
- **Typographie Forte** : Headers imposants, contraste élevé (Inter + JetBrains Mono)
- **Couleurs Subtiles** : Palette inspirée Stripe Blurple + grays neutres

### Cible Utilisateur
- **Power Users** : Freelances, CFO, comptables, early adopters
- **Confort avec les interfaces denses** : Capable de mémoriser les icônes
- **Multi-écrans** : Optimisé pour laptops 13-15 pouces

---

## 🎨 Design System

### Palette de Couleurs

```css
/* Primary & Accent */
--primary-500: #6366F1;      /* Indigo-500 (primary buttons, links) */
--primary-600: #4F46E5;      /* Indigo-600 (hover states) */
--primary-700: #4338CA;      /* Indigo-700 (active states) */

/* Success, Warning, Danger */
--success-500: #10B981;      /* Emerald-500 (positive deltas, revenue) */
--warning-500: #F59E0B;      /* Amber-500 (near budget limit) */
--danger-500: #EF4444;       /* Red-500 (over budget, expenses) */

/* Neutrals */
--gray-50: #F9FAFB;          /* Background (body) */
--gray-100: #F3F4F6;         /* Card background (alternate) */
--gray-200: #E5E7EB;         /* Borders */
--gray-500: #6B7280;         /* Secondary text */
--gray-800: #1F2937;         /* Sidebar background */
--gray-900: #111827;         /* Primary text */

/* Semantic Colors */
--background: #F9FAFB;       /* Body background */
--foreground: #111827;       /* Main text */
--muted: #F3F4F6;            /* Muted backgrounds */
--border: #E5E7EB;           /* Dividers, borders */
```

### Typographie

```css
/* Fonts */
font-family: 
  - Primary: 'Inter', system-ui, sans-serif
  - Monospace (amounts): 'JetBrains Mono', monospace

/* Scale */
--text-xs: 0.75rem;      /* 12px - labels, helper text */
--text-sm: 0.875rem;     /* 14px - body, table cells */
--text-base: 1rem;       /* 16px - default */
--text-lg: 1.125rem;     /* 18px - card titles */
--text-xl: 1.25rem;      /* 20px - section headers */
--text-2xl: 1.5rem;      /* 24px - KPI values */
--text-3xl: 1.875rem;    /* 30px - page titles */

/* Weights */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

### Spacing Scale

```css
/* Tailwind-based spacing */
4px   → 0.25rem  → space-1
8px   → 0.5rem   → space-2
12px  → 0.75rem  → space-3
16px  → 1rem     → space-4  (card padding)
24px  → 1.5rem   → space-6  (section gaps)
32px  → 2rem     → space-8  (large gaps)
48px  → 3rem     → space-12 (page margins)
```

### Icons

- **Bibliothèque** : Lucide React
- **Taille par défaut** : 20px (1.25rem)
- **Sidebar icons** : 24px (1.5rem)
- **Style** : Stroke width 2, rounded caps

---

## 🏗️ Structure Globale

### Layout Principal (Toutes Pages)

```
┌────┬──────────────────────────────────────────────────────────────────┐
│    │  [≡]  BankPulse    [Breadcrumb]         [🔍] [@] [⚙]           │
│ S  ├──────────────────────────────────────────────────────────────────┤
│ I  │                                                                   │
│ D  │                     MAIN CONTENT AREA                            │
│ E  │                                                                   │
│ B  │                                                                   │
│ A  │                                                                   │
│ R  │                                                                   │
│    │                                                                   │
│ 6  │                                                                   │
│ 4  │                                                                   │
│ p  │                                                                   │
│ x  │                                                                   │
└────┴──────────────────────────────────────────────────────────────────┘
```

### Top Bar (64px height)

```
┌───────────────────────────────────────────────────────────────────────┐
│  [≡]  BankPulse    Dashboard > Février 2026      [🔍]  [@]  [⚙]      │
└───────────────────────────────────────────────────────────────────────┘
│← Burger  Logo    Breadcrumbs                 Search Avatar Settings  │
```

**Composants** :
- `[≡]` : Toggle sidebar (mobile only, desktop → toujours visible)
- `BankPulse` : Logo + wordmark (click → Dashboard)
- `Dashboard > Février 2026` : Breadcrumbs dynamiques
- `[🔍]` : Search (Cmd+K) → ouvre Command palette
- `[@]` : Avatar → dropdown menu (profile, logout)
- `[⚙]` : Settings → page paramètres

**Code structure** :
```typescript
// components/layout/top-bar.tsx
<header className="h-16 border-b border-gray-200 bg-white sticky top-0 z-40">
  <div className="flex items-center justify-between h-full px-4">
    <div className="flex items-center gap-4">
      <Button variant="ghost" size="icon" className="lg:hidden">
        <Menu />
      </Button>
      <Logo />
      <Breadcrumbs />
    </div>
    <div className="flex items-center gap-2">
      <CommandSearch />
      <UserMenu />
      <SettingsButton />
    </div>
  </div>
</header>
```

---

### Sidebar Collapsed (64px width)

```
┌────┐
│ [≡]│  ← Toggle (masque/affiche la sidebar)
├────┤
│ 🏠 │  Dashboard
├────┤
│ 💳 │  Comptes
├────┤
│ 📊 │  Transactions
├────┤
│ 💰 │  Budgets
├────┤
│ 📈 │  Rapports (Phase 2)
├────┤
│    │
│ ⋮  │
│    │
├────┤
│ ⚙ │  Paramètres
├────┤
│ [@]│  Utilisateur
└────┘
```

**Comportement Hover (expand to 240px)** :

```
┌─────────────────────┐
│ [≡]  Navigation     │
├─────────────────────┤
│ 🏠  Dashboard       │
├─────────────────────┤
│ 💳  Mes Comptes     │
├─────────────────────┤
│ 📊  Transactions    │
├─────────────────────┤
│ 💰  Budgets         │
├─────────────────────┤
│ 📈  Rapports        │
├─────────────────────┤
│                     │
├─────────────────────┤
│ ⚙   Paramètres     │
├─────────────────────┤
│ [@]  John Doe      │
│      john@acme.com  │
└─────────────────────┘
```

**Code structure** :
```typescript
// components/layout/sidebar.tsx
<aside className="fixed left-0 top-0 z-50 h-screen w-16 bg-gray-800 
                transition-all duration-200 hover:w-60 
                overflow-hidden group">
  <nav className="flex flex-col h-full">
    {/* Logo / Toggle */}
    <div className="h-16 flex items-center px-4 border-b border-gray-700">
      <LayoutDashboard className="text-white" size={24} />
      <span className="ml-3 text-white font-semibold opacity-0 
                     group-hover:opacity-100 transition-opacity">
        BankPulse
      </span>
    </div>
    
    {/* Main Nav */}
    <div className="flex-1 py-4">
      <NavItem icon={Home} label="Dashboard" href="/dashboard" />
      <NavItem icon={CreditCard} label="Mes Comptes" href="/accounts" />
      <NavItem icon={List} label="Transactions" href="/transactions" />
      <NavItem icon={TrendingUp} label="Budgets" href="/budgets" />
    </div>
    
    {/* Bottom Nav */}
    <div className="border-t border-gray-700 py-4">
      <NavItem icon={Settings} label="Paramètres" href="/settings" />
      <UserNavItem />
    </div>
  </nav>
</aside>
```

**NavItem Component** :
```typescript
function NavItem({ icon: Icon, label, href }: NavItemProps) {
  const isActive = usePathname() === href
  
  return (
    <Link 
      href={href}
      className={cn(
        "flex items-center h-12 px-4 text-gray-300",
        "hover:bg-gray-700 hover:text-white transition-colors",
        isActive && "bg-primary-600 text-white"
      )}
    >
      <Icon size={24} className="shrink-0" />
      <span className="ml-3 opacity-0 group-hover:opacity-100 
                     transition-opacity whitespace-nowrap">
        {label}
      </span>
    </Link>
  )
}
```

---

## 📄 Pages Détaillées

> Les spécifications détaillées de chaque page (Dashboard, Mes Comptes, Transactions, Budgets, Login, Register, Paramètres) sont dans **[SPEC_UI_PAGES.md](./SPEC_UI_PAGES.md)**.


---

## 🎨 Composants Réutilisables

### 1. KPICard

```typescript
interface KPICardProps {
  title: string
  value: string
  delta?: string
  deltaType?: "positive" | "negative" | "neutral"
  subtitle?: string
  icon?: React.ReactNode
}

export function KPICard({ title, value, delta, deltaType, subtitle, icon }: KPICardProps) {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-500">{title}</span>
          {icon && <div className="text-gray-400">{icon}</div>}
        </div>
        <div className="text-3xl font-bold font-mono">{value}</div>
        {delta && (
          <div className={cn(
            "text-sm mt-1",
            deltaType === "positive" && "text-success-500",
            deltaType === "negative" && "text-danger-500",
            deltaType === "neutral" && "text-gray-500"
          )}>
            {delta} {subtitle}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
```

### 2. CategoryLegendItem

```typescript
interface CategoryLegendItemProps {
  icon: string
  name: string
  amount: number
  percentage: number
  color: string
}

export function CategoryLegendItem({ icon, name, amount, percentage, color }: CategoryLegendItemProps) {
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-2">
        <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
        <span className="text-sm">{icon} {name}</span>
      </div>
      <div className="flex items-center gap-3">
        <span className="text-sm font-mono font-semibold">{formatAmount(amount)}</span>
        <span className="text-sm text-gray-500">{percentage}%</span>
      </div>
    </div>
  )
}
```

### 3. EmptyState

```typescript
interface EmptyStateProps {
  icon: React.ReactNode
  title: string
  description: string
  action?: {
    label: string
    onClick: () => void
  }
}

export function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4">
      <div className="w-16 h-16 mb-4 text-gray-400">
        {icon}
      </div>
      <h3 className="text-lg font-medium text-gray-900 mb-2">
        {title}
      </h3>
      <p className="text-sm text-gray-500 mb-6 text-center max-w-sm">
        {description}
      </p>
      {action && (
        <Button onClick={action.onClick}>
          {action.label}
        </Button>
      )}
    </div>
  )
}
```

---

## 📱 Responsive Behavior

### Breakpoints

```css
/* Mobile First */
sm:  640px  → Mobile landscape / small tablets
md:  768px  → Tablets
lg:  1024px → Laptops (sidebar visible)
xl:  1280px → Desktops
2xl: 1536px → Large desktops
```

### Sidebar Mobile

```typescript
// Sur mobile (< 1024px), la sidebar est cachée par défaut
// et s'ouvre en overlay avec le burger menu

<Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
  <SheetTrigger asChild>
    <Button variant="ghost" size="icon" className="lg:hidden">
      <Menu />
    </Button>
  </SheetTrigger>
  <SheetContent side="left" className="w-64 p-0">
    <Sidebar />
  </SheetContent>
</Sheet>
```

### Grid Responsive

```typescript
// Dashboard KPIs
<div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
  {/* Sur mobile: 1 colonne, sur laptop: 2 colonnes */}
</div>

// Dashboard Charts
<div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
  {/* Donut + Top Merchants : 1 col mobile, 2 col desktop */}
</div>

// Filtres Transactions
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
  {/* Mobile: 1 col, Tablet: 2 col, Desktop: 4 col */}
</div>
```

---

## ⚡ Loading States & Skeletons

### Skeleton Dashboard

```typescript
function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardContent className="pt-6">
            <Skeleton className="h-4 w-24 mb-4" />
            <Skeleton className="h-10 w-32 mb-2" />
            <Skeleton className="h-4 w-40" />
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <Skeleton className="h-4 w-24 mb-4" />
            <Skeleton className="h-10 w-32 mb-2" />
            <Skeleton className="h-4 w-40" />
          </CardContent>
        </Card>
      </div>
      
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-64 w-full" />
        </CardContent>
      </Card>
    </div>
  )
}
```

---

## 🧪 Plan d'Implémentation UI / LAYOUT

### Phase 1 : Setup (Jour 1-2)
1. ✅ Initialiser projet Next.js 16+
2. ✅ Configurer TailwindCSS + shadcn/ui
3. ✅ Installer Recharts, Lucide React
4. ✅ Setup fonts (Inter + JetBrains Mono)
5. ✅ Créer palette de couleurs (tailwind.config.ts)

### Phase 2 : Layout & Navigation (Jour 2-3) ✅ LIVRÉE
1. ✅ Composant `Sidebar` (collapsed + hover expand)
2. ✅ Composant `TopBar` (breadcrumbs, search, user menu)
3. ✅ Layout principal (`app/(dashboard)/layout.tsx`)
4. ✅ Navigation items + active states

### Phase 3 : Auth (Jour 3-4) ✅ LIVRÉE
1. ✅ Pages Login + Register
2. ✅ Forms avec validation (zod + react-hook-form)
3. ✅ Connexion API `/auth/login` et `/auth/register`
4. ✅ JWT storage (HttpOnly cookies) via route handlers Next.js
5. ✅ `proxy.ts` auth (redirect si non connecté, redirect `/dashboard` si déjà connecté)

### Phase 4 : Dashboard (Jour 4-6)
1. KPI Cards (solde, dépenses)
2. Donut Chart (Recharts)
3. Top Marchands list
4. Abonnements récurrents
5. Empty states

### Phase 5 : Comptes (Jour 6-7)
1. Liste des comptes (AccountCard)
2. Modal Ajouter compte
3. Modal Importer CSV
4. Progress bar upload
5. Success/Error messages

### Phase 6 : Transactions (Jour 7-9)
1. Barre de filtres (sticky)
2. Table avec pagination cursor
3. Inline category selector
4. Bulk actions (tag, categorize)
5. Export CSV

### Phase 7 : Budgets (Jour 9-10)
1. KPI Cards résumé
2. BudgetProgressCard (progress bar + alertes)
3. Modal créer/éditer budget
4. Calcul progression temps réel

### Phase 8 : Polish (Jour 10-11)
1. Responsive (mobile + tablet)
2. Loading skeletons
3. Transitions & animations
4. Empty states partout
5. Tests end-to-end

---

## 🎯 Checklist Finale

### Design System
- [ ] Palette de couleurs configurée
- [ ] Typographie (Inter + JetBrains Mono)
- [ ] Spacing scale cohérent
- [ ] Icons (Lucide React)

### Layout & Navigation
- [x] Sidebar collapsed (64px) avec hover expand
- [x] TopBar (breadcrumbs, search, user menu)
- [x] Layout principal responsive
- [x] Mobile overlay sidebar (Sheet)

### Pages
- [ ] Dashboard (KPIs, Donut, Top Marchands, Abonnements)
- [ ] Mes Comptes (liste, import CSV, CRUD)
- [ ] Transactions (filtres, table, bulk actions, export)
- [ ] Budgets (progression, alertes, CRUD)
- [x] Login / Register
- [ ] Paramètres (profil, sécurité)

### Composants Réutilisables
- [ ] KPICard
- [ ] CategoryLegendItem
- [ ] MerchantRow
- [ ] SubscriptionRow
- [ ] AccountCard
- [ ] TransactionRow
- [ ] BudgetProgressCard
- [ ] EmptyState
- [ ] Skeleton loaders

### Interactions
- [ ] Hover states (sidebar, buttons, links)
- [ ] Loading states (skeletons)
- [ ] Transitions fluides
- [ ] Modals (Dialog)
- [ ] Dropdowns (DropdownMenu)
- [ ] Toasts (success, error)

### Performance
- [ ] Suspense boundaries
- [ ] Code splitting
- [ ] Image optimization
- [ ] Font optimization

---

**Prêt à implémenter ! 🚀**

Ce document servira de référence pour toute l'implémentation de l'Étape 8.
