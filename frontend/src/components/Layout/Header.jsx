import { UserCircle2 } from "lucide-react";

export function Header({ titulo }) {
  return (
    <header className="flex h-16 items-center justify-between border-b border-iq-border bg-white px-6">
      <h1 className="text-xl font-semibold text-iq-text">{titulo}</h1>
      <div className="flex items-center gap-3">
        <div className="text-right">
          <p className="text-sm font-medium text-iq-text">Alejandro</p>
          <p className="text-xs text-iq-sub">Administrador</p>
        </div>
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-iq-primary/10 text-iq-primary">
          <UserCircle2 size={26} />
        </div>
      </div>
    </header>
  );
}