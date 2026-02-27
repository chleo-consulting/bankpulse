# Architecture Frontend

Stack : Next.js 16.1.6, App Router, TypeScript strict, Tailwind v4, shadcn/ui v3 (new-york/neutral), Bun.

## Arborescence

```
frontend/
├── app/
│   ├── (auth)/
│   │   ├── layout.tsx                    ← layout centré sans Sidebar (fond gray-50)
│   │   ├── login/page.tsx                ← page login — Zod + react-hook-form
│   │   └── register/page.tsx             ← page register — Zod + react-hook-form + auto-login
│   ├── (dashboard)/
│   │   ├── layout.tsx                    ← DashboardLayout (client, useState sidebarOpen)
│   │   ├── dashboard/page.tsx            ← Server Component async, fetch 4 endpoints, empty state
│   │   ├── accounts/page.tsx             ← Server Component async, fetch comptes, passe à AccountsList
│   │   ├── transactions/page.tsx         ← Server Component async, fetch txns+cats+accounts+tags
│   │   ├── budgets/page.tsx              ← Server Component async, searchParams month, fetch progress+cats
│   │   └── settings/page.tsx             ← Server Component shell, max-w-2xl, importe SettingsTabs
│   ├── api/auth/
│   │   ├── login/route.ts               ← proxy → FastAPI + Set-Cookie access_token HttpOnly
│   │   ├── register/route.ts            ← proxy → FastAPI register + auto-login + Set-Cookie
│   │   └── logout/route.ts              ← Delete-Cookie + appel backend best-effort
│   ├── api/accounts/
│   │   ├── route.ts                     ← GET (liste) + POST (créer) → FastAPI avec Bearer
│   │   ├── [id]/route.ts                ← PATCH + DELETE → FastAPI avec Bearer
│   │   └── [id]/import/route.ts         ← POST multipart → FastAPI /accounts/{id}/import
│   ├── api/transactions/
│   │   ├── route.ts                     ← GET list cursor-based → FastAPI
│   │   ├── search/route.ts              ← GET search → FastAPI
│   │   ├── bulk-tag/route.ts            ← POST → FastAPI
│   │   ├── export/route.ts              ← GET CSV → FastAPI
│   │   └── [id]/category/route.ts       ← PATCH → FastAPI
│   ├── api/budgets/
│   │   ├── route.ts                     ← GET liste + POST créer → FastAPI
│   │   ├── progress/route.ts            ← GET progression par mois → FastAPI
│   │   └── [id]/route.ts                ← PATCH + DELETE → FastAPI
│   ├── globals.css                       ← design tokens BankPulse + shadcn vars
│   ├── layout.tsx                        ← root layout (Inter + JetBrains Mono, lang="fr", suppressHydrationWarning)
│   └── page.tsx                          ← redirect /dashboard
├── components/
│   ├── layout/
│   │   ├── sidebar.tsx                   ← Sidebar (desktop fixed w-16 hover:w-60) + MobileSidebar
│   │   └── top-bar.tsx                   ← TopBar sticky + Breadcrumbs + UserMenu (logout branché)
│   └── ui/                              ← composants shadcn (17 installés)
├── components/shared/
│   ├── kpi-card.tsx                      ← KPICard (titre, valeur mono, delta coloré)
│   └── empty-state.tsx                   ← EmptyState (icône, texte, bouton Link)
├── components/dashboard/
│   └── category-chart.tsx               ← "use client" — Recharts PieChart donut + légende
├── components/accounts/
│   ├── accounts-list.tsx                 ← "use client" — liste + solde consolidé + modals
│   ├── add-account-modal.tsx             ← Dialog Zod + react-hook-form (nom, IBAN, type, solde)
│   └── import-csv-modal.tsx             ← dropzone drag&drop + upload multipart + résultat
├── components/transactions/
│   └── transactions-list.tsx             ← "use client" — filtres 8 critères, table, pagination, bulk, export
├── components/budgets/
│   ├── budgets-list.tsx                  ← "use client" — navigation mensuelle, KPI cards, liste, empty state
│   ├── budget-progress-card.tsx          ← progress bar tricolore, alertes, dropdown actions
│   └── budget-modal.tsx                  ← Dialog create/edit — deux forms Zod distincts (create ≠ edit)
├── components/settings/
│   └── settings-tabs.tsx                 ← "use client" — 3 onglets (profil/sécurité/à propos), UI only sans backend
├── hooks/
│   └── useAuth.ts                        ← useAuth() : logout() + isLoggingOut
├── lib/
│   ├── utils.ts                         ← cn() (shadcn)
│   └── format.ts                        ← formatAmount (EUR fr-FR), formatDate (fr-FR)
├── types/api.ts                         ← LoginRequest, RegisterRequest, TokenResponse, UserResponse, ApiError + types dashboard + BankAccountResponse, ImportResult, AccountImportSummary + TagResponse, CategoryResponse, CategoryWithChildrenResponse, TransactionResponse, CursorTransactionListResponse + BudgetResponse, BudgetProgressItem, BudgetsProgress
├── proxy.ts                             ← protection routes (Next.js 16, anciennement middleware.ts)
├── .env.local                           ← NEXT_PUBLIC_API_URL=http://localhost:8000
└── next.config.ts                       ← proxy rewrites /api/v1/* → FastAPI :8000
```

