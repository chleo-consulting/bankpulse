# BankPulse - Pages Détaillées (UI)

> Voir aussi : [SPEC_UI.md](./SPEC_UI.md) pour le Design System, la Structure Globale et le Plan d'Implémentation.

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
