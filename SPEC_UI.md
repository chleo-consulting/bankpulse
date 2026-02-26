# BankPulse - UI Layout Design : Option "Sidebar Collapsed"

**Date** : 26 février 2026  
**Statut** : Validé pour implémentation Étape 8  
**Philosophie** : Interface ultra-compacte, focus maximal sur les données, idéale pour Power Users

---

## 📋 PRD — Étape 8 : Frontend Next.js (Assemblage final)

> Phase 1 livrée : squelette Next.js 16, design tokens BankPulse, shadcn/ui v3, fonts Inter + JetBrains Mono, proxy rewrites → FastAPI

**Objectif** : Interface utilisateur complète connectée à l'API, utilisable par un beta-testeur.

### Composants à livrer (par étape API associée)

| Étape API | Composants UI |
|-----------|---------------|
| Étape 2 | Pages Login / Register avec validation form |
| Étape 3 | Page "Mes comptes" + modal import CSV + progress bar upload |
| Étape 4 | Page Transactions — inline category selector |
| Étape 5 | Dashboard : KPI cards, Donut chart (Recharts), Top merchants, Recurring subscriptions |
| Étape 6 | Page Transactions avancée : filtres, recherche, bulk actions, export |
| Étape 7 | Page Budgets : Progress bars par catégorie, badges d'alerte |

### Requirements P0

| Req | Description |
|-----|-------------|
| R8.1 | Routing Next.js avec layout authentifié (redirect si non connecté) |
| R8.2 | Gestion du JWT en cookie HttpOnly |
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

---

## 1️⃣ Page : Dashboard (Route: `/dashboard`)

### Objectif
Vue synthétique de la situation financière en < 30 secondes. KPIs, breakdown catégories, top marchands, abonnements récurrents.

### Layout Complet

```
┌────┬──────────────────────────────────────────────────────────────────┐
│    │  [≡]  BankPulse    Dashboard > Février 2026   [🔍] [@] [⚙]     │
│ S  ├──────────────────────────────────────────────────────────────────┤
│ I  │                                                                   │
│ D  │  ┌────────────────────────┐  ┌────────────────────────────────┐ │
│ E  │  │  Solde Total           │  │  Dépenses ce mois             │ │
│ B  │  │  24 385,50 €           │  │  -1 842,00 €                  │ │
│ A  │  │  +2.3% vs mois dernier │  │  -12.3% vs mois dernier       │ │
│ R  │  └────────────────────────┘  └────────────────────────────────┘ │
│    │                                                                   │
│    │  ┌─────────────────────────────────────────────────────────────┐ │
│    │  │  Dépenses par Catégorie                         Février 2026│ │
│    │  │                                                              │ │
│    │  │  ┌────────────┐    🍽 Alimentation         542,00 €   42%  │ │
│    │  │  │            │    🚆 Transport            296,00 €   23%  │ │
│    │  │  │   Donut    │    🏠 Logement             231,00 €   18%  │ │
│    │  │  │   Chart    │    📺 Loisirs & Culture    154,00 €   12%  │ │
│    │  │  │            │    ⚡ Autres                65,00 €    5%  │ │
│    │  │  └────────────┘                                             │ │
│    │  └─────────────────────────────────────────────────────────────┘ │
│    │                                                                   │
│    │  ┌──────────────────────────┐  ┌──────────────────────────────┐ │
│    │  │  Top Marchands (5)       │  │  Abonnements Détectés (4)    │ │
│    │  │                          │  │                              │ │
│    │  │  1. Carrefour Market     │  │  Netflix      15,99 € / mois │ │
│    │  │     -245,80 €            │  │  Prochain: 01/03      [...]  │ │
│    │  │  2. SNCF Connect         │  │                              │ │
│    │  │     -156,00 €            │  │  Spotify       9,99 € / mois │ │
│    │  │  3. Amazon               │  │  Prochain: 15/03      [...]  │ │
│    │  │     -89,45 €             │  │                              │ │
│    │  │  4. Netflix              │  │  Le Monde     12,00 € / mois │ │
│    │  │     -15,99 €             │  │  Prochain: 20/03      [...]  │ │
│    │  │  5. Spotify              │  │                              │ │
│    │  │     -9,99 €              │  │  OVH Cloud    19,99 € / mois │ │
│    │  │                          │  │  Prochain: 28/03      [...]  │ │
│    │  │  [Voir tout →]           │  │                              │ │
│    │  │                          │  │  [+ Ajouter manuellement]    │ │
│    │  └──────────────────────────┘  └──────────────────────────────┘ │
│    │                                                                   │
└────┴──────────────────────────────────────────────────────────────────┘
```

### Sections Détaillées

#### Section 1 : KPI Cards (Grid 2 colonnes)

