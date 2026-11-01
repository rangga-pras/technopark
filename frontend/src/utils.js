export const todayWib = () =>
  new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Jakarta",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date());
export const displayDate = (value) => {
  const date = new Date(`${value}T12:00:00+07:00`);
  return Number.isNaN(date.valueOf())
    ? "Tanggal tidak valid"
    : new Intl.DateTimeFormat("id-ID", {
        dateStyle: "full",
        timeZone: "Asia/Jakarta",
      }).format(date);
};
export const slotLabel = (slot) =>
  `${slot.start_time.slice(0, 5)}–${slot.end_time.slice(0, 5)}`;
export const statusLabel = (status) =>
  ({ upcoming: "Mendatang", completed: "Selesai", cancelled: "Dibatalkan" })[
    status
  ] || status;
export const canEdit = (b) =>
  b.status === "upcoming" &&
  new Date(`${b.usage_date}T${b.time_slot.start_time}+07:00`) > new Date();
export function safeRedirect(value) {
  return typeof value === "string" &&
    value.startsWith("/") &&
    !value.startsWith("//") &&
    !value.startsWith("/login") &&
    !value.startsWith("/register")
    ? value
    : "/rooms";
}
