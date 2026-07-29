/**
 * Fixture for eval #4 — register gate (marketing / one-shot hero).
 * Intentionally a throwaway marketing surface: no forms, tables, accounts, or app workflows.
 * Premium skill should compose upstream aesthetics + a11y/stability polish only —
 * not force UX-CONTRACT.md, CRUD contracts, or durable app artifacts.
 */
export default function MarketingHeroPage() {
  return (
    <main className="min-h-screen">
      <section
        className="relative flex min-h-screen flex-col justify-end bg-cover bg-center px-8 pb-16 pt-24 text-white"
        style={{
          backgroundImage:
            "linear-gradient(180deg, transparent 40%, rgba(0,0,0,0.55)), url('/hero.jpg')",
        }}
      >
        <p className="font-display text-5xl tracking-tight md:text-7xl">
          Northwind Atelier
        </p>
        <h1 className="mt-4 max-w-xl text-2xl font-medium md:text-3xl">
          Cloth cut for weather you have not met yet.
        </h1>
        <p className="mt-3 max-w-md text-base text-white/85">
          A single seasonal lookbook page. No account, cart, or dashboard.
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <a
            href="#lookbook"
            className="inline-flex cursor-pointer items-center bg-white px-5 py-3 text-sm font-medium text-neutral-900 hover:bg-neutral-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white"
          >
            View the lookbook
          </a>
          <a
            href="#stores"
            className="inline-flex cursor-pointer items-center border border-white/70 px-5 py-3 text-sm font-medium text-white hover:bg-white/10 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white"
          >
            Find a store
          </a>
        </div>
      </section>
    </main>
  );
}