```typescript
<div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
  <KPICard
    title="Solde Total"
    value="24 385,50 €"
    delta="+2.3%"
    deltaType="positive"
    subtitle="vs mois dernier"
    icon={<Wallet />}
  />
  
  <KPICard
    title="Dépenses ce mois"
    value="-1 842,00 €"
    delta="-12.3%"
    deltaType="negative"
    subtitle="vs mois dernier"
    icon={<TrendingDown />}
  />
</div>
```

**Design KPICard** :
```
┌──────────────────────────┐
│  💰  Solde Total         │  ← Icon + Title (text-lg, gray-700)
│                          │
│  24 385,50 €             │  ← Value (text-3xl, font-bold, mono)
│  +2.3% vs mois dernier   │  ← Delta (text-sm, success-500 si +, danger si -)
└──────────────────────────┘
```

#### Section 2 : Breakdown Catégories (Card pleine largeur)

```typescript
<Card className="mb-6">
  <CardHeader>
    <CardTitle>Dépenses par Catégorie</CardTitle>
    <div className="text-sm text-gray-500">Février 2026</div>
  </CardHeader>
  <CardContent>
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      {/* Donut Chart */}
      <div className="flex items-center justify-center">
        <ResponsiveContainer width="100%" height={240}>
          <PieChart>
            <Pie
              data={categoryData}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={90}
              dataKey="amount"
              label={renderCustomLabel}
            >
              {categoryData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index]} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
          </PieChart>
        </ResponsiveContainer>
      </div>
      
      {/* Legend List */}
      <div className="flex flex-col justify-center gap-3">
        {categoryData.map((cat) => (
          <CategoryLegendItem
            key={cat.name}
            icon={cat.icon}
            name={cat.name}
            amount={cat.amount}
            percentage={cat.percentage}
            color={cat.color}
          />
        ))}
      </div>
    </div>
  </CardContent>
</Card>
```

**CategoryLegendItem** :
```
🍽  Alimentation        542,00 €   42%
│   │                   │          │
│   └─ name             └─amount   └─percentage
└─ icon (color dot)
```

#### Section 3 : Top Marchands + Abonnements (Grid 2 colonnes)

```typescript
<div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
  {/* Top Marchands */}
  <Card>
    <CardHeader>
      <CardTitle>Top Marchands (5)</CardTitle>
    </CardHeader>
    <CardContent>
      <div className="space-y-4">
        {topMerchants.map((merchant, idx) => (
          <MerchantRow
            key={merchant.id}
            rank={idx + 1}
            name={merchant.name}
            amount={merchant.amount}
          />
        ))}
      </div>
      <Button variant="link" className="mt-4">
        Voir tout →
      </Button>
    </CardContent>
  </Card>
  
  {/* Abonnements Récurrents */}
  <Card>
    <CardHeader>
      <CardTitle>Abonnements Détectés (4)</CardTitle>
    </CardHeader>
    <CardContent>
      <div className="space-y-4">
        {subscriptions.map((sub) => (
          <SubscriptionRow
            key={sub.id}
            name={sub.name}
            amount={sub.amount}
            frequency={sub.frequency}
            nextDate={sub.nextDate}
          />
        ))}
      </div>
      <Button variant="outline" className="mt-4 w-full">
        + Ajouter manuellement
      </Button>
    </CardContent>
  </Card>
</div>
```

**MerchantRow** :
```
1. Carrefour Market       -245,80 €
│  │                       │
│  └─ name                 └─ amount (font-mono, semibold)
└─ rank (text-gray-500)
```

**SubscriptionRow** :
```
Netflix          15,99 € / mois
Prochain: 01/03                [...]
│         │                    │
│         └─ amount            └─ actions dropdown
└─ name
```

### Empty States

Si aucune transaction importée :
```
┌────────────────────────────────────────┐
│                                        │
│            📊                          │
│                                        │
│      Aucune donnée disponible          │
│                                        │
│  Importez votre premier fichier CSV    │
│  pour voir votre dashboard.            │
│                                        │
│      [Importer un fichier CSV]         │
│                                        │
└────────────────────────────────────────┘
```

---

## 2️⃣ Page : Mes Comptes (Route: `/accounts`)

### Objectif
Gérer les comptes bancaires (CRUD), importer des transactions CSV, voir soldes consolidés.

### Layout Complet

