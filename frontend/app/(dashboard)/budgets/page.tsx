import { cookies } from "next/headers"

import { BudgetsList } from "@/components/budgets/budgets-list"
import type { BudgetsProgress, CategoryWithChildrenResponse } from "@/types/api"

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

interface Props {
  searchParams: Promise<{ month?: string }>
}

export default async function BudgetsPage({ searchParams }: Props) {
  const cookieStore = await cookies()
  const token = cookieStore.get("access_token")?.value ?? ""
  const { month } = await searchParams

  const progressUrl = new URL(`${API_URL}/api/v1/budgets/progress`)
  if (month) progressUrl.searchParams.set("month", month)

  const [progressRes, categoriesRes] = await Promise.all([
    fetch(progressUrl.toString(), {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
    }).catch(() => null),
    fetch(`${API_URL}/api/v1/categories`, {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
    }).catch(() => null),
  ])

  let progress: BudgetsProgress = { month: month ?? null, items: [] }
  let categories: CategoryWithChildrenResponse[] = []

  if (progressRes?.ok) {
    progress = await progressRes.json()
  }
  if (categoriesRes?.ok) {
    categories = await categoriesRes.json()
  }

  return (
    <BudgetsList initialProgress={progress} categories={categories} currentMonth={month ?? null} />
  )
}
