import React from 'react';
import { AlertTriangle, AlertOctagon, ShieldAlert, CheckCircle2 } from 'lucide-react';

interface Props {
  level: 'low' | 'medium' | 'high' | 'critical' | string;
  showIcon?: boolean;
}

export const RiskBadge: React.FC<Props> = ({ level, showIcon = true }) => {
  const normLevel = (level || 'low').toLowerCase();

  const config = {
    critical: {
      bg: 'bg-rose-950/60 border-rose-600/50 text-rose-300',
      icon: AlertOctagon,
      label: 'CRITICAL RISK',
    },
    high: {
      bg: 'bg-red-950/60 border-red-600/50 text-red-300',
      icon: ShieldAlert,
      label: 'HIGH RISK',
    },
    medium: {
      bg: 'bg-amber-950/60 border-amber-600/50 text-amber-300',
      icon: AlertTriangle,
      label: 'MEDIUM RISK',
    },
    low: {
      bg: 'bg-emerald-950/60 border-emerald-600/50 text-emerald-300',
      icon: CheckCircle2,
      label: 'LOW RISK',
    },
  }[normLevel] || {
    bg: 'bg-slate-800 border-slate-700 text-slate-300',
    icon: CheckCircle2,
    label: normLevel.toUpperCase(),
  };

  const Icon = config.icon;

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md border text-xs font-semibold uppercase tracking-wider ${config.bg}`}
    >
      {showIcon && <Icon className="w-3.5 h-3.5" />}
      {config.label}
    </span>
  );
};