```
┌────┬──────────────────────────────────────────────────────────────────┐
│    │  [≡]  BankPulse    Mes Comptes                [🔍] [@] [⚙]      │
│ S  ├──────────────────────────────────────────────────────────────────┤
│ I  │                                                                   │
│ D  │  ┌─────────────────────────────────────────────────────────────┐ │
│ E  │  │  Solde Total Consolidé                                      │ │
│ B  │  │  24 385,50 €                                                │ │
│ A  │  │  3 comptes actifs                                           │ │
│ R  │  └─────────────────────────────────────────────────────────────┘ │
│    │                                                                   │
│    │  Actions: [+ Ajouter un compte] [Importer CSV global]           │
│    │                                                                   │
│    │  ┌─────────────────────────────────────────────────────────────┐ │
│    │  │  🏦  Compte Courant Boursorama        [Importer CSV]  [...]  │ │
│    │  │  FR76 1234 5678 9012 3456 7890 12                           │ │
│    │  │  Solde: 2 450,80 €                                          │ │
│    │  │  Dernière synchro: 24/02/26 à 14:32                         │ │
│    │  │  327 transactions                                            │ │
│    │  └─────────────────────────────────────────────────────────────┘ │
│    │                                                                   │
│    │  ┌─────────────────────────────────────────────────────────────┐ │
│    │  │  🏦  Livret A BNP Paribas              [Importer CSV]  [...]  │ │
│    │  │  FR76 9876 5432 1098 7654 3210 98                           │ │
│    │  │  Solde: 18 500,00 €                                         │ │
│    │  │  Dernière synchro: 20/02/26 à 09:15                         │ │
│    │  │  12 transactions                                             │ │
│    │  └─────────────────────────────────────────────────────────────┘ │
│    │                                                                   │
│    │  ┌─────────────────────────────────────────────────────────────┐ │
│    │  │  🏦  Compte Joint Crédit Agricole      [Importer CSV]  [...]  │ │
│    │  │  FR76 1111 2222 3333 4444 5555 66                           │ │
│    │  │  Solde: 3 434,70 €                                          │ │
│    │  │  Dernière synchro: 24/02/26 à 08:45                         │ │
│    │  │  89 transactions                                             │ │
│    │  └─────────────────────────────────────────────────────────────┘ │
│    │                                                                   │
└────┴──────────────────────────────────────────────────────────────────┘
```

### Sections Détaillées

#### Section 1 : Solde Consolidé (Card KPI)

```typescript
<Card className="mb-6">
  <CardContent className="pt-6">
    <div className="text-sm text-gray-500">Solde Total Consolidé</div>
    <div className="text-4xl font-bold font-mono mt-2">24 385,50 €</div>
    <div className="text-sm text-gray-500 mt-1">3 comptes actifs</div>
  </CardContent>
</Card>
```

#### Section 2 : Actions Globales

```typescript
<div className="flex gap-4 mb-6">
  <Button onClick={handleAddAccount}>
    <Plus className="mr-2" size={16} />
    Ajouter un compte
  </Button>
  <Button variant="outline" onClick={handleGlobalImport}>
    <Upload className="mr-2" size={16} />
    Importer CSV global (Boursorama)
  </Button>
</div>
```

#### Section 3 : Liste des Comptes (AccountCard)

```typescript
<div className="space-y-4">
  {accounts.map((account) => (
    <AccountCard
      key={account.id}
      account={account}
      onImport={() => handleImport(account.id)}
      onEdit={() => handleEdit(account.id)}
      onDelete={() => handleDelete(account.id)}
    />
  ))}
</div>
```

**Design AccountCard** :
```
┌─────────────────────────────────────────────────────────────────┐
│  🏦  Compte Courant Boursorama          [Importer CSV]  [...]   │
│  FR76 1234 5678 9012 3456 7890 12                               │
│  Solde: 2 450,80 €                                              │
│  Dernière synchro: 24/02/26 à 14:32 • 327 transactions          │
└─────────────────────────────────────────────────────────────────┘
│← Icon  Title                           Actions →                │
│   IBAN (text-sm, mono, gray-500)                               │
│   Solde (text-2xl, font-bold)                                   │
│   Metadata (text-xs, gray-500)                                  │
```

**Actions Dropdown `[...]`** :
```
┌────────────────────┐
│ ✏️  Modifier        │
│ 📥  Importer CSV   │
│ 🔄  Actualiser     │
│ ────────────────   │
│ 🗑️  Supprimer      │
└────────────────────┘
```

### Modal : Ajouter un Compte

```
╔════════════════════════════════════════════════════════════════╗
║  Ajouter un compte bancaire                                [×] ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  Nom du compte *                                               ║
║  [Compte Courant Boursorama                               ]   ║
║                                                                ║
║  IBAN                                                          ║
║  [FR76 1234 5678 9012 3456 7890 12                        ]   ║
║                                                                ║
║  Type de compte *                                              ║
║  [Compte courant ▾                                        ]   ║
║                                                                ║
║  Solde initial (optionnel)                                     ║
║  [0,00                                                    ] € ║
║                                                                ║
║  [Annuler]                                      [Ajouter]      ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
```

### Modal : Importer CSV

