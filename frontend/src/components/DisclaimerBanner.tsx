import React from 'react';
import { ShieldAlert, Info } from 'lucide-react';

interface Props {
  compact?: boolean;
}

export const DisclaimerBanner: React.FC<Props> = ({ compact = false }) => {
  if (compact) {
    return (
      <div className="bg-amber-950/40 border border-amber-800/40 rounded-lg px-3 py-2 text-xs text-amber-300/90 flex items-center gap-2">
        <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0" />
        <span>
          <strong>Legal Info Only:</strong> NyayaAI provides automated legal document assistance, not professional legal advice. Consult a qualified attorney for legal decisions.
        </span>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-r from-amber-950/60 via-amber-900/40 to-amber-950/60 border border-amber-700/50 rounded-xl p-4 text-sm text-amber-200 shadow-lg flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
      <div className="flex items-start gap-3">
        <div className="p-2 bg-amber-900/60 border border-amber-600/40 rounded-lg text-amber-400 shrink-0 mt-0.5 md:mt-0">
          <ShieldAlert className="w-5 h-5" />
        </div>
        <div>
          <h4 className="font-semibold text-amber-300 text-base">Legal Information & Document Intelligence Platform</h4>
          <p className="text-amber-200/80 text-xs mt-0.5 leading-relaxed">
            NyayaAI provides plain-language explanations, clause analysis, and document intelligence for informational purposes only. It does not constitute professional legal advice or create an attorney-client relationship.
          </p>
        </div>
      </div>
      <div className="shrink-0 flex items-center gap-2 self-end md:self-auto">
        <span className="text-xs text-amber-400/80 font-medium px-2.5 py-1 rounded-full bg-amber-900/50 border border-amber-700/40 flex items-center gap-1">
          <Info className="w-3.5 h-3.5" /> Human Safeguards Active
        </span>
      </div>
    </div>
  );
};
