export function recommendationBadge(envelope) {
  if (envelope?.used_ai === true) {
    return {
      desktop: 'AI · Рекомендуемый шаг',
      mobile: 'AI · Рекомендуемый шаг',
    }
  }
  return {
    desktop: 'Рекомендуемый шаг',
    mobile: 'Рекомендуемый шаг',
  }
}

export function primaryRecommendation(envelope) {
  const items = envelope?.recommendations
  return Array.isArray(items) && items.length > 0 ? items[0] : null
}
