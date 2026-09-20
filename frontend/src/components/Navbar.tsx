'use client';

import React from 'react';
import Link from 'next/link';
import { Scale, FileText, GitCompare, UserCheck, Sparkles } from 'lucide-react';

interface NavbarProps {
  activeTab?: string;
  setActiveTab?: (tab: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab = 'documents', setActiveTab }) => {
  const navItems = [
    { id: 'documents', label: 'Documents', icon: FileText },
    { id: 'compare', label: 'Compare Agreements', icon: GitCompare },
    { id: 'lawyer-prep', label: 'Lawyer Prep & Export', icon: UserCheck },
  ];

  return (
    <header className="sticky top-0 z-50 bg-slate-950/80 backdrop-blur-md border-b border-slate-800/80 shadow-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo */}
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-blue-600 to-amber-500 p-0.5 shadow-lg group-hover:shadow-indigo-500/20 transition-all duration-300">
              <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                <Scale className="w-5 h-5 text-indigo-400 group-hover:scale-110 transition-transform" />
              </div>
            </div>
            <div>
              <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white via-indigo-200 to-amber-300">
                Nyaya<span className="text-amber-400">AI</span>
              </span>
              <span className="hidden sm:inline-block text-[10px] font-semibold tracking-wider text-slate-400 uppercase ml-2 px-1.5 py-0.5 rounded bg-slate-800/60 border border-slate-700/50">
                Legal Intelligence
              </span>
            </div>
          </Link>

          {/* Navigation Items */}
          <nav className="flex items-center gap-1 bg-slate-900/60 p-1 rounded-xl border border-slate-800/60">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab && setActiveTab(item.id)}
                  className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs sm:text-sm font-medium transition-all duration-200 ${
                    isActive
                      ? 'bg-gradient-to-r from-indigo-600 to-blue-600 text-white shadow-md shadow-indigo-600/20'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Status Indicator */}
          <div className="hidden lg:flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="text-xs text-slate-400 font-medium flex items-center gap-1">
              <Sparkles className="w-3.5 h-3.5 text-amber-400" /> RAG & Multi-Agent Active
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};
