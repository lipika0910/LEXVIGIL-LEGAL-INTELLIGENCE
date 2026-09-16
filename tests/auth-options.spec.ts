import { test, expect } from "@playwright/test";
import { join } from "node:path";
import { tmpdir } from "node:os";

test("Google entry, safe callback failure, recovery request and invalid reset", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", e => errors.push(e.message));
  await page.route("**/api/auth/options", r => r.fulfill({ json: { managed: true } }));
  await page.route("**/api/auth/google/start", r => r.fulfill({ json: { url: "/login?auth_error=flow_failed" } }));
  await page.route("**/api/auth/recovery/start", r => r.fulfill({ json: { message: "If this address is eligible, check your inbox for the newest reset link." } }));
  await page.goto("/login");
  await expect(page).toHaveTitle(/LexVigil/i);
  await expect(page.getByRole("heading", { name: "Welcome back" })).toBeVisible();
  await page.getByRole("button", { name: "Continue with Google" }).click();
  await expect(page.getByRole("status")).toContainText("could not be completed");
  await expect(page).toHaveURL(/\/login$/);
  await page.getByRole("link", { name: "Forgot password?" }).click();
  await page.getByLabel("Email", { exact: true }).fill("test@example.com");
  await page.getByRole("button", { name: "Send reset link" }).click();
  await expect(page.getByRole("status")).toContainText("If this address is eligible");
  await page.setViewportSize({ width: 390, height: 844 });
  await page.screenshot({ path: join(process.env.LEXVIGIL_E2E_ARTIFACTS || tmpdir(), "recovery-mobile.png"), fullPage: true });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.goto("/reset-password");
  await expect(page.getByRole("button", { name: "Update password" })).toBeDisabled();
  await expect(page.getByRole("alert")).toBeVisible();
  await expect(page.locator("vite-error-overlay")).toHaveCount(0);
  expect(errors).toEqual([]);
});

test("recovery validates matching passwords and returns to sign in", async ({ page }) => {
  let updates = 0;
  await page.route("**/api/auth/recovery/status", r => r.fulfill({ json: { ready: true } }));
  await page.route("**/api/auth/recovery/password", r => { updates++; return r.fulfill({ json: { message: "Password updated." } }); });
  await page.goto("/reset-password");
  await page.getByLabel("New password", { exact: true }).fill("a-test-password-123");
  await page.getByLabel("Confirm new password", { exact: true }).fill("different-password-123");
  await page.getByRole("button", { name: "Update password" }).click();
  await expect(page.getByRole("alert")).toContainText("Passwords do not match");
  expect(updates).toBe(0);
  await page.getByLabel("Confirm new password", { exact: true }).fill("a-test-password-123");
  await page.getByRole("button", { name: "Update password" }).click();
  await expect(page.getByRole("status")).toContainText("Password updated");
  await expect(page).toHaveURL(/\/login$/);
  expect(updates).toBe(1);
});
