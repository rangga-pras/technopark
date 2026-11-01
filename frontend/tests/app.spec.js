import { test, expect } from "@playwright/test";
import fs from "node:fs";
const nextDay = (offset = 1) => {
  const day = new Date();
  day.setDate(day.getDate() + offset);
  while (day.getDay() === 0) day.setDate(day.getDate() + 1);
  return `${day.getFullYear()}-${String(day.getMonth() + 1).padStart(2, "0")}-${String(day.getDate()).padStart(2, "0")}`;
};
const admin = () =>
  JSON.parse(
    fs.readFileSync(
      new URL("../../backend/.env.e2e.json", import.meta.url),
      "utf8",
    ),
  );
async function login(page, credentials) {
  await page.goto("/login");
  await page.getByLabel("Email", { exact: true }).fill(credentials.email);
  await page
    .getByLabel("Kata sandi", { exact: true })
    .fill(credentials.password);
  await page.getByRole("button", { name: "Masuk", exact: true }).click();
  await expect(page).toHaveURL(/\/rooms$/);
}
async function goAdmin(page) {
  if (await page.getByRole("button", { name: "Buka navigasi" }).isVisible()) {
    await page.getByRole("button", { name: "Buka navigasi" }).click();
  }
  await page
    .locator("header")
    .getByRole("link", { name: "Admin", exact: true })
    .click();
}

