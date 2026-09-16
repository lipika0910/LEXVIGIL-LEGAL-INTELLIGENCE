import { test, expect } from '@playwright/test';

test('API outage is visible and authentication options recover on retry', async ({ page }) => {
  let available = false;
  await page.route('**/api/auth/options', r => available
    ? r.fulfill({ json: { managed: true } })
    : r.fulfill({ status: 500, body: '' }));
  await page.goto('/login');
  await expect(page.getByRole('alert')).toContainText('service is unavailable');
  available = true;
  await page.getByRole('button', { name: 'Retry connection' }).click();
  await expect(page.getByRole('button', { name: 'Continue with Google' })).toBeVisible();
  await expect(page.getByRole('link', { name: 'Forgot password?' })).toBeVisible();
  await page.route('**/api/auth/login', r => r.fulfill({ status: 502, body: '' }));
  await page.getByLabel('Email', { exact: true }).fill('outage@example.com');
  await page.getByLabel('Password', { exact: true }).fill('synthetic-password-123');
  await page.getByRole('button', { name: 'Sign in', exact: true }).click();
  await expect(page.getByRole('alert')).toContainText('service is unavailable');
});