```
╔════════════════════════════════════════════════════════════════╗
║  Importer des transactions                                 [×] ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  Compte cible: Compte Courant Boursorama       [Changer]      ║
║                                                                ║
║  ┌──────────────────────────────────────────────────────────┐ ║
║  │                                                          │ ║
║  │              📁  Glissez votre fichier CSV ici          │ ║
║  │                   ou cliquez pour parcourir              │ ║
║  │                                                          │ ║
║  │            Formats acceptés: .csv (max 10 Mo)           │ ║
║  │            Banques supportées: Boursorama                │ ║
║  │                                                          │ ║
║  └──────────────────────────────────────────────────────────┘ ║
║                                                                ║
║  [?] Comment obtenir mon export CSV depuis Boursorama ?        ║
║                                                                ║
║  [Annuler]                                   [Importer]        ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
```

**Progress Bar lors de l'upload** :
```
┌────────────────────────────────────────────────────────────────┐
│  Import en cours...                                            │
│  ████████████████████████████████████████░░░░░░░░░░░  75%      │
│  245 transactions traitées / 327                               │
│  12 doublons ignorés                                           │
└────────────────────────────────────────────────────────────────┘
```

**Success Message** :
```
┌────────────────────────────────────────────────────────────────┐
│  ✅  Import réussi !                                           │
│  327 transactions importées                                    │
│  12 doublons ignorés                                           │
│  Solde mis à jour: 2 450,80 €                                  │
│                                                                │
│  [Voir les transactions]                       [Fermer]        │
└────────────────────────────────────────────────────────────────┘
```

---

## 3️⃣ Page : Transactions (Route: `/transactions`)

### Objectif
Vue avancée des transactions avec filtres multicritères, recherche, bulk actions, inline category edit, export CSV.

### Layout Complet

```
┌────┬──────────────────────────────────────────────────────────────────┐
│    │  [≡]  BankPulse    Transactions              [🔍] [@] [⚙]       │
│ S  ├──────────────────────────────────────────────────────────────────┤
│ I  │                                                                   │
│ D  │  ┌────────────────────────────────────────────────────────────┐ │
│ E  │  │  Filtres                                    [× Réinitialiser]│ │
│ B  │  │  [Compte ▾] [Catégorie ▾] [Marchand ▾]  Du [📅] Au [📅]   │ │
│ A  │  │  [Montant: min € — max €]  [Tags ▾]      [Rechercher...]   │ │
│ R  │  └────────────────────────────────────────────────────────────┘ │
│    │                                                                   │
│    │  327 transactions • 8 sélectionnées                              │
│    │  [⚡ Actions ▾]  [🏷 Tagger]  [📂 Catégoriser]  [📥 Exporter]   │
│    │                                                                   │
│    │  ┌────────────────────────────────────────────────────────────┐ │
│    │  │ ☐  Date     Description          Marchand      Montant Cat │ │
│    │  ├────────────────────────────────────────────────────────────┤ │
│    │  │ ☑  24/02   Courses aliment.     Carrefour   -45,80 € [🍽▾]│ │
│    │  │ ☑  23/02   Abonnement stream.   Netflix     -15,99 € [📺▾]│ │
│    │  │ ☐  22/02   Train Paris-Lyon     SNCF        -78,00 € [🚆▾]│ │
│    │  │ ☐  21/02   Salaire février      Acme Corp +3.500,00€ [💼▾]│ │
│    │  │ ☑  20/02   Déjeuner restau.     Le Zinc     -28,50 € [🍽▾]│ │
│    │  │ ☑  19/02   Essence              Total       -65,00 € [🚗▾]│ │
│    │  │ ☑  18/02   Abonnement cloud     OVH         -19,99 € [⚙▾] │ │
│    │  │ ☑  17/02   Pharmacie            Pharmacie   -23,45 € [🏥▾]│ │
│    │  │ ☑  16/02   Livres               FNAC        -42,90 € [📚▾]│ │
│    │  │ ☑  15/02   Loyer                Bailleur   -850,00 € [🏠▾]│ │
│    │  │                                                            │ │
│    │  │              [← Précédent]  Page 1/7  [Suivant →]        │ │
│    │  └────────────────────────────────────────────────────────────┘ │
│    │                                                                   │
└────┴──────────────────────────────────────────────────────────────────┘
```

### Sections Détaillées

#### Section 1 : Barre de Filtres (Sticky)