test("guest catalog, filters, empty state, deep links, and API retry", async ({
  page,
}) => {
  await page.goto("/rooms");
  await expect(page.locator(".room-card")).toHaveCount(9);
  await page.getByRole("button", { name: "4 orang", exact: true }).click();
  await expect(page.locator(".room-card")).toHaveCount(3);
  await page.getByRole("searchbox").fill("tidak-ada-ruang");
  await expect(
    page.getByRole("heading", { name: "Tidak ada hasil" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Hapus filter" }).click();
  await expect(page.locator(".room-card")).toHaveCount(9);
  const href = await page
    .locator(".room-image-link")
    .first()
    .getAttribute("href");
  await page.goto(href);
  await page.reload();
  await expect(
    page.getByRole("heading", { name: "Ruang Adi Soemarmo", exact: true }),
  ).toBeVisible();
  await page.route("**/api/rooms", (route) => route.abort());
  await page.goto("/rooms");
  await expect(
    page.getByRole("button", { name: "Coba lagi", exact: true }),
  ).toBeVisible();
  await page.unroute("**/api/rooms");
  await page.getByRole("button", { name: "Coba lagi", exact: true }).click();
  await expect(page.locator(".room-card")).toHaveCount(9);
});

test("guest selection survives registration, booking, edit, cancellation, and logout", async ({
  page,
}) => {
  await page.goto("/rooms");
  await page.locator(".room-image-link").first().click();
  await page.getByLabel("Tanggal pemakaian").fill(nextDay(3));
  await page.getByRole("button", { name: /09:00.*11:00/ }).click();
  await page.getByRole("button", { name: "Lanjutkan booking" }).click();
  await expect(page).toHaveURL(/\/login\?redirect=/);
  await page.getByRole("link", { name: "Daftar gratis" }).click();
  await page.getByLabel("Nama lengkap").fill("Ayu Pengujian");
  await page
    .getByLabel("Email", { exact: true })
    .fill(`ayu-${Date.now()}@example.com`);
  await page.getByLabel("Kata sandi", { exact: true }).fill("Ayu#Pengujian123");
  await page.getByLabel("Ulangi kata sandi").fill("Ayu#Pengujian123");
  await page.getByRole("button", { name: "Daftar & masuk" }).click();
  await expect(
    page.getByRole("heading", { name: "Konfirmasi booking" }),
  ).toBeVisible();
  await page.getByRole("checkbox").check();
  await page
    .getByRole("button", { name: "Konfirmasi booking", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Booking tersimpan" }),
  ).toBeVisible();
  await page.getByRole("link", { name: "Lihat booking saya" }).click();
  await expect(page.locator(".booking-card")).toHaveCount(1);
  await page.getByRole("link", { name: "Ubah jadwal" }).click();
  await page.getByRole("button", { name: /11:00.*13:00/ }).click();
  await page.getByRole("button", { name: "Tinjau perubahan" }).click();
  await page.getByRole("checkbox").check();
  await page.getByRole("button", { name: "Simpan perubahan" }).click();
  await expect(
    page.getByRole("heading", { name: "Booking tersimpan" }),
  ).toBeVisible();
  await page.getByRole("link", { name: "Lihat booking saya" }).click();
  await page
    .getByRole("button", { name: "Batalkan booking", exact: true })
    .click();
  await page.getByRole("button", { name: "Ya, batalkan" }).click();
  await page.getByRole("button", { name: /Dibatalkan/ }).click();
  await expect(page.locator(".booking-card")).toHaveCount(1);
  await page.locator(".account-link").click();
  await page.getByRole("button", { name: "Keluar dari akun" }).click();
  await page.goto("/my-bookings");
  await expect(page).toHaveURL(/\/login/);
  expect(
    await page.evaluate(() => localStorage.length + sessionStorage.length),
  ).toBe(0);
});

test("admin CRUD forms, validation, and operational summary use the API", async ({
  page,
}) => {
  await login(page, admin());
  await goAdmin(page);
  await expect(
    page.getByRole("heading", { name: "Ringkasan operasional" }),
  ).toBeVisible();
  await page
    .locator(".admin-nav")
    .getByRole("link", { name: "Fasilitas", exact: true })
    .click();
  await page.getByRole("button", { name: "Tambah fasilitas" }).click();
  await page.getByLabel("Nama", { exact: true }).fill("Fasilitas QA");
  await page.getByRole("button", { name: "Simpan", exact: true }).click();
  const row = page.getByRole("row").filter({ hasText: "Fasilitas QA" });
  await row.getByRole("button", { name: "Edit", exact: true }).click();
  await page.getByLabel("Nama", { exact: true }).fill("Fasilitas QA diubah");
  await page.getByRole("button", { name: "Simpan", exact: true }).click();
  await page
    .getByRole("row")
    .filter({ hasText: "Fasilitas QA diubah" })
    .getByRole("button", { name: "Hapus", exact: true })
    .click();
  await page.getByRole("button", { name: "Ya, hapus" }).click();
  await expect(
    page.getByText("Fasilitas QA diubah", { exact: true }),
  ).toHaveCount(0);
  await page
    .locator(".admin-nav")
    .getByRole("link", { name: "Ruangan", exact: true })
    .click();
  await page.getByRole("button", { name: "Tambah ruangan" }).click();
  await page.getByLabel("Nama", { exact: true }).fill("Ruang Pengujian");
  await page.getByLabel("Kapasitas orang").fill("5");
  await page
    .getByLabel("Deskripsi")
    .fill("Ruangan tambahan untuk pengujian operasional.");
  await page.getByLabel("Wi-Fi", { exact: true }).check();
  await page.getByRole("button", { name: "Simpan", exact: true }).click();
  await expect(
    page.getByRole("row").filter({ hasText: "Ruang Pengujian" }),
  ).toBeVisible();
  await page
    .getByRole("row")
    .filter({ hasText: "Ruang Adi Soemarmo" })
    .getByRole("button", { name: "Edit", exact: true })
    .click();
  await page.getByLabel("Nama", { exact: true }).fill("Nama yang ditolak");
  await page.getByRole("button", { name: "Simpan", exact: true }).click();
  await expect(page.getByRole("alert")).toContainText("harus dipertahankan");
  await page.getByRole("button", { name: "Tutup form" }).click();
  await page
    .getByRole("row")
    .filter({ hasText: "Ruang Pengujian" })
    .getByRole("button", { name: "Arsipkan", exact: true })
    .click();
  await page.getByRole("button", { name: "Ya, arsipkan" }).click();
  await expect(
    page.getByRole("row").filter({ hasText: "Ruang Pengujian" }),
  ).toContainText("Nonaktif");
  await page
    .locator(".admin-nav")
    .getByRole("link", { name: "Hari libur", exact: true })
    .click();
  await page.getByRole("button", { name: "Tambah hari libur" }).click();
  await page.getByLabel("Nama hari libur").fill("Libur QA");
  await page.getByLabel("Tanggal libur").fill(nextDay(30));
  await page.getByRole("button", { name: "Simpan", exact: true }).click();
  await page
    .getByRole("row")
    .filter({ hasText: "Libur QA" })
    .getByRole("button", { name: "Hapus", exact: true })
    .click();
  await page.getByRole("button", { name: "Ya, hapus" }).click();
  await page
    .locator(".admin-nav")
    .getByRole("link", { name: "Pengguna", exact: true })
    .click();
  await page.getByRole("button", { name: "Tambah pengguna" }).click();
  await page.getByLabel("Nama", { exact: true }).fill("Pengguna QA");
  await page
    .getByLabel("Email", { exact: true })
    .fill("pengguna-qa@example.com");
  await page.getByLabel("Kata sandi", { exact: true }).fill("Pengguna#QA123");
  await page.getByLabel("Ulangi kata sandi").fill("Pengguna#QA123");
  await page.getByRole("button", { name: "Simpan", exact: true }).click();
  await expect(
    page.getByRole("row").filter({ hasText: "pengguna-qa@example.com" }),
  ).toBeVisible();
  await page
    .locator(".admin-nav")
    .getByRole("link", { name: "Booking", exact: true })
    .click();
  await page.getByRole("button", { name: "Tambah booking" }).click();
  await page
    .getByLabel("Pemesan", { exact: true })
    .selectOption({ label: "Pengguna QA · pengguna-qa@example.com" });
  await page
    .getByLabel("Ruangan", { exact: true })
    .selectOption({ label: "Ruang Balapan · 4 orang" });
  await page.getByLabel("Tanggal pemakaian").fill(nextDay(10));
  await page.getByLabel("Slot WIB").selectOption("1");
  await page.getByRole("button", { name: "Simpan", exact: true }).click();
  const booking = page.getByRole("row").filter({ hasText: "Pengguna QA" });
  await expect(booking).toContainText("Mendatang");
  await booking.getByRole("button", { name: "Batalkan", exact: true }).click();
  await page.getByRole("button", { name: "Ya, batalkan" }).click();
  await expect(booking).toContainText("Dibatalkan");
  await page
    .locator(".admin-nav")
    .getByRole("link", { name: "Pengguna", exact: true })
    .click();
  await page
    .getByRole("row")
    .filter({ hasText: "pengguna-qa@example.com" })
    .getByRole("button", { name: "Nonaktifkan" })
    .click();
  await page.getByRole("button", { name: "Ya, nonaktifkan" }).click();
  await expect(
    page.getByRole("row").filter({ hasText: "pengguna-qa@example.com" }),
  ).toContainText("Nonaktif");
});

for (const width of [375, 768, 1280]) {
  test(`responsive ${width}px, images, keyboard navigation, session refresh`, async ({
    page,
  }) => {
    await page.setViewportSize({ width, height: 900 });
    for (const path of ["/", "/rooms", "/login", "/register"]) {
      await page.goto(path);
      await page.locator("h1").waitFor();
      await expect
        .poll(() =>
          page.evaluate(
            () => document.documentElement.scrollWidth <= innerWidth,
          ),
        )
        .toBe(true);
      const images = page.locator("img");
      for (const img of await images.all())
        expect(await img.getAttribute("alt")).not.toBeNull();
    }
    await page.goto("/");
    await page.getByRole("link", { name: "Langsung ke konten" }).focus();
    await page.keyboard.press("Enter");
    await expect(page.locator("#main-content")).toBeFocused();
    if (width < 769) {
      await page.getByRole("button", { name: "Buka navigasi" }).click();
      await expect(page.locator("#main-nav")).toBeVisible();
    }
    await login(page, admin());
    await goAdmin(page);
    await page
      .locator(".admin-nav")
      .getByRole("link", { name: "Pengguna", exact: true })
      .click();
    await expect(
      page.getByRole("heading", { name: "Pengguna", exact: true }),
    ).toBeVisible();
    await expect
      .poll(() =>
        page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
      )
      .toBe(true);
    await page.screenshot({
      path: `test-results/admin-${width}.png`,
      fullPage: true,
    });
    await page.reload();
    await expect(page).toHaveURL(/\/login/);
  });
}
