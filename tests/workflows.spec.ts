import { test, expect } from "@playwright/test";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { mkdirSync } from "node:fs";
const artifacts =
  process.env.LEXVIGIL_E2E_ARTIFACTS || join(tmpdir(), "lexvigil-e2e");
mkdirSync(artifacts, { recursive: true });

test("confirmation-required signup stays outside protected workspace", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.route("**/api/auth/register", (route) =>
    route.fulfill({
      json: {
        requires_confirmation: true,
        message:
          "Check your email to confirm your account, then return here to sign in.",
      },
    }),
  );
  await page.goto("/app/contracts");
  await expect(page).toHaveURL(/\/login$/);
  await expect(page).toHaveTitle(/LexVigil/i);
  await page.getByRole("button", { name: "Create an account" }).click();
  await page
    .getByLabel("Email", { exact: true })
    .fill("confirmation@example.com");
  await page.getByLabel("Password", { exact: true }).fill("safe-test-password");
  await page
    .getByRole("button", { name: "Create account", exact: true })
    .click();
  await expect(page.getByRole("status")).toContainText("Check your email");
  await expect(
    page.getByRole("heading", { name: "Welcome back" }),
  ).toBeVisible();
  await expect(page.getByLabel("Password", { exact: true })).toHaveValue("");
  await expect(page).toHaveURL(/\/login$/);
  await expect(page.locator("vite-error-overlay")).toHaveCount(0);
  await page.screenshot({
    path: join(artifacts, "confirmation.png"),
    fullPage: true,
  });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.screenshot({
    path: join(artifacts, "confirmation-mobile.png"),
    fullPage: true,
  });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  expect(errors).toEqual([]);
});
test("account, sample, save, sources, export, delete and privacy", async ({
  page,
  browser,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("/");
  await expect(page).toHaveTitle(/LexVigil/i);
  await expect(page.locator("vite-error-overlay")).toHaveCount(0);
  await expect(
    page.getByRole("heading", { name: /Clarity in the law/ }),
  ).toBeVisible();
  await page.screenshot({
    path: join(artifacts, "landing.png"),
    fullPage: true,
  });
  await page.getByRole("link", { name: /Open your workspace/ }).click();
  await page.getByRole("button", { name: "Create an account" }).click();
  await page
    .getByLabel("Email", { exact: true })
    .fill("test-" + Date.now() + "@example.com");
  await page
    .getByLabel("Password", { exact: true })
    .fill("test-long-password-42");
  await page
    .getByRole("button", { name: "Create account", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Read between the references." }),
  ).toBeVisible();
  await page.goto("/app/pilot");
  await expect(
    page.getByRole("heading", { name: "Use the evidence. Keep the judgment." }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Copy feedback template" }).click();
  await expect(page.getByRole("button", { name: "Copied" })).toBeVisible();
  await page.goto("/app/contracts");
  await page.getByRole("button", { name: /Analyze sample contract/ }).click();
  await expect(
    page.getByRole("heading", {
      name: "Payment-term inconsistency",
      exact: true,
    }),
  ).toBeVisible();
  const reportUrl = page.url();
  await page.screenshot({
    path: join(artifacts, "report.png"),
    fullPage: true,
  });
  const persisted = await (
    await page.request.get(reportUrl.replace("/app/", "/api/"))
  ).json();
  expect(persisted.result.schema_version).toBe("1.0");
  expect(persisted.result.clauses[0].spans.length).toBeGreaterThan(0);
  const isolated = await browser.newContext();
  expect(
    (await isolated.request.get(reportUrl.replace("/app/", "/api/"))).status(),
  ).toBe(401);
  await isolated.close();
  await page
    .getByRole("button", { name: "Source clauses", exact: true })
    .click();
  await expect(
    page.getByText("Original text · clause location").first(),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "References & terms", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Defined terms & effective values" }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Save analysis", exact: true })
    .click();
  await expect(
    page.getByRole("button", { name: "Saved", exact: true }),
  ).toBeDisabled();
  const download = page.waitForEvent("download");
  await page.getByRole("button", { name: "Export JSON" }).click();
  expect((await download).suggestedFilename()).toMatch(/lexvigil-.+json/);
  await page
    .getByRole("button", { name: "Delete analysis", exact: true })
    .click();
  await page
    .getByRole("alertdialog")
    .getByRole("button", { name: "Delete analysis", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "My analyses", exact: true }),
  ).toBeVisible();
  await page.setViewportSize({ width: 390, height: 844 });
  await page.getByRole("button", { name: "Toggle navigation" }).click();
  await page
    .getByRole("link", { name: "Analyze contract", exact: true })
    .click();
  await page.reload();
  await expect(page.locator(".upload-zone")).toBeVisible();
  await page.evaluate(() => document.fonts.ready);
  await expect
    .poll(async () =>
      page
        .locator(".sidebar")
        .evaluate((el) => el.getBoundingClientRect().right),
    )
    .toBeLessThanOrEqual(0);
  await page.screenshot({
    path: join(artifacts, "mobile.png"),
    fullPage: true,
    animations: "disabled",
  });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  expect(errors).toEqual([]);
});

test("real upload, missing reference, complete print and failure state", async ({
  page,
}) => {
  await page.goto("/login");
  await page.getByRole("button", { name: "Create an account" }).click();
  await page
    .getByLabel("Email", { exact: true })
    .fill("upload-" + Date.now() + "@example.com");
  await page
    .getByLabel("Password", { exact: true })
    .fill("test-long-password-42");
  await page
    .getByRole("button", { name: "Create account", exact: true })
    .click();
  await page.getByLabel("Choose contract file").setInputFiles({
    name: "real-contract.txt",
    mimeType: "text/plain",
    buffer: Buffer.from(
      "1.1 Delivery\nThe supplier shall follow Section 9.9.\n2.1 Termination\nEither party may terminate on sixty (60) days notice.",
    ),
  });
  await page
    .getByRole("button", { name: "Analyze contract", exact: true })
    .click();
  await expect(
    page.getByRole("heading", {
      name: "Unresolved reference to §9.9",
      exact: true,
    }),
  ).toBeVisible();
  await page.emulateMedia({ media: "print" });
  await expect(page.locator(".print-report")).toBeVisible();
  await expect(
    page
      .locator(".print-report")
      .getByText("Either party may terminate on sixty (60) days notice.", {
        exact: false,
      }),
  ).toBeVisible();
  await page.emulateMedia({ media: "screen" });
  await expect(
    page.getByRole("button", { name: "Request AI review" }),
  ).toBeVisible();
  await page
    .getByRole("link", { name: "Analyze contract", exact: true })
    .click();
  await page.getByLabel("Choose contract file").setInputFiles({
    name: "fake.pdf",
    mimeType: "application/pdf",
    buffer: Buffer.from("not a PDF"),
  });
  await page
    .getByRole("button", { name: "Analyze contract", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Analysis needs attention" }),
  ).toBeVisible();
  await expect(
    page.getByText("The file is not a valid PDF.", { exact: true }),
  ).toBeVisible();
});