```typescript
<Card className="mb-4 sticky top-16 z-30">
  <CardContent className="py-4">
    <div className="flex items-center justify-between mb-3">
      <h3 className="text-sm font-medium text-gray-700">Filtres</h3>
      <Button variant="ghost" size="sm" onClick={resetFilters}>
        × Réinitialiser
      </Button>
    </div>
    
    <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
      {/* Row 1 */}
      <Select value={filters.account} onValueChange={setAccount}>
        <SelectTrigger>
          <SelectValue placeholder="Tous les comptes" />
        </SelectTrigger>
      </Select>
      
      <Select value={filters.category} onValueChange={setCategory}>
        <SelectTrigger>
          <SelectValue placeholder="Toutes catégories" />
        </SelectTrigger>
      </Select>
      
      <Select value={filters.merchant} onValueChange={setMerchant}>
        <SelectTrigger>
          <SelectValue placeholder="Tous marchands" />
        </SelectTrigger>
      </Select>
      
      <Popover>
        <PopoverTrigger asChild>
          <Button variant="outline">
            📅 {filters.dateRange || "Sélectionner période"}
          </Button>
        </PopoverTrigger>
        <PopoverContent>
          <Calendar mode="range" selected={dateRange} />
        </PopoverContent>
      </Popover>
      
      {/* Row 2 */}
      <div className="flex gap-2">
        <Input
          type="number"
          placeholder="Montant min €"
          value={filters.amountMin}
          onChange={(e) => setAmountMin(e.target.value)}
        />
        <Input
          type="number"
          placeholder="Montant max €"
          value={filters.amountMax}
          onChange={(e) => setAmountMax(e.target.value)}
        />
      </div>
      
      <Select value={filters.tags} onValueChange={setTags}>
        <SelectTrigger>
          <SelectValue placeholder="Tous les tags" />
        </SelectTrigger>
      </Select>
      
      <Input
        placeholder="Rechercher..."
        value={filters.search}
        onChange={(e) => setSearch(e.target.value)}
        className="md:col-span-2"
      />
    </div>
  </CardContent>
</Card>
```

#### Section 2 : Toolbar Actions

```typescript
<div className="flex items-center justify-between mb-4">
  <div className="text-sm text-gray-700">
    327 transactions {selectedCount > 0 && `• ${selectedCount} sélectionnées`}
  </div>
  
  <div className="flex gap-2">
    {selectedCount > 0 && (
      <>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size="sm">
              ⚡ Actions
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent>
            <DropdownMenuItem onClick={handleBulkCategorize}>
              📂 Catégoriser
            </DropdownMenuItem>
            <DropdownMenuItem onClick={handleBulkTag}>
              🏷 Tagger
            </DropdownMenuItem>
            <DropdownMenuItem onClick={handleBulkDelete}>
              🗑️ Supprimer
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </>
    )}
    
    <Button variant="outline" size="sm" onClick={handleExport}>
      📥 Exporter CSV
    </Button>
  </div>
</div>
```

#### Section 3 : Table Transactions

```typescript
<Card>
  <Table>
    <TableHeader>
      <TableRow>
        <TableHead className="w-12">
          <Checkbox
            checked={allSelected}
            onCheckedChange={toggleSelectAll}
          />
        </TableHead>
        <TableHead>Date</TableHead>
        <TableHead>Description</TableHead>
        <TableHead>Marchand</TableHead>
        <TableHead className="text-right">Montant</TableHead>
        <TableHead>Catégorie</TableHead>
      </TableRow>
    </TableHeader>
    <TableBody>
      {transactions.map((tx) => (
        <TransactionRow
          key={tx.id}
          transaction={tx}
          selected={selectedIds.includes(tx.id)}
          onSelect={() => toggleSelect(tx.id)}
          onCategoryChange={(categoryId) => handleCategoryChange(tx.id, categoryId)}
        />
      ))}
    </TableBody>
  </Table>
  
  {/* Pagination */}
  <div className="flex items-center justify-center gap-2 py-4 border-t">
    <Button
      variant="outline"
      size="sm"
      onClick={prevPage}
      disabled={page === 1}
    >
      ← Précédent
    </Button>
    <span className="text-sm text-gray-600">
      Page {page} / {totalPages}
    </span>
    <Button
      variant="outline"
      size="sm"
      onClick={nextPage}
      disabled={page === totalPages}
    >
      Suivant →
    </Button>
  </div>
</Card>
```

**TransactionRow Component** :
```typescript
function TransactionRow({ transaction, selected, onSelect, onCategoryChange }) {
  return (
    <TableRow className={selected ? "bg-primary-50" : ""}>
      <TableCell>
        <Checkbox checked={selected} onCheckedChange={onSelect} />
      </TableCell>
      <TableCell className="text-sm text-gray-700">
        {formatDate(transaction.date)}
      </TableCell>
      <TableCell className="text-sm">
        {transaction.description}
      </TableCell>
      <TableCell className="text-sm text-gray-600">
        {transaction.merchant.name}
      </TableCell>
      <TableCell className="text-right font-mono font-semibold">
        <span className={transaction.amount < 0 ? "text-danger-500" : "text-success-500"}>
          {formatAmount(transaction.amount)}
        </span>
      </TableCell>
      <TableCell>
        <Select
          value={transaction.category_id}
          onValueChange={onCategoryChange}
        >
          <SelectTrigger className="w-32">
            <SelectValue>
              {transaction.category?.icon} {transaction.category?.name}
            </SelectValue>
          </SelectTrigger>
          <SelectContent>
            {categories.map((cat) => (
              <SelectItem key={cat.id} value={cat.id}>
                {cat.icon} {cat.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </TableCell>
    </TableRow>
  )
}
```

