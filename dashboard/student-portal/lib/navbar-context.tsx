"use client";
import { createContext, useContext, useState, useCallback, ReactNode } from "react";

interface NavbarContextValue {
  onSubmitClick: (() => void) | null;
  setOnSubmitClick: (fn: (() => void) | null) => void;
  isMobileMenuOpen: boolean;
  setMobileMenuOpen: (open: boolean) => void;
}

const NavbarContext = createContext<NavbarContextValue>({
  onSubmitClick: null,
  setOnSubmitClick: () => {},
  isMobileMenuOpen: false,
  setMobileMenuOpen: () => {},
});

export function NavbarProvider({ children }: { children: ReactNode }) {
  const [onSubmitClick, setOnSubmitClickState] = useState<(() => void) | null>(null);
  const [isMobileMenuOpen, setMobileMenuOpen] = useState(false);

  const setOnSubmitClick = useCallback((fn: (() => void) | null) => {
    setOnSubmitClickState(() => fn);
  }, []);

  return (
    <NavbarContext.Provider value={{ onSubmitClick, setOnSubmitClick, isMobileMenuOpen, setMobileMenuOpen }}>
      {children}
    </NavbarContext.Provider>
  );
}

export function useNavbar() {
  return useContext(NavbarContext);
}
