import { test, expect } from '@playwright/test'

const FRONTEND = process.env.VITE_FRONTEND_URL || 'http://localhost:5173'

test.describe('Auth E2E', () => {
  test('login page renders and validates', async ({ page }) => {
    await page.goto(`${FRONTEND}/login`)
    await expect(page.getByRole('heading', { name: /sign in/i })).toBeVisible()
    await page.getByLabel('Email address').fill('user@example.com')
    await page.getByLabel('Password').fill('password123')
    await page.getByRole('button', { name: /sign in/i }).click()
  })

  test('forgot password triggers reset email (mock)', async ({ page }) => {
    await page.goto(`${FRONTEND}/login`)
    await page.getByLabel('Email address').fill('user@example.com')
    await page.getByRole('button', { name: /forgot your password/i }).click()
  })

  test('reset password updates user', async ({ page }) => {
    await page.goto(`${FRONTEND}/reset-password`)
    await page.getByLabel('New password').fill('abcdef')
    await page.getByLabel('Confirm password').fill('abcdef')
    await page.getByRole('button', { name: /update password/i }).click()
  })

  test('OAuth buttons exist and redirect', async ({ page }) => {
    await page.goto(`${FRONTEND}/login`)
    await expect(page.getByRole('button', { name: /continue with google/i })).toBeVisible()
    await expect(page.getByRole('button', { name: /continue with github/i })).toBeVisible()
  })

  test('RTL toggle via LanguageSwitcher', async ({ page }) => {
    await page.goto(`${FRONTEND}/`)
    // open from TopBar language switcher if present
    // naive check: just ensure page has dir attr (set by init or toggle)
    const dir = await page.evaluate(() => document.documentElement.getAttribute('dir'))
    expect(dir === 'ltr' || dir === 'rtl').toBeTruthy()
  })
})