### Modal : Bulk Categorize

```
╔════════════════════════════════════════════════════════════════╗
║  Catégoriser 8 transactions                                [×] ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  Nouvelle catégorie *                                          ║
║  [🍽 Alimentation > Supermarché                           ▾]  ║
║                                                                ║
║  Appliquer à toutes les transactions de ces marchands ?        ║
║  ☐  Carrefour Market (12 autres transactions)                 ║
║  ☐  Total (5 autres transactions)                             ║
║                                                                ║
║  [Annuler]                                [Appliquer]          ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
```

---

## 4️⃣ Page : Budgets (Route: `/budgets`)

### Objectif
Créer et suivre des budgets par catégorie, voir progression temps réel, recevoir alertes approche/dépassement.

### Layout Complet

```
┌────┬──────────────────────────────────────────────────────────────────┐
│    │  [≡]  BankPulse    Budgets > Février 2026    [🔍] [@] [⚙]       │
│ S  ├──────────────────────────────────────────────────────────────────┤
│ I  │                                                                   │
│ D  │  Vue mensuelle: [← Jan] [Février 2026] [Mars →]   [+ Nouveau]   │
│ E  │                                                                   │
│ B  │  ┌────────────────────────┐  ┌────────────────────────────────┐ │
│ A  │  │  Budget Total          │  │  Dépensé                       │ │
│ R  │  │  2 500,00 €            │  │  1 842,00 €  (74%)             │ │
│    │  │  7 catégories          │  │  Reste: 658,00 €               │ │
│    │  └────────────────────────┘  └────────────────────────────────┘ │
│    │                                                                   │
│    │  ┌────────────────────────────────────────────────────────────┐ │
│    │  │  🍽  Alimentation                                   [...]   │ │
│    │  │  320,00 € / 500,00 €                               64%      │ │
│    │  │  ████████████████░░░░░░░░░                                  │ │
│    │  │  Reste: 180,00 € • 8 jours restants • Rythme: OK ✓         │ │
│    │  └────────────────────────────────────────────────────────────┘ │
│    │                                                                   │
│    │  ┌────────────────────────────────────────────────────────────┐ │
│    │  │  🚆  Transport                                     [...]   │ │
│    │  │  156,00 € / 200,00 €                               78%      │ │
│    │  │  ████████████████████░░░░░              ⚠️ Attention        │ │
│    │  │  Reste: 44,00 € • 8 jours restants • Rythme: Rapide        │ │
│    │  └────────────────────────────────────────────────────────────┘ │
│    │                                                                   │
│    │  ┌────────────────────────────────────────────────────────────┐ │
│    │  │  🏠  Logement                                      [...]   │ │
│    │  │  850,00 € / 850,00 €                              100%      │ │
│    │  │  ████████████████████████████       🔴 Budget atteint       │ │
│    │  │  Dépassement: 0,00 € • Fixe mensuel                        │ │
│    │  └────────────────────────────────────────────────────────────┘ │
│    │                                                                   │
│    │  ┌────────────────────────────────────────────────────────────┐ │
│    │  │  📺  Loisirs & Culture                             [...]   │ │
│    │  │  87,00 € / 150,00 €                                58%      │ │
│    │  │  ████████████████░░░░░░░░░░░░                               │ │
│    │  │  Reste: 63,00 € • 8 jours restants • Rythme: OK ✓          │ │
│    │  └────────────────────────────────────────────────────────────┘ │
│    │                                                                   │
└────┴──────────────────────────────────────────────────────────────────┘
```

### Sections Détaillées

#### Section 1 : Header avec Sélecteur de Période

```typescript
<div className="flex items-center justify-between mb-6">
  <div className="flex items-center gap-4">
    <span className="text-sm text-gray-600">Vue mensuelle:</span>
    <div className="flex items-center gap-2">
      <Button variant="outline" size="sm" onClick={prevMonth}>
        ← Jan
      </Button>
      <span className="font-semibold">Février 2026</span>
      <Button variant="outline" size="sm" onClick={nextMonth}>
        Mars →
      </Button>
    </div>
  </div>
  
  <Button onClick={handleCreateBudget}>
    <Plus className="mr-2" size={16} />
    Nouveau budget
  </Button>
</div>
```

#### Section 2 : Résumé du Mois (KPI Cards)

```typescript
<div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
  <Card>
    <CardContent className="pt-6">
      <div className="text-sm text-gray-500">Budget Total</div>
      <div className="text-3xl font-bold font-mono mt-2">2 500,00 €</div>
      <div className="text-sm text-gray-500 mt-1">7 catégories</div>
    </CardContent>
  </Card>
  
  <Card>
    <CardContent className="pt-6">
      <div className="text-sm text-gray-500">Dépensé</div>
      <div className="text-3xl font-bold font-mono mt-2">1 842,00 €</div>
      <div className="flex items-center gap-2 mt-1">
        <Badge variant="default">74%</Badge>
        <span className="text-sm text-gray-500">Reste: 658,00 €</span>
      </div>
    </CardContent>
  </Card>
</div>
```