## Décisions frontend

- **Proxy CORS** : `next.config.ts` rewrites `/api/v1/:path*` → `NEXT_PUBLIC_API_URL` — pas de config CORS côté backend
- **Design tokens** : bloc `@theme` dans `globals.css` — couleurs `primary-500/600/700`, `success-500`, `warning-500`, `danger-500`, `sidebar-bg/border`
- **Fonts** : Inter (`--font-inter`) + JetBrains Mono (`--font-jetbrains-mono`) via `next/font/google`
- **shadcn v3** : package `radix-ui` combiné + `@import "shadcn/tailwind.css"` dans globals.css
- **Tailwind v4** : configuration CSS-first via `@theme` — pas de `tailwind.config.ts` pour les couleurs
- **Sidebar collapse** : pattern `showLabel: boolean` — `false` → `opacity-0 group-hover:opacity-100`, `true` → toujours visible. Deux exports : `Sidebar` (desktop, `fixed w-16 hover:w-60 group`) + `MobileSidebar` (mobile dans Sheet, `w-60` expanded).
- **Couleurs sidebar** : utiliser les valeurs hex directes `bg-[#1f2937]` / `border-[#374151]` plutôt que les classes générées (`bg-sidebar-bg`) — plus fiable avec les blocs `@theme` imbriqués en Tailwind v4.
- **`suppressHydrationWarning`** : à mettre sur `<body>` dans `app/layout.tsx` pour éviter les fausses erreurs d'hydratation causées par des extensions browser (ex: `data-gptw=""`).
- **`SheetContent` sans titre visible** : Radix UI requiert un `DialogTitle` accessible → `<VisuallyHidden.Root><SheetTitle>Navigation</SheetTitle></VisuallyHidden.Root>` dans le SheetContent. `VisuallyHidden` de `radix-ui` est un namespace → utiliser `VisuallyHidden.Root`.
- **Cookies HttpOnly pour les tokens** : ne jamais stocker les JWT en `localStorage`. Les route handlers `/app/api/auth/*` font le proxy vers FastAPI et appellent `response.cookies.set("access_token", ..., { httpOnly: true, sameSite: "lax" })`. Le cookie est invisible au JS client.
- **Auth proxy pattern** : les route handlers Next.js (`/api/auth/login`, `/register`, `/logout`) servent d'intermédiaire entre le browser et FastAPI — ils reçoivent les credentials, appellent FastAPI, et gèrent les cookies. Le browser ne contacte jamais FastAPI directement pour l'auth.
- **`proxy.ts`** (pas `middleware.ts`) : Next.js 16 déprécie `middleware.ts` → utiliser `proxy.ts` avec la fonction exportée `proxy()` (même API, même `config` export).
- **Dashboard data fetching** : Server Component async + `cookies()` (next/headers) → fetch direct FastAPI avec `Authorization: Bearer`. `cache: "no-store"` obligatoire. `Promise.all` pour les fetches parallèles. Retourner `null` si fetch échoue → afficher empty state. Pas de route handler intermédiaire pour les reads (contrairement à l'auth).
- **Recharts** : toujours `"use client"`. PieChart donut = `<Pie innerRadius={65} outerRadius={95} strokeWidth={0}>`. Passer les données sérialisées du Server Component comme props — jamais d'ORM, que des objets JSON plats.
- **Zod v4 + react-hook-form** : ne pas utiliser `.default()` ni `z.coerce.number()` dans les schemas — les deux créent un mismatch input/output type incompatible avec `zodResolver`. Pour les champs numériques, utiliser `z.number()` + `onChange={(e) => onChange(e.target.valueAsNumber || 0)}`. Mettre les valeurs par défaut uniquement dans `defaultValues` de `useForm`.
- **Sonner Toaster** : importer directement `Toaster` depuis `"sonner"` dans `app/layout.tsx` (pas le wrapper `components/ui/sonner.tsx` qui dépend de `next-themes`). Usage client inchangé : `import { toast } from "sonner"`.
- **Route handlers avec segments dynamiques** : en Next.js 15/16+, `params` est une Promise → `const { id } = await params`. Typer comme `{ params: Promise<{ id: string }> }`.
- **Mutations client → route handlers** : les pages avec CRUD utilisent le pattern Server Component (fetch initial) + Client Component (état + mutations). Les mutations appellent `/api/<resource>/[id]` (route handlers Next.js) qui lisent le cookie HttpOnly et proxifient vers FastAPI avec `Authorization: Bearer`.
- **`searchParams` en Next.js 15/16+** : comme `params`, `searchParams` dans `page.tsx` est une Promise → `const { month } = await searchParams`. Typer comme `{ searchParams: Promise<{ month?: string }> }`. Pattern URL-based state : Client Component fait `router.push('/path?param=value')` → Server Component re-render avec nouvelles données.
- **Progress bar couleur** : `[&>div]:bg-emerald-500` sur le composant root `<Progress>` pour surcharger le `bg-primary` hardcodé sur l'indicateur interne. Tricolore : `[&>div]:bg-emerald-500` (ok) / `[&>div]:bg-amber-500` (near_limit) / `[&>div]:bg-red-500` (over_budget).
- **`EmptyState` partagé** : le composant `components/shared/empty-state.tsx` n'accepte que `href` pour l'action (bouton `<Link>`). Si l'action doit déclencher une modale (`onClick`), créer un empty state inline directement dans le composant client — ne pas modifier le composant partagé.
- **`loading.tsx` App Router** : placer un `loading.tsx` dans le même segment qu'une `page.tsx` Server Component → Next.js crée un `<Suspense>` boundary automatique. Skeleton structuré en miroir de la page réelle (même grid, même nombre de cards/rows). Aucun code Suspense manuel nécessaire.
- **Page Paramètres (`/settings`)** : UI-only sans appel backend (pas d'endpoint `/users/me` dans l'API FastAPI). Onglets : Mon Profil (form disabled + badge "Bientôt disponible"), Sécurité (idem), À propos (static). À connecter quand un endpoint de profil sera ajouté.
- **Modal create vs edit — deux forms** : quand create et edit ont des schemas Zod différents (ex: category_id requis en create, absent en edit), créer deux instances `useForm` distinctes (toujours initialisées — pas de hook conditionnel). Réinitialiser le form approprié dans un `useEffect` sur `[open, editItem]`.