#### Section 3 : Liste des Budgets (BudgetProgressCard)

```typescript
<div className="space-y-4">
  {budgets.map((budget) => (
    <BudgetProgressCard
      key={budget.id}
      budget={budget}
      onEdit={() => handleEdit(budget.id)}
      onDelete={() => handleDelete(budget.id)}
    />
  ))}
</div>
```

**Design BudgetProgressCard** :
```
┌────────────────────────────────────────────────────────────────┐
│  🍽  Alimentation                                      [...]   │
│  320,00 € / 500,00 €                                  64%      │
│  ████████████████░░░░░░░░░                                     │
│  Reste: 180,00 € • 8 jours restants • Rythme: OK ✓            │
└────────────────────────────────────────────────────────────────┘
│← Icon  Name                                          Actions → │
│   Spent / Limit                                      Percentage│
│   Progress Bar (color-coded)                                   │
│   Metadata (remaining, days left, pace)                        │
```

**BudgetProgressCard Component** :
```typescript
function BudgetProgressCard({ budget, onEdit, onDelete }) {
  const percentage = (budget.spent / budget.limit) * 100
  const alertType = getAlertType(percentage)
  
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-3">
            <span className="text-2xl">{budget.category.icon}</span>
            <div>
              <h3 className="font-semibold">{budget.category.name}</h3>
              <div className="text-sm text-gray-600 mt-1">
                <span className="font-mono">{formatAmount(budget.spent)}</span>
                {" / "}
                <span className="font-mono">{formatAmount(budget.limit)}</span>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Badge variant={alertType === "over" ? "destructive" : "default"}>
              {percentage.toFixed(0)}%
            </Badge>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm">...</Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                <DropdownMenuItem onClick={onEdit}>✏️ Modifier</DropdownMenuItem>
                <DropdownMenuItem onClick={onDelete}>🗑️ Supprimer</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
        
        <Progress value={percentage} className="h-2 mb-3" />
        
        <div className="flex items-center gap-4 text-sm text-gray-600">
          <span>Reste: {formatAmount(budget.limit - budget.spent)}</span>
          <span>•</span>
          <span>{budget.daysRemaining} jours restants</span>
          <span>•</span>
          <span className="flex items-center gap-1">
            Rythme: {budget.pace === "ok" ? "OK ✓" : "Rapide ⚠️"}
          </span>
        </div>
        
        {alertType === "over" && (
          <Alert variant="destructive" className="mt-3">
            🔴 Budget dépassé de {formatAmount(budget.spent - budget.limit)}
          </Alert>
        )}
        
        {alertType === "near" && (
          <Alert variant="warning" className="mt-3">
            ⚠️ Attention, vous approchez de la limite
          </Alert>
        )}
      </CardContent>
    </Card>
  )
}
```

### Modal : Créer/Éditer Budget

```
╔════════════════════════════════════════════════════════════════╗
║  Créer un budget                                           [×] ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  Catégorie *                                                   ║
║  [🍽 Alimentation                                          ▾]  ║
║                                                                ║
║  Montant limite *                                              ║
║  [500,00                                                  ] € ║
║                                                                ║
║  Période *                                                     ║
║  [Mensuel                                                  ▾]  ║
║                                                                ║
║  Mois de début                                                 ║
║  [Février 2026                                             ▾]  ║
║                                                                ║
║  Alerte approche (optionnel)                                   ║
║  ☑  M'alerter à 80% de la limite                              ║
║                                                                ║
║  [Annuler]                                      [Créer]        ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
```

---

## 5️⃣ Page : Login (Route: `/login`)

### Objectif
Authentification utilisateur avec email + password. Lien vers register.

### Layout Complet

```
┌────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                                                                     │
│                         ┌───────────────────┐                      │
│                         │                   │                      │
│                         │   BankPulse       │                      │
│                         │   [Logo]          │                      │
│                         │                   │                      │
│                         │  Connexion        │                      │
│                         │                   │                      │
│                         │  Email *          │                      │
│                         │  [john@acme.com  ]│                      │
│                         │                   │                      │
│                         │  Mot de passe *   │                      │
│                         │  [············   ]│                      │
│                         │                   │                      │
│                         │  ☐ Se souvenir    │                      │
│                         │                   │                      │
│                         │  [Se connecter]   │                      │
│                         │                   │                      │
│                         │  Pas de compte ?  │                      │
│                         │  [Créer un compte]│                      │
│                         │                   │                      │
│                         └───────────────────┘                      │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

**Code structure** :
```typescript
// app/(auth)/login/page.tsx
export default function LoginPage() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto w-12 h-12 bg-primary-500 rounded-lg mb-4" />
          <CardTitle className="text-2xl">BankPulse</CardTitle>
          <CardDescription>Connectez-vous à votre compte</CardDescription>
        </CardHeader>
        <CardContent>
          <LoginForm />
        </CardContent>
      </Card>
    </div>
  )
}
```

**LoginForm Component** :
```typescript
function LoginForm() {
  const form = useForm<LoginSchema>({
    resolver: zodResolver(loginSchema),
  })
  
  async function onSubmit(data: LoginSchema) {
    const res = await fetch("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    })
    if (res.ok) {
      router.push("/dashboard")
    }
  }
  
  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email *</FormLabel>
              <FormControl>
                <Input
                  type="email"
                  placeholder="john@acme.com"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        
        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Mot de passe *</FormLabel>
              <FormControl>
                <Input type="password" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        
        <div className="flex items-center">
          <Checkbox id="remember" />
          <label htmlFor="remember" className="ml-2 text-sm">
            Se souvenir de moi
          </label>
        </div>
        
        <Button type="submit" className="w-full">
          Se connecter
        </Button>
        
        <div className="text-center text-sm text-gray-600">
          Pas de compte ?{" "}
          <Link href="/register" className="text-primary-600 hover:underline">
            Créer un compte
          </Link>
        </div>
      </form>
    </Form>
  )
}
```

---

## 6️⃣ Page : Register (Route: `/register`)

### Layout Complet

```
┌────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                         ┌───────────────────┐                      │
│                         │                   │                      │
│                         │   BankPulse       │                      │
│                         │   [Logo]          │                      │
│                         │                   │                      │
│                         │  Créer un compte  │                      │
│                         │                   │                      │
│                         │  Prénom *         │                      │
│                         │  [John           ]│                      │
│                         │                   │                      │
│                         │  Nom *            │                      │
│                         │  [Doe            ]│                      │
│                         │                   │                      │
│                         │  Email *          │                      │
│                         │  [john@acme.com  ]│                      │
│                         │                   │                      │
│                         │  Mot de passe *   │                      │
│                         │  [············   ]│                      │
│                         │  Min. 8 caractères│                      │
│                         │                   │                      │
│                         │  [Créer mon compte]│                     │
│                         │                   │                      │
│                         │  Déjà un compte ? │                      │
│                         │  [Se connecter]   │                      │
│                         │                   │                      │
│                         └───────────────────┘                      │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

---

## 7️⃣ Page : Paramètres (Route: `/settings`)

### Layout Complet

```
┌────┬──────────────────────────────────────────────────────────────────┐
│    │  [≡]  BankPulse    Paramètres                [🔍] [@] [⚙]       │
│ S  ├──────────────────────────────────────────────────────────────────┤
│ I  │                                                                   │
│ D  │  [Mon Profil] [Sécurité] [Notifications] [Catégories] [À propos]│
│ E  │                                                                   │
│ B  │  ┌────────────────────────────────────────────────────────────┐ │
│ A  │  │  Mon Profil                                                │ │
│ R  │  │                                                             │ │
│    │  │  Prénom *                                                  │ │
│    │  │  [John                                                    ]│ │
│    │  │                                                             │ │
│    │  │  Nom *                                                     │ │
│    │  │  [Doe                                                     ]│ │
│    │  │                                                             │ │
│    │  │  Email                                                     │ │
│    │  │  [john@acme.com                                          ]│ │
│    │  │  (non modifiable)                                          │ │
│    │  │                                                             │ │
│    │  │  [Enregistrer les modifications]                           │ │
│    │  └────────────────────────────────────────────────────────────┘ │
│    │                                                                   │
└────┴──────────────────────────────────────────────────────────────────┘
```

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

### Phase 2 : Layout & Navigation (Jour 2-3)
1. Composant `Sidebar` (collapsed + hover expand)
2. Composant `TopBar` (breadcrumbs, search, user menu)
3. Layout principal (`app/layout.tsx`)
4. Navigation items + active states

### Phase 3 : Auth (Jour 3-4)
1. Pages Login + Register
2. Forms avec validation (zod + react-hook-form)
3. Connexion API `/auth/login` et `/auth/register`
4. JWT storage (HttpOnly cookies)
5. Middleware auth (redirect si non connecté)

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
- [ ] Sidebar collapsed (64px) avec hover expand
- [ ] TopBar (breadcrumbs, search, user menu)
- [ ] Layout principal responsive
- [ ] Mobile overlay sidebar (Sheet)

### Pages
- [ ] Dashboard (KPIs, Donut, Top Marchands, Abonnements)
- [ ] Mes Comptes (liste, import CSV, CRUD)
- [ ] Transactions (filtres, table, bulk actions, export)
- [ ] Budgets (progression, alertes, CRUD)
- [ ] Login / Register
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
